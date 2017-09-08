# -*- coding: utf-8 -*-
import os
from setuptools import setup, find_packages


def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

version = '0.2'

long_description = (
    read('README.rst') +
    '\n' +
    'Change history\n'
    '**************\n' +
    '\n' +
    read('CHANGES.txt') +
    '\n' +
    'Download\n'
    '********\n')

tests_require = ['zope.testing', 'plone.testing', 'plone.app.testing', 'mock']


setup(name='jazkarta.pfg.jazshop',
      version=version,
      description="Plone Formgen Fields for working with Jazkarta Shop",
      long_description=long_description,
      # Get more strings from
      # http://pypi.python.org/pypi?:action=list_classifiers
      classifiers=[
        'Development Status :: 4 - Beta',
        'Framework :: Plone',
        'Framework :: Plone :: 4.3',
        'Intended Audience :: Developers',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Operating System :: OS Independent',
        ],
      keywords='Plone PloneFormGen',
      author='Jazkarta',
      author_email='info@jazkarta.com',
      url='https://github.com/jazkarta/jazkarta.pfg.jazshop',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['jazkarta', 'jazkarta.pfg'],
      include_package_data=True,
      zip_safe=False,
      install_requires=['setuptools',
                        # -*- Extra requirements: -*-,
                        'Products.PloneFormGen',
                        'jazkarta.shop',
                        ],
      tests_require=tests_require,
      extras_require=dict(tests=tests_require),
      entry_points="""
      # -*- entry_points -*-
      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
