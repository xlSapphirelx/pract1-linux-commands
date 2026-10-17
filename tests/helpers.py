"""Общие вспомогательные функции тестов."""
import io
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
sys.path.insert(0, SRC)


def make_buffers():
    """Возвращает пару буферов (stdout, stderr) для оболочки."""
    return io.StringIO(), io.StringIO()
