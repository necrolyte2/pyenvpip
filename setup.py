# Install setuptools automagically from the interwebz
from ez_setup import use_setuptools
use_setuptools()

from setuptools import setup, find_packages

from pyenvpip import __version__

# Run setuptools setup
setup(
    name = "pyenvpip",
    version = __version__,
    packages = find_packages(),
    tests_require = [
        'nose',
        'mock'
    ],
    setup_requires = [
        'virtualenv',
        'pip',
    ],
    install_requires = [
        'virtualenv',
        'pip'
    ],
    author = 'Tyghe Vallard',
    author_email = 'vallardt@gmail.com',
    description = open('README.md').read(),
    py_modules = [
        'pyenvpip'
    ],
    license = 'GPLv2',
    entry_points = {
        'distutils.commands': [
            'install_virtualenv = pyenvpip:InstallVenv',
            'install_with_pip = pyenvpip:InstallWithPip',
            'pyenvpipinstall = pyenvpip:PyEnvPipInstall',
        ]
    },
)
