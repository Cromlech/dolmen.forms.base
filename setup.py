# -*- coding: utf-8 -*-

from os.path import join
from setuptools import setup, find_packages

name = 'dolmen.forms.base'
version = '2.2'
readme = open('README.txt').read()
history = open(join('docs', 'HISTORY.txt')).read()

install_requires = [
    'cromlech.browser >= 0.4.2',
    'cromlech.i18n',
    'dolmen.collection >= 0.3',
    'dolmen.template',
    'dolmen.view >= 0.4',
    'grokcore.component',
    'grokcore.security',
    'setuptools',
    'zope.component',
    'zope.configuration',
    'zope.event',
    'zope.i18n',
    'zope.i18nmessageid',
    'zope.interface',
    'zope.lifecycleevent',
    'zope.schema',
    ]

tests_require = [
    'BeautifulSoup',
    'WebOb',
    'cromlech.io >= 0.2a1',
    'cromlech.webob',
    'dolmen.location',
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
      )
