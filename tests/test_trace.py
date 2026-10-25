import pytest
from ape import chain, networks
from ape.exceptions import ChainError, ProviderError
from ethpm_types import ContractType

from ape_alchemy.exceptions import AlchemyFeatureNotAvailable


@pytest.fixture(autouse=True)
def ethereum_mainnet_alchemy():
    try:
        with networks.ethereum.mainnet.use_provider("alchemy"):
            yield
    except Exception as err:
        msg = str(err).lower()
        if any(n in msg for n in ("429", "too many requests", "rate limit")):
            pytest.skip(str(err))
        raise


def test_revert_message():
    txn_hash = "0x36144f609e0fc7afd3cc570d6a54582091642a44c5223a5ad59aa20008dd9577"
    try:
        receipt = chain.history[txn_hash]
        actual = receipt.trace.revert_message
    except (AlchemyFeatureNotAvailable, ProviderError, ChainError, KeyError) as err:
        pytest.skip(str(err))
    expected = "UniswapV2Router: INSUFFICIENT_OUTPUT_AMOUNT"
    assert actual == expected


def test_return_value():
    txn_hash = "0xe0897d735b67893648b20085ecef16232733425329df844292d5b2774cca436b"
    try:
        receipt = chain.history[txn_hash]
    except (ChainError, ProviderError, KeyError) as err:
        pytest.skip(str(err))

    # Ensure the ABI is cached so we can decode the return value.
    abi = [
        {
            "type": "function",
            "name": "submit",
            "stateMutability": "payable",
            "inputs": [{"name": "_referral", "type": "address"}],
            "outputs": [{"name": "", "type": "uint256"}],
        }
    ]
    chain.contracts[receipt.receiver] = ContractType(abi=abi)

    try:
        actual = receipt.return_value
    except (AlchemyFeatureNotAvailable, ProviderError, ChainError) as err:
        pytest.skip(str(err))
    expected = 1244617160572980465
    assert actual == expected
