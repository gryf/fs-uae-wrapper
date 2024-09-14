import os
import shutil
from tempfile import mkdtemp
from unittest import TestCase, mock

from fs_uae_wrapper import utils, whdload


class TestWHDLoad(TestCase):

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

    @mock.patch('fs_uae_wrapper.base.ArchiveBase._validate_options')
    def test_validate_options_arch_validation_fail(self, base_valid):

        base_valid.return_value = False
        wrapper = whdload.Wrapper('Config.fs-uae', utils.CmdOption(), {})
        self.assertFalse(wrapper._validate_options())

    @mock.patch('fs_uae_wrapper.base.ArchiveBase._validate_options')
    def test_validate_options_no_base_image(self, base_valid):

        base_valid.return_value = True
        wrapper = whdload.Wrapper('Config.fs-uae', utils.CmdOption(), {})
        self.assertFalse(wrapper._validate_options())

    @mock.patch('fs_uae_wrapper.base.ArchiveBase._validate_options')
    def test_validate_options_with_base_image_set(self, base_valid):

        base_valid.return_value = True
        wrapper = whdload.Wrapper('Config.fs-uae', utils.CmdOption(), {})
        wrapper.all_options['wrapper_whdload_base'] = 'fake_base_fname.7z'
        self.assertTrue(wrapper._validate_options())

    @mock.patch('fs_uae_wrapper.base.ArchiveBase.run')
    def test_run_base_run_fail(self, run):

        run.return_value = False
        wrapper = whdload.Wrapper('Config.fs-uae', utils.CmdOption(), {})
        self.assertFalse(wrapper.run())

    @mock.patch('fs_uae_wrapper.whdload.Wrapper._extract')
    @mock.patch('fs_uae_wrapper.base.ArchiveBase.run')
    def test_run_extract_fail(self, run, extract):

        run.return_value = True
        extract.return_value = False
        wrapper = whdload.Wrapper('Config.fs-uae', utils.CmdOption(), {})
        wrapper.all_options = {'wrapper': 'whdload',
                               'wrapper_archive': 'fake.tgz',
                               'wrapper_archiver': 'rar'}
        self.assertFalse(wrapper.run())

    @mock.patch('fs_uae_wrapper.base.ArchiveBase._copy_conf')
    @mock.patch('fs_uae_wrapper.whdload.Wrapper._extract')
    @mock.patch('fs_uae_wrapper.base.ArchiveBase.run')
    def test_run_copy_conf_fail(self, run, extract, copy_conf):

        run.return_value = True
        extract.return_value = True
        copy_conf.return_value = False
        wrapper = whdload.Wrapper('Config.fs-uae', utils.CmdOption(), {})
        self.assertFalse(wrapper.run())

    @mock.patch('fs_uae_wrapper.base.ArchiveBase._run_emulator')
    @mock.patch('fs_uae_wrapper.base.ArchiveBase._copy_conf')
    @mock.patch('fs_uae_wrapper.whdload.Wrapper._extract')
    @mock.patch('fs_uae_wrapper.base.ArchiveBase.run')
    def test_run_emulator_fail(self, run, extract, copy_conf, run_emulator):

        run.return_value = True
        extract.return_value = True
        copy_conf.return_value = True
        run_emulator.return_value = False
        wrapper = whdload.Wrapper('Config.fs-uae', utils.CmdOption(), {})
        self.assertFalse(wrapper.run())

    @mock.patch('fs_uae_wrapper.base.ArchiveBase._run_emulator')
    @mock.patch('fs_uae_wrapper.base.ArchiveBase._copy_conf')
    @mock.patch('fs_uae_wrapper.whdload.Wrapper._extract')
    @mock.patch('fs_uae_wrapper.base.ArchiveBase.run')
    def test_run_success(self, run, extract, copy_conf, run_emulator):

        run.return_value = True
        extract.return_value = True
        copy_conf.return_value = True
        run_emulator.return_value = True
        wrapper = whdload.Wrapper('Config.fs-uae', utils.CmdOption(), {})
        self.assertTrue(wrapper.run())

    @mock.patch('os.path.exists')
    def test_extract_nonexistent_image(self, exists):
        exists.return_value = False
        wrapper = whdload.Wrapper('Config.fs-uae', utils.CmdOption(), {})
        wrapper.fsuae_options['wrapper_whdload_base'] = 'fakefilename'
        self.assertFalse(wrapper._extract())

    @mock.patch('os.chdir')
    @mock.patch('os.path.exists')
    def test_extract_extraction_failed(self, exists, chdir):
        exists.return_value = True
        wrapper = whdload.Wrapper('Config.fs-uae', utils.CmdOption(), {})
        wrapper.fsuae_options['wrapper_whdload_base'] = 'fakefilename.7z'
        self.assertFalse(wrapper._extract())

    @mock.patch('fs_uae_wrapper.base.ArchiveBase._extract')
    @mock.patch('fs_uae_wrapper.utils.extract_archive')
    @mock.patch('os.chdir')
    @mock.patch('os.path.exists')
    def test_extract_extraction_of_whdload_arch_failed(self, exists, chdir,
                                                       image_extract,
                                                       arch_extract):
        exists.return_value = True
        image_extract.return_value = True
        arch_extract.return_value = False
        wrapper = whdload.Wrapper('Config.fs-uae', utils.CmdOption(), {})
        wrapper.fsuae_options['wrapper_whdload_base'] = 'fakefilename'
        self.assertFalse(wrapper._extract())

    @mock.patch('fs_uae_wrapper.whdload.Wrapper._find_slave')
    @mock.patch('fs_uae_wrapper.base.ArchiveBase._extract')
    @mock.patch('fs_uae_wrapper.utils.extract_archive')
    @mock.patch('os.chdir')
    @mock.patch('os.path.exists')
    def test_extract_slave_not_found(self, exists, chdir, image_extract,
                                     arch_extract, find_slave):
        exists.return_value = True
        image_extract.return_value = True
        arch_extract.return_value = True
        find_slave.return_value = False
        wrapper = whdload.Wrapper('Config.fs-uae', utils.CmdOption(), {})
        wrapper.fsuae_options['wrapper_whdload_base'] = 'fakefilename'
        self.assertFalse(wrapper._extract())

    @mock.patch('fs_uae_wrapper.whdload.Wrapper._find_slave')
    @mock.patch('fs_uae_wrapper.base.ArchiveBase._extract')
    @mock.patch('fs_uae_wrapper.utils.extract_archive')
    @mock.patch('os.chdir')
    @mock.patch('os.path.exists')
    def test_extract_success(self, exists, chdir, image_extract, arch_extract,
                             find_slave):
        exists.return_value = True
        image_extract.return_value = True
        arch_extract.return_value = True
        find_slave.return_value = True
        wrapper = whdload.Wrapper('Config.fs-uae', utils.CmdOption(), {})
        wrapper.fsuae_options['wrapper_whdload_base'] = 'fakefilename'
        self.assertTrue(wrapper._extract())

    @mock.patch('os.walk')
    @mock.patch('os.chdir')
    def test_find_slave_no_slave_file(self, chdir, walk):
        walk.return_value = [(".", ('game'), ()),
                             ('./game', (), ('foo', 'bar', 'baz'))]
        wrapper = whdload.Wrapper('Config.fs-uae', utils.CmdOption(), {})
        self.assertFalse(wrapper._find_slave())

    @mock.patch('os.listdir')
    @mock.patch('os.walk')
    @mock.patch('os.chdir')
    def test_find_slave_no_corresponding_icon(self, chdir, walk, listdir):
        contents = ('foo', 'bar', 'baz.slave')
        walk.return_value = [(".", ('game'), ()),
                             ('./game', (), contents)]
        listdir.return_value = contents
        wrapper = whdload.Wrapper('Config.fs-uae', utils.CmdOption(), {})
        self.assertFalse(wrapper._find_slave())

    @mock.patch('os.listdir')
    @mock.patch('os.walk')
    @mock.patch('os.chdir')
    def test_find_slave_success(self, chdir, walk, listdir):
        contents = ('foo', 'bar', 'baz.slave', 'baz.info')
        _open = mock.mock_open()
        walk.return_value = [(".", ('C', 'S', 'game'), ()),
                             ('./C', (), ('Assign', 'kgiconload')),
                             ('./S', (), ()),
                             ('./game', (), contents)]
        listdir.return_value = contents
        wrapper = whdload.Wrapper('Config.fs-uae', utils.CmdOption(), {})
        with mock.patch('builtins.open', _open):
            self.assertTrue(wrapper._find_slave())
        handle = _open()
        handle.write.assert_called_once_with('cd game\n'
                                             'C:kgiconload baz.info\n')

    @mock.patch('os.listdir')
    @mock.patch('os.walk')
    @mock.patch('os.chdir')
    def test_find_slave_minial(self, chdir, walk, listdir):
        contents = ('foo', 'bar', 'baz.slave', 'baz.info')
        _open = mock.mock_open()
        walk.return_value = [(".", ('C', 'S', 'game'), ()),
                             ('./C', (), ('Assign', 'WHDLoad')),
                             ('./S', (), ()),
                             ('./game', (), contents)]
        listdir.return_value = contents
        wrapper = whdload.Wrapper('Config.fs-uae', utils.CmdOption(), {})
        with mock.patch('builtins.open', _open):
            self.assertTrue(wrapper._find_slave())
        handle = _open()
        handle.write.assert_called_once_with('cd game\nC:whdload Preload '
                                             'Slave=baz.slave\n')

    @mock.patch('os.listdir')
    @mock.patch('os.walk')
    @mock.patch('os.chdir')
    def test_find_custom_options(self, chdir, walk, listdir):
        contents = ('foo', 'bar', 'baz.slave', 'baz.info')
        _open = mock.mock_open()
        walk.return_value = [(".", ('C', 'S', 'game'), ()),
                             ('./C', (), ('Assign', 'WHDLoad')),
                             ('./S', (), ()),
                             ('./game', (), contents)]
        listdir.return_value = contents
        wrapper = whdload.Wrapper('Config.fs-uae', utils.CmdOption(), {})
        whdl_opts = 'Preload SplashDelay=0 MMU PAL'
        wrapper.fsuae_options['wrapper_whdload_options'] = whdl_opts
        with mock.patch('builtins.open', _open):
            self.assertTrue(wrapper._find_slave())
        handle = _open()
        handle.write.assert_called_once_with(f'cd game\nC:whdload {whdl_opts} '
                                             'Slave=baz.slave\n')
