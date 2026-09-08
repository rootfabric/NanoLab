#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MODE="${1:-}"
case "$MODE" in
  --overview) MODE="overview" ;;
  --check-consistency) MODE="check-consistency" ;;
  --status) MODE="status" ;;
  --plan) MODE="plan" ;;
  --drive) MODE="drive" ;;
  --close-role) MODE="close-role" ;;
  --close-mission) MODE="close-mission" ;;
  *) echo "usage: $0 --overview|--check-consistency|--status|--plan|--drive|--close-role|--close-mission" >&2; exit 2 ;;
esac
export PYTHONPATH="$ROOT/scripts${PYTHONPATH:+:$PYTHONPATH}"
exec python3 -m harness.cli "$MODE" --root "$ROOT"
