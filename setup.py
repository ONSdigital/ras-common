"""A setuptools based setup module.

See:
https://github.com/ONSdigital/ras-common
"""

# Always prefer setuptools over distutils
from setuptools import setup, find_packages
# To use a consistent encoding
from codecs import open
from os import path
from pip.req import parse_requirements

install_reqs = parse_requirements('requirements.txt', session='hack')

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

__version__ = '0.1.0'

setup(
    name='ons_ras_common',

    # Versions should comply with PEP440.  For a discussion on single-sourcing
    # the version across setup.py and the project code, see
    # https://packaging.python.org/en/latest/single_source_version.html
    version=__version__,

    description='The Common library for ONS RAS Micro-Services',
    long_description="""
    This library covers a multitude of miscellaneous routines used by micro-services
    including but not limited to, Cloud Foundry provisioning, JWT encryption, generic
    encryption, Database detection and setup, router endpoint provisioning, Swagger
    API setup, configuration file management and async reactor startup.
    """,

    # The project's main homepage.
    url='https://github.com/ONSdigital/ras-common',

    # Author details
    author='RAS Development Team',
    author_email='onsdigital@linux.co.uk',

    # Choose your license
    license='MIT',

    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 3 - Alpha',

        # Indicate who your project is intended for
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',

        # Pick your license as you wish (should match "license" above)
        'License :: OSI Approved :: MIT License',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6'
    ],

    # What does your project relate to?
    keywords=['micro-service'],

    # You can just specify the packages manually here if your project is
    # simple. Or you can use find_packages().
    #packages=find_packages(exclude=['contrib', 'docs', 'tests']),

    # Alternatively, if you want to distribute just a my_module.py, uncomment
    # this:
    packages=["ons_ras_common"],

    # List run-time dependencies here.  These will be installed by pip when
    # your project is installed. For an analysis of "install_requires" vs pip's
    # requirements files see:
    # https://packaging.python.org/en/latest/requirements.html
    install_requires=[str(ir.req) for ir in install_reqs],

    # Although 'package_data' is the preferred approach, in some case you may
    # need to place data files outside of your packages. See:
    # http://docs.python.org/3.4/distutils/setupscript.html#installing-additional-files # noqa
    # In this case, 'data_file' will be installed into '<sys.prefix>/my_data'
    package_data={
        'samples': ['config.ini', 'local.ini', 'main.py', ' swagger.yaml', 'Procfile', 'runtime.txt']
    },

    entry_points={
    'console_scripts': [
        'ons_ras_common=ons_ras_common:tool',
    ],
},
)