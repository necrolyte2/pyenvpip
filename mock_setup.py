# Install setuptools automagically from the interwebz
from ez_setup import use_setuptools
use_setuptools()

from setuptools import setup, find_packages

from setuptools.dist import Distribution
dist = Distribution()
klass = dist.get_command_class('pyenvpipinstall')
class MyInstall(klass):
    def run(self):
        print "Arrr. I was called!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
        klass.run(self)

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
        'bdist_egg': MyInstall,
    }
)
