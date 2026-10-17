#!/usr/bin/env bash
# Проверка работы с различными вариантами VFS (этап 3).
cd "$(dirname "$0")/.." || exit 1
EMU="python3 src/main.py"
SCRIPT="examples/startup/stage3.txt"

run() {
    echo
    echo "=== $* ==="
    "$@" < /dev/null
    echo "[exit code: $?]"
}

run $EMU --vfs examples/vfs/minimal --script $SCRIPT
run $EMU --vfs examples/vfs/files --script $SCRIPT
run $EMU --vfs examples/vfs/deep --script $SCRIPT
run $EMU --vfs examples/vfs/does-not-exist
run $EMU --vfs examples/vfs/minimal/hello.txt
