#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Simple class for executing fs-uae with specified parameters. This is a
failsafe class for running fs-uae.
"""
import subprocess
import sys


class Plain(object):
    """Class for run fs-uae"""

    def run(self, conf, fs_uae_options):
        """
        Run the emulation.
        conf is a path to the configuration,
        fs_uae_options is a list contains tokenized options to be passed to
                       fs-uae
        """
        try:
            subprocess.call(['fs-uae'] + [conf] + fs_uae_options)
        except subprocess.CalledProcessError:
            sys.stderr.write('Warning: fs-uae returned non 0 exit code\n')

    def clean(self):
        """In this class, do nothing on exit"""
        return


def run(config_file, fs_uae_options, _, unused):
    """Run fs-uae with provided config file and options"""

    runner = Plain()
    try:
        runner.run(config_file, fs_uae_options)
    finally:
        runner.clean()
