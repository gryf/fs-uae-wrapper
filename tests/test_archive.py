import os
import sys
import shutil
from tempfile import mkstemp, mkdtemp
from unittest import TestCase

try:
    from unittest import mock
except ImportError:
    import mock

from fs_uae_wrapper import archive
from fs_uae_wrapper import utils


class TestArchive(TestCase):

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

    def test_validate_options(self):

        arch = archive.Archive('Config.fs-uae', utils.CmdOption(), {})
        self.assertFalse(arch._validate_options())

        arch.all_options['wrapper'] = 'archive'
        self.assertFalse(arch._validate_options())

        arch.all_options['wrapper_archive'] = 'fake.tgz'
        self.assertTrue(arch._validate_options())

    @mock.patch('fs_uae_wrapper.base.Base._run_emulator')
    @mock.patch('fs_uae_wrapper.base.Base._kickstart_option')
    @mock.patch('fs_uae_wrapper.base.Base._copy_conf')
    @mock.patch('fs_uae_wrapper.base.Base._extract')
    def test_run(self, extr, cconf, kick, runemul):

        extr.return_value = False
        cconf.return_value = False
        kick.return_value = {}
        runemul.return_value = False

        try:
            arch = archive.Archive('Config.fs-uae', utils.CmdOption(), {})
            self.assertFalse(arch.run())

            arch.all_options = {'wrapper': 'archive',
                                'wrapper_archive': 'fake.tgz'}

            self.assertFalse(arch.run())

            extr.return_value = True
            self.assertFalse(arch.run())

            cconf.return_value = True
            self.assertTrue(arch.run())

            kick.return_value = {'foo': 'bar'}
            self.assertTrue(arch.run())
            self.assertDictEqual(arch.fsuae_options, {'foo': 'bar'})

            runemul.return_value = True
            self.assertTrue(arch.run())
        finally:
            arch.clean()
