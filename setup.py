#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os.path

from setuptools import find_packages, setup

import versioneer


def parse_requirements(path):
    """Parse ``requirements.txt`` at ``path``."""
    requirements = []
    with open(path, "rt") as reqs_f:
        for line in reqs_f:
            line = line.strip()
            if line.startswith("-r"):
                fname = line.split()[1]
                inner_path = os.path.join(os.path.dirname(path), fname)
                requirements += parse_requirements(inner_path)
            elif line != "" and not line.startswith("#"):
                requirements.append(line)
    return requirements


with open("README.rst") as readme_file:
    readme = readme_file.read()

with open("HISTORY.rst") as history_file:
    history = history_file.read()

test_requirements = parse_requirements("requirements/test.txt")
install_requirements = parse_requirements("requirements/base.txt")

setup(
    author="Manuel Holtgrewe",
    author_email=("manuel.holtgrewe@bihealth.de"),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Topic :: Scientific/Engineering :: Bio-Informatics",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    entry_points={"console_scripts": ("varfish-cli = varfish_cli.__main__:main",)},
    description="Command line interface client for VarFish Server.",
    install_requires=install_requirements,
    license="MIT license",
    long_description=readme + "\n\n" + history,
    include_package_data=True,
    keywords="varfish_cli",
    name="varfish_cli",
    packages=find_packages(include=["varfish_cli"]),
    test_suite="tests",
    tests_require=test_requirements,
    url="https://github.com/bihealth/varfish-cli",
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    zip_safe=False,
)
