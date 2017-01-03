from unittest import TestCase

try:
    from unittest import mock
except ImportError:
    import mock

from fs_uae_wrapper import cd32
from fs_uae_wrapper import utils


class TestCD32(TestCase):

    @mock.patch('fs_uae_wrapper.path.which')
    def test_validate_options(self, which):

        which.return_value = 'rar'

        acd32 = cd32.CD32('Config.fs-uae', utils.CmdOption(), {})
        self.assertFalse(acd32._validate_options())

        acd32.all_options['wrapper'] = 'cd32'
        self.assertFalse(acd32._validate_options())

        acd32.all_options['wrapper_archive'] = 'fake.tgz'
        self.assertTrue(acd32._validate_options())

    @mock.patch('tempfile.mkdtemp')
    @mock.patch('fs_uae_wrapper.path.which')
    @mock.patch('fs_uae_wrapper.base.Base._save_save')
    @mock.patch('fs_uae_wrapper.base.Base._get_saves_dir')
    @mock.patch('fs_uae_wrapper.base.Base._run_emulator')
    @mock.patch('fs_uae_wrapper.base.Base._kickstart_option')
    @mock.patch('fs_uae_wrapper.base.Base._copy_conf')
    @mock.patch('fs_uae_wrapper.base.Base._load_save')
    @mock.patch('fs_uae_wrapper.base.Base._extract')
    def test_run(self, extract, load_save, copy_conf, kick_option,
                 run_emulator, get_save_dir, save_state, which, mkdtemp):

        extract.return_value = False
        copy_conf.return_value = False
        load_save.return_value = False
        kick_option.return_value = {}
        run_emulator.return_value = False
        get_save_dir.return_value = False
        save_state.return_value = False
        which.return_value = 'unrar'

        acd32 = cd32.CD32('Config.fs-uae', utils.CmdOption(), {})
        self.assertFalse(acd32.run())

        acd32.all_options = {'wrapper': 'cd32',
                             'wrapper_archive': 'fake.tgz',
                             'wrapper_archiver': 'rar'}

        self.assertFalse(acd32.run())

        extract.return_value = True
        self.assertFalse(acd32.run())

        copy_conf.return_value = True
        self.assertFalse(acd32.run())

        load_save.return_value = True
        self.assertFalse(acd32.run())

        kick_option.return_value = {'foo': 'bar'}
        self.assertFalse(acd32.run())
        self.assertDictEqual(acd32.fsuae_options, {'foo': 'bar'})

        run_emulator.return_value = True
        self.assertTrue(acd32.run())

        get_save_dir.return_value = True
        self.assertFalse(acd32.run())

        save_state.return_value = True
        self.assertTrue(acd32.run())
