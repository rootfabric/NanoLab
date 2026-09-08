#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MODE="${1:-}"
RUN_PATH="${2:-}"
case "$MODE" in
  validate|status|close) ;;
  *) echo "usage: $0 validate|status|close <run-dir>" >&2; exit 2 ;;
esac
if [[ -z "$RUN_PATH" ]]; then
  echo "run directory is required" >&2
  exit 2
fi
export PYTHONPATH="$ROOT/scripts${PYTHONPATH:+:$PYTHONPATH}"
exec python3 -m harness.experiment_cli "$MODE" "$RUN_PATH"
