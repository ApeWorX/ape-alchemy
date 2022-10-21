from ape import plugins

from .provider import Alchemy

NETWORKS = {
    "ethereum": [
        "mainnet",
        "goerli",
    ],
    "arbitrum": [
        "mainnet",
        "goerli",
    ],
    "optimism": [
        "mainnet",
        "goerli",
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
