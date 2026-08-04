#!/bin/bash
set -euo pipefail

function verbose_logs () {
    echo '::group::Prek verbose logs'
    PREK_LOG_PATH="$(prek cache dir --no-log-file --color=never)/prek.log"
    if [[ -f "$PREK_LOG_PATH" ]]; then
        cat "$PREK_LOG_PATH"
    else
        echo "No prek log file found at $PREK_LOG_PATH"
    fi
    echo '::endgroup::'
}

if git diff-tree --no-commit-id --name-only -r --root --diff-filter=d -z HEAD \
    | xargs --no-run-if-empty --null prek run --show-diff-on-failure --color=always --files; then
    verbose_logs
    echo '::group::Pruning prek cache'
    prek cache gc -v
    echo '::endgroup::'
else
    verbose_logs
    exit 1
fi
