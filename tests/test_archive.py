import os
import shutil
from tempfile import mkdtemp
from unittest import TestCase, mock

from fs_uae_wrapper import archive, utils


class TestArchive(TestCase):

    def setUp(self):
        self.dirname = mkdtemp()
        self.curdir = os.path.abspath(os.curdir)
        os.chdir(self.dirname)

    def tearDown(self):
        os.chdir(self.curdir)
        try:
            shutil.rmtree(self.dirname)
        except OSError:
            pass

    @mock.patch('fs_uae_wrapper.base.ArchiveBase._get_wrapper_archive_name')
    @mock.patch('fs_uae_wrapper.path.which')
    def test_validate_options(self, which, get_wrapper_arch_name):
        which.return_value = 'unrar'

        arch = archive.Wrapper('Config.fs-uae', utils.CmdOption(), {})
        self.assertFalse(arch._validate_options())

        get_wrapper_arch_name.return_value = None
        arch.all_options = {'wrapper': 'archive'}
        self.assertFalse(arch._validate_options())

        get_wrapper_arch_name.return_value = 'fake_arch_filename'
        arch.all_options['wrapper_archive'] = 'rar'
        self.assertTrue(arch._validate_options())

    @mock.patch('tempfile.mkdtemp')
    @mock.patch('fs_uae_wrapper.path.which')
    @mock.patch('fs_uae_wrapper.archive.Wrapper._make_archive')
    @mock.patch('fs_uae_wrapper.base.ArchiveBase._get_wrapper_archive_name')
    @mock.patch('fs_uae_wrapper.base.ArchiveBase._save_save')
    @mock.patch('fs_uae_wrapper.base.ArchiveBase._get_saves_dir')
    @mock.patch('fs_uae_wrapper.base.ArchiveBase._run_emulator')
    @mock.patch('fs_uae_wrapper.base.ArchiveBase._copy_conf')
    @mock.patch('fs_uae_wrapper.base.ArchiveBase._load_save')
    @mock.patch('fs_uae_wrapper.base.ArchiveBase._extract')
    def test_run(self, extract, load_save, copy_conf, run_emulator,
                 get_save_dir, save_state, get_wrapper_arch_name, make_arch,
                 which, mkdtemp):

        extract.return_value = False
        load_save.return_value = False
        copy_conf.return_value = False
        run_emulator.return_value = False
        get_save_dir.return_value = False
        save_state.return_value = False
        get_wrapper_arch_name.return_value = "fake_arch_filename"
        make_arch.return_value = False
        which.return_value = 'rar'

        arch = archive.Wrapper('Config.fs-uae', utils.CmdOption(), {})
        self.assertFalse(arch.run())

        arch.all_options = {'wrapper': 'archive',
                            'wrapper_archive': 'fake.tgz',
                            'wrapper_archiver': 'rar'}

        self.assertFalse(arch.run())

        extract.return_value = True
        self.assertFalse(arch.run())

        load_save.return_value = True
        self.assertFalse(arch.run())

        copy_conf.return_value = True
        self.assertFalse(arch.run())

        run_emulator.return_value = True
        self.assertFalse(arch.run())

        get_save_dir.return_value = True
        self.assertFalse(arch.run())

        save_state.return_value = True
        self.assertFalse(arch.run())

        make_arch.return_value = True
        self.assertTrue(arch.run())

    @mock.patch('os.rename')
    @mock.patch('os.unlink')
    @mock.patch('shutil.rmtree')
    @mock.patch('fs_uae_wrapper.utils.create_archive')
    @mock.patch('fs_uae_wrapper.base.ArchiveBase._get_title')
    @mock.patch('fs_uae_wrapper.base.ArchiveBase._get_saves_dir')
    def test_make_archive(self, sdir, title, carch, rmt, unlink, rename):

        sdir.return_value = None
        title.return_value = ''
        carch.return_value = False

        arch = archive.Wrapper('Config.fs-uae', utils.CmdOption(), {})
        arch.dir = self.dirname
        arch.arch_filepath = os.path.join(self.dirname, 'foo.tgz')
        arch.all_options = {}
        self.assertTrue(arch._make_archive())

        arch.all_options['wrapper_persist_data'] = '1'
        self.assertFalse(arch._make_archive())

        carch.return_value = True
        self.assertTrue(arch._make_archive())

        sdir.return_value = '/some/path'
        self.assertTrue(arch._make_archive())
