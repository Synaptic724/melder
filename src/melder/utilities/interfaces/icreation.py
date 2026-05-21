from typing import Any, Protocol, runtime_checkable
from melder.utilities.interfaces.icleanable import ICleanable


@runtime_checkable
class ICreation(ICleanable, Protocol):
    """
    Wrapper for one live runtime object tracked by `Creations`.

    `Creation` is the small ownership shell around an instantiated object. It
    gives the runtime a stable identity, stores disposal metadata derived from
    the originating spell, and lets the larger `Creations` manager handle
    registration, extraction, restoration, and ordered disposal.

    Contract:
    - The wrapper owns metadata about disposal, not disposal policy itself.
    - `cleanup()` clears the wrapper's references but does not call
      `cleanup()` / `close()` / `dispose()` on the wrapped object.
    - The actual disposal decision belongs to `Creations`.
    """

    def cleanup(self) -> None:
        """
        Release the wrapper's references without disposing of the wrapped object.

        Contract:
        - Idempotent and lock-protected.
        - Does not call disposal methods on the underlying value.
        - Only clears wrapper-held references so the higher-level `Creations`
          manager can own the actual disposal policy.
        """
        ...

    @property
    def id(self) -> str:
        """
        Return the stable ULID assigned to this wrapper.
        """
        ...

    @property
    def value(self) -> Any:
        """
        Return the wrapped runtime object.
        """
        ...

    @property
    def has_disposal_methods(self) -> bool | None:
        """
        Return whether the originating spell declared disposal methods.

        Contract:
            - True/False while the Creation is active.
            - None after cleanup.
        """
        ...

    @property
    def disposal_method_names(self) -> list[str] | None:
        """
        Return the ordered disposal method names recorded for this Creation.

        Contract:
            - List of method names while the Creation is active.
            - None after cleanup.
        """
        ...
