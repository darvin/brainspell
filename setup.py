#!/usr/bin/env python
"""
py2app/py2exe build script for MyApplication.

Will automatically ensure that all build prerequisites are available
via ez_setup

Usage (Mac OS X):
    python setup.py py2app

Usage (Windows):
    python setup.py py2exe

Usage (Ubuntu/Debian):
    python setup.py --command-packages=stdeb.command bdist_deb

Usage (RPM-based linux distros):
    python setup.py bdist_rpm
"""
import glob
from distutils.core import setup
from distutils.core import Command
from distutils.command.build import build
import sys
import os

mainscript = 'src/cryotec_client.pyw'

def needsupdate(src, targ):
    return not os.path.exists(targ) or os.path.getmtime(src) > os.path.getmtime(targ)


class CryotecClientBuildUi(Command):
    description = "build Python modules from qrc files"

    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def compile_qrc(self, qrc_file, py_file):
        if not needsupdate(qrc_file, py_file):
            return
        print("compiling %s -> %s" % (qrc_file, py_file))
        try:
            import subprocess
            rccprocess = subprocess.Popen(['pyrcc4', qrc_file, '-o', py_file])
            rccprocess.wait()
        except Exception, e:
            raise distutils.errors.DistutilsExecError, 'Unable to compile resouce file %s' % str(e)
            return
    def run(self):
        self.compile_qrc( 'resources/images/images.qrc', 'src/images_rc.py' )
#        self.compile_qrc( 'resources/translations/translations.qrc', 'src/translation_rc.py' )


class CryotecClientBuild(build):
    def is_win_platform(self):
        return hasattr(self, "plat_name") and (self.plat_name[:3] == 'win')

    sub_commands = [('build_ui', None)] + build.sub_commands
    #+ [('build_winext', is_win_platform)]


cmds = {
        'build' : CryotecClientBuild,
        'build_ui' : CryotecClientBuildUi,
        }


base_options = dict (name=u'cryotec_client',
      install_requires = ["pyqt",],
      version="1.0",
      description='Cryotec Client',
      author='Sergey Klimov',
      author_email='dcdarv@gmail.com',
      url='http://github.com/darvin/cryotec_client',
      package_dir = {'cryotec_client': 'src'},
      packages=['cryotec_client'],

      data_files=[('doc',glob.glob("doc/*.html")),
                  ('doc/images',glob.glob('doc/images/*.png')),
  ],
      long_description="""Cryotec Client""",
      license="Greedy Open Source",
      maintainer="Sergey Klimov",
      maintainer_email="dcdarv@gmail.com",
      classifiers=[
          'Development Status :: 4 - Beta',
          'Intended Audience :: End Users/Desktop',
          'License :: OSI Approved :: Python Software Foundation License',
          'Operating System :: MacOS :: MacOS X',
          'Operating System :: Microsoft :: Windows',
          'Operating System :: POSIX',
          'Programming Language :: Python',
          ],
      cmdclass = cmds,
      
     )



if sys.platform == 'darwin':
    extra_options = dict(
        setup_requires=['py2app'],
        app=[mainscript],
        # Cross-platform applications generally expect sys.argv to
        # be used for opening files.
        options=dict(py2app=dict(argv_emulation=True)),

    )
elif sys.platform == 'win32':

    import sys

    sys.path.append(r'c:/Program Files/Microsoft Visual Studio 9.0/VC/redist/x86/Microsoft.VC90.CRT')
    sys.path.append(r'c:\Python27\vcruntime')
    sys.path.append(r'c:\Python26\vcruntime')
    
    import py2exe
    # Override the function in py2exe to determine if a dll should be included
    dllList = ('mfc90.dll','msvcp90.dll','qtnetwork.pyd','qtxmlpatterns4.dll','qtsvg4.dll')
    origIsSystemDLL = py2exe.build_exe.isSystemDLL
    def isSystemDLL(pathname):
        if os.path.basename(pathname).lower() in dllList:
            return 0
        return origIsSystemDLL(pathname)
    py2exe.build_exe.isSystemDLL = isSystemDLL
    extra_options = dict(
        setup_requires=['py2exe'],
        windows=[{
            "script":mainscript,
            "icon_resources": [(0, "resources/images/ico/cryotec_logo.ico")],
            }],
        options = {
            py2exe : {
                "includes" : ["sip", "PyQt4._qt", "cryotec_server", "qtdjango"]
                }
            },
        
        data_files = [('resources',glob.glob('data/*.png')),
                      ('resources',glob.glob('data/*.ico')),
                      ("Microsoft.VC90.CRT", glob.glob(r'c:\Python27\vcruntime\*.*'))],

    )
else:
     extra_options = dict(
         # Normally unix-like platforms will use "setup.py install"
         # and install the main script as such
         scripts=[mainscript],
      )


base_options.update(extra_options)
options = base_options 



setup( **options)
