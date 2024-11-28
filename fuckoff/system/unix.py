import colorama
import sys
import termios
import tty

from shutil import which

from .. import const

init_output = colorama.init


def getch() -> str:
    fd = sys.stdin.fileno()
    old = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        return sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old)


def get_key() -> str:
    match getch():
        case _ as ch if ch in const.KEY_MAPPING:
            return const.KEY_MAPPING[ch]
        case '\x1b':
            if getch() != '[':
                return '\x1b'
            match getch():
                case 'A':
                    return const.KEY_UP
                case 'B':
                    return const.KEY_DOWN
                case _:
                    return '\x1b'
        case _ as ch:
            return ch


def open_command(arg: str) -> str:
    if which('xdg-open'):
        return 'xdg-open ' + arg
    return 'open ' + arg
