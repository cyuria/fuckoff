from fuckoff.specific.git import git_support
from fuckoff.utils import replace_argument


@git_support
def match(command):
    return ('error: did you mean `' in command.output
            and '` (with two dashes ?)' in command.output)


@git_support
def get_new_command(command):
    to = command.output.split('`')[1]
    return replace_argument(command.script, to[1:], to)
