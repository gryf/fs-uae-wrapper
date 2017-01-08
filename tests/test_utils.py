import os
import sys
from tempfile import mkstemp, mkdtemp
from unittest import TestCase
import shutil

try:
    from unittest import mock
except ImportError:
    import mock

from fs_uae_wrapper import utils


class TestUtils(TestCase):

    def setUp(self):
        fd, self.fname = mkstemp()
        self.dirname = mkdtemp()
        os.close(fd)
        self._argv = sys.argv[:]
        sys.argv = ['fs-uae-wrapper']
        self.curdir = os.path.abspath(os.curdir)

    def tearDown(self):
        os.chdir(self.curdir)
        shutil.rmtree(self.dirname)
        os.unlink(self.fname)
        sys.argv = self._argv[:]

    def test_get_config_options(self):

        configs = ["[conf]\nwrapper=foo\n",
                   "[conf]\n wrapper =foo\n",
                   "[conf]\n wrapper =    foo\n",
                   "[conf]\nwrapper = foo    \n"]

        for cfg in configs:
            with open(self.fname, 'w') as fobj:
                fobj.write(cfg)

            val = utils.get_config_options(self.fname)
            self.assertDictEqual(val, {'wrapper': 'foo'})

        with open(self.fname, 'w') as fobj:
            fobj.write("[conf]\nwraper=foo\n")
        conf = utils.get_config_options(self.fname)
        self.assertDictEqual(conf, {'wraper': 'foo'})

        with open(self.fname, 'w') as fobj:
            fobj.write("[conf]\nwrapper\n")
        conf = utils.get_config_options(self.fname)
        self.assertIsNone(conf)

        with open(self.fname, 'w') as fobj:
            fobj.write("[conf]\nfullscreen = 1\n")
        conf = utils.get_config_options(self.fname)
        self.assertDictEqual(conf, {'fullscreen': '1'})

        with open(self.fname, 'w') as fobj:
            fobj.write("[conf]\nwrapper= = = something went wrong\n")
        conf = utils.get_config_options(self.fname)
        self.assertDictEqual(conf, {'wrapper': '= = something went wrong'})

        with open(self.fname, 'w') as fobj:
            fobj.write("[conf]\nwrapper = =    \n")
        conf = utils.get_config_options(self.fname)
        self.assertDictEqual(conf, {'wrapper': '='})

        with open(self.fname, 'w') as fobj:
            fobj.write("[conf]\nwrapper =     \n")
        conf = utils.get_config_options(self.fname)
        self.assertDictEqual(conf, {'wrapper': ''})

    @mock.patch('fs_uae_wrapper.path.which')
    @mock.patch('fs_uae_wrapper.file_archive.Archive.extract')
    @mock.patch('fs_uae_wrapper.file_archive.Archive.create')
    @mock.patch('fs_uae_wrapper.message.Message.close')
    @mock.patch('fs_uae_wrapper.message.Message.show')
    def test_operate_archive(self, show, close, create, extract, which):

        os.chdir(self.dirname)
        which.return_value = None

        # No config
        self.assertFalse(utils.operate_archive('non-existent.7z', 'foo', '',
                                               None))

        # Archive type not known
        with open('unsupported-archive.ace', 'w') as fobj:
            fobj.write("\n")
        self.assertFalse(utils.operate_archive('unsupported-archive.ace',
                                               'foo', '', None))

        # archive is known, but extraction will fail - we have an empty
        # archive and there is no guarantee, that 7z exists on system where
        # test will run
        which.return_value = '7z'
        extract.return_value = True
        with open('supported-archive.7z', 'w') as fobj:
            fobj.write("\n")
        self.assertTrue(utils.operate_archive('supported-archive.7z',
                                              'extract', '', None))
        extract.assert_called_once()

        extract.reset_mock()
        self.assertTrue(utils.operate_archive('supported-archive.7z',
                                              'extract', '', None))
        extract.assert_called_once()

        os.unlink('supported-archive.7z')
        self.assertTrue(utils.operate_archive('supported-archive.7z',
                                              'create', 'test', ['foo']))
        create.assert_called_once()
        show.assert_called_once()

    @mock.patch('fs_uae_wrapper.utils.operate_archive')
    def test_extract_archive(self, operate):

        os.chdir(self.dirname)

        operate.return_value = True
        self.assertTrue(utils.extract_archive('arch.7z'))
        operate.assert_called_once_with('arch.7z', 'extract', '', None)

        operate.reset_mock()
        operate.return_value = False
        self.assertFalse(utils.extract_archive('arch.7z', 'MyFoo',
                                               ['foo', 'bar']))
        operate.assert_called_once_with('arch.7z', 'extract',
                                        "Extracting files for `MyFoo'. Please"
                                        " be patient", ['foo', 'bar'])

    @mock.patch('fs_uae_wrapper.utils.operate_archive')
    def test_create_archive(self, operate):
        operate.return_value = True
        self.assertTrue(utils.create_archive('arch.7z'))
        operate.assert_called_once_with('arch.7z', 'create', '', None)

        operate.reset_mock()
        operate.return_value = False
        self.assertFalse(utils.create_archive('arch.7z', 'MyFoo',
                                              ['foo', 'bar']))
        operate.assert_called_once_with('arch.7z', 'create',
                                        "Creating archive for `MyFoo'. Please"
                                        " be patient", ['foo', 'bar'])

    @mock.patch('fs_uae_wrapper.path.which')
    @mock.patch('fs_uae_wrapper.file_archive.Archive.extract')
    def test_extract_archive_positive(self, arch_extract, which):
        arch_extract.return_value = True
        which.return_value = '7z'

        os.chdir(self.dirname)
        # archive is known, and extraction should succeed
        arch_name = 'archive.7z'
        with open(arch_name, 'w') as fobj:
            fobj.write("\n")
        self.assertTrue(utils.extract_archive(arch_name))
        arch_extract.assert_called_once_with(arch_name)

    def test_merge_all_options(self):

        conf = {'foo': '1', 'bar': 'zip'}
        other = {'foo': '2', 'baz': '3'}

        merged = utils.merge_all_options(conf, other)

        self.assertDictEqual(merged, {'foo': '2', 'bar': 'zip', 'baz': '3'})
        self.assertDictEqual(conf, {'foo': '1', 'bar': 'zip'})
        self.assertDictEqual(other, {'foo': '2', 'baz': '3'})

    @mock.patch('subprocess.call')
    def test_run_command(self, call):
        call.return_value = 0
        self.assertTrue(utils.run_command(['ls']))
        call.assert_called_once_with(['ls'])

        call.reset_mock()
        self.assertTrue(utils.run_command('ls -l'))
        call.assert_called_once_with(['ls', '-l'])

        call.return_value = 1
        call.reset_mock()
        self.assertFalse(utils.run_command(['ls', '-l']))
        call.assert_called_once_with(['ls', '-l'])

        call.reset_mock()
        self.assertFalse(utils.run_command('ls'))
        call.assert_called_once_with(['ls'])

    @mock.patch('os.path.exists')
    def test_get_config(self, exists):
        exists.return_value = False

        os.chdir(self.dirname)
        self.assertDictEqual(utils.get_config('foo'), {})

        with open('conf.fs-uae', 'w') as fobj:
            fobj.write("[conf]\nwrapper=foo\n")
        self.assertDictEqual(utils.get_config('conf.fs-uae'),
                             {'wrapper': 'foo'})


class TestCmdOptions(TestCase):

    def test_add(self):

        cmd = utils.CmdOption()

        # commandline origin
        cmd.add('--fullscreen')
        self.assertEqual(cmd['fullscreen'], '1')

        cmd.add('--fade_out_duration=0')
        self.assertEqual(cmd['fade_out_duration'], '0')

        # pass the wrong parameter to fs-uae
        self.assertRaises(AttributeError, cmd.add, '-typo=0')

        # pass the wrong parameter to fs-uae again
        self.assertRaises(AttributeError, cmd.add, 'typo=true')

        # We have no idea what to do with this - might be a conf file
        self.assertRaises(AttributeError, cmd.add, 'this-is-odd')

    def test_list(self):

        cmd = utils.CmdOption()
        cmd.add('--fullscreen')
        cmd.add('--fast_memory=4096')

        self.assertDictEqual(cmd, {'fullscreen': '1', 'fast_memory': '4096'})
        self.assertListEqual(sorted(cmd.list()),
                             ['--fast_memory=4096', '--fullscreen'])

    @mock.patch('os.getenv')
    @mock.patch('os.path.expandvars')
    @mock.patch('distutils.spawn.find_executable')
    def test_interpolate_variables(self, find_exe, expandv, getenv):

        itrpl = utils.interpolate_variables

        string = '$CONFIG/../path/to/smth'
        self.assertEqual(itrpl(string, '/home/user/Config.fs-uae'),
                         '/home/path/to/smth')
        string = '$HOME'
        expandv.return_value = '/home/user'
        self.assertEqual(itrpl(string, '/home/user/Config.fs-uae'),
                         '/home/user')

        string = '$APP/$EXE'
        find_exe.return_value = '/usr/bin/fs-uae'
        self.assertEqual(itrpl(string, '/home/user/Config.fs-uae'),
                         '/usr/bin/fs-uae//usr/bin/fs-uae')

        string = '$DOCUMENTS'
        getenv.return_value = '/home/user/Docs'
        self.assertEqual(itrpl(string, '/home/user/Config.fs-uae'),
                         '/home/user/Docs')

        string = '$BASE'
        self.assertEqual(itrpl(string, '/home/user/Config.fs-uae'),
                         '$BASE')
        self.assertEqual(itrpl(string, '/home/user/Config.fs-uae', 'base'),
                         'base')
