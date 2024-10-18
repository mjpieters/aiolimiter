# SPDX-License-Identifier: MIT
# Copyright (c) 2019 Martijn Pieters
# Licensed under the MIT license as detailed in LICENSE.txt

import asyncio
import time
from pathlib import Path
from unittest import mock

import pytest
import toml

from aiolimiter import AsyncLimiter

WAIT_LIMIT = 2  # seconds before we declare the test failed


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
    start = time.time()
    pending = tasks
    remainder = len(tasks) - n
    while time.time() <= start + WAIT_LIMIT and len(pending) > remainder:
        _, pending = await asyncio.wait(
            tasks, timeout=WAIT_LIMIT, return_when=asyncio.FIRST_COMPLETED
        )
    assert len(pending) >= remainder
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


@pytest.mark.parametrize("task", [acquire_task, async_contextmanager_task])
async def test_acquire(event_loop, task):
    current_time = 0

    def mocked_time():
        return current_time

    # capacity released every 2 seconds
    limiter = AsyncLimiter(5, 10)

    with mock.patch.object(event_loop, "time", mocked_time):
        tasks = [asyncio.ensure_future(task(limiter)) for _ in range(10)]

        pending = await wait_for_n_done(tasks, 5)
        assert len(pending) == 5

        current_time = 3  # releases capacity for one and some buffer
        assert limiter.has_capacity()

        pending = await wait_for_n_done(pending, 1)
        assert len(pending) == 4

        current_time = 7  # releases capacity for two more, plus buffer
        pending = await wait_for_n_done(pending, 2)
        assert len(pending) == 2

        current_time = 11  # releases the remainder
        pending = await wait_for_n_done(pending, 2)
        assert len(pending) == 0


async def test_acquire_wait_time():
    limiter = AsyncLimiter(3, 3)
    # Fill the bucket with an amount of 1
    await limiter.acquire(1)

    # Acquiring an amount of 3 now should take 1s (+overhead)
    start = time.perf_counter()
    await limiter.acquire(3)
    end = time.perf_counter()
    assert end - start < 2
