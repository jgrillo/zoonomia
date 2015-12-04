import os

from itertools import ifilter
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
        line.strip() for line in ifilter(not_comment, requirements_file)
    )

with open(
    os.path.join(HERE, 'requirements-test.txt')
) as requirements_tests_file:
    REQUIREMENTS_TEST = tuple(
        line.strip() for line in ifilter(not_comment, requirements_tests_file)
    )

with open(os.path.join(HERE, 'README.md')) as readme_file:
    README = readme_file.read()

__version__ = 'unknown'

execfile(os.path.join(HERE, 'zoonomia', '_version.py'))

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
        'Development Status :: 1 - Planning',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: Implementation :: CPython',
        'Topic :: Scientific/Engineering',
        'Topic :: Software Development :: Libraries',
    ),
    install_requires=REQUIREMENTS,
    tests_require=REQUIREMENTS_TEST,
    test_suite='nose.collector',
    zip_safe=False
)
