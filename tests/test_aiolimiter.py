# SPDX-License-Identifier: MIT
# Copyright (c) 2019 Martijn Pieters
# Licensed under the MIT license as detailed in LICENSE.txt

import asyncio
from pathlib import Path
from unittest import mock

import pytest
import toml

from aiolimiter import AsyncLimiter

# max number of wait_for rounds when waiting for all events to settle
MAX_WAIT_FOR_ITER = 5


def test_version():
    # the version is taken from metadata
    from aiolimiter import __version__

    assert __version__

    pyproject = Path(__file__).resolve().parent.parent / "pyproject.toml"
    metadata = toml.load(pyproject)["tool"]["poetry"]

    # pyproject bumps to -alpha.0, -beta.1, etc., but releases a0, b1
    # We don't really need to care about those, just verify that sorta
    # the right version is used.
    assert __version__.startswith(metadata["version"].partition("-")[0])


async def wait_for_n_done(tasks, n):
    """Wait for n (or more) tasks to have completed"""
    iteration = 0
    remainder = len(tasks) - n
    while iteration <= MAX_WAIT_FOR_ITER:
        iteration += 1
        _, pending = await asyncio.wait(
            tasks, timeout=0, return_when=asyncio.FIRST_COMPLETED
        )
        if len(pending) <= remainder:
            break
    assert len(pending) <= remainder
    return pending


def test_attributes():
    limiter = AsyncLimiter(42, 81)
    assert limiter.max_rate == 42
    assert limiter.time_period == 81


async def test_has_capacity():
    limiter = AsyncLimiter(1)
    assert limiter.has_capacity()
    assert not limiter.has_capacity(42)

    await limiter.acquire()
    assert not limiter.has_capacity()


async def test_over_acquire():
    limiter = AsyncLimiter(1)
    with pytest.raises(ValueError):
        await limiter.acquire(42)


async def acquire_task(limiter):
    await limiter.acquire()


async def async_contextmanager_task(limiter):
    async with limiter:
        pass


class MockLoopTime:
    def __init__(self):
        self.current_time = 0
        event_loop = asyncio.get_running_loop()
        self.patch = mock.patch.object(event_loop, "time", self.mocked_time)

    def mocked_time(self):
        return self.current_time

    def __enter__(self):
        self.patch.start()
        return self

    def __exit__(self, *_):
        self.patch.stop()


@pytest.mark.parametrize("task", [acquire_task, async_contextmanager_task])
async def test_acquire(task):
    # capacity released every 2 seconds
    limiter = AsyncLimiter(5, 10)

    with MockLoopTime() as mocked_time:
        tasks = [asyncio.ensure_future(task(limiter)) for _ in range(10)]

        pending = await wait_for_n_done(tasks, 5)
        assert len(pending) == 5

        mocked_time.current_time = 3  # releases capacity for one and some buffer
        assert limiter.has_capacity()

        pending = await wait_for_n_done(pending, 1)
        assert len(pending) == 4

        mocked_time.current_time = 7  # releases capacity for two more, plus buffer
        pending = await wait_for_n_done(pending, 2)
        assert len(pending) == 2

        mocked_time.current_time = 11  # releases the remainder
        pending = await wait_for_n_done(pending, 2)
        assert len(pending) == 0


async def test_acquire_wait_time():
    limiter = AsyncLimiter(3, 3)

    with MockLoopTime() as mocked_time:
        # Fill the bucket with an amount of 1
        await limiter.acquire(1)

        # Acquiring an amount of 3 now should take 1 second
        task = asyncio.ensure_future(limiter.acquire(3))
        pending = await wait_for_n_done([task], 0)
        assert pending

        mocked_time.current_time = 1
        pending = await wait_for_n_done([task], 1)
        assert not pending
