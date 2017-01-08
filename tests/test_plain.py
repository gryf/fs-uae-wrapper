from unittest import TestCase

try:
    from unittest import mock
except ImportError:
    import mock

from fs_uae_wrapper import plain
from fs_uae_wrapper import utils


class TestPlainModule(TestCase):

    @mock.patch('fs_uae_wrapper.utils.run_command')
    def test_run(self, run_command):
        wrapper = plain.Wrapper('some.conf', utils.CmdOption(), {})
        wrapper.run()
        run_command.assert_called_once_with(['fs-uae', 'some.conf'])

    def test_clean(self):
        wrapper = plain.Wrapper('some.conf', utils.CmdOption(), {})
        self.assertIsNone(wrapper.clean())
