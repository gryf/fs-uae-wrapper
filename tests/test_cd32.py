import os
import sys
import shutil
from tempfile import mkstemp, mkdtemp
from unittest import TestCase

try:
    from unittest import mock
except ImportError:
    import mock

from fs_uae_wrapper import cd32
from fs_uae_wrapper import utils


class TestCD32(TestCase):

    def setUp(self):
        fd, self.fname = mkstemp()
        self.dirname = mkdtemp()
        self.confdir = mkdtemp()
        os.close(fd)
        self._argv = sys.argv[:]
        sys.argv = ['fs-uae-wrapper']
        self.curdir = os.path.abspath(os.curdir)

    def tearDown(self):
        os.chdir(self.curdir)
        try:
            shutil.rmtree(self.dirname)
        except OSError:
            pass
        try:
            shutil.rmtree(self.confdir)
        except OSError:
            pass
        os.unlink(self.fname)
        sys.argv = self._argv[:]

    def test_clean(self):

        acd32 = cd32.CD32('Config.fs-uae', utils.CmdOption(), {})
        acd32.clean()
        self.assertTrue(os.path.exists(self.dirname))

        acd32.dir = self.dirname
        acd32.clean()
        self.assertFalse(os.path.exists(self.dirname))

    @mock.patch('fs_uae_wrapper.utils.get_config')
    def test_kickstart_option(self, get_config):

        acd32 = cd32.CD32('Config.fs-uae', utils.CmdOption(), {})
        get_config.return_value = {'foo': 'bar'}
        self.assertDictEqual(acd32._kickstart_option(), {})

        get_config.return_value = {'kickstarts_dir': '/some/path'}
        self.assertDictEqual(acd32._kickstart_option(),
                             {'kickstarts_dir': '/some/path'})

        os.chdir(self.dirname)
        get_config.return_value = {'kickstarts_dir': '../some/path'}
        result = os.path.abspath(os.path.join(self.dirname, '../some/path'))
        self.assertDictEqual(acd32._kickstart_option(),
                             {'kickstarts_dir': result})

        acd32.conf_file = os.path.join(self.dirname, 'Config.fs-uae')
        get_config.return_value = {'kickstarts_dir': '$CONFIG/../path'}
        result = os.path.abspath(os.path.join(self.dirname, '../path'))
        self.assertDictEqual(acd32._kickstart_option(),
                             {'kickstarts_dir': result})

    def test_set_assets_paths(self):

        acd32 = cd32.CD32('Config.fs-uae', utils.CmdOption(), {})
        os.chdir(self.dirname)
        acd32.conf_file = 'Config.fs-uae'
        acd32.all_options = {'wrapper_archive': 'foo.7z'}

        acd32._set_assets_paths()
        full_path = os.path.join(self.dirname, 'Config_save.7z')
        self.assertEqual(acd32.save_filename, full_path)

        acd32.all_options = {'wrapper_archive': '/home/user/foo.7z'}

        acd32._set_assets_paths()
        full_path = os.path.join(self.dirname, 'Config_save.7z')
        self.assertEqual(acd32.save_filename, full_path)

    def test_copy_conf(self):

        acd32 = cd32.CD32('Config.fs-uae', utils.CmdOption(), {})
        acd32.conf_file = self.fname
        acd32.dir = self.dirname

        self.assertTrue(acd32._copy_conf())
        self.assertTrue(os.path.exists(os.path.join(self.dirname,
                                                    'Config.fs-uae')))

    @mock.patch('fs_uae_wrapper.utils.extract_archive')
    def test_extract(self, utils_extract):

        acd32 = cd32.CD32('Config.fs-uae', utils.CmdOption(), {})
        acd32.arch_filepath = self.fname
        acd32.dir = self.dirname

        utils_extract.return_value = False

        # message for the gui is taken from title in fs-uae conf or, if there
        # is no such entry, use archive name, which is mandatory to provide
        acd32.all_options = {'title': 'foo_game',
                             'wrapper_gui_msg': '1'}
        self.assertFalse(acd32._extract())
        utils_extract.assert_called_once_with(self.fname, 'foo_game')

        utils_extract.reset_mock()
        acd32.all_options = {'wrapper_archive': 'arch.tar',
                             'wrapper_gui_msg': '1'}
        self.assertFalse(acd32._extract())
        utils_extract.assert_called_once_with(self.fname, 'arch.tar')

        # lets pretend, the extracting has failed
        utils_extract.reset_mock()
        acd32.all_options = {'wrapper_gui_msg': '0'}
        utils_extract.return_value = False
        self.assertFalse(acd32._extract())
        utils_extract.assert_called_once_with(self.fname, '')

    @mock.patch('fs_uae_wrapper.utils.run_command')
    def test_run_emulator(self, run):

        acd32 = cd32.CD32('Config.fs-uae', utils.CmdOption(), {})
        acd32.dir = self.dirname

        self.assertTrue(acd32._run_emulator([]))
        run.assert_called_once_with(['fs-uae'])

        # Errors from emulator are not fatal to wrappers
        run.reset_mock()
        run.return_value = False
        self.assertTrue(acd32._run_emulator([]))
        run.assert_called_once_with(['fs-uae'])

    @mock.patch('fs_uae_wrapper.base.Base._get_saves_dir')
    @mock.patch('fs_uae_wrapper.utils.run_command')
    def test_save_save(self, run, saves_dir):

        acd32 = cd32.CD32('Config.fs-uae', utils.CmdOption(), {})
        acd32.dir = self.dirname
        acd32.save_filename = 'foobar_save.7z'
        saves_dir.acd32.save_filenamereturn_value = None
        run.return_value = True

        self.assertTrue(acd32._save_save())

        saves_dir.return_value = acd32.save_filename
        os.chdir(self.confdir)
        with open(acd32.save_filename, 'w') as fobj:
            fobj.write('asd')

        self.assertTrue(acd32._save_save())

        os.mkdir(os.path.join(self.dirname, 'fs-uae-save'))
        self.assertTrue(acd32._save_save())

        run.return_value = False
        self.assertFalse(acd32._save_save())

    @mock.patch('fs_uae_wrapper.utils.run_command')
    def test_load_save(self, run):

        acd32 = cd32.CD32('Config.fs-uae', utils.CmdOption(), {})
        acd32.dir = self.dirname
        acd32.save_filename = "foobar_save.7z"
        run.return_value = 0

        # fail to load save is not fatal
        self.assertTrue(acd32._load_save())

        os.chdir(self.confdir)
        with open(acd32.save_filename, 'w') as fobj:
            fobj.write('asd')

        self.assertTrue(acd32._load_save())
        run.assert_called_once_with(['7z', 'x', acd32.save_filename])

        # failure in searching for archiver are also non fatal
        run.reset_mock()
        run.return_value = 1
        self.assertTrue(acd32._save_save())
