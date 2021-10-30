# SPDX-License-Identifier: MIT
# Copyright (c) 2019 Martijn Pieters
# Licensed under the MIT license as detailed in LICENSE.txt

try:
    # Python 3.8+
    from importlib.metadata import version  # type: ignore
except ImportError:
    # Python 3.7
    from importlib_metadata import version  # type: ignore

from .leakybucket import AsyncLimiter

__version__ = version("aiolimiter")
__all__ = ["AsyncLimiter"]
