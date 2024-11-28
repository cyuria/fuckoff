import re

from shutil import which

from fuckoff.utils import for_app, replace_argument


def _get_command_name(command) -> str:
    found = re.findall(r'sudo: (.*): command not found', command.output)
    if found:
        return found[0]
    else:
        return ''


@for_app('sudo')
def match(command):
    if 'command not found' not in command.output:
        return False
    command_name = _get_command_name(command)
    return which(command_name)


def get_new_command(command):
    command_name = _get_command_name(command)
    return replace_argument(command.script, command_name,
                            u'env "PATH=$PATH" {}'.format(command_name))
