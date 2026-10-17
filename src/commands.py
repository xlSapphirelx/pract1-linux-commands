"""Реализации команд эмулятора."""
import time

from vfs import VfsError, iter_nodes

EXIT_OK = 0
EXIT_ERROR = 1
EXIT_NOT_FOUND = 127

ROOT_PATH = "/"
LS_FLAGS = "la"
CHOWN_FLAGS = "R"
DIR_PERMS = "drwxr-xr-x"
FILE_PERMS = "-rw-r--r--"
DIR_SIZE = 4096
LIST_TIME_FORMAT = "%b %d %H:%M"
DEFAULT_DATE_FORMAT = "%a %b %d %H:%M:%S %Z %Y"
DEFAULT_TAIL_LINES = 10


class UsageError(Exception):
    """Неверные параметры команды."""


def fail(shell, message, status=EXIT_ERROR):
    """Выводит сообщение об ошибке и возвращает код завершения."""
    print(message, file=shell.err)
    return status


def parse_flags(args, allowed):
    """Отделяет односимвольные флаги (-l, -la) от остальных аргументов.

    Возвращает пару (множество флагов, список остальных аргументов).
    """
    flags = set()
    rest = list(args)
    while rest and rest[0].startswith("-") and rest[0] != "-":
        token = rest.pop(0)
        if token == "--":
            break
        for char in token[1:]:
            if char not in allowed:
                raise UsageError(f"invalid option -- '{char}'")
            flags.add(char)
    return flags, rest


def read_text(shell, path):
    """Возвращает содержимое файла VFS как текст."""
    node = shell.vfs.lookup(path)
    if node.is_dir:
        raise VfsError("Is a directory")
    return node.data.decode("utf-8", errors="replace")


def cmd_exit(shell, args):
    """exit: завершает работу эмулятора."""
    shell.running = False
    return EXIT_OK


def cmd_cd(shell, args):
    """cd [ПУТЬ]: меняет текущий каталог (без аргумента — корень)."""
    if len(args) > 1:
        return fail(shell, "cd: too many arguments")
    target = args[0] if args else ROOT_PATH
    try:
        shell.vfs.chdir(target)
    except VfsError as exc:
        return fail(shell, f"cd: {target}: {exc}")
    return EXIT_OK


def _format_entry(name, node, long_format):
    """Формирует строку вывода ls для одного узла."""
    if not long_format:
        return name
    perms = DIR_PERMS if node.is_dir else FILE_PERMS
    size = DIR_SIZE if node.is_dir else node.size
    stamp = time.strftime(LIST_TIME_FORMAT, time.localtime(node.mtime))
    return f"{perms} {node.owner} {node.group} {size:>6} {stamp} {name}"


def _visible_children(node, show_all):
    """Возвращает отсортированные пары (имя, узел) содержимого каталога."""
    items = sorted(node.children.items())
    return [(n, c) for n, c in items if show_all or not n.startswith(".")]


def _resolve_targets(shell, paths):
    """Делит пути на файлы и каталоги; возвращает также код ошибки."""
    files, dirs, status = [], [], EXIT_OK
    for path in paths:
        try:
            node = shell.vfs.lookup(path)
        except VfsError as exc:
            status = fail(shell, f"ls: cannot access '{path}': {exc}")
            continue
        (dirs if node.is_dir else files).append((path, node))
    return files, dirs, status


def cmd_ls(shell, args):
    """ls [-l] [-a] [ПУТЬ...]: выводит содержимое каталогов и файлы."""
    try:
        flags, paths = parse_flags(args, LS_FLAGS)
    except UsageError as exc:
        return fail(shell, f"ls: {exc}")
    paths = paths or ["."]
    files, dirs, status = _resolve_targets(shell, paths)
    long_format = "l" in flags
    blocks = []
    if files:
        blocks.append([_format_entry(p, n, long_format) for p, n in files])
    for path, node in dirs:
        entries = _visible_children(node, "a" in flags)
        lines = [_format_entry(n, c, long_format) for n, c in entries]
        if len(paths) > 1:
            lines.insert(0, f"{path}:")
        blocks.append(lines)
    text = "\n\n".join("\n".join(block) for block in blocks if block)
    if text:
        print(text, file=shell.out)
    return status


def cmd_date(shell, args):
    """date [-u] [+ФОРМАТ]: выводит текущие дату и время."""
    utc = False
    fmt = None
    for arg in args:
        if arg == "-u":
            utc = True
        elif arg.startswith("+") and fmt is None:
            fmt = arg[1:]
        elif arg.startswith("+"):
            return fail(shell, f"date: extra operand '{arg}'")
        else:
            return fail(shell, f"date: invalid date '{arg}'")
    fmt = DEFAULT_DATE_FORMAT if fmt is None else fmt
    moment = shell.clock()
    if utc:
        fmt = fmt.replace("%Z", "UTC")
        stamp = time.gmtime(moment)
    else:
        stamp = time.localtime(moment)
    print(time.strftime(fmt, stamp), file=shell.out)
    return EXIT_OK


def _parse_count(value):
    """Преобразует значение параметра -n в неотрицательное число."""
    if not (value.isascii() and value.isdigit()):
        raise UsageError(f"invalid number of lines: '{value}'")
    return int(value)


def _parse_tail_args(args):
    """Разбирает параметр -n N (или -nN); возвращает (N, файлы)."""
    count = DEFAULT_TAIL_LINES
    rest = list(args)
    while rest and rest[0].startswith("-n"):
        value = rest.pop(0)[2:]
        if not value:
            if not rest:
                raise UsageError("option requires an argument -- 'n'")
            value = rest.pop(0)
        count = _parse_count(value)
    return count, rest


def cmd_tail(shell, args):
    """tail [-n N] ФАЙЛ...: выводит последние N (по умолчанию 10) строк."""
    try:
        count, paths = _parse_tail_args(args)
    except UsageError as exc:
        return fail(shell, f"tail: {exc}")
    if not paths:
        return fail(shell, "tail: missing file operand")
    status = EXIT_OK
    for index, path in enumerate(paths):
        try:
            text = read_text(shell, path)
        except VfsError as exc:
            message = f"tail: cannot open '{path}' for reading: {exc}"
            status = fail(shell, message)
            continue
        if len(paths) > 1:
            print(("\n" if index else "") + f"==> {path} <==", file=shell.out)
        lines = text.splitlines()
        for line in lines[len(lines) - min(count, len(lines)):]:
            print(line, file=shell.out)
    return status


def _parse_owner(spec):
    """Разбирает ВЛАДЕЛЕЦ[:ГРУППА]; пустая часть означает «не менять»."""
    owner, _, group = spec.partition(":")
    if not owner and not group:
        raise UsageError(f"invalid user: '{spec}'")
    return owner or None, group or None


def _apply_owner(node, owner, group):
    """Меняет владельца и/или группу узла VFS (только в памяти)."""
    if owner is not None:
        node.owner = owner
    if group is not None:
        node.group = group


def cmd_chown(shell, args):
    """chown [-R] ВЛАДЕЛЕЦ[:ГРУППА] ПУТЬ...: меняет владельца в VFS."""
    try:
        flags, rest = parse_flags(args, CHOWN_FLAGS)
        if not rest:
            raise UsageError("missing operand")
        owner, group = _parse_owner(rest[0])
    except UsageError as exc:
        return fail(shell, f"chown: {exc}")
    if len(rest) == 1:
        return fail(shell, f"chown: missing operand after '{rest[0]}'")
    status = EXIT_OK
    for path in rest[1:]:
        try:
            node = shell.vfs.lookup(path)
        except VfsError as exc:
            status = fail(shell, f"chown: cannot access '{path}': {exc}")
            continue
        for target in iter_nodes(node) if "R" in flags else [node]:
            _apply_owner(target, owner, group)
    return status


COMMANDS = {
    "ls": cmd_ls,
    "cd": cmd_cd,
    "date": cmd_date,
    "tail": cmd_tail,
    "chown": cmd_chown,
    "exit": cmd_exit,
}
