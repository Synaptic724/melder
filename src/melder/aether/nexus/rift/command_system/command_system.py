import threading
from contextlib import contextmanager
from typing import Any, Dict, List, Optional, Tuple

from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg
from melder.aether.aether import Aether
from melder.aether.nexus.acl.frame_acl_compiled_access_surface import (
    CompiledFrameACLAccessSurface,
)
from melder.utilities.general_base.cleanable import Cleanable
from melder.utilities.helpers.id_builder import IDBuilder


class CommandSystem(Cleanable):
    """
    Internal

    Room-local command surface for controlled getters and explicit execution.

    Purpose:
        Provide the first command-oriented layer above the viewer/workstation
        split without owning discovery or persistence itself.

    Contract:
        - Uses the owning `Rift` command projections as the command
          substrate.
        - Enforces compiled command ACL state on direct fetch paths before
          exposing frame/conduit/spell runtime objects.
        - Uses the owned workstation for active-target attribute/method getters
          and method execution.
        - Does not store results itself. Callers that want persistence must
          bind returned values into the workstation explicitly.
        - Leaves already-bound workstation objects outside post-bind ACL
          policing; command ACLs gate access before bind.

    Lifecycle:
        Owned by one `RiftSpace`. Cleanup drops references to the owning room
        and workstation but does not clean those children itself.
    """

    __melder_internal__ = _mrg.sentinel
    __slots__ = Cleanable.__slots__ + [
        "_id",
        "_owner_space_id",
        "_lock",
        "_rift",
        "_space",
        "_workstation",
    ]
    _DENIED_RAW_RUNTIME_OBJECT_ACCESS_METHOD_NAMES: frozenset[str] = frozenset()
    _DENIED_TOPOLOGY_MUTATION_METHOD_NAMES: frozenset[str] = frozenset()
    _DENIED_SPELL_ACTIVATION_METHOD_NAMES: frozenset[str] = frozenset()
    _RAW_RUNTIME_OBJECT_ACCESS_DENIED_MESSAGE_TEMPLATE: str = (
        "Command surface does not allow raw runtime-object access method '{0}'."
    )
    _TOPOLOGY_MUTATION_DENIED_MESSAGE_TEMPLATE: str = (
        "Command surface does not allow topology mutation method '{0}'."
    )
    _SPELL_ACTIVATION_DENIED_MESSAGE_TEMPLATE: str = (
        "Command surface does not allow spell activation method '{0}'."
    )
    _aether = Aether()

    def __init__(self, *, rift: Any, space: Any, workstation: Any) -> None:
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
        self._id: str = IDBuilder.create_id()
        self._owner_space_id: str = space.space_id
        self._lock: threading.RLock = threading.RLock()
        self._rift: Any = rift
        self._space: Any = space
        self._workstation: Any = workstation

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
            self._owner_space_id = None
            self._rift = None
            self._space = None
            self._workstation = None
            self._id = None
        self._lock = None

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
    ) -> object:
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
        Resolve one spell runtime object by stable lineage id while the command
        lock is already held.

        Contract:
            - Enforces raw-runtime access plus frame/spell command ACL checks
              before touching runtime conduit state.
            - Resolves through the command projection descriptor truth rather
              than viewer state.
            - Requires the caller to hold `self._lock`.

        Args:
            spell_index_id:
                Stable SpellIndex lineage id to resolve.
            frame_name:
                Resolved hosted frame name.

        Returns:
            object: Live spell runtime object.

        Raises:
            ValueError:
                If the lineage id is empty, unpublished, command-disabled, or
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

    def _get_target_method_locked(self, method_name: str) -> object:
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
            object: Bound callable from the current target.

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
            "get_conduit_cloud",
            "get_conduit_by_id",
            "get_conduit_by_name",
            "list_conduit_ids",
            "list_conduit_names",
            "count_conduits",
            "has_conduit_id",
            "has_conduit_name",
            "find_conduit_id_by_name",
            "create_lesser_conduit",
            "create_cluster",
            "delete_cluster",
            "join_cluster",
            "leave_cluster",
            "list_clusters",
            "link",
            "sever_link",
            "get_links",
            "get_lesser_conduit",
            "get_initiated_conduit",
            "get_provider_conduit",
            "get_initiated_conduits",
            "get_provider_conduits",
            "get_contracted_conduits",
            "get_spell_in_contracts",
            "get_spells_in_contract_by_conduit",
            "get_spells_in_contract_by_conduit_name",
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
            "meld",
            "meld_existing_spell",
            "get_target_attribute",
            "get_target_method",
            "execute_target_method",
        )

    def get_conduit_cloud(
            self,
            *,
            frame_name: Optional[str] = None,
    ) -> object:
        """
        Return the live conduit cloud for one hosted frame.

        Purpose:
            Expose the frame-local conduit discovery mesh through the shared
            command surface so non-static rooms can use the same mediated API
            vocabulary instead of reaching around it.

        Args:
            frame_name:
                Optional frame name. When omitted, the room default frame is
                used.

        Returns:
            object: Live conduit-cloud object for the resolved frame.

        Raises:
            ValueError:
                If command access is disabled for the frame or the current room
                blocks raw runtime-object access.
        """
        self.check_cleaned()
        with self._entered_command_action(
                action_name="get_conduit_cloud",
                frame_name=frame_name,
        ), self._lock:
            resolved_frame_name = self._resolve_runtime_frame_name(frame_name)
            self._assert_raw_runtime_object_access_allowed("get_conduit_cloud")
            self._assert_frame_command_enabled(resolved_frame_name)
            return self._aether.get_conduit_cloud(resolved_frame_name)

    def get_conduit_by_id(
            self,
            conduit_id: str,
            *,
            frame_name: Optional[str] = None,
    ) -> object:
        """
        Return one live conduit object by id, including lesser-conduit fallback.

        Args:
            conduit_id:
                Conduit id to resolve.
            frame_name:
                Optional frame name. When omitted, the room default frame is
                used.

        Returns:
            object: Live conduit object.

        Raises:
            ValueError:
                If the conduit is not published in the selected frame or
                command ACL denies conduit access.
        """
        self.check_cleaned()
        with self._entered_command_action(
                action_name="get_conduit_by_id",
                frame_name=frame_name,
        ), self._lock:
            resolved_frame_name = self._resolve_runtime_frame_name(frame_name)
            return self._get_conduit_by_id_locked(
                conduit_id,
                frame_name=resolved_frame_name,
            )

    def get_conduit_by_name(
            self,
            conduit_name: str,
            *,
            frame_name: Optional[str] = None,
    ) -> object:
        """
        Return one live root/normal conduit object by name.

        Args:
            conduit_name:
                Conduit name to resolve.
            frame_name:
                Optional frame name. When omitted, the room default frame is
                used.

        Returns:
            object: Live conduit object.

        Raises:
            ValueError:
                If the conduit name is not published in the selected frame,
                resolves ambiguously, or command ACL denies access.
        """
        self.check_cleaned()
        with self._entered_command_action(
                action_name="get_conduit_by_name",
                frame_name=frame_name,
        ), self._lock:
            resolved_frame_name = self._resolve_runtime_frame_name(frame_name)
            self._assert_raw_runtime_object_access_allowed("get_conduit_by_name")
            self._assert_frame_command_enabled(resolved_frame_name)
            conduit_id = self._get_required_published_conduit_id_by_name(
                conduit_name,
                frame_name=resolved_frame_name,
            )
            self._assert_conduit_command_enabled(
                conduit_id,
                frame_name=resolved_frame_name,
            )
            return self._aether.get_conduit_by_name(
                conduit_name,
                resolved_frame_name,
            )

    def create_lesser_conduit(
            self,
            conduit_id: str,
            *,
            frame_name: Optional[str] = None,
    ) -> object:
        """
        Create one lesser conduit beneath an existing conduit.

        Purpose:
            Provide the shared manual-runtime command seam for lesser-conduit
            creation without forcing callers to fetch a conduit first and then
            call into it directly.

        Args:
            conduit_id:
                Conduit id that should own the new lesser conduit.
            frame_name:
                Optional frame name. When omitted, the room default frame is
                used.

        Returns:
            object: Newly created lesser conduit object.

        Raises:
            ValueError:
                If the current room denies runtime topology mutation or the
                conduit cannot be resolved through the command surface.
        """
        self.check_cleaned()
        with self._entered_command_action(
                action_name="create_lesser_conduit",
                frame_name=frame_name,
        ), self._lock:
            self._assert_topology_mutation_allowed("create_lesser_conduit")
            resolved_frame_name = self._resolve_runtime_frame_name(frame_name)
            conduit = self._get_conduit_by_id_locked(
                conduit_id,
                frame_name=resolved_frame_name,
            )
            return conduit.create_lesser_conduit()

    def create_cluster(
            self,
            conduit_id: str,
            cluster_name: str,
            *,
            frame_name: Optional[str] = None,
    ) -> None:
        """
        Create one cluster through an existing conduit.

        Args:
            conduit_id:
                Conduit id that should issue the cluster creation request.
            cluster_name:
                Cluster name to create.
            frame_name:
                Optional frame name. When omitted, the room default frame is
                used.

        Returns:
            None.

        Raises:
            ValueError:
                If the current room denies runtime topology mutation or the
                conduit cannot be resolved through the command surface.
        """
        self.check_cleaned()
        with self._entered_command_action(
                action_name="create_cluster",
                frame_name=frame_name,
        ), self._lock:
            self._assert_topology_mutation_allowed("create_cluster")
            resolved_frame_name = self._resolve_runtime_frame_name(frame_name)
            conduit = self._get_conduit_by_id_locked(
                conduit_id,
                frame_name=resolved_frame_name,
            )
            conduit.create_cluster(cluster_name)

    def delete_cluster(
            self,
            conduit_id: str,
            cluster_name: str,
            *,
            frame_name: Optional[str] = None,
    ) -> None:
        """
        Delete one cluster through an existing conduit.

        Args:
            conduit_id:
                Conduit id that should issue the cluster deletion request.
            cluster_name:
                Cluster name to delete.
            frame_name:
                Optional frame name. When omitted, the room default frame is
                used.

        Returns:
            None.
        """
        self.check_cleaned()
        with self._entered_command_action(
                action_name="delete_cluster",
                frame_name=frame_name,
        ), self._lock:
            self._assert_topology_mutation_allowed("delete_cluster")
            resolved_frame_name = self._resolve_runtime_frame_name(frame_name)
            conduit = self._get_conduit_by_id_locked(
                conduit_id,
                frame_name=resolved_frame_name,
            )
            conduit.delete_cluster(cluster_name)

    def join_cluster(
            self,
            conduit_id: str,
            cluster_name: str,
            *,
            frame_name: Optional[str] = None,
    ) -> None:
        """
        Join one conduit to one cluster through the shared command surface.

        Args:
            conduit_id:
                Conduit id that should join the cluster.
            cluster_name:
                Cluster name to join.
            frame_name:
                Optional frame name. When omitted, the room default frame is
                used.

        Returns:
            None.
        """
        self.check_cleaned()
        with self._entered_command_action(
                action_name="join_cluster",
                frame_name=frame_name,
        ), self._lock:
            self._assert_topology_mutation_allowed("join_cluster")
            resolved_frame_name = self._resolve_runtime_frame_name(frame_name)
            conduit = self._get_conduit_by_id_locked(
                conduit_id,
                frame_name=resolved_frame_name,
            )
            conduit.join_cluster(cluster_name)

    def leave_cluster(
            self,
            conduit_id: str,
            cluster_name: str,
            *,
            frame_name: Optional[str] = None,
    ) -> None:
        """
        Remove one conduit from one cluster through the shared command surface.

        Args:
            conduit_id:
                Conduit id that should leave the cluster.
            cluster_name:
                Cluster name to leave.
            frame_name:
                Optional frame name. When omitted, the room default frame is
                used.

        Returns:
            None.
        """
        self.check_cleaned()
        with self._entered_command_action(
                action_name="leave_cluster",
                frame_name=frame_name,
        ), self._lock:
            self._assert_topology_mutation_allowed("leave_cluster")
            resolved_frame_name = self._resolve_runtime_frame_name(frame_name)
            conduit = self._get_conduit_by_id_locked(
                conduit_id,
                frame_name=resolved_frame_name,
            )
            conduit.leave_cluster(cluster_name)

    def list_clusters(
            self,
            conduit_id: str,
            *,
            frame_name: Optional[str] = None,
    ) -> Tuple[str, ...]:
        """
        Return the cluster names visible from one conduit.

        Args:
            conduit_id:
                Conduit id whose cluster membership view should be queried.
            frame_name:
                Optional frame name. When omitted, the room default frame is
                used.

        Returns:
            Tuple[str, ...]: Cluster names visible from the conduit.
        """
        self.check_cleaned()
        with self._entered_command_action(
                action_name="list_clusters",
                frame_name=frame_name,
        ), self._lock:
            resolved_frame_name = self._resolve_runtime_frame_name(frame_name)
            conduit = self._get_conduit_by_id_locked(
                conduit_id,
                frame_name=resolved_frame_name,
            )
            return tuple(conduit.list_clusters())

    def link(
            self,
            source_conduit_id: str,
            target_conduit_id: str,
            *,
            frame_name: Optional[str] = None,
    ) -> bool:
        """
        Link two conduits through the shared command surface.

        Args:
            source_conduit_id:
                Conduit id that should initiate the link.
            target_conduit_id:
                Target conduit id.
            frame_name:
                Optional frame name. When omitted, the room default frame is
                used.

        Returns:
            bool: True when the link succeeds.
        """
        self.check_cleaned()
        with self._entered_command_action(
                action_name="link",
                frame_name=frame_name,
        ), self._lock:
            self._assert_topology_mutation_allowed("link")
            resolved_frame_name = self._resolve_runtime_frame_name(frame_name)
            source_conduit = self._get_conduit_by_id_locked(
                source_conduit_id,
                frame_name=resolved_frame_name,
            )
            target_conduit = self._get_conduit_by_id_locked(
                target_conduit_id,
                frame_name=resolved_frame_name,
            )
            return source_conduit.link(target_conduit)

    def sever_link(
            self,
            source_conduit_id: str,
            target_conduit_id: str,
            *,
            frame_name: Optional[str] = None,
    ) -> bool:
        """
        Sever one conduit link through the shared command surface.

        Args:
            source_conduit_id:
                Conduit id that owns the link to sever.
            target_conduit_id:
                Target conduit id.
            frame_name:
                Optional frame name. When omitted, the room default frame is
                used.

        Returns:
            bool: True when the link is removed.
        """
        self.check_cleaned()
        with self._entered_command_action(
                action_name="sever_link",
                frame_name=frame_name,
        ), self._lock:
            self._assert_topology_mutation_allowed("sever_link")
            resolved_frame_name = self._resolve_runtime_frame_name(frame_name)
            source_conduit = self._get_conduit_by_id_locked(
                source_conduit_id,
                frame_name=resolved_frame_name,
            )
            target_conduit = self._get_conduit_by_id_locked(
                target_conduit_id,
                frame_name=resolved_frame_name,
            )
            return source_conduit.sever_link(target_conduit)

    def get_links(
            self,
            conduit_id: str,
            *,
            frame_name: Optional[str] = None,
    ) -> Tuple[object, ...]:
        """
        Return the current peer links for one conduit.

        Args:
            conduit_id:
                Conduit id whose peer links should be returned.
            frame_name:
                Optional frame name. When omitted, the room default frame is
                used.

        Returns:
            Tuple[object, ...]: Linked conduit objects.
        """
        self.check_cleaned()
        with self._entered_command_action(
                action_name="get_links",
                frame_name=frame_name,
        ), self._lock:
            resolved_frame_name = self._resolve_runtime_frame_name(frame_name)
            conduit = self._get_conduit_by_id_locked(
                conduit_id,
                frame_name=resolved_frame_name,
            )
            return tuple(conduit.get_links())

    def get_lesser_conduit(
            self,
            parent_conduit_id: str,
            conduit_id: str,
            *,
            frame_name: Optional[str] = None,
    ) -> object:
        """
        Return one lesser conduit linked beneath a parent conduit.

        Args:
            parent_conduit_id:
                Parent conduit id that owns the lesser lineage.
            conduit_id:
                Lesser conduit id to resolve.
            frame_name:
                Optional frame name. When omitted, the room default frame is
                used.

        Returns:
            object: Matching lesser conduit object, or None when missing.
        """
        self.check_cleaned()
        with self._entered_command_action(
                action_name="get_lesser_conduit",
                frame_name=frame_name,
        ), self._lock:
            resolved_frame_name = self._resolve_runtime_frame_name(frame_name)
            conduit = self._get_conduit_by_id_locked(
                parent_conduit_id,
                frame_name=resolved_frame_name,
            )
            return conduit.get_lesser_conduit(conduit_id)

    def get_initiated_conduit(
            self,
            conduit_id: str,
            peer_conduit_id: str,
            *,
            frame_name: Optional[str] = None,
    ) -> object:
        """
        Return one outbound linked conduit from a source conduit.

        Purpose:
            Expose the lower conduit-to-peer initiation lookup through the
            shared command surface without forcing callers to fetch the conduit
            first and then navigate it manually.

        Contract:
            - Resolves the source conduit through the command projection and
              command ACL before touching runtime conduit state.
            - Returns the concrete linked conduit object chosen by the lower
              conduit runtime.
            - Uses one top-level command action boundary for gate admission and
              memory emission.

        Args:
            conduit_id:
                Source conduit id whose outbound link set should be queried.
            peer_conduit_id:
                Peer conduit id to resolve from the source conduit's initiated
                links.
            frame_name:
                Optional frame name. When omitted, the room default frame is
                used.

        Returns:
            object: Matching outbound linked conduit object.
        """
        self.check_cleaned()
        with self._entered_command_action(
                action_name="get_initiated_conduit",
                frame_name=frame_name,
        ), self._lock:
            resolved_frame_name = self._resolve_runtime_frame_name(frame_name)
            conduit = self._get_conduit_by_id_locked(
                conduit_id,
                frame_name=resolved_frame_name,
            )
            return conduit.get_initiated_conduit(peer_conduit_id)

    def get_provider_conduit(
            self,
            conduit_id: str,
            peer_conduit_id: str,
            *,
            frame_name: Optional[str] = None,
    ) -> object:
        """
        Return one inbound provider conduit for a source conduit.

        Purpose:
            Expose the lower provider-link lookup through the shared command
            surface for callers that need the inbound peer object directly.

        Contract:
            - Resolves the source conduit through the command projection and
              command ACL before touching runtime conduit state.
            - Returns the provider conduit chosen by the lower conduit runtime.
            - Uses one top-level command action boundary for gate admission and
              memory emission.

        Args:
            conduit_id:
                Source conduit id whose inbound provider link set should be
                queried.
            peer_conduit_id:
                Peer conduit id to resolve from the source conduit's provider
                links.
            frame_name:
                Optional frame name. When omitted, the room default frame is
                used.

        Returns:
            object: Matching inbound provider conduit object.
        """
        self.check_cleaned()
        with self._entered_command_action(
                action_name="get_provider_conduit",
                frame_name=frame_name,
        ), self._lock:
            resolved_frame_name = self._resolve_runtime_frame_name(frame_name)
            conduit = self._get_conduit_by_id_locked(
                conduit_id,
                frame_name=resolved_frame_name,
            )
            return conduit.get_provider_conduit(peer_conduit_id)

    def get_initiated_conduits(
            self,
            conduit_id: str,
            *,
            frame_name: Optional[str] = None,
    ) -> Tuple[object, ...]:
        """
        Return the outbound linked conduits for one conduit.

        Purpose:
            Provide the full outbound link set for one conduit through the
            shared command surface.

        Contract:
            - Resolves the source conduit through command ACL and descriptor
              truth before touching runtime conduit state.
            - Returns a detached tuple preserving the lower conduit runtime's
              current outbound links.
            - Uses one top-level command action boundary for gate admission and
              memory emission.

        Args:
            conduit_id:
                Source conduit id whose outbound links should be returned.
            frame_name:
                Optional frame name. When omitted, the room default frame is
                used.

        Returns:
            Tuple[object, ...]: Outbound linked conduit objects.
        """
        self.check_cleaned()
        with self._entered_command_action(
                action_name="get_initiated_conduits",
                frame_name=frame_name,
        ), self._lock:
            resolved_frame_name = self._resolve_runtime_frame_name(frame_name)
            conduit = self._get_conduit_by_id_locked(
                conduit_id,
                frame_name=resolved_frame_name,
            )
            return tuple(conduit.get_initiated_conduits())

    def get_provider_conduits(
            self,
            conduit_id: str,
            *,
            frame_name: Optional[str] = None,
    ) -> Tuple[object, ...]:
        """
        Return the inbound provider conduits for one conduit.

        Purpose:
            Provide the full inbound provider-link set for one conduit through
            the shared command surface.

        Contract:
            - Resolves the source conduit through command ACL and descriptor
              truth before touching runtime conduit state.
            - Returns a detached tuple preserving the lower conduit runtime's
              current provider links.
            - Uses one top-level command action boundary for gate admission and
              memory emission.

        Args:
            conduit_id:
                Source conduit id whose inbound provider links should be
                returned.
            frame_name:
                Optional frame name. When omitted, the room default frame is
                used.

        Returns:
            Tuple[object, ...]: Inbound provider conduit objects.
        """
        self.check_cleaned()
        with self._entered_command_action(
                action_name="get_provider_conduits",
                frame_name=frame_name,
        ), self._lock:
            resolved_frame_name = self._resolve_runtime_frame_name(frame_name)
            conduit = self._get_conduit_by_id_locked(
                conduit_id,
                frame_name=resolved_frame_name,
            )
            return tuple(conduit.get_provider_conduits())

    def get_contracted_conduits(
            self,
            conduit_id: str,
            *,
            frame_name: Optional[str] = None,
    ) -> object:
        """
        Return the contracted peer conduits for one conduit.

        Purpose:
            Expose the lower conduit contract view directly on the shared
            command surface for callers that need the current contracted peers.

        Contract:
            - Resolves the source conduit through command ACL and descriptor
              truth before touching runtime conduit state.
            - Returns whatever contract collection object the lower conduit
              runtime exposes without rebinding or snapshotting it.
            - Uses one top-level command action boundary for gate admission and
              memory emission.

        Args:
            conduit_id:
                Source conduit id whose contracted peers should be returned.
            frame_name:
                Optional frame name. When omitted, the room default frame is
                used.

        Returns:
            object: Lower-runtime contracted conduit collection.
        """
        self.check_cleaned()
        with self._entered_command_action(
                action_name="get_contracted_conduits",
                frame_name=frame_name,
        ), self._lock:
            resolved_frame_name = self._resolve_runtime_frame_name(frame_name)
            conduit = self._get_conduit_by_id_locked(
                conduit_id,
                frame_name=resolved_frame_name,
            )
            return conduit.get_contracted_conduits()

    def get_spell_in_contracts(
            self,
            conduit_id: str,
            spell_id: str,
            *,
            frame_name: Optional[str] = None,
    ) -> object:
        """
        Return one contracted spell lookup result from a conduit.

        Purpose:
            Mirror the lower conduit spell-in-contract lookup on the shared
            command surface.

        Contract:
            - Resolves the conduit through command ACL and descriptor truth
              before touching runtime conduit state.
            - Defers spell-specific contract semantics to the lower conduit
              runtime instead of re-implementing them in the command surface.
            - Uses one top-level command action boundary for gate admission and
              memory emission.

        Args:
            conduit_id:
                Source conduit id whose contract view should be queried.
            spell_id:
                Current spell id to resolve inside the conduit's contract set.
            frame_name:
                Optional frame name. When omitted, the room default frame is
                used.

        Returns:
            object: Lower-runtime spell-in-contract lookup result.
        """
        self.check_cleaned()
        with self._entered_command_action(
                action_name="get_spell_in_contracts",
                frame_name=frame_name,
        ), self._lock:
            resolved_frame_name = self._resolve_runtime_frame_name(frame_name)
            conduit = self._get_conduit_by_id_locked(
                conduit_id,
                frame_name=resolved_frame_name,
            )
            return conduit.get_spell_in_contracts(spell_id)

    def get_spells_in_contract_by_conduit(
            self,
            conduit_id: str,
            peer_conduit_id: str,
            *,
            frame_name: Optional[str] = None,
    ) -> object:
        """
        Return contracted spell data keyed by peer conduit id.

        Purpose:
            Expose conduit-to-peer contract spell data through the shared
            command surface without requiring callers to walk the runtime
            conduit object manually.

        Contract:
            - Resolves the source conduit through command ACL and descriptor
              truth before touching runtime conduit state.
            - Defers contract payload shape to the lower conduit runtime.
            - Uses one top-level command action boundary for gate admission and
              memory emission.

        Args:
            conduit_id:
                Source conduit id whose contract table should be queried.
            peer_conduit_id:
                Peer conduit id whose contract spell data should be returned.
            frame_name:
                Optional frame name. When omitted, the room default frame is
                used.

        Returns:
            object: Lower-runtime contract spell payload for the peer conduit.
        """
        self.check_cleaned()
        with self._entered_command_action(
                action_name="get_spells_in_contract_by_conduit",
                frame_name=frame_name,
        ), self._lock:
            resolved_frame_name = self._resolve_runtime_frame_name(frame_name)
            conduit = self._get_conduit_by_id_locked(
                conduit_id,
                frame_name=resolved_frame_name,
            )
            return conduit.get_spells_in_contract_by_conduit(peer_conduit_id)

    def get_spells_in_contract_by_conduit_name(
            self,
            conduit_id: str,
            conduit_name: str,
            *,
            frame_name: Optional[str] = None,
    ) -> object:
        """
        Return contracted spell data keyed by peer conduit name.

        Purpose:
            Expose conduit-to-peer-name contract spell data through the shared
            command surface.

        Contract:
            - Resolves the source conduit through command ACL and descriptor
              truth before touching runtime conduit state.
            - Defers payload shape and peer-name resolution semantics to the
              lower conduit runtime.
            - Uses one top-level command action boundary for gate admission and
              memory emission.

        Args:
            conduit_id:
                Source conduit id whose contract table should be queried.
            conduit_name:
                Peer conduit name whose contract spell data should be returned.
            frame_name:
                Optional frame name. When omitted, the room default frame is
                used.

        Returns:
            object: Lower-runtime contract spell payload for the peer name.
        """
        self.check_cleaned()
        with self._entered_command_action(
                action_name="get_spells_in_contract_by_conduit_name",
                frame_name=frame_name,
        ), self._lock:
            resolved_frame_name = self._resolve_runtime_frame_name(frame_name)
            conduit = self._get_conduit_by_id_locked(
                conduit_id,
                frame_name=resolved_frame_name,
            )
            return conduit.get_spells_in_contract_by_conduit_name(conduit_name)

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

    def list_conduit_ids(
            self,
            *,
            frame_name: Optional[str] = None,
    ) -> Tuple[str, ...]:
        """
        Return the command-enabled published conduit ids for one frame.

        Args:
            frame_name:
                Optional frame name. When omitted, the room default frame is
                used.

        Returns:
            Tuple[str, ...]: Published command-enabled conduit ids.
        """
        self.check_cleaned()
        with self._entered_command_action(
                action_name="list_conduit_ids",
                frame_name=frame_name,
        ), self._lock:
            resolved_frame_name = self._resolve_runtime_frame_name(frame_name)
            conduit_records = self._get_enabled_published_conduit_records(
                resolved_frame_name
            )
            return tuple(record.conduit_id for record in conduit_records)

    def list_conduit_names(
            self,
            *,
            frame_name: Optional[str] = None,
    ) -> Tuple[str, ...]:
        """
        Return the command-enabled published conduit names for one frame.

        Args:
            frame_name:
                Optional frame name. When omitted, the room default frame is
                used.

        Returns:
            Tuple[str, ...]: Published command-enabled conduit names.
        """
        self.check_cleaned()
        with self._entered_command_action(
                action_name="list_conduit_names",
                frame_name=frame_name,
        ), self._lock:
            resolved_frame_name = self._resolve_runtime_frame_name(frame_name)
            conduit_records = self._get_enabled_published_conduit_records(
                resolved_frame_name
            )
            return tuple(
                record.payload.conduit_name
                for record in conduit_records
                if record.payload.conduit_name is not None
            )

    def count_conduits(
            self,
            *,
            frame_name: Optional[str] = None,
    ) -> int:
        """
        Return the number of command-enabled published conduits for one frame.

        Args:
            frame_name:
                Optional frame name. When omitted, the room default frame is
                used.

        Returns:
            int: Number of published command-enabled conduits.
        """
        self.check_cleaned()
        with self._entered_command_action(
                action_name="count_conduits",
                frame_name=frame_name,
        ), self._lock:
            resolved_frame_name = self._resolve_runtime_frame_name(frame_name)
            conduit_records = self._get_enabled_published_conduit_records(
                resolved_frame_name
            )
            return len(conduit_records)

    def has_conduit_id(
            self,
            conduit_id: str,
            *,
            frame_name: Optional[str] = None,
    ) -> bool:
        """
        Return whether one published command-enabled conduit id exists.

        Args:
            conduit_id:
                Conduit id to check.
            frame_name:
                Optional frame name. When omitted, the room default frame is
                used.

        Returns:
            bool: True when the conduit id is published and command-enabled.
        """
        self.check_cleaned()
        with self._entered_command_action(
                action_name="has_conduit_id",
                frame_name=frame_name,
        ), self._lock:
            resolved_frame_name = self._resolve_runtime_frame_name(frame_name)
            conduit_records = self._get_enabled_published_conduit_records(
                resolved_frame_name
            )
            return any(record.conduit_id == conduit_id for record in conduit_records)

    def has_conduit_name(
            self,
            conduit_name: str,
            *,
            frame_name: Optional[str] = None,
    ) -> bool:
        """
        Return whether one published command-enabled conduit name exists.

        Args:
            conduit_name:
                Conduit name to check.
            frame_name:
                Optional frame name. When omitted, the room default frame is
                used.

        Returns:
            bool: True when the conduit name is published and command-enabled.
        """
        self.check_cleaned()
        with self._entered_command_action(
                action_name="has_conduit_name",
                frame_name=frame_name,
        ), self._lock:
            resolved_frame_name = self._resolve_runtime_frame_name(frame_name)
            conduit_records = self._get_enabled_published_conduit_records(
                resolved_frame_name
            )
            return any(
                record.payload.conduit_name == conduit_name
                for record in conduit_records
            )

    def find_conduit_id_by_name(
            self,
            conduit_name: str,
            *,
            frame_name: Optional[str] = None,
    ) -> Optional[str]:
        """
        Return the published command-enabled conduit id for one conduit name.

        Args:
            conduit_name:
                Conduit name to resolve.
            frame_name:
                Optional frame name. When omitted, the room default frame is
                used.

        Returns:
            Optional[str]: Matching conduit id, or None when missing.

        Raises:
            ValueError: If the conduit name resolves ambiguously.
        """
        self.check_cleaned()
        with self._entered_command_action(
                action_name="find_conduit_id_by_name",
                frame_name=frame_name,
        ), self._lock:
            resolved_frame_name = self._resolve_runtime_frame_name(frame_name)
            self._assert_frame_command_enabled(resolved_frame_name)
            try:
                conduit_id = self._get_required_published_conduit_id_by_name(
                    conduit_name,
                    frame_name=resolved_frame_name,
                )
            except ValueError as exc:
                if "was not found" in str(exc):
                    return None
                raise
            compiled_access_surface = self._get_required_compiled_access_surface(
                resolved_frame_name
            )
            if conduit_id in compiled_access_surface.enabled_conduit_ids:
                return conduit_id
            return None

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
                Stable SpellIndex lineage id to resolve.
            frame_name:
                Optional frame name. When omitted, the room default frame is
                used.

        Returns:
            object: Live spell object.

        Raises:
            ValueError:
                If the spell lineage is not published in the selected frame or
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
                if spell_index.has_version(spell_id):
                    return spell
            raise ValueError(
                "Spell id '{0}' was not found in the owner spellbook.".format(spell_id)
            )

    def meld(
            self,
            conduit_id: str,
            spell_name: Optional[str] = None,
            *,
            spell: Optional[object] = None,
            spellframe: Optional[object] = None,
            binding_name: Optional[str] = None,
            frame_name: Optional[str] = None,
            spell_override: Optional[dict | list | tuple] = None,
    ) -> object:
        """
        Resolve and activate one spell through a command-selected conduit.

        Purpose:
            Mirror the lower `Conduit.meld(...)` API on the shared command
            surface without inventing a command-only alias.

        Args:
            conduit_id:
                Conduit id that should perform the meld.
            spell_name:
                Optional logical spell name key.
            spell:
                Optional spell id string or spell object.
            spellframe:
                Optional spellframe / protocol / frame key.
            binding_name:
                Optional binding name for resolution.
            frame_name:
                Optional hosted frame name. When omitted, the room default
                frame is used.
            spell_override:
                Optional per-call override payload forwarded to the conduit.

        Returns:
            object: Activated runtime object returned by the conduit meld path.
        """
        self.check_cleaned()
        with self._entered_command_action(
                action_name="meld",
                frame_name=frame_name,
        ), self._lock:
            self._assert_spell_activation_allowed("meld")
            resolved_frame_name = self._resolve_runtime_frame_name(frame_name)
            conduit = self._get_conduit_by_id_locked(
                conduit_id,
                frame_name=resolved_frame_name,
            )
            return conduit.meld(
                spell_name=spell_name,
                spell=spell,
                spellframe=spellframe,
                binding_name=binding_name,
                spell_override=spell_override,
            )

    def meld_existing_spell(
            self,
            conduit_id: str,
            spell_name: Optional[str] = None,
            *,
            spell: Optional[object] = None,
            spellframe: Optional[object] = None,
            binding_name: Optional[str] = None,
            frame_name: Optional[str] = None,
    ) -> object:
        """
        Return one already-live spell runtime object through a selected conduit.

        Purpose:
            Mirror the lower `Conduit.meld_existing_spell(...)` API on the
            shared command surface.

        Args:
            conduit_id:
                Conduit id that should perform the reuse-only resolution.
            spell_name:
                Optional logical spell name key.
            spell:
                Optional spell id string or spell object.
            spellframe:
                Optional spellframe / protocol / frame key.
            binding_name:
                Optional binding name for resolution.
            frame_name:
                Optional hosted frame name. When omitted, the room default
                frame is used.

        Returns:
            object: Already-live runtime object returned by the conduit.
        """
        self.check_cleaned()
        with self._entered_command_action(
                action_name="meld_existing_spell",
                frame_name=frame_name,
        ), self._lock:
            self._assert_spell_activation_allowed("meld_existing_spell")
            resolved_frame_name = self._resolve_runtime_frame_name(frame_name)
            conduit = self._get_conduit_by_id_locked(
                conduit_id,
                frame_name=resolved_frame_name,
            )
            return conduit.meld_existing_spell(
                spell_name=spell_name,
                spell=spell,
                spellframe=spellframe,
                binding_name=binding_name,
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

    def get_target_method(self, method_name: str) -> object:
        """
        Return one method/callable from the current workstation target.

        Args:
            method_name:
                Method name to retrieve from the active target.

        Returns:
            object: Bound callable from the target.

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
        rift_gate.admit()
        rift_gate.register_ticket()
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

    def _assert_topology_mutation_allowed(
            self,
            method_name: str,
    ) -> None:
        """
        Enforce topology-mutation policy for this command surface.

        Contract:
            - Base `CommandSystem` owns the shared topology-mutation
              vocabulary and defaults to allowing it.
            - Denials are represented explicitly through the class-level
              `_DENIED_TOPOLOGY_MUTATION_METHOD_NAMES` set instead of hidden
              no-op hook overrides.
            - Subclasses that need room-specific wording may override the class
              message template without replacing the assertion method itself.

        Args:
            method_name:
                Public topology-mutation method being attempted.

        Returns:
            None.

        Raises:
            ValueError:
                If the requesting topology-mutation command is denied in the
                current command-surface mode.
        """
        if method_name not in type(self)._DENIED_TOPOLOGY_MUTATION_METHOD_NAMES:
            return
        raise ValueError(
            type(self)._TOPOLOGY_MUTATION_DENIED_MESSAGE_TEMPLATE.format(
                method_name
            )
        )

    def _assert_spell_activation_allowed(
            self,
            method_name: str,
    ) -> None:
        """
        Enforce direct spell-activation policy for this command surface.

        Contract:
            - Base `CommandSystem` owns the shared spell-activation
              vocabulary and defaults to allowing it.
            - Denials are represented explicitly through the class-level
              `_DENIED_SPELL_ACTIVATION_METHOD_NAMES` set instead of hidden
              no-op hook overrides.
            - Subclasses that need room-specific wording may override the class
              message template without replacing the assertion method itself.

        Args:
            method_name:
                Direct spell-activation method being attempted.

        Returns:
            None.

        Raises:
            ValueError:
                If the requesting spell-activation command is denied in the
                current command-surface mode.
        """
        if method_name not in type(self)._DENIED_SPELL_ACTIVATION_METHOD_NAMES:
            return
        raise ValueError(
            type(self)._SPELL_ACTIVATION_DENIED_MESSAGE_TEMPLATE.format(
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
        Enforce spell-level command access for one stable spell lineage id.

        Args:
            spell_index_id:
                Stable spell lineage id being resolved.
            frame_name:
                Hosted frame the spell belongs to.

        Returns:
            None.

        Raises:
            ValueError:
                If the spell lineage is not command-enabled in the target
                frame.
        """
        compiled_access_surface = self._get_required_compiled_access_surface(frame_name)
        if spell_index_id in compiled_access_surface.enabled_spell_index_ids:
            return
        raise ValueError(
            "Command access to spell lineage '{0}' is disabled in frame '{1}'.".format(
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
        Return the stable spell lineage id matching one published spell id.

        Contract:
            - Resolves through published descriptor truth so ACL checks stay on
              stable lineage identity.
            - Accepts multiple matching records only when they collapse to one
              lineage id.

        Args:
            spell_id:
                Current published spell id to resolve.
            frame_name:
                Hosted frame to query.

        Returns:
            str: Stable published spell lineage id.

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
