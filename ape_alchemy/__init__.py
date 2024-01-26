from ape import plugins

from .provider import Alchemy, AlchemyConfig

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
    for ecosystem_name, networks in NETWORKS.items():
        for network_name in networks:
            yield ecosystem_name, network_name, Alchemy


@plugins.register(plugins.Config)
def config_class():
    yield AlchemyConfig
