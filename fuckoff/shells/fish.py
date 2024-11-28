import os
import re
import sys

from subprocess import Popen, PIPE
from time import time

from .generic import Generic
from .. import logs
from ..conf import settings
from ..utils import DEVNULL, cache


@cache('~/.config/fish/config.fish', '~/.config/fish/functions')
def _get_functions(overridden: set[str]) -> dict[str, str]:
    proc = Popen(['fish', '-ic', 'functions'], stdout=PIPE, stderr=DEVNULL, text=True)
    proc.wait()
    if proc.stdout is None:
        return {}
    functions = proc.stdout.read().strip().split('\n')
    return {
        func: func
        for func in functions
        if func not in overridden
    }


@cache('~/.config/fish/config.fish')
def _get_aliases(overridden: set[str]):
    proc = Popen(['fish', '-ic', 'alias'], stdout=PIPE, stderr=DEVNULL, text=True)
    proc.wait()
    if proc.stdout is None:
        return {}

    return {
        name: value for name, value in (
            re.split(' |=', alias, 1)
            for alias in (
                line.replace('alias ', '', 1)
                for line in proc.stdout.read().strip().split('\n')
            )
            if ' ' in alias or '=' in alias
        )
        if name not in overridden
    }


class Fish(Generic):
    friendly_name = 'Fish Shell'

    def _get_overridden_aliases(self) -> set[str]:
        overridden = os.environ.get('FUCKOFF_OVERRIDDEN_ALIASES', '')
        return set.union(
            {'cd', 'grep', 'ls', 'man', 'open'},
            {alias.strip() for alias in overridden.split(',')}
        )

    def app_alias(self, alias_name):
        alter_history = (
            '    builtin history delete --exact'
            ' --case-sensitive -- $fucked_up_command\n'
            '    builtin history merge\n'
        ) if settings.alter_history else ''
        # It is VERY important to have the variables declared WITHIN the alias
        return (
            'function {0} -d "Correct your previous console command"\n'
            '  set -l fucked_up_command $history[1]\n'
            '  env FUCKOFF_SHELL=fish FUCKOFF_ALIAS={0}'
            ' fuckoff $argv -- $fucked_up_command | read -l unfucked_command\n'
            '  if [ "$unfucked_command" != "" ]\n'
            '    eval $unfucked_command\n{1}'
            '  end\n'
            'end'
        ).format(alias_name, alter_history)

    def get_aliases(self):
        overridden = self._get_overridden_aliases()
        functions = _get_functions(overridden)
        aliases = _get_aliases(overridden)
        return functions | aliases

    def _expand_aliases(self, command_script):
        aliases = self.get_aliases()
        binary = command_script.split(' ')[0]
        if binary in aliases and aliases[binary] != binary:
            return command_script.replace(binary, aliases[binary], 1)
        elif binary in aliases:
            return u'fish -ic "{}"'.format(command_script.replace('"', r'\"'))
        else:
            return command_script

    def _get_history_file_name(self):
        return os.path.expanduser('~/.config/fish/fish_history')

    def _get_history_line(self, command_script):
        return u'- cmd: {}\n   when: {}\n'.format(command_script, int(time()))

    def _script_from_history(self, line):
        if '- cmd: ' in line:
            return line.split('- cmd: ', 1)[1]
        else:
            return ''

    def and_(self, *commands):
        return u'; and '.join(commands)

    def or_(self, *commands):
        return u'; or '.join(commands)

    def how_to_configure(self):
        return self._create_shell_configuration(
            content=u"fuckoff --alias | source",
            path='~/.config/fish/config.fish',
            reload='fish')

    def _get_version(self):
        """Returns the version of the current shell"""
        proc = Popen(['fish', '--version'], stdout=PIPE, stderr=DEVNULL, text=True)
        proc.wait()
        if proc.stdout is None:
            return ''
        return proc.stdout.read().split()[-1]

    def put_to_history(self, command):
        try:
            return self._put_to_history(command)
        except IOError:
            logs.exception("Can't update history", sys.exc_info())

    def _put_to_history(self, command_script):
        """Puts command script to shell history."""
        history_file_name = self._get_history_file_name()
        if not os.path.isfile(history_file_name):
            return

        with open(history_file_name, 'a') as history:
            entry = self._get_history_line(command_script)
            history.write(entry)
