import threading
from contextlib import contextmanager
from typing import TYPE_CHECKING, Any, Callable, Dict, List, Optional, Tuple
if TYPE_CHECKING:
    from melder.aether.conduit.conduit import Conduit
    from melder.nexus.acl.frame_acl_compiled_access_surface import (
        CompiledFrameACLAccessSurface,
    )
    from melder.nexus.rift.rift import Rift
    from melder.nexus.rift.rift_space.rift_space import RiftSpace
    from melder.nexus.rift.rift_space.workstation import Workstation

from melder.aether.aether import Aether
from melder.utilities.general_base.cleanable import Cleanable
from melder.utilities.helpers.id_builder import IDBuilder


class CommandSystem(Cleanable):
    """
    Internal

    Room-local shared command infrastructure plus common read/target helpers.

    Purpose:
        Provide shared command infrastructure above the viewer/workstation
        split without owning every room-specific command vocabulary.

    Contract:
        - Uses the owning `Rift` command projections as the shared command
          substrate.
        - Enforces compiled command ACL state on direct fetch paths before
          exposing frame/conduit/spell runtime objects.
        - Uses the owned workstation for active-target attribute/method getters
          and method execution.
        - Does not store results itself. Callers that want persistence must
          bind returned values into the workstation explicitly.
        - Leaves room-owned topology mutation and spell activation commands to
          room-specific subclasses instead of pretending every room owns the
          same broad public surface.

    Lifecycle:
        Owned by one `RiftSpace`. Cleanup drops references to the owning room
        and workstation but does not clean those children itself.

    Threading:
        Room-confined. It holds no cross-room state and takes no lock of its
        own; the ACL projections it enforces against are refreshed by the owning
        Rift.

    Registration:
        MELDER KERNEL. The three postures are melder-internal and constructed by their
        owning room (for example `CapabilityRiftSpace` builds
        `CapabilityCommandSystem`), with no user injection seam.

    Subsystem Context:
        The MEDIATED command layer above the viewer/workstation split.
        `FrameViewer` answers read questions, `Workstation` holds bindings and
        the active target, and this class is the controlled surface through
        which getters and executes actually run. Room-specific subclasses add
        the vocabulary that does not belong to every room.

    System Context:
        Two rules define this class and both are about refusing convenience.
        First, ACL IS ENFORCED ON THE DIRECT FETCH PATH - compiled command ACL
        state is checked BEFORE any frame, conduit, or spell runtime object is
        exposed. Checking after would mean the object had already escaped.
        Second, IT DOES NOT STORE RESULTS. A caller that wants persistence must
        bind the returned value into the workstation explicitly. Auto-storing
        would make every read silently extend object lifetime and quietly
        populate a room's canvas with things nobody chose to keep.
        The subclass split exists because pretending every room owns the same
        broad public surface is exactly the lie the room modes exist to prevent:
        `CapabilityCommandSystem` owns topology mutation and direct activation,
        `StaticCommandSystem` owns live-only retrieval and reuse-only
        activation, and `CodegenCommandSystem` owns the validate/execute seams
        plus the full research command family.
    """
    __ast_helper_access__: str = "internal"
    __agent_purpose__: str = (
        "access: internal. Room-local shared command infrastructure plus common read/target "
        "helpers. Melder kernel machinery: read it to understand the runtime, do not drive it "
        "directly."
    )

    __slots__ = Cleanable.__slots__ + [
        "_id",
        "_owner_space_id",
        "_lock",
        "_rift",
        "_space",
        "_workstation",
    ]
    _DENIED_RAW_RUNTIME_OBJECT_ACCESS_METHOD_NAMES: frozenset[str] = frozenset()
    _RAW_RUNTIME_OBJECT_ACCESS_DENIED_MESSAGE_TEMPLATE: str = (
        "Command surface does not allow raw runtime-object access method '{0}'."
    )
    _aether = Aether()

    def __init__(
            self,
            *,
            rift: Rift,
            space: RiftSpace,
            workstation: Workstation,
    ) -> None:
        """
        Internal

        Initialize one room-local command system.

        Args:
            rift:
                Owning `Rift` that manages applied projection state.
            space:
                Owning `RiftSpace`.
            workstation:
                Room-local workstation owned by the same space.

        Returns:
            None.

        Raises:
            TypeError:
                If `space` or `workstation` is None.
        """
        super().__init__()
        if rift is None:
            raise TypeError("rift cannot be None.")
        if space is None:
            raise TypeError("space cannot be None.")
        if workstation is None:
            raise TypeError("workstation cannot be None.")
        type(self)._aether = Aether()
        self._id: str = IDBuilder.create_id()
        self._owner_space_id: str = space.space_id
        self._lock: threading.RLock = threading.RLock()
        self._rift: Rift = rift
        self._space: RiftSpace = space
        self._workstation: Workstation = workstation

    def cleanup(self) -> None:
        """
        Internal

        Idempotently clear command-system-owned references.

        Contract:
            - Safe to call more than once.
            - Clears only command-system-owned references.
            - Does not cleanup the owning `RiftSpace` or its workstation,
              because those remain owned by the room itself.

        Returns:
            None.
        """
        if self._cleaned:
            return
        with self._lock:
            if self._cleaned:
                return
            self._cleaned = True
            del self._owner_space_id
            del self._rift
            del self._space
            del self._workstation
            del self._id
        del self._lock

    @property
    def command_system_id(self) -> str:
        """
        Return the stable command-system identifier.

        Returns:
            str: Stable command-system id.
        """
        self.check_cleaned()
        with self._lock:
            return self._id

    @property
    def owner_space_id(self) -> str:
        """
        Return the owning room identifier.

        Returns:
            str: Owning `RiftSpace` id.
        """
        self.check_cleaned()
        with self._lock:
            return self._owner_space_id

    def _get_conduit_by_id_locked(
            self,
            conduit_id: str,
            *,
            frame_name: str,
    ) -> Conduit:
        """
        Resolve one conduit object while the command lock is already held.

        Contract:
            - Enforces raw-runtime access, frame command enablement, and
              conduit-level ACL checks before touching Aether runtime state.
            - Falls back through lesser-conduit lineage traversal when the root
              conduit lookup misses.
            - Requires the caller to hold `self._lock`.

        Args:
            conduit_id:
                Conduit id to resolve.
            frame_name:
                Resolved hosted frame name.

        Returns:
            object: Live conduit object or matching lesser conduit object.

        Raises:
            ValueError:
                If runtime-object access is denied, the frame/conduit ACL gate
                fails, or the conduit cannot be found in the frame.
        """
        self._assert_raw_runtime_object_access_allowed("get_conduit_by_id")
        self._assert_frame_command_enabled(frame_name)
        self._assert_conduit_command_enabled(
            conduit_id,
            frame_name=frame_name,
        )
        try:
            return self._aether.get_conduit_by_id(
                conduit_id,
                frame_name,
            )
        except ValueError:
            frame = self._get_required_runtime_frame(frame_name)
            for root_conduit in frame._conduits.values():
                conduit_ward = root_conduit._conduit_ward
                if conduit_ward is None:
                    continue
                lesser_conduit = conduit_ward._get_lesser_conduit(conduit_id)
                if lesser_conduit is not None:
                    return lesser_conduit
            raise ValueError(
                "Conduit id '{0}' was not found in frame '{1}'.".format(
                    conduit_id,
                    frame_name,
                )
            )

    def _get_spell_by_index_id_locked(
            self,
            spell_index_id: str,
            *,
            frame_name: str,
    ) -> object:
        """
        Resolve one spell runtime object by stable spell-index id while the command
        lock is already held.

        Contract:
            - Enforces raw-runtime access plus frame/spell command ACL checks
              before touching runtime conduit state.
            - Resolves through the command projection descriptor truth rather
              than viewer state.
            - Requires the caller to hold `self._lock`.

        Args:
            spell_index_id:
                Stable SpellIndex spell-index id to resolve.
            frame_name:
                Resolved hosted frame name.

        Returns:
            object: Live spell runtime object.

        Raises:
            ValueError:
                If the spell-index id is empty, unpublished, command-disabled, or
                not found in the owner spellbooks for the frame.
        """
        if not spell_index_id:
            raise ValueError("spell_index_id cannot be empty.")
        self._assert_raw_runtime_object_access_allowed(
            "get_spell_by_index_id"
        )
        self._assert_frame_command_enabled(frame_name)
        self._assert_spell_command_enabled(
            spell_index_id,
            frame_name=frame_name,
        )
        descriptor = self._rift._get_required_command_projection(
            frame_name
        ).frame_descriptor
        matching_spell_records = [
            spell_record
            for spell_record in descriptor.spell_records_by_key.values()
            if spell_record.spell_index_id == spell_index_id
        ]
        if len(matching_spell_records) == 0:
            raise ValueError(
                "Spell index id '{0}' was not found in frame '{1}'.".format(
                    spell_index_id,
                    frame_name,
                )
            )
        for spell_record in matching_spell_records:
            owner_conduit_id = spell_record.owner_conduit_id
            if not owner_conduit_id:
                continue
            owner_conduit = self._get_conduit_by_id_locked(
                owner_conduit_id,
                frame_name=frame_name,
            )
            spell = owner_conduit.get_spell_by_index_id(spell_index_id)
            if spell is not None:
                return spell
        raise ValueError(
            "Spell index id '{0}' was not found in the owner spellbooks for frame '{1}'.".format(
                spell_index_id,
                frame_name,
            )
        )

    def _get_target_method_locked(
            self,
            method_name: str,
    ) -> Callable[..., object]:
        """
        Resolve one callable from the current workstation target while the
        command lock is already held.

        Contract:
            - Requires the caller to hold `self._lock`.
            - Enforces the same validation contract as
              `get_target_method(...)`.

        Args:
            method_name:
                Method name to resolve from the active workstation target.

        Returns:
            Callable[..., object]: Bound callable from the current target.

        Raises:
            ValueError:
                If `method_name` is empty.
            AttributeError:
                If the current target does not expose the requested attribute.
            RuntimeError:
                If the resolved attribute is not callable.
        """
        if not method_name:
            raise ValueError("method_name cannot be empty.")
        target = self._workstation.get_target()
        method = getattr(target, method_name)
        if not callable(method):
            raise RuntimeError(
                "Target attribute '{0}' is not callable.".format(method_name)
            )
        return method

    def _list_supported_command_methods_tuple(self) -> Tuple[str, ...]:
        """
        Return the shared stable command-method vocabulary without any gate or
        room-policy filtering.

        Contract:
            - Acts as the single source of truth for the base command surface.
            - Returns stable presentation order for discovery/reporting.
            - Does not perform gating, memory emission, or room-specific
              filtering.

        Returns:
            Tuple[str, ...]: Shared base command-method names in stable order.
        """
        return (
            "link_frame",
            "get_nexus_frame",
            "describe_spells_in_conduit",
            "get_resolution_state",
            "get_active_spellspace",
            "find_spell_id",
            "find_spell_key",
            "get_spell_permissions",
            "snapshot_state",
            "get_spell_by_source_id",
            "get_spell_by_index_id",
            "get_spell_by_id",
            "get_target_attribute",
            "get_target_method",
            "execute_target_method",
        )


    def describe_spells_in_conduit(
            self,
            conduit_id: str,
            *,
            frame_name: Optional[str] = None,
    ) -> List[dict[str, Any]]:
        """
        Return the spell description payloads exposed by one conduit.

        Purpose:
            Provide a structured spell-description surface for one runtime
            conduit through the shared command API.

        Contract:
            - Resolves the conduit through command ACL and descriptor truth
              before touching runtime conduit state.
            - Returns the lower conduit runtime's current spell description
              payloads as a list without additional filtering.
            - Uses one top-level command action boundary for gate admission and
              memory emission.

        Args:
            conduit_id:
                Conduit id whose spell descriptions should be returned.
            frame_name:
                Optional frame name. When omitted, the room default frame is
                used.

        Returns:
            List[dict[str, Any]]: Runtime spell description payloads for the
            conduit.
        """
        self.check_cleaned()
        with self._entered_command_action(
                action_name="describe_spells_in_conduit",
                frame_name=frame_name,
        ), self._lock:
            resolved_frame_name = self._resolve_runtime_frame_name(frame_name)
            conduit = self._get_conduit_by_id_locked(
                conduit_id,
                frame_name=resolved_frame_name,
            )
            return conduit.describe_spells_in_conduit()

    def get_resolution_state(
            self,
            conduit_id: str,
            *,
            frame_name: Optional[str] = None,
    ) -> object:
        """
        Return the conduit-scoped resolution state for one conduit.

        Purpose:
            Expose the lower conduit runtime's current resolution-state object
            through the shared command surface.

        Contract:
            - Resolves the conduit through command ACL and descriptor truth
              before touching runtime conduit state.
            - Returns the live lower-runtime resolution-state object directly.
            - Uses one top-level command action boundary for gate admission and
              memory emission.

        Args:
            conduit_id:
                Conduit id whose resolution state should be returned.
            frame_name:
                Optional frame name. When omitted, the room default frame is
                used.

        Returns:
            object: Live conduit-scoped resolution-state object.
        """
        self.check_cleaned()
        with self._entered_command_action(
                action_name="get_resolution_state",
                frame_name=frame_name,
        ), self._lock:
            resolved_frame_name = self._resolve_runtime_frame_name(frame_name)
            conduit = self._get_conduit_by_id_locked(
                conduit_id,
                frame_name=resolved_frame_name,
            )
            return conduit.get_resolution_state()

    def get_active_spellspace(
            self,
            conduit_id: str,
            *,
            frame_name: Optional[str] = None,
    ) -> object:
        """
        Return the active spellspace for one conduit, if any.

        Purpose:
            Expose the lower conduit runtime's active spellspace surface
            through the shared command API.

        Contract:
            - Resolves the conduit through command ACL and descriptor truth
              before touching runtime conduit state.
            - Returns the currently active spellspace object or whatever the
              lower runtime exposes for the no-active-spellspace case.
            - Uses one top-level command action boundary for gate admission and
              memory emission.

        Args:
            conduit_id:
                Conduit id whose active spellspace should be returned.
            frame_name:
                Optional frame name. When omitted, the room default frame is
                used.

        Returns:
            object: Active spellspace object or lower-runtime sentinel value.
        """
        self.check_cleaned()
        with self._entered_command_action(
                action_name="get_active_spellspace",
                frame_name=frame_name,
        ), self._lock:
            resolved_frame_name = self._resolve_runtime_frame_name(frame_name)
            conduit = self._get_conduit_by_id_locked(
                conduit_id,
                frame_name=resolved_frame_name,
            )
            return conduit.get_active_spellspace()

    def find_spell_id(
            self,
            conduit_id: str,
            spellframe: str,
            spell_name: str,
            binding_name: str,
            *,
            frame_name: Optional[str] = None,
    ) -> object:
        """
        Return the current spell id resolved from logical spell identifiers.

        Purpose:
            Mirror the lower conduit spell-id lookup on the shared command
            surface using logical spell identity fields.

        Contract:
            - Resolves the conduit through command ACL and descriptor truth
              before touching runtime conduit state.
            - Defers lookup semantics to the lower conduit runtime instead of
              re-implementing spell identity matching in the command layer.
            - Uses one top-level command action boundary for gate admission and
              memory emission.

        Args:
            conduit_id:
                Conduit id whose spell inventory should be queried.
            spellframe:
                Logical spellframe key.
            spell_name:
                Logical spell name.
            binding_name:
                Logical binding name.
            frame_name:
                Optional frame name. When omitted, the room default frame is
                used.

        Returns:
            object: Current spell id resolved by the lower conduit runtime.
        """
        self.check_cleaned()
        with self._entered_command_action(
                action_name="find_spell_id",
                frame_name=frame_name,
        ), self._lock:
            resolved_frame_name = self._resolve_runtime_frame_name(frame_name)
            conduit = self._get_conduit_by_id_locked(
                conduit_id,
                frame_name=resolved_frame_name,
            )
            return conduit.find_spell_id(spellframe, spell_name, binding_name)

    def find_spell_key(
            self,
            conduit_id: str,
            spellframe: str,
            spell_name: str,
            binding_name: str,
            *,
            frame_name: Optional[str] = None,
    ) -> object:
        """
        Return the spellbook key resolved from logical spell identifiers.

        Purpose:
            Mirror the lower conduit spellbook-key lookup on the shared command
            surface using logical spell identity fields.

        Contract:
            - Resolves the conduit through command ACL and descriptor truth
              before touching runtime conduit state.
            - Defers lookup semantics to the lower conduit runtime instead of
              re-implementing spell identity matching in the command layer.
            - Uses one top-level command action boundary for gate admission and
              memory emission.

        Args:
            conduit_id:
                Conduit id whose spell inventory should be queried.
            spellframe:
                Logical spellframe key.
            spell_name:
                Logical spell name.
            binding_name:
                Logical binding name.
            frame_name:
                Optional frame name. When omitted, the room default frame is
                used.

        Returns:
            object: Spellbook key resolved by the lower conduit runtime.
        """
        self.check_cleaned()
        with self._entered_command_action(
                action_name="find_spell_key",
                frame_name=frame_name,
        ), self._lock:
            resolved_frame_name = self._resolve_runtime_frame_name(frame_name)
            conduit = self._get_conduit_by_id_locked(
                conduit_id,
                frame_name=resolved_frame_name,
            )
            return conduit.find_spell_key(spellframe, spell_name, binding_name)

    def get_spell_permissions(
            self,
            conduit_id: str,
            spell_id: str,
            *,
            frame_name: Optional[str] = None,
    ) -> object:
        """
        Return the permissions string for one spell inside one conduit.

        Purpose:
            Expose one lower-runtime spell-permissions lookup through the
            shared command surface.

        Contract:
            - Resolves the conduit through command ACL and descriptor truth
              before touching runtime conduit state.
            - Returns the exact permissions value exposed by the lower conduit
              runtime.
            - Uses one top-level command action boundary for gate admission and
              memory emission.

        Args:
            conduit_id:
                Conduit id whose spell permissions should be queried.
            spell_id:
                Current spell id to inspect.
            frame_name:
                Optional frame name. When omitted, the room default frame is
                used.

        Returns:
            object: Lower-runtime permissions value for the spell.
        """
        self.check_cleaned()
        with self._entered_command_action(
                action_name="get_spell_permissions",
                frame_name=frame_name,
        ), self._lock:
            resolved_frame_name = self._resolve_runtime_frame_name(frame_name)
            conduit = self._get_conduit_by_id_locked(
                conduit_id,
                frame_name=resolved_frame_name,
            )
            return conduit.get_spell_permissions(spell_id)

    def snapshot_state(
            self,
            conduit_id: str,
            *,
            frame_name: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Return a detached snapshot of one conduit state payload.

        Purpose:
            Expose one lower-runtime conduit state snapshot through the shared
            command surface.

        Contract:
            - Resolves the conduit through command ACL and descriptor truth
              before touching runtime conduit state.
            - Returns the lower conduit runtime's detached snapshot payload.
            - Uses one top-level command action boundary for gate admission and
              memory emission.

        Args:
            conduit_id:
                Conduit id whose state snapshot should be returned.
            frame_name:
                Optional frame name. When omitted, the room default frame is
                used.

        Returns:
            Dict[str, Any]: Detached conduit state snapshot payload.
        """
        self.check_cleaned()
        with self._entered_command_action(
                action_name="snapshot_state",
                frame_name=frame_name,
        ), self._lock:
            resolved_frame_name = self._resolve_runtime_frame_name(frame_name)
            conduit = self._get_conduit_by_id_locked(
                conduit_id,
                frame_name=resolved_frame_name,
            )
            return conduit.snapshot_state()

    def get_spell_by_source_id(
            self,
            spell_source_id: str,
            *,
            frame_name: Optional[str] = None,
    ) -> object:
        """
        Return one live spell object using a published spell source id.

        Args:
            spell_source_id:
                Published spell source id in `spellbook_id:spell_id` form.
            frame_name:
                Optional frame name. When omitted, the room default frame is
                used.

        Returns:
            object: Live spell object.

        Raises:
            ValueError:
                If the spell source id is not published in the selected frame
                or command ACL denies spell access.
        """
        self.check_cleaned()
        with self._entered_command_action(
                action_name="get_spell_by_source_id",
                frame_name=frame_name,
        ), self._lock:
            resolved_frame_name = self._resolve_runtime_frame_name(frame_name)
            spell_record = self._get_required_published_spell_record_by_source_id(
                spell_source_id,
                frame_name=resolved_frame_name,
            )
            self._assert_raw_runtime_object_access_allowed(
                "get_spell_by_source_id"
            )
            return self._get_spell_by_index_id_locked(
                spell_record.spell_index_id,
                frame_name=resolved_frame_name,
            )

    def get_spell_by_index_id(
            self,
            spell_index_id: str,
            *,
            frame_name: Optional[str] = None,
    ) -> object:
        """
        Return one live spell object by stable spell index id.

        Args:
            spell_index_id:
                Stable SpellIndex spell-index id to resolve.
            frame_name:
                Optional frame name. When omitted, the room default frame is
                used.

        Returns:
            object: Live spell object.

        Raises:
            ValueError:
                If the spell index is not published in the selected frame or
                command ACL denies spell access.
        """
        self.check_cleaned()
        with self._entered_command_action(
                action_name="get_spell_by_index_id",
                frame_name=frame_name,
        ), self._lock:
            resolved_frame_name = self._resolve_runtime_frame_name(frame_name)
            return self._get_spell_by_index_id_locked(
                spell_index_id,
                frame_name=resolved_frame_name,
            )

    def get_spell_by_id(
            self,
            spell_id: str,
            *,
            frame_name: Optional[str] = None,
    ) -> object:
        """
        Return one live spell object by current spell id.

        Args:
            spell_id:
                Current spell id to resolve.
            frame_name:
                Optional frame name. When omitted, the room default frame is
                used.

        Returns:
            object: Live spell object.

        Raises:
            ValueError:
                If the spell is not published in the selected frame or command
                ACL denies spell access.
        """
        self.check_cleaned()
        with self._entered_command_action(
                action_name="get_spell_by_id",
                frame_name=frame_name,
        ), self._lock:
            resolved_frame_name = self._resolve_runtime_frame_name(frame_name)
            self._assert_raw_runtime_object_access_allowed("get_spell_by_id")
            self._assert_frame_command_enabled(resolved_frame_name)
            spell_index_id = self._get_required_published_spell_index_id_by_spell_id(
                spell_id,
                frame_name=resolved_frame_name,
            )
            self._assert_spell_command_enabled(
                spell_index_id,
                frame_name=resolved_frame_name,
            )
            owner_conduit = self._aether._get_conduit_by_spell_id(
                spell_id,
                resolved_frame_name,
            )
            spellbook = owner_conduit._spellbook
            if spellbook is None:
                raise ValueError(
                    "Owner conduit for spell '{0}' has no spellbook.".format(spell_id)
                )
            for spell_index, spell in spellbook._spells.items():
                if spell_index.has_spell(spell_id):
                    return spell
            raise ValueError(
                "Spell id '{0}' was not found in the owner spellbook.".format(spell_id)
            )

    def get_target_attribute(self, attribute_name: str) -> object:
        """
        Return one attribute value from the current workstation target.

        Args:
            attribute_name:
                Attribute name to retrieve from the active target.

        Returns:
            object: Retrieved attribute value.

        Raises:
            ValueError:
                If `attribute_name` is empty.
            AttributeError:
                If the target does not expose the requested attribute.
        """
        self.check_cleaned()
        with self._entered_command_action(
                action_name="get_target_attribute",
                frame_name=None,
        ), self._lock:
            if not attribute_name:
                raise ValueError("attribute_name cannot be empty.")
            target = self._workstation.get_target()
            return getattr(target, attribute_name)

    def get_target_method(
            self,
            method_name: str,
    ) -> Callable[..., object]:
        """
        Return one method/callable from the current workstation target.

        Args:
            method_name:
                Method name to retrieve from the active target.

        Returns:
            Callable[..., object]: Bound callable from the target.

        Raises:
            ValueError:
                If `method_name` is empty.
            AttributeError:
                If the target does not expose the requested method.
            RuntimeError:
                If the resolved attribute is not callable.
        """
        self.check_cleaned()
        with self._entered_command_action(
                action_name="get_target_method",
                frame_name=None,
        ), self._lock:
            return self._get_target_method_locked(method_name)

    def execute_target_method(
            self,
            method_name: str,
            *args: Any,
            bind_as_name: Optional[str] = None,
            bind_as_store: str = "objects",
            bind_result_weak_ref: Optional[bool] = None,
            **kwargs: Any
    ) -> object:
        """
        Execute one method on the current workstation target.

        Args:
            method_name:
                Method name to execute on the active target.
            *args:
                Positional arguments passed to the method.
            bind_as_name:
                Optional workstation binding name for the return value.
            bind_as_store:
                Store to use when binding the return value.
            bind_result_weak_ref:
                Optional workstation reference-mode override for the bound
                result. `True` forces weak storage, `False` forces strong
                storage, and `None` uses the room/workstation default.
            **kwargs:
                Keyword arguments passed to the method.

        Returns:
            object: Method return value.
        """
        self.check_cleaned()
        with self._entered_command_action(
                action_name="execute_target_method",
                frame_name=None,
        ), self._lock:
            method = self._get_target_method_locked(method_name)
            result = method(*args, **kwargs)
            if bind_as_name is not None:
                self._bind_result(
                    bind_as_name=bind_as_name,
                    bind_as_store=bind_as_store,
                    value=result,
                    bind_result_weak_ref=bind_result_weak_ref,
                )
            return result

    def link_frame(self, frame_name: str) -> None:
        """
        Engage one target frame on this Rift through the shared command surface.

        Args:
            frame_name:
                Target frame name to link.

        Returns:
            None.
        """
        self.check_cleaned()
        with self._entered_command_action(
                action_name="link_frame",
                frame_name=frame_name,
        ), self._lock:
            self._rift.create_frame_link(frame_name)

    def get_nexus_frame(self, frame_name: Optional[str] = None) -> object:
        """
        Return one rooted Nexus-managed conduit through the shared command surface.

        Args:
            frame_name:
                Optional explicit Nexus frame name.

        Returns:
            object: Root conduit for the resolved Nexus-managed frame.
        """
        self.check_cleaned()
        with self._entered_command_action(
                action_name="get_nexus_frame",
                frame_name=frame_name,
        ), self._lock:
            return self._rift.get_nexus_frame(frame_name=frame_name)

    def list_supported_command_methods(self) -> Tuple[str, ...]:
        """
        Return the public command methods supported by this room surface.

        Purpose:
            Give callers a cheap, explicit way to discover the current
            command-surface vocabulary instead of guessing from room type or
            trial-and-error errors.

        Returns:
            Tuple[str, ...]: Supported public command method names in stable
                presentation order.
        """
        self.check_cleaned()
        with self._entered_command_action(
                action_name="list_supported_command_methods",
                frame_name=None,
        ):
            return self._list_supported_command_methods_tuple()

    @contextmanager
    def _entered_command_action(
            self,
            *,
            action_name: str,
            frame_name: Optional[str],
            category: str = "command",
    ) -> Any:
        """
        Enter one explicit top-level public command action.

        Args:
            action_name:
                Stable public command method name that completed successfully.
            frame_name:
                Optional caller-supplied frame name associated with the action.

        Returns:
            Any: Context manager that guarantees symmetric RiftGate release and
            successful top-level memory emission.
        """
        with self._entered_action_hook_scope_if_available(
                category=category,
                action_name=action_name,
        ):
            rift_gate = self._begin_command_action()
            command_succeeded = False
            try:
                yield
                command_succeeded = True
            finally:
                self._finish_command_action(
                    rift_gate=rift_gate,
                    action_name=action_name,
                    frame_name=frame_name,
                    emit_memory=command_succeeded,
                )

    def _begin_command_action(self) -> Optional[Any]:
        """
        Enter one top-level command action under RiftGate control.

        Contract:
            - Verifies that the command system is still live.
            - Resolves the owning room Rift gate when one is available.
            - Calls `admit()` before registering one active ticket.
            - Returns the gate object so the caller can guarantee symmetric
              release in a `finally` block.

        Returns:
            Optional[Any]: Owning room Rift gate, or None when no gate is bound
            to the room.
        """
        self.check_cleaned()
        rift_gate = self._get_rift_gate_if_available()
        if rift_gate is None:
            return None
        # Ticket-first admission (drain-race fix 2026-07-12): one verb
        # acquires a VISIBLE ticket before validating state, so a
        # projection refresh's drain can never observe zero tickets while
        # this command sits between admit and register.
        rift_gate.admit_ticket()
        return rift_gate

    def _finish_command_action(
            self,
            *,
            rift_gate: Optional[Any],
            action_name: str,
            frame_name: Optional[str],
            emit_memory: bool,
    ) -> None:
        """
        Exit one top-level command action and optionally emit command memory.

        Contract:
            - Releases the RiftGate ticket before emitting memory so the gate
              never stays held across memory callbacks.
            - Emits command memory only when the caller marks the command as a
              successful top-level action.
            - Never suppresses gate-release failures.

        Args:
            rift_gate:
                Rift gate returned by `_begin_command_action(...)`.
            action_name:
                Stable public command method name.
            frame_name:
                Optional caller-supplied frame name.
            emit_memory:
                True when the command completed successfully and should emit one
                memory record.

        Returns:
            None.
        """
        if rift_gate is not None:
            rift_gate.unregister_ticket()
        if emit_memory:
            self._emit_command_memory_if_enabled(
                action_name=action_name,
                frame_name=frame_name,
            )

    def _emit_command_memory_if_enabled(
            self,
            *,
            action_name: str,
            frame_name: Optional[str],
    ) -> None:
        """
        Emit one command memory record when the owning room enables memory output.

        Args:
            action_name:
                Stable public command method name.
            frame_name:
                Optional caller-supplied frame name.

        Returns:
            None.
        """
        memory_system = self._get_memory_system_if_available()
        if memory_system is None or not memory_system.memory_enabled:
            return
        resolved_frame_name = self._resolve_memory_frame_name(frame_name)
        if resolved_frame_name is None:
            return
        memory_system.create_and_emit_memory(
            frame_name=resolved_frame_name,
            action_name=action_name,
            metadata={
                "surface": "command",
                "command_system_id": self._id,
                "owner_space_id": self._owner_space_id,
            },
        )

    def _get_memory_system_if_available(self) -> Optional[Any]:
        """
        Return the owning room's memory system when one is available.

        Returns:
            Optional[Any]: Room-local memory system, or None when unavailable.
        """
        try:
            return self._space.memory_system
        except AttributeError:
            return None

    def _get_rift_gate_if_available(self) -> Optional[Any]:
        """
        Return the owning room's Rift gate when one is available.

        Returns:
            Optional[Any]: Room-local Rift gate, or None when unavailable.
        """
        try:
            return self._space.rift_gate
        except AttributeError:
            return None

    @contextmanager
    def _entered_action_hook_scope_if_available(
            self,
            *,
            category: str,
            action_name: str,
    ) -> Any:
        """
        Enter the owning room's action-hook scope when one is available.

        Args:
            category:
                Action category.
            action_name:
                Stable public action name.

        Returns:
            Any: Hook scope context manager.
        """
        try:
            action_scope = self._space._entered_action_hook_scope(
                category=category,
                action_name=action_name,
            )
        except AttributeError:
            yield
            return
        with action_scope:
            yield

    def _resolve_memory_frame_name(
            self,
            frame_name: Optional[str],
    ) -> Optional[str]:
        """
        Resolve the frame name that should be recorded in emitted command memories.

        Args:
            frame_name:
                Optional caller-supplied frame name.

        Returns:
            Optional[str]: Concrete frame name for memory emission, or None when
                the command has no resolvable frame context.
        """
        try:
            return self._resolve_runtime_frame_name(frame_name)
        except Exception:
            return None

    def _assert_raw_runtime_object_access_allowed(
            self,
            method_name: str,
    ) -> None:
        """
        Enforce raw runtime-object access policy for this command surface.

        Contract:
            - Base `CommandSystem` owns the shared raw-runtime getter
              vocabulary and defaults to allowing it.
            - Denials are represented explicitly through the class-level
              `_DENIED_RAW_RUNTIME_OBJECT_ACCESS_METHOD_NAMES` set instead of
              hidden no-op hook overrides.
            - Subclasses that need room-specific wording may override the class
              message template without replacing the assertion method itself.

        Args:
            method_name:
                Public command-system method attempting raw runtime-object
                exposure.

        Returns:
            None.

        Raises:
            ValueError:
                If the requesting method is denied raw runtime-object access in
                the current command-surface mode.
        """
        if method_name not in type(self)._DENIED_RAW_RUNTIME_OBJECT_ACCESS_METHOD_NAMES:
            return
        raise ValueError(
            type(self)._RAW_RUNTIME_OBJECT_ACCESS_DENIED_MESSAGE_TEMPLATE.format(
                method_name
            )
        )

    def _assert_frame_command_enabled(self, frame_name: str) -> None:
        """
        Enforce frame-level command access for one hosted frame.

        Args:
            frame_name:
                Hosted frame whose command gate should be checked.

        Returns:
            None.

        Raises:
            ValueError:
                If the frame does not enable command access.
        """
        compiled_access_surface = self._get_required_compiled_access_surface(frame_name)
        if compiled_access_surface.command_frame_enabled:
            return
        raise ValueError(
            "Command access is disabled for frame '{0}'.".format(frame_name)
        )

    def _assert_conduit_command_enabled(
            self,
            conduit_id: str,
            *,
            frame_name: str,
    ) -> None:
        """
        Enforce conduit-level command access for one published conduit id.

        Args:
            conduit_id:
                Published conduit id being resolved.
            frame_name:
                Hosted frame the conduit belongs to.

        Returns:
            None.

        Raises:
            ValueError:
                If the conduit is not command-enabled in the target frame.
        """
        compiled_access_surface = self._get_required_compiled_access_surface(frame_name)
        if conduit_id in compiled_access_surface.enabled_conduit_ids:
            return
        raise ValueError(
            "Command access to conduit '{0}' is disabled in frame '{1}'.".format(
                conduit_id,
                frame_name,
            )
        )

    def _assert_spell_command_enabled(
            self,
            spell_index_id: str,
            *,
            frame_name: str,
    ) -> None:
        """
        Enforce spell-level command access for one stable spell index id.

        Args:
            spell_index_id:
                Stable spell index id being resolved.
            frame_name:
                Hosted frame the spell belongs to.

        Returns:
            None.

        Raises:
            ValueError:
                If the spell index is not command-enabled in the target
                frame.
        """
        compiled_access_surface = self._get_required_compiled_access_surface(frame_name)
        if spell_index_id in compiled_access_surface.enabled_spell_index_ids:
            return
        raise ValueError(
            "Command access to spell index '{0}' is disabled in frame '{1}'.".format(
                spell_index_id,
                frame_name,
            )
        )

    def _get_enabled_published_conduit_records(
            self,
            frame_name: str,
    ) -> Tuple[Any, ...]:
        """
        Return published conduit records that are command-enabled in one frame.

        Args:
            frame_name:
                Hosted frame to query.

        Returns:
            Tuple[Any, ...]: Published conduit records enabled for command
                access in the target frame.

        Raises:
            ValueError:
                If command access is disabled for the frame.
        """
        self._assert_frame_command_enabled(frame_name)
        compiled_access_surface = self._get_required_compiled_access_surface(frame_name)
        enabled_conduit_ids = set(compiled_access_surface.enabled_conduit_ids)
        descriptor = self._rift._get_required_command_projection(
            frame_name
        ).frame_descriptor
        return tuple(
            conduit_record
            for conduit_record in descriptor.conduit_records_by_id.values()
            if conduit_record.conduit_id in enabled_conduit_ids
        )

    def _get_required_published_conduit_id_by_name(
            self,
            conduit_name: str,
            *,
            frame_name: str,
    ) -> str:
        """
        Return the published conduit id matching one conduit name.

        Contract:
            - Resolves against published descriptor truth, not runtime conduit
              registries.
            - Raises on missing or ambiguous published matches.

        Args:
            conduit_name:
                Published conduit name to resolve.
            frame_name:
                Hosted frame to query.

        Returns:
            str: Published conduit id for the named conduit.

        Raises:
            ValueError:
                If the conduit name is empty, missing, or ambiguous.
        """
        if not conduit_name:
            raise ValueError("conduit_name cannot be empty.")
        descriptor = self._rift._get_required_command_projection(
            frame_name
        ).frame_descriptor
        matching_conduit_ids = [
            conduit_record.conduit_id
            for conduit_record in descriptor.conduit_records_by_id.values()
            if conduit_record.payload.conduit_name == conduit_name
        ]
        if len(matching_conduit_ids) == 0:
            raise ValueError(
                "Conduit name '{0}' was not found in frame '{1}'.".format(
                    conduit_name,
                    frame_name,
                )
            )
        if len(matching_conduit_ids) > 1:
            raise ValueError(
                "Conduit name '{0}' is ambiguous in frame '{1}'.".format(
                    conduit_name,
                    frame_name,
                )
            )
        return matching_conduit_ids[0]

    def _get_required_published_spell_index_id_by_spell_id(
            self,
            spell_id: str,
            *,
            frame_name: str,
    ) -> str:
        """
        Return the stable spell index id matching one published spell id.

        Contract:
            - Resolves through published descriptor truth so ACL checks stay on
              stable spell-index identity.
            - Accepts multiple matching records only when they collapse to one
              spell-index id.

        Args:
            spell_id:
                Current published spell id to resolve.
            frame_name:
                Hosted frame to query.

        Returns:
            str: Stable published spell index id.

        Raises:
            ValueError:
                If the spell id is empty, missing, or ambiguous across
                published lineages.
        """
        if not spell_id:
            raise ValueError("spell_id cannot be empty.")
        descriptor = self._rift._get_required_command_projection(
            frame_name
        ).frame_descriptor
        matching_spell_index_ids = {
            spell_record.spell_index_id
            for spell_record in descriptor.spell_records_by_key.values()
            if spell_record.spell_id == spell_id
        }
        if len(matching_spell_index_ids) == 0:
            raise ValueError(
                "Spell id '{0}' was not found in frame '{1}'.".format(
                    spell_id,
                    frame_name,
                )
            )
        if len(matching_spell_index_ids) > 1:
            raise ValueError(
                "Spell id '{0}' is ambiguous in frame '{1}'.".format(
                    spell_id,
                    frame_name,
                )
            )
        return next(iter(matching_spell_index_ids))

    def _get_required_published_spell_record_by_source_id(
            self,
            spell_source_id: str,
            *,
            frame_name: str,
    ) -> Any:
        """
        Return the published spell record matching one spell source id.

        Args:
            spell_source_id:
                Published spell source id in `spellbook_id:spell_id` form.
            frame_name:
                Hosted frame to query.

        Returns:
            Any: Matching published spell record.
        """
        if not spell_source_id:
            raise ValueError("spell_source_id cannot be empty.")
        if ":" not in spell_source_id:
            raise ValueError(
                "spell_source_id must be in 'spellbook_id:spell_id' form."
            )
        origin_spellbook_id, spell_id = spell_source_id.split(":", 1)
        descriptor = self._rift._get_required_command_projection(
            frame_name
        ).frame_descriptor
        matching_spell_records = [
            spell_record
            for spell_record in descriptor.spell_records_by_key.values()
            if (
                spell_record.origin_spellbook_id == origin_spellbook_id
                and spell_record.spell_id == spell_id
            )
        ]
        if len(matching_spell_records) == 0:
            raise ValueError(
                "Spell '{0}' was not found in frame '{1}'.".format(
                    spell_source_id,
                    frame_name,
                )
            )
        if len(matching_spell_records) > 1:
            raise ValueError(
                "Spell '{0}' is ambiguous in frame '{1}'.".format(
                    spell_source_id,
                    frame_name,
                )
            )
        return matching_spell_records[0]

    def _get_required_compiled_access_surface(
            self,
            frame_name: str,
    ) -> CompiledFrameACLAccessSurface:
        """
        Return the compiled ACL access surface for one hosted frame.

        Args:
            frame_name:
                Hosted frame whose compiled ACL surface is required.

        Returns:
            CompiledFrameACLAccessSurface:
                Compiled frame ACL access surface for the target frame.

        Raises:
            ValueError:
                If the room has no command projection for the requested frame.
        """
        return self._rift._get_required_command_projection(
            frame_name
        ).compiled_access_surface

    def _bind_result(
            self,
            *,
            bind_as_name: str,
            bind_as_store: str,
            value: object,
            bind_result_weak_ref: Optional[bool] = None,
    ) -> None:
        """
        Bind a returned value back into the workstation.

        Contract:
            - Routes binding into exactly one workstation store.
            - Raises for unsupported stores instead of silently discarding the
              value.

        Args:
            bind_as_name:
                Binding name for the returned value.
            bind_as_store:
                Target workstation store.
            value:
                Value to bind.
            bind_result_weak_ref:
                Optional workstation reference-mode override for the bound
                result.

        Returns:
            None.
        """
        if bind_as_store == "objects":
            self._workstation.bind_object(
                bind_as_name,
                value,
                weak_ref=bind_result_weak_ref,
            )
            return
        if bind_as_store == "attributes":
            self._workstation.bind_attribute(
                bind_as_name,
                value,
                weak_ref=bind_result_weak_ref,
            )
            return
        if bind_as_store == "methods":
            self._workstation.bind_method(
                bind_as_name,
                value,
                weak_ref=bind_result_weak_ref,
            )
            return
        raise ValueError(
            "Unsupported workstation store '{0}'.".format(bind_as_store)
        )

    def _resolve_runtime_frame_name(
            self,
            frame_name: Optional[str],
    ) -> str:
        """
        Resolve the runtime frame name for direct Aether-backed getters.

        Args:
            frame_name:
                Optional explicit frame name.

        Returns:
            str: Resolved runtime frame name.
        """
        resolved_frame_name = (
            frame_name
            if frame_name is not None
            else self._rift._get_default_runtime_frame_name()
        )
        if resolved_frame_name is None:
            raise ValueError("Rift has no default runtime frame.")
        return resolved_frame_name

    def _get_required_runtime_frame(self, frame_name: str) -> object:
        """
        Return one live Aether frame by name or raise.

        Args:
            frame_name:
                Runtime frame name to resolve.

        Returns:
            object: Live `AethericFrame`.
        """
        try:
            return self._aether._aetheric_frames[frame_name]
        except KeyError as exc:
            raise ValueError(
                "Aetheric frame '{0}' does not exist.".format(frame_name)
            ) from exc


