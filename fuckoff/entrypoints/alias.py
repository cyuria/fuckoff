from shutil import which

from .. import logs
from ..conf import settings
from ..shells import shell


def _get_alias(known_args):
    alias = shell.app_alias(known_args.alias)

    if known_args.enable_experimental_instant_mode:
        if not which('script'):
            logs.warn("Instant mode requires `script` app")
            return alias
        return shell.instant_mode_alias(known_args.alias)

    return alias


def print_alias(known_args):
    settings.init(known_args)
    print(_get_alias(known_args))
