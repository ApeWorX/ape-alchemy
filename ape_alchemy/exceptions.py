from ape.exceptions import ProviderError


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
    """
    An error raised when there is no API key set.
    """

    def __init__(self, options: tuple[str, ...]):
        env_var_str = ", ".join([f"${n}" for n in options])
        super().__init__(f"Must set one of {env_var_str}.")
