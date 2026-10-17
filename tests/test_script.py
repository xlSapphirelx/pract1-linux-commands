"""Тесты выполнения стартового скрипта."""
import os
import tempfile
import unittest

import helpers
from script import run_script
from shell import Shell
from vfs import Vfs


class ScriptTest(unittest.TestCase):
    """Проверки run_script."""

    def setUp(self):
        """Создаёт оболочку и временный каталог для скриптов."""
        self.out, self.err = helpers.make_buffers()
        self.shell = helpers.add_echo(
            Shell(Vfs.empty("v"), self.out, self.err)
        )
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)

    def write(self, text):
        """Записывает скрипт и возвращает путь к нему."""
        path = os.path.join(self.tmp.name, "script.txt")
        with open(path, "w", encoding="utf-8") as handle:
            handle.write(text)
        return path

    def test_input_and_output_are_shown(self):
        """На экран выводится и ввод, и результат."""
        failed = run_script(self.shell, self.write("echo a\n"))
        self.assertEqual(failed, 0)
        self.assertEqual(self.out.getvalue(), "v:/$ echo a\na\n")

    def test_error_lines_are_skipped(self):
        """Ошибочная строка пропускается, остальные выполняются."""
        failed = run_script(self.shell, self.write("foo\necho ok\n"))
        self.assertEqual(failed, 1)
        self.assertIn("ok\n", self.out.getvalue())
        self.assertIn("line 1", self.err.getvalue())

    def test_comments_and_blank_lines(self):
        """Комментарии и пустые строки игнорируются."""
        run_script(self.shell, self.write("# note\n\n  \necho x\n"))
        self.assertEqual(self.out.getvalue(), "v:/$ echo x\nx\n")

    def test_exit_stops_script(self):
        """После exit остальные строки не выполняются."""
        run_script(self.shell, self.write("exit\necho never\n"))
        self.assertNotIn("never", self.out.getvalue())
        self.assertFalse(self.shell.running)

    def test_missing_script_is_reported(self):
        """Отсутствующий скрипт приводит к сообщению об ошибке."""
        path = os.path.join(self.tmp.name, "nope.txt")
        self.assertEqual(run_script(self.shell, path), 1)
        self.assertIn("cannot read", self.err.getvalue())


if __name__ == "__main__":
    unittest.main()
