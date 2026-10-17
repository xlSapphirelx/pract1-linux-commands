"""Виртуальная файловая система, целиком хранящаяся в памяти."""
import os
from dataclasses import dataclass, field

from config import DEFAULT_VFS_NAME, vfs_display_name

SEPARATOR = "/"
PARENT = ".."
CURRENT = "."
DEFAULT_OWNER = "user"
DEFAULT_GROUP = "user"


class VfsError(Exception):
    """Ошибка работы с виртуальной файловой системой."""


@dataclass
class Node:
    """Узел VFS: файл (с содержимым) или каталог (с потомками)."""

    name: str
    is_dir: bool
    data: bytes = b""
    owner: str = DEFAULT_OWNER
    group: str = DEFAULT_GROUP
    mtime: float = 0.0
    children: dict = field(default_factory=dict)

    @property
    def size(self):
        """Размер содержимого файла в байтах."""
        return len(self.data)


def iter_nodes(node):
    """Обходит узел и всех его потомков (сначала родитель)."""
    yield node
    for name in sorted(node.children):
        yield from iter_nodes(node.children[name])


class Vfs:
    """Дерево узлов в памяти и текущий каталог."""

    def __init__(self, root, name=DEFAULT_VFS_NAME):
        """Создаёт VFS с корневым каталогом root и именем name."""
        self.root = root
        self.name = name
        self.cwd = []

    @classmethod
    def empty(cls, name=DEFAULT_VFS_NAME):
        """Создаёт пустую VFS, содержащую только корневой каталог."""
        return cls(Node("", True), name)

    def split(self, path):
        """Возвращает абсолютный путь как список компонентов."""
        parts = [] if path.startswith(SEPARATOR) else list(self.cwd)
        for part in path.split(SEPARATOR):
            if part in ("", CURRENT):
                continue
            if part == PARENT:
                if parts:
                    parts.pop()
            else:
                parts.append(part)
        return parts

    def lookup(self, path):
        """Находит узел по пути или бросает VfsError."""
        node = self.root
        for part in self.split(path):
            if not node.is_dir:
                raise VfsError("Not a directory")
            if part not in node.children:
                raise VfsError("No such file or directory")
            node = node.children[part]
        return node

    def cwd_path(self):
        """Текущий каталог в виде абсолютного пути."""
        return SEPARATOR + SEPARATOR.join(self.cwd)

    def chdir(self, path):
        """Делает каталог path текущим."""
        if not self.lookup(path).is_dir:
            raise VfsError("Not a directory")
        self.cwd = self.split(path)

    def stats(self):
        """Возвращает пару (число каталогов, число файлов) без корня."""
        dirs = files = 0
        for node in iter_nodes(self.root):
            if node is self.root:
                continue
            if node.is_dir:
                dirs += 1
            else:
                files += 1
        return dirs, files


def _read_file(entry):
    """Читает содержимое файла с диска как байты."""
    try:
        with open(entry.path, "rb") as handle:
            return handle.read()
    except OSError as exc:
        raise VfsError(
            f"cannot read '{entry.path}': {exc.strerror}"
        ) from exc


def _make_node(entry):
    """Создаёт узел VFS для записи каталога на диске."""
    mtime = entry.stat(follow_symlinks=False).st_mtime
    if entry.is_dir(follow_symlinks=False):
        return Node(entry.name, True, mtime=mtime)
    return Node(entry.name, False, data=_read_file(entry), mtime=mtime)


def _is_supported(entry):
    """Поддерживаются только обычные файлы и каталоги без ссылок."""
    if entry.is_symlink():
        return False
    return entry.is_file() or entry.is_dir()


def _fill(node, disk_path):
    """Рекурсивно заполняет каталог node содержимым disk_path."""
    try:
        with os.scandir(disk_path) as scanner:
            entries = sorted(scanner, key=lambda item: item.name)
    except OSError as exc:
        raise VfsError(
            f"cannot read '{disk_path}': {exc.strerror}"
        ) from exc
    for entry in entries:
        if not _is_supported(entry):
            continue
        child = _make_node(entry)
        node.children[entry.name] = child
        if child.is_dir:
            _fill(child, entry.path)


def load_directory(path):
    """Загружает директорию с диска в VFS (только чтение с диска)."""
    if not os.path.isdir(path):
        raise VfsError(f"'{path}' is not a directory")
    root = Node("", True, mtime=os.stat(path).st_mtime)
    _fill(root, path)
    return Vfs(root, vfs_display_name(path))
