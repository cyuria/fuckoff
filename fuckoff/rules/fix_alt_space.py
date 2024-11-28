import re

from fuckoff.specific.sudo import sudo_support


@sudo_support
def match(command):
    return ('command not found' in command.output.lower()
            and u' ' in command.script)


@sudo_support
def get_new_command(command):
    return re.sub(u' ', ' ', command.script)
