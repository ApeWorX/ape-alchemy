from ape import plugins

from .providers import AlchemyEthereumProvider

NETWORKS = {
    "ethereum": [
        "mainnet",
        "ropsten",
        "rinkeby",
        "kovan",
        "goerli",
    ],
    "arbitrum": [
        "mainnet",
        "testnet",
    ],
}


@plugins.register(plugins.ProviderPlugin)
def providers():
    for ecosystem_name in NETWORKS:
        for network_name in NETWORKS[ecosystem_name]:
            yield ecosystem_name, network_name, AlchemyEthereumProvider
