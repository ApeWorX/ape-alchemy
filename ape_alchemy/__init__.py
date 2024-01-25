from ape import plugins

from .provider import Alchemy

NETWORKS = {
    "ethereum": [
        "mainnet",
        "goerli",
        "sepolia",
    ],
    "arbitrum": [
        "mainnet",
        "goerli",
        "sepolia",
    ],
    "base": [
        "mainnet",
        "goerli",
        "sepolia",
    ],
    "optimism": [
        "mainnet",
        "goerli",
        "sepolia",
    ],
    "polygon": [
        "mainnet",
        "mumbai",
    ],
}


@plugins.register(plugins.ProviderPlugin)
def providers():
    for ecosystem_name in NETWORKS:
        for network_name in NETWORKS[ecosystem_name]:
            yield ecosystem_name, network_name, Alchemy
