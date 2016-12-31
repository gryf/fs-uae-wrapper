import os
import sys
from tempfile import mkstemp, mkdtemp
from unittest import TestCase
import shutil

try:
    from unittest import mock
except ImportError:
    import mock

from fs_uae_wrapper import cd32


class TestCD32(TestCase):

    def setUp(self):
        fd, self.fname = mkstemp()
        self.dirname = mkdtemp()
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
        os.unlink(self.fname)
        sys.argv = self._argv[:]

    def test_clean(self):

        acd32 = cd32.CD32()
        acd32.clean()
        self.assertTrue(os.path.exists(self.dirname))

        acd32.dir = self.dirname
        acd32.clean()
        self.assertFalse(os.path.exists(self.dirname))

    @mock.patch('fs_uae_wrapper.utils.get_config')
    def test_kickstart_option(self, get_config):

        acd32 = cd32.CD32()
        get_config.return_value = {'foo': 'bar'}
        self.assertDictEqual(acd32.kickstart_option(), {})

        get_config.return_value = {'kickstarts_dir': '/some/path'}
        self.assertDictEqual(acd32.kickstart_option(),
                             {'kickstarts_dir': '/some/path'})

        os.chdir(self.dirname)
        get_config.return_value = {'kickstarts_dir': '../some/path'}
        result = os.path.abspath(os.path.join(self.dirname, '../some/path'))
        self.assertDictEqual(acd32.kickstart_option(),
                             {'kickstarts_dir': result})

        acd32.conf_file = os.path.join(self.dirname, 'Config.fs-uae')
        get_config.return_value = {'kickstarts_dir': '$CONFIG/../path'}
        result = os.path.abspath(os.path.join(self.dirname, '../path'))
        self.assertDictEqual(acd32.kickstart_option(),
                             {'kickstarts_dir': result})

    def test_set_assets_paths(self):

        acd32 = cd32.CD32()
        os.chdir(self.dirname)
        acd32.conf_file = 'Config.fs-uae'
        acd32.all_options = {'wrapper_archive': 'foo.7z'}

        acd32.set_assets_paths()
        full_path = os.path.join(self.dirname, 'Config_save.7z')
        self.assertEqual(acd32.save_filename, full_path)

        acd32.all_options = {'wrapper_archive': '/home/user/foo.7z'}

        acd32.set_assets_paths()
        full_path = os.path.join(self.dirname, 'Config_save.7z')
        self.assertEqual(acd32.save_filename, full_path)

    def test_copy_conf(self):

        acd32 = cd32.CD32()
        acd32.conf_file = self.fname
        acd32.dir = self.dirname

        self.assertTrue(acd32._copy_conf())
        self.assertTrue(os.path.exists(os.path.join(self.dirname,
                                                    'Config.fs-uae')))
