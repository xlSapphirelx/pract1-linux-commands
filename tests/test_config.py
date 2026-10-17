"""Тесты параметров командной строки."""
import unittest

import helpers  # noqa: F401
from config import format_debug, parse_args, vfs_display_name


class ConfigTest(unittest.TestCase):
    """Проверки разбора параметров и отладочного вывода."""

    def test_defaults(self):
        """Без параметров значения не заданы."""
        args = parse_args([])
        self.assertIsNone(args.vfs)
        self.assertIsNone(args.script)

    def test_both_options(self):
        """Оба параметра разбираются."""
        args = parse_args(["--vfs", "/tmp/v", "--script", "s.txt"])
        self.assertEqual(args.vfs, "/tmp/v")
        self.assertEqual(args.script, "s.txt")

    def test_unknown_option_exits(self):
        """Неизвестный параметр завершает разбор с кодом 2."""
        with self.assertRaises(SystemExit) as ctx:
            parse_args(["--bogus"])
        self.assertEqual(ctx.exception.code, 2)

    def test_debug_lists_all_parameters(self):
        """Отладочный вывод содержит все параметры."""
        text = "\n".join(format_debug(parse_args(["--vfs", "x"])))
        self.assertIn("vfs = x", text)
        self.assertIn("script = <not set>", text)

    def test_vfs_display_name(self):
        """Имя VFS — последняя папка пути."""
        self.assertEqual(vfs_display_name("/a/b/"), "b")
        self.assertEqual(vfs_display_name("data"), "data")
        self.assertEqual(vfs_display_name(None), "vfs")


if __name__ == "__main__":
    unittest.main()
