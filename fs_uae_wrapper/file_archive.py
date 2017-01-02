"""
File archive classes
"""
import os
import subprocess
import sys
import re


def which(archivers):
    """
    Check if there selected archiver is available in the system and place it
    to the archiver attribute
    """

    if not isinstance(archivers, list):
        archivers = [archivers]

    for fname in archivers:
        for path in os.environ["PATH"].split(os.pathsep):
            path = os.path.join(path.strip('"'), fname)
            if os.path.isfile(path) and os.access(path, os.X_OK):
                return fname

    return None


class Archive(object):
    """Base class for archive support"""
    ADD = ['a']
    EXTRACT = ['x']
    ARCH = 'false'

    def __init__(self):
        self.archiver = which(self.ARCH)
        self._compess = self.archiver
        self._decompess = self.archiver

    def create(self, arch_name):
        """
        Create archive. Return True on success, False otherwise.
        """
        result = subprocess.call([self._compess] + self.ADD + [arch_name, '.'])
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
            self._decompess = which('unzip')
            ZipArchive.ADD = ['-r']
            ZipArchive.EXTRACT = []


class SevenZArchive(Archive):
    ARCH = '7z'


class LzxArchive(Archive):
    EXTRACT = ['-x']
    ARCH = 'unlzx'

    @classmethod
    def create(self, arch_name):
        sys.stderr.write('Cannot create LZX archive. Only extracting is'
                         'supported\n')
        return False


class RarArchive(Archive):
    ARCH = ['rar', 'unrar']

    def create(self, arch_name):
        if self.archiver == 'unrar':
            sys.stderr.write('Cannot create RAR archive. Only extracting is'
                             'supported by unrar.\n')
            return False

        result = subprocess.call([self._compess] + self.ADD + [arch_name] +
                                 sorted(os.listdir('.')))
        if result != 0:
            sys.stderr.write("Unable to create archive `%s'\n" % arch_name)
            return False
        return True


def get_archiver(arch_name):
    """Return right class for provided archive file name"""

    _, ext = os.path.splitext(arch_name)
    re_tar = re.compile('.*(.[tT][aA][rR].[^.]+$)')
    result = re_tar.match(arch_name)

    if result:
        ext = result.groups()[0]

    archivers = {'.tar': TarArchive,
                 '.tgz': TarGzipArchive,
                 '.tar.gz': TarGzipArchive,
                 '.tar.bz2': TarBzip2Archive,
                 '.tar.xz': TarXzArchive,
                 '.rar': RarArchive,
                 '.7z': SevenZArchive,
                 '.zip': ZipArchive,
                 '.lha': LhaArchive,
                 '.lzx': LzxArchive}

    archiver = archivers.get(ext)
    if not archiver:
        sys.stderr.write("Unable find archive type for `%s'\n" % arch_name)
        return None

    archobj = archiver()
    if archobj.archiver is None:
        sys.stderr.write("Unable find executable for operating on files"
                         " `*%s'\n" % ext)
        return None

    return archobj
