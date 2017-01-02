import os
import sys
import shutil
from tempfile import mkstemp, mkdtemp
from unittest import TestCase

try:
    from unittest import mock
except ImportError:
    import mock

from fs_uae_wrapper import base
from fs_uae_wrapper import utils


class TestBase(TestCase):

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

        bobj = base.Base('Config.fs-uae', utils.CmdOption(), {})
        bobj.clean()
        self.assertTrue(os.path.exists(self.dirname))

        bobj.dir = self.dirname
        bobj.clean()
        self.assertFalse(os.path.exists(self.dirname))

    @mock.patch('fs_uae_wrapper.utils.get_config')
    def test_kickstart_option(self, get_config):

        bobj = base.Base('Config.fs-uae', utils.CmdOption(), {})
        get_config.return_value = {'foo': 'bar'}
        self.assertDictEqual(bobj._kickstart_option(), {})

        get_config.return_value = {'kickstarts_dir': '/some/path'}
        self.assertDictEqual(bobj._kickstart_option(),
                             {'kickstarts_dir': '/some/path'})

        os.chdir(self.dirname)
        get_config.return_value = {'kickstarts_dir': '../some/path'}
        result = os.path.abspath(os.path.join(self.dirname, '../some/path'))
        self.assertDictEqual(bobj._kickstart_option(),
                             {'kickstarts_dir': result})

        bobj.conf_file = os.path.join(self.dirname, 'Config.fs-uae')
        get_config.return_value = {'kickstarts_dir': '$CONFIG/../path'}
        result = os.path.abspath(os.path.join(self.dirname, '../path'))
        self.assertDictEqual(bobj._kickstart_option(),
                             {'kickstarts_dir': result})

    def test_set_assets_paths(self):

        bobj = base.Base('Config.fs-uae', utils.CmdOption(), {})
        os.chdir(self.dirname)
        bobj.conf_file = 'Config.fs-uae'
        bobj.all_options = {'wrapper_archive': 'foo.7z',
                            'wrapper_archiver': '7z'}

        bobj._set_assets_paths()
        full_path = os.path.join(self.dirname, 'Config_save.7z')
        self.assertEqual(bobj.save_filename, full_path)

        bobj.all_options = {'wrapper_archive':  '/home/user/foo.7z',
                            'wrapper_archiver': '7z'}

        bobj._set_assets_paths()
        full_path = os.path.join(self.dirname, 'Config_save.7z')
        self.assertEqual(bobj.save_filename, full_path)

    def test_copy_conf(self):

        bobj = base.Base('Config.fs-uae', utils.CmdOption(), {})
        bobj.conf_file = self.fname
        bobj.dir = self.dirname

        self.assertTrue(bobj._copy_conf())
        self.assertTrue(os.path.exists(os.path.join(self.dirname,
                                                    'Config.fs-uae')))

    @mock.patch('fs_uae_wrapper.utils.extract_archive')
    def test_extract(self, utils_extract):

        bobj = base.Base('Config.fs-uae', utils.CmdOption(), {})
        bobj.arch_filepath = self.fname
        bobj.dir = self.dirname

        utils_extract.return_value = False

        # message for the gui is taken from title in fs-uae conf or, if there
        # is no such entry, use archive name, which is mandatory to provide
        bobj.all_options = {'title': 'foo_game', 'wrapper_gui_msg': '1'}
        self.assertFalse(bobj._extract())
        utils_extract.assert_called_once_with(self.fname, 'foo_game')

        utils_extract.reset_mock()
        bobj.all_options = {'wrapper_archive': 'arch.tar',
                            'wrapper_gui_msg': '1'}
        self.assertFalse(bobj._extract())
        utils_extract.assert_called_once_with(self.fname, 'arch.tar')

        # lets pretend, the extracting has failed
        utils_extract.reset_mock()
        bobj.all_options = {'wrapper_gui_msg': '0'}
        utils_extract.return_value = False
        self.assertFalse(bobj._extract())
        utils_extract.assert_called_once_with(self.fname, '')

    @mock.patch('fs_uae_wrapper.utils.run_command')
    def test_run_emulator(self, run):

        bobj = base.Base('Config.fs-uae', utils.CmdOption(), {})
        bobj.dir = self.dirname

        self.assertTrue(bobj._run_emulator([]))
        run.assert_called_once_with(['fs-uae'])

        # Errors from emulator are not fatal to wrappers
        run.reset_mock()
        run.return_value = False
        self.assertTrue(bobj._run_emulator([]))
        run.assert_called_once_with(['fs-uae'])

    @mock.patch('fs_uae_wrapper.base.Base._get_saves_dir')
    @mock.patch('fs_uae_wrapper.utils.create_archive')
    def test_save_save(self, carch, saves_dir):

        bobj = base.Base('Config.fs-uae', utils.CmdOption(), {})
        bobj.dir = self.dirname
        bobj.save_filename = 'foobar_save.7z'
        saves_dir.bobj.save_filenamereturn_value = None
        carch.return_value = True

        self.assertTrue(bobj._save_save())

        saves_dir.return_value = bobj.save_filename
        os.chdir(self.confdir)
        with open(bobj.save_filename, 'w') as fobj:
            fobj.write('asd')

        self.assertTrue(bobj._save_save())

        os.mkdir(os.path.join(self.dirname, 'fs-uae-save'))
        self.assertTrue(bobj._save_save())

        carch.return_value = False
        self.assertFalse(bobj._save_save())

    @mock.patch('fs_uae_wrapper.utils.extract_archive')
    def test_load_save(self, earch):

        bobj = base.Base('Config.fs-uae', utils.CmdOption(), {})
        bobj.dir = self.dirname
        bobj.save_filename = "foobar_save.7z"
        earch.return_value = 0

        # fail to load save is not fatal
        self.assertTrue(bobj._load_save())

        os.chdir(self.confdir)
        with open(bobj.save_filename, 'w') as fobj:
            fobj.write('asd')

        self.assertTrue(bobj._load_save())
        earch.assert_called_once_with(bobj.save_filename)

        # failure in searching for archiver are also non fatal
        earch.reset_mock()
        earch.return_value = 1
        self.assertTrue(bobj._save_save())

    def test_get_saves_dir(self):

        bobj = base.Base('Config.fs-uae', utils.CmdOption(), {})
        bobj.dir = self.dirname

        self.assertIsNone(bobj._get_saves_dir())

        bobj.all_options['save_states_dir'] = '/some/path'
        self.assertIsNone(bobj._get_saves_dir())

        bobj.all_options['save_states_dir'] = '$CONFIG/../saves'
        self.assertIsNone(bobj._get_saves_dir())

        bobj.all_options['save_states_dir'] = '/foo/$CONFIG/saves'
        self.assertIsNone(bobj._get_saves_dir())

        bobj.all_options['save_states_dir'] = '$CONFIG/saves'
        self.assertIsNone(bobj._get_saves_dir())

        path = os.path.join(self.dirname, 'saves')
        with open(path, 'w') as fobj:
            fobj.write('\n')
        self.assertIsNone(bobj._get_saves_dir())

        os.unlink(path)
        os.mkdir(path)
        self.assertEqual(bobj._get_saves_dir(), 'saves')

    @mock.patch('fs_uae_wrapper.path.which')
    def test_validate_options(self, which):

        which.return_value = None

        bobj = base.Base('Config.fs-uae', utils.CmdOption(), {})
        bobj.all_options = {}

        self.assertFalse(bobj._validate_options())

        bobj.all_options = {'wrapper': 'dummy'}
        self.assertFalse(bobj._validate_options())

        bobj.all_options = {'wrapper': 'dummy',
                            'wrapper_archiver': 'myarchiver'}
        self.assertFalse(bobj._validate_options())

        which.return_value = '7z'
        bobj.all_options = {'wrapper': 'dummy',
                            'wrapper_archiver': '7z'}
        self.assertTrue(bobj._validate_options())

    def test_run_clean(self):

        bobj = base.Base('Config.fs-uae', utils.CmdOption(), {})
        bobj.all_options = {}

        self.assertFalse(bobj.run())

        bobj.all_options = {'wrapper': 'dummy',
                            'wrapper_archiver': 'rar'}
        try:
            self.assertTrue(bobj.run())
            self.assertTrue(os.path.exists(bobj.dir))
        finally:
            bobj.clean()
