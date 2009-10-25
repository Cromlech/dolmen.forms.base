from os.path import join
from setuptools import setup, find_packages

name = 'dolmen.forms.base'
version = '0.1'
readme = open(join('src', 'dolmen', 'forms', 'base', 'README.txt')).read()
history = open(join('docs', 'HISTORY.txt')).read()

install_requires = [
    'setuptools',
    'z3c.form',
    'zope.schema',
    'zope.interface',
    'zope.configuration',
    'megrok.z3cform.base'
    ]

tests_require = install_requires + [
    'zope.testing',
    ]

setup(name=name,
      version=version,
      description="",
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
