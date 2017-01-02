from unittest import TestCase

try:
    from unittest import mock
except ImportError:
    import mock

from fs_uae_wrapper import archive
from fs_uae_wrapper import utils


class TestArchive(TestCase):

    def test_validate_options(self):

        arch = archive.Archive('Config.fs-uae', utils.CmdOption(), {})
        self.assertFalse(arch._validate_options())

        arch.all_options['wrapper'] = 'archive'
        self.assertFalse(arch._validate_options())

        arch.all_options['wrapper_archive'] = 'fake.tgz'
        self.assertTrue(arch._validate_options())

    @mock.patch('tempfile.mkdtemp')
    @mock.patch('fs_uae_wrapper.base.Base._run_emulator')
    @mock.patch('fs_uae_wrapper.base.Base._kickstart_option')
    @mock.patch('fs_uae_wrapper.base.Base._copy_conf')
    @mock.patch('fs_uae_wrapper.base.Base._extract')
    def test_run(self, extr, cconf, kick, runemul, mkdtemp):

        extr.return_value = False
        cconf.return_value = False
        kick.return_value = {}
        runemul.return_value = False

        arch = archive.Archive('Config.fs-uae', utils.CmdOption(), {})
        self.assertFalse(arch.run())

        arch.all_options = {'wrapper': 'archive',
                            'wrapper_archive': 'fake.tgz'}

        self.assertFalse(arch.run())

        extr.return_value = True
        self.assertFalse(arch.run())

        cconf.return_value = True
        self.assertTrue(arch.run())

        kick.return_value = {'foo': 'bar'}
        self.assertTrue(arch.run())
        self.assertDictEqual(arch.fsuae_options, {'foo': 'bar'})

        runemul.return_value = True
        self.assertTrue(arch.run())
