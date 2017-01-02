"""
Base class for all wrapper modules
"""
import os
import sys
import shutil
import tempfile

from fs_uae_wrapper import utils


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
        self.arch_filepath = None

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

        return True

    def clean(self):
        """Remove temporary file"""
        if self.dir:
            shutil.rmtree(self.dir)
        return

    def _kickstart_option(self):
        """
        This is kind of hack - since we potentially can have a relative path
        to kickstart directory, there is a need for getting this option from
        configuration files (which unfortunately can be spanned all over the
        different places, see https://fs-uae.net/configuration-files) and
        check whether or not one of 'kickstarts_dir', 'kickstart_file' or
        'kickstart_ext_file' options are set. In either case if one of those
        options are set and are relative, they should be set to absolute path,
        so that kickstart files can be found by relocated configuration file.
        """

        conf = utils.get_config(self.conf_file)

        kick = {}

        for key in ('kickstart_file', 'kickstart_ext_file', 'kickstarts_dir'):
            val = conf.get(key)
            if val:
                if not os.path.isabs(val):
                    val = utils.interpolate_variables(val, self.conf_file)
                    kick[key] = os.path.abspath(val)
                else:
                    kick[key] = val

        return kick

    def _set_assets_paths(self):
        """
        Set full paths for archive file (without extension) and for save state
        archive file
        """
        conf_abs_dir = os.path.dirname(os.path.abspath(self.conf_file))
        conf_base = os.path.basename(self.conf_file)
        conf_base = os.path.splitext(conf_base)[0]

        arch = self.all_options['wrapper_archive']
        if os.path.isabs(arch):
            self.arch_filepath = arch
        else:
            self.arch_filepath = os.path.join(conf_abs_dir, arch)
        # set optional save_state
        self.save_filename = os.path.join(conf_abs_dir, conf_base + '_save.7z')

    def _copy_conf(self):
        """copy provided configuration as Config.fs-uae"""
        shutil.copy(self.conf_file, self.dir)
        os.rename(os.path.join(self.dir, os.path.basename(self.conf_file)),
                  os.path.join(self.dir, 'Config.fs-uae'))
        return True

    def _extract(self):
        """Extract archive to temp dir"""

        title = self._get_title()
        curdir = os.path.abspath('.')
        os.chdir(self.dir)
        result = utils.extract_archive(self.arch_filepath, title)
        os.chdir(curdir)
        return result

    def _run_emulator(self, fsuae_options):
        """execute fs-uae in provided directory"""
        curdir = os.path.abspath('.')
        os.chdir(self.dir)
        utils.run_command(['fs-uae'] + fsuae_options)
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
        save_path = self._get_saves_dir()
        if not save_path:
            return True

        if os.path.exists(self.save_filename):
            os.unlink(self.save_filename)

        if not utils.run_command(['7z', 'a', self.save_filename, save_path]):
            sys.stderr.write('Error: archiving save state failed\n')
            return False

        return True

    def _load_save(self):
        """
        Put the saves (if exists) to the temp directory.
        """
        if not os.path.exists(self.save_filename):
            return True

        curdir = os.path.abspath('.')
        os.chdir(self.dir)
        utils.run_command(['7z', 'x', self.save_filename])
        os.chdir(curdir)
        return True

    def _get_saves_dir(self):
        """
        Return full path to save state directory or None in cases:
            - there is no save state dir set relative to config file
            - save state dir is set globally
            - save state dir is set relative to the config file
            - save state dir doesn't exists
        """
        if not self.all_options.get('save_states_dir'):
            return None

        if self.all_options['save_states_dir'].startswith('$CONFIG') and \
           '..' not in self.all_options['save_states_dir']:
            save = self.all_options['save_states_dir'].replace('$CONFIG/', '')
        else:
            return None

        save_path = os.path.join(self.dir, save)
        if not os.path.exists(save_path) or not os.path.isdir(save_path):
            return None

        return save_path

    def _validate_options(self):
        """Validate mandatory options"""
        if 'wrapper' not in self.all_options:
            sys.stderr.write("Configuration lacks of required "
                             "`wrapper' option.\n")
            return False
        return True
