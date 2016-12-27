#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Simple class for executing fs-uae with specified parameters. This is a
failsafe class for running fs-uae.
"""
import subprocess
import sys


def run_plain(conf_file, fs_uae_options):
    """
    Run the emulation.
    conf_file is a path to the configuration,
    fs_uae_options is an dict-like object which contains commandline options to
                   be passed to fs-uae
    """
    try:
        subprocess.call(['fs-uae'] + [conf_file] + fs_uae_options.list())
    except subprocess.CalledProcessError:
        sys.stderr.write('Warning: fs-uae returned non 0 exit code\n')
    return True


def run(config_file, fs_uae_options, _):
    """Run fs-uae with provided config file and options"""
    return run_plain(config_file, fs_uae_options)
