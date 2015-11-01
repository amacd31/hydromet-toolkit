import os
from io import open

import versioneer

from setuptools import setup

setup(
    name='hydromet',
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    description='Toolkit for manipulating and exploring hydrological and meteorological variables.',
    author='Andrew MacDonald',
    author_email='andrew@maccas.net',
    license='BSD',
    url='https://github.com/amacd31/hydromet-toolkit',
    install_requires=['numpy', 'pandas'],
    packages = ['hydromet'],
    test_suite = 'tests',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'Topic :: Software Development :: Build Tools',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'License :: OSI Approved :: BSD License',

        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
    ],
)
