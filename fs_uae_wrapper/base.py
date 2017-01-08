"""
Base class for all wrapper modules
"""
import logging
import os
import shutil
import sys
import tempfile

from fs_uae_wrapper import utils
from fs_uae_wrapper import path


class Base(object):
    """
    Base class for wrapper modules
    """
    def __init__(self, conf_file, fsuae_options, configuration):
        """
        Params:
            conf_file:      a relative path to provided configuration file
            fsuae_options:  is an CmdOption object created out of command line
                            parameters
            configuration:  is config dictionary created out of config file
        """
        self.conf_file = conf_file
        self.fsuae_config = configuration
        self.fsuae_options = fsuae_options
        self.all_options = utils.merge_all_options(configuration,
                                                   fsuae_options)
        self.dir = None
        self.save_filename = None

    def run(self):
        """
        Main function which accepts configuration file for FS-UAE
        It will do as follows:
            - set needed full path for asset files
            - extract archive file
            - copy configuration
            - [copy save if exists]
            - run the emulation
            - archive save state
        """
        if not self._validate_options():
            return False

        self.dir = tempfile.mkdtemp()
        self._normalize_options()
        self._set_assets_paths()

        return True

    def clean(self):
        """Remove temporary file"""
        if self.dir:
            shutil.rmtree(self.dir)
        return

    def _set_assets_paths(self):
        """
        Set full paths for archive file (without extension) and for save state
        archive file
        """
        conf_abs_dir = os.path.dirname(os.path.abspath(self.conf_file))
        conf_base = os.path.basename(self.conf_file)
        conf_base = os.path.splitext(conf_base)[0]

        # set optional save_state
        arch_ext = utils.get_arch_ext(self.all_options.get('wrapper_archiver'))
        if arch_ext:
            self.save_filename = os.path.join(conf_abs_dir, conf_base +
                                              '_save' + arch_ext)

    def _copy_conf(self):
        """copy provided configuration as Config.fs-uae"""
        shutil.copy(self.conf_file, self.dir)
        os.rename(os.path.join(self.dir, os.path.basename(self.conf_file)),
                  os.path.join(self.dir, 'Config.fs-uae'))
        return True

    def _run_emulator(self):
        """execute fs-uae"""
        curdir = os.path.abspath('.')
        os.chdir(self.dir)
        utils.run_command(['fs-uae'] + self.fsuae_options.list())
        os.chdir(curdir)
        return True

    def _get_title(self):
        """
        Return the title if found in configuration. As a fallback archive file
        name will be used as title.
        """
        title = ''
        gui_msg = self.all_options.get('wrapper_gui_msg', '0')
        if gui_msg == '1':
            title = self.all_options.get('title')
            if not title:
                title = self.all_options['wrapper_archive']
        return title

    def _save_save(self):
        """
        Get the saves from emulator and store it where configuration is placed
        """
        if self.all_options.get('wrapper_save_state', '0') != '1':
            return True

        os.chdir(self.dir)
        save_path = self._get_saves_dir()
        if not save_path:
            return True

        if os.path.exists(self.save_filename):
            os.unlink(self.save_filename)

        curdir = os.path.abspath('.')

        if not utils.create_archive(self.save_filename, '', [save_path]):
            logging.error('Error: archiving save state failed.')
            os.chdir(curdir)
            return False

        os.chdir(curdir)
        return True

    def _load_save(self):
        """
        Put the saves (if exists) to the temp directory.
        """
        if self.all_options.get('wrapper_save_state', '0') != '1':
            return True

        if not os.path.exists(self.save_filename):
            return True

        curdir = os.path.abspath('.')
        os.chdir(self.dir)
        utils.extract_archive(self.save_filename)
        os.chdir(curdir)
        return True

    def _get_saves_dir(self):
        """
        Return path to save state directory or None in cases:
            - there is no save state dir set relative to copied config file
            - save state dir is set globally
            - save state dir is set relative to the config file
            - save state dir doesn't exists
        Note, that returned path is relative not absolute
        """
        if not self.all_options.get('save_states_dir'):
            return None

        if self.all_options['save_states_dir'].startswith('$WRAPPER') and \
           '..' not in self.all_options['save_states_dir']:
            save = self.all_options['save_states_dir'].replace('$WRAPPER/', '')
        else:
            return None

        save_path = os.path.join(self.dir, save)
        if not os.path.exists(save_path) or not os.path.isdir(save_path):
            return None

        if save.endswith('/'):
            save = save[:-1]

        return save

    def _normalize_options(self):
        """
        Search and replace values for options which starts with $CONFIG with
        absolute path for all options.

        Configuration file will be placed in new directory, therefore it is
        needed to calculate new paths so that emulator can find assets.
        """
        options = ['wrapper_archive', 'accelerator_rom', 'base_dir',
                   'cdrom_drive_0', 'cdroms_dir', 'controllers_dir',
                   'cpuboard_flash_ext_file', 'cpuboard_flash_file',
                   'floppies_dir', 'floppy_overlays_dir', 'fmv_rom',
                   'graphics_card_rom', 'hard_drives_dir', 'kickstart_file',
                   'kickstarts_dir', 'logs_dir', 'save_states_dir',
                   'screenshots_output_dir']

        for num in range(20):
            options.append('cdrom_image_%d' % num)
            options.append('floppy_image_%d' % num)

        for num in range(4):
            options.append('floppy_drive_%d' % num)

        for num in range(10):
            options.append('hard_drive_%d' % num)

        changed_options = {}

        for key, val in utils.get_config(self.conf_file).items():

            if key not in options:
                continue

            if val.startswith('/'):
                continue

            if val.startswith('~'):
                continue

            if val.startswith('$HOME'):
                continue

            if val.startswith('$WRAPPER'):
                changed_options[key] = val.replace('$WRAPPER', self.dir)
                continue

            if val.startswith('$CONFIG'):
                abspath = utils.interpolate_variables(val, self.conf_file)
                changed_options[key] = abspath
                continue

            changed_options[key] = os.path.abspath(val)

        self.fsuae_options.update(changed_options)

    def _validate_options(self):
        """Validate mandatory options"""
        if 'wrapper' not in self.all_options:
            logging.error("Configuration lacks of required `wrapper' option.")
            return False

        if self.all_options.get('wrapper_save_state', '0') == '0':
            return True

        if 'wrapper_archiver' not in self.all_options:
            logging.error("Configuration lacks of required "
                          "`wrapper_archiver' option.")
            return False

        if not path.which(self.all_options['wrapper_archiver']):
            logging.error("Cannot find archiver `%s'.",
                          self.all_options['wrapper_archiver'])
            return False

        return True


class ArchiveBase(Base):
    """
    Base class for archive based wrapper modules
    """
    def __init__(self, conf_file, fsuae_options, configuration):
        """
        Params:
            conf_file:      a relative path to provided configuration file
            fsuae_options:  is an CmdOption object created out of command line
                            parameters
            configuration:  is config dictionary created out of config file
        """
        super(ArchiveBase, self).__init__(conf_file, fsuae_options,
                                          configuration)
        self.arch_filepath = None

    def _set_assets_paths(self):
        """
        Set full paths for archive file (without extension) and for save state
        archive file
        """
        super(ArchiveBase, self)._set_assets_paths()

        conf_abs_dir = os.path.dirname(os.path.abspath(self.conf_file))
        arch = self.all_options.get('wrapper_archive')
        if arch:
            if os.path.isabs(arch):
                self.arch_filepath = arch
            else:
                self.arch_filepath = os.path.join(conf_abs_dir, arch)

    def _extract(self):
        """Extract archive to temp dir"""

        title = self._get_title()
        curdir = os.path.abspath('.')
        os.chdir(self.dir)
        result = utils.extract_archive(self.arch_filepath, title)
        os.chdir(curdir)
        return result

    def _validate_options(self):

        validation_result = super(ArchiveBase, self)._validate_options()

        if 'wrapper_archive' not in self.all_options:
            sys.stderr.write("Configuration lacks of required "
                             "`wrapper_archive' option.\n")
            validation_result = False

        return validation_result
