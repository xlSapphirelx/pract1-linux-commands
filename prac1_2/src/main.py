"""Точка входа эмулятора оболочки."""
import sys

from config import format_debug, parse_args
from script import run_script
from shell import Shell, repl
from vfs import Vfs, VfsError, load_directory

EXIT_USAGE = 2


def configure_output():
    """Включает построчную буферизацию, чтобы порядок вывода сохранялся."""
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(line_buffering=True)


def load_vfs(path):
    """Загружает VFS из директории или создаёт пустую, если путь не задан."""
    if path is None:
        return Vfs.empty()
    return load_directory(path)


def main(argv=None):
    """Запускает эмулятор и возвращает код завершения."""
    configure_output()
    args = parse_args(argv)
    for line in format_debug(args):
        print(line)
    try:
        vfs = load_vfs(args.vfs)
    except VfsError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return EXIT_USAGE
    dirs, files = vfs.stats()
    print(f"[debug] vfs '{vfs.name}' loaded: {dirs} dirs, {files} files")
    shell = Shell(vfs)
    if args.script:
        failed = run_script(shell, args.script)
        if failed:
            print(f"script finished with {failed} error(s)", file=sys.stderr)
    if shell.running:
        repl(shell)
    return 0


if __name__ == "__main__":
    sys.exit(main())
