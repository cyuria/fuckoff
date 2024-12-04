import os
import pytest

from subprocess import PIPE, STDOUT
from mock import Mock
from pathlib import Path

from .utils import CorrectedCommand, Rule

from fuckoff import const
from fuckoff.types import Command


class TestCorrectedCommand(object):

    def test_equality(self):
        assert (CorrectedCommand('ls', None, 100) ==
                CorrectedCommand('ls', None, 200))
        assert (CorrectedCommand('ls', None, 100) !=
                CorrectedCommand('ls', lambda *_: None, 100))

    def test_hashable(self):
        assert {CorrectedCommand('ls', None, 100),
                CorrectedCommand('ls', None, 200)} == {CorrectedCommand('ls')}

    def test_representable(self):
        assert '{}'.format(CorrectedCommand('ls', None, 100)) == \
               'CorrectedCommand(script=ls, side_effect=None, priority=100)'
        assert u'{}'.format(CorrectedCommand(u'echo café', None, 100)) == \
               u'CorrectedCommand(script=echo café, side_effect=None, priority=100)'

    @pytest.mark.parametrize('script, printed, override_settings', [
        ('git branch', 'git branch', {'repeat': False, 'debug': False}),
        ('git brunch',
         "git brunch || fuck --repeat --force-command 'git brunch'",
         {'repeat': True, 'debug': False}),
        ('git brunch',
         "git brunch || fuck --repeat --debug --force-command 'git brunch'",
         {'repeat': True, 'debug': True})])
    def test_run(self, capsys, settings, script, printed, override_settings):
        settings.update(**override_settings)
        CorrectedCommand(script, None, 1000).run(Command(script, ''))
        out, _ = capsys.readouterr()
        assert out == printed


class TestRule(object):
    def test_from_path_rule_exception(self, mocker):
        load_source = mocker.patch('fuckoff.conf.load_source',
                                   side_effect=ImportError("No module named foo..."))
        assert Rule.from_path(Path('git.py')) is None
        load_source.assert_called_once_with('git', 'git.py')

    def test_from_path(self, mocker):
        def match(_: Command) -> bool:
            return False

        def get_new_command(_: Command) -> list[str]:
            return []

        load_source = mocker.patch(
            'fuckoff.conf.load_source',
            return_value=Mock(
                match=match,
                get_new_command=get_new_command,
                enabled_by_default=True,
                priority=900,
                requires_output=True
            )
        )
        rule_path = Path('rules') / 'bash.py'
        result = Rule.from_path(rule_path)
        expected = Rule('bash', match, get_new_command, priority=900)
        assert result == expected
        load_source.assert_called_once_with('bash', str(rule_path))

    def test_from_path_excluded_rule(self, mocker, settings):
        load_source = mocker.patch('fuckoff.conf.load_source')
        settings.update(exclude_rules=['git'])
        rule_path = os.path.join(os.sep, 'rules', 'git.py')
        assert Rule.from_path(Path(rule_path)) is None
        assert not load_source.called

    @pytest.mark.parametrize('rules, rule, is_enabled', [
        (const.DEFAULT_RULES, Rule('git', enabled_by_default=True), True),
        (const.DEFAULT_RULES, Rule('git', enabled_by_default=False), False),
        ([], Rule('git', enabled_by_default=False), False),
        ([], Rule('git', enabled_by_default=True), False),
        (const.DEFAULT_RULES + ['git'], Rule('git', enabled_by_default=False), True),
        (['git'], Rule('git', enabled_by_default=False), True)])
    def test_is_enabled(self, settings, rules, rule, is_enabled):
        settings.update(rules=rules)
        assert rule.is_enabled == is_enabled

    def test_isnt_match(self):
        assert not Rule('', lambda _: False).is_match(
            Command('ls', ''))

    def test_is_match(self):
        rule = Rule('', lambda x: x.script == 'cd ..')
        assert rule.is_match(Command('cd ..', ''))

    @pytest.mark.usefixtures('no_colors')
    def test_isnt_match_when_rule_failed(self, capsys):
        rule = Rule('test', Mock(side_effect=OSError('Denied')),
                    requires_output=False)
        assert not rule.is_match(Command('ls', ''))
        assert capsys.readouterr()[1].split('\n')[0] == '[WARN] Rule test:'

    def test_get_corrected_commands_with_rule_returns_list(self):
        rule = Rule(get_new_command=lambda x: [x.script + '!', x.script + '@'],
                    priority=100)
        assert (list(rule.get_corrected_commands(Command('test', '')))
                == [CorrectedCommand(script='test!', priority=100),
                    CorrectedCommand(script='test@', priority=200)])

    def test_get_corrected_commands_with_rule_returns_command(self):
        rule = Rule(get_new_command=lambda x: [x.script + '!'],
                    priority=100)
        result = list(rule.get_corrected_commands(Command('test', '')))
        expected = [CorrectedCommand(script='test!', priority=100)]
        assert result == expected


class TestCommand(object):
    @pytest.fixture(autouse=True)
    def Popen(self, monkeypatch):
        Popen = Mock()
        Popen.return_value.stdout.read.return_value = 'output'
        monkeypatch.setattr('fuckoff.output_readers.rerun.Popen', Popen)
        return Popen

    @pytest.fixture(autouse=True)
    def prepare(self, monkeypatch):
        monkeypatch.setattr('fuckoff.output_readers.rerun._wait_output',
                            lambda *_: True)

    def test_from_script_calls(self, Popen, settings, os_environ):
        settings.env = {}
        assert Command.from_raw_script(
            ['apt-get', 'search', 'vim']) == Command(
            'apt-get search vim', 'output')
        Popen.assert_called_once_with(
            'apt-get search vim',
            shell=True,
            text=True,
            stdin=PIPE,
            stdout=PIPE,
            stderr=STDOUT,
            env=os_environ
        )

    @pytest.mark.parametrize('script, result', [
        (['ls', '-la'], 'ls -la'),
        (['ls'], 'ls'),
        (['echo \\ '], 'echo \\ '),
        (['echo \\\n'], 'echo \\\n')])
    def test_from_script(self, script, result):
        assert Command.from_raw_script(script).script == result
