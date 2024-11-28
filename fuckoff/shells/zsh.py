from time import time
import os
from subprocess import Popen, PIPE
from tempfile import gettempdir
from uuid import uuid4
from ..conf import settings
from ..const import USER_COMMAND_MARK
from ..utils import DEVNULL, memoize
from .generic import Generic


class Zsh(Generic):
    friendly_name = 'ZSH'

    def app_alias(self, alias_name):
        # It is VERY important to have the variables declared WITHIN the function
        return '''
            {name} () {{
                export FUCKOFF_SHELL=zsh;
                export FUCKOFF_ALIAS={name};
                export FUCKOFF_SHELL_ALIASES=$(alias);
                export FUCKOFF_HISTORY=$(fc -ln -10);
                FUCKOFF_CMD=$(
                    fuckoff "$@" -- $(fc -ln -1)
                ) && eval "$FUCKOFF_CMD";
                unset FUCKOFF_HISTORY;
                {alter_history}
            }}
        '''.format(
            name=alias_name,
            alter_history=(
                'history -s $FUCKOFF_CMD;'
                if settings.alter_history else ''
            )
        )

    def instant_mode_alias(self, alias_name):
        if os.environ.get('FUCKOFF_INSTANT_MODE', '').lower() == 'true':
            mark = ('%{' +
                    USER_COMMAND_MARK + '\b' * len(USER_COMMAND_MARK)
                    + '%}')
            return '''
                export PS1="{user_command_mark}$PS1";
                {app_alias}
            '''.format(user_command_mark=mark,
                       app_alias=self.app_alias(alias_name))
        else:
            log_path = os.path.join(
                gettempdir(), 'fuckoff-script-log-{}'.format(uuid4().hex))
            return '''
                export FUCKOFF_INSTANT_MODE=True;
                export FUCKOFF_OUTPUT_LOG={log};
                fuckoff --shell-logger {log};
                rm -f {log};
                exit
            '''.format(log=log_path)

    def _parse_alias(self, alias):
        name, value = alias.split('=', 1)
        if value[0] == value[-1] == '"' or value[0] == value[-1] == "'":
            value = value[1:-1]
        return name, value

    @memoize
    def get_aliases(self):
        raw_aliases = os.environ.get('FUCKOFF_SHELL_ALIASES', '').split('\n')
        return dict(
            self._parse_alias(alias)
            for alias in raw_aliases
            if alias and '=' in alias
        )

    def _get_history_file_name(self):
        return os.environ.get(
            "HISTFILE",
            os.path.expanduser('~/.zsh_history')
        )

    def _get_history_line(self, command_script):
        return u': {}:0;{}\n'.format(int(time()), command_script)

    def _script_from_history(self, line):
        return line.split(';', 1)[1] if ';' in line else ''

    def how_to_configure(self):
        return self._create_shell_configuration(
            content=u'eval $(fuckoff --alias)',
            path='~/.zshrc',
            reload='source ~/.zshrc')

    def _get_version(self):
        """Returns the version of the current shell"""
        proc = Popen(
            ['zsh', '--norc', '--noprofile', '-c', 'echo $ZSH_VERSION'],
            stdout=PIPE,
            stderr=DEVNULL,
            text=True
        )
        proc.wait()
        if proc.stdout is None:
            return ''
        return proc.stdout.read().strip()
