"""
File archive classes
"""
import os
import subprocess
import sys
import re

from fs_uae_wrapper import path


class Archive(object):
    """Base class for archive support"""
    ADD = ['a']
    EXTRACT = ['x']
    ARCH = 'false'

    def __init__(self):
        self.archiver = path.which(self.ARCH)
        self._compess = self.archiver
        self._decompess = self.archiver

    def create(self, arch_name, files=None):
        """
        Create archive. Return True on success, False otherwise.
        """
        files = files if files else ['.']
        result = subprocess.call([self._compess] + self.ADD + [arch_name]
                                 + files)
        if result != 0:
            sys.stderr.write("Unable to create archive `%s'\n" % arch_name)
            return False
        return True

    def extract(self, arch_name):
        """
        Extract archive. Return True on success, False otherwise.
        """
        if not os.path.exists(arch_name):
            sys.stderr.write("Archive `%s' doesn't exists.\n" % arch_name)
            return False

        result = subprocess.call([self._decompess] + self.EXTRACT +
                                 [arch_name])
        if result != 0:
            sys.stderr.write("Unable to extract archive `%s'\n" % arch_name)
            return False
        return True


class TarArchive(Archive):
    ADD = ['cf']
    EXTRACT = ['xf']
    ARCH = 'tar'


class TarGzipArchive(TarArchive):
    ADD = ['zcf']


class TarBzip2Archive(TarArchive):
    ADD = ['jcf']


class TarXzArchive(TarArchive):
    ADD = ['Jcf']


class LhaArchive(Archive):
    ARCH = 'lha'


class ZipArchive(Archive):
    ADD = ['a', '-tzip']
    ARCH = ['7z', 'zip']

    def __init__(self):
        super(ZipArchive, self).__init__()
        if self.archiver == 'zip':
            self._decompess = path.which('unzip')
            ZipArchive.ADD = ['-r']
            ZipArchive.EXTRACT = []


class SevenZArchive(Archive):
    ARCH = '7z'


class LzxArchive(Archive):
    EXTRACT = ['-x']
    ARCH = 'unlzx'

    @classmethod
    def create(self, arch_name, files=None):
        sys.stderr.write('Cannot create LZX archive. Only extracting is'
                         'supported\n')
        return False


class RarArchive(Archive):
    ARCH = ['rar', 'unrar']

    def create(self, arch_name, files=None):
        files = files if files else sorted(os.listdir('.'))
        if self.archiver == 'unrar':
            sys.stderr.write('Cannot create RAR archive. Only extracting is'
                             'supported by unrar.\n')
            return False

        result = subprocess.call([self._compess] + self.ADD + [arch_name] +
                                 files)
        if result != 0:
            sys.stderr.write("Unable to create archive `%s'\n" % arch_name)
            return False
        return True


class Archivers(object):
    """Archivers class"""
    archivers = [{'arch': TarArchive, 'name': 'tar', 'ext': ['tar']},
                 {'arch': TarGzipArchive, 'name': 'tgz',
                  'ext': ['tar.gz', 'tgz']},
                 {'arch': TarBzip2Archive, 'name': 'tar.bz2',
                  'ext': ['tar.bz2']},
                 {'arch': TarXzArchive, 'name': 'tar.xz', 'ext': ['tar.xz']},
                 {'arch': RarArchive, 'name': 'rar', 'ext': ['rar']},
                 {'arch': SevenZArchive, 'name': '7z', 'ext': ['7z']},
                 {'arch': ZipArchive, 'name': 'zip', 'ext': ['zip']},
                 {'arch': LhaArchive, 'name': 'lha', 'ext': ['lha', 'lzh']},
                 {'arch': LzxArchive, 'name': 'lzx', 'ext': ['lzx']}]

    @classmethod
    def get(cls, extension):
        """
        Get the archive class or None
        """
        for arch in cls.archivers:
            if extension in arch['ext']:
                return arch['arch']
        return None

    @classmethod
    def get_extension_by_name(cls, name):
        """
        Get the first defined extension for the archive format
        """
        for arch in cls.archivers:
            if name == arch['name']:
                return '.' + arch['ext'][0]
        return None


def get_archiver(arch_name):
    """Return right class for provided archive file name"""

    _, ext = os.path.splitext(arch_name)
    re_tar = re.compile('.*(.[tT][aA][rR].[^.]+$)')
    result = re_tar.match(arch_name)

    if result:
        ext = result.groups()[0]

    if ext:
        ext = ext[1:]

    archiver = Archivers.get(ext)
    if not archiver:
        sys.stderr.write("Unable find archive type for `%s'\n" % arch_name)
        return None

    archobj = archiver()
    if archobj.archiver is None:
        sys.stderr.write("Unable find executable for operating on files"
                         " `*%s'\n" % ext)
        return None

    return archobj
