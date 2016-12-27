from unittest import TestCase

try:
    from unittest import mock
except ImportError:
    import mock

from fs_uae_wrapper import plain
from fs_uae_wrapper import utils


class TestPlainModule(TestCase):

    @mock.patch('subprocess.call')
    def test_show(self, subprocess_call):

        plain.run('some.conf', utils.CmdOption(), None)
        subprocess_call.assert_called_once()
