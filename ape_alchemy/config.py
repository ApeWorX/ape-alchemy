from ape.api import PluginConfig


class RateLimitConfig(PluginConfig):
    """
    Configuration for rate limiting.

    Args:
        min_retry_delay (int): The amount of milliseconds to wait before
          retrying the request. Defaults to ``1_000`` (one second).
        retry_backoff_factor (int): The multiplier applied to the retry delay
          after each failed attempt. Defaults to ``2``.
        max_retry_delay (int): The maximum length of the retry delay.
          Defaults to ``30_000`` (30 seconds).
        max_retries (int): The maximum number of retries.
          Defaults to ``3``.
        retry_jitter (int): A random number of milliseconds up to this limit
          is added to each retry delay. Defaults to ``250`` milliseconds.
    """

    min_retry_delay: int = 1_000
    retry_backoff_factor: int = 2
    max_retry_delay: int = 30_000
    max_retries: int = 3
    retry_jitter: int = 250


class AlchemyConfig(PluginConfig):
    """
    Configuration for Alchemy.

    Args:
        rate_limit (RateLimitConfig): The rate limiting configuration.
        trace_timeout (int): The maximum amount of milliseconds to wait for a
          trace. Defaults to ``10_000`` (10 seconds).
    """

    rate_limit: RateLimitConfig = RateLimitConfig()
    trace_timeout: str = "10s"
