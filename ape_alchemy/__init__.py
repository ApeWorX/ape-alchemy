from ape import plugins


@plugins.register(plugins.Config)
def config_class():
    from .config import AlchemyConfig

    return AlchemyConfig


@plugins.register(plugins.ProviderPlugin)
def providers():
    from ._utils import NETWORKS
    from .provider import Alchemy

    for ecosystem_name in NETWORKS:
        for network_name in NETWORKS[ecosystem_name]:
            yield ecosystem_name, network_name, Alchemy


def __getattr__(name: str):
    if name == "NETWORKS":
        from ._utils import NETWORKS

        return NETWORKS

    elif name == "Alchemy":
        from .provider import Alchemy

        return Alchemy

    elif name == "AlcheymyConfig":
        from .config import AlchemyConfig

        return AlchemyConfig

    raise AttributeError(name)


__all__ = [
    "NETWORKS",
    "Alchemy",
    "AlchemyConfig",
]
