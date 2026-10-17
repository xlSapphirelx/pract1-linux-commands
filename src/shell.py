"""Оболочка эмулятора: выполнение команд и интерактивный цикл (REPL)."""
import sys

import commands
from cmdparser import parse_line
from config import DEFAULT_VFS_NAME


class Shell:
    """Состояние оболочки: имя VFS, потоки вывода и таблица команд."""

    def __init__(self, vfs_name=DEFAULT_VFS_NAME, out=None, err=None):
        """Создаёт оболочку; потоки по умолчанию — stdout и stderr."""
        self.vfs_name = vfs_name
        self.out = sys.stdout if out is None else out
        self.err = sys.stderr if err is None else err
        self.running = True
        self.table = dict(commands.COMMANDS)

    def prompt(self):
        """Возвращает приглашение к вводу, содержащее имя VFS."""
        return f"{self.vfs_name}$ "

    def execute(self, line):
        """Выполняет одну строку и возвращает код завершения."""
        name, args = parse_line(line)
        if name is None:
            return commands.EXIT_OK
        handler = self.table.get(name)
        if handler is None:
            print(f"{name}: command not found", file=self.err)
            return commands.EXIT_NOT_FOUND
        return handler(self, args)


def repl(shell, input_func=input):
    """Читает команды пользователя, пока оболочка не завершена."""
    while shell.running:
        try:
            line = input_func(shell.prompt())
        except EOFError:
            print(file=shell.out)
            break
        except KeyboardInterrupt:
            print(file=shell.out)
            continue
        shell.execute(line)
