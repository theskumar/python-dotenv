#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import re
import sys
from setuptools import setup


def get_version(module):
    """
    Return package version as listed in `__version__`.
    """
    init_py = open('{0}.py'.format(module)).read()
    return re.search("__version__ = ['\"]([^'\"]+)['\"]", init_py).group(1)


version = get_version('dotenv')


if sys.argv[-1] == 'publish':
    os.system('python setup.py sdist upload')
    os.system('python setup.py bdist_wheel upload')
    print('You probably want to also tag the version now:')
    print('  git tag -a {0} -m "version {0}"'.format(version, version))
    print('  git push --tags')
    sys.exit()


setup(
    name='django-dotenv',
    description="foreman reads from .env. manage.py doesn't. Let's fix that.",
    version=version,
    author='Jacob Kaplan-Moss',
    author_email='jacob@jacobian.org',
    maintainer='José Padilla',
    maintainer_email='hello@jpadilla.com',
    url='http://github.com/jpadilla/django-dotenv',
    py_modules=['dotenv'],
    test_suite='tests',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Topic :: Internet :: WWW/HTTP',
    ]
)
