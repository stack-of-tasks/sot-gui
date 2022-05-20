#!/usr/bin/env python

from pathlib import Path
from setuptools import setup, find_packages

PACKAGE_NAME = "sot_gui"

setup(
    name=PACKAGE_NAME,
    version="1.0",
    description="",
    author="Justine Fricou",
    author_email="justine.fricou@gmail.com",
    packages=find_packages(where='src'),
    package_dir={PACKAGE_NAME: str(Path("src") / PACKAGE_NAME)},
)
    