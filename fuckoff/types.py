from __future__ import annotations

import sys

from collections.abc import Callable, Generator
from pathlib import Path
from typing import Optional
from warnings import warn

from . import logs
from . import shells
from . import conf
from .const import DEFAULT_PRIORITY, ALL_ENABLED
from .utils import get_alias, format_raw_script
from .output_readers import get_output


# Introduced in python 3.13
# This isn't guaranteed to be available so use our own implementation instead
def deprecated(message: str):
    def decorator(func):
        def deprecation_wrapper():
            warn(message, DeprecationWarning)
            func()
        return deprecation_wrapper
    return decorator


class Command(object):
    """Command that should be fixed."""

    def __init__(self, script: str, output: Optional[str]):
        """Initializes command with given values."""
        self.script = script
        self.output = output

    @property
    @deprecated('use `output` instead')
    def stdout(self) -> Optional[str]:
        return self.output

    @property
    @deprecated('use `output` instead')
    def stderr(self) -> Optional[str]:
        return self.output

    @property
    def script_parts(self) -> list[str]:
        if not hasattr(self, '_script_parts'):
            try:
                self._script_parts = shells.shell.split_command(self.script)
            except Exception:
                logs.debug(u"Can't split command script {} because:\n {}".format(
                    self, sys.exc_info()))
                self._script_parts = []

        return self._script_parts

    def __eq__(self, other) -> bool:
        if not isinstance(other, Command):
            return False
        return (
            self.script == other.script
            and self.output == other.output
        )

    def __repr__(self) -> str:
        return u'Command(script={}, output={})'.format(self.script, self.output)

    def update(self, **kwargs) -> Command:
        """Returns new command with replaced fields."""
        kwargs.setdefault('script', self.script)
        kwargs.setdefault('output', self.output)
        return Command(**kwargs)

    @classmethod
    def from_raw_script(cls, raw_script: list[str]):
        """Creates instance of `Command` from a list of script parts."""
        script = format_raw_script(raw_script)
        expanded = shells.shell.from_shell(script)
        output = get_output(script, expanded)
        return cls(expanded, output)


class Rule(object):
    """Rule for fixing commands."""

    def __init__(
            self,
            name: str,
            match: Callable[[Command], bool],
            get_new_command: Callable[[Command], list[str]],
            enabled_by_default: bool,
            side_effect: Optional[Callable[[Command, str], None]],
            priority: int,
            requires_output: bool
    ):
        """Initializes rule with given fields."""
        self.name = name
        self.match = match
        self.get_new_command = get_new_command
        self.enabled_by_default = enabled_by_default
        self.side_effect = side_effect
        self.priority = priority
        self.requires_output = requires_output

    def __eq__(self, other):
        if not isinstance(other, Rule):
            return False
        return (
            self.name == other.name
            and self.match == other.match
            and self.get_new_command == other.get_new_command
            and self.enabled_by_default == other.enabled_by_default
            and self.side_effect == other.side_effect
            and self.priority == other.priority
            and self.requires_output == other.requires_output
        )

    def __repr__(self):
        return 'Rule(name={}, match={}, get_new_command={}, ' \
               'enabled_by_default={}, side_effect={}, ' \
               'priority={}, requires_output={})'.format(
                   self.name, self.match, self.get_new_command,
                   self.enabled_by_default, self.side_effect,
                   self.priority, self.requires_output)

    @classmethod
    def from_path(cls, path: Path) -> Optional[Rule]:
        """Creates rule instance from path."""
        name = path.name[:-3]
        if name in conf.settings.exclude_rules:
            logs.debug(u'Ignoring excluded rule: {}'.format(name))
            return None
        with logs.debug_time(u'Importing rule: {};'.format(name)):
            try:
                rule_module = conf.load_source(name, str(path))
            except Exception:
                logs.exception(u"Rule {} failed to load".format(name), sys.exc_info())
                return None
        priority = getattr(rule_module, 'priority', DEFAULT_PRIORITY)
        return cls(
            name,
            rule_module.match,
            rule_module.get_new_command,
            getattr(rule_module, 'enabled_by_default', True),
            getattr(rule_module, 'side_effect', None),
            conf.settings.priority.get(name, priority),
            getattr(rule_module, 'requires_output', True)
        )

    @property
    def is_enabled(self) -> bool:
        """Returns `True` when rule enabled."""
        print(self)
        print(conf.settings.rules)
        if self.enabled_by_default and ALL_ENABLED in conf.settings.rules:
            return True
        return self.name in conf.settings.rules

    def is_match(self, command: Command) -> bool:
        """Returns `True` if rule matches the command."""
        if command.output is None and self.requires_output:
            return False

        try:
            with logs.debug_time(u'Trying rule: {};'.format(self.name)):
                return self.match(command)
        except Exception:
            logs.rule_failed(self, sys.exc_info())
            return False

    def get_corrected_commands(self, command: Command) -> Generator[CorrectedCommand]:
        """Returns generator with corrected commands."""
        new_commands = self.get_new_command(command)
        if not isinstance(new_commands, list):
            new_commands = (new_commands,)
        for n, new_command in enumerate(new_commands):
            yield CorrectedCommand(
                script=new_command,
                side_effect=self.side_effect,
                priority=(n + 1) * self.priority
            )


class CorrectedCommand(object):
    """Corrected by rule command."""

    def __init__(
            self,
            script: str,
            side_effect: Optional[Callable[[Command, str], None]],
            priority: int
    ):
        """Initializes instance with given fields."""
        self.script = script
        self.side_effect = side_effect
        self.priority = priority

    def __eq__(self, other):
        """Ignores `priority` field."""
        if not isinstance(other, CorrectedCommand):
            return False
        return (
            self.script == other.script
            and self.side_effect == other.side_effect
        )

    def __hash__(self):
        return (self.script, self.side_effect).__hash__()

    def __repr__(self) -> str:
        return u'CorrectedCommand(script={}, side_effect={}, priority={})'.format(
            self.script, self.side_effect, self.priority)

    def _get_script(self) -> str:
        """Returns fixed commands script.

        If `settings.repeat` is `True`, appends command with second attempt
        of running fuck in case fixed command fails again.

        """
        if conf.settings.repeat:
            repeat_fuck = '{} --repeat {}--force-command {}'.format(
                get_alias(),
                '--debug ' if conf.settings.debug else '',
                shells.shell.quote(self.script))
            return shells.shell.or_(self.script, repeat_fuck)
        else:
            return self.script

    def run(self, old_cmd: Command) -> None:
        """Runs command from rule for passed command."""
        if self.side_effect:
            self.side_effect(old_cmd, self.script)
        if conf.settings.alter_history:
            shells.shell.put_to_history(self.script)

        sys.stdout.write(self._get_script())
