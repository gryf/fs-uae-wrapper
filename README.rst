==============
FS-UAE Wrapper
==============

.. image:: https://travis-ci.org/gryf/fs-uae-wrapper.svg?branch=master
    :target: https://travis-ci.org/gryf/fs-uae-wrapper

.. image:: https://img.shields.io/pypi/v/fs-uae-wrapper.svg
    :target: https://pypi.python.org/pypi/fs-uae-wrapper

This little utility is a wrapper on great FS-UAE_ emulator, to perform some
actions, like uncompressing archived files (CD ROMs images, filesystems),
launch the emulator and archive emulator save state.

As an example, if there is a collection of CD³² game files and one want to
provide configuration for each game, but want to keep ISO images with
corresponding files in archive (due to size of those images) than FS-UAE
Wrapper is a way to achieve this.

The reason behind writing this wrapper is a need for having a portable set of
games/systems where there would be a way for storing the state of either entire
filesystem or just console state (in case of CD³²) and keeping size small,
preferably in a archive file vs a bunch of files.

Requirements
============

- Python (2 or 3)
- `fs-uae`_ (obviously :)

Also, there should be archivers programs available for compress/decompress
archives. Fs-uae-wrapper supports several types of archives:

- `7z`_
- `lha`_
- `lzx`_ - decompress only
- `rar`_ - if only ``unrar`` is available, than only decompression is supported
- `tar`_, also compressed with:

  - bzip2
  - gzip
  - xz

- `zip`_

There are several archive types which are supported, ranging from tar
(compressed with gzip, bzip2 and xz), 7z, rar, zip. lha and lzx. All of those
formats should have corresponding decompressors available in the system,
otherwise archive extraction will fail.

Installation
============

Just perform (preferably in ``virtualenv``) a command:

.. code:: shell-session

   $ pip install fs-uae-wrapper

Usage
=====

After installation you should be able to access new command
``fs-uae-wrapper``, and its invocation is identical like ``fs-uae`` binary:

.. code:: shell-session

   $ fs-uae-wrapper [fs-uae-config-file] [parameters]

There is special option for passing wrapping module, which might be placed
directly in fs-uae configuration or passed as an option:

.. code:: ini

   [config]
   ...
   wrapper = cd32
   ...

or

.. code:: shell-session

   $ fs-uae-wrapper --wrapper=cd32

In this case there would several things happen. First, ``Config.fs-uae`` would
be searched, read and there would be ``wrapper`` option searched. If found,
specific module will be loaded and depending on the module, there would be
performed specific tasks before ``fs-uae`` is launched and after it.

Assumption is, that configuration file are written in portable way, so the are
saved as `relative configuration file`_ (hence the name ``Config.fs-uae``, even
if the are named differently. If certain wrapper is specified, it will create
temporary directory and place the configuration file there as
``Config.fs-uae``.

If no ``wrapper`` option would be passed either as an config option or
command line argument, all command line options will be passed to the fs-uae
executable as-is.

Modules
=======

Currently, three wrapper modules are available:

- plain
- cd32
- archive

plain
-----

Options used:

* None

``Plain`` module is kind of dummy or failsafe if you will, since all it do is
run ``fs-uae`` with provided configuration and command line options. It will be
chosen in case when there is no ``wrapper`` option provided neither via the
configuration file nor command line parameter.

cd32
----

Options used:

* ``wrapper`` (required) with ``cd32`` as an value
* ``wrapper_archive`` (required) path to the archive with CD32 iso/cue/wav
* ``wrapper_gui_msg`` (optional) if set to "1", will display a graphical
  message during extracting files

Let's see some sample config for a game, which is saved as
``ChaosEngine.fs-uae``:

.. code:: ini
   :number-lines:

   [config]
   wrapper = cd32
   wrapper_archive = ChaosEngine.7z
   wrapper_gui_msg = 1

   amiga_model = CD32
   title = The Chaos Engine CD32

   cdrom_drive_0 = Chaos Engine, The (1994)(Renegade)(M4)[!][CDD3445].cue

   save_states_dir = $CONFIG/fs-uae-save/

   joystick_port_1_mode = cd32 gamepad
   platform = cd32

Next, the invocation of the wrapper would be as follows:

.. code:: shell-session

   $ fs-uae-wrapper ChaosEngine.fs-uae

Now, there several thing will happen:

- Config file will be read, and wrapper module will be find (because we already
  put it on line 2)
- New temporary directory will be created
- Archive with game assists will be extracted in that directory
- Configuration file will be copied into that directory, and renamed to
  ``Config.fs-uae``
- If there is saved state, it also would be extracted there
- ``fs-uae`` will be launched inside that directory

Next, after ``fs-uae`` quit, there will:

- Create archive containing save state with name like the configuration file
  with additional ``_save`` suffix. In this example it would be
  ``ChaosEngine_save.7z``.
- Wipe out temporary directory

archive
-------

Options used:

* ``wrapper`` (required) with ``cd32`` as an value
* ``wrapper_archive`` (required) path to the archive with assets (usually means
  whole system directories, floppies or hd images)
* ``wrapper_gui_msg`` (optional) if set to "1", will display a graphical
  message during extracting files
* ``wrapper_persist_data`` (optional) if set to "1", will compress (possibly
  changed) data, replacing original archive

Example configuration:

.. code:: ini
   :number-lines:

   [config]
   wrapper = archive
   wrapper_archive = Workbench_3.1.tar.bz2
   wrapper_gui_msg = 1
   wrapper_persist_data = 1

   ...

And execution is as usual:

.. code:: shell-session

   $ fs-uae-wrapper Workbench.fs-uae

This module will do several steps (similar as with ``cd32`` wrapper):

- create temporary directory
- extract provided in configuration archive
- extract save state (if exists)
- copy configuration under name ``Config.fs-uae``
- run the fs-uae emulator
- create archive with save state (if save state directory place is *not* a
  global one)
- optionally create new archive under the same name as the original one and
  replace it with original one.

This module is quite useful in two use cases. First is a usual work with
Workbench, where there is a need to keep changes of filesystem. Second is the
opposite - if there is a need to test some software, but not necessary keep it
in a Workbench, than it will act as a temporary copy of the system, so that
next time fs-uae will be run, there will be no files of tested software
cluttering around.

License
=======

This work is licensed on 3-clause BSD license. See LICENSE file for details.

.. _fs-uae: https://fs-uae.net/
.. _relative configuration file: https://fs-uae.net/configuration-files
.. _rar: http://www.rarlab.com/rar_add.htm
.. _7z: http://p7zip.sourceforge.net/
.. _lha: http://lha.sourceforge.jp
.. _lzx: http://aminet.net/package/misc/unix/unlzx.c.readme
.. _tar: https://www.gnu.org/software/tar/
.. _zip: http://www.info-zip.org
