# SPDX-License-Identifier: MIT
# Copyright (c) 2019 Martijn Pieters
# Licensed under the MIT license as detailed in LICENSE.txt

from importlib.metadata import version

from .leakybucket import AsyncLimiter

__version__ = version("aiolimiter")
__all__ = ["AsyncLimiter"]
