import pytest

from fuckoff.shells.tcsh import Tcsh


@pytest.mark.usefixtures('isfile', 'no_memoize', 'no_cache')
class TestTcsh(object):
    @pytest.fixture
    def shell(self):
        return Tcsh()

    @pytest.fixture(autouse=True)
    def Popen(self, mocker):
        mock = mocker.patch('fuckoff.shells.tcsh.Popen')
        mock.return_value.stdout.read.return_value = (
            'fuck\teval $(fuckoff $(fc -ln -1))\n'
            'l\tls -CF\n'
            'la\tls -A\n'
            'll\tls -alF')
        return mock

    @pytest.mark.parametrize('before, after', [
        ('pwd', 'pwd'),
        ('fuck', 'eval $(fuckoff $(fc -ln -1))'),
        ('awk', 'awk'),
        ('ll', 'ls -alF')])
    def test_from_shell(self, before, after, shell):
        assert shell.from_shell(before) == after

    def test_to_shell(self, shell):
        assert shell.to_shell('pwd') == 'pwd'

    def test_and_(self, shell):
        assert shell.and_('ls', 'cd') == 'ls && cd'

    def test_or_(self, shell):
        assert shell.or_('ls', 'cd') == 'ls || cd'

    def test_get_aliases(self, shell):
        assert shell.get_aliases() == {'fuck': 'eval $(fuckoff $(fc -ln -1))',
                                       'l': 'ls -CF',
                                       'la': 'ls -A',
                                       'll': 'ls -alF'}

    def test_app_alias(self, shell):
        assert 'setenv FUCKOFF_SHELL tcsh' in shell.app_alias('fuck')
        assert 'alias fuck' in shell.app_alias('fuck')
        assert 'alias FUCK' in shell.app_alias('FUCK')
        assert 'fuckoff' in shell.app_alias('fuck')

    def test_get_history(self, history_lines, shell):
        history_lines(['ls', 'rm'])
        assert list(shell.get_history()) == ['ls', 'rm']

    def test_how_to_configure(self, shell, config_exists):
        config_exists.return_value = True
        assert shell.how_to_configure().can_configure_automatically

    def test_how_to_configure_when_config_not_found(self, shell,
                                                    config_exists):
        config_exists.return_value = False
        assert not shell.how_to_configure().can_configure_automatically

    def test_info(self, shell, Popen):
        Popen.return_value.stdout.read.side_effect = [
            'tcsh 6.20.00 (Astron) 2016-11-24 (unknown-unknown-bsd44) \n']
        assert shell.info() == 'Tcsh 6.20.00'
        assert Popen.call_args[0][0] == ['tcsh', '--version']

    @pytest.mark.parametrize('side_effect, exception', [
        (['\n'], IndexError), (OSError, OSError)])
    def test_get_version_error(self, side_effect, exception, shell, Popen):
        Popen.return_value.stdout.read.side_effect = side_effect
        with pytest.raises(exception):
            shell._get_version()
        assert Popen.call_args[0][0] == ['tcsh', '--version']
