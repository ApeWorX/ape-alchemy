import re

import pytest
from ape.exceptions import ContractLogicError
from ape.types import LogFilter
from hexbytes import HexBytes
from requests import HTTPError
from web3.exceptions import ContractLogicError as Web3ContractLogicError

from ape_alchemy.provider import MissingProjectKeyError

TXN_HASH = "0x3cef4aaa52b97b6b61aa32b3afcecb0d14f7862ca80fdc76504c37a9374645c4"


@pytest.fixture
def parity_trace():
    return {
        "action": {
            "from": "0x5cab1e5286529370880776461c53a0e47d74fb63",
            "callType": "call",
            "gas": "0x17e6f0",
            "input": "0x96d373e5",
            "to": "0xc17f2c69ae2e66fd87367e3260412eeff637f70e",
            "value": "0x0",
        },
        "blockHash": "0xa7e0792b07687130af6042d9e295e7a96d83a34f40fe01074348cac5c5dd0699",
        "blockNumber": 15104985,
        "result": {"gasUsed": "0x1562f0", "output": "0x"},
        "subtraces": 1,
        "traceAddress": [],
        "transactionHash": TXN_HASH,
        "transactionPosition": 259,
        "type": "call",
    }


@pytest.fixture
def log_filter():
    return LogFilter(
        address=["0xF7F78379391C5dF2Db5B66616d18fF92edB82022"],
        fromBlock="0x3",
        toBlock="0x3",
        topics=[
            "0x1a7c56fae0af54ebae73bc4699b9de9835e7bb86b050dff7e80695b633f17abd",
            [
                "0x0000000000000000000000000000000000000000000000000000000000000000",
                "0x0000000000000000000000000000000000000000000000000000000000000001",
            ],
        ],
    )


@pytest.fixture
def block():
    return {
        "transactions": [],
        "hash": HexBytes("0xae1960ba0513948a507b652def457305d490d24bc0dd131d8d02be56564a3ee2"),
        "number": 0,
        "parentHash": HexBytes(
            "0x0000000000000000000000000000000000000000000000000000000000000000"
        ),
        "size": 517,
        "timestamp": 1660338772,
        "gasLimit": 30029122,
        "gasUsed": 0,
        "baseFeePerGas": 1000000000,
        "difficulty": 131072,
        "totalDifficulty": 131072,
    }


@pytest.fixture
def receipt():
    return {
        "blockNumber": 15329094,
        "data": b"0xa9059cbb00000000000000000000000016b308eb4591d9b4e34034ca2ff992d224b9927200000000000000000000000000000000000000000000000000000000030a32c0",  # noqa: E501
        "gasLimit": 79396,
        "gasPrice": 14200000000,
        "gasUsed": 65625,
        "logs": [
            {
                "blockHash": HexBytes(
                    "0x141a61b8c738c0f1508728116049a0d4a6ff41ee1180d956148880f32ae99215"
                ),
                "address": "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48",
                "logIndex": 213,
                "data": HexBytes(
                    "0x00000000000000000000000000000000000000000000000000000000030a32c0"
                ),
                "removed": False,
                "topics": [
                    HexBytes("0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"),
                    HexBytes("0x000000000000000000000000958f973513f723f2cb9b47abe5e903695ab93e36"),
                    HexBytes("0x00000000000000000000000016b308eb4591d9b4e34034ca2ff992d224b99272"),
                ],
                "blockNumber": 15329094,
                "transactionIndex": 132,
                "transactionHash": HexBytes(
                    "0x9e4be62c1a16caacaccd9d8c7706b75dc17a957ec6c5dea418a137a5c3a197c5"
                ),
            }
        ],
        "nonce": 16,
        "receiver": "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48",
        "sender": "0x958f973513F723f2cB9b47AbE5e903695aB93e36",
        "status": 1,
        "hash": TXN_HASH,
        "value": 0,
    }


def test_when_no_api_key_raises_error(missing_token, alchemy_provider):
    with pytest.raises(
        MissingProjectKeyError,
        match=re.escape(
            "Must set one of "
            "$WEB3_ALCHEMY_PROJECT_ID, "
            "$WEB3_ALCHEMY_API_KEY, "
            "$WEB3_ETHEREUM_SEPOLIA_ALCHEMY_PROJECT_ID, "
            "$WEB3_ETHEREUM_SEPOLIA_ALCHEMY_API_KEY."
        ),
    ):
        alchemy_provider.connect()


def test_send_transaction_reverts(token, alchemy_provider, mock_web3, transaction):
    expected_revert_message = "EXPECTED REVERT MESSAGE"
    mock_web3.eth.send_raw_transaction.side_effect = Web3ContractLogicError(
        f"execution reverted : {expected_revert_message}"
    )
    alchemy_provider._web3 = mock_web3

    with pytest.raises(ContractLogicError, match=expected_revert_message):
        alchemy_provider.send_transaction(transaction)


def test_send_transaction_reverts_no_message(token, alchemy_provider, mock_web3, transaction):
    mock_web3.eth.send_raw_transaction.side_effect = Web3ContractLogicError("execution reverted")
    alchemy_provider._web3 = mock_web3

    with pytest.raises(ContractLogicError, match="Transaction failed."):
        alchemy_provider.send_transaction(transaction)


def test_estimate_gas_would_revert(token, alchemy_provider, mock_web3, transaction):
    expected_revert_message = "EXPECTED REVERT MESSAGE"
    mock_web3.eth.estimate_gas.side_effect = Web3ContractLogicError(
        f"execution reverted : {expected_revert_message}"
    )
    alchemy_provider._web3 = mock_web3

    with pytest.raises(ContractLogicError, match=expected_revert_message):
        alchemy_provider.estimate_gas_cost(transaction)


def test_estimate_gas_would_revert_no_message(token, alchemy_provider, mock_web3, transaction):
    mock_web3.eth.estimate_gas.side_effect = Web3ContractLogicError("execution reverted")
    alchemy_provider._web3 = mock_web3

    with pytest.raises(ContractLogicError, match="Transaction failed."):
        alchemy_provider.estimate_gas_cost(transaction)


def test_get_contract_logs(networks, alchemy_provider, mock_web3, block, log_filter):
    _ = alchemy_provider.chain_id  # Make sure this has been called _before_ setting mock.
    mock_web3.eth.get_block.return_value = block
    alchemy_provider._web3 = mock_web3
    networks.active_provider = alchemy_provider
    actual = [x for x in alchemy_provider.get_contract_logs(log_filter)]

    # Fails when improper response handling of logs (is part of bug fix)
    assert actual == []


def test_get_transaction_trace(networks, alchemy_provider, mock_web3, parity_trace, receipt):
    mock_web3.provider.make_request.return_value = [parity_trace]
    mock_web3.eth.wait_for_transaction_receipt.return_value = receipt
    alchemy_provider._web3 = mock_web3
    networks.active_provider = alchemy_provider
    trace = alchemy_provider.get_transaction_trace(TXN_HASH)
    actual = repr(trace.get_calltree())
    expected = r"CALL: 0xC17f2C69aE2E66FD87367E3260412EEfF637F70E\.<0x96d373e5\> \[1401584 gas\]"
    assert re.match(expected, actual)


def test_make_request_rate_limiting(mocker, alchemy_provider, mock_web3):
    alchemy_provider._web3 = mock_web3

    class RateLimitTester:
        tries = 2
        _try = 0
        tries_made = 0

        def rate_limit_hook(self, rpc, params):
            self.tries_made += 1
            if self._try == self.tries:
                self._try = 0
                return {"success": True}
            else:
                self._try += 1
                response = mocker.MagicMock()
                response.status_code = 429
                raise HTTPError(response=response)

    rate_limit_tester = RateLimitTester()
    mock_web3.provider.make_request.side_effect = rate_limit_tester.rate_limit_hook
    result = alchemy_provider.make_request("ape_testRateLimiting", parameters=[])
    assert rate_limit_tester.tries_made == rate_limit_tester.tries + 1
    assert result == {"success": True}


def test_make_request_empty_result(alchemy_provider, mock_web3):
    """
    Testing the case when the result is empty that it still returns it
    (and not the raw JSON response).
    """
    alchemy_provider._web3 = mock_web3
    mock_web3.provider.make_request.return_value = {"jsonrpc": "2.0", "id": 8, "result": []}
    result = alchemy_provider.make_request("ape_madeUpRPC", [])
    assert result == []
