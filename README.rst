===================
Kitty Theme Changer
===================

:author: Curtis Sand
:author_email: curtissand@gmail.com
:repository: https://github.com/fretboardfreak/kitty-theme-changer.git

Change Kitty Terminal Themes Easily!

Kitty Theme Changer provides simple CLI script that will help you test out and
change theme configuration files for the Kitty Terminal Emulator.

For more information on the terminal visit: https://github.com/kovidgoyal/kitty

The Kitty Theme Changer script has been tested with the collection of themes
found in the kitty-themes repository: https://github.com/dexpota/kitty-themes

Installation
============

The recommended method for installing the Kitty Theme Changer is to use ``pip``
to install the package into your python environment. This can be done safely
inside a python virtual environment or using the ``--user`` flag on the system
wide ``pip`` install.

System Wide::

    pip install --user git+git://github.com/fretboardfreak/kitty-theme-changer.git@master

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


1. First step in configuring the Kitty Theme Changer is to
   download a set of themes for kitty
   (recommendation: https://github.com/dexpota/kitty-themes).

2. Second step is to configure kitty to include a theme config
   file. To do this add the line 'include ./theme.conf' in your
   kitty.conf file.

3. Third step is to add the symlinks that the Kitty Theme
   Changer uses to toggle between a light and a dark theme.
   Create these inside '~/.config/kitty/' with::

       ln -s /path/to/kitty/themes/sometheme.conf light-theme.conf
       ln -s /path/to/kitty/themes/othertheme.conf dark-theme.conf
       ln -s theme.conf dark-theme.conf

4. Fourth and final step is to create the Kitty Theme Changer
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

    """A container object to hold the Config that this script works with."""
    from pathlib import Path
    theme_dir = Path('~/kitty-themes/themes').expanduser()
    conf_dir = Path('~/.config/kitty').expanduser()
    theme_link = conf_dir.joinpath('theme.conf')
    light_theme_link = conf_dir.joinpath('light-theme.conf')
    dark_theme_link = conf_dir.joinpath('dark-theme.conf')
    socket = 'unix:/tmp/kittysocket'


.. EOF README
