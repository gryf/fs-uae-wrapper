#!/usr/bin/env python
"""
Wrapper for FS-UAE to perform some actions before and or after running the
emulator, if appropriate option is enabled.
"""
import importlib
import os
import sys

from fs_uae_wrapper import utils
from fs_uae_wrapper import WRAPPER_KEY


def parse_args():
    """
    Look out for config file and for config options which would be blindly
    passed to fs-uae.
    """
    fs_conf = None
    options = utils.CmdOption()
    for parameter in sys.argv[1:]:
        try:
            options.add(parameter)
        except AttributeError:
            if os.path.exists(parameter):
                fs_conf = parameter

    if fs_conf is None and os.path.exists('Config.fs-uae'):
        fs_conf = 'Config.fs-uae'

    return fs_conf, options


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
    config_file, cmd_options = parse_args()

    if 'help' in cmd_options:
        usage()
        sys.exit(0)

    if not config_file:
        sys.stderr.write('Error: Configuration file not found\nSee --help'
                         ' for usage\n')
        sys.exit(1)

    configuration = utils.get_config_options(config_file)

    if configuration is None:
        sys.stderr.write('Error: Configuration file have syntax issues\n')
        sys.exit(2)

    wrapper_module = cmd_options.get(WRAPPER_KEY)
    if not wrapper_module:
        wrapper_module = configuration.get(WRAPPER_KEY)

    if not wrapper_module:
        wrapper = importlib.import_module('fs_uae_wrapper.plain')
    else:
        try:
            wrapper = importlib.import_module('fs_uae_wrapper.' +
                                              wrapper_module)
        except ImportError:
            sys.stderr.write("Error: provided wrapper module: `%s' doesn't "
                             "exists.\n" % wrapper_module)
            sys.exit(3)

    if not wrapper.run(config_file, cmd_options, configuration):
        sys.exit(4)


if __name__ == "__main__":
    run()
