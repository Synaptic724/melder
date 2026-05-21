from typing import List, Optional, Protocol, Tuple, runtime_checkable

InstanceKey = Tuple[str, Optional[int]]


@runtime_checkable
class IParamSource(Protocol):
    """
    Phase-9 parameter source contract.

    Purpose:
        Describe where one constructor parameter obtains its value during
        injection-plan execution.

    Contract:
        - `kind` identifies the source mode for this parameter.
        - `dependency_keys` is present only for dependency-driven resolution.
        - `override_key` is present only for explicit override-driven
          resolution.
        - `contract_key` is present only for SpellContract-driven resolution.
        - Consumers treat this object as immutable after build.
    """

    @property
    def kind(self) -> str:
        """
        Return the source mode for this parameter.
        """
        ...

    @property
    def dependency_keys(self) -> Optional[List[InstanceKey]]:
        """
        Return dependency instance keys for this parameter, if any.
        """
        ...

    @property
    def override_key(self) -> Optional[str]:
        """
        Return the override key for this parameter, if any.
        """
        ...

    @property
    def contract_key(self) -> Optional[str]:
        """
        Return the SpellContract key for this parameter, if any.
        """
        ...

