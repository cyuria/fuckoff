import os
import pytest

from pathlib import Path

from fuckoff import shells
from fuckoff import conf

shells.shell = shells.Generic()


def pytest_configure(config):
    config.addinivalue_line("markers", "functional: mark test as functional")


def pytest_addoption(parser):
    """Adds `--enable-functional` argument."""
    group = parser.getgroup("fuckoff")
    group.addoption('--enable-functional', action="store_true", default=False,
                    help="Enable functional tests")


@pytest.fixture
def no_memoize(monkeypatch):
    monkeypatch.setattr('fuckoff.utils._memoize_disabled', True)


@pytest.fixture(autouse=True)
def settings():
    yield conf.settings
    conf.settings = conf.Settings(
        user_dir=Path('~/.fuckoff')
    )


@pytest.fixture
def no_colors(settings):
    settings.no_colors = True


@pytest.fixture(autouse=True)
def no_cache(monkeypatch):
    monkeypatch.setattr('fuckoff.utils._cache_disabled', True)


@pytest.fixture(autouse=True)
def functional(request):
    if request.node.get_closest_marker('functional') \
            and not request.config.getoption('enable_functional'):
        pytest.skip('functional tests are disabled')


@pytest.fixture
def source_root():
    return Path(__file__).parent.parent.resolve()


@pytest.fixture
def set_shell(monkeypatch):
    def _set(cls):
        shell = cls()
        monkeypatch.setattr('fuckoff.shells.shell', shell)
        return shell

    return _set


@pytest.fixture(autouse=True)
def os_environ(monkeypatch):
    env = {'PATH': os.environ['PATH']}
    monkeypatch.setattr('os.environ', env)
    return env
