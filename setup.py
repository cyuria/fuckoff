#!/usr/bin/env python
from setuptools import setup, find_packages
import pkg_resources
import sys
import os
import fastentrypoints


try:
    if int(pkg_resources.get_distribution("pip").version.split('.')[0]) < 6:
        print('pip older than 6.0 not supported, please upgrade pip with:\n\n'
              '    pip install -U pip')
        sys.exit(-1)
except pkg_resources.DistributionNotFound:
    pass

if os.environ.get('CONVERT_README'):
    import pypandoc

    long_description = pypandoc.convert_file('README.md', 'rst')
else:
    long_description = ''

version = sys.version_info[:2]
if version < (3, 10):
    print('fuckoff requires Python version 3.10 or later' +
          ' ({}.{} detected).'.format(*version))
    sys.exit(-1)

VERSION = '0.1.0-alpha'

install_requires = ['psutil', 'colorama', 'decorator', 'pyte']
extras_require = {":sys_platform=='win32'": ['win_unicode_console']}

if sys.platform == "win32":
    scripts = ['scripts\\fuck.bat', 'scripts\\fuck.ps1']
    entry_points = {
        'console_scripts': [
            'fuckoff = fuckoff.entrypoints.main:main',
            'fuckoff_firstuse = fuckoff.entrypoints.not_configured:main'
        ]
    }
else:
    scripts = []
    entry_points = {
        'console_scripts': [
            'fuckoff = fuckoff.entrypoints.main:main',
            'fuck = fuckoff.entrypoints.not_configured:main'
        ]
    }

setup(
    name='fuckoff',
    version=VERSION,
    description="A fork/rewrite of the excellent nvbn/thefuck",
    long_description=long_description,
    author='Cyuria',
    author_email='cyuria.dev@gmail.com',
    url='https://github.com/cyuria/fuckoff',
    license='MIT',
    packages=find_packages(
        exclude=['ez_setup', 'examples', 'tests', 'tests.*', 'release']
    ),
    include_package_data=True,
    zip_safe=False,
    python_requires='>=3.10',
    install_requires=install_requires,
    extras_require=extras_require,
    scripts=scripts,
    entry_points=entry_points
)
