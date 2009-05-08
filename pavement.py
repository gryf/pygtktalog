"""
    Project: pyGTKtalog
    Description: Makefile and setup.py replacement. Used package: paver
    Type: management
    Author: Roman 'gryf' Dobosz, gryf73@gmail.com
    Created: 2009-05-07
"""
import os
import sys
import shutil

from paver.easy import sh, dry, call_task
from paver.tasks import task, needs, help
from paver.setuputils import setup
#import setuptools.command.sdist
from paver.misctasks import generate_setup, minilib
try:
    from pylint import lint
    have_lint = True
except:
    have_lint = False


# distutil/setuptool setup method.
setup(
      name='pyGTKtalog',
      version='1.99',

      long_description='pyGTKtalog is application similar to WhereIsIT, '
                       'for collecting information on files from CD/DVD '
                       'or directories.',
      description='pyGTKtalog is a file indexing tool written in pyGTK',
      author='Roman Dobosz',
      author_email='gryf73@gmail.com',
      url='http://google.com',
      platforms=['Linux', 'BSD'],
      license='GNU General Public License (GPL)',
      classifiers=['Development Status :: 2 - Pre-Alpha',
                   'Environment :: X11 Applications :: GTK',
                   'Intended Audience :: End Users/Desktop',
                   'License :: OSI Approved :: GNU General Public License '
                   '(GPL)',
                   'Natural Language :: English',
                   'Natural Language :: Polish',
                   'Operating System :: POSIX :: Linux',
                   'Programming Language :: Python',
                   'Topic :: Desktop Environment',
                   'Topic :: Utilities'],

      include_package_data=True,
      exclude_package_data={'': ['*.patch']},
      packages=["pygtktalog"],
      scripts=['bin/gtktalog.py'],
      test_suite = 'nose.collector'
)


@task
@needs(['genpl', 'minilib', 'generate_setup'])
def sdist():
    """sdist with message catalogs"""
    call_task("setuptools.command.sdist")

@task
@needs(['genpl'])
def build():
    """build with message catalogs"""
    call_task("setuptools.command.build")


@task
def clean():
    """remove 'pyo', 'pyc' and '~' files"""
    # clean *.pyc, *.pyo and jEdit backup files *~
    for root, dummy, files in os.walk("."):
        for fname in files:
            if fname.endswith(".pyc") or fname.endswith(".pyo") or \
               fname.endswith("~"):
                fdel = os.path.join(root, fname)
                os.unlink(fdel)
                print "deleted", fdel

@task
@needs(["clean"])
def distclean():
    """make clean, and remove any dist/build/egg stuff from project"""
    for dirname in [os.path.join('pygtktalog', 'locale'), 'build', 'dist',
                    'pyGTKtalog.egg-info']:
        if os.path.exists(dirname):
            shutil.rmtree(dirname, ignore_errors=True)
            print "removed directory", dirname

    for filename in ['paver-minilib.zip', 'setup.py']:
        if os.path.exists(filename):
            os.unlink(filename)
            print "deleted", filename

@task
def run():
    """run application"""
    sh("PYTHONPATH=%s:$PYTHONPATH bin/gtktalog.py" % _setup_env())

@task
@needs(['genpl'])
def runpl():
    """run application with pl_PL localization"""
    os.environ['LC_ALL'] = 'pl_PL.utf8'
    run()

@task
def pot():
    """generate 'pot' file out of python/glade files"""
    if not os.path.exists('locale'):
        os.mkdir('locale')
    sh("python bin/generate_pot.py > locale/pygtktalog.pot")

@task
@needs(['pot'])
def mergepl():
    """create or merge if exists polish 'po' translation file"""
    if os.path.exists(os.path.join('locale', 'pl.po')):
        sh('msgmerge -U locale/pl.po locale/pygtktalog.pot')
    else:
        shutil.copy(os.path.join('locale', 'pygtktalog.pot'),
                    os.path.join('locale', 'pl.po'))

@task
@needs(['mergepl'])
def genpl():
    """generate message catalog file for polish locale"""
    if not os.path.exists(os.path.join('pygtktalog', 'locale')):
        full_path = 'pygtktalog'
        for name in ['locale', 'pl', 'LC_MESSAGES']:
            full_path = os.path.join(full_path, name)
            os.mkdir(full_path)
    sh('msgfmt locale/pl.po -o pygtktalog/locale/pl/LC_MESSAGES/pygtktalog.mo')

if have_lint:
    @task
    def pylint():
        '''Check the module you're building with pylint.'''
        pylintopts = ['pygtktalog']
        dry('pylint %s' % (" ".join(pylintopts)), lint.Run, pylintopts)

@task
def test():
    """run unit tests"""
    os.system("PYTHONPATH=%s:$PYTHONPATH nosetests -w test" % _setup_env())


def _setup_env():
    """Helper function to set up paths"""
    # current directory
    this_path = os.path.dirname(os.path.abspath(__file__))
    if this_path not in sys.path:
        sys.path.insert(0, this_path)
        
    # return 
    return this_path

