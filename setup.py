#!/usr/bin/env python
# -*- coding: utf-8 -*-
from setuptools import find_packages, setup  # type: ignore

extras_require = {
    "test": [  # `test` GitHub Action jobs uses this
        "ape-arbitrum",  # Needed for testing Arbitrum integration
        "ape-optimism",  # Needed for testing Optimism integration
        "ape-polygon",  # Needed for testing Polygon integration
        "pytest>=6.0",  # Core testing package
        "pytest-xdist",  # multi-process runner
        "pytest-cov",  # Coverage analyzer plugin
        "pytest-mock",  # For creating mocks
        "hypothesis>=6.2.0,<7.0",  # Strategy-based fuzzer
    ],
    "lint": [
        "black>=22.10.0",  # auto-formatter and linter
        "mypy>=0.991",  # Static type analyzer
        "types-requests",  # Needed due to mypy typeshed
        "flake8>=5.0.4",  # Style linter
        "flake8-breakpoint>=1.1.0",  # detect breakpoints left in code
        "flake8-print>=4.0.0",  # detect print statements left in code
        "isort>=5.10.1",  # Import sorting linter
    ],
    "doc": [
        "myst-parser>=0.17.0,<0.18",  # Tools for parsing markdown files in the docs
        "sphinx-click>=3.1.0,<4.0",  # For documenting CLI
        "Sphinx>=4.4.0,<5.0",  # Documentation generator
        "sphinx_rtd_theme>=1.0.0,<2",  # Readthedocs.org theme
        "sphinxcontrib-napoleon>=0.7",  # Allow Google-style documentation
    ],
    "release": [  # `release` GitHub Action job uses this
        "setuptools",  # Installation tool
        "wheel",  # Packaging tool
        "twine",  # Package upload tool
    ],
    "dev": [
        "commitizen",  # Manage commits and publishing releases
        "pre-commit",  # Ensure that linters are run prior to commiting
        "pytest-watch",  # `ptw` test watcher/runner
        "IPython",  # Console for interacting
        "ipdb",  # Debugger (Must use `export PYTHONBREAKPOINT=ipdb.set_trace`)
    ],
}

# NOTE: `pip install -e .[dev]` to install package
extras_require["dev"] = (
    extras_require["test"]
    + extras_require["lint"]
    + extras_require["doc"]
    + extras_require["release"]
    + extras_require["dev"]
)

with open("./README.md") as readme:
    long_description = readme.read()


setup(
    name="ape-alchemy",
    use_scm_version=True,
    setup_requires=["setuptools_scm"],
    description="""ape-alchemy: Alchemy Provider plugins for Ethereum-based networks""",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="ApeWorX Ltd.",
    author_email="admin@apeworx.io",
    url="https://github.com/ApeWorX/ape-alchemy",
    include_package_data=True,
    install_requires=[
        "eth-ape>=0.5.2,<0.6",
        "web3",  # Get web3 version from ape
        "requests",
    ],
    python_requires=">=3.8,<3.11",
    extras_require=extras_require,
    py_modules=["ape_alchemy"],
    license="Apache-2.0",
    zip_safe=False,
    keywords="ethereum",
    packages=find_packages(exclude=["tests", "tests.*"]),
    package_data={"ape_alchemy": ["py.typed"]},
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Natural Language :: English",
        "Operating System :: MacOS",
        "Operating System :: POSIX",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
)
