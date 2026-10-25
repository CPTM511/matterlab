#!/bin/sh
set -eu
if [ -n "${PYTHONOPTIMIZE:-}" ]; then
  echo "PYTHONOPTIMIZE must be absent" >&2
  exit 2
fi
export PYTHONDONTWRITEBYTECODE=1
exec PRIVATE_PATH_ALIAS_1 -B "$(dirname "$0")/supervisor.py" "$@"
