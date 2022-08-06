# SPDX-License-Identifier: MIT
# Copyright (c) 2019 Martijn Pieters
# Licensed under the MIT license as detailed in LICENSE.txt

import asyncio
from contextlib import AbstractAsyncContextManager
from types import TracebackType
from typing import Dict, Optional, Type

from .compat import wait_for


class AsyncLimiter(AbstractAsyncContextManager):
    """A leaky bucket rate limiter.

    This is an :ref:`asynchronous context manager <async-context-managers>`;
    when used with :keyword:`async with`, entering the context acquires
    capacity::

        limiter = AsyncLimiter(10)
        for foo in bar:
            async with limiter:
                # process foo elements at 10 items per minute

    :param max_rate: Allow up to `max_rate` / `time_period` acquisitions before
       blocking.
    :param time_period: duration, in seconds, of the time period in which to
       limit the rate. Note that up to `max_rate` acquisitions are allowed
       within this time period in a burst.

    """

    __slots__ = (
        "max_rate",
        "time_period",
        "_rate_per_sec",
        "_level",
        "_last_check",
        "_waiters",
    )

    max_rate: float  #: The configured `max_rate` value for this limiter.
    time_period: float  #: The configured `time_period` value for this limiter.

    def __init__(self, max_rate: float, time_period: float = 60) -> None:
        self.max_rate = max_rate
        self.time_period = time_period
        self._rate_per_sec = max_rate / time_period
        self._level = 0.0
        self._last_check = 0.0
        # queue of waiting futures to signal capacity to
        self._waiters: Dict[asyncio.Task, asyncio.Future] = {}

    def _leak(self) -> None:
        """Drip out capacity from the bucket."""
        loop = asyncio.get_running_loop()
        if self._level:
            # drip out enough level for the elapsed time since
            # we last checked
            elapsed = loop.time() - self._last_check
            decrement = elapsed * self._rate_per_sec
            self._level = max(self._level - decrement, 0)
        self._last_check = loop.time()

    def has_capacity(self, amount: float = 1) -> bool:
        """Check if there is enough capacity remaining in the limiter

        :param amount: How much capacity you need to be available.

        """
        self._leak()
        requested = self._level + amount
        # if there are tasks waiting for capacity, signal to the first
        # there there may be some now (they won't wake up until this task
        # yields with an await)
        if requested < self.max_rate:
            for fut in self._waiters.values():
                if not fut.done():
                    fut.set_result(True)
                    break
        return self._level + amount <= self.max_rate

    async def acquire(self, amount: float = 1) -> None:
        """Acquire capacity in the limiter.

        If the limit has been reached, blocks until enough capacity has been
        freed before returning.

        :param amount: How much capacity you need to be available.
        :exception: Raises :exc:`ValueError` if `amount` is greater than
           :attr:`max_rate`.

        """
        if amount > self.max_rate:
            raise ValueError("Can't acquire more than the maximum capacity")

        loop = asyncio.get_running_loop()
        task = asyncio.current_task(loop)
        assert task is not None
        while not self.has_capacity(amount):
            # wait for the next drip to have left the bucket
            # add a future to the _waiters map to be notified
            # 'early' if capacity has come up
            fut = loop.create_future()
            self._waiters[task] = fut
            try:
                await wait_for(
                    asyncio.shield(fut), 1 / self._rate_per_sec * amount, loop=loop
                )
            except asyncio.TimeoutError:
                pass
            fut.cancel()
        self._waiters.pop(task, None)

        self._level += amount

        return None

    async def __aenter__(self) -> None:
        await self.acquire()
        return None

    async def __aexit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc: Optional[BaseException],
        tb: Optional[TracebackType],
    ) -> None:
        return None
