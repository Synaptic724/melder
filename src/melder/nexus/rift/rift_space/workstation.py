import threading
from typing import Any, Callable, Dict, List, Optional, Tuple

from melder.utilities.data_structures.weak_data_structures.weak_concurrent_dict import (
    WeakConcurrentDict,
)
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
        - Stores only room-local bindings; it does not discover or resolve new
          targets from Melder/Nexus.
        - Keeps object, attribute/value, and method/callable bindings in
          separate logical stores.
        - Each logical store supports both strong and weak backing storage.
        - Bind calls accept `weak_ref=True`, `weak_ref=False`, or
          `weak_ref=None`.
        - `weak_ref=None` resolves through the room-local default captured when
          this workstation is created.
        - Explicit weak binding raises when the supplied value cannot be
          weak-referenced; it never silently degrades to strong storage.
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

    Registration:
        MELDER KERNEL - guarded. Created by the owning `RiftSpace`; users reach
        it through `space.workstation`.

    Subsystem Context:
        The BINDING CANVAS of a room, third beside `FrameViewer` (reads) and
        `CommandSystem` (mediated actions). Commands deliberately do not store
        results, so this is where anything worth keeping lands.

    System Context:
        The weak/strong storage model is the core of this class and it is where
        room posture becomes concrete. `weak_ref=None` resolves through the
        ROOM-LOCAL DEFAULT captured at construction - weak in static rooms,
        strong in capability rooms - so the same call in different rooms
        correctly produces different lifetime semantics without the caller
        restating policy.
        Explicit weak binding RAISES when a value cannot be weak-referenced and
        never silently degrades to strong. That refusal is the important one: a
        silent downgrade would hand back a binding whose lifetime contract is
        the opposite of what was requested, and the caller would have no way to
        detect it.
        Separating object, attribute, and method stores keeps those namespaces
        from colliding, and the single active target reflects that a room is one
        person's workspace - a canvas with several simultaneous "current" things
        would make every target-relative command ambiguous.

    AGENT_ACCESS: public

    AGENT_PURPOSE:
        access: public. The room-local binding canvas (space.workstation): save objects,
        attribute and method bindings (strong or weak) and one active target across steps.
        Commands do not store their results, so this is where you keep what matters.
    """

    __slots__ = Cleanable.__slots__ + [
        "_id",
        "_owner_space_id",
        "_lock",
        "_default_weak_ref_bindings",
        "_event_publisher",
        "_strong_objects_by_name",
        "_strong_attributes_by_name",
        "_strong_methods_by_name",
        "_weak_objects_by_name",
        "_weak_attributes_by_name",
        "_weak_methods_by_name",
        "_target_name",
        "_target_store",
    ]
    _VALID_STORES: Tuple[str, ...] = ("objects", "attributes", "methods")
    _DEFAULT_CLEANUP_METHODS: Tuple[str, ...] = ("cleanup", "close", "dispose")

    def __init__(
            self,
            owner_space_id: str,
            *,
            default_weak_ref_bindings: bool = False,
            event_publisher: Optional[Callable[[Dict[str, object]], None]] = None,
    ) -> None:
        """
        Internal

        Initialize one room-local workstation canvas.

        Args:
            owner_space_id:
                Stable room identifier for the owning `RiftSpace`.
            default_weak_ref_bindings:
                Default weak-reference mode used when one bind call receives
                `weak_ref=None`.
            event_publisher:
                Optional best-effort room-local event publisher used for weak
                binding collection signals.

        Returns:
            None.

        Raises:
            ValueError:
                If `owner_space_id` is empty.
        """
        super().__init__()
        if not owner_space_id:
            raise ValueError("owner_space_id cannot be empty.")
        self._id: str = IDBuilder.create_id()
        self._owner_space_id: str = owner_space_id
        self._lock: threading.RLock = threading.RLock()
        self._default_weak_ref_bindings: bool = bool(default_weak_ref_bindings)
        self._event_publisher: Optional[Callable[[Dict[str, object]], None]] = (
            event_publisher
        )
        self._strong_objects_by_name: Dict[str, object] = {}
        self._strong_attributes_by_name: Dict[str, object] = {}
        self._strong_methods_by_name: Dict[str, object] = {}
        self._weak_objects_by_name: WeakConcurrentDict[str, object] = (
            WeakConcurrentDict(auto_prune=True)
        )
        self._weak_attributes_by_name: WeakConcurrentDict[str, object] = (
            WeakConcurrentDict(auto_prune=True)
        )
        self._weak_methods_by_name: WeakConcurrentDict[str, object] = (
            WeakConcurrentDict(auto_prune=True)
        )
        self._target_name: Optional[str] = None
        self._target_store: Optional[str] = None

    def cleanup(self) -> None:
        """
        Internal

        Idempotently clear workstation binding state.

        Contract:
            - Safe to call more than once.
            - Clears strong and weak binding stores.
            - Clears active-target state.
            - Does not attempt to cleanup every stored binding automatically;
              explicit target cleanup is a separate operation.

        Returns:
            None.
        """
        if self._cleaned:
            return
        with self._lock:
            if self._cleaned:
                return

            self._cleaned = True

            self._strong_objects_by_name.clear()
            self._strong_attributes_by_name.clear()
            self._strong_methods_by_name.clear()
            self._weak_objects_by_name.cleanup()
            self._weak_attributes_by_name.cleanup()
            self._weak_methods_by_name.cleanup()

            del self._strong_objects_by_name
            del self._strong_attributes_by_name
            del self._strong_methods_by_name
            del self._weak_objects_by_name
            del self._weak_attributes_by_name
            del self._weak_methods_by_name
            del self._default_weak_ref_bindings
            del self._event_publisher
            del self._target_name
            del self._target_store
            del self._owner_space_id
            del self._id
        del self._lock

    @property
    def workstation_id(self) -> str:
        """
        Return the stable workstation identifier.

        Contract:
            - Identifies THIS WORKSTATION, distinct from `owner_space_id` - the space
              that hosts it.

        Threading:
            Reads under `self._lock`, so the result is a coherent snapshot.

        Lifecycle / Cleanup:
            Guarded by `check_cleaned()`.

        Raises:
            RuntimeError: If the object has been cleaned.

        Returns:
            str: Stable workstation id.
        """
        self.check_cleaned()
        with self._lock:
            return self._id

    @property
    def owner_space_id(self) -> str:
        """
        Return the owning room identifier.

        Contract:
            - The rift space hosting this workstation, fixed at construction. A
              workstation is never re-homed to another space.

        Threading:
            Reads under `self._lock`, so the result is a coherent snapshot.

        Lifecycle / Cleanup:
            Guarded by `check_cleaned()`.

        Raises:
            RuntimeError: If the object has been cleaned.

        Returns:
            str: Owning `RiftSpace` id.
        """
        self.check_cleaned()
        with self._lock:
            return self._owner_space_id

    def bind_object(
            self,
            name: str,
            value: object,
            *,
            weak_ref: Optional[bool] = None,
    ) -> None:
        """
        Store one object binding by name.

        Contract:
            Delegates to the shared `_bind(...)` helper using the `objects`
            store and the requested reference mode.

        Args:
            name:
                Binding name.
            value:
                Bound object value.
            weak_ref:
                Explicit reference-mode override. `True` forces weak storage,
                `False` forces strong storage, and `None` uses the room-local
                workstation default.

        Returns:
            None.

        Raises:
            ValueError:
                If `name` is empty.
            TypeError:
                If weak storage is requested for a value that cannot be
                weak-referenced.
        """
        self.check_cleaned()
        self._bind("objects", name, value, weak_ref=weak_ref)

    def bind_attribute(
            self,
            name: str,
            value: object,
            *,
            weak_ref: Optional[bool] = None,
    ) -> None:
        """
        Store one attribute/value binding by name.

        Contract:
            Delegates to the shared `_bind(...)` helper using the `attributes`
            store and the requested reference mode.

        Args:
            name:
                Binding name.
            value:
                Bound attribute/value.
            weak_ref:
                Explicit reference-mode override. `True` forces weak storage,
                `False` forces strong storage, and `None` uses the room-local
                workstation default.

        Returns:
            None.

        Raises:
            ValueError:
                If `name` is empty.
            TypeError:
                If weak storage is requested for a value that cannot be
                weak-referenced.
        """
        self.check_cleaned()
        self._bind("attributes", name, value, weak_ref=weak_ref)

    def bind_method(
            self,
            name: str,
            value: object,
            *,
            weak_ref: Optional[bool] = None,
    ) -> None:
        """
        Store one method/callable binding by name.

        Contract:
            Delegates to the shared `_bind(...)` helper using the `methods`
            store and the requested reference mode.

        Args:
            name:
                Binding name.
            value:
                Bound method/callable.
            weak_ref:
                Explicit reference-mode override. `True` forces weak storage,
                `False` forces strong storage, and `None` uses the room-local
                workstation default.

        Returns:
            None.

        Raises:
            ValueError:
                If `name` is empty.
            TypeError:
                If weak storage is requested for a value that cannot be
                weak-referenced.
        """
        self.check_cleaned()
        self._bind("methods", name, value, weak_ref=weak_ref)

    def get(self, name: str, *, store: Optional[str] = None) -> object:
        """
        Return one saved binding by name.

        Args:
            name:
                Binding name to resolve.
            store:
                Optional explicit store name (`objects`, `attributes`,
                `methods`). When omitted, the binding must resolve uniquely
                across the logical stores.

        Returns:
            object: Saved binding value.

        Raises:
            ValueError:
                If `name` is empty, the binding is missing, or the name is
                ambiguous across the logical stores.
        """
        self.check_cleaned()
        with self._lock:
            _, _, value = self._resolve_binding(name, store=store)
            return value

    def release(self, name: str, *, store: Optional[str] = None) -> object:
        """
        Remove one saved binding and return the removed value.

        Args:
            name:
                Binding name to remove.
            store:
                Optional explicit store name. When omitted, the binding must
                resolve uniquely across the logical stores.

        Returns:
            object: Removed binding value.

        Raises:
            ValueError:
                If the binding cannot be resolved.
        """
        self.check_cleaned()
        with self._lock:
            resolved_store, resolved_weak_ref, value = self._resolve_binding(
                name,
                store=store,
            )
            self._remove_resolved_binding(
                resolved_store,
                name,
                resolved_weak_ref,
            )
            if self._target_name == name and self._target_store == resolved_store:
                self._clear_target_locked()
            return value

    def describe_bindings(self) -> Dict[str, List[str]]:
        """
        Return a detached summary of saved binding names by logical store.

        Contract:
            - Returns a FIVE-KEY summary - `objects`, `attributes`, `methods`,
              `target_name` and `target_store` - always with all five keys
              present, so callers can index them without a `get`.
            - `target_name` and `target_store` are normalized to LISTS for shape
              consistency with the other three: empty when no target is bound,
              single-element when one is. Neither is a list of many targets.
              `target_store` names WHICH store the active target came from, so a
              caller can round-trip it back through `get(name, store=...)`.
            - Names only, not values: this describes what is bound, not what those
              bindings currently hold.

        Threading:
            Reads under `self._lock`, so the result is a coherent snapshot.

        Lifecycle / Cleanup:
            Guarded by `check_cleaned()`.

        Raises:
            RuntimeError: If the object has been cleaned.

        Returns:
            Dict[str, List[str]]: Binding names grouped by logical store.
        """
        self.check_cleaned()
        with self._lock:
            return {
                "objects": self._describe_store_names("objects"),
                "attributes": self._describe_store_names("attributes"),
                "methods": self._describe_store_names("methods"),
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
                resolve uniquely across the logical stores.

        Returns:
            None.

        Raises:
            ValueError:
                If the binding cannot be resolved.
        """
        self.check_cleaned()
        with self._lock:
            resolved_store, _, _ = self._resolve_binding(name, store=store)
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
        with self._lock:
            if self._target_name is None or self._target_store is None:
                raise ValueError("Workstation has no active target.")
            _, _, value = self._resolve_binding(
                self._target_name,
                store=self._target_store,
            )
            return value

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
        with self._lock:
            self._clear_target_locked()

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
        with self._lock:
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
            self._clear_target_locked()

    def call_target(
            self,
            *args: Any,
            bind_as_name: Optional[str] = None,
            bind_as_store: str = "objects",
            **kwargs: Any
    ) -> object:
        """
        Invoke the current target and optionally bind the return value.

        Contract:
            - Resolves the current target through the logical store layer.
            - When `bind_as_name` is supplied, the return value is rebound
              through the normal workstation bind path with `weak_ref=None`,
              which means the room default applies.

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
        with self._lock:
            target = self.get_target()
            if not callable(target):
                raise RuntimeError("Active target is not callable.")
            result = target(*args, **kwargs)
            if bind_as_name is not None:
                self._bind(
                    bind_as_store,
                    bind_as_name,
                    result,
                    weak_ref=None,
                )
            return result

    def _bind(
            self,
            store: str,
            name: str,
            value: object,
            *,
            weak_ref: Optional[bool],
    ) -> None:
        """
        Store one binding in the requested logical store.

        Contract:
            - Validates that the binding name is non-empty.
            - Resolves the requested reference mode through the workstation
              default when `weak_ref` is `None`.
            - Replaces any older binding with the same name in that logical
              store, regardless of whether it previously lived in strong or
              weak storage.
            - Explicit weak binding raises when the supplied value cannot be
              weak-referenced.

        Args:
            store:
                Logical store name to mutate.
            name:
                Binding name.
            value:
                Bound value.
            weak_ref:
                Explicit or deferred reference-mode selector.

        Returns:
            None.
        """
        self.check_cleaned()
        with self._lock:
            if not name:
                raise ValueError("binding name cannot be empty.")
            effective_weak_ref = self._resolve_weak_ref_mode(weak_ref)
            self._clear_binding_name_from_store(store, name)
            strong_store_map, weak_store_map = self._get_store_maps(store)
            if effective_weak_ref:
                weak_store_map[name] = value
                self._register_weak_binding_callback(
                    store,
                    name,
                    weak_store_map,
                )
                return
            strong_store_map[name] = value

    def _resolve_binding(
            self,
            name: str,
            *,
            store: Optional[str] = None,
    ) -> Tuple[str, bool, object]:
        """
        Resolve one binding to its logical store, reference mode, and value.

        Contract:
            - When `store` is supplied, lookup is restricted to that logical
              store.
            - When `store` is omitted, the name must resolve uniquely across
              the logical stores.
            - Strong and weak bindings within the same logical store are
              treated as one namespace and must not both resolve for the same
              name.

        Args:
            name:
                Binding name to resolve.
            store:
                Optional explicit logical store name.

        Returns:
            Tuple[str, bool, object]: Resolved logical store name, weak flag,
            and binding value.

        Raises:
            ValueError:
                If the binding is missing or ambiguous.
        """
        if not name:
            raise ValueError("binding name cannot be empty.")
        if store is not None:
            return self._resolve_binding_in_store(store, name)
        matches: List[Tuple[str, bool, object]] = []
        for store_name in self._VALID_STORES:
            try:
                matches.append(self._resolve_binding_in_store(store_name, name))
            except ValueError:
                continue
        if len(matches) == 0:
            raise ValueError("Binding '{0}' was not found.".format(name))
        if len(matches) > 1:
            raise ValueError(
                "Binding '{0}' is ambiguous across workstation stores.".format(
                    name
                )
            )
        return matches[0]

    def _resolve_binding_in_store(
            self,
            store: str,
            name: str,
    ) -> Tuple[str, bool, object]:
        """
        Resolve one binding inside one logical store.

        Args:
            store:
                Logical store name to resolve.
            name:
                Binding name to resolve.

        Returns:
            Tuple[str, bool, object]: Resolved logical store name, weak flag,
            and binding value.

        Raises:
            ValueError:
                If the binding is missing or ambiguous within the logical
                store.
        """
        strong_store_map, weak_store_map = self._get_store_maps(store)
        matches: List[Tuple[str, bool, object]] = []
        if name in strong_store_map:
            matches.append((store, False, strong_store_map[name]))
        if name in weak_store_map:
            matches.append((store, True, weak_store_map[name]))
        if len(matches) == 0:
            raise ValueError(
                "Binding '{0}' was not found in '{1}'.".format(
                    name,
                    store,
                )
            )
        if len(matches) > 1:
            raise ValueError(
                "Binding '{0}' is ambiguous inside '{1}'.".format(
                    name,
                    store,
                )
            )
        return matches[0]

    def _clear_binding_name_from_store(self, store: str, name: str) -> None:
        """
        Remove one binding name from both backing stores for one logical store.

        Args:
            store:
                Logical store name.
            name:
                Binding name to clear.

        Returns:
            None.
        """
        strong_store_map, weak_store_map = self._get_store_maps(store)
        strong_store_map.pop(name, None)
        weak_store_map.prune()
        if name in weak_store_map:
            try:
                weak_store_map.pop(name)
            except Exception:
                pass

    def _remove_resolved_binding(
            self,
            store: str,
            name: str,
            weak_ref: bool,
    ) -> None:
        """
        Remove one already-resolved binding from its backing store.

        Args:
            store:
                Logical store name.
            name:
                Binding name to remove.
            weak_ref:
                Backing-store selector returned by `_resolve_binding(...)`.

        Returns:
            None.
        """
        strong_store_map, weak_store_map = self._get_store_maps(store)
        if weak_ref:
            weak_store_map.pop(name)
            return
        strong_store_map.pop(name)

    def _describe_store_names(self, store: str) -> List[str]:
        """
        Return one detached, sorted binding-name list for a logical store.

        Args:
            store:
                Logical store name.

        Returns:
            List[str]: Sorted binding names from the strong and weak backing
            stores.
        """
        strong_store_map, weak_store_map = self._get_store_maps(store)
        names = set(strong_store_map.keys())
        names.update(list(weak_store_map.keys()))
        return sorted(names)

    def _register_weak_binding_callback(
            self,
            store: str,
            name: str,
            weak_store_map: WeakConcurrentDict[str, object],
    ) -> None:
        """
        Attach one best-effort room-local publication callback to a weak binding.

        Args:
            store:
                Logical store that owns the binding.
            name:
                Binding name.
            weak_store_map:
                Weak backing store that now owns the binding.

        Returns:
            None.
        """
        if self._event_publisher is None:
            return
        node = weak_store_map._dict.get(name)
        if node is None:
            return
        node.add_callback(
            lambda collected_node: self._publish_weak_binding_event(
                store,
                name,
                collected_node,
            )
        )

    def _publish_weak_binding_event(
            self,
            store: str,
            name: str,
            node: object,
    ) -> None:
        """
        Publish one room-local event when a weak binding dies on the GC path.

        Args:
            store:
                Logical store that owned the binding.
            name:
                Binding name.
            node:
                Weak node that fired the callback.

        Returns:
            None.
        """
        if self._event_publisher is None:
            return
        if not getattr(node, "has_fired", False):
            return
        try:
            self._event_publisher(
                {
                    "event_type": "binding_collected",
                    "binding_name": name,
                    "binding_store": store,
                    "workstation_id": self._id,
                    "owner_space_id": self._owner_space_id,
                }
            )
        except Exception:
            pass

    def _resolve_weak_ref_mode(self, weak_ref: Optional[bool]) -> bool:
        """
        Resolve one bind call's effective weak-reference mode.

        Args:
            weak_ref:
                Explicit or deferred weak-reference selector.

        Returns:
            bool: Effective weak-reference mode for the bind call.
        """
        if weak_ref is None:
            return self._default_weak_ref_bindings
        return bool(weak_ref)

    def _clear_target_locked(self) -> None:
        """
        Clear the current target while the workstation lock is already held.

        Returns:
            None.
        """
        self._target_name = None
        self._target_store = None

    def _get_store_maps(
            self,
            store: str,
    ) -> Tuple[Dict[str, object], WeakConcurrentDict[str, object]]:
        """
        Return the strong and weak backing stores for one logical store.

        Contract:
            Supports exactly the three logical workstation stores: `objects`,
            `attributes`, and `methods`.

        Args:
            store:
                Logical store name to resolve.

        Returns:
            Tuple[Dict[str, object], WeakConcurrentDict[str, object]]: Strong
            and weak backing stores for the requested logical store.

        Raises:
            ValueError:
                If the logical store name is not supported.
        """
        if store == "objects":
            return self._strong_objects_by_name, self._weak_objects_by_name
        if store == "attributes":
            return self._strong_attributes_by_name, self._weak_attributes_by_name
        if store == "methods":
            return self._strong_methods_by_name, self._weak_methods_by_name
        raise ValueError(
            "Unsupported workstation store '{0}'.".format(store)
        )
