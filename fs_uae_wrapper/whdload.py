"""
Run fs-uae with WHDLoad games

It will use compressed base image and compressed directories.
"""
import logging
import os

from fs_uae_wrapper import base, utils


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
        case_insensitvie_map = {}

        # build case insensitive map of paths and find the slave file
        for root, dirnames, fnames in os.walk('.'):
            for dirname in dirnames:
                full_path = os.path.normpath(os.path.join(root, dirname))
                case_insensitvie_map[full_path.lower()] = full_path

            for fname in fnames:
                full_path = os.path.normpath(os.path.join(root, fname))
                case_insensitvie_map[full_path.lower()] = full_path
                if not slave_fname and fname.lower().endswith('.slave'):
                    slave_path, slave_fname = os.path.normpath(root), fname

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

        # find proper way to handle slave
        # 1. check if there are user provided params
        contents = f"cd {slave_path}\n"
        if self.fsuae_options.get('wrapper_whdload_options'):
            contents = (f"{contents}"
                        f"C:whdload "
                        f"{self.fsuae_options['wrapper_whdload_options']} "
                        f"Slave={slave_fname}\n")
        else:
            # no params, find if kgiconload is available
            if case_insensitvie_map.get('c/kgiconload'):
                contents = f"{contents}C:kgiconload {icon_fname}\n"
            else:
                # if not, just add common defaults
                contents = (f"{contents}C:whdload Preload "
                            f"Slave={slave_fname}\n")

        fname = os.path.join(case_insensitvie_map.get('s'), 'whdload-startup')
        with open(fname, "w") as fobj:
            fobj.write(contents)

        os.chdir(curdir)
        return True
