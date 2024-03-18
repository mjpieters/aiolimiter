# SPDX-License-Identifier: MIT
# Copyright (c) 2019 Martijn Pieters
# Licensed under the MIT license as detailed in LICENSE.txt

# doit tasks for aiolimiter

import os
from pathlib import Path

from doit.action import CmdAction
from doit.exceptions import TaskFailed
from doit.tools import Interactive, run_once

DOIT_CONFIG = {"default_tasks": ["all"], "minversion": "0.31.0"}
POETRY_ACTIVE = os.environ.get("POETRY_ACTIVE", False)
# https://github.com/MicrosoftDocs/vsts-docs/issues/4051
ON_CI = os.environ.get("BUILD_REASON", False) or os.environ.get("CI", False)

# Paths


def _path_sortkey(p):
    """Sort paths lexicographically, but put directories last

    This ensures easy clean-ups while still getting a nicer output
    """
    return (p.is_dir(), *p.parts)


def is_towncrier_fragment(path):
    parts = path.name.split(".")
    return (
        len(parts) > 1
        and parts[0].isdigit()
        and parts[0].isascii()
        and parts[1] in {"feature", "bugfix", "doc", "removal", "misc"}
    )


# source files
THIS = Path(__file__).resolve()
HERE = THIS.parent
PYPROJECT = HERE / "pyproject.toml"
SRC_PATH = HERE / "src"
SRC_FILES = sorted(SRC_PATH.rglob("*.py"), key=_path_sortkey)
TESTS_PATH = HERE / "tests"
TESTS_FILES = sorted(TESTS_PATH.rglob("*.py"), key=_path_sortkey)
DOC_PATH = HERE / "docs"
RST_FILES = sorted(DOC_PATH.rglob("*.rst"), key=_path_sortkey)
CHANGELOG_PATH = HERE / "changelog.d"
CHANGELOG_TEMPLATE = CHANGELOG_PATH / "towncrier_template.md"
CHANGELOG_FRAGMENTS = sorted(filter(is_towncrier_fragment, CHANGELOG_PATH.iterdir()))

ALL_PY_FILES = sorted(
    [THIS, *SRC_FILES, *TESTS_FILES, *DOC_PATH.glob("*.py")], key=_path_sortkey
)

# outputs
DOC_BUILD_PATH = DOC_PATH / "_build"
DOC_HTML_PATH = DOC_BUILD_PATH / "html"
DOC_SPELLING_PATH = DOC_BUILD_PATH / "spelling"
DOC_HTML_FILES = sorted([*DOC_HTML_PATH.rglob("*"), DOC_HTML_PATH], key=_path_sortkey)
DOC_SPELLING_FILES = [DOC_SPELLING_PATH / "output.txt", DOC_SPELLING_PATH]
DIST_PATH = HERE / "dist"
DIST_FILES = sorted(
    [*DIST_PATH.glob("*.tar.gz"), *DIST_PATH.glob("*.whl")], key=_path_sortkey
)
CHANGELOG = HERE / "CHANGELOG.md"


def with_poetry(*actions):
    if not POETRY_ACTIVE:
        return actions
    # handle both shell and exec actions
    return [
        (
            f"poetry run {action}"
            if isinstance(action, str)
            else ["poetry", "run", *action]
        )
        for action in actions
    ]


def task_poetry_install():
    # in case we have doit installed outside of poetry
    # and there is no lock file, run poetry first.
    return {
        "basename": "_install_poetry",
        "actions": [["poetry", "install", "--with", "docs"]],
        "targets": ["poetry.lock"],
        "uptodate": [run_once],
    }


def task_devsetup():
    """Set up the development environment"""
    yield {
        "name": "install_precommit",
        "setup": ["_install_poetry"],
        "actions": with_poetry(["pre-commit", "install"]),
        "targets": [".git/hooks/pre-commit"],
        "file_dep": [".pre-commit-config.yaml"],
    }


def task_lint():
    """Lint the code with isort, flake8 and mypy"""
    yield {
        "name": "isort_check",
        "setup": ["devsetup"],
        "actions": with_poetry("isort --check-only %(changed)s"),
        "file_dep": ALL_PY_FILES,
    }
    yield {
        "name": "flake8",
        "setup": ["devsetup"],
        "actions": with_poetry("flake8 %(changed)s"),
        "file_dep": ALL_PY_FILES,
    }
    yield {
        "name": "mypy",
        "setup": ["devsetup"],
        "actions": with_poetry(["mypy", SRC_PATH]),
        "file_dep": SRC_FILES,
    }


def task_format():
    """Format files with isort and black"""
    yield {
        "name": "isort",
        "setup": ["devsetup"],
        "actions": with_poetry("isort %(changed)s"),
        "file_dep": ALL_PY_FILES,
    }
    yield {
        "name": "black",
        "setup": ["devsetup"],
        "actions": with_poetry("black %(changed)s"),
        "file_dep": ALL_PY_FILES,
    }


def task_test():
    """Run the tests"""
    test_cmd = with_poetry("pytest")[0]
    return {
        "setup": ["devsetup"],
        "actions": [Interactive(test_cmd)],
        "file_dep": [*SRC_FILES, *TESTS_FILES],
        "task_dep": ["lint"],
    }


def task_tox():
    """Run tox, testing against all supported Python releases"""
    test_cmd = with_poetry("tox")[0]
    return {
        "setup": ["devsetup"],
        "actions": [Interactive(test_cmd)],
        "file_dep": [*SRC_FILES, *TESTS_FILES],
        "task_dep": ["lint"],
    }


def task_docs_checks():
    """Check documentation spelling and towncrier handling"""
    make_cmd = with_poetry(["make", "spelling"])[0]
    yield {
        "name": "docs_spelling",
        "setup": ["devsetup"],
        "actions": [CmdAction(make_cmd, cwd=DOC_PATH, shell=False)],
        "file_dep": [
            *SRC_FILES,
            *RST_FILES,
            DOC_PATH / "conf.py",
            DOC_PATH / "Makefile",
            DOC_PATH / "spelling_wordlist.txt",
        ],
        "targets": DOC_SPELLING_FILES,
        "clean": True,
    }

    def check_towncrier_fragments(changed):
        for path in map(Path, changed):
            if not (is_towncrier_fragment(path) or path == CHANGELOG_TEMPLATE):
                return TaskFailed(
                    f"{CHANGELOG_PATH.name}/{path.name} is not a valid towncrier "
                    f"fragment name."
                )

    yield {
        "name": "towncrier_fragments",
        "actions": [check_towncrier_fragments],
        "file_dep": sorted(CHANGELOG_PATH.iterdir()),
    }
    yield {
        "name": "towncrier",
        "task_dep": ["docs_checks:towncrier_fragments"],
        "setup": ["devsetup"],
        "actions": with_poetry(["towncrier", "--draft"]),
        "file_dep": [PYPROJECT, CHANGELOG_TEMPLATE, *CHANGELOG_FRAGMENTS],
    }


def task_docs():
    """Build the documentation"""
    make_cmd = with_poetry(["make", "html"])[0]
    return {
        "setup": ["devsetup"],
        "task_dep": ["docs_checks"],
        "actions": [CmdAction(make_cmd, cwd=DOC_PATH, shell=False)],
        "file_dep": [
            *SRC_FILES,
            *RST_FILES,
            DOC_PATH / "conf.py",
            DOC_PATH / "Makefile",
        ],
        "targets": DOC_HTML_FILES,
        "clean": True,
    }


def task_build():
    """Build the distribution packages"""
    yield {
        "name": "poetry",
        "setup": ["devsetup"],
        "actions": ["poetry build"],
        "task_dep": ["test", "docs"],
        "file_dep": [PYPROJECT, *ALL_PY_FILES],
        "targets": [DIST_PATH, *DIST_FILES],
        "clean": True,
    }
    yield {
        "name": "check",
        "setup": ["devsetup", "build:poetry"],
        "actions": ["twine check dist/*"],
        "file_dep": [*DIST_FILES],
    }


def task_all():
    """Run all checks, then build the docs and release"""
    return {"actions": [], "task_dep": ["tox", "docs", "build"]}
