#!/usr/bin/env python
# encoding: UTF-8
import ast
from os import path

from setuptools import setup

try:
    # For setup.py install
    from ons_ras_common.ons_version import __version__ as version
except ImportError:
    # For pip installations
    version = str(
        ast.literal_eval(
            open(path.join(
                path.dirname(__file__),
                "ons_ras_common", "ons_version.py"),
                'r').read().split("=")[-1].strip()
            )
    )

install_requirements = [
    i.strip() for i in open(
        path.join(path.dirname(__file__), "requirements.txt"), 'r'
    ).readlines()
]

setup(
    name='ras_common',
    version=version,
    description='The Common library for ONS RAS Micro-Services',
    url='https://github.com/ONSdigital/ras-common',
    author='G Irving',
    author_email='gemma.i_95@hotmail.co.uk',
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6'
    ],
    keywords=['micro-service', 'ons-ras'],
    packages=["ons_ras_common"],
    install_requires=install_requirements,
    package_data={
        "ras-common": [
            "requirements.txt",
        ]
    },
    entry_points={
        'console_scripts': [
        ],
    },
)
