import re

from fuckoff.utils import for_app

MISTAKE = r'(?<=Terraform has no command named ")([^"]+)(?="\.)'
FIX = r'(?<=Did you mean ")([^"]+)(?="\?)'


@for_app('terraform')
def match(command):
    return re.search(MISTAKE, command.output) and re.search(FIX, command.output)


def get_new_command(command):
    mistake = re.search(MISTAKE, command.output)
    fix = re.search(FIX, command.output)
    if mistake is None or fix is None:
        raise Exception('Rule incorrectly matched')
    return command.script.replace(mistake.group(0), fix.group(0))
