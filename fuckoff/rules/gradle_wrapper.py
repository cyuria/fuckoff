import os

from shutil import which

from fuckoff.utils import for_app


@for_app('gradle')
def match(command):
    return (not which(command.script_parts[0])
            and 'not found' in command.output
            and os.path.isfile('gradlew'))


def get_new_command(command):
    return u'./gradlew {}'.format(' '.join(command.script_parts[1:]))
