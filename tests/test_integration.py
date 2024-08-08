import pytest
import websocket  # type: ignore
from ape import accounts, networks
from ape.exceptions import APINotImplementedError
from ape.utils import ZERO_ADDRESS

from ape_alchemy import NETWORKS
from ape_alchemy.provider import NETWORKS_SUPPORTING_WEBSOCKETS, Alchemy


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
    if provider.network.ecosystem.name not in NETWORKS_SUPPORTING_WEBSOCKETS:
        # Test will fail. Network does not support ws clients.
        return

    assert provider.ws_uri.startswith("wss")

    try:
        ws = websocket.WebSocket()
        ws.connect(provider.ws_uri)
        ws.close()

    except Exception as err:
        pytest.fail(f"Websocket URI not accessible. Reason: {err}")


def test_polygon_zkevm():
    # We noticed strange behavior on this network and thus called for more tests.
    with networks.polygon_zkevm.cardona.use_provider("alchemy") as provider:
        with pytest.raises(APINotImplementedError):
            _ = provider.priority_fee

        receiver = accounts.test_accounts[0]
        tx = provider.network.ecosystem.create_transaction(receiver=receiver)
        with pytest.raises(APINotImplementedError):
            _ = provider.create_access_list(tx)


def test_make_requeset_handles_result():
    """
    There was a bug where eth_call because ape-alchemy wasn't
    handling the result from make_request properly.
    """
    tx = {
        "to": "0x5576815a38A3706f37bf815b261cCc7cCA77e975",
        "value": "0x0",
        "data": "0x70a082310000000000000000000000005576815a38a3706f37bf815b261ccc7cca77e975",
    }
    with networks.polygon_zkevm.cardona.use_provider("alchemy") as provider:
        result = provider.make_request("eth_call", [tx, "latest"])
        assert not isinstance(result, dict)
