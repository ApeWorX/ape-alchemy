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

**NOTE**: If you require the Geth style traces, you still have access to them via the `get_transaction_trace()` method and utilities from the `evm-trace` library:

```python
from evm_trace import CallType, get_calltree_from_geth_trace

from ape import networks

alchemy = networks.provider  # Assuming connected to Alchemy
txn_hash = "0x053cba5c12172654d894f66d5670bab6215517a94189a9ffc09bc40a589ec04d"
receipt = alchemy.get_transaction(txn_hash)
root_node_kwargs = {
    "gas_cost": receipt.gas_used,
    "gas_limit": receipt.gas_limit,
    "address": receipt.receiver,
    "calldata": receipt.data,
    "value": receipt.value,
    "call_type": CallType.CALL,
    "failed": receipt.failed,
}
trace_frame_iter = alchemy.get_transaction_trace(txn_hash)
call_tree = get_calltree_from_geth_trace(trace_frame_iter)
```

## Development

Please see the [contributing guide](CONTRIBUTING.md) to learn more how to contribute to this project.
Comments, questions, criticisms and pull requests are welcomed.

## License

This project is licensed under the [Apache 2.0](LICENSE).
