import pytest
import websocket  # type: ignore
from ape import networks
from ape.utils import ZERO_ADDRESS

from ape_alchemy import NETWORKS
from ape_alchemy.provider import Alchemy


@pytest.fixture(params=[(name, net) for name, values in NETWORKS.items() for net in values])
def provider(request):
    ecosystem_cls = networks.get_ecosystem(request.param[0])
    network_cls = ecosystem_cls.get_network(request.param[1])
    with network_cls.use_provider("alchemy") as provider:
        yield provider


def test_http(provider):
    assert isinstance(provider, Alchemy)
    assert provider.http_uri.startswith("https")
    assert provider.get_balance(ZERO_ADDRESS) > 0
    assert provider.get_block(0)


def test_ws(provider):
    assert provider.ws_uri.startswith("wss")

    try:
        ws = websocket.WebSocket()
        ws.connect(provider.ws_uri)
        ws.close()

    except Exception as err:
        pytest.fail(f"Websocket URI not accessible. Reason: {err}")
