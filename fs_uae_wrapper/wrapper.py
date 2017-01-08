#!/usr/bin/env python
"""
Wrapper for FS-UAE to perform some actions before and or after running the
emulator, if appropriate option is enabled.
"""
import importlib
import logging
import os
import sys

from fs_uae_wrapper import utils
from fs_uae_wrapper import WRAPPER_KEY


def setup_logger(options):
    """Setup logger format and level"""

    level = logging.WARNING

    if options['wrapper_quiet']:
        level = logging.ERROR
        if options['wrapper_quiet'] > 1:
            level = logging.CRITICAL

    if options['wrapper_verbose']:
        level = logging.INFO
        if options['wrapper_verbose'] > 1:
            level = logging.DEBUG

    logging.basicConfig(level=level,
                        format="%(asctime)s %(levelname)s: %(message)s")


def parse_args():
    """
    Look out for config file and for config options which would be blindly
    passed to fs-uae.
    """
    fs_conf = None
    options = utils.CmdOption()
    options['wrapper_verbose'] = 0
    options['wrapper_quiet'] = 0

    for parameter in sys.argv[1:]:
        if parameter in ['-v', '-q']:
            if parameter == '-v':
                options['wrapper_verbose'] += 1
            if parameter == '-q':
                options['wrapper_quiet'] += 1
            continue
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
    sys.stdout.write("Usage: %s [conf-file] [-v] [-q] [fs-uae-option...]\n\n"
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
    config_file, fsuae_options = parse_args()
    setup_logger(fsuae_options)
    del fsuae_options['wrapper_verbose']
    del fsuae_options['wrapper_quiet']

    if 'help' in fsuae_options:
        usage()
        sys.exit(0)

    if not config_file:
        logging.error('Error: Configuration file not found. See --help'
                      ' for usage')
        sys.exit(1)

    configuration = utils.get_config_options(config_file)

    if configuration is None:
        logging.error('Error: Configuration file have syntax issues')
        sys.exit(2)

    wrapper_module = fsuae_options.get(WRAPPER_KEY)
    if not wrapper_module:
        wrapper_module = configuration.get(WRAPPER_KEY)

    if not wrapper_module:
        wrapper = importlib.import_module('fs_uae_wrapper.plain')
    else:
        try:
            wrapper = importlib.import_module('fs_uae_wrapper.' +
                                              wrapper_module)
        except ImportError:
            logging.error("Error: provided wrapper module: `%s' doesn't "
                          "exists.", wrapper_module)
            sys.exit(3)

    runner = wrapper.Wrapper(config_file, fsuae_options, configuration)

    try:
        exit_code = runner.run()
    finally:
        runner.clean()

    if not exit_code:
        sys.exit(4)


if __name__ == "__main__":
    run()
