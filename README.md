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

Use in most commands using the `--network` option:

```bash
ape console --network ethereum:goerli:alchemy
```

## Development

This project is in development and should be considered a beta.
Things might not be in their final state and breaking changes may occur.
Comments, questions, criticisms and pull requests are welcomed.

## License

This project is licensed under the [Apache 2.0](LICENSE).
