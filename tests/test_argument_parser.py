import pytest

from fuckoff.argument_parser import Parser


def _args(**override):
    args = {'alias': None, 'command': [], 'yes': False,
            'help': False, 'version': False, 'debug': False,
            'force_command': None, 'repeat': False,
            'enable_experimental_instant_mode': False,
            'shell_logger': None}
    args.update(override)
    return args


@pytest.mark.parametrize('argv, result', [
    (['fuckoff'], _args()),
    (['fuckoff', '-a'], _args(alias='fuck')),
    (
        ['fuckoff', '--alias', '--enable-experimental-instant-mode'],
        _args(alias='fuck', enable_experimental_instant_mode=True)
    ),
    (['fuckoff', '-a', 'fix'], _args(alias='fix')),
    (
        ['fuckoff', '-y', '--', 'git', 'branch'],
        _args(command=['git', 'branch'], yes=True)
    ),
    (
        ['fuckoff', '-y', '--', 'git', 'branch', '-a'],
        _args(command=['git', 'branch', '-a'], yes=True)
    ),
    (['fuckoff', '-v'], _args(version=True)),
    (['fuckoff', '--help'], _args(help=True)),
    (
        ['fuckoff', '-y', '-d', '--', 'git', 'branch', '-a'],
        _args(command=['git', 'branch', '-a'], yes=True, debug=True)
    ),
    (
        ['fuckoff', '-r', '-d', '--', 'git', 'branch', '-a'],
        _args(command=['git', 'branch', '-a'], repeat=True, debug=True)
    ),
    (['fuckoff', '-l', '/tmp/log'], _args(shell_logger='/tmp/log')),
    (
        ['fuckoff', '--shell-logger', '/tmp/log'],
        _args(shell_logger='/tmp/log')
    )])
def test_parse(argv, result):
    assert vars(Parser().parse(argv)) == result
