import os
from typing import TYPE_CHECKING

import ape
import pytest
from requests import HTTPError, Response
from web3 import Web3

if TYPE_CHECKING:
    from ape_alchemy.provider import Alchemy

FEATURE_NOT_AVAILABLE_BECAUSE_OF_TIER_RESPONSE = (
    "trace_transaction is not available on the Free tier - "
    "upgrade to Growth or Enterprise for access. See available methods at "
    "https://docs.alchemy.com/alchemy/documentation/apis"
)
FEATURE_NOT_AVAILABLE_BECAUSE_OF_NETWORK_RESPONSE = (
    "trace_transaction is not available on the ETH_SEPOLIA. "
    "For more information see our docs: "
    "https://docs.alchemy.com/alchemy/documentation/apis/ethereum"
)


@pytest.fixture
def accounts():
    return ape.accounts


@pytest.fixture
def networks():
    return ape.networks


@pytest.fixture
def missing_token(alchemy_provider, mocker):
    env = os.environ.copy()
    mock = mocker.patch("os.environ.get")

    def side_effect(key, *args, **kwargs):
        return None if "WEB3" in key else env.get(key, *args, **kwargs)

    alchemy_provider.network_uris = {}
    mock.side_effect = side_effect
    return mock


@pytest.fixture
def token(mocker):
    env = os.environ.copy()
    mock = mocker.patch("os.environ.get")

    def side_effect(key, *args, **kwargs):
        return "TEST_TOKEN" if "WEB3" in key else env.get(key, *args, **kwargs)

    mock.side_effect = side_effect
    return mock


@pytest.fixture
def mock_web3(mocker):
    mock = mocker.MagicMock(spec=Web3)
    mock.eth = mocker.MagicMock()
    mock.manager = mocker.MagicMock()
    return mock


@pytest.fixture
def transaction(accounts, networks):
    with networks.ethereum.local.use_provider("test"):
        sender = accounts.test_accounts[0]
        receiver = accounts.test_accounts[1]
        receipt = sender.transfer(receiver, "1 gwei")
        return receipt.transaction


@pytest.fixture
def txn_hash():
    return "0x55d07ce5e3f4f5742f3318cf328d700e43ee8cdb46000f2ac731a9379fca8ea7"


@pytest.fixture(
    params=(
        FEATURE_NOT_AVAILABLE_BECAUSE_OF_TIER_RESPONSE,
        FEATURE_NOT_AVAILABLE_BECAUSE_OF_NETWORK_RESPONSE,
    )
)
def feature_not_available_http_error(mocker, request):
    response = mocker.MagicMock(spec=Response)
    response.fixture_param = request.param  # For assertions
    response.json.return_value = {"error": {"message": request.param}}
    error = HTTPError(response=response)
    return error


@pytest.fixture
def alchemy_provider(networks) -> "Alchemy":
    return networks.ethereum.sepolia.get_provider("alchemy")
