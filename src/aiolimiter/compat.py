# SPDX-License-Identifier: MIT
# Copyright (c) 2019 Martijn Pieters
# Licensed under the MIT license as detailed in LICENSE.txt

# compatibility across Python versions
import asyncio
import sys

if sys.version_info < (3, 8):  # pragma: no cover
    wait_for = asyncio.wait_for
else:
    from typing import Any, Awaitable, Coroutine, Generator, TypeVar, Union

    _T = TypeVar("_T")
    _FutureLike = Union["asyncio.Future[_T]", Generator[Any, None, _T], Awaitable[_T]]

    def wait_for(
        fut: _FutureLike[_T], *args: Any, loop: Any, **kwargs: Any
    ) -> Coroutine[Any, Any, _T]:
        # loop argument is deprecated, drop it automatically
        return asyncio.wait_for(fut, *args, **kwargs)
