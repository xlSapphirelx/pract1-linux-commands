"""Реализации команд эмулятора."""

EXIT_OK = 0
EXIT_ERROR = 1
EXIT_NOT_FOUND = 127


def _print_stub(shell, name, args):
    """Выводит имя команды-заглушки и её аргументы."""
    print(f"{name} args={args}", file=shell.out)
    return EXIT_OK


def cmd_ls(shell, args):
    """Заглушка ls: выводит имя и аргументы."""
    return _print_stub(shell, "ls", args)


def cmd_cd(shell, args):
    """Заглушка cd: выводит имя и аргументы."""
    return _print_stub(shell, "cd", args)


def cmd_exit(shell, args):
    """Завершает работу эмулятора."""
    shell.running = False
    return EXIT_OK


COMMANDS = {
    "ls": cmd_ls,
    "cd": cmd_cd,
    "exit": cmd_exit,
}
