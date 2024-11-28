import re

from shutil import which
from subprocess import Popen, PIPE

from ..utils import memoize, eager

npm_available = bool(which('npm'))


@memoize
@eager
def get_scripts():
    """Get custom npm scripts."""
    proc = Popen(['npm', 'run-script'], stdout=PIPE, text=True)
    proc.wait()
    if proc.stdout is None:
        return

    lines = iter(proc.stdout.readlines())
    try:
        next(
            None for line in lines
            if 'available via `npm run-script`:' in line
        )
    except StopIteration:
        return

    yield from (
        line.strip().split(' ')[0]
        for line in lines
        if re.match('^  [^ ]+', line)
    )
