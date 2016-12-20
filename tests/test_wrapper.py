import os
import sys
from tempfile import mkstemp, mkdtemp
from unittest import TestCase
import shutil

try:
    from unittest import mock
except ImportError:
    import mock

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

    def test_get_wrapper_from_conf_positive(self):

        configs = ["[conf]\nwrapper=foo\n",
                   "[conf]\n wrapper =foo\n",
                   "[conf]\n wrapper =    foo\n",
                   "[conf]\nwrapper = foo    \n"]

        for cfg in configs:
            with open(self.fname, 'w') as fobj:
                fobj.write(cfg)

            val = wrapper.get_wrapper_from_conf(self.fname)
            self.assertEqual(val, 'foo')

    def test_get_wrapper_from_conf_negative(self):

        configs = ["[conf]\nwraper=foo\n",
                   "[conf]\nwrapper\n",
                   "[conf]\nfullscreen = 1\n"]

        for cfg in configs:
            with open(self.fname, 'w') as fobj:
                fobj.write(cfg)

            val = wrapper.get_wrapper_from_conf(self.fname)
            self.assertIsNone(val)

        configs2 = [("[conf]\nwrapper= = = something went wrong\n",
                     "= = something went wrong"),
                    ("[conf]\nwrapper = =    \n", "="),
                    ("[conf]\nwrapper =     \n", "")]
        for cfg, result in configs2:
            with open(self.fname, 'w') as fobj:
                fobj.write(cfg)

            val = wrapper.get_wrapper_from_conf(self.fname)
            self.assertEqual(val, result)

    @mock.patch('fs_uae_wrapper.plain.run')
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
        mock_plain_run.called_once_with('Config.fs-uae',
                                        ['--fullscreen',
                                         '--fade_out_duration=0'],
                                        [])

        # This will obviously fail for nonexistent module
        sys.argv.append('--wrapper=dummy_wrapper')
        self.assertRaises(SystemExit, wrapper.run)

    def test_parse_option(self):

        # commandline origin
        self.assertEqual(wrapper.parse_option('--fullscreen'),
                         ('fullscreen', '1'))

        self.assertEqual(wrapper.parse_option('--fade_out_duration=0'),
                         ('fade_out_duration', '0'))

        # pass the wrong parameter to fs-uae
        self.assertEqual(wrapper.parse_option('-typo=true'), ('-typo', 'true'))

        # pass the wrong parameter to fs-uae again
        self.assertEqual(wrapper.parse_option('typo=true'), ('typo', 'true'))

        # We have no idea what to do with this - might be a conf file
        self.assertEqual(wrapper.parse_option('this-is-odd'), (None, None))

    def test_parse_args(self):

        # Looking for configuration file... first, we have nothing
        self.assertEqual(wrapper.parse_args(), (None, [], {}))

        # still no luck - nonexistent file
        sys.argv.append('there-is-no-config.fs-uae')
        self.assertEqual(wrapper.parse_args(), (None, [], {}))

        # lets make it
        os.chdir(self.dirname)
        with open('there-is-no-config.fs-uae', 'w') as fobj:
            fobj.write('\n')

        self.assertEqual(wrapper.parse_args(),
                         ('there-is-no-config.fs-uae', [], {}))

        # remove argument, try to find default one
        sys.argv.pop()
        self.assertListEqual(sys.argv, ['fs-uae-wrapper'])

        with open('Config.fs-uae', 'w') as fobj:
            fobj.write('\n')

        self.assertEqual(wrapper.parse_args(), ('Config.fs-uae', [], {}))
