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

from pathlib import Path
from subprocess import call


VERSION = "0.1"
VERBOSE = False
DEBUG = False
DEBUG_OUTPUT_PREFIX = 'debug: '


class Config(object):
    """A container object to hold the Config that this script works with."""
    theme_dir = Path('~/storage/lib/kitty-themes/themes').expanduser()
    conf_dir = Path('~/.config/kitty').expanduser()
    theme_link = conf_dir.joinpath('theme.conf')
    light_theme_link = conf_dir.joinpath('light-theme.conf')
    dark_theme_link = conf_dir.joinpath('dark-theme.conf')
    socket = 'unix:/tmp/kittysocket'


def main():
    """Main script logic."""
    args = parse_cmd_line()

    if args.action:
        dprint('calling action: {}'.format(args.action))
        getattr(Actions, args.action)(args)
    else: # take default action
        dprint('no action provided: calling default action')
        Actions.show(args)

    return 0


def parse_cmd_line():
    """Parse the command line arguments."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        '--version', help='Print the version and exit.', action='version',
        version='%(prog)s {}'.format(VERSION))
    DebugAction.add_parser_argument(parser)
    VerboseAction.add_parser_argument(parser)
    parser.add_argument(
        '-l', '--list', action="store_const", const='list', dest='action',
        default='', help="List available themes.")
    parser.add_argument(
        '-s', '--show', action='store_const', const='show', dest='action',
        default='', help="Show the current configuration.")
    parser.add_argument(
        '--test', action='store_const', const='test', dest='action',
        default='', help="Test a new theme in the current kitty session.")
    parser.add_argument(
        '-t', '--toggle', action='store_const', const='toggle', dest='action',
        default='', help="Toggle between the dark and light themes.")
    parser.add_argument(
        '--setd', action='store_const', const='set_dark', dest='action',
        default='', help='Set the dark-theme.conf as the default.')
    parser.add_argument(
        '--setl', action='store_const', const='set_light', dest='action',
        default='', help='Set the light-theme.conf as the default.')
    parser.add_argument(
        '-L', '--live', action='store_const', const='live', dest='action',
        default='', help='Update existing kitty sessions to use the config.')
    parser.add_argument(
        action='store', dest='theme', metavar='THEME', nargs='?', default='',
        help=("The theme name to use. Use --list to get a list "
              "of available themes."))

    args = parser.parse_args()

    # ensure actions that need a theme input receive one
    action_needs_theme = ['test', 'set_dark', 'set_light']
    if args.action and args.action in action_needs_theme:
        dprint('action {} requires a theme from the user.'.format(args.action))
        if not args.theme:
            msg = 'The "{}" action requires a theme name.'.format(args.action)
            parser.error(msg)
    return args


def list_themes(args):
    """List the available themes."""
    print('Available Kitty Themes:')
    dprint('Looking for themes in: {}'.format(Config.theme_dir))
    for theme in sorted(Config.theme_dir.glob('*conf'),
                        key=lambda s: s.stem.lower()):
        print('  {}'.format(theme.stem))


def show_config(args):
    """Show the current theme configuration."""
    dprint('looking at symlink target of {}'.format(Config.theme_link))
    theme = Config.theme_link.resolve().stem
    print('current configured theme is: {}'.format(theme))


def get_theme_file(theme_name):
    """From a theme name, get the filename of an existing file.

    Return None if the file does not exist.
    """
    theme_file = Config.theme_dir.joinpath('{}.conf'.format(theme_name))
    dprint('theme_file: {}'.format(theme_file))
    if not theme_file.exists():
        print('Provided theme does not exist. Use the '
              '--list option to see available themes.')
        sys.exit(1)
    return theme_file


def test_theme(args):
    """Test the given theme in the current kitty session."""
    theme_file = get_theme_file(args.theme)
    vprint('Changing theme of current kitty window to: {}'.format(
        theme_file.name))
    cmd = ['kitty', '@', '--to={}'.format(Config.socket), 'set-colors',
           theme_file]
    dprint('executing: {}'.format(' '.join(cmd)))
    call(cmd)


def toggle_themes(args):
    """Toggle the themes between light and dark."""
    vprint('Toggling configured theme between light and dark.')
    if Config.light_theme_link.resolve() == Config.theme_link.resolve():
        # light theme: reconfig to dark theme
        dprint('light theme configured. enabling dark theme.')
        Config.theme_link.unlink()
        Config.theme_link.symlink_to(Config.dark_theme_link)
    elif Config.dark_theme_link.resolve() == Config.theme_link.resolve():
        # dark theme: reconfig to light theme
        dprint('dark theme configured. enabling light theme.')
        Config.theme_link.unlink()
        Config.theme_link.symlink_to(Config.light_theme_link)
    else:
        print('Configured theme.conf does not match configured '
              'light-theme.conf or dark-theme.conf. Setting theme to dark.')
        args.theme = Config.dark_theme_link.resolve().stem
        set_dark_theme(args)


def set_dark_theme(args):
    """Set the default theme to the configured dark theme."""
    theme_file = get_theme_file(args.theme)
    dprint('existing dark theme is: {}'.format(
        Config.dark_theme_link.resolve()))
    vprint('Changing configured dark theme to {}'.format(theme_file.name))
    Config.dark_theme_link.unlink()
    Config.dark_theme_link.symlink_to(theme_file)


def set_light_theme(args):
    """Set the default theme to the configured light theme."""
    theme_file = get_theme_file(args.theme)
    dprint('existing light theme is: {}'.format(
        Config.light_theme_link.resolve()))
    vprint('Changing configured light theme to {}'.format(theme_file.name))
    Config.dark_theme_link.unlink()
    Config.dark_theme_link.symlink_to(theme_file)


def make_theme_live(args):
    """Update all existing kitty sessions to use the configured theme."""
    vprint('Changing theme of all running kitty windows to: {}'.format(
        Config.theme_link.resolve().name))
    cmd = ['kitty', '@', '--to={}'.format(Config.socket), 'set-colors',
           '--all', Config.theme_link]
    dprint('executing: {}'.format(' '.join(cmd)))
    call(cmd)


class Actions(object):
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
        parser.add_argument(cls.sflag, cls.flag, help=cls.help, action=cls)

    def __init__(self, option_strings, dest, **kwargs):
        super(DebugAction, self).__init__(option_strings, dest, nargs=0,
                                          default=False, **kwargs)

    def __call__(self, parser, namespace, values, option_string=None):
        global DEBUG
        DEBUG = True
        setattr(namespace, self.dest, True)


class VerboseAction(DebugAction):
    """Enable the verbose output mechanism."""

    sflag = '-v'
    flag = '--verbose'
    help = 'Enable verbose output.'

    def __call__(self, parser, namespace, values, option_string=None):
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
