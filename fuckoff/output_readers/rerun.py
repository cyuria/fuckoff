import os
import shlex

from psutil import AccessDenied, Process, TimeoutExpired
from subprocess import Popen, PIPE, STDOUT
from typing import Optional

from .. import logs
from .. import conf


def _kill_process(proc: Process):
    """Tries to kill the process otherwise just logs a debug message, the
    process will be killed when fuckoff terminates. """
    try:
        proc.kill()
    except AccessDenied:
        logs.debug(u'Rerun: process PID {} ({}) could not be terminated'.format(
            proc.pid, proc.exe()))


def _wait_output(popen: Popen, is_slow: bool) -> bool:
    """Returns `True` if we can get output of the command in the
    `settings.wait_command` time.

    Command will be killed if it wasn't finished in the time."""
    proc = Process(popen.pid)
    try:
        proc.wait(conf.settings.wait_slow_command if is_slow
                  else conf.settings.wait_command)
        return True
    except TimeoutExpired:
        for child in proc.children(recursive=True):
            _kill_process(child)
        _kill_process(proc)
        return False


def get_output(script: str, expanded: str) -> Optional[str]:
    """Runs the script and obtains stdin/stderr."""
    env = dict(os.environ)
    env.update(conf.settings.env)

    split_expand = shlex.split(expanded)
    is_slow = split_expand[0] in conf.settings.slow_commands if split_expand else False
    with logs.debug_time(u'Call: {}; with env: {}; is slow: {}'.format(
            script, env, is_slow)):
        print(expanded)
        result = Popen(
            expanded,
            shell=True,
            text=True,
            stdin=PIPE,
            stdout=PIPE,
            stderr=STDOUT,
            env=env
        )
        if not _wait_output(result, is_slow):
            logs.debug(u'Execution timed out!')
            return None

        if result.stdout is None:
            logs.debug(u'Execution timed out!')
            return None

        output = result.stdout.read()
        logs.debug(u'Received output: {}'.format(output))
        return output
