import os
import sys
from tempfile import mkstemp, mkdtemp
from unittest import TestCase
import shutil

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
