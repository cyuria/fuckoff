from dataclasses import dataclass, field
import importlib.util
import os
import sys

from pathlib import Path
from types import ModuleType
from typing import Optional

from . import const
from . import logs
from .argument_parser import Arguments


def load_source(name: str, path: str | Path) -> ModuleType:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise Exception('Source file failed to load')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _get_user_dir_path():
    """Returns Path object representing the user config resource"""
    xdg_config_home = os.environ.get('XDG_CONFIG_HOME', '~/.config')
    return Path(xdg_config_home, 'fuckoff').expanduser()


@dataclass
class Settings:
    rules: list[str] = field(default_factory=lambda: const.DEFAULT_RULES)
    exclude_rules: list[str] = field(default_factory=lambda: [])
    wait_command: float = 0.5
    require_confirmation: bool = True
    no_colors: bool = False
    debug: bool = False
    priority: dict[str, int] = field(default_factory=lambda: {})
    history_limit: Optional[int] = None
    alter_history: bool = True
    wait_slow_command: float = 5
    slow_commands: list[str] = field(default_factory=lambda: [
        'lein',
        'react-native',
        'gradle',
        './gradlew',
        'vagrant'
    ])
    repeat: bool = False
    instant_mode: bool = False
    num_close_matches: int = 3
    env: dict[str, str] = field(default_factory=lambda: {
        'LC_ALL': 'C',
        'LANG': 'C',
        'GIT_TRACE': '1',
    })
    excluded_search_path_prefixes: list[str] = field(default_factory=lambda: [])
    user_dir: Path = _get_user_dir_path()

    def init(self, args: Optional[Arguments] = None):
        """Fills `settings` with values from `settings.py` and env."""

        self._setup_user_dir()
        self._init_settings_file()

        try:
            self.update(**self._settings_from_file())
        except Exception:
            logs.exception("Can't load settings from file", sys.exc_info())

        try:
            self.update(**self._settings_from_env())
        except Exception:
            logs.exception("Can't load settings from env", sys.exc_info())

        self.update(**self._settings_from_args(args))

    def update(self, **kwargs):
        for arg in kwargs:
            if arg not in vars(self):
                raise Exception(f"Unknown setting '{arg}'")
        vars(self).update(kwargs)

    def _init_settings_file(self):
        settings_path = self.user_dir.joinpath('settings.py')
        if not settings_path.is_file():
            with settings_path.open(mode='w') as settings_file:
                settings_file.write(const.SETTINGS_HEADER)
                for key in vars(Settings()):
                    settings_file.write(u'# {} = {}\n'.format(key, getattr(Settings(), key)))

    def _setup_user_dir(self):
        """Returns user config dir, create it when it doesn't exist."""
        user_dir = _get_user_dir_path()

        rules_dir = user_dir.joinpath('rules')
        if not rules_dir.is_dir():
            rules_dir.mkdir(parents=True)
        self.user_dir = user_dir

    def _settings_from_file(self):
        """Loads settings from file."""
        settings = load_source('settings', self.user_dir / 'settings.py')
        return {
            key: getattr(settings, key)
            for key in vars(self)
            if key in vars(settings)
        }

    def _rules_from_env(self, val):
        """Transforms rules list from env-string to python."""
        val = val.split(':')
        if 'DEFAULT_RULES' in val:
            val = const.DEFAULT_RULES + [rule for rule in val if rule != 'DEFAULT_RULES']
        return val

    def _priority_from_env(self, val):
        """Gets priority pairs from env."""
        for part in val.split(':'):
            try:
                rule, priority = part.split('=')
                yield rule, int(priority)
            except ValueError:
                continue

    def _val_from_env(self, env, attr):
        """Transforms env-strings to python."""
        val = os.environ[env]
        if attr in ('rules', 'exclude_rules'):
            return self._rules_from_env(val)
        elif attr == 'priority':
            return dict(self._priority_from_env(val))
        elif attr in ('wait_command', 'history_limit', 'wait_slow_command',
                      'num_close_matches'):
            return int(val)
        elif attr in ('require_confirmation', 'no_colors', 'debug',
                      'alter_history', 'instant_mode'):
            return val.lower() == 'true'
        elif attr in ('slow_commands', 'excluded_search_path_prefixes'):
            return val.split(':')
        else:
            return val

    def _settings_from_env(self):
        """Loads settings from env."""
        return {attr: self._val_from_env(env, attr)
                for env, attr in const.ENV_TO_ATTR.items()
                if env in os.environ}

    def _settings_from_args(self, args):
        """Loads settings from args."""
        if not args:
            return {}

        from_args = {}
        if args.yes:
            from_args['require_confirmation'] = not args.yes
        if args.debug:
            from_args['debug'] = args.debug
        if args.repeat:
            from_args['repeat'] = args.repeat
        return from_args


settings = Settings()
