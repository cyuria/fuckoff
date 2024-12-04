import re

from fuckoff.utils import replace_command, for_app


@for_app('tmux')
def match(command):
    return ('ambiguous command:' in command.output
            and 'could be:' in command.output)


def get_new_command(command):
    cmd = re.match(r"ambiguous command: (.*), could be: (.*)",
                   command.output)
    if cmd is None:
        raise Exception('Rule incorrectly matched')

    old_cmd = cmd.group(1)
    suggestions = [c.strip() for c in cmd.group(2).split(',')]

    return replace_command(command, old_cmd, suggestions)
