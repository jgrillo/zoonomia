#   Copyright 2015-2017 Jesse C. Grillo
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

import os

from setuptools import setup

HERE = os.path.abspath(os.path.dirname(__file__))


def not_comment(line):
    """Predicate function to determine whether a line is not a comment."""
    if line.strip().startswith('#'):
        return False
    else:
        return True


with open(os.path.join(HERE, 'requirements.txt')) as requirements_file:
    REQUIREMENTS = tuple(
        line.strip() for line in filter(not_comment, requirements_file)
    )

with open(
    os.path.join(HERE, 'requirements-test.txt')
) as requirements_tests_file:
    REQUIREMENTS_TEST = tuple(
        line.strip() for line in filter(not_comment, requirements_tests_file)
    )

with open(os.path.join(HERE, 'README.md')) as readme_file:
    README = readme_file.read()

__version__ = '0.0.1'

setup(
    name='zoonomia',
    version=__version__,
    author='Jesse C. Grillo',
    author_email='jesse.grillo@gmail.com',
    url='https://www.github.com/jgrillo/zoonomia',
    description='Multi-objective strongly typed genetic programming library',
    long_description=README,
    license='MIT',
    packages=('zoonomia',),
    classifiers=(
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Topic :: Scientific/Engineering',
        'Topic :: Software Development :: Libraries',
        'Topic :: Scientific/Engineering :: Artificial Intelligence',
        'Topic :: Scientific/Engineering :: Artificial Life'
    ),
    install_requires=REQUIREMENTS,
    tests_require=REQUIREMENTS_TEST,
    zip_safe=False
)
