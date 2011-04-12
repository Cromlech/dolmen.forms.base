from os.path import join
from setuptools import setup, find_packages

name = 'dolmen.forms.base'
version = '1.0b3'
readme = open(join('src', 'dolmen', 'forms', 'base', 'README.txt')).read()
history = open(join('docs', 'HISTORY.txt')).read()

install_requires = [
    'dolmen.view',
    'dolmen.collection',
    'cromlech.io',
    'cromlech.browser',
    'grokcore.component',
    'grokcore.security',
    'setuptools',
    'zope.event',
    'zope.interface',
    'zope.lifecycleevent',
    'zope.schema',
    'zope.i18n',
    'zope.i18nmessageid',
    ]

tests_require = [
    'zope.component',
    'cromlech.webob',
    ]

setup(name=name,
      version=version,
      description=("Dolmen forms framework"),
      long_description = readme + '\n\n' + history,
      keywords='Dolmen Forms',
      author='Souheil Chelfouh',
      author_email='trollfot@gmail.com',
      url='',
      license='GPL',
      package_dir={'': 'src'},
      packages=find_packages('src', exclude=['ez_setup']),
      namespace_packages=['dolmen', 'dolmen.forms'],
      include_package_data=True,
      zip_safe=False,
      tests_require = tests_require,
      install_requires = install_requires,
      extras_require = {'test': tests_require},
      test_suite="dolmen.forms.base",
      classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Framework :: Zope3',
        'Intended Audience :: Other Audience',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
          ],
      )
