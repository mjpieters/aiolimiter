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
