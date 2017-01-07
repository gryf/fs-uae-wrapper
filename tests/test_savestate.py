import os
import shutil
from tempfile import mkdtemp
from unittest import TestCase

try:
    from unittest import mock
except ImportError:
    import mock

from fs_uae_wrapper import savestate
from fs_uae_wrapper import utils


class TestSaveState(TestCase):

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

    @mock.patch('tempfile.mkdtemp')
    @mock.patch('fs_uae_wrapper.path.which')
    @mock.patch('fs_uae_wrapper.base.Base._save_save')
    @mock.patch('fs_uae_wrapper.base.Base._get_saves_dir')
    @mock.patch('fs_uae_wrapper.base.Base._run_emulator')
    @mock.patch('fs_uae_wrapper.base.Base._copy_conf')
    @mock.patch('fs_uae_wrapper.base.Base._load_save')
    def test_run(self, load_save, copy_conf, run_emulator, get_save_dir,
                 save_state, which, mkdtemp):

        copy_conf.return_value = False
        run_emulator.return_value = False
        get_save_dir.return_value = False
        save_state.return_value = False
        which.return_value = 'rar'

        arch = savestate.SaveState('Config.fs-uae', utils.CmdOption(), {})
        self.assertFalse(arch.run())

        arch.all_options = {'wrapper': 'savestate',
                            'wrapper_save_state': '1',
                            'wrapper_archiver': 'rar'}

        self.assertFalse(arch.run())

        self.assertFalse(arch.run())

        copy_conf.return_value = True
        self.assertFalse(arch.run())

        run_emulator.return_value = True
        self.assertTrue(arch.run())

        get_save_dir.return_value = True
        self.assertFalse(arch.run())

        save_state.return_value = True
        self.assertTrue(arch.run())

    @mock.patch('fs_uae_wrapper.path.which')
    def test_validate_options(self, which):
        which.return_value = 'unrar'

        arch = savestate.SaveState('Config.fs-uae', utils.CmdOption(), {})
        self.assertFalse(arch._validate_options())

        arch.all_options['wrapper'] = 'savestate'
        self.assertFalse(arch._validate_options())

        arch.all_options['wrapper_archiver'] = 'rar'
        self.assertTrue(arch._validate_options())
