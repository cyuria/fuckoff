import re

from fuckoff.specific.sudo import sudo_support
from fuckoff.utils import for_app


@sudo_support
@for_app('cp')
def match(command):
    output = command.output.lower()
    return 'omitting directory' in output or 'is a directory' in output


@sudo_support
def get_new_command(command):
    return re.sub(r'^cp', 'cp -a', command.script)
