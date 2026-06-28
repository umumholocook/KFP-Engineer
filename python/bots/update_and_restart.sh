#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "pulling latest code"
git pull

echo "installing dependencies"
if command -v pyenv >/dev/null 2>&1 && [[ -f "$SCRIPT_DIR/../../.python-version" ]]; then
    PYTHON="$(cd "$SCRIPT_DIR" && pyenv which python)"
else
    PYTHON="${PYTHON:-python3}"
fi
"$PYTHON" -m pip install -r "$SCRIPT_DIR/requirements.txt"

echo "restarting KFP bot..."
exec bash "$SCRIPT_DIR/start_kfp.sh" --background