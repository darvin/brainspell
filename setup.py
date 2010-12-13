#!/usr/bin/env python
"""
"""
import glob
from setuptools import find_packages
from distutils.core import setup
from distutils.core import Command
from distutils.command.build import build
import sys
import os

mainscript = 'src/qbrainspell.pyw'

def needsupdate(src, targ):
    return not os.path.exists(targ) or os.path.getmtime(src) > os.path.getmtime(targ)


class BSBuildUi(Command):
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


class BSBuild(build):
    def is_win_platform(self):
        return hasattr(self, "plat_name") and (self.plat_name[:3] == 'win')

    sub_commands = [('build_ui', None)] + build.sub_commands
    #+ [('build_winext', is_win_platform)]


cmds = {
        'build' : BSBuild,
        'build_ui' : BSBuildUi,
        }


base_options = dict (name=u'brainspell',
      version="0.1",
      description='BrainSpell is brainfuck game',
      author='Sergey Klimov',
      author_email='dcdarv@gmail.com',
      scripts=[mainscript],
      url='http://github.com/darvin/brainspell',
      packages = ['brainspell', 'brainspell.gui'],
      package_dir = {'brainspell': 'src'},

      data_files=[('doc',glob.glob("doc/*.html")),
                  ('doc/images',glob.glob('doc/images/*.png')),
  ],
      long_description="""BrainSpell game""",
      license="GPL",
      maintainer="Sergey Klimov",
      maintainer_email="dcdarv@gmail.com",
      classifiers=[
          'Development Status :: 4 - Beta',
          'Environment :: X11 Applications :: Qt',
          'License :: OSI Approved :: GNU General Public License (GPL)',
          'Operating System :: OS Independent',
          'Programming Language :: Python',
          'Topic :: Games/Entertainment',
          ],
      cmdclass = cmds,
     )




extra_options = {}
base_options.update(extra_options)
options = base_options



setup( **options)
