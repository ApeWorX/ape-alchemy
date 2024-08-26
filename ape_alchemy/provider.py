import os
from collections.abc import Iterable
from typing import Any, Optional

from ape.api import ReceiptAPI, TraceAPI, TransactionAPI, UpstreamProvider
from ape.exceptions import (
    APINotImplementedError,
    ContractLogicError,
    ProviderError,
    VirtualMachineError,
)
from ape.logging import logger
from ape.types import BlockID
from ape_ethereum.provider import Web3Provider
from ape_ethereum.transactions import AccessList
from eth_pydantic_types import HexBytes
from eth_typing import HexStr
from requests import HTTPError
from web3 import HTTPProvider, Web3
from web3.exceptions import ContractLogicError as Web3ContractLogicError
from web3.gas_strategies.rpc import rpc_gas_price_strategy
from web3.middleware import geth_poa_middleware
from web3.types import RPCEndpoint

from .exceptions import AlchemyFeatureNotAvailable, AlchemyProviderError, MissingProjectKeyError
from .trace import AlchemyTransactionTrace

# The user must either set one of these or an ENV VAR of the pattern:
#  WEB3_<ECOSYSTEM>_<NETWORK>_PROJECT_ID or  WEB3_<ECOSYSTEM>_<NETWORK>_API_KEY
DEFAULT_ENVIRONMENT_VARIABLE_NAMES = ("WEB3_ALCHEMY_PROJECT_ID", "WEB3_ALCHEMY_API_KEY")

# Alchemy will try to publish private transactions for 25 blocks.
PRIVATE_TX_BLOCK_WAIT = 25

NETWORKS_SUPPORTING_WEBSOCKETS = ("ethereum", "arbitrum", "base", "optimism", "polygon")


class Alchemy(Web3Provider, UpstreamProvider):
    """
    A web3 provider using an HTTP connection to Alchemy.

    Docs: https://docs.alchemy.com/alchemy/
    """

    network_uris: dict[tuple, str] = {}

    @property
    def uri(self):
        """
        Alchemy RPC URI, including the project ID.
        """
        ecosystem_name = self.network.ecosystem.name
        network_name = self.network.name
        if (ecosystem_name, network_name) in self.network_uris:
            return self.network_uris[(ecosystem_name, network_name)]

        key = None

        ecosystem_nm_part = ecosystem_name.upper().replace("-", "_")
        network_nm_part = network_name.upper().replace("-", "_")
        expected_env_var_prefix = f"WEB3_{ecosystem_nm_part}_{network_nm_part}_ALCHEMY"
        options = (
            *DEFAULT_ENVIRONMENT_VARIABLE_NAMES,
            f"{expected_env_var_prefix}_PROJECT_ID",
            f"{expected_env_var_prefix}_API_KEY",
        )

        for env_var_name in options:
            env_var = os.environ.get(env_var_name)
            if env_var:
                key = env_var
                break

        if not key:
            raise MissingProjectKeyError(options)

        network_formats_by_ecosystem = {
            "ethereum": "https://eth-{0}.g.alchemy.com/v2/{1}",
            "arbitrum": "https://arb-{0}.g.alchemy.com/v2/{1}",
            "base": "https://base-{0}.g.alchemy.com/v2/{1}",
            "optimism": "https://opt-{0}.g.alchemy.com/v2/{1}",
            "polygon": "https://polygon-{0}.g.alchemy.com/v2/{1}",
            "polygon-zkevm": "https://polygonzkevm-{0}.g.alchemy.com/v2/{1}",
        }

        network_format = network_formats_by_ecosystem[ecosystem_name]
        uri = network_format.format(self.network.name, key)
        self.network_uris[(ecosystem_name, network_name)] = uri
        return uri

    @property
    def http_uri(self) -> str:
        # NOTE: Overriding `Web3Provider.http_uri` implementation
        return self.uri

    @property
    def ws_uri(self) -> str:
        # NOTE: Overriding `Web3Provider.ws_uri` implementation
        return "ws" + self.uri[4:]  # Remove `http` in default URI w/ `ws`

    @property
    def priority_fee(self) -> int:
        if self.network.ecosystem.name == "polygon-zkevm":
            # The error is only 400 with no info otherwise.
            raise APINotImplementedError()

        return super().priority_fee

    @property
    def connection_str(self) -> str:
        return self.uri

    def connect(self):
        self._web3 = Web3(HTTPProvider(self.uri))
        try:
            # Any chain that *began* as PoA needs the middleware for pre-merge blocks
            base = 8453
            optimism = 10
            polygon = 137

            if self._web3.eth.chain_id in (base, optimism, polygon):
                self._web3.middleware_onion.inject(geth_poa_middleware, layer=0)

            self._web3.eth.set_gas_price_strategy(rpc_gas_price_strategy)
        except Exception as err:
            raise ProviderError(f"Failed to connect to Alchemy.\n{repr(err)}") from err

    def disconnect(self):
        self._web3 = None

    def _get_prestate_trace(self, transaction_hash: str) -> dict:
        return self.make_request(
            "debug_traceTransaction", [transaction_hash, {"tracer": "prestateTracer"}]
        )

    def get_transaction_trace(self, transaction_hash: str, **kwargs) -> TraceAPI:
        return AlchemyTransactionTrace(transaction_hash=transaction_hash, **kwargs)

    def get_virtual_machine_error(self, exception: Exception, **kwargs) -> VirtualMachineError:
        txn = kwargs.get("txn")
        if not hasattr(exception, "args") or not len(exception.args):
            return VirtualMachineError(base_err=exception, txn=txn)

        args = exception.args
        message = args[0]
        if (
            not isinstance(exception, Web3ContractLogicError)
            and isinstance(message, dict)
            and "message" in message
        ):
            # Is some other VM error, like gas related
            return VirtualMachineError(message["message"], txn=txn)

        elif not isinstance(message, str):
            return VirtualMachineError(base_err=exception, txn=txn)

        # If get here, we have detected a contract logic related revert.
        message_prefix = "execution reverted"
        if message.startswith(message_prefix):
            message = message.replace(message_prefix, "")

            if ":" in message:
                # Was given a revert message
                message = message.split(":")[-1].strip()
                return ContractLogicError(revert_message=message, txn=txn)
            else:
                # No revert message
                return ContractLogicError(txn=txn)

        return VirtualMachineError(message=message, txn=txn)

    def create_access_list(
        self, transaction: TransactionAPI, block_id: Optional[BlockID] = None
    ) -> list[AccessList]:
        if self.network.ecosystem.name == "polygon-zkevm":
            # The error is only 400 with no info otherwise.
            raise APINotImplementedError()

        return super().create_access_list(transaction, block_id=block_id)

    def make_request(self, rpc: str, parameters: Optional[Iterable] = None) -> Any:
        parameters = parameters or []
        try:
            result = self.web3.provider.make_request(RPCEndpoint(rpc), parameters)
        except HTTPError as err:
            response_data = err.response.json() if err.response else {}
            if "error" not in response_data:
                raise AlchemyProviderError(str(err)) from err

            error_data = response_data["error"]
            message = (
                error_data.get("message", str(error_data))
                if isinstance(error_data, dict)
                else error_data
            )
            cls = (
                AlchemyFeatureNotAvailable
                if "is not available" in message
                else AlchemyProviderError
            )
            raise cls(message) from err

        if isinstance(result, dict) and (res := result.get("result")):
            return res

        return result

    def send_private_transaction(self, txn: TransactionAPI, **kwargs) -> ReceiptAPI:
        """
        See `Alchemy's guide <https://www.alchemy.com/overviews/ethereum-private-transactions>`__
        for more information on sending private transaction using Alchemy.
        For more information on the API itself, see its
        `REST reference <https://docs.alchemy.com/reference/eth-sendprivatetransaction>`__.

        Args:
            txn: (:class:`~ape.api.transactionsTransactionAPI`): The transaction.
            **kwargs: Kwargs here are used for private-transaction "preferences".

        Returns:
            :class:`~ape.api.transactions.ReceiptAPI`
        """
        max_block_number = kwargs.pop("max_block_number", None)

        params = {
            "tx": HexBytes(txn.serialize_transaction()).hex(),
            "maxBlockNumber": max_block_number,
        }
        if kwargs and "fast" not in kwargs:
            # If sending preferences, `fast` must be present.
            kwargs["fast"] = False
            params["preferences"] = kwargs

        try:
            txn_hash = self.make_request("eth_sendPrivateTransaction", [params])
        except (ValueError, Web3ContractLogicError) as err:
            vm_err = self.get_virtual_machine_error(err, txn=txn)
            raise vm_err from err

        # Since Alchemy will attempt to publish for 25 blocks,
        # we add 25 * block_time to the timeout.
        timeout = (
            PRIVATE_TX_BLOCK_WAIT * self.network.block_time
            + self.network.transaction_acceptance_timeout
        )

        receipt = self.get_receipt(
            txn_hash,
            required_confirmations=(
                txn.required_confirmations
                if txn.required_confirmations is not None
                else self.network.required_confirmations
            ),
            timeout=timeout,
        )
        logger.info(
            f"Confirmed {receipt.txn_hash} (private) (total fees paid = {receipt.total_fees_paid})"
        )
        self.chain_manager.history.append(receipt)
        return receipt

    def get_receipt(
        self,
        txn_hash: str,
        required_confirmations: int = 0,
        timeout: Optional[int] = None,
        **kwargs,
    ) -> ReceiptAPI:
        if not required_confirmations and not timeout:
            # Allows `get_receipt` to work better when not sending.
            data = self.web3.eth.get_transaction_receipt(HexStr(txn_hash))
            txn = dict(self.web3.eth.get_transaction(HexStr(txn_hash)))
            return self.network.ecosystem.decode_receipt(
                {
                    "provider": self,
                    "required_confirmations": required_confirmations,
                    **txn,
                    **data,
                }
            )
        # Sending txns will get here because they always pass in required confs.
        return super().get_receipt(
            txn_hash, required_confirmations=required_confirmations, timeout=timeout, **kwargs
        )
