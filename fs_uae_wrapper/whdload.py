"""
Run fs-uae with WHDLoad games

It will use compressed base image and compressed directories.
"""
import logging
import os
import shutil

from fs_uae_wrapper import base
from fs_uae_wrapper import utils


class Wrapper(base.ArchiveBase):
    """
    Class for performing extracting archive, copying emulator files, and
    cleaning it back again
    """
    def __init__(self, conf_file, fsuae_options, configuration):
        super(Wrapper, self).__init__(conf_file, fsuae_options, configuration)
        self.archive_type = None

    def run(self):
        """
        Main function which accepts configuration file for FS-UAE
        It will do as follows:
            - extract base image and archive file
            - copy configuration
            - run the emulation
        """
        logging.debug("run")
        if not super().run():
            return False

        if not self._extract():
            return False

        if not self._copy_conf():
            return False

        return self._run_emulator()

    def _validate_options(self):
        """
        Do the validation for the options, additionally check if there is
        mandatory WHDLoad base OS images set.
        """
        if not super()._validate_options():
            return False

        if not self.all_options.get('wrapper_whdload_base'):
            logging.error("wrapper_whdload_base is not set in configuration, "
                          "exiting.")
            return False
        return True

    def _extract(self):
        """Extract base image and then WHDLoad archive"""
        base_image = self.fsuae_options['wrapper_whdload_base']
        if not os.path.exists(base_image):
            logging.error("Base image `%s` does't exists in provided "
                          "location.", base_image)
            return False

        title = self._get_title()
        curdir = os.path.abspath('.')
        os.chdir(self.dir)
        result = utils.extract_archive(base_image)
        os.chdir(curdir)
        if not result:
            return False

        if not super()._extract():
            return False

        return self._find_slave()

    def _find_slave(self):
        """Find Slave file and create apropriate entry in S:whdload-startup"""
        curdir = os.path.abspath('.')
        os.chdir(self.dir)

        # find slave name
        slave_fname = None
        slave_path = None

        for root, dirs, fnames in os.walk('.'):
            for fname in fnames:
                if fname.lower().endswith('.slave'):
                    slave_path, slave_fname = os.path.normpath(root), fname
                    break
        if slave_fname is None:
            logging.error("Cannot find .slave file in archive.")
            return False

        # find corresponfing info (an icon) fname
        icon_fname = None
        for fname in os.listdir(slave_path):
            if (fname.lower().endswith('.info') and
                os.path.splitext(slave_fname)[0].lower() ==
                os.path.splitext(fname)[0].lower()):
                icon_fname = fname
                break
        if icon_fname is None:
            logging.error("Cannot find .info file corresponding to %s in "
                          "archive.", slave_fname)
            return False

        # Write startup file
        with open("S/whdload-startup", "w") as fobj:
            fobj.write(f"cd {slave_path}\n")
            fobj.write(f"C:kgiconload {icon_fname}\n")

        os.chdir(curdir)
        return True
