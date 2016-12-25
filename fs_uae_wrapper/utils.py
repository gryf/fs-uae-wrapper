"""
Misc utilities
"""
import os
import subprocess
import sys

from fs_uae_wrapper.wrapper import WRAPPER_KEY


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


def extract_archive(arch_name):
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

    try:
        subprocess.check_call(cmd + [arch_name])
    except subprocess.CalledProcessError:
        sys.stderr.write("Error during extracting archive `%s'.\n" % arch_name)
        return False

    return True


def merge_options(configuration, wrapper_options):
    """
    Merge dictionaries with wrapper options into one. Commandline options
    have precedence.
    """
    options = {}
    for key, val in configuration:
        if WRAPPER_KEY in key:
            options[key] = val

    options.update(wrapper_options)

    return options
