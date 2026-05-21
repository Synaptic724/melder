from typing import Any, Dict, List, Optional, Protocol, runtime_checkable
from melder.utilities.interfaces.icleanable import ICleanable

@runtime_checkable
class IWorkstation(ICleanable, Protocol):
    """
    Interface for the room-local workstation canvas.
    """

    @property
    def workstation_id(self) -> str:
        """
        Return the stable workstation identifier.
        """
        ...

    @property
    def owner_space_id(self) -> str:
        """
        Return the owning room identifier.
        """
        ...

    def bind_object(
            self,
            name: str,
            value: object,
            *,
            weak_ref: Optional[bool] = None,
    ) -> None:
        """
        Store one object binding by name.
        """
        ...

    def bind_attribute(
            self,
            name: str,
            value: object,
            *,
            weak_ref: Optional[bool] = None,
    ) -> None:
        """
        Store one attribute/value binding by name.
        """
        ...

    def bind_method(
            self,
            name: str,
            value: object,
            *,
            weak_ref: Optional[bool] = None,
    ) -> None:
        """
        Store one method/callable binding by name.
        """
        ...

    def get(self, name: str, *, store: Optional[str] = None) -> object:
        """
        Return one saved binding by name.
        """
        ...

    def release(self, name: str, *, store: Optional[str] = None) -> object:
        """
        Remove one saved binding and return the removed value.
        """
        ...

    def describe_bindings(self) -> Dict[str, List[str]]:
        """
        Return a detached summary of saved binding names by store.
        """
        ...

    def set_target(self, name: str, *, store: Optional[str] = None) -> None:
        """
        Select one saved binding as the active target.
        """
        ...

    def get_target(self) -> object:
        """
        Return the current active target value.
        """
        ...

    def clear_target(self) -> None:
        """
        Clear the current active-target selection only.
        """
        ...

    def cleanup_target(self, *method_names: str) -> None:
        """
        Call cleanup methods on the current target and then clear target selection.
        """
        ...

    def call_target(
            self,
            *args: Any,
            bind_as_name: Optional[str] = None,
            bind_as_store: str = "objects",
            **kwargs: Any
    ) -> object:
        """
        Invoke the current target and optionally bind the return value.
        """
        ...

