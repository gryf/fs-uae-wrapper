"""
Misc utilities
"""
from distutils import spawn
import os
import subprocess
import sys
try:
    import configparser
except ImportError:
    import ConfigParser as configparser

from fs_uae_wrapper import message


ARCHIVERS = {'.tar': ['tar', 'xf'],
             '.tgz':  ['tar', 'xf'],
             '.tar.gz':  ['tar', 'xf'],
             '.tar.bz2':  ['tar', 'xf'],
             '.tar.xz':  ['tar', 'xf'],
             '.rar':  ['unrar', 'x'],
             '.7z':  ['7z', 'x'],
             '.zip':  ['7z', 'x'],
             '.lha':  ['lha', 'x'],
             '.lzx':  ['unlzx']}


class CmdOption(dict):
    """
    Holder class for commandline switches.
    """

    def add(self, option):
        """parse and add option to the dictionary"""
        if not option.startswith('--'):
            raise AttributeError("Cannot add option `%s' to the dictionary" %
                                 option)
        if '=' in option:
            key, val = option.split('=', 1)
            key = key[2:].strip()
            self[key] = val.strip()
        else:
            key = option[2:].strip()
            # parameters are always as options - parse them when need it later
            self[key] = '1'

    def list(self):
        """Return list of options as it was passed through the commandline"""
        ret_list = []
        for key, val in self.items():
            if val != '1':
                ret_list.append('--%(k)s=%(v)s' % {'k': key, 'v': val})
            else:
                ret_list.append('--%(k)s' % {'k': key})
        return ret_list


def get_config_options(conf):
    """Read config file and return options as a dict"""
    parser = configparser.SafeConfigParser()
    try:
        parser.read(conf)
    except configparser.ParsingError:
        # Configuration syntax is wrong
        return None

    return {key: val for section in parser.sections()
            for key, val in parser.items(section)}


def extract_archive(arch_name, show_gui_message, message_text):
    """
    Extract provided archive to current directory
    """

    if not os.path.exists(arch_name):
        sys.stderr.write("Archive `%s' doesn't exists.\n" % arch_name)
        return False

    _, ext = os.path.splitext(arch_name)

    cmd = ARCHIVERS.get(ext)

    if cmd is None:
        sys.stderr.write("Unable find archive type for `%s'.\n" % arch_name)
        return False

    msg = message.Message("Extracting files for `%s'. Please be "
                          "patient" % message_text)
    if show_gui_message == '1':
        msg.show()

    try:
        subprocess.check_call(cmd + [arch_name])
    except subprocess.CalledProcessError:
        sys.stderr.write("Error during extracting archive `%s'.\n" % arch_name)
        msg.close()
        return False

    msg.close()
    return True


def merge_all_options(configuration, commandline):
    """
    Merge dictionaries with wrapper options into one. Commandline options
    have precedence.
    """
    options = configuration.copy()
    options.update(commandline)
    return options


def interpolate_variables(string, config_path, base=None):
    """
    Interpolate variables used in fs-uae configuration files, like:
        - $CONFIG
        - $HOME
        - $EXE
        - $APP
        - $DOCUMENTS
        - $BASE
    """

    if '$CONFIG' in string:
        string = string.replace('$CONFIG',
                                os.path.dirname(os.path.abspath(config_path)))
    if '$HOME' in string:
        string = string.replace('$HOME', os.path.expandvars('$HOME'))

    if '$EXE' in string:
        string = string.replace('$EXE', spawn.find_executable('fs-uae'))

    if '$APP' in string:
        string = string.replace('$APP', spawn.find_executable('fs-uae'))

    if '$DOCUMENTS' in string:
        xdg_docs = os.getenv('XDG_DOCUMENTS_DIR',
                             os.path.expanduser('~/Documents'))
        string = string.replace('$DOCUMENTS', xdg_docs)

    if base:
        if '$BASE' in string:
            string = string.replace('$BASE', base)

    return string


def get_config(conf_file):
    """
    Try to find configuration files and collect data from it.
    Will search for paths described in https://fs-uae.net/paths
    - ~/Documents/FS-UAE/Configurations/Default.fs-uae
    - ~/Documents/FS-UAE/Configurations/Host.fs-uae
    - ~/FS-UAE/Configurations/Default.fs-uae
    - ~/FS-UAE/Configurations/Host.fs-uae
    - ~/.config/fs-uae/fs-uae.conf
    - ./fs-uae.conf
    - ./Config.fs-uae
    """

    xdg_conf = os.getenv('XDG_CONFIG_HOME', os.path.expanduser('~/.config'))
    user = os.path.expanduser('~/')
    paths = ((os.path.join(xdg_conf, 'fs-uae/fs-uae.conf'),
              os.path.join(xdg_conf, 'fs-uae/')),
             (os.path.join(user,
                           'Documents/FS-UAE/Configurations/Default.fs-uae'),
              os.path.join(user, 'Documents/FS-UAE')),
             (os.path.join(user, 'FS-UAE/Configurations/Default.fs-uae'),
              os.path.join(user, 'FS-UAE')))

    for path, conf_dir in paths:
        if os.path.exists(path):
            config = get_config_options(path)
            if config is None:
                continue
            conf = get_config_options(conf_file) or {}
            config.update(conf)
            break
    else:
        conf_dir = None
        config = get_config_options(conf_file) or {}

    if 'base_dir' in config:
        base_dir = interpolate_variables(config['base_dir'], conf_file)
        host = os.path.join(base_dir, 'Configurations/Host.fs-uae')

        if os.path.exists(host):
            host_conf = get_config_options(host) or {}
            config.update(host_conf)
            # overwrite host options again via provided custom/relative conf
            conf = get_config_options(conf_file) or {}
            config.update(conf)
    elif conf_dir:
        config['_base_dir'] = conf_dir

    return config
