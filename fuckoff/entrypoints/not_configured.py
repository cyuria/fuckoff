# Initialize output before importing any module, that can use colorama.
from ..system import init_output

init_output()

import getpass  # noqa: E402
import json  # noqa: E402
import os  # noqa: E402
import time  # noqa: E402

from pathlib import Path  # noqa: E402
from tempfile import gettempdir  # noqa: E402
from typing import Dict  # noqa: E402

from .. import const  # noqa: E402
from .. import logs  # noqa: E402
from ..conf import settings  # noqa: E402
from ..shells import shell  # noqa: E402
from ..shells.generic import ShellConfiguration  # noqa: E402


def _get_not_configured_usage_tracker_path():
    """Returns path of special file where we store latest shell pid."""
    return Path(gettempdir()).joinpath(u'fuckoff.last_not_configured_run_{}'.format(
        getpass.getuser(),
    ))


def _record_first_run():
    """Records shell pid to tracker file."""
    info = {
        'pid': os.getppid(),
        'time': time.time(),
    }

    with _get_not_configured_usage_tracker_path().open('w') as tracker:
        json.dump(info, tracker)


def _get_previous_command():
    history = shell.get_history()

    if not history:
        return None
    return history[-1]


def _is_second_run():
    """Returns `True` when we know that `fuck` called second time."""
    tracker_path = _get_not_configured_usage_tracker_path()
    if not tracker_path.exists():
        return False

    with tracker_path.open('r') as tracker:
        try:
            info = json.load(tracker)
        except ValueError:
            return False

    if not isinstance(info, Dict):
        return False

    if not info.get('pid') == os.getppid():
        return False

    return (
        _get_previous_command() == 'fuck' or
        time.time() - info.get('time', 0) < const.CONFIGURATION_TIMEOUT
    )


def _is_already_configured(configuration: ShellConfiguration) -> bool:
    """Returns `True` when alias already in shell config."""
    path = Path(configuration.path).expanduser()
    with path.open('r') as shell_config:
        return configuration.content in shell_config.read()


def _configure(configuration_details):
    """Adds alias to shell config."""
    path = Path(configuration_details.path).expanduser()
    with path.open('a') as shell_config:
        shell_config.write(u'\n')
        shell_config.write(configuration_details.content)
        shell_config.write(u'\n')


def main():
    """Shows useful information about how-to configure alias on a first run
    and configure automatically on a second.

    It'll be only visible when user type fuck and when alias isn't configured.

    """
    settings.init()
    configuration = shell.how_to_configure()
    if (
        configuration and
        configuration.can_configure_automatically
    ):
        if _is_already_configured(configuration):
            logs.already_configured(configuration)
            return
        elif _is_second_run():
            _configure(configuration)
            logs.configured_successfully(configuration)
            return
        else:
            _record_first_run()

    logs.how_to_configure_alias(configuration)
