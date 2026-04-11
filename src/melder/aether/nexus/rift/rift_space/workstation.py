from typing import Any, Dict, List, Optional, Tuple

from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg
from melder.utilities.general_base.cleanable import Cleanable
from melder.utilities.helpers.id_builder import IDBuilder


class Workstation(Cleanable):
    """
    Internal

    Room-local binding canvas owned by one `RiftSpace`.

    Purpose:
        Provide the local operating canvas inside one room where saved objects,
        saved attribute/value bindings, saved method/callable bindings, and the
        active target can be retained across steps.

    Contract:
        - Stores only room-local bindings; it does not discover or resolve
          new targets from Melder/Nexus.
        - Keeps object, attribute/value, and method/callable bindings in
          separate stores.
        - Tracks at most one active target binding at a time.
        - `cleanup_target(...)` acts only on the currently selected target and
          then clears target selection.
        - `call_target(...)` invokes the currently selected callable target and
          may bind the return value back into the workstation.
        - Cleanup clears workstation-owned binding state but does not attempt
          to cleanup every stored binding automatically.

    Lifecycle:
        Owned by one `RiftSpace`. Cleanup is idempotent and clears binding
        stores plus active-target state.
    """

    __melder_internal__ = _mrg.sentinel
    __slots__ = Cleanable.__slots__ + [
        "_workstation_id",
        "_owner_space_id",
        "_objects_by_name",
        "_attributes_by_name",
        "_methods_by_name",
        "_target_name",
        "_target_store",
    ]
    _VALID_STORES: Tuple[str, ...] = ("objects", "attributes", "methods")
    _DEFAULT_CLEANUP_METHODS: Tuple[str, ...] = ("cleanup", "close", "dispose")

    def __init__(self, owner_space_id: str) -> None:
        """
        Internal

        Initialize one room-local workstation canvas.

        Args:
            owner_space_id:
                Stable room identifier for the owning `RiftSpace`.

        Returns:
            None.

        Raises:
            ValueError:
                If `owner_space_id` is empty.
        """
        super().__init__()
        if not owner_space_id:
            raise ValueError("owner_space_id cannot be empty.")
        self._workstation_id: str = IDBuilder.create_id()
        self._owner_space_id: str = owner_space_id
        self._objects_by_name: Dict[str, object] = {}
        self._attributes_by_name: Dict[str, object] = {}
        self._methods_by_name: Dict[str, object] = {}
        self._target_name: Optional[str] = None
        self._target_store: Optional[str] = None

    def cleanup(self) -> None:
        """
        Internal

        Idempotently clear workstation binding state.

        Contract:
            - Safe to call more than once.
            - Clears object/value/callable binding stores.
            - Clears active-target state.
            - Does not attempt to cleanup every stored binding automatically;
              explicit target cleanup is a separate operation.

        Returns:
            None.
        """
        if self._cleaned:
            return
        self._cleaned = True
        self._objects_by_name.clear()
        self._attributes_by_name.clear()
        self._methods_by_name.clear()
        self._objects_by_name = None
        self._attributes_by_name = None
        self._methods_by_name = None
        self._target_name = None
        self._target_store = None
        self._owner_space_id = None
        self._workstation_id = None

    @property
    def workstation_id(self) -> str:
        """
        Return the stable workstation identifier.

        Returns:
            str: Stable workstation id.
        """
        self.check_cleaned()
        return self._workstation_id

    @property
    def owner_space_id(self) -> str:
        """
        Return the owning room identifier.

        Returns:
            str: Owning `RiftSpace` id.
        """
        self.check_cleaned()
        return self._owner_space_id

    def bind_object(self, name: str, value: object) -> None:
        """
        Store one object binding by name.

        Contract:
            Delegates to the shared `_bind(...)` helper using the `objects`
            store.

        Args:
            name:
                Binding name.
            value:
                Bound object value.

        Returns:
            None.

        Raises:
            ValueError:
                If `name` is empty.
        """
        self._bind("objects", name, value)

    def bind_attribute(self, name: str, value: object) -> None:
        """
        Store one attribute/value binding by name.

        Contract:
            Delegates to the shared `_bind(...)` helper using the `attributes`
            store.

        Args:
            name:
                Binding name.
            value:
                Bound attribute/value.

        Returns:
            None.

        Raises:
            ValueError:
                If `name` is empty.
        """
        self._bind("attributes", name, value)

    def bind_method(self, name: str, value: object) -> None:
        """
        Store one method/callable binding by name.

        Contract:
            Delegates to the shared `_bind(...)` helper using the `methods`
            store.

        Args:
            name:
                Binding name.
            value:
                Bound method/callable.

        Returns:
            None.

        Raises:
            ValueError:
                If `name` is empty.
        """
        self._bind("methods", name, value)

    def get(self, name: str, *, store: Optional[str] = None) -> object:
        """
        Return one saved binding by name.

        Args:
            name:
                Binding name to resolve.
            store:
                Optional explicit store name (`objects`, `attributes`,
                `methods`). When omitted, the binding must resolve uniquely
                across the stores.

        Returns:
            object: Saved binding value.

        Raises:
            ValueError:
                If `name` is empty, the binding is missing, or the name is
                ambiguous across stores.
        """
        self.check_cleaned()
        _, value = self._resolve_binding(name, store=store)
        return value

    def release(self, name: str, *, store: Optional[str] = None) -> object:
        """
        Remove one saved binding and return the removed value.

        Args:
            name:
                Binding name to remove.
            store:
                Optional explicit store name. When omitted, the binding must
                resolve uniquely across the stores.

        Returns:
            object: Removed binding value.

        Raises:
            ValueError:
                If the binding cannot be resolved.
        """
        self.check_cleaned()
        resolved_store, value = self._resolve_binding(name, store=store)
        self._get_store_map(resolved_store).pop(name)
        if self._target_name == name and self._target_store == resolved_store:
            self.clear_target()
        return value

    def describe_bindings(self) -> Dict[str, List[str]]:
        """
        Return a detached summary of saved binding names by store.

        Returns:
            Dict[str, List[str]]: Binding names grouped by store.
        """
        self.check_cleaned()
        return {
            "objects": sorted(self._objects_by_name.keys()),
            "attributes": sorted(self._attributes_by_name.keys()),
            "methods": sorted(self._methods_by_name.keys()),
            "target_name": [] if self._target_name is None else [self._target_name],
            "target_store": [] if self._target_store is None else [self._target_store],
        }

    def set_target(self, name: str, *, store: Optional[str] = None) -> None:
        """
        Select one saved binding as the active target.

        Args:
            name:
                Binding name to select.
            store:
                Optional explicit store name. When omitted, the binding must
                resolve uniquely across the stores.

        Returns:
            None.

        Raises:
            ValueError:
                If the binding cannot be resolved.
        """
        self.check_cleaned()
        resolved_store, _ = self._resolve_binding(name, store=store)
        self._target_name = name
        self._target_store = resolved_store

    def get_target(self) -> object:
        """
        Return the currently selected target value.

        Returns:
            object: Current target value.

        Raises:
            ValueError:
                If no target is selected.
        """
        self.check_cleaned()
        if self._target_name is None or self._target_store is None:
            raise ValueError("Workstation has no active target.")
        return self._get_store_map(self._target_store)[self._target_name]

    def clear_target(self) -> None:
        """
        Clear the current active-target selection only.

        Contract:
            - Leaves all stored bindings intact.
            - Resets only the active-target pointers.

        Returns:
            None.
        """
        self.check_cleaned()
        self._target_name = None
        self._target_store = None

    def cleanup_target(self, *method_names: str) -> None:
        """
        Call cleanup methods on the current target and then clear target selection.

        Args:
            *method_names:
                Optional ordered cleanup method names. When omitted, the
                workstation uses the default sequence:
                `cleanup`, `close`, `dispose`.

        Returns:
            None.

        Raises:
            ValueError:
                If no target is selected, a method name is empty, or no cleanup
                method can be resolved on the current target.
            RuntimeError:
                If one resolved cleanup method is not callable.
        """
        self.check_cleaned()
        target = self.get_target()
        cleanup_names = method_names or self._DEFAULT_CLEANUP_METHODS
        resolved_any = False
        for method_name in cleanup_names:
            if not method_name:
                raise ValueError("cleanup method names cannot be empty.")
            method = getattr(target, method_name, None)
            if method is None:
                continue
            if not callable(method):
                raise RuntimeError(
                    "Target cleanup attribute '{0}' is not callable.".format(
                        method_name
                    )
                )
            method()
            resolved_any = True
        if not resolved_any:
            raise ValueError("No cleanup method was found on the active target.")
        self.clear_target()

    def call_target(
            self,
            *args: Any,
            bind_as_name: Optional[str] = None,
            bind_as_store: str = "objects",
            **kwargs: Any
    ) -> object:
        """
        Invoke the current target and optionally bind the return value.

        Args:
            *args:
                Positional arguments passed to the target.
            bind_as_name:
                Optional workstation binding name for the return value.
            bind_as_store:
                Store to use when binding the return value:
                `objects`, `attributes`, or `methods`.
            **kwargs:
                Keyword arguments passed to the target.

        Returns:
            object: Target return value.

        Raises:
            ValueError:
                If no target is selected or `bind_as_store` is invalid.
            RuntimeError:
                If the target is not callable.
        """
        self.check_cleaned()
        target = self.get_target()
        if not callable(target):
            raise RuntimeError("Active target is not callable.")
        result = target(*args, **kwargs)
        if bind_as_name is not None:
            self._bind(bind_as_store, bind_as_name, result)
        return result

    def _bind(self, store: str, name: str, value: object) -> None:
        """
        Store one binding in the requested store.

        Contract:
            - Validates that the binding name is non-empty.
            - Resolves the target store through `_get_store_map(...)`.
            - Replaces any older binding with the same name in that store.

        Args:
            store:
                Store name to mutate.
            name:
                Binding name.
            value:
                Bound value.

        Returns:
            None.
        """
        self.check_cleaned()
        if not name:
            raise ValueError("binding name cannot be empty.")
        store_map = self._get_store_map(store)
        store_map[name] = value

    def _resolve_binding(
            self,
            name: str,
            *,
            store: Optional[str] = None,
    ) -> Tuple[str, object]:
        """
        Resolve one binding to its store name and value.

        Contract:
            - When `store` is supplied, lookup is restricted to that store.
            - When `store` is omitted, the name must resolve uniquely across
              the three workstation stores.
            - Raises instead of returning ambiguous or missing bindings.

        Args:
            name:
                Binding name to resolve.
            store:
                Optional explicit store name.

        Returns:
            Tuple[str, object]: Resolved store name and binding value.
        """
        if not name:
            raise ValueError("binding name cannot be empty.")
        if store is not None:
            store_map = self._get_store_map(store)
            try:
                return store, store_map[name]
            except KeyError as exc:
                raise ValueError(
                    "Binding '{0}' was not found in '{1}'.".format(
                        name,
                        store,
                    )
                ) from exc
        matches: List[Tuple[str, object]] = []
        for store_name in self._VALID_STORES:
            store_map = self._get_store_map(store_name)
            if name in store_map:
                matches.append((store_name, store_map[name]))
        if len(matches) == 0:
            raise ValueError("Binding '{0}' was not found.".format(name))
        if len(matches) > 1:
            raise ValueError(
                "Binding '{0}' is ambiguous across workstation stores.".format(
                    name
                )
            )
        return matches[0]

    def _get_store_map(self, store: str) -> Dict[str, object]:
        """
        Return the binding map for one named store.

        Contract:
            - Supports exactly the three workstation stores: `objects`,
              `attributes`, and `methods`.
            - Returns the live internal mapping for the selected store.

        Args:
            store:
                Store name to resolve.

        Returns:
            Dict[str, object]: Live binding map for the store.

        Raises:
            ValueError:
                If the store name is not supported.
        """
        if store == "objects":
            return self._objects_by_name
        if store == "attributes":
            return self._attributes_by_name
        if store == "methods":
            return self._methods_by_name
        raise ValueError(
            "Unsupported workstation store '{0}'.".format(store)
        )
