#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Simple class for executing fs-uae with specified parameters. This is a
failsafe class for running fs-uae.
"""
from fs_uae_wrapper import base
from fs_uae_wrapper import utils


class Wrapper(base.Base):
    """Simple class for running fs-uae"""

    def run(self):
        """
        Main function which run FS-UAE
        """
        self._run_emulator()

    def _run_emulator(self):
        """execute fs-uae"""
        utils.run_command(['fs-uae'] + [self.conf_file] +
                          self.fsuae_options.list())

    def clean(self):
        """Do the cleanup. Here - just do nothing"""
        return
