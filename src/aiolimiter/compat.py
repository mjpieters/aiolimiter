# SPDX-License-Identifier: MIT
# Copyright (c) 2019 Martijn Pieters
# Licensed under the MIT license as detailed in LICENSE.txt

# compatibility across Python versions
import asyncio
import contextlib

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
