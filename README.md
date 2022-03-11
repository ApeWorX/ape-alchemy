# Ape Alchemy Plugin

Alchemy Provider plugins for Ethereum-based networks.

## Dependencies

* [python3](https://www.python.org/downloads) version 3.7 or greater, python3-dev

## Installation

### via `pip`

You can install the latest release via [`pip`](https://pypi.org/project/pip/):

```bash
pip install ape-alchemy
```

### via `setuptools`

You can clone the repository and use [`setuptools`](https://github.com/pypa/setuptools) for the most up-to-date version:

```bash
git clone https://github.com/ApeWorX/ape-alchemy.git
cd ape-alchemy
python3 setup.py install
```

## Quick Usage

First, make sure you have one of the following environment variables set (it doesn't matter which one):

* WEB3_ALCHEMY_PROJECT_ID
* WEB3_ALCHEMY_API_KEY

Either in your current terminal session or in your root RC file (e.g. `.bashrc`), add the following:

```bash
export WEB3_ALCHEMY_PROJECT_ID=MY_API_TOKEN
```

To use the Alchemy provider plugin in most commands, set it via the `--network` option:

```bash
ape console --network ethereum:goerli:alchemy
```

## Development

Please see the [contributing guide](CONTRIBUTING.md) to learn more how to contribute to this project.
Comments, questions, criticisms and pull requests are welcomed.

## License

This project is licensed under the [Apache 2.0](LICENSE).
