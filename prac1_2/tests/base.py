"""Базовый класс тестов команд поверх примера VFS."""
import unittest

import helpers
from shell import Shell
from vfs import load_directory

EPOCH = 0.0


class CommandTestCase(unittest.TestCase):
    """Базовый класс: оболочка поверх VFS из примера deep."""

    vfs_name = "deep"

    def setUp(self):
        """Создаёт оболочку с буферами и фиксированными часами."""
        vfs = load_directory(helpers.example_vfs(self.vfs_name))
        self.out, self.err = helpers.make_buffers()
        self.shell = Shell(vfs, self.out, self.err, clock=lambda: EPOCH)

    def run_line(self, line):
        """Выполняет строку и возвращает (код, stdout, stderr)."""
        self.out.seek(0)
        self.out.truncate()
        self.err.seek(0)
        self.err.truncate()
        status = self.shell.execute(line)
        return status, self.out.getvalue(), self.err.getvalue()
