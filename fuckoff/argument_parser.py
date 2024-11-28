from collections.abc import Iterable
import os
import sys
from argparse import ArgumentParser, SUPPRESS
from dataclasses import dataclass
from .const import ARGUMENT_PLACEHOLDER


@dataclass
class Arguments:
    version: bool
    alias: str
    shell_logger: str
    enable_experimental_instant_mode: bool
    help: bool
    yes: bool
    repeat: bool
    debug: bool
    force_command: str
    command: list[str]


class Parser(object):
    """Argument parser that can handle arguments with our special
    placeholder."""

    def __init__(self):
        self._parser = ArgumentParser(prog='fuckoff', add_help=False)
        self._add_arguments()

    def _add_arguments(self):
        """Adds arguments to parser."""
        self._parser.add_argument(
            '-v', '--version',
            action='store_true',
            help="show program's version number and exit")
        self._parser.add_argument(
            '-a', '--alias',
            nargs='?',
            const=os.environ.get('FUCKOFF_ALIAS', 'fuck'),
            help='[custom-alias-name] prints alias for current shell')
        self._parser.add_argument(
            '-l', '--shell-logger',
            action='store',
            help='log shell output to the file')
        self._parser.add_argument(
            '--enable-experimental-instant-mode',
            action='store_true',
            help='enable experimental instant mode, use on your own risk')
        self._parser.add_argument(
            '-h', '--help',
            action='store_true',
            help='show this help message and exit')

        """It's too dangerous to use `-y` and `-r` together."""
        group = self._parser.add_mutually_exclusive_group()
        group.add_argument(
            '-y', '--yes', '--yeah', '--hard',
            action='store_true',
            help='execute fixed command without confirmation')
        group.add_argument(
            '-r', '--repeat',
            action='store_true',
            help='repeat on failure')

        self._parser.add_argument(
            '-d', '--debug',
            action='store_true',
            help='enable debug output')
        self._parser.add_argument(
            '--force-command',
            action='store',
            help=SUPPRESS)
        self._parser.add_argument(
            'command',
            nargs='*',
            help='command that should be fixed')

    def _prepare_arguments(self, argv: list[str]) -> list[str]:
        """Prepares arguments by:

        - removing placeholder and moving arguments after it to beginning,
          we need this to distinguish arguments from `command` with ours;

        - adding `--` before `command`, so our parse would ignore arguments
          of `command`.

        """
        if ARGUMENT_PLACEHOLDER in argv:
            index = argv.index(ARGUMENT_PLACEHOLDER)
            return argv[index + 1:] + ['--'] + argv[:index]
        elif not argv or argv[0].startswith('-'):
            return argv
        else:
            return ['--'] + argv

    def parse(self, argv: list[str]) -> Arguments:
        arguments = self._prepare_arguments(argv[1:])
        parsed = self._parser.parse_args(arguments)
        return Arguments(**vars(parsed))

    def print_usage(self):
        self._parser.print_usage(sys.stderr)

    def print_help(self):
        self._parser.print_help(sys.stderr)
