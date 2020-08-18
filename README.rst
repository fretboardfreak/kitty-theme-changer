===================
Kitty Theme Changer
===================

:author: Curtis Sand
:author_email: curtissand@gmail.com
:repository: https://github.com/fretboardfreak/kitty-theme-changer.git

Change Kitty Terminal Themes Easily!

Kitty Theme Changer provides simple CLI script that will help you test out and
change theme configuration files for the Kitty Terminal Emulator.

----

Table of Contents:

#. `Installation`_

#. `Configuration`_

#. `Tips and Tricks`_

   #. `First Run`_

   #. `Kitty Configuration Tips`_

----

For more information on the terminal visit: https://github.com/kovidgoyal/kitty

The Kitty Theme Changer script has been tested with the collection of themes
found in the kitty-themes repository: https://github.com/dexpota/kitty-themes

Installation
============

The recommended method for installing the Kitty Theme Changer is to use ``pip``
to install the package into your python environment. This can be done safely
inside a python virtual environment or using the ``--user`` flag on ``pip``
install to install the script in your home directory.

Home directory install::

    pip install --user git+git://github.com/fretboardfreak/kitty-theme-changer.git@master

Note that you *can* install the Kitty Theme Changer into the system's core
python installation but I feel that python package management is a bit cleaner
if user installed packages are kept out of the system directories.

Inside a Python Virtual Environment::

    python -m venv my_python_env
    my_python_env/bin/pip install git+git://github.com/fretboardfreak/kitty-theme-changer.git@master


.. note:: The above URI will install the latest development version of the
          Kitty Theme Changer. To instead install one of the tagged releases
          replace ``@master`` with ``@RELEASE`` where the text RELEASE is the
          tagged version (e.g. ``...kitty-theme-changer.git@0.1``).

As an alternative you could clone this repository and execute the script
directly. This method would not leverage the setuptools entrypoint and would
depend on you ensuring that the script is available in your PATH variable
yourself.

Configuration
=============

1. First step in configuring the Kitty Theme Changer is to download a set of
   themes for kitty (recommendation: https://github.com/dexpota/kitty-themes).

2. Second step is to configure kitty to include a theme config
   file. To do this add the line ``include ./theme.conf`` in your
   kitty.conf file.

3. Third and final step is to create the Kitty Theme Changer
   config file which will point to the correct paths for the
   themes you've collected.

   The Kitty theme changer uses a simple python module as
   a configuration file. By default this is '~/.kittythemechanger.py'.
   The list of required variables and their types are:

   - theme_dir (pathlib.Path): Directory of Kitty theme.conf files.

   - conf_dir (pathlib.Path): Directory Kitty looks in for theme.conf

   - theme_link (pathlib.Path): Symlink file Kitty loads from kitty.conf

   - light_theme_link (pathlib.Path): Symlink to a 'light' theme config file.

   - dark_theme_link (pathlib.Path): Symlink to a 'dark' theme config file.

   - socket (str): a Kitty compatible socket string for the '--listen-on' flag. See 'man kitty'.

   An example .kittythemechanger.py file is shown below::

       '''A config module for the Kitty Theme Changer Tool.'''
       from pathlib import Path
       from os import getpid
       from psutil import process_iter

       theme_dir = Path('~/kitty-themes/themes').expanduser()
       conf_dir = Path('~/.config/kitty').expanduser()
       theme_link = conf_dir.joinpath('theme.conf')
       light_theme_link = conf_dir.joinpath('light-theme.conf')
       dark_theme_link = conf_dir.joinpath('dark-theme.conf')

       def kitty_pid():
         ps = {x.pid: x for x in psutil.process_iter(['name', 'pid', 'ppid'])}
         cp = ps[getpid()]
         while cp.name() != 'kitty':
            cp = cp.parent()
         return cp.pid

       socket = 'unix:/tmp/kitty-socket-{}'.format(kitty_pid())

Tips and Tricks
===============

First Run
---------

On the first run the Kitty Theme Changer script will randomly choose a theme to
set as both the light and dark theme. It does this to create the 3 symlinks in
the kitty configuration directory pointed to by the config file. One pointing
to a light theme, one pointing to a dark theme and a third that ties the kitty
configuration with one of the light or dark links. (kitty.conf -> theme.conf ->
light-theme.conf -> actual theme file). You can prevent a random theme from
being chosen by creating the light and dark symlink files manually (the file
names are set in your Kitty Theme Changer configuration file.) or you can
simply set your themes to your preference after the first run.

Kitty Configuration Tips
------------------------

- Kitty Terminal Emulator Site: https://sw.kovidgoyal.net/kitty/index.html
- Kitty Terminal Configuration Docs: https://sw.kovidgoyal.net/kitty/conf.html

The main features of the Kitty Theme Changer tool - listing themes, setting a
dark or light theme, toggling between configured themes - can be used without
any additional tweaks to the Kitty Terminal config.

However, the "--test" and "--live" features require some settings in order to
work correctly.

- Kitty Remote Control: The remote control feature must be turned on. Either
  with a value of "yes" or a value of "socket-only" to limit remote control
  commands to only use the socket specified in the "--listen-on" flag when
  running kitty. ::

      allow_remote_control yes

- Kitty Socket: Any launchers or aliases that you use to start kitty should
  include a "--listen-on" option. The socket string that you choose for the
  "--listen-on" flag should match the socket string in your Kitty Theme Changer
  configuration file. You can also use "listen_on unix:/tmp/kitty-socket" in kitty.conf

- Single Instance/Instance Groups: For the "--live" feature to change the color
  theme for all running windows it is useful to run kitty with the
  ``--single-instance`` option turned on.

  If you want the Kitty Theme Changer to modify only a set of kitty windows
  then you can make all those windows part of the same Kitty instance using the
  ``--instance-group GROUPNAME`` flag.


.. EOF README
