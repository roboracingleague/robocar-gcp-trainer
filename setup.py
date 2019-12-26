from setuptools import setup, find_packages
import os

NAME = 'roborace'
VERSION = '1.0'
REQUIRED_PACKAGES = []


setup(
    name=NAME,
    version=VERSION,
    packages=find_packages(),
    install_requires=REQUIRED_PACKAGES,    
    )