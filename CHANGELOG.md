# Changelog

<!--
    You should *NOT* be adding new change log entries to this file, this
    file is managed by towncrier. You *may* edit previous change logs to
    fix problems like typo corrections or such.
    To add a new change log entry, please see
    https://pip.pypa.io/en/latest/development/contributing/#news-entries
    we named the news folder "changelog.d", and use Markdown to format
    entries.

    WARNING: Don't drop the next directive!
-->

<!-- Towncrier release notes start -->

## Aiolimiter 1.2.1 (2024-12-08)


### Bugfixes

- Issue a `RuntimeWarning` and reset internal waiter state when being reused across asyncio loops. ([#292](https://github.com/mjpieters/aiolimiter/issues/292))


## Aiolimiter 1.2.0 (2024-12-01)


### Bugfixes

- Improve performance by using a single timeout and a heapq for blocked tasks.
  This ensures only a single task needs to wake up per 'drip' of the bucket,
  instead of creating timeouts for every task. ([#73](https://github.com/mjpieters/aiolimiter/issues/73))


## Aiolimiter 1.1.1 (2024-11-30)


### Bugfixes

- Only include CHANGELOG.md in the source distribution. ([#206](https://github.com/mjpieters/aiolimiter/issues/206))
- Fixed wait time calculation for waiting tasks, making acquisition faster (PR by @schoennenbeck) ([#217](https://github.com/mjpieters/aiolimiter/issues/217))



### Misc

- [#139](https://github.com/mjpieters/aiolimiter/issues/139), [#288](https://github.com/mjpieters/aiolimiter/issues/288)


## Aiolimiter 1.1.0 (2023-05-08)



### Features

- Add ``__slots__`` to the ``AsyncLimiter`` class, reducing memory requirements. ([#85](https://github.com/mjpieters/aiolimiter/issues/85))



### Deprecations and Removals

- Dropped support for Python 3.6 ([#62](https://github.com/mjpieters/aiolimiter/issues/62))



### Misc

- [#95](https://github.com/mjpieters/aiolimiter/issues/95)


## Aiolimiter 1.0.0 (2021-10-15)

### Bugfixes

- Avoid warnings on Python 3.8 and up by not passing in the loop to
  ``asyncio.wait_for()``. ([#46](https://github.com/mjpieters/aiolimiter/issues/46))


## Aiolimiter 1.0.0b1 (2019-12-01)

### Improved Documentation

- Corrected build process to ensure CHANGELOG.md is updated on release. ([#4](https://github.com/mjpieters/aiolimiter/issues/4))


## Aiolimiter 1.0.0b0 (2019-11-30)

_No significant changes_.
