import json
import os
from typing import Optional, TypedDict
import pyte
import socket

from shutil import get_terminal_size

from .. import const, logs


class Commands(TypedDict):
    command: str
    output: str


def _get_socket_path() -> str:
    return os.environ.get(const.SHELL_LOGGER_SOCKET_ENV, '')


def is_available() -> bool:
    """Returns `True` if shell logger socket available."""
    path = _get_socket_path()
    if not path:
        return False

    return os.path.exists(path)


def _get_last_n(n) -> list[Commands]:
    with socket.socket(socket.AF_UNIX) as client:
        client.connect(_get_socket_path())
        request = json.dumps({
            "type": "list",
            "count": n,
        }) + '\n'
        client.sendall(request.encode('utf-8'))
        response = client.makefile().readline()
        return json.loads(response)['commands']


def _get_output_lines(output: str) -> list[str]:
    lines = output.split('\n')
    screen = pyte.Screen(get_terminal_size().columns, len(lines))
    stream = pyte.Stream(screen)
    stream.feed('\n'.join(lines))
    return screen.display


def get_output(script) -> Optional[str]:
    """Gets command output from shell logger."""
    with logs.debug_time(u'Read output from external shell logger'):
        commands = _get_last_n(const.SHELL_LOGGER_LIMIT)
        if not commands:
            return None

        if commands[0]['command'] != script:
            logs.warn("Output isn't available in shell logger")
            return None

        lines = _get_output_lines(commands[0]['output'])
        output = '\n'.join(lines).strip()
        return output
