from collections.abc import Iterable, Iterator
import sys
from typing import Optional

from . import logs
from . import const
from . import conf
from .types import CorrectedCommand
from .exceptions import NoRuleMatched
from .system import get_key
from .utils import get_alias


def read_actions():
    """Yields actions for pressed keys."""
    while True:
        key = get_key()

        # Handle arrows, j/k (qwerty), and n/e (colemak)
        if key in (const.KEY_UP, const.KEY_CTRL_N, 'k', 'e'):
            yield const.ACTION_PREVIOUS
        elif key in (const.KEY_DOWN, const.KEY_CTRL_P, 'j', 'n'):
            yield const.ACTION_NEXT
        elif key in (const.KEY_CTRL_C, 'q'):
            yield const.ACTION_ABORT
        elif key in ('\n', '\r'):
            yield const.ACTION_SELECT


class CommandSelector(object):
    """Helper for selecting rule from rules list."""

    def __init__(self, commands: Iterable[CorrectedCommand]):
        self._commands = list(commands)
        if not self._commands:
            raise NoRuleMatched
        self._realised = False
        self._index = 0

    def next(self):
        self._index = (self._index + 1) % len(self._commands)

    def previous(self):
        self._index = (self._index - 1) % len(self._commands)

    @property
    def value(self) -> CorrectedCommand:
        return self._commands[self._index]


def select_command(
        corrected_commands: Iterator[CorrectedCommand]
) -> Optional[CorrectedCommand]:
    """Returns:

     - the first command when confirmation disabled;
     - None when ctrl+c pressed;
     - selected command.
    """

    if not conf.settings.require_confirmation:
        try:
            corrected = next(corrected_commands)
        except StopIteration:
            logs.failed('No fucks given' if get_alias() == 'fuck'
                        else 'Nothing found')
            return None
        logs.show_corrected_command(corrected)
        return corrected

    try:
        selector = CommandSelector(corrected_commands)
    except NoRuleMatched:
        logs.failed('No fucks given' if get_alias() == 'fuck'
                    else 'Nothing found')
        return None

    logs.confirm_text(selector.value)

    for action in read_actions():
        match action:
            case const.ACTION_SELECT:
                sys.stderr.write('\n')
                return selector.value
            case const.ACTION_ABORT:
                logs.failed('\nAborted')
                return None
            case const.ACTION_PREVIOUS:
                selector.previous()
                logs.confirm_text(selector.value)
            case const.ACTION_NEXT:
                selector.next()
                logs.confirm_text(selector.value)
