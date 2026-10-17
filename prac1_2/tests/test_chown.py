"""Тесты команды chown (этап 5)."""
import unittest

import helpers
from base import CommandTestCase
from commands import EXIT_ERROR, EXIT_OK
from vfs import iter_nodes, load_directory


class ChownTest(CommandTestCase):
    """Команда chown и её видимый результат."""

    def owner_of(self, path):
        """Возвращает пару (владелец, группа) узла."""
        node = self.shell.vfs.lookup(path)
        return node.owner, node.group

    def test_change_owner_only(self):
        """chown OWNER меняет только владельца."""
        self.assertEqual(self.run_line("chown alice /a/top.txt")[0], EXIT_OK)
        self.assertEqual(self.owner_of("/a/top.txt"), ("alice", "user"))

    def test_change_owner_and_group(self):
        """chown OWNER:GROUP меняет обе части."""
        self.run_line("chown bob:staff /a/top.txt")
        self.assertEqual(self.owner_of("/a/top.txt"), ("bob", "staff"))

    def test_change_group_only(self):
        """chown :GROUP меняет только группу."""
        self.run_line("chown :staff /a/top.txt")
        self.assertEqual(self.owner_of("/a/top.txt"), ("user", "staff"))

    def test_owner_with_empty_group(self):
        """chown OWNER: не меняет группу."""
        self.run_line("chown carol: /a/top.txt")
        self.assertEqual(self.owner_of("/a/top.txt"), ("carol", "user"))

    def test_multiple_paths(self):
        """Можно указать несколько путей."""
        self.run_line("chown dave /a/top.txt /docs/readme.txt")
        self.assertEqual(self.owner_of("/a/top.txt")[0], "dave")
        self.assertEqual(self.owner_of("/docs/readme.txt")[0], "dave")

    def test_directory_without_recursion(self):
        """Без -R содержимое каталога не меняется."""
        self.run_line("chown eve /a")
        self.assertEqual(self.owner_of("/a")[0], "eve")
        self.assertEqual(self.owner_of("/a/top.txt")[0], "user")

    def test_recursive(self):
        """С -R меняется весь каталог рекурсивно."""
        self.run_line("chown -R eve:ops /a")
        for node in iter_nodes(self.shell.vfs.lookup("/a")):
            self.assertEqual((node.owner, node.group), ("eve", "ops"))
        self.assertEqual(self.owner_of("/docs")[0], "user")

    def test_visible_in_ls_long(self):
        """Результат виден в ls -l."""
        self.run_line("chown frank:team /a/top.txt")
        _, out, _ = self.run_line("ls -l /a/top.txt")
        self.assertIn(" frank team ", out)

    def test_relative_path(self):
        """Относительные пути считаются от текущего каталога."""
        self.run_line("cd a")
        self.run_line("chown gina top.txt")
        self.assertEqual(self.owner_of("/a/top.txt")[0], "gina")

    def test_errors(self):
        """Ошибки: нет операндов, нет пути, плохой флаг и владелец."""
        cases = {
            "chown": "missing operand",
            "chown alice": "missing operand after 'alice'",
            "chown -x alice /a": "invalid option -- 'x'",
            "chown : /a": "invalid user: ':'",
            "chown alice /nope": "cannot access '/nope'",
        }
        for line, text in cases.items():
            status, _, err = self.run_line(line)
            self.assertEqual(status, EXIT_ERROR, line)
            self.assertIn(text, err, line)

    def test_error_does_not_stop_other_paths(self):
        """Ошибка по одному пути не мешает остальным."""
        status, _, _ = self.run_line("chown hal /nope /a/top.txt")
        self.assertEqual(status, EXIT_ERROR)
        self.assertEqual(self.owner_of("/a/top.txt")[0], "hal")

    def test_changes_only_in_memory(self):
        """После chown повторная загрузка с диска даёт прежних владельцев."""
        self.run_line("chown -R zed /")
        fresh = load_directory(helpers.example_vfs("deep"))
        self.assertEqual(fresh.lookup("/a/top.txt").owner, "user")


if __name__ == "__main__":
    unittest.main()
