import re

from fuckoff.specific.brew import brew_available
from fuckoff.utils import for_app

enabled_by_default = brew_available


def _get_suggestions(str):
    suggestions = str.replace(" or ", ", ").split(", ")
    return suggestions


@for_app('brew', at_least=2)
def match(command):
    is_proper_command = ('install' in command.script and
                         'No available formula' in command.output and
                         'Did you mean' in command.output)
    return is_proper_command


def get_new_command(command):
    matcher = re.search('Warning: No available formula with the name "(?:[^"]+)". Did you mean (.+)\\?', command.output)
    if matcher is None:
        return []
    suggestions = _get_suggestions(matcher.group(1))
    return ["brew install " + formula for formula in suggestions]
