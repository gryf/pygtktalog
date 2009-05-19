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
from paver.misctasks import generate_setup, minilib
try:
    from pylint import lint
    HAVE_LINT = True
except ImportError:
    HAVE_LINT = False


REV = os.popen("svn info 2>/dev/null|grep ^Revis|cut -d ' ' -f 2").readlines()
if REV:
    REV = "r" + REV[0].strip()
else:
    REV = '0'
    
LOCALES = ('pl','en')


# distutil/setuptool setup method.
setup(
      name='pyGTKtalog',
      version='1.99.%s' % REV,

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
@needs(['locale_gen', 'minilib', 'generate_setup'])
def sdist():
    """sdist with message catalogs"""
    call_task("setuptools.command.sdist")

@task
@needs(['locale_gen'])
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
    #sh("PYTHONPATH=%s:$PYTHONPATH bin/gtktalog.py" % _setup_env())
    import gtktalog
    gtktalog.run()

@task
def pot():
    """generate 'pot' file out of python/glade files"""
    if not os.path.exists('locale'):
        os.mkdir('locale')
    sh("python bin/generate_pot.py > locale/pygtktalog.pot")

@task
@needs(['pot'])
def locale_merge():
    """create or merge if exists 'po' translation files"""
    potfile = os.path.join('locale', 'pygtktalog.pot')
    for lang in LOCALES:
        msg_catalog = os.path.join('locale', "%s.po" % lang)
        if os.path.exists(msg_catalog):
            sh('msgmerge -U %s %s' % (msg_catalog, potfile))
        else:
            shutil.copy(pot, msg_catalog)

@task
@needs(['locale_merge'])
def locale_gen():
    """generate message catalog file for available locale files"""
    full_path = os.path.join('pygtktalog', 'locale')
    if not os.path.exists(full_path):
        os.mkdir(full_path)
    
    for lang in LOCALES:
        lang_path = full_path
        for dirname in [lang, 'LC_MESSAGES']:
            lang_path = os.path.join(lang_path, dirname)
            if not os.path.exists(lang_path):
                os.mkdir(lang_path)
        catalog_file = os.path.join(lang_path, 'pygtktalog.mo')
        msg_catalog = os.path.join('locale', "%s.po" % lang)
        sh('msgfmt %s -o %s' % (msg_catalog, catalog_file))

if HAVE_LINT:
    @task
    def pylint():
        '''Check the module you're building with pylint.'''
        pylintopts = ['pygtktalog']
        dry('pylint %s' % (" ".join(pylintopts)), lint.Run, pylintopts)

@task
def test():
    """run unit tests"""
    os.system("PYTHONPATH=%s:$PYTHONPATH nosetests -w test" % _setup_env())


@task
@needs(['locale_gen'])
def runpl():
    """run application with pl_PL localization. This is just for my
    convenience"""
    os.environ['LC_ALL'] = 'pl_PL.utf8'
    run()


def _setup_env():
    """Helper function to set up paths"""
    # current directory
    this_path = os.path.dirname(os.path.abspath(__file__))
    if this_path not in sys.path:
        sys.path.insert(0, this_path)

    return this_path

