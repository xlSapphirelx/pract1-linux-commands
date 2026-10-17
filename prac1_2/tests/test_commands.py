"""Тесты команд ls, cd, date, tail (этап 4)."""
import os
import tempfile
import unittest

from base import CommandTestCase
from commands import EXIT_ERROR, EXIT_OK
from vfs import load_directory


class LsTest(CommandTestCase):
    """Команда ls."""

    def test_root_listing_hides_dotfiles(self):
        """Без -a скрытые файлы не показываются."""
        status, out, _ = self.run_line("ls")
        self.assertEqual(status, EXIT_OK)
        self.assertEqual(out, "a\ndocs\n")

    def test_all_flag_shows_hidden(self):
        """-a показывает скрытые файлы."""
        _, out, _ = self.run_line("ls -a")
        self.assertEqual(out, ".hidden\na\ndocs\n")

    def test_long_format(self):
        """-l показывает права, владельца, размер и имя."""
        _, out, _ = self.run_line("ls -l /a/top.txt")
        self.assertTrue(out.startswith("-rw-r--r-- user user"))
        self.assertTrue(out.endswith(" /a/top.txt\n"))
        self.assertIn(" 14 ", out)

    def test_combined_flags(self):
        """Флаги можно объединять: -la."""
        _, out, _ = self.run_line("ls -la")
        self.assertEqual(len(out.splitlines()), 3)

    def test_relative_path_and_dotdot(self):
        """Относительные пути и .. работают."""
        self.run_line("cd a/b")
        _, out, _ = self.run_line("ls ..")
        self.assertEqual(out, "b\ntop.txt\n")

    def test_multiple_paths_have_headers(self):
        """Несколько путей: файлы, затем каталоги с заголовками."""
        _, out, _ = self.run_line("ls /docs /a/top.txt /a/b")
        self.assertEqual(
            out, "/a/top.txt\n\n/docs:\nlog\nreadme.txt\n\n/a/b:\nc\nmid.txt\n"
        )

    def test_missing_path(self):
        """Несуществующий путь даёт ошибку, остальные выводятся."""
        status, out, err = self.run_line("ls /nope /docs")
        self.assertEqual(status, EXIT_ERROR)
        self.assertIn("cannot access '/nope'", err)
        self.assertIn("readme.txt", out)

    def test_invalid_option(self):
        """Неизвестный флаг — ошибка."""
        status, _, err = self.run_line("ls -z")
        self.assertEqual(status, EXIT_ERROR)
        self.assertIn("invalid option -- 'z'", err)

    def test_empty_directory_prints_nothing(self):
        """Пустой каталог ничего не выводит."""
        self.shell.vfs.lookup("/docs/log").children.clear()
        _, out, _ = self.run_line("ls /docs/log")
        self.assertEqual(out, "")


class CdTest(CommandTestCase):
    """Команда cd."""

    def test_cd_changes_prompt(self):
        """cd меняет текущий каталог и приглашение."""
        self.assertEqual(self.run_line("cd a/b/c")[0], EXIT_OK)
        self.assertEqual(self.shell.prompt(), "deep:/a/b/c$ ")

    def test_cd_without_args_goes_to_root(self):
        """cd без аргументов возвращает в корень."""
        self.run_line("cd /docs")
        self.run_line("cd")
        self.assertEqual(self.shell.vfs.cwd_path(), "/")

    def test_cd_dotdot_stops_at_root(self):
        """Выше корня подняться нельзя."""
        self.run_line("cd ../../..")
        self.assertEqual(self.shell.vfs.cwd_path(), "/")

    def test_cd_missing(self):
        """cd в несуществующий каталог — ошибка."""
        status, _, err = self.run_line("cd nope")
        self.assertEqual(status, EXIT_ERROR)
        self.assertIn("cd: nope: No such file or directory", err)

    def test_cd_to_file(self):
        """cd в файл — ошибка."""
        status, _, err = self.run_line("cd a/top.txt")
        self.assertEqual(status, EXIT_ERROR)
        self.assertIn("Not a directory", err)

    def test_cd_too_many_args(self):
        """Лишние аргументы cd — ошибка."""
        self.assertEqual(self.run_line("cd a b")[0], EXIT_ERROR)


class DateTest(CommandTestCase):
    """Команда date."""

    def test_default_format_utc(self):
        """Формат по умолчанию, время UTC."""
        _, out, _ = self.run_line("date -u")
        self.assertEqual(out, "Thu Jan 01 00:00:00 UTC 1970\n")

    def test_custom_format(self):
        """+ФОРМАТ задаёт вывод."""
        _, out, _ = self.run_line("date -u +%Y-%m-%d")
        self.assertEqual(out, "1970-01-01\n")

    def test_local_time_without_flag(self):
        """Без -u выводится непустая строка."""
        status, out, _ = self.run_line("date")
        self.assertEqual(status, EXIT_OK)
        self.assertIn("1970", out)

    def test_invalid_argument(self):
        """Неверный аргумент — ошибка."""
        status, _, err = self.run_line("date tomorrow")
        self.assertEqual(status, EXIT_ERROR)
        self.assertIn("invalid date 'tomorrow'", err)

    def test_extra_operand(self):
        """Два формата — ошибка."""
        self.assertEqual(self.run_line("date +%Y +%m")[0], EXIT_ERROR)


class TailTest(CommandTestCase):
    """Команда tail."""

    log = "/docs/log/app.log"

    def test_default_ten_lines(self):
        """По умолчанию выводятся последние 10 строк."""
        _, out, _ = self.run_line(f"tail {self.log}")
        lines = out.splitlines()
        self.assertEqual(len(lines), 10)
        self.assertTrue(lines[-1].endswith("event 12"))
        self.assertTrue(lines[0].endswith("event 3"))

    def test_n_option_forms(self):
        """-n N и -nN эквивалентны."""
        first = self.run_line(f"tail -n 2 {self.log}")[1]
        second = self.run_line(f"tail -n2 {self.log}")[1]
        self.assertEqual(first, second)
        self.assertEqual(len(first.splitlines()), 2)

    def test_zero_lines(self):
        """-n 0 ничего не выводит."""
        self.assertEqual(self.run_line(f"tail -n 0 {self.log}")[1], "")

    def test_more_lines_than_file(self):
        """Если строк меньше N, выводится весь файл."""
        _, out, _ = self.run_line("tail -n 99 /a/b/c/deep.txt")
        self.assertEqual(out, "Level 4 file.\nSecond line.\n")

    def test_multiple_files_have_headers(self):
        """Для нескольких файлов выводятся заголовки."""
        _, out, _ = self.run_line("tail -n 1 /a/top.txt /a/b/mid.txt")
        self.assertEqual(
            out,
            "==> /a/top.txt <==\nLevel 2 file.\n\n"
            "==> /a/b/mid.txt <==\nLevel 3 file.\n",
        )

    def test_errors(self):
        """Ошибки: нет файла, каталог, нет операнда, плохое N."""
        cases = {
            "tail /nope": "cannot open '/nope'",
            "tail /a": "Is a directory",
            "tail": "missing file operand",
            "tail -n x /a/top.txt": "invalid number of lines: 'x'",
            "tail -n": "option requires an argument",
        }
        for line, text in cases.items():
            status, _, err = self.run_line(line)
            self.assertEqual(status, EXIT_ERROR, line)
            self.assertIn(text, err, line)

    def test_binary_file_does_not_crash(self):
        """Двоичные данные декодируются с заменой символов."""
        with tempfile.TemporaryDirectory() as tmp:
            with open(os.path.join(tmp, "b.bin"), "wb") as handle:
                handle.write(b"ok\n\xff\xfe\nlast\n")
            self.shell.vfs = load_directory(tmp)
            status, out, _ = self.run_line("tail -n 2 b.bin")
        self.assertEqual(status, EXIT_OK)
        self.assertTrue(out.endswith("last\n"))


if __name__ == "__main__":
    unittest.main()
