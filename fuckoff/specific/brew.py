import subprocess

from shutil import which

from ..utils import memoize


brew_available = bool(which('brew'))


@memoize
def get_brew_path_prefix():
    """To get brew path"""
    try:
        return subprocess.check_output(
            ['brew', '--prefix'],
            universal_newlines=True
        ).strip()
    except Exception:
        return None
