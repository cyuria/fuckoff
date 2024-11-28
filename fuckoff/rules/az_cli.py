import re

from fuckoff.utils import for_app, replace_argument

INVALID_CHOICE = "(?=az)(?:.*): '(.*)' is not in the '.*' command group."
OPTIONS = "^The most similar choice to '.*' is:\n\\s*(.*)$"


@for_app('az')
def match(command):
    return "is not in the" in command.output and "command group" in command.output


def get_new_command(command):
    search = re.search(INVALID_CHOICE, command.output)
    if search is None:
        return []
    mistake = search.group(1)
    options = re.findall(OPTIONS, command.output, flags=re.MULTILINE)
    return [replace_argument(command.script, mistake, o) for o in options]
