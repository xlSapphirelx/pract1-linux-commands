#!/usr/bin/env bash
# Проверка параметров командной строки эмулятора (этап 2).
cd "$(dirname "$0")/.." || exit 1
EMU="python3 src/main.py"

run() {
    echo
    echo "=== $* ==="
    "$@" < /dev/null
    echo "[exit code: $?]"
}

run $EMU
run $EMU --vfs examples/vfs/minimal
run $EMU --script examples/startup/stage2.txt
run $EMU --vfs examples/vfs/minimal --script examples/startup/stage2.txt
run $EMU --script examples/startup/missing.txt
run $EMU --unknown-option
