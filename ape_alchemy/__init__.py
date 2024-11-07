from ape import plugins


@plugins.register(plugins.ProviderPlugin)
def providers():
    from ._utils import NETWORKS
    from .provider import Alchemy

    for ecosystem_name in NETWORKS:
        for network_name in NETWORKS[ecosystem_name]:
            yield ecosystem_name, network_name, Alchemy
