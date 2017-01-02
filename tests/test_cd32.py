from unittest import TestCase

try:
    from unittest import mock
except ImportError:
    import mock

from fs_uae_wrapper import cd32
from fs_uae_wrapper import utils


class TestCD32(TestCase):

    def test_validate_options(self):

        acd32 = cd32.CD32('Config.fs-uae', utils.CmdOption(), {})
        self.assertFalse(acd32._validate_options())

        acd32.all_options['wrapper'] = 'cd32'
        self.assertFalse(acd32._validate_options())

        acd32.all_options['wrapper_archive'] = 'fake.tgz'
        self.assertTrue(acd32._validate_options())

    @mock.patch('tempfile.mkdtemp')
    @mock.patch('fs_uae_wrapper.base.Base._save_save')
    @mock.patch('fs_uae_wrapper.base.Base._run_emulator')
    @mock.patch('fs_uae_wrapper.base.Base._kickstart_option')
    @mock.patch('fs_uae_wrapper.base.Base._load_save')
    @mock.patch('fs_uae_wrapper.base.Base._copy_conf')
    @mock.patch('fs_uae_wrapper.base.Base._extract')
    def test_run(self, extr, cconf, lsave, kick, runemul, ssave, mkdtemp):

        extr.return_value = False
        cconf.return_value = False
        lsave.return_value = False
        kick.return_value = {}
        runemul.return_value = False
        ssave.return_value = False

        acd32 = cd32.CD32('Config.fs-uae', utils.CmdOption(), {})
        self.assertFalse(acd32.run())

        acd32.all_options = {'wrapper': 'cd32',
                             'wrapper_archive': 'fake.tgz'}

        self.assertFalse(acd32.run())

        extr.return_value = True
        self.assertFalse(acd32.run())

        cconf.return_value = True
        self.assertFalse(acd32.run())

        lsave.return_value = True
        self.assertTrue(acd32.run())

        kick.return_value = {'foo': 'bar'}
        self.assertTrue(acd32.run())
        self.assertDictEqual(acd32.fsuae_options, {'foo': 'bar'})

        runemul.return_value = True
        self.assertFalse(acd32.run())

        ssave.return_value = True
        self.assertTrue(acd32.run())
