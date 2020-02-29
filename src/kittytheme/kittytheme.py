#!/usr/bin/env python3
"""Helper for setting and switching Kitty Terminal Themes."""

# Copyright 2020 Curtis Sand
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import argparse
import sys
import random

from importlib.util import spec_from_file_location
from importlib.util import module_from_spec
from pathlib import Path
from subprocess import call


VERSION = "0.5"
VERBOSE = False
DEBUG = False
DEBUG_OUTPUT_PREFIX = 'debug: '

DEFAULT_CONFIG = '~/.kittythemechanger.py'


def main():
    """Main script logic."""
    # parse the command line arguments
    parser = build_argument_parser()
    args = parser.parse_args()
    dprint(f'parsed args: {args}')

    if args.test and args.live:
        parser.error('The options "--live" and "--test" cannot be '
                     'used together.')

    # if --help-config is used, print config help then exit
    if args.config_help:
        print_config_help()
        sys.exit(0)

    # load config module
    spec = spec_from_file_location(args.config.stem, args.config.as_posix())
    config = module_from_spec(spec)
    spec.loader.exec_module(config)
    check_config(config)

    check_symlinks(config)

    # dispatch selected actions
    do_default = True
    if args.list:
        do_default = False
        dprint('calling action: list')
        Actions.list(args, config)

    if args.set_dark:
        do_default = False
        dprint('calling action: set_dark')
        Actions.set_dark(args, config)
    if args.set_light:
        do_default = False
        dprint('calling action: set_light')
        Actions.set_light(args, config)

    if args.show:
        do_default = False
        dprint('calling action: show')
        Actions.show(args, config)

    if args.test:
        do_default = False
        dprint('calling action: test')
        Actions.test(args, config)

    if args.toggle:
        do_default = False
        dprint('calling action: toggle')
        Actions.toggle(args, config)

    if args.live:
        do_default = False
        dprint('calling action: live')
        Actions.live(args, config)

    if do_default:  # take default action
        dprint('no action provided: calling default action')
        Actions.show(args, config)

    return 0


def build_argument_parser():
    """Parse the command line arguments."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        '--version', help='Print the version and exit.', action='version',
        version='%(prog)s {}'.format(VERSION))
    DebugAction.add_parser_argument(parser)
    VerboseAction.add_parser_argument(parser)
    parser.add_argument(
        '-c', '--config', type=existing_file, default=DEFAULT_CONFIG,
        help=('The configuration for the Kitty Theme Changer. See '
              '"--help-config" for more info. Default: {}'.format(
                DEFAULT_CONFIG)))
    parser.add_argument(
        '-l', '--list', dest='list', action="store_true",
        default=False, help="List available themes.")
    parser.add_argument(
        '-s', '--show', dest='show', action="store_true",
        default=False, help="Show the current configuration.")
    parser.add_argument(
        '-T', '--test', dest='test', metavar="TEST_THEME",
        default='', help="Test a new theme in the current kitty session.")
    parser.add_argument(
        '-t', '--toggle', dest='toggle', action="store_true",
        default=False, help="Toggle between the dark and light themes.")
    parser.add_argument(
        '--setd', dest='set_dark', metavar='DARK_THEME',
        default='', help='Set the dark theme.')
    parser.add_argument(
        '--setl', dest='set_light', metavar='LIGHT_THEME',
        default='', help='Set the light theme.')
    parser.add_argument(
        '-L', '--live', dest='live', action='store_true', default=False,
        help='Update existing kitty sessions to use the config.')
    parser.add_argument(
        '--help-config', action='store_true', dest='config_help',
        default=False,
        help="Print info on how to configure Kitty Theme Changer.")

    return parser


def existing_file(input_text):
    """Ensure the input text is an existing file path."""
    dprint('input config file: {}'.format(input_text))
    filepath = Path(input_text).expanduser()
    if not filepath.exists():
        raise argparse.ArgumentTypeError(
            'The configuration file must exist. Use --help-config to see '
            'how to configure the Kitty Theme Changer.')
    return filepath


def check_config(config):
    """Check that the config module has the required attributes."""
    required_config_attributes = [
        ('theme_dir', Path),
        ('conf_dir', Path),
        ('theme_link', Path),
        ('light_theme_link', Path),
        ('dark_theme_link', Path),
        ('socket', str)
    ]
    dprint('checking config: {}'.format(dir(config)))
    dprint(config.__file__)
    for attribute, type in required_config_attributes:
        check_status = True
        try:
            check_status = isinstance(getattr(config, attribute), type)
        except AttributeError:
            check_status = False
        if not check_status:
            raise Exception(
                'The config module is missing a variable named '
                '{} of type {}'.format(attribute, type))


def get_random_theme_config(theme_dir):
    """Randomly choose a theme file from the theme dir."""
    try:
        ret_val = random.choice([i for i in theme_dir.glob('*conf')])
    except IndexError:
        print('Error: cannot find any theme files ending in "conf" in the '
              f'directory "{theme_dir}". Please follow the instructions '
              'given with "--help-config" to ensure the theme changer is '
              'configured correctly.')
        sys.exit(1)
    return ret_val


def check_symlinks(config):
    """Check that the three theme symlinks exist or create them."""
    dprint('Checking that the theme symlinks exist.')
    if not config.dark_theme_link.exists():
        dprint('dark theme link does not exist, creating it.')
        config.dark_theme_link.symlink_to(
            get_random_theme_config(config.theme_dir))
    if not config.light_theme_link.exists():
        dprint('light theme link does not exist, creating it.')
        config.light_theme_link.symlink_to(
            get_random_theme_config(config.theme_dir))
    if not config.theme_link.exists():
        dprint('main theme link does not exist, creating it.')
        config.theme_link.symlink_to(config.dark_theme_link)


def list_themes(args, config):
    """List the available themes."""
    print('Available Kitty Themes:')
    dprint('Looking for themes in: {}'.format(config.theme_dir))
    for theme in sorted(config.theme_dir.glob('*conf'),
                        key=lambda s: s.stem.lower()):
        print('  {}'.format(theme.stem))


def show_config(args, config):
    """Show the current theme configuration."""
    dprint('looking at symlink target of {}'.format(config.theme_link))
    theme = config.theme_link.resolve().stem
    light_theme = config.light_theme_link.resolve().stem
    dark_theme = config.dark_theme_link.resolve().stem
    dark_active = '***' if dark_theme == theme else ''
    light_active = '***' if light_theme == theme else ''
    print('{}dark theme: {}{}'.format(
        dark_active, dark_theme, dark_active))
    print('{}light theme: {}{}'.format(
        light_active, light_theme, light_active))


def get_theme_file(theme_name, config):
    """From a theme name, get the filename of an existing file.

    Return None if the file does not exist.
    """
    theme_file = None
    for fname in config.theme_dir.glob('*.conf'):
        # Allow case insensitive theme name inputs
        if fname.stem.lower() == theme_name.lower():
            theme_file = fname

    if not theme_file or not theme_file.exists():
        print(f'Provided theme, "{theme_name}" does not exist. Use the '
              '--list option to see available themes.')
        sys.exit(1)
    dprint('theme_file: {}'.format(theme_file))
    return theme_file


def test_theme(args, config):
    """Test the given theme in the current kitty session."""
    theme_file = get_theme_file(args.test, config)
    vprint('Changing theme of current kitty window to: {}'.format(
        theme_file.name))
    cmd = ['kitty', '@', '--to={}'.format(config.socket), 'set-colors',
           theme_file.as_posix()]
    dprint('executing: {}'.format(' '.join(cmd)))
    call(cmd)


def toggle_themes(args, config):
    """Toggle the themes between light and dark."""
    vprint('Toggling configured theme between light and dark.')
    if config.light_theme_link.resolve() == config.theme_link.resolve():
        # light theme: reconfig to dark theme
        dprint('light theme configured. enabling dark theme.')
        config.theme_link.unlink()
        config.theme_link.symlink_to(config.dark_theme_link)
    elif config.dark_theme_link.resolve() == config.theme_link.resolve():
        # dark theme: reconfig to light theme
        dprint('dark theme configured. enabling light theme.')
        config.theme_link.unlink()
        config.theme_link.symlink_to(config.light_theme_link)
    else:
        print('Configured theme.conf does not match configured '
              'light-theme.conf or dark-theme.conf. Setting theme to dark.')
        config.theme_link.unlink()
        config.theme_link.symlink_to(config.dark_theme_link)


def set_dark_theme(args, config):
    """Set the default theme to the configured dark theme."""
    theme_file = get_theme_file(args.set_dark, config)
    dprint('existing dark theme is: {}'.format(
        config.dark_theme_link.resolve()))
    vprint('Changing configured dark theme to {}'.format(theme_file.name))
    config.dark_theme_link.unlink()
    config.dark_theme_link.symlink_to(theme_file)


def set_light_theme(args, config):
    """Set the default theme to the configured light theme."""
    theme_file = get_theme_file(args.set_light, config)
    dprint('existing light theme is: {}'.format(
        config.light_theme_link.resolve()))
    vprint('Changing configured light theme to {}'.format(theme_file.name))
    config.light_theme_link.unlink()
    config.light_theme_link.symlink_to(theme_file)


def make_theme_live(args, config):
    """Update all existing kitty sessions to use the configured theme."""
    vprint('Changing theme of all running kitty windows to: {}'.format(
        config.theme_link.resolve().name))
    cmd = ['kitty', '@', '--to={}'.format(config.socket), 'set-colors',
           '--all', config.theme_link.as_posix()]
    dprint('executing: {}'.format(' '.join(cmd)))
    call(cmd)


def print_config_help():
    """Print a help message about configuring Kitty Theme Changer."""
    msg = "Configuring Kitty Theme Changer\n\n"
    msg += "1. First step in configuring the Kitty Theme Changer is to download a set of\n"
    msg += "   themes for kitty (recommendation: https://github.com/dexpota/kitty-themes).\n\n"
    msg += "2. Second step is to configure kitty to include a theme config\n"
    msg += "   file. To do this add the line ``include ./theme.conf`` in your\n"
    msg += "   kitty.conf file.\n\n"
    msg += "3. Third and final step is to create the Kitty Theme Changer\n"
    msg += "   config file which will point to the correct paths for the\n"
    msg += "   themes you've collected.\n\n"
    msg += "   The Kitty theme changer uses a simple python module as\n"
    msg += "   a configuration file. By default this is '~/.kittythemechanger.py'.\n"
    msg += "   The list of required variables and their types are:\n\n"
    msg += "   - theme_dir (pathlib.Path): Directory of Kitty theme.conf files.\n"
    msg += "   - conf_dir (pathlib.Path): Directory Kitty looks in for theme.conf\n"
    msg += "   - theme_link (pathlib.Path): Symlink file Kitty loads from kitty.conf\n"
    msg += "   - light_theme_link (pathlib.Path): Symlink to a 'light' theme config file.\n"
    msg += "   - dark_theme_link (pathlib.Path): Symlink to a 'dark' theme config file.\n"
    msg += "   - socket (str): a Kitty compatible socket string for the '--listen-on' flag. See 'man kitty'.\n\n"
    msg += "   An example .kittythemechanger.py file is shown below::\n\n"
    msg += "       '''A config module for the Kitty Theme Changer Tool.'''\n"
    msg += "       from pathlib import Path\n"
    msg += "       theme_dir = Path('~/kitty-themes/themes').expanduser()\n"
    msg += "       conf_dir = Path('~/.config/kitty').expanduser()\n"
    msg += "       theme_link = conf_dir.joinpath('theme.conf')\n"
    msg += "       light_theme_link = conf_dir.joinpath('light-theme.conf')\n"
    msg += "       dark_theme_link = conf_dir.joinpath('dark-theme.conf')\n"
    msg += "       socket = 'unix:/tmp/kittysocket'\n"
    print(msg)


class Actions:
    """A container object to hold the actions this script can perform."""

    list = list_themes
    show = show_config
    test = test_theme
    toggle = toggle_themes
    set_dark = set_dark_theme
    set_light = set_light_theme
    live = make_theme_live


def dprint(msg):
    """Conditionally print a debug message."""
    if DEBUG:
        print('{}{}'.format(DEBUG_OUTPUT_PREFIX, msg))


def vprint(msg):
    """Conditionally print a verbose message."""
    if VERBOSE:
        print(msg)


class DebugAction(argparse.Action):
    """Enable the debugging output mechanism."""

    sflag = '-d'
    flag = '--debug'
    help = 'Enable debugging output.'

    @classmethod
    def add_parser_argument(cls, parser):
        """Add arguments for this action to an argparse parser object."""
        parser.add_argument(cls.sflag, cls.flag, help=cls.help, action=cls)

    def __init__(self, option_strings, dest, **kwargs):
        """Initialize this Action object."""
        super(DebugAction, self).__init__(option_strings, dest, nargs=0,
                                          default=False, **kwargs)

    def __call__(self, parser, namespace, values, option_string=None):
        """Set DEBUG to True for this execution."""
        global DEBUG
        DEBUG = True
        setattr(namespace, self.dest, True)


class VerboseAction(DebugAction):
    """Enable the verbose output mechanism."""

    sflag = '-v'
    flag = '--verbose'
    help = 'Enable verbose output.'

    def __call__(self, parser, namespace, values, option_string=None):
        """Set VERBOSE to True for this execution."""
        global VERBOSE
        VERBOSE = True
        setattr(namespace, self.dest, True)


if __name__ == '__main__':
    try:
        sys.exit(main())
    except SystemExit:
        sys.exit(0)
    except KeyboardInterrupt:
        print('...interrupted by user, exiting.')
        sys.exit(1)
    except Exception as exc:
        if DEBUG:
            raise
        else:
            print('Unhandled Error:\n{}'.format(exc))
            sys.exit(1)
