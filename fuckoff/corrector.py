from __future__ import annotations

import sys

from pathlib import Path
from typing import Generator, Iterable, Iterator

from . import logs
from .conf import settings
from .types import Command, Rule, CorrectedCommand


def get_rules_import_paths() -> Generator[Path]:
    """Yields all rules import paths."""
    # Bundled rules:
    yield Path(__file__).parent.joinpath('rules')
    # Rules defined by user:
    yield settings.user_dir.joinpath('rules')
    # Packages with third-party rules:
    for path in sys.path:
        for contrib_module in Path(path).glob('fuckoff_contrib_*'):
            contrib_rules = contrib_module.joinpath('rules')
            if not contrib_rules.is_dir():
                continue
            yield contrib_rules


def get_loaded_rules(rules_paths: Iterable[Path]) -> Iterable[Rule]:
    """Yields all available rules."""

    return (
        rule for rule in (
            Rule.from_path(path) for path in rules_paths
            if path.name != '__init__.py'
        ) if rule and rule.is_enabled
    )


def get_rules() -> list[Rule]:
    """Returns all enabled rules."""
    return sorted(get_loaded_rules(
        rule_path
        for path in get_rules_import_paths()
        for rule_path in sorted(path.glob('*.py'))
    ), key=lambda rule: rule.priority)


def organize_commands(
        corrected_commands: Iterator[CorrectedCommand]
) -> Generator[CorrectedCommand]:
    """Yields sorted commands without duplicates."""
    try:
        first_command = next(corrected_commands)
        yield first_command
    except StopIteration:
        return

    without_duplicates = {
        command for command in sorted(
            corrected_commands,
            key=lambda command: command.priority
        ) if command != first_command
    }

    sorted_commands = sorted(
        without_duplicates,
        key=lambda corrected_command: corrected_command.priority
    )

    logs.debug(u'Corrected commands: {}'.format(
        ', '.join(u'{}'.format(cmd) for cmd in [first_command] + sorted_commands)))

    for command in sorted_commands:
        yield command


def get_corrected_commands(command: Command) -> Generator[CorrectedCommand]:
    """Returns generator with sorted and unique corrected commands."""
    return organize_commands(
        corrected for rule in get_rules()
        if rule.is_match(command)
        for corrected in rule.get_corrected_commands(command)
    )
