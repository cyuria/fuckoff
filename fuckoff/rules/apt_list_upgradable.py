from fuckoff.specific.apt import apt_available
from fuckoff.specific.sudo import sudo_support
from fuckoff.utils import for_app

enabled_by_default = apt_available


@sudo_support
@for_app('apt')
def match(command):
    return 'apt list --upgradable' in command.output


@sudo_support
def get_new_command(_):
    return 'apt list --upgradable'
