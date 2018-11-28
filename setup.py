
import os
from setuptools import setup, find_packages

def read(filename):
    return open(os.path.join(os.path.dirname(__file__), filename)).read()

def get_version(version_file):
    ns = {}
    exec(read(version_file), ns)
    return ns['__version__']

setup(
    name = 'tdm',
    version = get_version('tdm/version.py'),
    author = 'Mac Coombe',
    author_email = 'mac.coombe@csiro.au',
    description = ('THREDDS Data Manager Client'),
    # TODO: license = '',
    keywords = 'THREDDS',
    url = 'https://bitbucket.csiro.au/projects/SC/repos/tdm-client-python/browse',
    packages = find_packages(),
    long_description = read('readme.md'),
    install_requires = [
        'requests'
    ],
    extras_require = {
        'large_files': [
            'requests-toolbelt'
        ]
    },
    classifiers = [
        'Development Status :: 3 - Alpha',
        'Topic :: Scientific/Engineering :: Information Analysis',
        'License :: OSI Approved :: BSD License',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Operating System :: POSIX',
        'Programming Language :: Python :: 2.7'
    ]
)
