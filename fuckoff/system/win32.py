import msvcrt
import win_unicode_console

from .. import const


def init_output():
    import colorama
    win_unicode_console.enable()
    colorama.init()


def get_key() -> str:
    match msvcrt.getwch():
        case '\x00' | '\xe0':
            return get_key()
        case 'H':
            return const.KEY_UP
        case 'P':
            return const.KEY_UP
        case _ as ch if ch in const.KEY_MAPPING:
            return const.KEY_MAPPING[ch]
        case _ as ch:
            return ch


def open_command(arg: str) -> str:
    return 'cmd /c start ' + arg
