"""
File archive classes
"""
import os
import subprocess
import sys


class Archive(object):
    """Base class for archive support"""
    ADD = ['a']
    EXTRACT = ['x']
    ARCH = 'false'

    def __init__(self):
        self.archiver = None
        self.which()

    def create(self, arch_name):
        """
        Create archive using self.archiver and parameters in self.ADD
        attribute
        """
        return subprocess.call([self.archiver] + self.ADD +
                               [arch_name, '.']) == 0

    def extract(self, arch_name):
        """
        Create archive using self.archiver and parameters in self.ADD
        attribute
        """
        return subprocess.call([self.archiver] + self.EXTRACT +
                               [arch_name]) == 0

    def which(self):
        """
        Check if there selected archiver is available in the system and place
        it to the archiver attribute
        """

        if isinstance(self.ARCH, list):
            executables = self.ARCH
        else:
            executables = [self.ARCH]
        for fname in executables:
            for path in os.environ["PATH"].split(os.pathsep):
                path = os.path.join(path.strip('"'), fname)
                if os.path.isfile(path) and os.access(path, os.X_OK):
                    self.archiver = fname
                    return

        self.archiver = None


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
    ARCH = '7z'


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

        return subprocess.call([self.archiver] + self.ADD + [arch_name] +
                               sorted(os.listdir('.'))) == 0


def get_archiver(filename):
    """Return right class for provided archive filename"""

    if not os.path.exists(filename):
        sys.stderr.write("Archive `%s' doesn't exists.\n" % filename)
        return None

    _, ext = os.path.splitext(filename)

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
        return None

    archobj = archiver()
    if archobj.archiver is None:
        return None

    return archobj
