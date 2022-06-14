from pathlib import Path

import pytest
from ape.api import NetworkAPI, TransactionAPI
from ape.api.config import PluginConfig
from ape.exceptions import ContractLogicError
from requests import HTTPError, Response
from web3 import Web3
from web3.exceptions import ContractLogicError as Web3ContractLogicError

from ape_alchemy.providers import (
    AlchemyEthereumProvider,
    AlchemyFeatureNotAvailable,
    MissingProjectKeyError,
)

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
def mock_network(mocker):
    mock = mocker.MagicMock(spec=NetworkAPI)
    mock.name = "MOCK_NETWORK"
    return mock


@pytest.fixture
def mock_config(mocker):
    return mocker.MagicMock(spec=PluginConfig)


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
def alchemy_provider(mock_network, mock_config) -> AlchemyEthereumProvider:
    return AlchemyEthereumProvider(
        name="alchemy",
        network=mock_network,
        config=mock_config,
        request_header={},
        data_folder=Path("."),
        provider_settings={},
    )


class TestAlchemyEthereumProvider:
    def test_when_no_api_key_raises_error(self, missing_token, alchemy_provider):
        with pytest.raises(MissingProjectKeyError) as err:
            alchemy_provider.connect()

        expected = "Must set one of $WEB3_ALCHEMY_PROJECT_ID, $WEB3_ALCHEMY_API_KEY."
        assert expected in str(err.value)

    def test_send_transaction_reverts(self, token, alchemy_provider, mock_web3, mock_transaction):
        expected_revert_message = "EXPECTED REVERT MESSAGE"
        mock_web3.eth.send_raw_transaction.side_effect = Web3ContractLogicError(
            f"execution reverted : {expected_revert_message}"
        )
        alchemy_provider._web3 = mock_web3

        with pytest.raises(ContractLogicError) as err:
            alchemy_provider.send_transaction(mock_transaction)

        assert err.value.revert_message == expected_revert_message

    def test_send_transaction_reverts_no_message(
        self, token, alchemy_provider, mock_web3, mock_transaction
    ):
        mock_web3.eth.send_raw_transaction.side_effect = Web3ContractLogicError(
            "execution reverted"
        )
        alchemy_provider._web3 = mock_web3

        with pytest.raises(ContractLogicError):
            alchemy_provider.send_transaction(mock_transaction)

    def test_estimate_gas_would_revert(self, token, alchemy_provider, mock_web3, mock_transaction):
        expected_revert_message = "EXPECTED REVERT MESSAGE"
        mock_web3.eth.estimate_gas.side_effect = Web3ContractLogicError(
            f"execution reverted : {expected_revert_message}"
        )
        alchemy_provider._web3 = mock_web3

        with pytest.raises(ContractLogicError) as err:
            alchemy_provider.estimate_gas_cost(mock_transaction)

        assert err.value.revert_message == expected_revert_message

    def test_estimate_gas_would_revert_no_message(
        self, token, alchemy_provider, mock_web3, mock_transaction
    ):
        mock_web3.eth.estimate_gas.side_effect = Web3ContractLogicError("execution reverted")
        alchemy_provider._web3 = mock_web3

        with pytest.raises(ContractLogicError):
            alchemy_provider.estimate_gas_cost(mock_transaction)

    def test_feature_not_available(
        self, token, alchemy_provider, mock_web3, txn_hash, feature_not_available_http_error
    ):
        mock_web3.manager.request_blocking.side_effect = feature_not_available_http_error
        alchemy_provider._web3 = mock_web3

        with pytest.raises(AlchemyFeatureNotAvailable) as err:
            _ = [t for t in alchemy_provider.get_transaction_trace(txn_hash)]

        assert str(err.value) == feature_not_available_http_error.response.fixture_param
