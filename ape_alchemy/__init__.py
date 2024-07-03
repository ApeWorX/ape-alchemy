from ape import plugins

from .provider import Alchemy

NETWORKS = {
    "ethereum": [
        "mainnet",
        "sepolia",
    ],
    "arbitrum": [
        "mainnet",
        "sepolia",
    ],
    "base": [
        "mainnet",
        "sepolia",
    ],
    "optimism": [
        "mainnet",
        "sepolia",
    ],
    "polygon": [
        "mainnet",
        "amoy",
    ],
    "polygon-zkevm": [
        "mainnet",
        "cardona",
    ],
}


@plugins.register(plugins.ProviderPlugin)
def providers():
    for ecosystem_name in NETWORKS:
        for network_name in NETWORKS[ecosystem_name]:
            yield ecosystem_name, network_name, Alchemy
