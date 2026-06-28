#!/usr/bin/env bash
set -euo pipefail

# pyenv Python may log harmless hashlib/blake2 OpenSSL warnings at import time.
filter_pyenv_hashlib_noise() {
    while IFS= read -r line; do
        case "$line" in
            *blake2b*|*blake2s*|*unsupported\ hash\ type*|*/hashlib.py*)
                continue
                ;;
            *Traceback\ \(most\ recent\ call\ last\)*|*^^^^^*|*globals\(\)\[__func_name\]*|*__get_openssl*|*__get_builtin*)
                continue
                ;;
            ERROR:root:code\ for\ hash\ *)
                continue
                ;;
        esac
        printf '%s\n' "$line" >&2
    done
}
exec 2> >(filter_pyenv_hashlib_noise)

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
PID_FILE="$SCRIPT_DIR/.kfp_bot.pid"
RESTART_FILE="${TMPDIR:-/tmp}/kpf_restart"

FOREGROUND=1
CHECK_ONLY=0

usage() {
    cat <<'EOF'
Usage: start_kfp.sh [options]

Starts the KFP Discord bot (python/bots/main.py).

Options:
  --check        Validate environment and exit (do not start the bot)
  --background   Run the bot in the background (writes PID to .kfp_bot.pid)
  --foreground   Run in the foreground (default)
  -h, --help     Show this help

Requires:
  KFP_TOKEN environment variable
  pip install -r requirements.txt
EOF
}

while [[ $# -gt 0 ]]; do
    case "$1" in
        --check)
            CHECK_ONLY=1
            shift
            ;;
        --background|-b)
            FOREGROUND=0
            shift
            ;;
        --foreground|-f)
            FOREGROUND=1
            shift
            ;;
        -h|--help)
            usage
            exit 0
            ;;
        *)
            echo "Unknown option: $1" >&2
            usage >&2
            exit 1
            ;;
    esac
done

find_python() {
    if command -v pyenv >/dev/null 2>&1; then
        if [[ -f "$REPO_ROOT/.python-version" ]]; then
            local pyenv_python
            pyenv_python="$(cd "$SCRIPT_DIR" && pyenv which python 2>/dev/null || true)"
            if [[ -n "$pyenv_python" && -x "$pyenv_python" ]]; then
                echo "$pyenv_python"
                return
            fi
        fi
    fi

    if command -v python3 >/dev/null 2>&1; then
        echo python3
        return
    fi

    echo python
}

PYTHON="$(find_python)"

cd "$SCRIPT_DIR"

if [[ -z "${KFP_TOKEN:-}" ]]; then
    echo "Error: KFP_TOKEN is not set." >&2
    echo "Export your bot token before starting, e.g.:" >&2
    echo "  export KFP_TOKEN='your-discord-bot-token'" >&2
    exit 1
fi

echo "Using Python: $("$PYTHON" --version 2>&1) ($("$PYTHON" -c 'import sys; print(sys.executable)'))"
echo "Working directory: $SCRIPT_DIR"

"$PYTHON" - <<'PY'
import importlib.util
import sys

required = ("discord", "peewee", "PIL", "aiohttp", "zhconv")
missing = [name for name in required if importlib.util.find_spec(name) is None]
if missing:
    print("Error: missing packages:", ", ".join(missing), file=sys.stderr)
    print("Run: pip install -r requirements.txt", file=sys.stderr)
    sys.exit(1)

import discord
print(f"discord.py {discord.__version__}")
PY

"$PYTHON" -m py_compile main.py
echo "main.py syntax OK"

import_smoke() {
    KFP_TOKEN="${KFP_TOKEN}" "$PYTHON" - <<'PY'
import importlib
import os

os.environ.setdefault("KFP_TOKEN", "preflight")

for module_name in sorted(
    name[:-3]
    for name in os.listdir("cogs")
    if name.endswith(".py") and not name.startswith("__")
):
    importlib.import_module(f"cogs.{module_name}")
print("All cogs import OK")
PY
}

import_smoke

if [[ "$CHECK_ONLY" -eq 1 ]]; then
    echo "Preflight check passed."
    exit 0
fi

stop_existing_bot() {
    if [[ -f "$RESTART_FILE" ]]; then
        local restart_pid=""
        restart_pid="$(sed -n 's/.*\.\([0-9][0-9]*\)$/\1/p' "$RESTART_FILE" | tail -n 1)"
        if [[ -n "$restart_pid" ]] && kill -0 "$restart_pid" 2>/dev/null; then
            echo "Stopping previous bot process $restart_pid (restart marker)..."
            kill "$restart_pid" 2>/dev/null || true
            sleep 1
            kill -9 "$restart_pid" 2>/dev/null || true
        fi
    fi

    if [[ -f "$PID_FILE" ]]; then
        local old_pid=""
        old_pid="$(cat "$PID_FILE")"
        if [[ -n "$old_pid" ]] && kill -0 "$old_pid" 2>/dev/null; then
            echo "Stopping previous bot process $old_pid (pid file)..."
            kill "$old_pid" 2>/dev/null || true
            sleep 1
            kill -9 "$old_pid" 2>/dev/null || true
        fi
        rm -f "$PID_FILE"
    fi
}

stop_existing_bot

if [[ "$FOREGROUND" -eq 1 ]]; then
    echo "Starting KFP bot in foreground..."
    exec "$PYTHON" main.py
fi

echo "Starting KFP bot in background..."
nohup "$PYTHON" main.py >> "$SCRIPT_DIR/kfp_bot.log" 2>&1 &
echo $! > "$PID_FILE"
echo "Bot started with PID $(cat "$PID_FILE"). Logs: $SCRIPT_DIR/kfp_bot.log"