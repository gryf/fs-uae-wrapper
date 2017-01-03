import os
import shutil
from tempfile import mkdtemp
from unittest import TestCase

try:
    from unittest import mock
except ImportError:
    import mock

from fs_uae_wrapper import archive
from fs_uae_wrapper import utils


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

    @mock.patch('fs_uae_wrapper.path.which')
    def test_validate_options(self, which):
        which.return_value = None

        arch = archive.Archive('Config.fs-uae', utils.CmdOption(), {})
        self.assertFalse(arch._validate_options())

        arch.all_options['wrapper'] = 'archive'
        self.assertFalse(arch._validate_options())

        arch.all_options['wrapper_archive'] = 'fake.tgz'
        self.assertFalse(arch._validate_options())

        arch.all_options['wrapper_archiver'] = 'rar'
        self.assertFalse(arch._validate_options())

        which.return_value = 'unrar'
        arch.all_options['wrapper_archiver'] = 'rar'
        self.assertTrue(arch._validate_options())

    @mock.patch('tempfile.mkdtemp')
    @mock.patch('fs_uae_wrapper.path.which')
    @mock.patch('fs_uae_wrapper.archive.Archive._make_archive')
    @mock.patch('fs_uae_wrapper.base.Base._run_emulator')
    @mock.patch('fs_uae_wrapper.base.Base._kickstart_option')
    @mock.patch('fs_uae_wrapper.base.Base._copy_conf')
    @mock.patch('fs_uae_wrapper.base.Base._load_save')
    @mock.patch('fs_uae_wrapper.base.Base._extract')
    def test_run(self, extr, load, copy, kick, run, march, which, mkdtemp):

        extr.return_value = False
        load.return_value = False
        copy.return_value = False
        kick.return_value = False
        run.return_value = False
        march.return_value = False
        which.return_value = 'rar'

        arch = archive.Archive('Config.fs-uae', utils.CmdOption(), {})
        self.assertFalse(arch.run())

        arch.all_options = {'wrapper': 'archive',
                            'wrapper_archive': 'fake.tgz',
                            'wrapper_archiver': 'rar'}

        self.assertFalse(arch.run())

        extr.return_value = True
        self.assertFalse(arch.run())

        load.return_value = True
        self.assertFalse(arch.run())

        copy.return_value = True
        self.assertFalse(arch.run())

        kick.return_value = {'foo': 'bar'}
        self.assertFalse(arch.run())
        self.assertDictEqual(arch.fsuae_options, {'foo': 'bar'})

        run.return_value = True
        self.assertFalse(arch.run())

        march.return_value = True
        self.assertTrue(arch.run())

    @mock.patch('os.rename')
    @mock.patch('os.unlink')
    @mock.patch('shutil.rmtree')
    @mock.patch('fs_uae_wrapper.utils.create_archive')
    @mock.patch('fs_uae_wrapper.base.Base._get_title')
    @mock.patch('fs_uae_wrapper.base.Base._get_saves_dir')
    def test_make_archive(self, sdir, title, carch, rmt, unlink, rename):

        sdir.return_value = None
        title.return_value = ''
        carch.return_value = False

        arch = archive.Archive('Config.fs-uae', utils.CmdOption(), {})
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
