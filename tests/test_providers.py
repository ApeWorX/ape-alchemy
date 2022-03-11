from pathlib import Path

import pytest
from ape.api import NetworkAPI, TransactionAPI
from ape.api.config import PluginConfig
from ape.exceptions import ContractLogicError
from web3 import Web3
from web3.exceptions import ContractLogicError as Web3ContractLogicError

from ape_alchemy.providers import AlchemyEthereumProvider, MissingProjectKeyError


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
    return mock


@pytest.fixture
def mock_transaction(mocker):
    return mocker.MagicMock(spec=TransactionAPI)


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

        assert "Must set one of $WEB3_ALCHEMY_PROJECT_ID, $WEB3_ALCHEMY_API_KEY." in str(err.value)

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
