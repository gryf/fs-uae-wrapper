"""
Run CD32 games using fsuae

It will use compressed directories, and create 7z archive for save state dirs.
It is assumed, that filename of cue file (without extension) is the same as
archive with game assets, while using config name (without extension) will be
used as a base for save state (it will append '_save.7z' to the archive file
name.

"""
import os
import shutil
import sys
import tempfile

from fs_uae_wrapper import utils


class CD32(object):
    """
    Class for performing extracting archive, copying emulator files, and
    cleaning it back again
    """
    def __init__(self):
        self.dir = None
        self.conf_file = None
        self.save_filename = None
        self.arch_filepath = None
        self.all_options = None
        self.fsuae_config = None

    def run(self, conf_file, fs_uae_options, configuration):
        """
        Main function which accepts configuration file for FS-UAE
        It will do as follows:
            - set needed full path for asset files
            - extract archive file
            - copy configuration
            - [copy save if exists]
            - run the emulation
            - archive save state

        Params:
            conf_file:      a relative path to provided configuration file
            fs_uae_options: is an CmdOption object created out of command line
                            parameters
            configuration:  is config dictionary created out of config file
        """
        self.all_options = utils.merge_all_options(configuration,
                                                   fs_uae_options)

        if 'wrapper_archive' not in self.all_options:
            sys.stderr.write("Configuration lacks of required "
                             "`wrapper_archive' option.\n")
            return False

        self.fsuae_config = configuration
        self.conf_file = conf_file
        self.dir = tempfile.mkdtemp()

        self.set_assets_paths()
        if not self._extract():
            return False

        for method in (self._copy_conf, self._load_save):
            if not method():
                return False

        kick_opts = self.kickstart_option()
        if kick_opts:
            fs_uae_options.update(kick_opts)

        if self._run_game(fs_uae_options.list()):
            return self._save_save()

        return True

    def clean(self):
        """Remove temporary file"""
        if self.dir:
            shutil.rmtree(self.dir)
        return

    def kickstart_option(self):
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

    def set_assets_paths(self):
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
        self.save_filename = os.path.join(conf_abs_dir, conf_base + '_save.7z')

    def _copy_conf(self):
        """copy provided configuration as Config.fs-uae"""
        shutil.copy(self.conf_file, self.dir)
        os.rename(os.path.join(self.dir, os.path.basename(self.conf_file)),
                  os.path.join(self.dir, 'Config.fs-uae'))
        return True

    def _extract(self):
        """Extract archive to temp dir"""

        item = self.all_options.get('title')
        if not item:
            item = self.all_options['wrapper_archive']

        curdir = os.path.abspath('.')
        os.chdir(self.dir)
        result = utils.extract_archive(self.arch_filepath,
                                       self.all_options.get('wrapper_gui_msg'),
                                       item)
        os.chdir(curdir)
        return result

    def _run_game(self, fs_uae_options):
        """execute game in provided directory"""
        curdir = os.path.abspath('.')
        os.chdir(self.dir)
        utils.run_command(['fs-uae'] + fs_uae_options)
        os.chdir(curdir)
        return True

    def _save_save(self):
        """
        Get the saves from emulator and store it where configuration is placed
        """
        save_path = os.path.join(self.dir, 'fs-uae-save')
        if not os.path.exists(save_path):
            return True

        if os.path.exists(self.save_filename):
            os.unlink(self.save_filename)

        if not utils.run_command(['7z', 'a', self.save_filename,
                                  os.path.join(self.dir, 'fs-uae-save')]):
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


def run(config_file, fs_uae_options, configuration):
    """Run fs-uae with provided config file and options"""

    runner = CD32()
    try:
        return runner.run(config_file, fs_uae_options, configuration)
    finally:
        runner.clean()
