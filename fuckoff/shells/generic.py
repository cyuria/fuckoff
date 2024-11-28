import os
import shlex

from pathlib import Path
from typing import Dict, Optional

from .types import ShellConfiguration
from .. import logs
from .. import utils
from ..conf import settings


class Generic(object):
    friendly_name = 'Generic Shell'

    def get_aliases(self) -> Dict[str, str]:
        return {}

    def _expand_aliases(self, command_script: str) -> str:
        aliases = self.get_aliases()
        binary = command_script.split(' ')[0]
        if binary in aliases:
            return command_script.replace(binary, aliases[binary], 1)
        else:
            return command_script

    def from_shell(self, command_script: str) -> str:
        """Prepares command before running in app."""
        return self._expand_aliases(command_script)

    def to_shell(self, command_script: str) -> str:
        """Prepares command for running in shell."""
        return command_script

    def app_alias(self, alias_name: str):
        return (
            """alias {0}='eval "$(FUCKOFF_ALIAS={0} """
            """fuckoff -- "$(fc -ln -1)")"'"""
        ).format(alias_name)

    def instant_mode_alias(self, alias_name):
        logs.warn("Instant mode not supported by your shell")
        return self.app_alias(alias_name)

    def _get_history_file_name(self) -> str:
        return ''

    def _get_history_line(self, command_script) -> str:
        _ = command_script
        return ''

    @utils.memoize
    def get_history(self) -> list[str]:
        """Returns list of history entries."""
        history_file_name = self._get_history_file_name()
        if not os.path.isfile(history_file_name):
            return []

        with open(history_file_name, 'r', errors='ignore') as history_file:
            lines = history_file.readlines()

        if settings.history_limit:
            lines = lines[-settings.history_limit:]

        return [
            prepared for prepared in (
                self._script_from_history(line).strip()
                for line in lines
            ) if prepared
        ]

    def and_(self, *commands: str) -> str:
        return u' && '.join(commands)

    def or_(self, *commands):
        return u' || '.join(commands)

    def how_to_configure(self) -> Optional[ShellConfiguration]:
        return None

    def split_command(self, command: str) -> list[str]:
        """Split the command using shell-like syntax."""
        try:
            return shlex.split(command)
        except ValueError:
            return command.split(' ')

    def quote(self, s):
        """Return a shell-escaped version of the string s."""
        return shlex.quote(s)

    def _script_from_history(self, line: str) -> str:
        return line

    def put_to_history(self, command):
        """Adds fixed command to shell history.

        In most of shells we change history on shell-level, but not
        all shells support it (Fish).

        """
        _ = command

    def get_builtin_commands(self) -> list[str]:
        """Returns shells builtin commands."""
        return ['alias', 'bg', 'bind', 'break', 'builtin', 'case', 'cd',
                'command', 'compgen', 'complete', 'continue', 'declare',
                'dirs', 'disown', 'echo', 'enable', 'eval', 'exec', 'exit',
                'export', 'fc', 'fg', 'getopts', 'hash', 'help', 'history',
                'if', 'jobs', 'kill', 'let', 'local', 'logout', 'popd',
                'printf', 'pushd', 'pwd', 'read', 'readonly', 'return', 'set',
                'shift', 'shopt', 'source', 'suspend', 'test', 'times', 'trap',
                'type', 'typeset', 'ulimit', 'umask', 'unalias', 'unset',
                'until', 'wait', 'while']

    def _get_version(self) -> str:
        """Returns the version of the current shell"""
        return ''

    def info(self):
        """Returns the name and version of the current shell"""
        try:
            version = self._get_version()
        except Exception as e:
            logs.warn(u'Could not determine shell version: {}'.format(e))
            version = ''
        return u'{} {}'.format(self.friendly_name, version).rstrip()

    def _create_shell_configuration(self, content: str, path: str, reload: str):
        return ShellConfiguration(
            content=content,
            path=path,
            reload=reload,
            can_configure_automatically=Path(path).expanduser().exists()
        )
