# SPDX-License-Identifier: MIT
# Copyright (c) 2019 Martijn Pieters
# Licensed under the MIT license as detailed in LICENSE.txt

# compatibility across Python versions
import asyncio
import contextlib
import sys

try:
    # Python 3.7 or newer
    AsyncContextManagerBase = contextlib.AbstractAsyncContextManager
    current_task = asyncio.current_task
    get_running_loop = asyncio.get_running_loop
except AttributeError:  # pragma: no cover
    # Python 3.6
    AsyncContextManagerBase = object  # type: ignore
    current_task = asyncio.Task.current_task
    get_running_loop = asyncio.get_event_loop


if sys.version_info < (3, 8):  # pragma: no cover
    wait_for = asyncio.wait_for
else:
    from typing import Any, TypeVar

    _T = TypeVar("_T")

    def wait_for(*args: Any, **kwargs: Any) -> "asyncio.Future[_T]":
        # loop argument is deprecated, drop it automatically
        return asyncio.wait_for(*args)
