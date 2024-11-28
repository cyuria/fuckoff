""" This file provide some utility functions for Arch Linux specific rules."""
import subprocess
from shutil import which
from .. import utils


@utils.memoize
def get_pkgfile(command: str) -> list[str]:
    """ Gets the packages that provide the given command using `pkgfile`.

    If the command is of the form `sudo foo`, searches for the `foo` command
    instead.
    """
    try:
        command = command.strip().removeprefix('sudo ')
        command = command.split(" ")[0]

        packages = subprocess.check_output(
            ['pkgfile', '-b', '-v', command],
            universal_newlines=True,
            stderr=utils.DEVNULL
        ).splitlines()

        return [package.split()[0] for package in packages]
    except subprocess.CalledProcessError as err:
        if err.returncode != 1 or err.output != "":
            raise err
        return []


def archlinux_env():
    if which('yay'):
        pacman = 'yay'
    elif which('pikaur'):
        pacman = 'pikaur'
    elif which('yaourt'):
        pacman = 'yaourt'
    elif which('pacman'):
        pacman = 'sudo pacman'
    else:
        return False, None

    enabled_by_default = which('pkgfile')

    return enabled_by_default, pacman
