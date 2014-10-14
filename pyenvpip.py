from glob import glob
import sys
from os.path import exists, join, isdir, basename, isabs, abspath
import os
import subprocess

import setuptools
from setuptools.dist import Distribution
from setuptools.command.develop import develop as _develop
from setuptools.command.bdist_egg import bdist_egg as _bdist_egg

__version__ = "0.0.1"

class develop_pip_only(_develop):
    def run(self):
        _develop.run(self)

class InstallVenv(setuptools.Command):
    description = 'Installs a virtualenv for you'
    user_options = [
        ('venvpath=',None,'Virtual env path to install to'),
    ]

    def initialize_options(self):
        self.venvpath = None

    def finalize_options(self):
        # Set default for venvpath to venv
        if self.venvpath is None:
            self.venvpath = 'venv'
        # Ensure absolute path
        if not isabs(self.venvpath):
            self.venvpath = abspath(self.venvpath)

    def run(self):
        '''
        Runs virtualenv creation as well as activation
        '''
        if self.venvpath is not None \
            and not isdir(self.venvpath):
            self.install_virtualenv(self.venvpath)
        self.activate_virtualenv(self.venvpath)

    def _venv_activate_path(self, venvpath):
        return join(venvpath, 'bin', 'activate')

    def _in_virtual_env(self):
        venvpath = os.environ.get('VIRTUAL_ENV',False)
        if venvpath and exists(self._venv_activate_path(venvpath)):
            return True
        return False

    def mod_klass_prefix_attributes(self, klass):
        '''
        Modify all prefixes so installation goes into this virtualenv
        '''
        prefix = self.venvpath
        # Gets 2.6, 2.7 ...
        v=sys.version_info[:2]
        # python2.6, python2.7 ...
        pyver = 'python{0}.{1}'.format(*v)
        bindir = join(prefix, 'bin')
        sitepkgdir = join(prefix,'lib',pyver,'site-packages')
        site64pkgdir = sitepkgdir.replace('lib','lib64')

        prefix_attrs = (
            'exec_prefix',
            'install_platbase',
            'install_base',
            'install_data',
            'prefix',
            # Config vars
            'platbase',
            'base',
            'sys_prefix',
            'exec_prefix',
            'sys_exec_prefix',
        )
        for p in prefix_attrs:
            setattr(klass, p, prefix)
            klass.config_vars[p] = prefix

        sitepkg_attrs = (
            'install_lib_base',
            'install_purelib',
            'install_lib',
        )
        for p in sitepkg_attrs:
            setattr(klass, p, sitepkgdir)

    def install_virtualenv(self, *virtenvoptions):
        print "Installing virtualenv {0}".format(virtenvoptions[0])
        # Find virtualenv.py in sys.paths which should be a .egg directory
        vpth = ''
        for pth in sys.path:
            if basename(pth).startswith('virtualenv'):
                vpth = join(pth,'virtualenv.py')
        if not vpth:
            raise Exception("Could not find virtualenv.py path")
        subprocess.check_call(
            [sys.executable,vpth] + list(virtenvoptions)
        )

    def activate_virtualenv(self, venvpth):
        # Activate this path
        activatepth = self._venv_activate_path(venvpth) + '_this.py'
        print "Activating using {0}".format(activatepth)
        execfile(activatepth, dict(__file__=activatepth))

class InstallWithPip(setuptools.Command):
    description = 'Installs all requirements from a requirements.txt file'
    user_options = [
        ('requirements=', None, 'Pip Requirements file path'),
    ]

    def initialize_options(self):
        self.requirements = None

    def finalize_options(self):
        # Set default file if not specified
        if self.requirements is None:
            # Only set file if default file exists
            if exists('requirements.txt'):
                self.requirements = 'requirements.txt'

    def run(self):
        if self.requirements is not None:
            self.pip_install(self.requirements)

    def pip_install( self, reqfile ):
        from subprocess import check_call
        print "Installing all requirements from {0}".format(reqfile)
        check_call( ['pip','install','-r',reqfile] )

class EnvPipInstall(InstallVenv, InstallWithPip):
    description = 'Installs virtualenv and utilizes pip instead ' \
                    'of easy_install for dependencies'

    # Hacky McHackerton
    __mro__ = [
        InstallVenv, InstallWithPip
    ]

    user_options = InstallWithPip.user_options + \
            InstallVenv.user_options

    def _lazy_caller(self, objects, method):
        for obj in objects:
            getattr(obj,method)(self)

    def initialize_options(self):
        self._lazy_caller(
            EnvPipInstall.__mro__, 'initialize_options'
        )

    def finalize_options(self):
        self._lazy_caller(
            EnvPipInstall.__mro__, 'finalize_options'
        )

    def run(self):
        self._lazy_caller(
            EnvPipInstall.__mro__, 'run'
        )
