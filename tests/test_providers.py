import pytest
from ape.exceptions import ContractLogicError
from web3.exceptions import ContractLogicError as Web3ContractLogicError

from ape_alchemy.providers import AlchemyFeatureNotAvailable, MissingProjectKeyError


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
        mock_web3.provider.make_request.side_effect = feature_not_available_http_error
        alchemy_provider._web3 = mock_web3

        with pytest.raises(AlchemyFeatureNotAvailable) as err:
            _ = [t for t in alchemy_provider.get_transaction_trace(txn_hash)]

        assert str(err.value) == feature_not_available_http_error.response.fixture_param
