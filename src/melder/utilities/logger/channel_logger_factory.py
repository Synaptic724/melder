from typing import Any, Dict, Iterable, Optional, Union, Callable
from melder.utilities.general_base.cleanable import Cleanable
from melder.utilities.logger.safe_logger import SafeLogger

class IrisLoggerFactory(Cleanable):
    """
    Minimal adapter that exposes the **same call shape** as your `resolve_channel_logger`
    which is from the InitHelpers module in Commandops.

    Purpose:
        - Let you pass a resolver function (e.g., `resolve_channel_logger`) into places
          that expect a "factory" object.
        - Avoids extra logic or policy: zero transformation, zero defaults, zero magic.

    Contract:
        - The resolver you provide MUST accept the same keyword parameters documented
          below and return either a `ChannelLogger` or a `SafeLogger`.

    Example:
        >>> factory = iris_logger_factory(resolve_channel_logger)
        >>> logger = factory(
        ...     registrant=conduit,
        ...     channels="frame.Conduit[123]",
        ...     groups=["frame:default", "type:Conduit"],
        ...     system_groups=["audit"],
        ...     props={"frame": "default", "id": "123"},
        ... )
        >>> logger.info("it works")
    """

    def __init__(self, resolve_fn: Callable[..., Any]):
        """
        Initialize the adapter.

        Args:
            resolve_fn: A callable compatible with your `resolve_channel_logger`
                        signature. It will be called directly—no wrapping/alteration.
        """
        super().__init__()
        self._resolve_fn = resolve_fn

    def cleanup(self):
        if hasattr(self._resolve_fn, "cleanup"):
            self._resolve_fn.cleanup()
        self._resolve_fn = None

    def __call__(
            self,
            registrant: object,
            *,
            groups: Optional[Iterable[str]] = None,
            system_groups: Optional[Iterable[str]] = None,
            props: Optional[Dict[str, Any]] = None,
            channels: Optional[Union[str, Iterable[str]]] = None,
    ) -> Any:
        """
        Forward the request to the underlying resolver, unchanged.

        Args:
            registrant: The object requesting the logger (e.g., Spellbook/Conduit/Ward).
                        Must expose the identity you rely on (e.g., `_id`) if your
                        resolver expects it.
            groups: Optional iterable of group tags to associate with the logger.
            system_groups: Optional iterable of **system** group tags (reserved semantics).
            props: Optional structured property dictionary to attach as metadata.
            channels: A channel name or iterable of channel names for routing.

        Returns:
            Whatever the resolver returns, typically a `ChannelLogger` (Iris) or
            a `SafeLogger` fallback.

        Notes:
            - This method does NOT validate or mutate inputs.
            - Any exceptions raised by `resolve_fn` will propagate unless your resolver
              handles them internally.
        """
        return SafeLogger(self._resolve_fn(
            registrant=registrant,
            groups=groups,
            system_groups=system_groups,
            props=props,
            channels=channels,
        ))
