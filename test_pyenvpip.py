import os
import sys
from os.path import *
import shutil
import subprocess
import tempfile

from nose.tools import eq_, ok_, raises
from nose.plugins.attrib import attr
from mock import Mock, patch

class BaseTestDir(object):
    def setUp(self):
        self.cwd = os.getcwd()
        self.tdir = tempfile.mkdtemp()
        os.chdir(self.tdir)

    def tearDown(self):
        os.chdir(self.cwd)
        shutil.rmtree(self.tdir)

class Base(BaseTestDir):
    def setUp(self):
        super(Base, self).setUp()

class MockCommand(object):
    pass

@patch('pyenvpip.subprocess')
@patch('setuptools.Command', MockCommand)
class TestInstallVenv(Base):
    def _mock_create_virtualenv(self, *args, **kwargs):
        ''' mock the shell call to virtualenv '''
        cmd = args[0]
        envdir = cmd[1]
        activate = join(envdir, 'bin', 'activate')
        activate_this = activate + '_this.py'
        os.makedirs( dirname(activate) )
        open(activate,'w').close()
        self._make_activate_this(activate_this)

    def _make_activate_this(self, pth):
        with open(pth,'w') as fh:
            fh.write('import os\n')
            fh.write('import sys\n')
            fh.write('import site\n')
            fh.write('os.environ[\'PATH\'] = \'pathset\'\n')
            fh.write('sys.path = \'pathset\'\n')

    def test_installs_to_specified_argument(self, subprocess):
        subprocess.check_call = self._mock_create_virtualenv
        from pyenvpip import InstallVenv
        c = InstallVenv()
        c.initialize_options()
        c.venvpath = 'myenv'
        c.finalize_options()
        c.run()
        activate_this = c._venv_activate_path('myenv')
        ok_( exists(activate_this), "Did not install virtualenv into myenv" )
    
    def test_installs_to_default(self, subprocess):
        subprocess.check_call = self._mock_create_virtualenv
        from pyenvpip import InstallVenv
        c = InstallVenv()
        c.initialize_options()
        c.finalize_options()
        c.run()
        activate_this = c._venv_activate_path('venv')
        ok_( exists(activate_this), "Did not install virtualenv into venv" )

    def test_does_not_reinstall(self, subprocess):
        subprocess.check_call = self._mock_create_virtualenv
        from pyenvpip import InstallVenv

        self._mock_create_virtualenv( ['virtualenv', 'venv'] )
        for root, files, dirs in os.walk('.'):
            for f in files:
                print join(root,f)
        activate_this = 'venv/bin/activate_this.py'
        stat = os.stat(activate_this)

        c = InstallVenv()

        c.initialize_options()
        c.finalize_options()
        c.run()

        eq_( stat, os.stat(activate_this), "Reinstalled when it should not have" )

    def test_activate_modifies_environ(self, subprocess):
        from pyenvpip import InstallVenv
        self._mock_create_virtualenv( ['virtualenv', 'venv'] )
        
        c = InstallVenv()
        c.activate_virtualenv('venv')

        eq_( 'pathset', os.environ['PATH'] )
        eq_( 'pathset', sys.path )
