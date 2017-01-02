"""
Run fs-uae with archived filesystem/adf files

It will use compressed directories, and optionally replace source archive with
the temporary one.
"""
import os
import shutil
import sys

from fs_uae_wrapper import base
from fs_uae_wrapper import utils


class Archive(base.Base):
    """
    Class for performing extracting archive, copying emulator files, and
    cleaning it back again
    """
    def __init__(self, conf_file, fsuae_options, configuration):
        super(Archive, self).__init__(conf_file, fsuae_options, configuration)
        self.archive_type = None

    def run(self):
        """
        Main function which accepts configuration file for FS-UAE
        It will do as follows:
            - set needed full path for asset files
            - extract archive file
            - copy configuration
            - run the emulation
            - optionally make archive save state

        Params:
            conf_file:      a relative path to provided configuration file
            fsuae_options: is an CmdOption object created out of command line
                            parameters
            configuration:  is config dictionary created out of config file
        """
        if not super(Archive, self).run():
            return False

        self._set_assets_paths()
        if not self._extract():
            return False

        self._load_save()

        if not self._copy_conf():
            return False

        kick_opts = self._kickstart_option()
        if kick_opts:
            self.fsuae_options.update(kick_opts)

        if not self._run_emulator(self.fsuae_options.list()):
            return False

        return self._make_archive()

    def _validate_options(self):

        validation_result = super(Archive, self)._validate_options()

        if not super(Archive, self)._validate_options():
            validation_result = False

        if 'wrapper_archive' not in self.all_options:
            sys.stderr.write("Configuration lacks of required "
                             "`wrapper_archive' option.\n")
            validation_result = False

        return validation_result

    def _make_archive(self):
        """
        Produce archive and save it back. Than remove old one.
        """
        if self.all_options.get('wrapper_persist_data', '0') != '1':
            return True

        saves = self._get_saves_dir()
        if saves:
            if not self._save_save():
                return False

        curdir = os.path.abspath('.')
        os.chdir(self.dir)

        if saves:
            shutil.rmtree(saves)
        os.unlink('Config.fs-uae')

        title = self._get_title()

        arch = os.path.basename(self.arch_filepath)
        if not utils.create_archive(arch, title):
            return False

        os.rename(arch, self.arch_filepath)
        os.chdir(curdir)
        return True


def run(config_file, fsuae_options, configuration):
    """Run fs-uae with provided config file and options"""

    runner = Archive(config_file, fsuae_options, configuration)
    try:
        return runner.run()
    finally:
        runner.clean()
