==============
FS-UAE Wrapper
==============

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
- `7z`_ archiver
- `unrar`_

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

For now, only for ``cd32`` module exists, but there are planned couple more.

cd32
----

There are few assumptions regarding file names and archives. Let's see some
sample config for a game, which is saved as ``ChaosEngine.fs-uae``:

.. code:: ini
   :number-lines:

   [config]
   wrapper = cd32

   amiga_model = CD32
   title = The Chaos Engine CD32

   cdrom_drive_0 = Chaos Engine, The (1994)(Renegade)(M4)[!][CDD3445].cue

   save_states_dir = $CONFIG/fs-uae-save/

   joystick_port_1_mode = cd32 gamepad
   platform = cd32

First assumption is that archive containing files for the game (here: *Chaos
Engine*) should not be in subdirectory. Second, archive name should be the same
as a cue file, so in this case it should be like ``Chaos Engine, The
(1994)(Renegade)(M4)[!][CDD3445].zip`` in case of zip archive. There are three
archive types supported: 7z, rar and zip.

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

License
=======

This work is licensed on 3-clause BSD license. See LICENSE file for details.

..  _FS-UAE: https://fs-uae.net/
.. _relative configuration file: https://fs-uae.net/configuration-files
.. _unrar: http://www.rarlab.com/rar_add.htm
.. _7z: http://p7zip.sourceforge.net/
