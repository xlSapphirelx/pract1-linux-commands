"""Тесты запуска эмулятора как отдельного процесса."""
import os
import subprocess
import sys
import unittest

import helpers

MAIN = os.path.join(helpers.SRC, "main.py")
EXIT_USAGE = 2


def run_cli(*args):
    """Запускает эмулятор с пустым вводом и возвращает результат."""
    return subprocess.run(
        [sys.executable, MAIN, *args],
        input="",
        capture_output=True,
        text=True,
        check=False,
    )


class CliTest(unittest.TestCase):
    """Проверки параметров запуска."""

    def test_debug_output_of_parameters(self):
        """При запуске выводятся все заданные параметры."""
        result = run_cli("--vfs", helpers.example_vfs("minimal"))
        self.assertEqual(result.returncode, 0)
        self.assertIn("vfs = ", result.stdout)
        self.assertIn("script = <not set>", result.stdout)

    def test_unknown_option(self):
        """Неизвестный параметр даёт код 2."""
        self.assertEqual(run_cli("--zzz").returncode, EXIT_USAGE)

    def test_vfs_is_loaded(self):
        """VFS загружается из директории, приглашение содержит её имя."""
        result = run_cli("--vfs", helpers.example_vfs("deep"))
        self.assertEqual(result.returncode, 0)
        self.assertIn("loaded: 5 dirs, 6 files", result.stdout)
        self.assertIn("deep:/$", result.stdout)

    def test_missing_vfs_directory(self):
        """Несуществующая директория VFS даёт код 2 и сообщение."""
        result = run_cli("--vfs", "no/such/dir")
        self.assertEqual(result.returncode, EXIT_USAGE)
        self.assertIn("is not a directory", result.stderr)

    def test_script_error_is_reported(self):
        """Ошибка скрипта сообщается в stderr."""
        result = run_cli("--script", "no/such/script.txt")
        self.assertIn("cannot read", result.stderr)


if __name__ == "__main__":
    unittest.main()
