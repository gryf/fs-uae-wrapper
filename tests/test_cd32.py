from unittest import TestCase
from unittest import mock

from fs_uae_wrapper import cd32
from fs_uae_wrapper import utils


class TestCD32(TestCase):

    @mock.patch('tempfile.mkdtemp')
    @mock.patch('fs_uae_wrapper.path.which')
    @mock.patch('fs_uae_wrapper.base.ArchiveBase._get_wrapper_archive_name')
    @mock.patch('fs_uae_wrapper.base.ArchiveBase._save_save')
    @mock.patch('fs_uae_wrapper.base.ArchiveBase._get_saves_dir')
    @mock.patch('fs_uae_wrapper.base.ArchiveBase._run_emulator')
    @mock.patch('fs_uae_wrapper.base.ArchiveBase._copy_conf')
    @mock.patch('fs_uae_wrapper.base.ArchiveBase._load_save')
    @mock.patch('fs_uae_wrapper.base.ArchiveBase._extract')
    def test_run(self, extract, load_save, copy_conf, run_emulator,
                 get_save_dir, save_state, get_wrapper_arch_name, which,
                 mkdtemp):

        extract.return_value = False
        copy_conf.return_value = False
        load_save.return_value = False
        run_emulator.return_value = False
        get_save_dir.return_value = False
        save_state.return_value = False
        get_wrapper_arch_name.return_value = "fake_arch_filename"
        which.return_value = 'unrar'

        acd32 = cd32.Wrapper('Config.fs-uae', utils.CmdOption(), {})
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

        run_emulator.return_value = True
        self.assertTrue(acd32.run())

        get_save_dir.return_value = True
        self.assertFalse(acd32.run())

        save_state.return_value = True
        self.assertTrue(acd32.run())
