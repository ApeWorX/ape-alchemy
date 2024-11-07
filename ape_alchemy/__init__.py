from ape import plugins


@plugins.register(plugins.ProviderPlugin)
def providers():
    from .provider import Alchemy
    from ._utils import NETWORKS

    for ecosystem_name in NETWORKS:
        for network_name in NETWORKS[ecosystem_name]:
            yield ecosystem_name, network_name, Alchemy
