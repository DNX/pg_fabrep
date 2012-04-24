#!/usr/bin/env python
# -*- coding: utf-8 -*-
from setuptools import setup, find_packages
import os

CLASSIFIERS = [
    'Development Status :: 3 - Alpha',
    'Environment :: Console',
    'Intended Audience :: Developers',
    'Intended Audience :: System Administrators',
    'Operating System :: MacOS :: MacOS X',
    'Operating System :: Unix',
    'Operating System :: POSIX',
    'Programming Language :: Python',
    'Programming Language :: Python :: 2.5',
    'Programming Language :: Python :: 2.6',
    'Topic :: Software Development',
    'Topic :: Software Development :: Build Tools',
    'Topic :: Software Development :: Libraries',
    'Topic :: Software Development :: Libraries :: Python Modules',
    'Topic :: System :: Clustering',
    'Topic :: System :: Software Distribution',
    'Topic :: System :: Systems Administration',
]

setup(
    name="pg_fabrep",
    version=__import__('pg_fabrep').get_version(),
    url='https://bitbucket.org/DNX/pg_fabrep/',
    download_url='http://bitbucket.org/DNX/pg_fabrep/downloads',
    license='BSD License',
    description="Postgresql Streaming Replication with Fabric and Repmgr",
    long_description=open(os.path.join(os.path.dirname(__file__), 'README.rst')).read(),
    author='Denis Darii',
    author_email='denis.darii@gmail.com',
    keywords='postgres streaming replication fabric repmgr',
    packages=find_packages(),
    namespace_packages=['pg_fabrep'],
    include_package_data=True,
    zip_safe=False,
    classifiers=CLASSIFIERS,
    install_requires=[
        'Fabric>=1.3',
    ],
)
