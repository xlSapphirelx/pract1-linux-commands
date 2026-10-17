"""Выполнение стартового скрипта эмулятора."""
from commands import EXIT_OK

COMMENT_PREFIX = "#"


def read_script(path):
    """Возвращает список строк скрипта."""
    with open(path, encoding="utf-8") as handle:
        return handle.read().splitlines()


def run_script(shell, path):
    """Выполняет команды скрипта последовательно.

    Строки скрипта выводятся вместе с приглашением, имитируя диалог
    с пользователем. Ошибочные строки пропускаются, о каждой ошибке
    сообщается в поток ошибок. Пустые строки и строки, начинающиеся
    с символа #, игнорируются. Возвращает число ошибок.
    """
    try:
        lines = read_script(path)
    except (OSError, UnicodeDecodeError) as exc:
        print(f"script: cannot read '{path}': {exc}", file=shell.err)
        return 1
    failed = 0
    for number, raw in enumerate(lines, start=1):
        line = raw.strip()
        if not line or line.startswith(COMMENT_PREFIX):
            continue
        print(f"{shell.prompt()}{line}", file=shell.out)
        status = shell.execute(line)
        if status != EXIT_OK:
            failed += 1
            print(
                f"script: {path}: line {number}: '{line}' "
                f"failed with status {status}",
                file=shell.err,
            )
        if not shell.running:
            break
    return failed
