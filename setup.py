#!/usr/bin/env python
# -*- coding: utf-8 -*-
from setuptools import find_packages, setup

extras_require = {
    "test": [  # `test` GitHub Action jobs uses this
        "ape-arbitrum",  # Needed for testing Arbitrum integration
        "ape-base",  # Needed for testing Base integration
        "ape-fantom",  # Needed for testing fantom integration
        "ape-optimism",  # Needed for testing Optimism integration
        "ape-polygon",  # Needed for testing Polygon integration
        "ape-polygon-zkevm",  # Needed for testing Polygon-ZkEVM integration
        "pytest>=6.0",  # Core testing package
        "pytest-xdist",  # Multi-process runner
        "pytest-cov",  # Coverage analyzer plugin
        "pytest-mock",  # For creating mocks
        "hypothesis>=6.2.0,<7.0",  # Strategy-based fuzzer
        "websocket-client",  # Used for web socket integration testing
    ],
    "lint": [
        "black>=25.1.0,<26",  # Auto-formatter and linter
        "mypy>=1.15.0,<2",  # Static type analyzer
        "types-setuptools",  # Needed for mypy type shed
        "types-requests",  # Needed for mypy type shed
        "flake8>=7.1.2,<8",  # Style linter
        "flake8-breakpoint>=1.1.0,<2",  # Detect breakpoints left in code
        "flake8-print>=5.0.0,<6",  # Detect print statements left in code
        "flake8-pydantic",  # For detecting issues with Pydantic models
        "flake8-type-checking",  # Detect imports to move in/out of type-checking blocks
        "isort>=6.0.0,<7",  # Import sorting linter
        "mdformat>=0.7.22",  # Auto-formatter for markdown
        "mdformat-gfm>=0.3.5",  # Needed for formatting GitHub-flavored markdown
        "mdformat-frontmatter>=0.4.1",  # Needed for frontmatters-style headers in issue templates
        "mdformat-pyproject>=0.0.2",  # Allows configuring in pyproject.toml
    ],
    "doc": [
        "sphinx-ape",
    ],
    "release": [  # `release` GitHub Action job uses this
        "setuptools>=75.6.0",  # Installation tool
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
    description="""ape-alchemy: Alchemy provider plugins""",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="ApeWorX Ltd.",
    author_email="admin@apeworx.io",
    url="https://github.com/ApeWorX/ape-alchemy",
    include_package_data=True,
    install_requires=[
        "eth-ape>=0.8.34,<0.9",
        "eth-pydantic-types>=0.2.0,<0.3",
        "ethpm-types>=0.6.26,<0.7",
        "evm-trace>=0.2.6,<0.3",
        "web3>=6.20.1,<8",
        "requests>=2.32.3,<3",
        "evmchains>=0.1.3,<0.2",  # Dependent on networks (not imports)
    ],
    python_requires=">=3.9,<4",
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
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
)
