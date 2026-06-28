#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "pulling latest code"
git pull

echo "restarting KFP bot..."
exec bash "$SCRIPT_DIR/start_kfp.sh" --background