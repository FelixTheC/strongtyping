#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@created: 30.04.20
@author: felix
"""
import pathlib

from setuptools import find_packages
from setuptools import setup

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()
setup(
    name="strongtyping",
    version="1.1.16",
    description="Decorator which checks whether the function is called with the correct type of parameters",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/FelixTheC/strongtyping",
    author="FelixTheC",
    author_email="fberndt87@gmail.com",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
    ],
    packages=find_packages(exclude=['test_*']),
    python_requires='>=3.6',
    include_package_data=True,
)
