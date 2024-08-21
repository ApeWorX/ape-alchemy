import pytest
from ape import chain, networks


@pytest.fixture(autouse=True)
def ethereum_mainnet_alchemy():
    with networks.ethereum.mainnet.use_provider("alchemy"):
        yield


def test_revert_message():
    txn_hash = "0x36144f609e0fc7afd3cc570d6a54582091642a44c5223a5ad59aa20008dd9577"
    receipt = chain.history[txn_hash]
    actual = receipt.trace.revert_message
    expected = "UniswapV2Router: INSUFFICIENT_OUTPUT_AMOUNT"
    assert actual == expected


def test_return_value():
    txn_hash = "0xe0897d735b67893648b20085ecef16232733425329df844292d5b2774cca436b"
    receipt = chain.history[txn_hash]
    actual = receipt.return_value
    expected = 1244617160572980465
    assert actual == expected
