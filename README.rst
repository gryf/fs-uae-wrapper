==============
FS-UAE Wrapper
==============

.. image:: https://github.com/gryf/fs-uae-wrapper/workflows/Test/badge.svg
   :target: https://github.com/gryf/fs-uae-wrapper/actions?query=workflow%3ATest+event%3Apush+branch%3Amaster

.. image:: https://img.shields.io/pypi/v/fs-uae-wrapper.svg
    :target: https://pypi.python.org/pypi/fs-uae-wrapper

This little utility is a wrapper on great FS-UAE_ emulator, to perform some
actions, like uncompressing archived files (CD ROMs images, filesystems),
launch the emulator and archive emulator save state.

As an example, if there is a collection of CD³² game files and you want to
provide configuration for each game, but want to keep ISO images with
corresponding files in archive (due to size of those images) than FS-UAE
Wrapper is a way to achieve this.

The reason behind writing this wrapper is a need for having a portable set of
games/systems where there would be a way for storing the state of either entire
filesystem or just console state (in case of CD³²) and keeping size small,
preferably in a archive file vs a bunch of files.

Requirements
============

- Python 3
- `fs-uae`_ (obviously :)

Fs-uae-wrapper supports several types of archives:

- `7z`_
- `lha`_
- `lzx`_ - decompress only
- `rar`_ - if only ``unrar`` is available, than only decompression is supported
- `tar`_, also compressed with:

  - bzip2
  - gzip
  - xz

- `zip`_

All of those formats should have corresponding software available in the
system, otherwise archive extraction/compression will fail.

Installation
============

FS-UAE Wrapper is available on `CheeseShop`_ (or python package index if you
will). To install it, you can simply invoke (preferably in ``virtualenv``) a
command:

.. code:: shell-session

   $ pip install fs-uae-wrapper

Note, that if ``virtualenv`` was used, there is no need for activating it every
time, since if invoke wrapper like this:

.. code:: shell-session

   $ /path/to/virtualenv/bin/fs-uae-wrapper

you should be able run the wrapper properly. *Tested only on Linux :)*.

Usage
=====

After installation you should be able to access new command ``fs-uae-wrapper``
(or use the full path to the ``virtualenv`` like on the section above), and it's
invocation is identical like ``fs-uae`` binary:

.. code:: shell-session

   $ fs-uae-wrapper [fs-uae-config-file] [parameters]

There is special option for passing wrapping module, which might be placed
directly in fs-uae configuration or passed as an option:

.. code:: ini

   [config]
   # ...
   wrapper = cd32
   # ...

or

.. code:: shell-session

   $ fs-uae-wrapper --wrapper=cd32

In this case there would several things happen. First, ``Config.fs-uae`` would
be searched, read and there would be ``wrapper`` option searched. If found,
specific module will be loaded and depending on the module, there would be
performed specific tasks before ``fs-uae`` is launched and after it.

Assumption is, that configuration file are written in portable way, so the are
saved as `relative configuration file`_ (hence the name ``Config.fs-uae``),
even if the are named differently. If certain wrapper is specified, it will
create temporary directory and place the configuration file there as
``Config.fs-uae``.

If no ``wrapper`` option would be passed either as an config option or
command line argument, all command line options will be passed to the fs-uae
executable as-is.

Note, that you can also pass all *wrapper* options via commandline in the very
same way as you can pass config options to `fs-uae`, so you don't have to
modify original configuration if you don't want to.

There is also new config variable introduced: ``$WRAPPER`` which have the same
role as ``$CONFIG``, but apply for copied config. For instance - in module
archive there are filesystem extracted to new location - to access this
filesystem relatively to the copied configuration file it is enough to provide
a config option:

.. code:: ini

   [config]
   wrapper = archive
   # ...

   hard_drive_0 = $WRAPPER/my_hardrive

which means, that we are expecting to have system files on ``my_hardrive`` in
directory, where configuration will be copied.

Modules
=======

Currently, couple of wrapper modules are available:

- plain
- cd32
- archive
- savestate
- whdload

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
* ``wrapper_archiver`` (optional) archiver to use for storage save state -
  default ``7z``.
* ``wrapper_gui_msg`` (optional) if set to "1", will display a graphical
  message during extracting files
* ``wrapper_save_state`` (optional) if set to "1", will load/archive save state
  directory, defined as ``$WRAPPER/[save-state-dir-name]`` using provided
  ``wrapper_archiver`` archiver. If this option is enabled,
  ``wrapper_archiver`` will be required.

Module ``cd32`` is used for running ``fs-uae`` with compressed CD images. For
better understanding how it works, let's go through solid example. Here is an
fragment of configuration file is saved as ``ChaosEngine.fs-uae``:

.. code:: ini

   [config]
   wrapper = cd32
   wrapper_archive = ChaosEngine.7z
   wrapper_archiver = zip
   wrapper_gui_msg = 1

   amiga_model = CD32
   title = The Chaos Engine CD32

   cdrom_drive_0 = Chaos Engine, The (1994)(Renegade)(M4)[!][CDD3445].cue

   save_states_dir = $WRAPPER/fs-uae-save/

   joystick_port_1_mode = cd32 gamepad
   platform = cd32
   # ...

Command line invocation of the wrapper would be as follows:

.. code:: shell-session

   $ fs-uae-wrapper ChaosEngine.fs-uae

Now, there several thing will happen:

- Config file will be read, and wrapper module will be found
- New temporary directory will be created
- Archive with game assets will be extracted in that directory
- Configuration file will be copied into that directory, and renamed to
  ``Config.fs-uae``
- If ``wrapper_save_state`` is set, and there is saved state archive, it also
  would be extracted there
- ``fs-uae`` will be launched inside that directory

Next, after ``fs-uae`` quit, there will:

- Optionally create archive containing save state with name like the
  configuration file with additional ``_save`` suffix. In this example it would
  be ``ChaosEngine_save.7z``.
- Wipe out temporary directory

archive
-------

Options used:

* ``wrapper`` (required) with ``archive`` as an value
* ``wrapper_archive`` (optional) path to the archive with assets (usually means
  whole system directories, floppies or hard disk images), defaults to same
  name as configuration file with some detected archive extension. Note, that
  name is case sensitive
* ``wrapper_archiver`` (optional) archiver to use for storage save state -
  default ``7z``.
* ``wrapper_gui_msg`` (optional) if set to "1", will display a graphical
  message during extracting files
* ``wrapper_persist_data`` (optional) if set to "1", will compress (possibly
  changed) data, replacing original archive
* ``wrapper_save_state`` (optional) if set to "1", will archive save state
  directory, defined as ``$WRAPPER/[save-state-dir-name]`` using provided
  ``wrapper_archiver`` archiver. If this option is enabled,
  ``wrapper_archiver`` will be required.

This module is quite useful in two use cases. First is a usual work with
Workbench, where there is a need to keep changes of filesystem. Second is the
opposite - if there is a need to test some software, but not necessary keep it
in a Workbench, than it will act as a temporary copy of the system, so that
next time fs-uae will be run, there will be no files of tested software
cluttering around.

Example configuration:

.. code:: ini

   [config]
   wrapper = archive
   wrapper_archive = Workbench_3.1.tar.bz2
   wrapper_archiver = lha
   wrapper_gui_msg = 1
   wrapper_persist_data = 1
   wrapper_save_state = 1
   # ...

And execution is as usual:

.. code:: shell-session

   $ fs-uae-wrapper Workbench.fs-uae

This module will do several steps (similar as with ``cd32`` wrapper):

- create temporary directory
- extract provided in configuration archive
- extract save state (if ``wrapper_save_state`` is set to ``1`` and archive
  with save exists)
- copy configuration under name ``Config.fs-uae``
- run the fs-uae emulator
- optionally create archive with save state (if save state directory place is
  *not* a global one)
- optionally create new archive under the same name as the original one and
  replace it with original one.

savestate
---------

Options used:

* ``wrapper`` (required) with ``archive`` as an value
* ``wrapper_archiver`` (optional) archiver to use for storage save state -
  default ``7z``.

This module is primarily used to run emulator with read only media attached
(like images of floppies or uncompressed CD-ROMs) and its purpose is to
preserve save state which will be created as an archive alongside with original
configuration file in selected archive format. Note, that there is required to
provide ``wrapper_archiver``, since option ``wrapper_save_state`` is implicitly
set to value ``1`` in this module.

Example configuration:

.. code:: ini

   [config]
   wrapper = savestate
   wrapper_archiver = 7z
   # ...

And execution is as usual:

.. code:: shell-session

   $ fs-uae-wrapper Sanity-Arte.fs-uae

The steps would be as follows:

- create temporary directory
- extract save state (if ``wrapper_save_state`` is set to ``1`` and archive
  with save exists)
- copy configuration under name ``Config.fs-uae``
- run the fs-uae emulator
- optionally create archive with save state (if save state directory place is
  *not* a global one)

whdload
-------

Options used:

* ``wrapper`` (required) with ``whdload`` as an value
* ``wrapper_whdload_base`` (required) path to the whdload base system. Usually
  it's minimal system containing at least whdload executables in C, and config
  in S. Read on below for further details.
* ``wrapper_whdload_options`` (optional) this option will replace the line in
  ``s:whdload-startup`` with specific ``whdload`` options for certain slave.
  For reference look at WHDLoad documentation and/or on ``s:WHDLoad.prefs``.
  Note, that ``Slave=`` option must not be used.
* ``wrapper_archive`` (optional) path to the whdload archive, defaults to same
  name as configuration file with some detected archive extension. Note, that
  name is case sensitive

This module is solely used with whdload distributed games (not just whdload
slave files, but whole games, which can be found on several places on the
internet).

Base image
~~~~~~~~~~

To make it work, first the absolute minimal image need to contain following
structure:

.. code::

   .
   ├── C
   │   ├── DIC
   │   ├── Execute
   │   ├── Patcher
   │   ├── RawDIC
   │   ├── SetPatch
   │   ├── WHDLoad
   │   └── WHDLoadCD32
   └── S
       ├── startup-sequence
       └── WHDLoad.prefs

where the minimum dependences are:

- ``Excecute`` from your copy of Workbench
- `WHDLoad`_ 18.9
- `SetPatch`_ 43.6

and the ``S/startup-sequence`` should at least contain:

.. code::

   setpatch QUIET

   IF EXISTS S:whdload-startup
     Execute S:whdload-startup
   EndIF

To leverage more pleasant UX, additionally those bits should be installed (or -
copied into base image filesystem):

- ``Assign`` and whatever commands you'll be use in scripts from your copy of
- `uaequit`_ - this will allow to quit emulator, after quiting game
  Workbench
- `kgiconload`_ - tool for reading icon and executing *default tool* with
  optionally defined tool types as parameters (in this case: WHDLoad)
- `SKick`_ optionally - for kickstart relocations. Also images of corresponding
  kickstart ROM images will be needed.


and then ``s/startup-sequence`` might looks a follows:

.. code::

   Assign >NIL: ENV: RAM:
   Assign >NIL: T: RAM:

   setpatch QUIET

   IF EXISTS S:whdload-startup
     Execute S:whdload-startup
   EndIF

   C:UAEquit

Creating base image archive
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Now, the tree for the minimal image could look like that:

.. code::

   .
   ├── C
   │   ├── Assign
   │   ├── DIC
   │   ├── Execute
   │   ├── kgiconload
   │   ├── Patcher
   │   ├── RawDIC
   │   ├── SetPatch
   │   ├── UAEquit
   │   ├── WHDLoad
   │   └── WHDLoadCD32
   └── S
       ├── startup-sequence
       └── WHDLoad.prefs

to use relocation tables you'll need to place ``Kickstarts`` drawer into Devs
drawer. Also keep in mind, that corresponding kickstart rom images need to be
placed there as well, otherwise it may or may not work. Structure looks like
this:

.. code::

   .
   ├── C
   │   ├── Assign
   │   ├── …
   │   └── WHDLoadCD32
   ├── Devs
   │   └── Kickstarts
   │       ├── 39115_ROMKick.PAT
   │       ├── 39115_ROMKick.RTB
   │       ├── …
   │       ├── kick40068.A4000.PAT
   │       └── kick40068.A4000.RTB
   └── S
       ├── startup-sequence
       └── WHDLoad.prefs

Important: You'll need to prepare archive with base OS without top directory,
i.e. suppose you have prepared all the files in ``/tmp/baseos``:

.. code:: shell-session

   $ pwd
   /tmp
   $ cd baseos
   $ pwd
   /tmp/basos
   $ ls
   C    S
   $ zip -r /tmp/base.zip .
     adding: C/ (stored 0%)
     adding: C/Assign (deflated 31%)
     adding: C/WHDLoadCD32 (deflated 26%)
     adding: C/RawDIC (deflated 46%)
     adding: C/UAEquit (deflated 39%)
     adding: C/Execute (deflated 42%)
     adding: C/Patcher (deflated 56%)
     adding: C/DIC (deflated 33%)
     adding: C/kgiconload (deflated 49%)
     adding: C/SetPatch (deflated 39%)
     adding: C/WHDLoad (deflated 23%)
     adding: S/ (stored 0%)
     adding: S/startup-sequence (deflated 36%)
     adding: S/WHDLoad.prefs (deflated 51%)

You can do it with other archivers as well, like 7z: ``7z a /tmp/base.7z .`` or
tar with different compressions: ``tar Jcf /tmp/base.tar.xz .``, ``tar zcf
/tmp/base.tgz .``, ``tar jcf /tmp/base.tar.bz2 .``. It should work with all
mentioned at the beginning of this document archivers.

Starting point is in ``S/startup-sequence`` file, where eventually
``S/whdload-startup`` is executed, which will be created by fs-uae-warpper
before execution by fs-uae.


Configuration
~~~~~~~~~~~~~

Now, to use whdload module with any of the WHDLoad game, you'll need to prepare
configuration for the wrapper.

Example configuration:

.. code:: ini

   [config]
   wrapper = whdload
   wrapper_whdload_base = $CONFIG/whdload_base.7z
   # ...

And execution is as usual:

.. code:: shell-session

   $ fs-uae-wrapper ChaosEngine_v1.2_0106.fs-uae

Now, similar to the archive module, it will create temporary directory, unpack
base image there, unpack WHDLoad game archive, search for slave file, and
prepare ``s:whdload-startup``, and finally pass all the configuration to
fs-uae.


Limitations
===========

There is one limitation when using save ``wrapper_save_state`` option. In case
of floppies it should work without any issues, although save state for running
Workbench or WHDLoad games may or may not work. In the past there was an issue
with `fs-uae`_ where saving state was causing data corruption on the emulated
system. Use it with caution!


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
.. _CheeseShop: https://pypi.python.org/pypi/fs-/fs-uae-wrapperuae-wrapper
.. _WHDLoad: https://www.whdload.de
.. _uaequit: https://aminet.net/package/misc/emu/UAEquit
.. _SKick: https://aminet.net/package/util/boot/skick346
.. _SetPatch: https://aminet.net/package/util/boot/SetPatch_43.6b
.. _kgiconload: https://eab.abime.net/showpost.php?p=733614&postcount=92
