"""Тесты разбора строки ввода."""
import unittest

import helpers  # noqa: F401
from cmdparser import parse_line


class ParseLineTest(unittest.TestCase):
    """Проверки parse_line."""

    def test_empty_line(self):
        """Пустая и пробельная строки не содержат команды."""
        self.assertEqual(parse_line(""), (None, []))
        self.assertEqual(parse_line("   \t "), (None, []))

    def test_command_only(self):
        """Строка из одного слова — команда без аргументов."""
        self.assertEqual(parse_line("ls"), ("ls", []))

    def test_arguments_split_by_spaces(self):
        """Аргументы разделяются любым количеством пробелов."""
        self.assertEqual(parse_line("ls  -l   /a"), ("ls", ["-l", "/a"]))

    def test_quotes_are_not_special(self):
        """Простой парсер не обрабатывает кавычки."""
        self.assertEqual(parse_line('cd "a b"'), ("cd", ['"a', 'b"']))


if __name__ == "__main__":
    unittest.main()
