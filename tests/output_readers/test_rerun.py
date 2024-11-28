import pytest
import sys
from mock import Mock, patch
from psutil import AccessDenied, TimeoutExpired

from fuckoff.output_readers import rerun


class TestRerun(object):
    def setup_method(self, _):
        self.patcher = patch('fuckoff.output_readers.rerun.Process')
        process_mock = self.patcher.start()
        self.proc_mock = process_mock.return_value = Mock()

    def teardown_method(self, _):
        self.patcher.stop()

    @patch('fuckoff.output_readers.rerun._wait_output', return_value=False)
    @patch('fuckoff.output_readers.rerun.Popen')
    def test_get_output(self, popen_mock, wait_output_mock):
        popen_mock.return_value.stdout.read.return_value = b'output'
        assert rerun.get_output('', '') is None
        wait_output_mock.assert_called_once()

    @pytest.mark.skipif(sys.platform == 'win32', reason="skip when running on Windows")
    @patch('fuckoff.output_readers.rerun._wait_output')
    def test_get_output_unicode_misspell(self, wait_output_mock):
        rerun.get_output(u'pácman', u'pácman')
        wait_output_mock.assert_called_once()

    def test_wait_output_is_slow(self, settings):
        assert rerun._wait_output(Mock(), True)
        self.proc_mock.wait.assert_called_once_with(settings.wait_slow_command)

    def test_wait_output_is_not_slow(self, settings):
        assert rerun._wait_output(Mock(), False)
        self.proc_mock.wait.assert_called_once_with(settings.wait_command)

    @patch('fuckoff.output_readers.rerun._kill_process')
    def test_wait_output_timeout(self, kill_process_mock):
        self.proc_mock.wait.side_effect = TimeoutExpired(3)
        self.proc_mock.children.return_value = []
        assert not rerun._wait_output(Mock(), False)
        kill_process_mock.assert_called_once_with(self.proc_mock)

    @patch('fuckoff.output_readers.rerun._kill_process')
    def test_wait_output_timeout_children(self, kill_process_mock):
        self.proc_mock.wait.side_effect = TimeoutExpired(3)
        self.proc_mock.children.return_value = [Mock()] * 2
        assert not rerun._wait_output(Mock(), False)
        assert kill_process_mock.call_count == 3

    def test_kill_process(self):
        proc = Mock()
        rerun._kill_process(proc)
        proc.kill.assert_called_once_with()

    @patch('fuckoff.output_readers.rerun.logs')
    def test_kill_process_access_denied(self, logs_mock):
        proc = Mock()
        proc.kill.side_effect = AccessDenied()
        rerun._kill_process(proc)
        proc.kill.assert_called_once_with()
        logs_mock.debug.assert_called_once()
