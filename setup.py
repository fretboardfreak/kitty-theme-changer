"""The setuptools deployment script."""
# Copyright 2019 Curtis Sand
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
import os
import subprocess
import distutils.log
import unittest
from distutils.cmd import Command
from setuptools import setup
from setuptools import find_packages
from setuptools.command.test import test
from pathlib import Path


def install_requires():
    """Read the requirements for installing the project."""
    path = Path('requirements.txt')
    if not path.exists():
        return ""
    with open(path, 'r') as reqf:
        return reqf.read().splitlines()


def tests_require():
    """Read the requirements for testing the project."""
    path = Path('dev_requirements.txt')
    if not path.exists():
        return ""
    with open(path, 'r') as dev_req:
        return dev_req.read().splitlines()


def readme():
    """Read the readme file for the long description."""
    with open('README.rst', 'r') as readmef:
        return readmef.read()


class SetupCommand(Command):
    """Base command for distutils in the project."""

    def initialize_options(self):
        """Set defaults for options."""
        pass

    def finalize_options(self):
        """Post-process options."""
        pass

    def run(self):
        """Run the custom setup command."""
        pass

    def _run_command(self, command):
        """Execute the command."""
        self.announce('running command: %s' % str(command),
                      level=distutils.log.INFO)
        try:
            subprocess.check_call(command)
        except subprocess.CalledProcessError as exc:
            self.announce('Non-zero returncode "%s": %s' %
                          (exc.returncode, exc.cmd),
                          level=distutils.log.INFO)
            return 1

    @property
    def setup_path(self):
        """Get the path to the setup.py script."""
        return os.path.dirname(__file__)

    @property
    def software_package(self):
        """Get the path to the software parkace."""
        return os.path.join(self.setup_path, 'src/kittytheme')

    @property
    def test_paths(self):
        """Get the list of paths for python files that should be tested."""
        return [self.software_package, __file__]


class DevelopmentCommand(SetupCommand):
    """Base command for project development and testing."""

    pass


class PylintCommand(DevelopmentCommand):
    """A custom command to run Pylint on all Python source files."""

    description = "Run pylint on the python sources."
    user_options = [
        ('pylint-rcfile=', None, 'path to Pylint config file.')
    ]

    def __init__(self, *args, **kwargs):
        """Initialize the class."""
        super().__init__(*args, **kwargs)
        self.pylint_rcfile = ""

    def initialize_options(self):
        """Set defaults for options."""
        self.pylint_rcfile = ''

    def finalize_options(self):
        """Post-process options."""
        if self.pylint_rcfile:
            assert os.path.exists(self.pylint_rcfile), (
                'Cannot find config file "%s"' % self.pylint_rcfile)

    def run(self):
        """Prepare and run the Pylint command."""
        super().run()
        command = ['pylint']
        rcfile = self.pylint_rcfile
        if not rcfile and os.path.exists('pylintrc'):
            rcfile = 'pylintrc'
        if rcfile:
            command.append('--rcfile=%s' % rcfile)
        command.extend([test_path for test_path in self.test_paths
                        if test_path != __file__])
        self._run_command(command)


class PycodestyleCommand(DevelopmentCommand):
    """A custom command to run pycodestyle on all python source files."""

    description = "Run pycodestyle on all python sources."
    user_options = []

    def run(self):
        """Run the pycodestyle tool."""
        super().run()
        self._run_command(['pycodestyle', '--statistics', '--verbose'] +
                          self.test_paths)


class Pep257Command(DevelopmentCommand):
    """A custom command to run pep257 on all Python source files."""

    description = "Run pep257 on all python sources."
    user_options = []

    def run(self):
        """Run the pep257 checker."""
        super().run()
        self._run_command(['pep257', '--count', '--verbose'] +
                          self.test_paths)


class UnitTestCommand(DevelopmentCommand):
    """A custom command for running unit tests."""

    description = "Run the unittests."
    user_options = []

    def run(self):
        """Run the unittests."""
        super().run()
        # load test suite
        test_loader = unittest.defaultTestLoader
        setup_dir, _ = os.path.split(__file__)
        test_suite = test_loader.discover(os.path.join(setup_dir, 'src/tests'))

        # run the tests
        test_runner = unittest.TextTestRunner(verbosity=3)
        test_runner.run(test_suite)


class DevInstallCommand(SetupCommand):
    """A custom command to install the development requirements."""

    description = "Install the development requirements."
    user_options = []

    def run(self):
        """Install the development requirements."""
        if self.distribution.install_requires:
            self.distribution.fetch_build_eggs(
                self.distribution.install_requires)
        if self.distribution.tests_require:
            self.distribution.fetch_build_eggs(
                self.distribution.tests_require)


class Test(test):
    """Combine unittest, pycodestyle and pylint checks all into one command."""

    description = "Run pycodestyle, pylint and unittest commands together."
    user_options = [('interactive', 'i', 'Enable interactive pauses.')]

    def __init__(self, *args, **kwargs):
        """Add instance variables for the Test subclass."""
        self.interactive = None
        super().__init__(*args, **kwargs)

    def _interactive_pause(self):
        """Pause for the use to press enter. So interactive."""
        if self.interactive:
            input('enter to continue...')

    def run(self):
        """Run all tests and checkers for project."""
        # Skip parent method to avoid reinstalling packages
        # super().run()
        self.run_command('pycodestyle')
        self._interactive_pause()
        self.run_command('pep257')
        self._interactive_pause()
        self.run_command('pylint')
        self._interactive_pause()
        # disabled until there are unit tests to execute
        # self.run_command('unittest')
        # self._interactive_pause()


setup(
    name='kitty-theme-changer',
    version='0.6',
    description='A CLI tool changing the Kitty Terminal Theme configuration.',
    long_description=readme(),
    url='https://github.com/fretboardfreak/kitty-theme-changer.git',
    author='Curtis Sand',
    author_email='curtissand@gmail.com',
    license='Apache',
    package_dir={'': 'src'},
    packages=find_packages('src'),
    entry_points={
        'console_scripts': ['kitty-theme=kittytheme.kittytheme:main']
    },
    use_2to3=False,
    install_requires=install_requires(),
    zip_safe=True,
    include_package_data=True,
    test_suite='kittytheme.tests',
    tests_require=tests_require(),
    keywords='kitty terminal themes config',
    classifiers=[
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: Apache Software License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3 :: Only',
        'Topic :: Terminals :: Terminal Emulators/X Terminals',
    ],
    cmdclass={
        'pylint': PylintCommand,
        'pycodestyle': PycodestyleCommand,
        'unittest': UnitTestCommand,
        'pep257': Pep257Command,
        'test': Test,
        'dev': DevInstallCommand})
