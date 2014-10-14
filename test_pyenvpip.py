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

class TestInstallVenv(Base):
    def setUp(self):
        super(TestInstallVenv, self).setUp()

        self.envpath = 'venv'
        self.apath = join(self.envpath, 'bin', 'activate')
        self.atpath = join(self.envpath, 'bin', 'activate_this.py')

        with patch('setuptools.Command.__init__', Mock(return_value=None)):
            from pyenvpip import InstallVenv
            self.inst = InstallVenv()

    def tearDown(self):
        if os.environ.get('VIRTUAL_ENV',False):
            del os.environ['VIRTUAL_ENV']

    def _mock_create_virtualenv(self, *args, **kwargs):
        ''' mock the shell call to virtualenv '''
        cmd = args[0]
        envdir = cmd[2]
        activate = join(envdir, 'bin', 'activate')
        activate_this = activate + '_this.py'
        os.makedirs( dirname(activate) )
        open(activate,'w').close()
        self._make_activate_this(activate_this)

    def _make_activate_this(self, pth):
        # Make directories up to pth
        d = dirname(pth)
        if not isdir(d):
            os.makedirs(d)
        # Make activate
        with open(pth,'w') as fh:
            fh.write('import os\n')
            fh.write('import sys\n')
            fh.write('import site\n')
            fh.write('os.environ["PATH"] += os.pathsep + "pathset"\n')
            fh.write('sys.path.append("pathset")\n')

    def _run(self, inst ):
        with patch('pyenvpip.subprocess') as subprocess:
            subprocess.check_call = self._mock_create_virtualenv
            self.inst.initialize_options()
            self.inst.finalize_options()
            self.inst.run()

    def test_installs_to_specified_argument(self):
        self.inst.venvpath = self.envpath
        self._run(self.inst)

        ok_( exists(self.atpath), "Did not install virtualenv into myenv" )
    
    def test_installs_to_default(self):
        self._run(self.inst)
        activate_this = self.inst._venv_activate_path('venv')

        ok_( exists(activate_this), "Did not install virtualenv into venv" )

    def test_does_not_reinstall(self):
        self._mock_create_virtualenv(['python','virtualenv', 'venv'])
        for root, files, dirs in os.walk('.'):
            for f in files:
                print join(root,f)
        activate_this = 'venv/bin/activate_this.py'
        stat = os.stat(activate_this)
        self._run(self.inst)

        eq_( stat, os.stat(activate_this), "Reinstalled when it should not have" )

    def test_activate_modifies_environ(self):
        self._mock_create_virtualenv(['python','virtualenv.py','venv'])
        self.inst.activate_virtualenv('venv')

        eq_( 'pathset', os.environ['PATH'].split(os.pathsep)[-1] )
        eq_( 'pathset', sys.path[-1] )

    def test_venv_activate_path_gets_correct_path(self):
        vpath = 'virtualenv'
        apath = join(vpath,'bin','activate')
        r = self.inst._venv_activate_path(vpath)
        eq_( apath, r )

    def test_in_virtual_env_environ_checked(self):
        self.inst.venvpath = self.envpath
        self._make_activate_this(self.apath)

        self.inst._in_virtual_env()
        eq_( False, self.inst._in_virtual_env() )

        os.environ['VIRTUAL_ENV'] = self.envpath
        self.inst._in_virtual_env()
        eq_( True, self.inst._in_virtual_env() )

    def test_in_virtual_env_activate_checked(self):
        self.inst.venvpath = self.envpath
        os.environ['VIRTUAL_ENV'] = self.envpath

        eq_( False, self.inst._in_virtual_env() )

        self._make_activate_this(self.apath)
        eq_( True, self.inst._in_virtual_env() )
