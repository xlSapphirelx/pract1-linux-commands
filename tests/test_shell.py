"""Тесты оболочки и REPL (этап 1)."""
import unittest

import helpers
from commands import EXIT_NOT_FOUND, EXIT_OK
from shell import Shell, repl
from vfs import Vfs


class ShellTest(unittest.TestCase):
    """Проверки выполнения команд и приглашения."""

    def setUp(self):
        """Создаёт оболочку с буферами вывода."""
        self.out, self.err = helpers.make_buffers()
        self.shell = Shell(Vfs.empty("myvfs"), self.out, self.err)

    def test_prompt_contains_vfs_name(self):
        """Приглашение содержит имя VFS и текущий каталог."""
        self.assertEqual(self.shell.prompt(), "myvfs:/$ ")

    def test_ls_stub_prints_name_and_args(self):
        """ls выводит своё имя и аргументы."""
        self.assertEqual(self.shell.execute("ls -l /x"), EXIT_OK)
        self.assertEqual(self.out.getvalue(), "ls args=['-l', '/x']\n")

    def test_cd_stub_prints_name_and_args(self):
        """cd выводит своё имя и аргументы."""
        self.shell.execute("cd a b")
        self.assertEqual(self.out.getvalue(), "cd args=['a', 'b']\n")

    def test_unknown_command(self):
        """Неизвестная команда даёт ошибку и код 127."""
        self.assertEqual(self.shell.execute("foo"), EXIT_NOT_FOUND)
        self.assertIn("foo: command not found", self.err.getvalue())

    def test_empty_line_is_ignored(self):
        """Пустая строка ничего не делает."""
        self.assertEqual(self.shell.execute("   "), EXIT_OK)
        self.assertEqual(self.out.getvalue(), "")

    def test_exit_stops_shell(self):
        """exit останавливает оболочку."""
        self.shell.execute("exit")
        self.assertFalse(self.shell.running)


class ReplTest(unittest.TestCase):
    """Проверки интерактивного цикла."""

    def test_repl_runs_until_exit(self):
        """REPL выполняет команды до exit и игнорирует остальное."""
        out, err = helpers.make_buffers()
        shell = Shell(Vfs.empty("v"), out, err)
        lines = iter(["ls", "exit", "ls never"])
        repl(shell, lambda prompt: next(lines))
        self.assertEqual(out.getvalue(), "ls args=[]\n")

    def test_repl_stops_on_eof(self):
        """Конец ввода завершает REPL без ошибки."""
        out, err = helpers.make_buffers()
        shell = Shell(Vfs.empty("v"), out, err)

        def raise_eof(prompt):
            """Имитирует конец ввода."""
            raise EOFError

        repl(shell, raise_eof)
        self.assertEqual(out.getvalue(), "\n")


if __name__ == "__main__":
    unittest.main()
