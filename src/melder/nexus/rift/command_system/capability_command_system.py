from typing import Optional, Tuple
from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg

from melder.nexus.rift.command_system.command_system import CommandSystem


class CapabilityCommandSystem(CommandSystem):
    """
    Internal

    Capability-room command surface.

    Purpose:
        Own the broad manual-runtime command surface for
        `CapabilityRiftSpace`.

    Contract:
        - Inherits shared command infrastructure plus truly shared public
          helpers from `CommandSystem`.
        - Owns topology mutation, cluster, direct `meld(...)`, and reuse-only
          `meld_existing_spell(...)` command methods explicitly.
        - Represents the broad manual-runtime posture between static and later
          slimmer codegen command surfaces.
    """

    __melder_internal__ = _mrg.sentinel
    _CAPABILITY_COMMAND_METHOD_NAMES: Tuple[str, ...] = (
        "get_conduit_cloud",
        "get_conduit_by_id",
        "get_conduit_by_name",
        "list_conduit_ids",
        "list_conduit_names",
        "count_conduits",
        "has_conduit_id",
        "has_conduit_name",
        "find_conduit_id_by_name",
        "get_links",
        "create_lesser_conduit",
        "create_cluster",
        "delete_cluster",
        "join_cluster",
        "leave_cluster",
        "list_clusters",
        "link",
        "sever_link",
        "get_lesser_conduit",
        "get_initiated_conduit",
        "get_provider_conduit",
        "get_initiated_conduits",
        "get_provider_conduits",
        "get_contracted_conduits",
        "get_spell_in_contracts",
        "get_spells_in_contract_by_conduit",
        "get_spells_in_contract_by_conduit_name",
        "meld",
        "meld_existing_spell",
        # Research reads (capability rooms carry the reads ONLY)
        "research_walk",
        "research_history",
        "research_heads",
        "research_residency",
        "research_diff",
        "research_campaign_view",
        "research_source",
        "research_impact",
        "research_module_graph",
        "research_source_drift",
        "research_module",
        "research_part",
        "research_parts",
        "research_part_diff",
        "research_group_view",
        "research_group_diff",
        "research_group_impact",
    )

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

    def get_conduit_cloud(
            self,
            *,
            frame_name: Optional[str] = None,
    ) -> object:
        """
        Return the live conduit cloud for one hosted frame.

        Args:
            frame_name:
                Optional frame name. When omitted, the room default frame is
                used.

        Returns:
            object: Live conduit-cloud object for the resolved frame.
        """
        self.check_cleaned()
        with self._entered_command_action(
                action_name="get_conduit_cloud",
                frame_name=frame_name,
        ), self._lock:
            resolved_frame_name = self._resolve_runtime_frame_name(frame_name)
            self._assert_raw_runtime_object_access_allowed("get_conduit_cloud")
            self._assert_frame_command_enabled(resolved_frame_name)
            frame = self._aether._get_existing_frame(resolved_frame_name)
            return frame._conduit_cloud

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

    def create_lesser_conduit(
            self,
            conduit_id: str,
            *,
            frame_name: Optional[str] = None,
    ) -> object:
        """
        Create one lesser conduit beneath an existing conduit.

        Purpose:
            Provide the capability-room manual runtime seam for lesser-conduit
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
        """
        self.check_cleaned()
        with self._entered_command_action(
                action_name="create_lesser_conduit",
                frame_name=frame_name,
        ), self._lock:
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
        """
        self.check_cleaned()
        with self._entered_command_action(
                action_name="create_cluster",
                frame_name=frame_name,
        ), self._lock:
            resolved_frame_name = self._resolve_runtime_frame_name(frame_name)
            self._get_conduit_by_id_locked(
                conduit_id,
                frame_name=resolved_frame_name,
            )
            conduit_cloud = self._aether.get_conduit_cloud(resolved_frame_name)
            conduit_cloud.create_cluster(cluster_name)

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
            resolved_frame_name = self._resolve_runtime_frame_name(frame_name)
            self._get_conduit_by_id_locked(
                conduit_id,
                frame_name=resolved_frame_name,
            )
            conduit_cloud = self._aether.get_conduit_cloud(resolved_frame_name)
            conduit_cloud.delete_cluster(cluster_name)

    def join_cluster(
            self,
            conduit_id: str,
            cluster_name: str,
            *,
            frame_name: Optional[str] = None,
    ) -> None:
        """
        Join one conduit to one cluster through the capability command surface.

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
            resolved_frame_name = self._resolve_runtime_frame_name(frame_name)
            conduit = self._get_conduit_by_id_locked(
                conduit_id,
                frame_name=resolved_frame_name,
            )
            conduit_cloud = self._aether.get_conduit_cloud(resolved_frame_name)
            conduit_cloud.add_conduit_to_cluster(conduit, cluster_name)

    def leave_cluster(
            self,
            conduit_id: str,
            cluster_name: str,
            *,
            frame_name: Optional[str] = None,
    ) -> None:
        """
        Remove one conduit from one cluster through the capability command surface.

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
            resolved_frame_name = self._resolve_runtime_frame_name(frame_name)
            conduit = self._get_conduit_by_id_locked(
                conduit_id,
                frame_name=resolved_frame_name,
            )
            conduit_cloud = self._aether.get_conduit_cloud(resolved_frame_name)
            conduit_cloud.remove_conduit_from_cluster(conduit, cluster_name)

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
            self._get_conduit_by_id_locked(
                conduit_id,
                frame_name=resolved_frame_name,
            )
            conduit_cloud = self._aether.get_conduit_cloud(resolved_frame_name)
            return tuple(conduit_cloud.get_clusters_for_conduit(conduit_id))

    def link(
            self,
            source_conduit_id: str,
            target_conduit_id: str,
            *,
            frame_name: Optional[str] = None,
    ) -> bool:
        """
        Link two conduits through the capability command surface.

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

    def sever_link(
            self,
            source_conduit_id: str,
            target_conduit_id: str,
            *,
            frame_name: Optional[str] = None,
    ) -> bool:
        """
        Sever one conduit link through the capability command surface.

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

    # ------------------------------------------------------------------
    # Research surface (MutationResearch) - READ ONLY in this room
    # ------------------------------------------------------------------

    def _require_live_mutation_research(self) -> object:
        """
        Return the Aether-hosted MutationResearch root, when it is live.

        Contract:
            - Non-constructing peek (the command path never births MR).
            - Teach-grade refusal when research is absent or inactive.

        Returns:
            object: The live, activated MutationResearch root.

        Raises:
            RuntimeError: If the root does not exist, is cleaned, or is
                not activated.
        """
        research = self._aether._mutation_research
        if research is None or research.cleaned or not research.activated:
            raise RuntimeError(
                "MutationResearch is not active in this world; activate the "
                "root (configuration + activate) before using research "
                "commands."
            )
        return research

    def research_walk(self, lane: str = "default") -> object:
        """
        Return one research lane's line of versions (read-only).

        Args:
            lane: Lane name or id; the default lane when omitted.

        Returns:
            object: Ordered node payloads (detached).
        """
        self.check_cleaned()
        with self._entered_command_action(
                action_name="research_walk",
                frame_name=None,
        ), self._lock:
            return self._require_live_mutation_research().research_set().walk(
                lane,
            )

    def research_history(self, spell_id: str) -> object:
        """
        Return everything the research record knows about one identity.

        Args:
            spell_id: Binding-signature SHA256 to report on.

        Returns:
            object: History payload (detached).
        """
        self.check_cleaned()
        with self._entered_command_action(
                action_name="research_history",
                frame_name=None,
        ), self._lock:
            return (
                self._require_live_mutation_research()
                .research_set()
                .history(spell_id)
            )

    def research_heads(self) -> object:
        """
        Return the tip identity of every open research lane.

        Returns:
            object: lane name -> tip spell id mapping (detached).
        """
        self.check_cleaned()
        with self._entered_command_action(
                action_name="research_heads",
                frame_name=None,
        ), self._lock:
            return (
                self._require_live_mutation_research().research_set().heads()
            )

    def research_residency(self, spell_id: str) -> object:
        """
        Return the query-time residency join for one identity.

        Args:
            spell_id: Binding-signature SHA256 to locate.

        Returns:
            object: Residency payload (detached).
        """
        self.check_cleaned()
        with self._entered_command_action(
                action_name="research_residency",
                frame_name=None,
        ), self._lock:
            return self._require_live_mutation_research().residency_view(
                spell_id,
            )

    def research_diff(
            self,
            left_spell_id: str,
            right_spell_id: str,
            *,
            strategy: str = "structural",
    ) -> object:
        """
        Return a derived diff between two research identities (read-only).

        Args:
            left_spell_id: Left version identity.
            right_spell_id: Right version identity.
            strategy: Registered diff strategy name.

        Returns:
            object: Detached diff verdict.
        """
        self.check_cleaned()
        with self._entered_command_action(
                action_name="research_diff",
                frame_name=None,
        ), self._lock:
            return self._require_live_mutation_research().diff_research(
                left_spell_id,
                right_spell_id,
                strategy=strategy,
            )

    def research_campaign_view(self, campaign: str) -> object:
        """
        Return everything the record knows about one research campaign.

        Args:
            campaign: Campaign stamp to gather.

        Returns:
            object: Campaign payload (detached).
        """
        self.check_cleaned()
        with self._entered_command_action(
                action_name="research_campaign_view",
                frame_name=None,
        ), self._lock:
            return (
                self._require_live_mutation_research()
                .research_set()
                .campaign_view(campaign)
            )

    # ------------------------------------------------------------------
    # Foresight reads (MutationResearch) - source / impact / graph /
    # drift. Capability rooms carry the READS only; the candidate preview
    # takes code and stays codegen-room-only.
    # ------------------------------------------------------------------

    def research_source(
            self,
            spell_id: str,
            *,
            module_name: Optional[str] = None,
    ) -> object:
        """
        Return the code of one spell's module world (or one module of it).

        Args:
            spell_id: Binding-signature SHA256 whose world to read.
            module_name: Optional single module to return.

        Returns:
            object: Per-module source rows (recorded-first, live-disk
                fallback, honest text_unavailable).
        """
        self.check_cleaned()
        with self._entered_command_action(
                action_name="research_source",
                frame_name=None,
        ), self._lock:
            return self._require_live_mutation_research().source_view(
                spell_id,
                module_name=module_name,
            )

    def research_impact(
            self,
            *,
            spell_id: Optional[str] = None,
            module_name: Optional[str] = None,
    ) -> object:
        """
        Return one blast radius joined with research residency.

        Args:
            spell_id: Optional spell SHA256 at the blast center.
            module_name: Optional canonical module name at the blast center.

        Returns:
            object: Radius payload plus the per-spell `research` join
                (declared/lane/campaign rows).
        """
        self.check_cleaned()
        with self._entered_command_action(
                action_name="research_impact",
                frame_name=None,
        ), self._lock:
            return self._require_live_mutation_research().impact_view(
                spell_id=spell_id,
                module_name=module_name,
            )

    def research_module_graph(self, spell_id: str) -> object:
        """
        Return one spell's module world as a walkable graph payload.

        Args:
            spell_id: Binding-signature SHA256 whose world to walk.

        Returns:
            object: Modules, dependency edges, local reverse edges,
                export surfaces, fingerprints, paths, and load order.
        """
        self.check_cleaned()
        with self._entered_command_action(
                action_name="research_module_graph",
                frame_name=None,
        ), self._lock:
            return self._require_live_mutation_research().module_graph_view(
                spell_id,
            )

    def research_source_drift(self) -> object:
        """
        Return the full recorded-vs-disk drift report with radii.

        Returns:
            object: Drift statuses per sealed module plus blast radii for
                every module that is not unchanged.
        """
        self.check_cleaned()
        with self._entered_command_action(
                action_name="research_source_drift",
                frame_name=None,
        ), self._lock:
            return (
                self._require_live_mutation_research().source_drift_view()
            )

    def research_module(
            self,
            spell_id: str,
            module_name: str,
    ) -> object:
        """
        Return the full crystal dossier for one module of one version.

        Args:
            spell_id: Binding-signature SHA256 whose world carries it.
            module_name: Module to gather.

        Returns:
            object: Source (labeled synthetic/user/live_disk), fingerprint,
                path, deps, local importers, export surface, drift.
        """
        self.check_cleaned()
        with self._entered_command_action(
                action_name="research_module",
                frame_name=None,
        ), self._lock:
            return self._require_live_mutation_research().module_view(
                spell_id,
                module_name,
            )

    def research_part(
            self,
            spell_id: str,
            part_name: str,
            *,
            kind: Optional[str] = None,
            module_name: Optional[str] = None,
    ) -> object:
        """
        Return one named top-level function/class's text from a version.

        Args:
            spell_id: Binding-signature SHA256 whose world to search.
            part_name: Top-level part name.
            kind: Optional "function" or "class" filter.
            module_name: Optional single module to search.

        Returns:
            object: Part text + span + carrying module, or an honest miss.
        """
        self.check_cleaned()
        with self._entered_command_action(
                action_name="research_part",
                frame_name=None,
        ), self._lock:
            return self._require_live_mutation_research().part_view(
                spell_id,
                part_name,
                kind=kind,
                module_name=module_name,
            )

    def research_part_diff(
            self,
            left_spell_id: str,
            right_spell_id: str,
            part_name: str,
            *,
            kind: Optional[str] = None,
            module_name: Optional[str] = None,
    ) -> object:
        """
        Unified text diff of one named part between two versions + radius.

        Args:
            left_spell_id: Left version identity.
            right_spell_id: Right version identity.
            part_name: Top-level part name to compare.
            kind: Optional "function" or "class" filter.
            module_name: Optional single module to search on both sides.

        Returns:
            object: Per-side found flags/modules/kinds, unified diff of the
                part text (recorded material only), and the carrying
                module's residency-joined blast radius.
        """
        self.check_cleaned()
        with self._entered_command_action(
                action_name="research_part_diff",
                frame_name=None,
        ), self._lock:
            return self._require_live_mutation_research().part_diff(
                left_spell_id,
                right_spell_id,
                part_name,
                kind=kind,
                module_name=module_name,
            )

    def research_parts(
            self,
            spell_id: str,
            *,
            module_name: Optional[str] = None,
    ) -> object:
        """
        Return every top-level class/function of a version, with code.

        Args:
            spell_id: Binding-signature SHA256 whose world to inventory.
            module_name: Optional single module to inventory.

        Returns:
            object: Per-module part rows (name/kind/span/text) with
                per-module honesty (text_unavailable / parse_error).
        """
        self.check_cleaned()
        with self._entered_command_action(
                action_name="research_parts",
                frame_name=None,
        ), self._lock:
            return self._require_live_mutation_research().parts_view(
                spell_id,
                module_name=module_name,
            )

    def research_group_view(self, group_id: str) -> object:
        """
        Return one composition's roster with residence and drift truth.

        Args:
            group_id: Composition identity to gather.

        Returns:
            object: Roster + per-member lane joins + behind drift flags.
        """
        self.check_cleaned()
        with self._entered_command_action(
                action_name="research_group_view",
                frame_name=None,
        ), self._lock:
            return self._require_live_mutation_research().group_view(
                group_id,
            )

    def research_group_diff(
            self,
            left_group_id: str,
            right_group_id: str,
            *,
            strategy: str = "members",
    ) -> object:
        """
        Return a derived diff between two recorded compositions.

        Args:
            left_group_id: Left composition identity.
            right_group_id: Right composition identity.
            strategy: Registered grouped strategy ("members" default:
                added/removed members + lane-evidenced version moves).

        Returns:
            object: Detached grouped-diff verdict.
        """
        self.check_cleaned()
        with self._entered_command_action(
                action_name="research_group_diff",
                frame_name=None,
        ), self._lock:
            return self._require_live_mutation_research(
            ).group_diff_research(
                left_group_id,
                right_group_id,
                strategy=strategy,
            )

    def research_group_impact(self, group_id: str) -> object:
        """
        Return one composition's union blast radius with closure math.

        Args:
            group_id: Composition identity at the blast center.

        Returns:
            object: Union radius, internal/outbound split, closure
                fraction, affected compositions, residency join.
        """
        self.check_cleaned()
        with self._entered_command_action(
                action_name="research_group_impact",
                frame_name=None,
        ), self._lock:
            return self._require_live_mutation_research(
            ).group_impact_view(group_id)

    def list_supported_command_methods(self) -> Tuple[str, ...]:
        """
        Return the public command methods supported by capability rooms.

        Returns:
            Tuple[str, ...]: Shared command names plus capability-owned method
            names in stable presentation order.
        """
        self.check_cleaned()
        with self._entered_command_action(
                action_name="list_supported_command_methods",
                frame_name=None,
        ):
            return self._list_supported_command_methods_tuple() + (
                self._CAPABILITY_COMMAND_METHOD_NAMES
            )
