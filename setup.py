#!/usr/bin/env python
"""
Setup for the fs-uae-wrapper
"""
from distutils.core import setup


setup(name='fs-uae-wrapper',
      packages=['fs_uae_wrapper'],
      version='0.3',
      description='Automate archives and state for fs-uae',
      author='Roman Dobosz',
      author_email='gryf73@gmail.com',
      url='https://github.com/gryf/fs-uea-wrapper',
      download_url='https://github.com/gryf/pygtktalog.git',
      keywords=['uae', 'fs-uae', 'amiga', 'emulator', 'wrapper'],
      scripts=['script/fs-uae-wrapper'],
      classifiers=['Programming Language :: Python :: 2',
                   'Programming Language :: Python :: 2.7',
                   'Programming Language :: Python :: 3',
                   'Programming Language :: Python :: 3.4',
                   'Development Status :: 4 - Beta',
                   'Environment :: Console',
                   'Intended Audience :: End Users/Desktop',
                   'License :: OSI Approved :: BSD License',
                   'Operating System :: OS Independent',
                   'Topic :: System :: Emulators',
                   'Topic :: Games/Entertainment'],
      long_description=open('README.rst').read(),
      options={'test': {'verbose': False,
                        'coverage': False}})
