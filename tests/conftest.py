import ape
import pytest
from ape.api import TransactionAPI
from requests import HTTPError, Response
from web3 import Web3

from ape_alchemy.providers import AlchemyEthereumProvider

FEATURE_NOT_AVAILABLE_BECAUSE_OF_TIER_RESPONSE = (
    "trace_transaction is not available on the Free tier - "
    "upgrade to Growth or Enterprise for access. See available methods at "
    "https://docs.alchemy.com/alchemy/documentation/apis"
)
FEATURE_NOT_AVAILABLE_BECAUSE_OF_NETWORK_RESPONSE = (
    "trace_transaction is not available on the ETH_RINKEBY. "
    "For more information see our docs: "
    "https://docs.alchemy.com/alchemy/documentation/apis/ethereum"
)


@pytest.fixture
def networks():
    return ape.networks


@pytest.fixture
def missing_token(mocker):
    mock = mocker.patch("os.environ.get")
    mock.return_value = None
    return mock


@pytest.fixture
def token(mocker):
    mock = mocker.patch("os.environ.get")
    mock.return_value = "TEST_TOKEN"
    return mock


@pytest.fixture
def mock_web3(mocker):
    mock = mocker.MagicMock(spec=Web3)
    mock.eth = mocker.MagicMock()
    mock.manager = mocker.MagicMock()
    return mock


@pytest.fixture
def mock_transaction(mocker):
    return mocker.MagicMock(spec=TransactionAPI)


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
def alchemy_provider(networks) -> AlchemyEthereumProvider:
    return networks.get_provider_from_choice("ethereum:rinkeby:alchemy")
