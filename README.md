# Quick Start

Use the [Alchemy](https://alchemy.com/?r=jk3NDM0MTIwODIzM) provider plugin to interact with blockchains via APIs.
The `ape-alchemy` plugin supports the following ecosystems:

- Ethereum
- Arbitrum
- Base
- Optimism
- Polygon

## Dependencies

- [python3](https://www.python.org/downloads) version 3.8 up to 3.11.

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

- `WEB3_ALCHEMY_PROJECT_ID`
- `WEB3_ALCHEMY_API_KEY`
- `WEB3_<ecosystem>_<network>_ALCHEMY_PROJECT_ID`
- `WEB3_<ecosystem>_<network>_ALCHEMY_PROJECT_ID`

For example, to use both Arbitrum and Ethereum in the same session, you could set both `WEB3_ARBITRUM_MAINNET_ALCHEMY_PROJECT_ID` and `WEB3_ETHEREUM_MAINNET_ALCHEMY_PROJECT_ID`.

**NOTE**: If using non-Ethereum networks, take care to install the correct plugins, such as `ape-arbitrum`, `ape-optimism`, etc:

```bash
ape plugins install arbitrum
```

Then, either in your current terminal session or in your root RC file (e.g. `.bashrc`), add the following:

```bash
export WEB3_ALCHEMY_PROJECT_ID=MY_API_TOKEN=<value-of-secret-key>
```

To use the Alchemy provider plugin in most commands, set it via the `--network` option:

```bash
ape console --network ethereum:goerli:alchemy
```

To connect to Alchemy from a Python script, use the `networks` top-level manager:

```python
from ape import networks

with networks.parse_network_choice("ethereum:mainnet:alchemy") as provider:
    ...
```

### Transaction Traces

If you are using a paid tier of Alchemy, you have access to both Geth and Parity style traces.
Parity traces are faster and thus are the ones uses in Ethereum receipts' `show_trace()` method:

```python
from ape import networks

alchemy = networks.provider  # Assuming connected to Alchemy
txn_hash = "0x053cba5c12172654d894f66d5670bab6215517a94189a9ffc09bc40a589ec04d"
receipt = alchemy.get_transaction(txn_hash)
receipt.show_trace()  # Prints the Transaction trace
```

To access the raw `CallTree`, do:

```python
from ape import networks

alchemy = networks.provider  # Assuming connected to Alchemy
txn_hash = "0x053cba5c12172654d894f66d5670bab6215517a94189a9ffc09bc40a589ec04d"
call_tree = alchemy.get_call_tree(txn_hash)
```

To learn more about transaction traces, view [Ape's transaction guide](https://docs.apeworx.io/ape/stable/userguides/transactions.html#traces).
