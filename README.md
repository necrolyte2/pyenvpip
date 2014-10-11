# Basic Usage

Allows you to extend your setup.py easily so that you can have it easily install a virtualenv, pip and even any version of Python.

Just add pyenvpip to your setup.py setup_requires list


```
setup(
    ...,
    setup_requires = [
        'pyenvpip',
    ],
)
```

This will add 3 new commands to your setup.py

- install_virtualenv
  - Instructs the setup.py to install a new virtualenv for you and activate it inside of the setup.py
- install_with_pip
  - Uses a requirements.txt file to run pip install -r with
- pyenvpipinstall
  - Essentially runs install_virtualenv, then install_with_pip followed by a regular setup.py install


# Advanced Usage

You may want to just overwrite your setup.py's install method completely and have it do everything by default

setup.py

```
from setuptools.dist import Distribution
dist = Distribution()
setuptools_install = dist.get_command_class('install')
class MyInstall(setuptools_install):
    def run(self):
        klass = dist.get_command_obj('envpipinstall')
        klass.ensure_finalized()
        klass.run()
        klass.mod_klass_prefix_attributes(self)
        setuptools_install.run(self)

setup(
    setup_requires = [
        'pyenvpip',
    ],
    cmdclass = {
        'install': MyInstall,
    }
)
```

This essentially patches the normal install process such that it runs the PyEnvPipInstall class instead.
