#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MODE="${1:-}"
EXECUTION_PATH="${2:-}"
case "$MODE" in validate|status|close) ;; *) echo "usage: $0 validate|status|close <execution-dir>" >&2; exit 2 ;; esac
if [[ -z "$EXECUTION_PATH" ]]; then echo "execution directory is required" >&2; exit 2; fi
export PYTHONPATH="$ROOT/scripts${PYTHONPATH:+:$PYTHONPATH}"
exec python3 -m harness.work_cli "$MODE" "$EXECUTION_PATH"
