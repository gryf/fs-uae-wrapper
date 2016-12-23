#!/usr/bin/env python
"""
Wrapper for FS-UAE to perform some actions before and or after running the
emulator, if appropriate option is enabled.
"""
import importlib
import os
import sys


WRAPPER_KEY = 'wrapper'


def get_wrapper_from_conf(conf):
    """
    Process config file only for 'wrapper' option. Specific wrapper modules
    can reread the file, looking for specific for wrapper module options.
    """
    with open(conf) as fobj:
        for line in fobj.readlines():
            if WRAPPER_KEY in line and '=' in line:
                key, val = parse_option(line)
                if key == WRAPPER_KEY:
                    break
        else:
            val = None

    return val


def parse_option(string):
    """
    Return parsed option as an key/value tuple, where key is an stripped
    from dash option name and the value is an value stripped of whitespace.
    """
    key = val = None

    if '=' in string:
        key, val = string.split('=', 1)
        if key.startswith('--'):
            key = key[2:].strip()
        else:
            key = key.strip()
        val = val.strip()
    elif string.startswith('--'):
        key = string[2:].strip()
        # parameters are always as strings - parse them when need it later
        val = '1'

    return key, val


def parse_args():
    """
    Look out for config file and for config options which would be blindly
    passed to fs-uae.
    """
    fs_conf = None
    fs_uae_options = []
    wrapper_options = {}
    for parameter in sys.argv[1:]:
        key, val = parse_option(parameter)
        if key is not None and val is not None:
            if key == WRAPPER_KEY:
                wrapper_options[key] = val
            else:
                fs_uae_options.append(parameter)
        else:
            if os.path.exists(parameter):
                fs_conf = parameter

    if fs_conf is None and os.path.exists('Config.fs-uae'):
        fs_conf = 'Config.fs-uae'

    return fs_conf, fs_uae_options, wrapper_options


def usage():
    """Print help"""
    sys.stdout.write("Usage: %s [conf-file] [fs-uae-option...]\n\n"
                     % sys.argv[0])
    sys.stdout.write("Config file is not required, if `Config.fs-uae' "
                     "exists in the current\ndirectory, although it might "
                     "depend on selected wrapper type. As for the\nfs-uae "
                     "options, please see `http://fs-uae.net/options'. All "
                     "options passed\nvia commandline should start with `--' "
                     "and if they require argument, there\nshould not be a "
                     "space around `='.\n\n")


def run():
    """run wrapper module"""
    config_file, fs_uae_options, wrapper_options = parse_args()

    if '--help' in fs_uae_options:
        usage()
        sys.exit(0)

    if not config_file:
        sys.stderr.write('Error: Configuration file not found\nSee --help'
                         ' for usage\n')
        sys.exit(1)

    wrapper_module = wrapper_options.get(WRAPPER_KEY)
    if not wrapper_module:
        wrapper_module = get_wrapper_from_conf(config_file)

    if not wrapper_module:
        wrapper = importlib.import_module('fs_uae_wrapper.plain')
    else:
        try:
            wrapper = importlib.import_module('fs_uae_wrapper.' +
                                              wrapper_module)
        except ImportError:
            sys.stderr.write("Error: provided wrapper module: `%s' doesn't "
                             "exists.\n" % wrapper_module)
            sys.exit(2)

    wrapper.run(config_file, fs_uae_options, wrapper_options)


if __name__ == "__main__":
    run()
