# Install setuptools automagically from the interwebz
from ez_setup import use_setuptools
use_setuptools()

from setuptools import setup, find_packages

from setuptools.dist import Distribution
dist = Distribution()
setuptools_install = dist.get_command_class('install')

import sys

class MyInstall(setuptools_install):
    def run(self):
        klass = dist.get_command_obj('envpipinstall')
        klass.ensure_finalized()
        klass.run()
        klass.mod_klass_prefix_attributes(self)
        setuptools_install.run(self)

# Run setuptools setup
setup(
    name = "mocky",
    packages = find_packages(),
    setup_requires = [
        'pyenvpip',
    ],
    author = 'Tyghe Vallard',
    author_email = 'vallardt@gmail.com',
    license = 'GPLv3',
    cmdclass = {
        'install': MyInstall,
    }
)
