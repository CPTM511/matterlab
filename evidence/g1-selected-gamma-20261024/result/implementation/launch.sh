#!/bin/sh
set -eu
# -B applies before run_gamma.py imports any frozen-bundle module.
: "${MATTERLAB_PYTHON:?Set MATTERLAB_PYTHON to the verified existing Python interpreter}"
bundle_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
exec "$MATTERLAB_PYTHON" -B "$bundle_dir/run_gamma.py" "$@"
