import os
import sys
from difflib import SequenceMatcher
from pprint import pformat

from ..argument_parser import Arguments
from .. import logs, types, const
from ..conf import settings
from ..corrector import get_corrected_commands
from ..ui import select_command
from ..utils import get_alias, get_all_executables


def _get_raw_command(known_args: Arguments):
    if known_args.force_command:
        return [known_args.force_command]

    if not os.environ.get('FUCKOFF_HISTORY'):
        return known_args.command

    history = os.environ['FUCKOFF_HISTORY'].split('\n')[::-1]
    alias = get_alias()
    executables = get_all_executables()
    for command in history:
        if command in executables:
            return [command]
        diff = SequenceMatcher(a=alias, b=command).ratio()
        if diff < const.DIFF_WITH_ALIAS:
            return [command]
    return []


def fix_command(known_args: Arguments):
    """Fixes previous command. Used when `fuckoff` called without arguments."""
    settings.init(known_args)
    with logs.debug_time('Total'):
        logs.debug(u'Run with settings: {}'.format(pformat(settings)))
        raw_command = _get_raw_command(known_args)

        if not raw_command:
            logs.debug('Empty command, nothing to do')
            return

        command = types.Command.from_raw_script(raw_command)

        corrected_commands = get_corrected_commands(command)
        selected_command = select_command(corrected_commands)

        if selected_command:
            selected_command.run(command)
        else:
            sys.exit(1)
