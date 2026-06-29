from __future__ import annotations

import threading
from types import SimpleNamespace
from typing import Any, Dict, List, Optional, Set

import pytest

from melder.aether.conduit.conduit_ward.contract.detail_reason import DetailReason
from melder.aether.conduit.conduit_ward.permissions.permissions import Permissions
from melder.aether.conduit.conduit_ward.policies.policies import Policies
from melder.aether.conduit.conduit_ward.transfer.transfer_of_ownership import TransferOfOwnership
from melder.aether.aetheric_frame.dev_ops.incident_manager.incident_severity import IncidentSeverity
from melder.aether.aetheric_frame.dev_ops.spell_system_states.spell_state import SpellState
from melder.aether.aetheric_frame.dev_ops.spell_system_states.spell_state_change_reason import SpellStateChangeReason
from melder.aether.aetheric_frame.dev_ops.spell_system_states.spell_validity import SpellValidity
from melder.aether.spellbook.bind.spell_index import SpellIndex
from melder.aether.spellbook.spell_compiler.spell_compiler_artifact import (
    SpellCompilerArtifact,
)
from melder.utilities.synchronization.creation_gate_controller import (
    CreationGateController,
)

SOURCE_ID = "source"
TARGET_ID = "target"
PEER_ID = "peer"
DEFAULT_SPELL_ID = "spell-1"


class FakeState:
    """
    Minimal spell state that records validity transitions.

    Contract:
    - set_validity updates stored validity and change_reason.
    - Calls are recorded for later assertions.
    """

    def __init__(
        self,
        *,
        validity: SpellValidity,
        change_reason: SpellStateChangeReason,
    ) -> None:
        """
        Initialize the fake state with a validity and change reason.

        Args:
            validity: Initial validity for the lineage.
            change_reason: Initial change reason for the lineage.
        """
        self.validity = validity
        self.change_reason = change_reason
        self.calls: List[Dict[str, Any]] = []

    def set_validity(
        self,
        validity: SpellValidity,
        *,
        change_reason: Optional[SpellStateChangeReason] = None,
        flags_to_add: Optional[List[SpellState]] = None,
        flags_to_remove: Optional[List[SpellState]] = None,
        transitively_dirty: Optional[bool] = None,
    ) -> None:
        """
        Record and apply a validity change.

        Args:
            validity: New validity value.
            change_reason: Optional reason override for the change.
            flags_to_add: Optional flags to add to the lineage.
            flags_to_remove: Optional flags to remove from the lineage.
            transitively_dirty: Optional transitive dirty flag.
        """
        self.validity = validity
        if change_reason is not None:
            self.change_reason = change_reason
        self.calls.append(
            {
                "validity": validity,
                "change_reason": change_reason,
                "flags_to_add": flags_to_add,
                "flags_to_remove": flags_to_remove,
                "transitively_dirty": transitively_dirty,
            }
        )


class FakeSpellStatesSystem:
    """
    Minimal spell state system used by transfer tests.

    Contract:
    - register_index creates a FakeState when needed.
    - mark_structural_change records requests.
    - unregister_index and conduit-dirty calls are supported.
    """

    def __init__(self) -> None:
        """
        Initialize empty state storage.
        """
        self._states: Dict[str, FakeState] = {}
        self.mark_calls: List[Dict[str, Any]] = []
        self.unregister_calls: List[Dict[str, Any]] = []
        self.conduit_dirty_calls: List[Dict[str, Any]] = []

    def get_by_index_id(self, index_id: str) -> Optional[FakeState]:
        """
        Return the state for an index id, or None when absent.

        Args:
            index_id: SpellIndex id to look up.
        Returns:
            FakeState when present; otherwise None.
        """
        return self._states.get(index_id)

    def register_index(self, spell_index: SpellIndex) -> None:
        """
        Register a lineage state for the given spell index.

        Args:
            spell_index: SpellIndex identifying the lineage.
            spell: Spell object associated with the lineage.
        """
        if spell_index.id in self._states:
            return
        self._states[spell_index.id] = FakeState(
            validity=SpellValidity.unknown,
            change_reason=SpellStateChangeReason.new_index,
        )

    def unregister_index(self, spell_index: SpellIndex) -> Optional[FakeState]:
        """
        Remove a lineage state when unregistering.

        Args:
            spell_index: SpellIndex whose state should be removed.
        Returns:
            Removed FakeState when present, otherwise None.
        """
        removed = self._states.pop(spell_index.id, None)
        self.unregister_calls.append({"spell_index": spell_index, "removed": removed})
        return removed

    def compute_impact_closure(self, lineage_ids: List[str]) -> Set[str]:
        """
        Return a minimal impact closure for the provided lineage ids.

        Args:
            lineage_ids: Lineage ids to include in the closure.
        Returns:
            Set of lineage ids considered impacted.
        """
        return {lineage_id for lineage_id in lineage_ids if lineage_id}

    def mark_structural_change(self, *, spell_index: SpellIndex, reason: SpellStateChangeReason) -> None:
        """
        Record a structural change request.

        Args:
            spell_index: SpellIndex being marked.
            reason: Reason for the structural change.
        """
        self.mark_calls.append({"spell_index": spell_index, "reason": reason})

    def mark_conduit_dirty(
        self,
        *,
        conduit_id: str,
        change_reason: Optional[SpellStateChangeReason] = None,
    ) -> None:
        """
        Record a conduit dirty request.

        Args:
            conduit_id: Conduit id being marked dirty.
            change_reason: Optional change reason for the dirtiness.
        """
        self.conduit_dirty_calls.append(
            {
                "conduit_id": conduit_id,
                "change_reason": change_reason,
            }
        )


class FakeChangeControlManager:
    """
    Minimal change-control manager capturing pending changes.

    Contract:
    - register_pending_change stores an entry keyed by index id.
    - clear_pending_change removes the pending entry.
    """

    def __init__(self) -> None:
        """
        Initialize an empty pending-change registry.
        """
        self._pending: Dict[str, Dict[str, Any]] = {}
        self._cleared: List[str] = []
        self._revalidate_fn = None

    def get_pending_change(self, index_id: str) -> Optional[Dict[str, Any]]:
        """
        Return a pending change entry by index id.

        Args:
            index_id: SpellIndex id for lookup.
        Returns:
            Pending change entry, or None if absent.
        """
        return self._pending.get(index_id)

    def register_pending_change(
        self,
        *,
        spell_index: SpellIndex,
        reason: str,
        metadata: Dict[str, Any],
    ) -> None:
        """
        Register a pending change entry.

        Args:
            spell_index: SpellIndex being registered.
            reason: Change reason string.
            metadata: Arbitrary metadata about the change.
        """
        self._pending[spell_index.id] = {
            "spell_index": spell_index,
            "reason": reason,
            "metadata": metadata,
        }

    def has_registered_revalidators(self) -> bool:
        """
        Return whether any revalidator callback is currently registered.

        Returns:
            bool: True when the fake manager carries a non-null revalidator.
        """
        return self._revalidate_fn is not None

    def clear_pending_change(self, index_id: str) -> None:
        """
        Clear a pending change entry by index id.

        Args:
            index_id: SpellIndex id to clear.
        """
        self._cleared.append(index_id)
        self._pending.pop(index_id, None)


class FakeIncidentManager:
    """
    Minimal incident manager recording emitted incidents.

    Contract:
    - create_incident records the payload for inspection.
    """

    def __init__(self) -> None:
        """
        Initialize the incident list.
        """
        self.incidents: List[Dict[str, Any]] = []

    def create_incident(
        self,
        *,
        kind: str,
        severity: IncidentSeverity,
        summary: str,
        spell_index_id: str,
        root_ids: List[str],
        details: Dict[str, Any],
    ) -> None:
        """
        Record an incident payload.

        Args:
            kind: Incident kind identifier.
            severity: Severity of the incident.
            summary: Human-readable summary.
            spell_index_id: SpellIndex id associated with the incident.
            root_ids: Root spell ids involved.
            details: Additional incident details.
        """
        self.incidents.append(
            {
                "kind": kind,
                "severity": severity,
                "summary": summary,
                "spell_index_id": spell_index_id,
                "root_ids": list(root_ids),
                "details": dict(details),
            }
        )


class FakeCreations:
    """
    In-memory creations store used by transfer tests.

    Contract:
    - extract_spell_creations removes and returns creations.
    - restore_spell_creations replaces creations.
    """

    def __init__(self, initial: Optional[Dict[str, List[Any]]] = None) -> None:
        """
        Initialize the creations store.

        Args:
            initial: Optional mapping of spell_id to creation list.
        """
        self._store: Dict[str, List[Any]] = {}
        if initial:
            for spell_id, items in initial.items():
                self._store[spell_id] = list(items)

    def extract_spell_creations(self, spell_id: str) -> List[Any]:
        """
        Extract and remove creations for a spell_id.

        Args:
            spell_id: Spell id whose creations are removed.
        Returns:
            List of extracted creations.
        """
        return self._store.pop(spell_id, [])

    def restore_spell_creations(self, spell_id: str, extracted: List[Any]) -> None:
        """
        Restore creations for a spell_id.

        Args:
            spell_id: Spell id whose creations are restored.
            extracted: Creations to restore.
        """
        self._store[spell_id] = list(extracted)

    def get_creations(self, spell_id: str) -> List[Any]:
        """
        Return the current creations list for a spell_id.

        Args:
            spell_id: Spell id to look up.
        Returns:
            List of creations stored for the spell_id.
        """
        return list(self._store.get(spell_id, []))


class FakeCluster:
    """
    Cluster stub holding shared spell indices.

    Contract:
    - add_shared_spell registers a shared spell under an owner id.
    """

    def __init__(self) -> None:
        """
        Initialize an empty shared-spell registry.
        """
        self.members: Set[str] = set()
        self.shared_spells: Dict[str, set[SpellIndex]] = {}

    def add_shared_spell(self, owner_id: str, spell_index: SpellIndex) -> None:
        """
        Add a shared spell index for the given owner.

        Args:
            owner_id: Conduit id that owns the share.
            spell_index: SpellIndex being shared.
        """
        self.members.add(owner_id)
        self.shared_spells.setdefault(owner_id, set()).add(spell_index)

    def get_shared_spells(self) -> Dict[str, set[SpellIndex]]:
        """
        Return a detached snapshot of shared spell indices by owner id.

        Returns:
            Dict[str, set[SpellIndex]]: Snapshot of the shared-spell registry.
        """
        return {
            owner_id: set(indices)
            for owner_id, indices in self.shared_spells.items()
        }

    def get_members(self) -> Set[str]:
        """
        Return a detached snapshot of current cluster members.

        Returns:
            Set[str]: Member conduit ids currently recorded on the cluster.
        """
        return set(self.members)


class FakeFrame:
    """
    Minimal Aether frame containing registry and clusters.
    """

    def __init__(self) -> None:
        """
        Initialize an empty registry and cluster map.
        """
        self._spell_registry: Dict[str, set[SpellIndex]] = {}
        self._conduit_clusters: Dict[str, FakeCluster] = {}
        self._conduits: Dict[str, Any] = {}
        self._conduit_cloud = FakeConduitCloud(self)


class FakeConduitCloud:
    """
    Minimal cloud-facing cluster surface for transfer contract tests.

    Contract:
    - Proxies cluster and conduit lookups to the backing FakeFrame.
    """

    def __init__(self, frame: FakeFrame, frame_name: str = "default") -> None:
        """Initialize the cloud facade over one fake frame."""
        self._frame = frame
        self.frame_name = frame_name

    def _get_cluster(self, cluster_name: str) -> FakeCluster:
        """Return one named cluster from the backing frame."""
        return self._frame._conduit_clusters[cluster_name]

    def get_cluster(self, cluster_name: str) -> FakeCluster:
        """Return one named cluster from the backing frame."""
        return self._get_cluster(cluster_name)

    def get_clusters_for_conduit(self, conduit_id: str) -> List[str]:
        """Return cluster names containing one conduit id."""
        return [
            cluster_name
            for cluster_name, cluster in self._frame._conduit_clusters.items()
            if conduit_id in cluster.members or conduit_id in cluster.shared_spells
        ]

    def get_conduit_by_id(self, conduit_id: str) -> Any:
        """Return one conduit by id from the backing frame."""
        return self._frame._conduits[conduit_id]


class FakeAether:
    """
    Minimal Aether implementation for registry operations.

    Contract:
    - add/remove update the registry in the frame.
    """

    def __init__(
        self,
        frame: FakeFrame,
        change_control_manager: FakeChangeControlManager,
        incident_manager: FakeIncidentManager,
    ) -> None:
        """
        Initialize the Aether stub with a single frame.

        Args:
            frame: Frame backing registry storage.
            change_control_manager: Change-control manager stub.
            incident_manager: Incident manager stub.
        """
        self._default_frame = frame
        self._aetheric_frames = {"default": frame}
        self._change_control_manager = change_control_manager
        self._incident_manager = incident_manager
        self.configuration = None
        self.add_calls: List[Dict[str, Any]] = []
        self.remove_calls: List[Dict[str, Any]] = []

    def get_conduit_cloud(self, frame_name: str):
        """Return the frame-local cloud service for the requested frame."""
        return self._default_frame._conduit_cloud

    def _get_change_control_manager(self, frame_name: str) -> FakeChangeControlManager:
        """
        Return the change-control manager for the frame.

        Args:
            frame_name: Frame name requested.
        Returns:
            Change-control manager instance.
        """
        return self._change_control_manager

    def _get_incident_manager(self, frame_name: str) -> FakeIncidentManager:
        """
        Return the incident manager for the frame.

        Args:
            frame_name: Frame name requested.
        Returns:
            Incident manager instance.
        """
        return self._incident_manager

    def _get_cluster(self, cluster_name: str, frame_name: str) -> FakeCluster:
        """
        Return the named cluster for the requested frame.

        Args:
            cluster_name: Cluster name to resolve.
            frame_name: Frame name containing the cluster.

        Returns:
            FakeCluster: Resolved cluster object.
        """
        return self._get_frame(frame_name)._conduit_clusters[cluster_name]

    def _get_clusters_for_conduit(self, conduit_id: str, frame_name: str) -> List[str]:
        """
        Return cluster names that currently contain the supplied conduit id.

        Args:
            conduit_id: Conduit id to search for.
            frame_name: Frame name to resolve.

        Returns:
            List[str]: Cluster names containing the conduit id.
        """
        frame = self._get_frame(frame_name)
        return [
            cluster_name
            for cluster_name, cluster in frame._conduit_clusters.items()
            if conduit_id in cluster.members or conduit_id in cluster.shared_spells
        ]

    def _get_frame(self, frame_name: str) -> FakeFrame:
        """
        Resolve the frame by name.

        Args:
            frame_name: Frame name to resolve.
        Returns:
            The resolved FakeFrame.
        """
        if frame_name == "default":
            return self._default_frame
        return self._aetheric_frames[frame_name]

    def _get_existing_frame(self, frame_name: str = "default") -> FakeFrame:
        """
        Return one existing frame without creating new frame state.

        Args:
            frame_name: Frame name to resolve.

        Returns:
            FakeFrame: Existing frame for the requested name.
        """
        return self._get_frame(frame_name)

    def _add_spells_to_aether(self, conduit_id: str, indices: set[SpellIndex], frame_name: str) -> None:
        """
        Add spell indices to the registry for a conduit.

        Args:
            conduit_id: Conduit id owning the indices.
            indices: SpellIndex set to add.
            frame_name: Frame name for the registry.
        """
        frame = self._get_frame(frame_name)
        frame._spell_registry.setdefault(conduit_id, set()).update(indices)
        self.add_calls.append({"conduit_id": conduit_id, "indices": set(indices), "frame_name": frame_name})

    def _register_single_spell_index(self, conduit_id: str, spell_index: SpellIndex, frame_name: str) -> None:
        """
        Register a single spell index for a conduit.

        Args:
            conduit_id: Conduit id owning the index.
            spell_index: SpellIndex to register.
            frame_name: Frame name for the registry.
        """
        self._add_spells_to_aether(conduit_id, {spell_index}, frame_name)

    def _remove_spells_from_aether(self, conduit_id: str, indices: set[SpellIndex], frame_name: str) -> None:
        """
        Remove spell indices from the registry for a conduit.

        Args:
            conduit_id: Conduit id owning the indices.
            indices: SpellIndex set to remove.
            frame_name: Frame name for the registry.
        """
        frame = self._get_frame(frame_name)
        frame._spell_registry.setdefault(conduit_id, set()).difference_update(indices)
        self.remove_calls.append({"conduit_id": conduit_id, "indices": set(indices), "frame_name": frame_name})

    def _remove_single_spell_index(self, conduit_id: str, spell_index: SpellIndex, frame_name: str) -> None:
        """
        Remove a single spell index for a conduit.

        Args:
            conduit_id: Conduit id owning the index.
            spell_index: SpellIndex to remove.
            frame_name: Frame name for the registry.
        """
        self._remove_spells_from_aether(conduit_id, {spell_index}, frame_name)

    def _get_conduits_in_cluster(self, cluster_name: str, frame_name: str) -> List[str]:
        """
        Return conduit ids for a named cluster.

        Args:
            cluster_name: Cluster name to inspect.
            frame_name: Frame name to resolve.
        Returns:
            List of conduit ids for owners in the cluster share map.
        """
        frame = self._get_frame(frame_name)
        cluster = frame._conduit_clusters.get(cluster_name)
        if cluster is None:
            return []
        member_ids = set(cluster.members)
        member_ids.update(owner_id for owner_id in cluster.shared_spells.keys() if owner_id)
        return list(member_ids)

    def list_conduit_ids(self, frame_name: str) -> List[str]:
        """
        Return registered conduit ids for the requested frame.

        Args:
            frame_name: Frame name to inspect.
        Returns:
            List[str]: Registered conduit ids.
        """
        frame = self._get_frame(frame_name)
        return list(frame._conduits.keys())

    def get_conduit_by_id(self, conduit_id: str, frame_name: str) -> Any:
        """
        Return a conduit by id from the requested frame.

        Args:
            conduit_id: Conduit id to resolve.
            frame_name: Frame name to inspect.
        Returns:
            Any: Matching conduit instance.
        """
        frame = self._get_frame(frame_name)
        return frame._conduits[conduit_id]

    def _get_conduit_by_spell_id(self, spell_id: str, frame_name: str) -> Any:
        """
        Return the conduit that currently owns the supplied spell id.

        Args:
            spell_id: Spell id to locate.
            frame_name: Frame name to resolve.

        Returns:
            Any: Conduit currently owning the supplied spell id.

        Raises:
            ValueError: If no conduit currently owns the spell id.
        """
        frame = self._get_frame(frame_name)
        for conduit_id, indices in frame._spell_registry.items():
            for spell_index in indices:
                if (
                        spell_index.selected_spell_id == spell_id or
                        spell_index.has_spell(spell_id)
                ):
                    return frame._conduits[conduit_id]
        raise ValueError(spell_id)


class FakeSpellbook:
    """
    Minimal spellbook storage for transfer operations.
    """

    class _ConfigurationStub:
        def get_property(self, key: str) -> bool:
            raise KeyError(key)

    def __init__(
        self,
        states_system: FakeSpellStatesSystem,
        *,
        aether: Optional[FakeAether] = None,
    ) -> None:
        """
        Initialize spell storage and the state system link.

        Args:
            states_system: Spell state system used by transfers.
        """
        self._lock = threading.RLock()
        self._spells: Dict[SpellIndex, Any] = {}
        self._lookup_spells: Dict[str, SpellIndex] = {}
        self._spell_system_states = states_system
        self._spells_by_id: Dict[str, Any] = {}
        self._contracted_spells: Dict[str, Dict[SpellIndex, Any]] = {}
        self._contracted_spells_by_id: Dict[str, Any] = {}
        self._spell_id_pool: Dict[str, SpellIndex] = {}
        self._risk_register_calls: List[Dict[str, Any]] = []
        self._risk_unregister_calls: List[Dict[str, Any]] = []
        self._nexus_publish_enabled: bool = True
        self._nexus_publish_calls: List[Any] = []
        self._configuration = self._ConfigurationStub()
        self._aether = aether

    def _register_spell_with_risk_manager(self, conduit_id: str, spell_obj: Any) -> None:
        """
        Record a risk-manager registration call.

        Args:
            conduit_id: Conduit id registering the spell.
            spell_obj: Spell being registered.
        """
        self._risk_register_calls.append({"conduit_id": conduit_id, "spell": spell_obj})

    def _unregister_spell_with_risk_manager(self, conduit_id: str, spell_obj: Any) -> None:
        """
        Record a risk-manager unregister call.

        Args:
            conduit_id: Conduit id unregistering the spell.
            spell_obj: Spell being unregistered.
        """
        self._risk_unregister_calls.append({"conduit_id": conduit_id, "spell": spell_obj})

    def _publish_spell_record_to_nexus(self, spell_obj: Any) -> None:
        """
        Record one Nexus spell publication request.

        Args:
            spell_obj:
                Spell object being published.
        """
        self._nexus_publish_calls.append(spell_obj)

    def _unregister_owned_spell_id(self, spell_id: str, spell_obj: Any) -> None:
        """
        Remove owned spell_id mappings for the given spell.

        Args:
            spell_id: Current version id for the spell.
            spell_obj: Owned spell instance being removed.
        Raises:
            RuntimeError: If the owned map or pool map references a different spell.
        """
        existing = self._spells_by_id.get(spell_id)
        if existing is not None and existing is not spell_obj:
            raise RuntimeError(f"Owned spell_id mapped to a different spell (spell_id={spell_id}).")
        self._spells_by_id.pop(spell_id, None)

        existing_pool = self._spell_id_pool.get(spell_id)
        if existing_pool is not None and existing_pool is not spell_obj:
            raise RuntimeError(f"spell_id_pool mapped to a different spell (spell_id={spell_id}).")
        self._spell_id_pool.pop(spell_id, None)

    def _resolve_system_caching_enabled(self) -> bool:
        """
        Return the fake spellbook caching posture for transfer-time ownership restamping.

        Contract:
            Mirrors the live spellbook helper consumed by
            `TransferOfOwnership._flip_registry_and_spellbooks(...)`.
        Returns:
            bool: True for the fake spellbook test surface.
        """
        return True


class FakeConduitWard:
    """
    Minimal conduit ward recording contract operations.
    """

    def __init__(self, policy: Policies) -> None:
        """
        Initialize the ward with a policy.

        Args:
            policy: Policy enum for the ward.
        """
        self._policy = policy
        self._contracts: Dict[str, Any] = {}
        self.link_calls: List[Any] = []
        self.add_calls: List[Dict[str, Any]] = []
        self.remove_calls: List[Dict[str, Any]] = []

    def _link(self, peer: Any) -> None:
        """
        Record a link attempt to a peer conduit.

        Args:
            peer: Peer conduit to link.
        """
        self.link_calls.append(peer)

    def _add_spell_to_contract(
        self,
        *,
        spell: Any,
        conduit: Any,
        conduit_id: str,
        permissions: Permissions,
        reason: DetailReason,
        root_spell_id: str,
        link_dependencies: bool,
    ) -> None:
        """
        Record a contract add operation.

        Args:
            spell: Spell being shared.
            conduit: Peer conduit.
            conduit_id: Peer conduit id.
            permissions: Permissions for the share.
            reason: Reason for the share.
            root_spell_id: Root spell id for the share.
            link_dependencies: Whether dependencies were linked.
        """
        self.add_calls.append(
            {
                "spell": spell,
                "conduit": conduit,
                "conduit_id": conduit_id,
                "permissions": permissions,
                "reason": reason,
                "root_spell_id": root_spell_id,
                "link_dependencies": link_dependencies,
            }
        )

    def _remove_spell_from_contract(
        self,
        *,
        spell_id: str,
        conduit: Any,
        conduit_id: str,
    ) -> None:
        """
        Record a contract remove operation.

        Args:
            spell_id: Spell id being removed.
            conduit: Peer conduit.
            conduit_id: Peer conduit id.
        """
        self.remove_calls.append({"spell_id": spell_id, "conduit": conduit, "conduit_id": conduit_id})

    def _get_contracted_conduits(self) -> List[Any]:
        """
        Return contracted conduits for this ward.

        Returns:
            Empty list for the test harness.
        """
        return []


class FakeConduit:
    """
    Minimal conduit implementation for transfer tests.

    Contract:
    - get_spell_by_id returns spells stored in the spellbook.
    """

    _aether: Optional[FakeAether] = None

    def __init__(
        self,
        conduit_id: str,
        *,
        name: Optional[str] = None,
        frame_name: str,
        spellbook: FakeSpellbook,
        creations: FakeCreations,
        ward: FakeConduitWard,
        dynamic: bool = True,
    ) -> None:
        """
        Initialize a conduit with the required attributes.

        Args:
            conduit_id: Unique conduit id.
            name: Optional conduit name.
            frame_name: Aetheric frame name.
            spellbook: Spellbook storage.
            creations: Creations store.
            ward: Conduit ward.
            dynamic: Dynamic environment flag.
        """
        self._id = conduit_id
        self._name = name
        self._aetheric_frame_name = frame_name
        self.__dynamic_environment__ = dynamic
        self._spellbook = spellbook
        self._creations = creations
        self._conduit_ward = ward
        self._creation_gate_controller = CreationGateController()
        self._conduit_cloud = FakeConduitCloud(
            self._aether._get_frame(frame_name),
            frame_name,
        )
        self._lock = threading.RLock()

    def get_conduit_cloud(self) -> FakeConduitCloud:
        """
        Return the frame-local cloud service for this fake conduit.

        Returns:
            FakeConduitCloud: Backing cloud service for the conduit frame.
        """
        return self._conduit_cloud

    def get_spell_by_id(self, spell_id: str, frame_name: str) -> Optional[Any]:
        """
        Return a spell by id from this conduit.

        Args:
            spell_id: Spell id to locate.
            frame_name: Frame name (unused in this stub).
        Returns:
            Spell object when found, otherwise None.
        """
        with self._spellbook._lock:
            for spell in self._spellbook._spells.values():
                if spell.spell_id == spell_id:
                    return spell
        return None


class FakeContract:
    """
    Contract stub providing detail maps and peer resolution.
    """

    def __init__(
        self,
        contract_id: str,
        ward_a: FakeConduitWard,
        ward_b: FakeConduitWard,
        conduit_a: FakeConduit,
        conduit_b: FakeConduit,
        *,
        spell_id: str,
        details_in_a: bool,
        details_in_b: bool,
    ) -> None:
        """
        Initialize a contract with detail maps.

        Args:
            contract_id: Contract id.
            ward_a: Ward for conduit A.
            ward_b: Ward for conduit B.
            conduit_a: Conduit A.
            conduit_b: Conduit B.
            spell_id: Spell id for details.
            details_in_a: Whether ward A has a detail entry.
            details_in_b: Whether ward B has a detail entry.
        """
        self._id = contract_id
        self._ward_a = ward_a
        self._ward_b = ward_b
        self._details_a = {spell_id: "detail"} if details_in_a else {}
        self._details_b = {spell_id: "detail"} if details_in_b else {}
        self._peer_a = SimpleNamespace(_conduit=conduit_a)
        self._peer_b = SimpleNamespace(_conduit=conduit_b)

    def _check_if_exists(self, ward: FakeConduitWard, spell_id: str) -> bool:
        """
        Check whether a spell detail exists for the ward.

        Args:
            ward: Ward to check.
            spell_id: Spell id to locate.
        Returns:
            True when the detail exists for the ward.
        """
        if ward is self._ward_a:
            return spell_id in self._details_a
        if ward is self._ward_b:
            return spell_id in self._details_b
        return False

    def _get_peer(self, ward: FakeConduitWard) -> SimpleNamespace:
        """
        Return the peer wrapper for a ward.

        Args:
            ward: Ward requesting its peer.
        Returns:
            SimpleNamespace containing the peer conduit.
        """
        if ward is self._ward_a:
            return self._peer_b
        return self._peer_a


def build_spell(
    *,
    spell_id: str,
    owner_id: str,
    spell_index: SpellIndex,
    dependencies: Optional[List[str]] = None,
    existence: str = "scoped",
    permissions: Permissions = Permissions.read,
) -> SimpleNamespace:
    """
    Build a minimal spell object with required attributes.

    Args:
        spell_id: Spell identifier.
        owner_id: Owning conduit id.
        spell_index: SpellIndex associated with the spell.
        dependencies: Optional dependency ids.
        existence: Existence label for creations.
        permissions: Permissions for contract operations.
    Returns:
        SimpleNamespace representing the spell.
    """
    if dependencies is None:
        dependencies = []
    spell = SimpleNamespace(
        spell_id=spell_id,
        spell_index=spell_index,
        _owner_conduit_id=owner_id,
        _owner_conduit_name=None,
        _owner_creations=None,
        _spellbook=None,
        _spell_system_states=None,
        _cleanup_creation_context=lambda: None,
        _compiler_artifact=SpellCompilerArtifact(spell_id),
        _crafter=None,
        _key=f"key-{spell_id}",
        dependencies=list(dependencies),
        existence=existence,
        permissions=permissions,
    )

    def _add_owned_conduit(
        conduit_id: str,
        conduit_name: Optional[str] = None,
        creations: Any = None,
        *,
        dynamic_environment: bool = False,
        creation_gate_controller: Optional[CreationGateController] = None,
        caching_enabled: bool = False,
    ) -> None:
        """
        Record conduit ownership for the test spell.

        Args:
            conduit_id: Conduit id that owns the spell.
            conduit_name: Optional conduit name.
            creations: Optional creations container for ownership.
            dynamic_environment: Dynamic-mode flag for ownership stamp.
            creation_gate_controller: Creation gate controller passed by caller.
        """
        spell._owner_conduit_id = conduit_id
        spell._owner_conduit_name = conduit_name
        spell._owner_creations = creations
        spell._dynamic_environment = dynamic_environment
        spell._creation_gate_controller = creation_gate_controller

    spell._add_owned_conduit = _add_owned_conduit
    return spell


def build_environment(
    *,
    spell_id: str = DEFAULT_SPELL_ID,
    dependencies: Optional[List[str]] = None,
    include_contract: bool = False,
    include_cluster: bool = False,
    contract_details_in_a: bool = True,
    contract_details_in_b: bool = False,
    source_dynamic: bool = True,
    target_dynamic: bool = True,
    target_policy: Policies = Policies.default,
    peer_policy: Policies = Policies.default,
    source_creations: Optional[Dict[str, List[Any]]] = None,
    target_creations: Optional[Dict[str, List[Any]]] = None,
    target_has_deps: bool = True,
    register_dependency_indices: bool = True,
) -> SimpleNamespace:
    """
    Build a test environment for transfer contract-level tests.

    Args:
        spell_id: Root spell id to transfer.
        dependencies: Optional dependency ids for the root spell.
        include_contract: Whether to include a contract borrower.
        include_cluster: Whether to include a cluster borrower.
        contract_details_in_a: Whether ward A contains the spell detail.
        contract_details_in_b: Whether ward B contains the spell detail.
        source_dynamic: Source conduit dynamic flag.
        target_dynamic: Target conduit dynamic flag.
        target_policy: Target ward policy.
        peer_policy: Peer ward policy.
        source_creations: Optional creations seeded on the source.
        target_creations: Optional creations seeded on the target.
        target_has_deps: Whether target has dependency spells.
        register_dependency_indices: Whether to register dependency indices in the source registry.
    Returns:
        SimpleNamespace with all constructed collaborators.
    """
    if dependencies is None:
        dependencies = []

    frame = FakeFrame()
    change_control_manager = FakeChangeControlManager()
    incident_manager = FakeIncidentManager()
    aether = FakeAether(frame, change_control_manager, incident_manager)
    FakeConduit._aether = aether

    states_system = FakeSpellStatesSystem()
    source_book = FakeSpellbook(states_system, aether=aether)
    target_book = FakeSpellbook(states_system, aether=aether)
    peer_book = FakeSpellbook(states_system, aether=aether)

    source_ward = FakeConduitWard(Policies.default)
    target_ward = FakeConduitWard(target_policy)
    peer_ward = FakeConduitWard(peer_policy)

    source = FakeConduit(
        SOURCE_ID,
        frame_name="default",
        spellbook=source_book,
        creations=FakeCreations(source_creations),
        ward=source_ward,
        dynamic=source_dynamic,
    )
    target = FakeConduit(
        TARGET_ID,
        frame_name="default",
        spellbook=target_book,
        creations=FakeCreations(target_creations),
        ward=target_ward,
        dynamic=target_dynamic,
    )
    peer = FakeConduit(
        PEER_ID,
        frame_name="default",
        spellbook=peer_book,
        creations=FakeCreations(),
        ward=peer_ward,
        dynamic=True,
    )

    spell_index = SpellIndex(spell_id)
    spell_obj = build_spell(
        spell_id=spell_id,
        owner_id=SOURCE_ID,
        spell_index=spell_index,
        dependencies=dependencies,
    )
    spell_obj._spellbook = source_book
    spell_obj._spell_system_states = states_system
    spell_obj._owner_conduit_id = SOURCE_ID
    source_book._spells[spell_index] = spell_obj
    source_book._lookup_spells[spell_obj._key] = spell_index
    source_book._spells_by_id[spell_index.selected_spell_id] = spell_obj

    frame._spell_registry[SOURCE_ID] = {spell_index}
    frame._spell_registry[TARGET_ID] = set()
    frame._spell_registry[PEER_ID] = set()
    frame._conduits = {SOURCE_ID: source, TARGET_ID: target, PEER_ID: peer}

    dependency_spells: Dict[str, Any] = {}
    for dep_id in dependencies:
        dep_index = SpellIndex(dep_id)
        dep_spell = build_spell(
            spell_id=dep_id,
            owner_id=SOURCE_ID,
            spell_index=dep_index,
        )
        dep_spell._spellbook = source_book
        dep_spell._spell_system_states = states_system
        dep_spell._owner_conduit_id = SOURCE_ID
        source_book._spells[dep_index] = dep_spell
        source_book._lookup_spells[dep_spell._key] = dep_index
        source_book._spells_by_id[dep_index.selected_spell_id] = dep_spell
        dependency_spells[dep_id] = dep_spell
        if register_dependency_indices:
            frame._spell_registry[SOURCE_ID].add(dep_index)
        if target_has_deps:
            target_dep_index = SpellIndex(dep_id)
            target_dep_spell = build_spell(
                spell_id=dep_id,
                owner_id=TARGET_ID,
                spell_index=target_dep_index,
            )
            target_dep_spell._spellbook = target_book
            target_dep_spell._spell_system_states = states_system
            target_dep_spell._owner_conduit_id = TARGET_ID
            target_book._spells[target_dep_index] = target_dep_spell
            target_book._lookup_spells[target_dep_spell._key] = target_dep_index
            target_book._spells_by_id[target_dep_index.selected_spell_id] = target_dep_spell

    if include_cluster:
        cluster = FakeCluster()
        cluster.add_shared_spell(SOURCE_ID, spell_index)
        frame._conduit_clusters["cluster-1"] = cluster
    else:
        cluster = None

    if include_contract:
        contract = FakeContract(
            "contract-1",
            source_ward,
            peer_ward,
            source,
            peer,
            spell_id=spell_id,
            details_in_a=contract_details_in_a,
            details_in_b=contract_details_in_b,
        )
        source_ward._contracts[contract._id] = contract
    else:
        contract = None

    return SimpleNamespace(
        frame=frame,
        change_control_manager=change_control_manager,
        incident_manager=incident_manager,
        states_system=states_system,
        source=source,
        target=target,
        peer=peer,
        source_ward=source_ward,
        target_ward=target_ward,
        peer_ward=peer_ward,
        cluster=cluster,
        contract=contract,
        spell=spell_obj,
        spell_index=spell_index,
        dependency_spells=dependency_spells,
    )


def test_preflight_rejects_non_dynamic_source() -> None:
    """
    Verify preflight rejects non-dynamic source conduits.

    Raises:
        RuntimeError: When the source conduit is not dynamic.
    """
    env = build_environment(source_dynamic=False)
    transfer = TransferOfOwnership(
        source_conduit=env.source,
        target_conduit=env.target,
        spell=env.spell,
    )
    with pytest.raises(RuntimeError, match="dynamic mode"):
        transfer.preflight()


def test_preflight_rejects_non_dynamic_target() -> None:
    """
    Verify preflight rejects non-dynamic target conduits.

    Raises:
        RuntimeError: When the target conduit is not dynamic.
    """
    env = build_environment(target_dynamic=False)
    transfer = TransferOfOwnership(
        source_conduit=env.source,
        target_conduit=env.target,
        spell=env.spell,
    )
    with pytest.raises(RuntimeError, match="dynamic mode"):
        transfer.preflight()


def test_preflight_rejects_non_owner() -> None:
    """
    Verify preflight rejects spells not owned by the source conduit.

    Raises:
        RuntimeError: When the spell owner does not match the source conduit.
    """
    env = build_environment()
    env.spell._owner_conduit_id = "other-owner"
    transfer = TransferOfOwnership(
        source_conduit=env.source,
        target_conduit=env.target,
        spell=env.spell,
    )
    with pytest.raises(RuntimeError, match="does not own"):
        transfer.preflight()


def test_preflight_summary_includes_borrowers_dependencies_and_snapshot() -> None:
    """
    Verify preflight summary contains borrowers, dependencies, and snapshot data.

    Contract:
    - Borrowers include contract and cluster entries when configured.
    - Dependencies and creations are reported.
    - Snapshot contains registry/spellbook presence on target.
    """
    env = build_environment(
        dependencies=["dep-1"],
        include_contract=True,
        include_cluster=True,
    )
    transfer = TransferOfOwnership(
        source_conduit=env.source,
        target_conduit=env.target,
        spell=env.spell,
        move_creations=True,
        include_dependencies=False,
    )
    summary = transfer.preflight()
    borrowers = summary["borrowers"]
    assert any(b["type"] == "contract" for b in borrowers)
    assert any(b["type"] == "cluster" for b in borrowers)
    assert summary["dependencies"] == ["dep-1"]
    assert summary["creations"]["existence"] == env.spell.existence
    assert summary["snapshot"]["in_target_registry"] is False
    assert summary["snapshot"]["in_target_spellbook"] is False


def test_preflight_rejects_unresolvable_dependencies_without_include() -> None:
    """
    Verify preflight rejects unresolvable dependencies when not included.

    Raises:
        RuntimeError: When dependencies cannot be resolved on target.
    """
    env = build_environment(dependencies=["dep-1"], target_has_deps=False)
    transfer = TransferOfOwnership(
        source_conduit=env.source,
        target_conduit=env.target,
        spell=env.spell,
        include_dependencies=False,
    )
    with pytest.raises(RuntimeError, match="Dependencies are not resolvable"):
        transfer.preflight()


def test_execute_transfers_registry_and_spellbook_and_clears_change_intent() -> None:
    """
    Verify execute flips ownership and clears change-control entries.

    Contract:
    - Registry and spellbook move to the target conduit.
    - Change-control pending entry is cleared on success.
    """
    env = build_environment()
    transfer = TransferOfOwnership(
        source_conduit=env.source,
        target_conduit=env.target,
        spell=env.spell,
        invalidate_after_transfer=True,
    )
    transfer.preflight()
    transfer.execute()
    assert env.spell_index in env.frame._spell_registry[TARGET_ID]
    assert env.spell_index not in env.frame._spell_registry[SOURCE_ID]
    with env.source._spellbook._lock:
        assert env.spell_index not in env.source._spellbook._spells
    with env.target._spellbook._lock:
        assert env.spell_index in env.target._spellbook._spells
    assert env.change_control_manager.get_pending_change(env.spell_index.id) is None


def test_execute_move_creations_transfers_to_target() -> None:
    """
    Verify move_creations transfers creations to the target conduit.

    Contract:
    - Creations are removed from source and present on target.
    """
    env = build_environment(source_creations={DEFAULT_SPELL_ID: ["obj-1"]})
    transfer = TransferOfOwnership(
        source_conduit=env.source,
        target_conduit=env.target,
        spell=env.spell,
        move_creations=True,
        invalidate_after_transfer=False,
    )
    transfer.preflight()
    transfer.execute()
    assert env.source._creations.get_creations(DEFAULT_SPELL_ID) == []
    assert env.target._creations.get_creations(DEFAULT_SPELL_ID) == ["obj-1"]


def test_execute_teardown_creations_removes_without_transfer() -> None:
    """
    Verify teardown removes creations without transferring them.

    Contract:
    - Creations are removed from the source and not added to target.
    """
    env = build_environment(source_creations={DEFAULT_SPELL_ID: ["obj-1"]})
    transfer = TransferOfOwnership(
        source_conduit=env.source,
        target_conduit=env.target,
        spell=env.spell,
        move_creations=False,
        invalidate_after_transfer=False,
    )
    transfer.preflight()
    transfer.execute()
    assert env.source._creations.get_creations(DEFAULT_SPELL_ID) == []
    assert env.target._creations.get_creations(DEFAULT_SPELL_ID) == []


def test_execute_force_unshare_removes_contract_entries() -> None:
    """
    Verify force_unshare removes contract entries for the spell.

    Contract:
    - Contract wards record remove calls for the spell.
    """
    env = build_environment(include_contract=True, contract_details_in_a=True, contract_details_in_b=True)
    transfer = TransferOfOwnership(
        source_conduit=env.source,
        target_conduit=env.target,
        spell=env.spell,
        force_unshare=True,
        invalidate_after_transfer=False,
    )
    transfer.preflight()
    transfer.execute()
    assert env.source_ward.remove_calls
    assert env.peer_ward.remove_calls


def test_execute_repoint_borrowers_moves_contract_to_target() -> None:
    """
    Verify repointing adds a contract to the target and removes the source entry.

    Contract:
    - Target ward links and adds the spell to the contract.
    - Source ward removes its contract entry.
    """
    env = build_environment(include_contract=True, contract_details_in_a=True, contract_details_in_b=False)
    transfer = TransferOfOwnership(
        source_conduit=env.source,
        target_conduit=env.target,
        spell=env.spell,
        force_unshare=False,
        invalidate_after_transfer=False,
    )
    transfer.preflight()
    transfer.execute()
    assert len(env.target_ward.link_calls) == 1
    assert len(env.target_ward.add_calls) == 1
    assert len(env.source_ward.remove_calls) == 1


def test_execute_marks_dependencies_dirty_when_requested() -> None:
    """
    Verify dependencies are marked dirty when requested.

    Contract:
    - Dependency spell indices are sent to mark_structural_change.
    """
    env = build_environment(dependencies=["dep-1", "dep-2"], target_has_deps=True)
    transfer = TransferOfOwnership(
        source_conduit=env.source,
        target_conduit=env.target,
        spell=env.spell,
        include_dependencies=False,
        mark_dependencies_dirty=True,
        invalidate_after_transfer=False,
    )
    transfer.preflight()
    transfer.execute()
    marked = {call["spell_index"].selected_spell_id for call in env.states_system.mark_calls}
    assert marked == {"dep-1", "dep-2"}


def test_execute_includes_owned_dependencies_and_moves_registry() -> None:
    """
    Verify include_dependencies transfers owned dependencies as well.

    Contract:
    - Dependency registry entries move to the target conduit.
    """
    env = build_environment(
        dependencies=["dep-1"],
        target_has_deps=False,
        register_dependency_indices=True,
    )
    dep_spell = env.dependency_spells["dep-1"]
    transfer = TransferOfOwnership(
        source_conduit=env.source,
        target_conduit=env.target,
        spell=env.spell,
        include_dependencies=True,
        invalidate_after_transfer=False,
    )
    transfer.preflight()
    transfer.execute()
    assert dep_spell.spell_index in env.frame._spell_registry[TARGET_ID]
    assert dep_spell.spell_index not in env.frame._spell_registry[SOURCE_ID]


def test_execute_failure_records_incident_and_restores_registry() -> None:
    """
    Verify execute failures record an incident and restore registry ownership.

    Contract:
    - Failure path emits an ownership_transfer_failed incident.
    - Registry ownership returns to the source.
    """
    env = build_environment()

    class FailingLock:
        """
        Context manager that raises on entry to force a spellbook failure.
        """

        def __enter__(self) -> "FailingLock":
            """
            Raise an error to simulate lock acquisition failure.

            Raises:
                RuntimeError: Always raised to force failure.
            """
            raise RuntimeError("lock boom")

        def __exit__(self, exc_type: Any, exc: Any, tb: Any) -> bool:
            """
            Exit without suppressing exceptions.

            Args:
                exc_type: Exception type if any.
                exc: Exception instance if any.
                tb: Traceback if any.
            Returns:
                False to propagate exceptions.
            """
            return False

    env.target._spellbook._lock = FailingLock()
    transfer = TransferOfOwnership(
        source_conduit=env.source,
        target_conduit=env.target,
        spell=env.spell,
    )
    transfer.preflight()
    with pytest.raises(RuntimeError, match="Failed to flip spellbooks"):
        transfer.execute()
    assert env.spell_index in env.frame._spell_registry[SOURCE_ID]
    assert env.spell_index not in env.frame._spell_registry[TARGET_ID]
    kinds = [incident["kind"] for incident in env.incident_manager.incidents]
    assert "ownership_transfer_failed" in kinds


def test_execute_invalidate_false_sets_gated_validity() -> None:
    """
    Verify invalidation disabled leaves the lineage gated after transfer.

    Contract:
    - Final validity is gated with a structure_changed reason.
    """
    env = build_environment()
    state = FakeState(validity=SpellValidity.valid, change_reason=SpellStateChangeReason.validation_passed)
    env.states_system._states[env.spell_index.id] = state
    transfer = TransferOfOwnership(
        source_conduit=env.source,
        target_conduit=env.target,
        spell=env.spell,
        invalidate_after_transfer=False,
    )
    transfer.preflight()
    transfer.execute()
    current_state = env.states_system.get_by_index_id(env.spell_index.id)
    assert current_state is not None
    assert current_state.validity == SpellValidity.gated
    assert current_state.change_reason == SpellStateChangeReason.structure_changed


