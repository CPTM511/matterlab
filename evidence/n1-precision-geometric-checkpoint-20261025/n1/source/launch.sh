#!/bin/sh
set -eu
: "${MATTERLAB_PYTHON:?Set verified existing interpreter}"
bundle_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
exec "$MATTERLAB_PYTHON" -B "$bundle_dir/run_native.py" "$@"
