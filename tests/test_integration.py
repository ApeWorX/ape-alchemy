import pytest
from ape import networks
from ape.utils import ZERO_ADDRESS

from ape_alchemy.provider import Alchemy


@pytest.mark.parametrize(
    "ecosystem,network",
    [
        ("ethereum", "mainnet"),
        ("ethereum", "goerli"),
        ("arbitrum", "mainnet"),
        ("arbitrum", "goerli"),
        ("optimism", "mainnet"),
        ("optimism", "goerli"),
        ("polygon", "mainnet"),
        ("polygon", "mumbai"),
    ],
)
def test_alchemy(ecosystem, network):
    ecosystem_cls = networks.get_ecosystem(ecosystem)
    network_cls = ecosystem_cls.get_network(network)
    with network_cls.use_provider("alchemy") as provider:
        assert isinstance(provider, Alchemy)
        assert provider.get_balance(ZERO_ADDRESS) > 0
        assert provider.get_block(0)
