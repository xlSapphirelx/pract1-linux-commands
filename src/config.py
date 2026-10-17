"""Параметры командной строки эмулятора."""
import argparse
import os

DEFAULT_VFS_NAME = "vfs"
NOT_SET = "<not set>"


def build_parser():
    """Создаёт разборщик параметров командной строки."""
    parser = argparse.ArgumentParser(
        prog="main.py",
        description="Эмулятор оболочки UNIX-подобной ОС с VFS.",
    )
    parser.add_argument(
        "--vfs",
        metavar="PATH",
        help="путь к физическому расположению VFS",
    )
    parser.add_argument(
        "--script",
        metavar="PATH",
        help="путь к стартовому скрипту",
    )
    return parser


def parse_args(argv=None):
    """Разбирает параметры; при ошибке завершает процесс с кодом 2."""
    return build_parser().parse_args(argv)


def vfs_display_name(path):
    """Имя VFS для приглашения: имя последней папки пути."""
    if not path:
        return DEFAULT_VFS_NAME
    name = os.path.basename(os.path.normpath(path))
    return name or DEFAULT_VFS_NAME


def format_debug(args):
    """Возвращает строки отладочного вывода всех заданных параметров."""
    lines = ["[debug] launch parameters:"]
    for key, value in sorted(vars(args).items()):
        shown = NOT_SET if value is None else value
        lines.append(f"[debug]   {key} = {shown}")
    return lines
