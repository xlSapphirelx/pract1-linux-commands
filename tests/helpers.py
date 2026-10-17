"""Общие вспомогательные функции тестов."""
import io
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
sys.path.insert(0, SRC)


def make_buffers():
    """Возвращает пару буферов (stdout, stderr) для оболочки."""
    return io.StringIO(), io.StringIO()


def example_vfs(name):
    """Путь к примеру VFS из каталога examples/vfs."""
    return os.path.join(ROOT, "examples", "vfs", name)


def add_echo(shell):
    """Добавляет в оболочку тестовую команду echo."""

    def echo(sh, args):
        """Печатает аргументы через пробел."""
        print(" ".join(args), file=sh.out)
        return 0

    shell.table["echo"] = echo
    return shell
