from os.path import join
from setuptools import setup, find_packages

name = 'dolmen.forms.base'
version = '1.0a1'
readme = open(join('src', 'dolmen', 'forms', 'base', 'README.txt')).read()
history = open(join('docs', 'HISTORY.txt')).read()

install_requires = [
    'grokcore.component',
    'megrok.layout',
    'setuptools',
    'zeam.form.base',
    'zeam.form.layout',
    'zeam.form.ztk',
    'zope.configuration',
    'zope.event',
    'zope.interface',
    'zope.lifecycleevent',
    'zope.schema',
    ]

tests_require = [
    'zope.component',
    'zope.testing',
    ]

setup(name=name,
      version=version,
      description=("Forms meta-package for Dolmen, "
                   "using megrok.z3cform.base and z3c.form"),
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
