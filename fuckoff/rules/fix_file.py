import re
import os
from typing import Pattern

from fuckoff.shells import shell
from fuckoff.utils import memoize


# for the sake of readability do not use named groups above
def _make_pattern(pattern: str) -> Pattern[str]:
    pattern = pattern.replace('{file}', '(?P<file>[^:\n]+)') \
                     .replace('{line}', '(?P<line>[0-9]+)') \
                     .replace('{col}', '(?P<col>[0-9]+)')
    return re.compile(pattern, re.MULTILINE)


# order is important: only the first match is considered
patterns: list[Pattern[str]] = [_make_pattern(p) for p in (
    # js, node:
    '^    at {file}:{line}:{col}',
    # cargo:
    '^   {file}:{line}:{col}',
    # python, fuckoff:
    '^  File "{file}", line {line}',
    # awk:
    '^awk: {file}:{line}:',
    # git
    '^fatal: bad config file line {line} in {file}',
    # llc:
    '^llc: {file}:{line}:{col}:',
    # lua:
    '^lua: {file}:{line}:',
    # fish:
    '^{file} \\(line {line}\\):',
    # bash, sh, ssh:
    '^{file}: line {line}: ',
    # cargo, clang, gcc, go, pep8, rustc:
    '^{file}:{line}:{col}',
    # ghc, make, ruby, zsh:
    '^{file}:{line}:',
    # perl:
    'at {file} line {line}',
)]


@memoize
def _search(output):
    for pattern in patterns:
        m = pattern.search(output)
        if m and os.path.isfile(m.group('file')):
            return m


def match(command):
    if 'EDITOR' not in os.environ:
        return False

    return _search(command.output) is not None


def get_new_command(command):
    m = _search(command.output)
    if m is None:
        raise Exception('Rule incorrectly matched')

    # Note: there does not seem to be a standard for columns, so they are just
    # ignored. If you would like to add columns, make your own rule
    return [
        shell.and_(
            f"{os.environ['EDITOR']} {m.group('file')} +{m.group('line')}",
            command.script
        )
    ]
