from setuptools import setup, find_packages
import os

version = '0.1'

setup(name='dolmen.forms.base',
      version=version,
      description="",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      classifiers=[
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
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
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
