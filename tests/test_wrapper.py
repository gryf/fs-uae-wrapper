import os
import shutil
import sys
from tempfile import mkdtemp, mkstemp
from unittest import TestCase, mock

from fs_uae_wrapper import wrapper


class TestWrapper(TestCase):

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

    @mock.patch('fs_uae_wrapper.plain.Wrapper.run')
    def test_run(self, mock_plain_run):

        sys.argv.append('--help')
        self.assertRaises(SystemExit, wrapper.run)

        sys.argv.pop()
        self.assertRaises(SystemExit, wrapper.run)

        sys.argv.append('--fullscreen')
        sys.argv.append('--fade_out_duration=0')
        # will exit due to not found configuration
        self.assertRaises(SystemExit, wrapper.run)

        os.chdir(self.dirname)
        with open('Config.fs-uae', 'w') as fobj:
            fobj.write('\n')

        wrapper.run()
        mock_plain_run.assert_called_once()

        # This will obviously fail for nonexistent module
        sys.argv.append('--wrapper=dummy_wrapper')
        self.assertRaises(SystemExit, wrapper.run)

    def test_run_wrong_conf(self):

        os.chdir(self.dirname)
        with open('Config.fs-uae', 'w') as fobj:
            fobj.write('foo\n')

        self.assertRaises(SystemExit, wrapper.run)

    def test_parse_args(self):

        # Looking for configuration file... first, we have nothing
        self.assertEqual(wrapper.parse_args(),
                         (None, {'wrapper_verbose': 0, 'wrapper_quiet': 0}))

        # still no luck - nonexistent file
        sys.argv.append('there-is-no-config.fs-uae')
        self.assertEqual(wrapper.parse_args(),
                         (None, {'wrapper_verbose': 0, 'wrapper_quiet': 0}))

        # lets make it
        os.chdir(self.dirname)
        with open('there-is-no-config.fs-uae', 'w') as fobj:
            fobj.write('\n')

        self.assertEqual(wrapper.parse_args(),
                         ('there-is-no-config.fs-uae',
                          {'wrapper_verbose': 0, 'wrapper_quiet': 0}))

        # remove argument, try to find default one
        sys.argv.pop()
        self.assertListEqual(sys.argv, ['fs-uae-wrapper'])

        with open('Config.fs-uae', 'w') as fobj:
            fobj.write('\n')

        self.assertEqual(wrapper.parse_args(),
                         ('Config.fs-uae',
                          {'wrapper_verbose': 0, 'wrapper_quiet': 0}))

        # add --wrapper-foo and --wrapper-bar options
        sys.argv.extend(['--wrapper=plain', '--wrapper_foo=1',
                         '--wrapper_bar=false'])
        self.assertListEqual(sys.argv,
                             ['fs-uae-wrapper', '--wrapper=plain',
                              '--wrapper_foo=1', '--wrapper_bar=false'])

        with open('Config.fs-uae', 'w') as fobj:
            fobj.write('\n')

        conf, fsopts = wrapper.parse_args()
        self.assertEqual(conf, 'Config.fs-uae')
        self.assertDictEqual(fsopts, {'wrapper': 'plain',
                                      'wrapper_foo': '1',
                                      'wrapper_bar': 'false',
                                      'wrapper_verbose': 0,
                                      'wrapper_quiet': 0})

        # mix wrapper* params in commandline and config
        sys.argv = ['fs-uae-wrapper',
                    '--wrapper=plain',
                    '--wrapper_bar=false',
                    '--fullscreen',
                    '--fast_memory=4096']
        with open('Config.fs-uae', 'w') as fobj:
            fobj.write('[conf]\nwrapper = cd32\nwrapper_foo = /some/path\n')

        conf, fsopts = wrapper.parse_args()
        self.assertEqual(conf, 'Config.fs-uae')
        self.assertDictEqual(fsopts, {'wrapper': 'plain',
                                      'wrapper_bar': 'false',
                                      'fullscreen': '1',
                                      'fast_memory': '4096',
                                      'wrapper_verbose': 0,
                                      'wrapper_quiet': 0})
