"""Тесты виртуальной файловой системы (этап 3)."""
import os
import tempfile
import unittest

import helpers
from vfs import Node, Vfs, VfsError, iter_nodes, load_directory

BINARY = bytes(range(256))


def snapshot(path):
    """Снимок диска: список (путь, содержимое) для сравнения."""
    result = []
    for base, dirs, files in os.walk(path):
        dirs.sort()
        for name in sorted(files):
            full = os.path.join(base, name)
            with open(full, "rb") as handle:
                result.append((full, handle.read()))
    return result


class LoadTest(unittest.TestCase):
    """Загрузка VFS из директории на диске."""

    def test_minimal(self):
        """Минимальная VFS: один файл в корне."""
        vfs = load_directory(helpers.example_vfs("minimal"))
        self.assertEqual(vfs.name, "minimal")
        self.assertEqual(vfs.stats(), (0, 1))

    def test_several_files(self):
        """VFS с несколькими файлами."""
        vfs = load_directory(helpers.example_vfs("files"))
        self.assertEqual(vfs.stats(), (0, 3))
        self.assertIn(b"alpha", vfs.lookup("/data.csv").data)

    def test_three_levels(self):
        """VFS глубиной не менее трёх уровней."""
        vfs = load_directory(helpers.example_vfs("deep"))
        node = vfs.lookup("/a/b/c/deep.txt")
        self.assertFalse(node.is_dir)
        self.assertEqual(vfs.stats(), (5, 6))

    def test_not_a_directory(self):
        """Файл и несуществующий путь не являются VFS."""
        file_path = os.path.join(helpers.example_vfs("minimal"), "hello.txt")
        with self.assertRaises(VfsError):
            load_directory(file_path)
        with self.assertRaises(VfsError):
            load_directory(file_path + ".missing")

    def test_binary_data_is_preserved(self):
        """Двоичные данные читаются без искажений."""
        with tempfile.TemporaryDirectory() as tmp:
            with open(os.path.join(tmp, "bin.dat"), "wb") as handle:
                handle.write(BINARY)
            vfs = load_directory(tmp)
            self.assertEqual(vfs.lookup("bin.dat").data, BINARY)

    def test_disk_is_not_modified(self):
        """Изменения в памяти не затрагивают диск."""
        path = helpers.example_vfs("deep")
        before = snapshot(path)
        vfs = load_directory(path)
        vfs.lookup("/a/top.txt").data = b"changed"
        vfs.lookup("/a").children.clear()
        self.assertEqual(snapshot(path), before)


class PathTest(unittest.TestCase):
    """Разрешение путей и текущий каталог."""

    def setUp(self):
        """Загружает VFS с тремя уровнями вложенности."""
        self.vfs = load_directory(helpers.example_vfs("deep"))

    def test_split_handles_dots(self):
        """Компоненты . и .. обрабатываются, выше корня не выйти."""
        self.assertEqual(self.vfs.split("/a/./b/../b/c"), ["a", "b", "c"])
        self.assertEqual(self.vfs.split("/../.."), [])

    def test_chdir_and_relative_paths(self):
        """Относительные пути считаются от текущего каталога."""
        self.vfs.chdir("a/b")
        self.assertEqual(self.vfs.cwd_path(), "/a/b")
        self.assertEqual(self.vfs.lookup("c/deep.txt").name, "deep.txt")
        self.vfs.chdir("../..")
        self.assertEqual(self.vfs.cwd_path(), "/")

    def test_lookup_errors(self):
        """Ошибки: нет файла; файл используется как каталог."""
        with self.assertRaises(VfsError):
            self.vfs.lookup("/nope")
        with self.assertRaises(VfsError):
            self.vfs.lookup("/a/top.txt/x")

    def test_chdir_to_file_fails(self):
        """cd в файл невозможен, текущий каталог не меняется."""
        with self.assertRaises(VfsError):
            self.vfs.chdir("/a/top.txt")
        self.assertEqual(self.vfs.cwd_path(), "/")

    def test_iter_nodes_order(self):
        """Обход начинается с корня и включает все узлы."""
        nodes = list(iter_nodes(self.vfs.root))
        self.assertIs(nodes[0], self.vfs.root)
        self.assertEqual(len(nodes), 12)

    def test_empty_vfs(self):
        """Пустая VFS содержит только корень."""
        vfs = Vfs.empty("x")
        self.assertEqual(vfs.stats(), (0, 0))
        self.assertIsInstance(vfs.root, Node)


if __name__ == "__main__":
    unittest.main()
