"""Точка входа эмулятора оболочки."""
import sys

from config import format_debug, parse_args, vfs_display_name
from script import run_script
from shell import Shell, repl


def configure_output():
    """Включает построчную буферизацию, чтобы порядок вывода сохранялся."""
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(line_buffering=True)


def main(argv=None):
    """Запускает эмулятор и возвращает код завершения."""
    configure_output()
    args = parse_args(argv)
    for line in format_debug(args):
        print(line)
    shell = Shell(vfs_display_name(args.vfs))
    if args.script:
        failed = run_script(shell, args.script)
        if failed:
            print(f"script finished with {failed} error(s)", file=sys.stderr)
    if shell.running:
        repl(shell)
    return 0


if __name__ == "__main__":
    sys.exit(main())
