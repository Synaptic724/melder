from typing import Any, Dict, Mapping, Optional, Protocol, runtime_checkable

from melder.utilities.interfaces.iparamsource import IParamSource


@runtime_checkable
class IInjectionSpec(Protocol):
    """
    Phase-9 injection specification contract for one instance key.

    Purpose:
        Expose the per-parameter source metadata and override payload attached
        to one planned instance.

    Contract:
        - `param_sources` maps parameter names to immutable `IParamSource`
          descriptors.
        - `allow_list_aggregation` reports whether any parameter uses
          multi-value dependency aggregation.
        - `uses_positional_override` reports whether `contract_payload`
          contains a positional `__args__` override.
        - `contract_payload` is optional and, when present, is treated as
          read-only by consumers.
    """

    @property
    def param_sources(self) -> Mapping[str, IParamSource]:
        """
        Return the parameter-source mapping for this instance.
        """
        ...

    @property
    def allow_list_aggregation(self) -> bool:
        """
        Return whether list-style dependency aggregation is enabled.
        """
        ...

    @property
    def uses_positional_override(self) -> bool:
        """
        Return whether positional contract overrides are enabled.
        """
        ...

    @property
    def contract_payload(self) -> Optional[Dict[str, Any]]:
        """
        Return the optional contract override payload for this instance.
        """
        ...

