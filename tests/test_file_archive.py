import os
import sys
import shutil
from tempfile import mkstemp, mkdtemp
from unittest import TestCase

try:
    from unittest import mock
except ImportError:
    import mock

from fs_uae_wrapper import file_archive
from fs_uae_wrapper import utils


class TestArchive(TestCase):

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

    def test_get_archiver(self):
        arch = file_archive.get_archiver('foobarbaz.cab')
        self.assertIsNone(arch)
        with open('foobarbaz.cab', 'w') as fobj:
            fobj.write('\n')
        arch = file_archive.get_archiver('foobarbaz.cab')
        self.assertIsNone(arch)

        with open('foobarbaz.tar', 'w') as fobj:
            fobj.write('\n')

        arch = file_archive.get_archiver('foobarbaz.tar')
        self.assertIsInstance(arch, file_archive.TarArchive)

        file_archive.TarArchive.ARCH = 'blahblah'
        arch = file_archive.get_archiver('foobarbaz.tar')
        self.assertIsNone(arch)
        file_archive.TarArchive.ARCH = 'tar'

    @mock.patch('subprocess.call')
    def test_archive(self, call):
        arch = file_archive.Archive()
        call.return_value = 0

        self.assertTrue(arch.create('foo'))
        call.assert_called_once_with(['false', 'a', 'foo', '.'])

        call.reset_mock()
        call.return_value = 1
        self.assertFalse(arch.extract('foo'))
        call.assert_called_once_with(['false', 'x', 'foo'])

    def test_archive_which(self):
        arch = file_archive.Archive()
        self.assertEqual(arch.archiver, 'false')
        arch.ARCH = 'sh'

        arch.which()
        self.assertEqual(arch.archiver, 'sh')

        arch.ARCH = 'blahblahexec'
        arch.which()
        self.assertIsNone(arch.archiver)

        arch.ARCH = ['blahblahexec', 'pip', 'sh']
        arch.which()
        self.assertEqual(arch.archiver, 'pip')

    @mock.patch('fs_uae_wrapper.file_archive.Archive.which')
    @mock.patch('subprocess.call')
    def test_tar(self, call, which):
        arch = file_archive.TarArchive()
        arch.archiver = 'tar'
        call.return_value = 0

        self.assertTrue(arch.create('foo'))
        call.assert_called_once_with(['tar', 'cf', 'foo', '.'])

        call.reset_mock()
        call.return_value = 1
        self.assertFalse(arch.extract('foo'))
        call.assert_called_once_with(['tar', 'xf', 'foo'])

        call.reset_mock()
        arch = file_archive.TarGzipArchive()
        arch.archiver = 'tar'
        call.return_value = 0
        self.assertTrue(arch.create('foo'))
        call.assert_called_once_with(['tar', 'zcf', 'foo', '.'])

        call.reset_mock()
        call.return_value = 1
        self.assertFalse(arch.extract('foo'))
        call.assert_called_once_with(['tar', 'xf', 'foo'])

        call.reset_mock()
        arch = file_archive.TarBzip2Archive()
        arch.archiver = 'tar'
        call.return_value = 0
        self.assertTrue(arch.create('foo'))
        call.assert_called_once_with(['tar', 'jcf', 'foo', '.'])

        call.reset_mock()
        call.return_value = 1
        self.assertFalse(arch.extract('foo'))
        call.assert_called_once_with(['tar', 'xf', 'foo'])

        call.reset_mock()
        arch = file_archive.TarXzArchive()
        arch.archiver = 'tar'
        call.return_value = 0
        self.assertTrue(arch.create('foo'))
        call.assert_called_once_with(['tar', 'Jcf', 'foo', '.'])

        call.reset_mock()
        call.return_value = 1
        self.assertFalse(arch.extract('foo'))
        call.assert_called_once_with(['tar', 'xf', 'foo'])

    @mock.patch('fs_uae_wrapper.file_archive.Archive.which')
    @mock.patch('subprocess.call')
    def test_lha(self, call, which):
        arch = file_archive.LhaArchive()
        arch.archiver = 'lha'
        call.return_value = 0

        self.assertTrue(arch.create('foo'))
        call.assert_called_once_with(['lha', 'a', 'foo', '.'])

        call.reset_mock()
        call.return_value = 1
        self.assertFalse(arch.extract('foo'))
        call.assert_called_once_with(['lha', 'x', 'foo'])

    @mock.patch('fs_uae_wrapper.file_archive.Archive.which')
    @mock.patch('subprocess.call')
    def test_lzx(self, call, which):
        arch = file_archive.LzxArchive()
        arch.archiver = 'unlzx'
        call.return_value = 0

        self.assertFalse(arch.create('foo'))
        call.assert_not_called()

        call.reset_mock()
        call.return_value = 1
        self.assertFalse(arch.extract('foo'))
        call.assert_called_once_with(['unlzx', '-x', 'foo'])

    @mock.patch('fs_uae_wrapper.file_archive.Archive.which')
    @mock.patch('subprocess.call')
    def test_7zip(self, call, which):
        arch = file_archive.SevenZArchive()
        arch.archiver = '7z'
        call.return_value = 0

        self.assertTrue(arch.create('foo'))
        call.assert_called_once_with(['7z', 'a', 'foo', '.'])

        call.reset_mock()
        call.return_value = 1
        self.assertFalse(arch.extract('foo'))
        call.assert_called_once_with(['7z', 'x', 'foo'])

    @mock.patch('fs_uae_wrapper.file_archive.Archive.which')
    @mock.patch('subprocess.call')
    def test_zip(self, call, which):
        arch = file_archive.ZipArchive()
        arch.archiver = '7z'
        call.return_value = 0

        self.assertTrue(arch.create('foo'))
        call.assert_called_once_with(['7z', 'a', '-tzip', 'foo', '.'])

        call.reset_mock()
        call.return_value = 1
        self.assertFalse(arch.extract('foo'))
        call.assert_called_once_with(['7z', 'x', 'foo'])

    @mock.patch('fs_uae_wrapper.file_archive.Archive.which')
    @mock.patch('subprocess.call')
    def test_rar(self, call, which):
        arch = file_archive.RarArchive()
        arch.archiver = 'rar'
        call.return_value = 0

        self.assertTrue(arch.create('foo'))
        call.assert_called_once_with(['rar', 'a', 'foo'])

        call.reset_mock()
        for fname in ('foo', 'bar', 'baz'):
            with open(fname, 'w') as fobj:
                fobj.write('\n')
        os.mkdir('directory')
        with open('directory/fname', 'w') as fobj:
            fobj.write('\n')
        self.assertTrue(arch.create('foo.rar'))
        call.assert_called_once_with(['rar', 'a', 'foo.rar', 'bar', 'baz',
                                      'directory', 'foo'])

        call.reset_mock()
        call.return_value = 1
        self.assertFalse(arch.extract('foo'))
        call.assert_called_once_with(['rar', 'x', 'foo'])

        call.reset_mock()
        call.return_value = 0
        arch.archiver = 'unrar'

        self.assertFalse(arch.create('foo'))
        call.assert_not_called()

        call.reset_mock()
        call.return_value = 1
        self.assertFalse(arch.extract('foo'))
        call.assert_called_once_with(['unrar', 'x', 'foo'])