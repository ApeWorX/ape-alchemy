import os
from typing import Any, Dict, Iterator, Tuple

from ape.api import UpstreamProvider, Web3Provider
from ape.exceptions import ContractLogicError, ProviderError, VirtualMachineError
from evm_trace import CallTreeNode, ParityTraceList, TraceFrame, get_calltree_from_parity_trace
from requests import HTTPError
from web3 import HTTPProvider, Web3  # type: ignore
from web3.exceptions import ContractLogicError as Web3ContractLogicError
from web3.gas_strategies.rpc import rpc_gas_price_strategy
from web3.middleware import geth_poa_middleware

_ETH_ENVIRONMENT_VARIABLE_NAMES = ("WEB3_ALCHEMY_PROJECT_ID", "WEB3_ALCHEMY_API_KEY")
_ARB_ENVIRONMENT_VARIABLE_NAMES = (
    "WEB3_ARBITRUM_ALCHEMY_PROJECT_ID",
    "WEB3_ARBITRUM_ALCHEMY_API_KEY",
)


class AlchemyProviderError(ProviderError):
    """
    An error raised by the Alchemy provider plugin.
    """


class AlchemyFeatureNotAvailable(AlchemyProviderError):
    """
    An error raised when trying to use a feature that is unavailable
    on the user's tier or network.
    """


class MissingProjectKeyError(AlchemyProviderError):
    def __init__(self, options: Tuple[str, ...]):
        env_var_str = ", ".join([f"${n}" for n in options])
        super().__init__(f"Must set one of {env_var_str}.")


class AlchemyEthereumProvider(Web3Provider, UpstreamProvider):
    """
    A web3 provider using an HTTP connection to Alchemy.

    Docs: https://docs.alchemy.com/alchemy/
    """

    network_uris: Dict[tuple, str] = {}

    @property
    def uri(self):
        ecosystem_name = self.network.ecosystem.name
        network_name = self.network.name
        if (ecosystem_name, network_name) in self.network_uris:
            return self.network_uris[(ecosystem_name, network_name)]

        key = None

        options_by_ecosystem = {
            "ethereum": _ETH_ENVIRONMENT_VARIABLE_NAMES,
            "arbitrum": _ARB_ENVIRONMENT_VARIABLE_NAMES,
        }
        options = options_by_ecosystem[ecosystem_name]
        for env_var_name in options:
            env_var = os.environ.get(env_var_name)
            if env_var:
                key = env_var
                break

        if not key:
            raise MissingProjectKeyError(options)

        network_formats_by_ecosystem = {
            "ethereum": "https://eth-{0}.alchemyapi.io/v2/{1}",
            "arbitrum": "https://arb-{0}.g.alchemy.com/v2/{1}",
        }

        network_format = network_formats_by_ecosystem[ecosystem_name]
        uri = network_format.format(self.network.name, key)
        self.network_uris[(ecosystem_name, network_name)] = uri
        return uri

    @property
    def connection_str(self) -> str:
        return self.uri

    def connect(self):
        self._web3 = Web3(HTTPProvider(self.uri))
        try:
            if self._web3.eth.chain_id in (4, 5, 42):
                self._web3.middleware_onion.inject(geth_poa_middleware, layer=0)
            self._web3.eth.set_gas_price_strategy(rpc_gas_price_strategy)
        except Exception as err:
            raise ProviderError(f"Failed to connect to Alchemy.\n{repr(err)}") from err

    def disconnect(self):
        self._web3 = None

    def get_transaction_trace(self, txn_hash: str) -> Iterator[TraceFrame]:
        result = self._make_request("debug_traceTransaction", [txn_hash])
        frames = result.get("structLogs", [])
        for frame in frames:
            yield TraceFrame(**frame)

    def get_call_tree(self, txn_hash: str) -> CallTreeNode:
        receipt = self.get_transaction(txn_hash)
        raw_trace_list = self._make_request("trace_transaction", [txn_hash])
        trace_list = ParityTraceList.parse_obj(raw_trace_list)
        return get_calltree_from_parity_trace(trace_list, gas_cost=receipt.gas_used)

    def get_virtual_machine_error(self, exception: Exception) -> VirtualMachineError:
        if not hasattr(exception, "args") or not len(exception.args):
            return VirtualMachineError(base_err=exception)

        args = exception.args
        message = args[0]
        if (
            not isinstance(exception, Web3ContractLogicError)
            and isinstance(message, dict)
            and "message" in message
        ):
            # Is some other VM error, like gas related
            return VirtualMachineError(message=message["message"])

        elif not isinstance(message, str):
            return VirtualMachineError(base_err=exception)

        # If get here, we have detected a contract logic related revert.
        message_prefix = "execution reverted"
        if message.startswith(message_prefix):
            message = message.replace(message_prefix, "")

            if ":" in message:
                # Was given a revert message
                message = message.split(":")[-1].strip()
                return ContractLogicError(revert_message=message)
            else:
                # No revert message
                return ContractLogicError()

        return VirtualMachineError(message=message)

    def _make_request(self, endpoint: str, parameters: list) -> Any:
        try:
            return super()._make_request(endpoint, parameters)
        except HTTPError as err:
            response_data = err.response.json()
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
