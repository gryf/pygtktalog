#!/usr/bin/env python2
"""
Setup for the pyGTKtalog project
"""
from distutils.core import setup


setup(name='pygtktalog',
      packages=['pygtktalog'],
      version='2.0',
      description='Catalog application with GTK interface',
      author='Roman Dobosz',
      author_email='gryf73@gmail.com',
      url='https://github.com/gryf/pygtktalog',
      download_url='https://github.com/gryf/pygtktalog.git',
      keywords=['catalog', 'gwhere', 'where is it', 'collection', 'GTK'],
      requires=['Pillow', 'sqlalchemy'],
      scripts=['scripts/cmdcatalog.py'],
      classifiers=['Programming Language :: Python :: 2',
                   'Programming Language :: Python :: 2.7',
                   'Programming Language :: Python :: 2 :: Only',
                   'Development Status :: 4 - Beta',
                   'Environment :: Console',
                   'Intended Audience :: End Users/Desktop',
                   'License :: OSI Approved :: BSD License',
                   'Operating System :: OS Independent',
                   'Topic :: Multimedia :: Graphics'],
      long_description=open('README.rst').read(),
      options={'test': {'verbose': False,
                        'coverage': False}})
