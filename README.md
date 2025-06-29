# aiolimiter

[![GitHub Actions status for default branch][checks_badge]][checks_status]
[![codecov.io status for default branch][codecov_badge]][codecov_status]
[![Latest PyPI package version][pypi_badge]][aiolimiter_release]
[![Latest Read The Docs][rtd_badge]][aiolimiter_docs]

[checks_badge]: https://github.com/mjpieters/aiolimiter/actions/workflows/ci-cd.yml/badge.svg
[checks_status]: https://github.com/mjpieters/aiolimiter/actions/workflows/ci-cd.yml "GitHub Actions status for default branch"
[codecov_badge]: https://codecov.io/gh/mjpieters/aiolimiter/branch/main/graph/badge.svg
[codecov_status]: https://codecov.io/gh/mjpieters/aiolimiter "codecov.io status for default branch"
[pypi_badge]: https://img.shields.io/pypi/v/aiolimiter
[aiolimiter_release]: https://pypi.org/project/aiolimiter "Latest PyPI package version"
[rtd_badge]: https://readthedocs.org/projects/aiolimiter/badge/?version=latest
[aiolimiter_docs]: https://aiolimiter.readthedocs.io/en/latest/?badge=latest "Latest Read The Docs"

## Introduction

An efficient implementation of a rate limiter for asyncio.

This project implements the [Leaky bucket algorithm][], giving you precise control over the rate a code section can be entered:

```python
from aiolimiter import AsyncLimiter

# allow for 100 concurrent entries within a 30 second window
rate_limit = AsyncLimiter(100, 30)


async def some_coroutine():
    async with rate_limit:
        # this section is *at most* going to entered 100 times
        # in a 30 second period.
        await do_something()
```

It was first developed [as an answer on Stack Overflow][so45502319].

## Documentation

https://aiolimiter.readthedocs.io

## Installation

```sh
$ pip install aiolimiter
```

The library requires Python 3.9 or newer.

## Requirements

- Python >= 3.9

## License

`aiolimiter` is offered under the [MIT license](./LICENSE.txt).

## Source code

The project is hosted on [GitHub][].

Please file an issue in the [bug tracker][] if you have found a bug
or have some suggestions to improve the library.

## Developer setup

This project uses [uv][] to manage dependencies, testing and releases. Make sure you have installed that tool, then run the following command to get set up:

```sh
uv sync
```

Tests are run with `pytest` and `tox`. Releases are made managed by a GitHub Actions workflow. Code quality is maintained with `ruff` and `pyright`, and `pre-commit` runs quick checks to maintain the standards set.

A [Taskfile](https://taskfile.dev/) is provided that defines specific tasks such as linting, formatting or previewing the documentation:

```console
$ task --list
task: Available tasks for this project:
* default:                     Default task, runs linters and tests
* dev:format:                  Runs formatters      (aliases: format)
* dev:install-precommit:       Install pre-commit into local git checkout
* dev:lint:                    Runs linters      (aliases: lint)
* dev:lint:code:               Lint the source code
* dev:lint:renovate:           Lint the Renovate configuration file
* dev:test:                    Run tests                                          (aliases: test)
* dev:tox:                     Run tests with tox                                 (aliases: tox)
* dev:uv-lock:                 Updates the uv lock file                           (aliases: lock)
* dist:build:                  Build the distribution packages                    (aliases: dist)
* dist:clean:                  Remove built distribution packages                 (aliases: clean)
* dist:publish:                Publish package to PyPI                            (aliases: publish)
* docs:build:                  Build project documentation                        (aliases: docs)
* docs:serve:                  Live preview server for project documentation      (aliases: preview)
```

[leaky bucket algorithm]: https://en.wikipedia.org/wiki/Leaky_bucket
[so45502319]: https://stackoverflow.com/a/45502319/100297
[github]: https://github.com/mjpieters/aiolimiter
[bug tracker]: https://github.com/mjpieters/aiolimiter/issues
[uv]: https://docs.astral.sh/uv/
