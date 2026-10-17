"""Точка входа эмулятора оболочки."""
import sys

from shell import Shell, repl


def main():
    """Запускает интерактивный режим и возвращает код завершения."""
    repl(Shell())
    return 0


if __name__ == "__main__":
    sys.exit(main())
