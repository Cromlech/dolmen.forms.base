1# -*- coding: utf-8 -*-

from os.path import join
from setuptools import setup, find_packages

name = 'dolmen.forms.base'
version = '3.0-crom'
readme = open('README.txt').read()
history = open(join('docs', 'HISTORY.txt')).read()

install_requires = [
    'crom',
    'cromlech.browser >= 0.5',
    'cromlech.i18n',
    'dolmen.collection >= 0.3',
    'dolmen.template',
    'grokker',
    'setuptools',
    'zope.configuration',
    'zope.event',
    'zope.i18nmessageid',
    'zope.interface',
    'zope.lifecycleevent',
    'zope.schema',
    ]

tests_require = [
    'cromlech.browser [test]',
    'WebOb >= 1.2.1',
    'cromlech.webob',
    'infrae.testbrowser',
    'zope.location',
    ]

setup(name=name,
      version=version,
      description=("Dolmen forms framework"),
      long_description=readme + '\n\n' + history,
      keywords='Dolmen Forms',
      author='The Dolmen Team',
      author_email='dolmen@list.dolmen-project.org',
      url='http://gitweb.dolmen-project.org/',
      license='BSD',
      package_dir={'': 'src'},
      packages=find_packages('src', exclude=['ez_setup']),
      namespace_packages=['dolmen', 'dolmen.forms'],
      include_package_data=True,
      zip_safe=False,
      tests_require=tests_require,
      install_requires=install_requires,
      extras_require={'test': tests_require},
      test_suite="dolmen.forms.base",
      classifiers=[
          'Development Status :: 4 - Beta',
          'Environment :: Web Environment',
          'Intended Audience :: Other Audience',
          'License :: OSI Approved :: GNU General Public License (GPL)',
          'Operating System :: OS Independent',
          'Programming Language :: Python',
          ],
      entry_points="""
      # -*- Entry points: -*-
      [cromlech.i18n.translation_directory]
      dolmen.forms.base = dolmen.forms.base:register_translations
      """,
      )
