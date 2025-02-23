import pytest
import websocket  # type: ignore
from ape import accounts, networks
from ape.exceptions import APINotImplementedError, TransactionNotFoundError
from ape.utils import ZERO_ADDRESS

from ape_alchemy._utils import NETWORKS
from ape_alchemy.provider import Alchemy

# These networks have badly formatted responses at the moment and cause test failures.
# TODO: Figure out how to re-gain support here.
NETWORK_SKIPS = ("flow-evm:testnet",)

# Using this to pytest node names are clearer.
NETWORK_KEY_MAP = [
    f"{eco_name}:{net_name}"
    for eco_name, network_data in NETWORKS.items()
    for net_name in network_data
    if f"{eco_name}:{net_name}" not in NETWORK_SKIPS
]


@pytest.fixture(params=NETWORK_KEY_MAP)
def provider(request):
    eco_name, net_name = request.param.split(":")
    ecosystem_cls = networks.get_ecosystem(eco_name)
    network_cls = ecosystem_cls.get_network(net_name)
    with network_cls.use_provider("alchemy") as provider:
        yield provider


def test_http(provider):
    assert isinstance(provider, Alchemy)
    assert provider.http_uri.startswith("https")

    # NOTE: Sometimes the balance is 0, for some chains.
    assert provider.get_balance(ZERO_ADDRESS) is not None
    assert provider.get_block(0)
    assert provider.get_block("latest")


def test_ws(provider):
    ws_uri = provider.ws_uri
    if ws_uri is None:
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


def test_make_request_handles_result():
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


def test_get_receipt():
    with networks.ethereum.sepolia.use_provider("alchemy") as alchemy:
        txn_hash = "0x68605140856c13038d325048c411aed98cc1eecc189f628a38edb597f6b9679e"
        existing_tx = alchemy.get_receipt(txn_hash)
        assert existing_tx.txn_hash == txn_hash

        txn_hash = "0x66600044856c13038d325048c411aed98cc1eecc189f628a38eeeeeeeeeeeeee"
        with pytest.raises(TransactionNotFoundError):
            _ = alchemy.get_receipt(txn_hash)
