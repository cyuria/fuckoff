import pytest
from fuckoff.rules.workon_doesnt_exists import match, get_new_command
from fuckoff.types import Command


@pytest.fixture(autouse=True)
def envs(mocker):
    return mocker.patch(
        'fuckoff.rules.workon_doesnt_exists._get_all_environments',
        return_value=['fuckoff', 'code_view'])


@pytest.mark.parametrize('script', [
    'workon tehfuck', 'workon code-view', 'workon new-env'])
def test_match(script):
    assert match(Command(script, ''))


@pytest.mark.parametrize('script', [
    'workon fuckoff', 'workon code_view', 'work on tehfuck'])
def test_not_match(script):
    assert not match(Command(script, ''))


@pytest.mark.parametrize('script, result', [
    ('workon tehfuck', 'workon fuckoff'),
    ('workon code-view', 'workon code_view'),
    ('workon zzzz', 'mkvirtualenv zzzz')])
def test_get_new_command(script, result):
    assert get_new_command(Command(script, ''))[0] == result
