from __future__ import annotations

import threading
from types import SimpleNamespace
from typing import Any, Callable, Dict, List, Optional

import pytest

from melder.aether.conduit.conduit_ward.contract.detail_reason import DetailReason
from melder.aether.conduit.conduit_ward.permissions.permissions import Permissions
from melder.aether.conduit.conduit_ward.policies.policies import Policies
from melder.aether.conduit.conduit_ward.transfer.transfer_of_ownership import TransferOfOwnership
from melder.aether.dev_ops.incident_manager.incident_severity import IncidentSeverity
from melder.aether.dev_ops.spell_system_states.spell_state import SpellState
from melder.aether.dev_ops.spell_system_states.spell_state_change_reason import SpellStateChangeReason
from melder.aether.dev_ops.spell_system_states.spell_validity import SpellValidity
from melder.spellbook.bind.spell_index import SpellIndex
import melder.aether.conduit.conduit_ward.transfer.transfer_of_ownership as transfer_module

SOURCE_ID = "source"
TARGET_ID = "target"
PEER_ID = "peer"
DEFAULT_SPELL_ID = "spell-1"


class FakeState:
    """
    Minimal spell state stub for validity transitions.

    Contract:
    - Stores validity and change_reason updates.
    - Records each set_validity call for assertions.
    """

    def __init__(
        self,
        *,
        validity: SpellValidity,
        change_reason: SpellStateChangeReason,
    ) -> None:
        """
        Initialize a fake state with starting validity and change_reason.

        Args:
            validity: Initial validity for the state.
            change_reason: Initial change reason.
        """
        self.validity = validity
        self.change_reason = change_reason
        self.set_calls: List[Dict[str, Any]] = []

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
        Capture a validity transition and update stored fields.

        Args:
            validity: New validity to assign.
            change_reason: Optional change reason override.
            flags_to_add: Optional flags added to the state.
            flags_to_remove: Optional flags removed from the state.
            transitively_dirty: Optional transitive dirty flag.
        """
        self.validity = validity
        if change_reason is not None:
            self.change_reason = change_reason
        self.set_calls.append(
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
    Minimal spell state system for TransferOfOwnership tests.

    Contract:
    - Registers states by index id.
    - Records structural change requests.
    """

    def __init__(self) -> None:
        """
        Initialize empty state and call registries.
        """
        self._states: Dict[str, FakeState] = {}
        self.mark_calls: List[Dict[str, Any]] = []

    def get_by_index_id(self, index_id: str) -> Optional[FakeState]:
        """
        Return a state by index id, or None when absent.

        Args:
            index_id: SpellIndex id to look up.
        Returns:
            The FakeState if registered, otherwise None.
        """
        return self._states.get(index_id)

    def register_lineage(self, spell_index: SpellIndex, spell: Any) -> None:
        """
        Register a lineage state for the provided spell index.

        Args:
            spell_index: SpellIndex whose state should be created.
            spell: Spell object used to seed state metadata.
        """
        if spell_index.id in self._states:
            return
        self._states[spell_index.id] = FakeState(
            validity=SpellValidity.unknown,
            change_reason=SpellStateChangeReason.new_lineage,
        )


    def mark_structural_change(
        self,
        *,
        spell_index: SpellIndex,
        reason: SpellStateChangeReason,
    ) -> None:
        """
        Record a structural change request.

        Args:
            spell_index: SpellIndex being marked.
            reason: Reason for the structural change.
        """
        self.mark_calls.append({"spell_index": spell_index, "reason": reason})


class FakeChangeControlManager:
    """
    Minimal change-control manager that stores pending changes.

    Contract:
    - Allows register/get/clear of pending change entries by index id.
    """

    def __init__(self, *, revalidate_fn: Optional[Callable[[], None]] = None) -> None:
        """
        Initialize the pending change store.

        Args:
            revalidate_fn: Optional revalidator callback to expose.
        """
        self._pending: Dict[str, Dict[str, Any]] = {}
        self._register_calls: List[Dict[str, Any]] = []
        self._clear_calls: List[str] = []
        self._revalidate_fn = revalidate_fn

    def get_pending_change(self, index_id: str) -> Optional[Dict[str, Any]]:
        """
        Fetch a pending change by index id.

        Args:
            index_id: SpellIndex id to look up.
        Returns:
            Pending change entry or None.
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
        Record a pending change entry.

        Args:
            spell_index: SpellIndex representing the change.
            reason: Change-control reason string.
            metadata: Additional context to store.
        """
        entry = {"spell_index": spell_index, "reason": reason, "op_id": metadata.get("op_id"), "metadata": metadata}
        self._pending[spell_index.id] = entry
        self._register_calls.append(entry)

    def clear_pending_change(self, index_id: str) -> None:
        """
        Clear a pending change entry by index id.

        Args:
            index_id: SpellIndex id to clear.
        """
        self._clear_calls.append(index_id)
        self._pending.pop(index_id, None)


class FakeIncidentManager:
    """
    Minimal incident manager that stores emitted incidents.

    Contract:
    - create_incident records inputs in a list.
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
        Record an incident payload for assertions.

        Args:
            kind: Incident kind identifier.
            severity: Severity enum value.
            summary: Short summary of the incident.
            spell_index_id: SpellIndex id associated with the incident.
            root_ids: Root spell ids involved.
            details: Structured incident details.
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
    In-memory creations store with extract and restore semantics.

    Contract:
    - extract_spell_creations removes entries and returns them.
    - restore_spell_creations replaces entries with provided data.
    """

    def __init__(self, initial: Optional[Dict[str, List[Any]]] = None) -> None:
        """
        Initialize the creation store.

        Args:
            initial: Optional mapping of spell_id to creation list.
        """
        self._store: Dict[str, List[Any]] = {}
        if initial:
            for spell_id, items in initial.items():
                self._store[spell_id] = list(items)

    def extract_spell_creations(self, spell_id: str) -> List[Any]:
        """
        Remove and return creations for a spell_id.

        Args:
            spell_id: Identifier for the spell.
        Returns:
            List of extracted creation objects.
        """
        return self._store.pop(spell_id, [])

    def restore_spell_creations(self, spell_id: str, extracted: List[Any]) -> None:
        """
        Restore creations for a spell_id.

        Args:
            spell_id: Identifier for the spell.
            extracted: Creations to restore.
        """
        self._store[spell_id] = list(extracted)

    def add(self, spell_obj: Any, obj: Any) -> None:
        """
        Add a creation entry for a spell object.

        Args:
            spell_obj: Spell object owning the creation.
            obj: Creation instance.
        """
        self._store.setdefault(spell_obj.spell_id, []).append(obj)

    def remove(self, spell_obj: Any) -> None:
        """
        Remove all creations for a spell object.

        Args:
            spell_obj: Spell object owning the creations.
        """
        self._store.pop(spell_obj.spell_id, None)

    def get_creations(self, spell_id: str) -> List[Any]:
        """
        Return a snapshot of creations for a spell_id.

        Args:
            spell_id: Identifier for the spell.
        Returns:
            List of creations currently stored.
        """
        return list(self._store.get(spell_id, []))


class FakeCluster:
    """
    Cluster stub that tracks shared spell indices.

    Contract:
    - add_shared_spell adds indices to shared_spells per owner.
    """

    def __init__(self) -> None:
        """
        Initialize the shared spell registry.
        """
        self.shared_spells: Dict[str, set[SpellIndex]] = {}

    def add_shared_spell(self, owner_id: str, spell_index: SpellIndex) -> None:
        """
        Add a shared spell index for an owner.

        Args:
            owner_id: Conduit id sharing the spell.
            spell_index: SpellIndex being shared.
        """
        self.shared_spells.setdefault(owner_id, set()).add(spell_index)


class FakeFrame:
    """
    Minimal frame holding spell registry and conduit clusters.
    """

    def __init__(self) -> None:
        """
        Initialize empty registry and cluster mappings.
        """
        self._spell_registry: Dict[str, set[SpellIndex]] = {}
        self._conduit_clusters: Dict[str, FakeCluster] = {}


class FakeAether:
    """
    Minimal Aether stub for registry and manager lookups.

    Contract:
    - add/remove update the frame registry for conduits.
    """

    def __init__(
        self,
        frame: FakeFrame,
        change_control_manager: FakeChangeControlManager,
        incident_manager: FakeIncidentManager,
        *,
        frame_name: str = "default",
    ) -> None:
        """
        Initialize the Aether stub with managers and frame.

        Args:
            frame: Frame backing the registry and clusters.
            change_control_manager: Change-control manager stub.
            incident_manager: Incident manager stub.
            frame_name: Name of the frame for registry access.
        """
        self._default_frame = frame
        self._aetheric_frames = {frame_name: frame}
        self._change_control_manager = change_control_manager
        self._incident_manager = incident_manager
        self.add_calls: List[Dict[str, Any]] = []
        self.remove_calls: List[Dict[str, Any]] = []

    def _get_change_control_manager(self, frame_name: str) -> FakeChangeControlManager:
        """
        Return the change-control manager for the requested frame.

        Args:
            frame_name: Frame name to look up.
        Returns:
            The configured FakeChangeControlManager.
        """
        return self._change_control_manager

    def _get_incident_manager(self, frame_name: str) -> FakeIncidentManager:
        """
        Return the incident manager for the requested frame.

        Args:
            frame_name: Frame name to look up.
        Returns:
            The configured FakeIncidentManager.
        """
        return self._incident_manager

    def _get_frame(self, frame_name: str) -> FakeFrame:
        """
        Resolve the frame by name.

        Args:
            frame_name: Name of the frame to resolve.
        Returns:
            The resolved FakeFrame.
        """
        if frame_name == "default":
            return self._default_frame
        return self._aetheric_frames[frame_name]

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


class FakeSpellbook:
    """
    Minimal spellbook stub with spell storage, id map, and lock.
    """

    def __init__(self, states_system: FakeSpellStatesSystem) -> None:
        """
        Initialize spellbook storage and state system reference.

        Args:
            states_system: Spell state system backing the book.
        """
        self._lock = threading.RLock()
        self._spells: Dict[SpellIndex, Any] = {}
        self._lookup_spells: Dict[str, SpellIndex] = {}
        self._spells_by_id: Dict[str, Any] = {}
        self._spell_system_states = states_system
        self._spell_id_pool: Dict[str, SpellIndex] = {}


class FakeConduitWard:
    """
    Minimal conduit ward stub that records contract actions.

    Contract:
    - _link records peer link attempts.
    - _add_spell_to_contract and _remove_spell_from_contract record arguments.
    """

    def __init__(self, policy: Policies) -> None:
        """
        Initialize a ward with policy and empty call logs.

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
        Record a request to add a spell to a contract.

        Args:
            spell: Spell being shared.
            conduit: Peer conduit for the contract.
            conduit_id: Peer conduit id.
            permissions: Permissions applied to the share.
            reason: Detail reason for the share.
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
        Record a request to remove a spell from a contract.

        Args:
            spell_id: Spell id being removed.
            conduit: Peer conduit for the contract.
            conduit_id: Peer conduit id.
        """
        self.remove_calls.append({"spell_id": spell_id, "conduit": conduit, "conduit_id": conduit_id})


class FakeConduit:
    """
    Minimal conduit stub exposing attributes required by TransferOfOwnership.

    Contract:
    - get_spell_by_id returns the first matching spell by id.
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
        Initialize a conduit with required attributes.

        Args:
            conduit_id: Unique conduit id.
            name: Optional conduit name.
            frame_name: Aetheric frame name.
            spellbook: Spellbook instance.
            creations: Creations store.
            ward: Conduit ward.
            dynamic: Dynamic environment flag.
        """
        self._id = conduit_id
        self._name = name
        self._aetheric_frame = frame_name
        self.__dynamic_environment__ = dynamic
        self._spellbook = spellbook
        self._creations = creations
        self._conduit_ward = ward
        self._lock = threading.RLock()

    def get_spell_by_id(self, spell_id: str, frame_name: str) -> Optional[Any]:
        """
        Return a spell by id from this conduit.

        Args:
            spell_id: Spell id to look up.
            frame_name: Frame name (ignored in this stub).
        Returns:
            Matching spell object, or None when absent.
        """
        with self._spellbook._lock:
            for spell in self._spellbook._spells.values():
                if spell.spell_id == spell_id:
                    return spell
        return None


class FakeContract:
    """
    Contract stub exposing detail maps and peer lookups.

    Contract:
    - _check_if_exists inspects detail maps per ward.
    - _get_peer returns the opposing conduit wrapper.
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
        Initialize a contract with detail maps for each ward.

        Args:
            contract_id: Unique contract id.
            ward_a: Ward A for the contract.
            ward_b: Ward B for the contract.
            conduit_a: Conduit for ward A.
            conduit_b: Conduit for ward B.
            spell_id: Spell id used in detail maps.
            details_in_a: Whether ward A contains the spell detail.
            details_in_b: Whether ward B contains the spell detail.
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
        Return True if a spell detail exists for the given ward.

        Args:
            ward: Ward to inspect.
            spell_id: Spell id to find.
        Returns:
            True if present, otherwise False.
        """
        if ward is self._ward_a:
            return spell_id in self._details_a
        if ward is self._ward_b:
            return spell_id in self._details_b
        return False

    def _get_peer(self, ward: FakeConduitWard) -> SimpleNamespace:
        """
        Return the peer wrapper for the given ward.

        Args:
            ward: Ward requesting the peer.
        Returns:
            SimpleNamespace wrapping the peer conduit.
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
        spell_id: Spell id for the object.
        owner_id: Owner conduit id.
        spell_index: SpellIndex associated with the spell.
        dependencies: Optional list of dependency spell ids.
        existence: Existence mode for creations.
        permissions: Permissions for contract sharing.
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
        owned_spell=False,
        _spellbook=None,
        _spell_system_states=None,
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
    ) -> None:
        """
        Record conduit ownership for the test spell.

        Args:
            conduit_id: Conduit id that owns the spell.
            conduit_name: Optional conduit name.
            creations: Optional creations container for ownership.
        """
        spell._owner_conduit_id = conduit_id
        spell._owner_conduit_name = conduit_name
        spell._owner_creations = creations
        spell.owned_spell = True

    spell._add_owned_conduit = _add_owned_conduit
    return spell


def build_environment(
    *,
    spell_id: str = DEFAULT_SPELL_ID,
    dependencies: Optional[List[str]] = None,
    source_dynamic: bool = True,
    target_dynamic: bool = True,
    target_policy: Policies = Policies.default,
    peer_policy: Policies = Policies.default,
    include_contract: bool = False,
    include_cluster: bool = False,
    contract_details_in_a: bool = True,
    contract_details_in_b: bool = True,
    source_creations: Optional[Dict[str, List[Any]]] = None,
    target_creations: Optional[Dict[str, List[Any]]] = None,
    source_has_deps: bool = True,
    target_has_deps: bool = True,
) -> SimpleNamespace:
    """
    Assemble a TransferOfOwnership test harness.

    Args:
        spell_id: Root spell id for the transfer.
        dependencies: Optional dependency ids on the root spell.
        source_dynamic: Whether the source conduit is dynamic.
        target_dynamic: Whether the target conduit is dynamic.
        target_policy: Policy for the target conduit ward.
        peer_policy: Policy for the peer conduit ward.
        include_contract: Whether to attach a contract borrower.
        include_cluster: Whether to attach a cluster borrower.
        contract_details_in_a: Whether contract ward A has the spell detail.
        contract_details_in_b: Whether contract ward B has the spell detail.
        source_creations: Optional creations seeded on the source.
        target_creations: Optional creations seeded on the target.
        source_has_deps: Whether dependency spells exist on source.
        target_has_deps: Whether dependency spells exist on target.
    Returns:
        SimpleNamespace containing the constructed environment.
    """
    if dependencies is None:
        dependencies = []

    frame = FakeFrame()
    change_control_manager = FakeChangeControlManager()
    incident_manager = FakeIncidentManager()
    aether = FakeAether(frame, change_control_manager, incident_manager)
    FakeConduit._aether = aether

    states_system = FakeSpellStatesSystem()
    source_book = FakeSpellbook(states_system)
    target_book = FakeSpellbook(states_system)
    peer_book = FakeSpellbook(states_system)

    source_creations_obj = FakeCreations(source_creations)
    target_creations_obj = FakeCreations(target_creations)

    source_ward = FakeConduitWard(Policies.default)
    target_ward = FakeConduitWard(target_policy)
    peer_ward = FakeConduitWard(peer_policy)

    source = FakeConduit(
        SOURCE_ID,
        frame_name="default",
        spellbook=source_book,
        creations=source_creations_obj,
        ward=source_ward,
        dynamic=source_dynamic,
    )
    target = FakeConduit(
        TARGET_ID,
        frame_name="default",
        spellbook=target_book,
        creations=target_creations_obj,
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

    source_book._spells[spell_index] = spell_obj
    source_book._lookup_spells[spell_obj._key] = spell_index
    source_book._spells_by_id[spell_index.current] = spell_obj

    frame._spell_registry[SOURCE_ID] = {spell_index}
    frame._spell_registry[TARGET_ID] = set()
    frame._spell_registry[PEER_ID] = set()

    dependency_spells: Dict[str, Any] = {}
    if dependencies and source_has_deps:
        for dep_id in dependencies:
            dep_index = SpellIndex(dep_id)
            dep_spell = build_spell(
                spell_id=dep_id,
                owner_id=SOURCE_ID,
                spell_index=dep_index,
            )
            source_book._spells[dep_index] = dep_spell
            source_book._lookup_spells[dep_spell._key] = dep_index
            source_book._spells_by_id[dep_index.current] = dep_spell
            dependency_spells[dep_id] = dep_spell

    if dependencies and target_has_deps:
        for dep_id in dependencies:
            dep_index = SpellIndex(dep_id)
            dep_spell = build_spell(
                spell_id=dep_id,
                owner_id=TARGET_ID,
                spell_index=dep_index,
            )
            target_book._spells[dep_index] = dep_spell
            target_book._lookup_spells[dep_spell._key] = dep_index
            target_book._spells_by_id[dep_index.current] = dep_spell

    cluster = None
    if include_cluster:
        cluster = FakeCluster()
        cluster.add_shared_spell(SOURCE_ID, spell_index)
        frame._conduit_clusters["cluster-1"] = cluster

    contract = None
    contract_ward_a = None
    contract_ward_b = None
    if include_contract:
        contract_ward_a = FakeConduitWard(Policies.default)
        contract_ward_b = FakeConduitWard(Policies.default)
        contract = FakeContract(
            "contract-1",
            contract_ward_a,
            contract_ward_b,
            source,
            peer,
            spell_id=spell_id,
            details_in_a=contract_details_in_a,
            details_in_b=contract_details_in_b,
        )
        source_ward._contracts[contract._id] = contract

    return SimpleNamespace(
        aether=aether,
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
        contract=contract,
        contract_ward_a=contract_ward_a,
        contract_ward_b=contract_ward_b,
        cluster=cluster,
        spell=spell_obj,
        spell_index=spell_index,
        source_creations=source_creations_obj,
        target_creations=target_creations_obj,
        dependency_spells=dependency_spells,
    )


def test_preflight_requires_dynamic_mode_on_source() -> None:
    """
    Verify preflight rejects a non-dynamic source conduit.

    Raises:
        RuntimeError: When source is not dynamic.
    """
    env = build_environment(source_dynamic=False)
    transfer = TransferOfOwnership(
        source_conduit=env.source,
        target_conduit=env.target,
        spell=env.spell,
    )
    with pytest.raises(RuntimeError, match="dynamic mode"):
        transfer.preflight()


def test_preflight_requires_dynamic_mode_on_target() -> None:
    """
    Verify preflight rejects a non-dynamic target conduit.

    Raises:
        RuntimeError: When target is not dynamic.
    """
    env = build_environment(target_dynamic=False)
    transfer = TransferOfOwnership(
        source_conduit=env.source,
        target_conduit=env.target,
        spell=env.spell,
    )
    with pytest.raises(RuntimeError, match="dynamic mode"):
        transfer.preflight()


def test_preflight_summary_includes_snapshot_and_options() -> None:
    """
    Verify preflight returns a summary with snapshot and option fields.

    Contract:
    - Summary exposes spell identifiers and options.
    - Change intent is recorded in the manager.
    """
    env = build_environment(dependencies=["dep-1"])
    transfer = TransferOfOwnership(
        source_conduit=env.source,
        target_conduit=env.target,
        spell=env.spell,
        move_creations=True,
        include_dependencies=False,
        force_unshare=True,
        invalidate_after_transfer=False,
        mark_dependencies_dirty=True,
    )
    summary = transfer.preflight()
    assert summary["spell_id"] == env.spell.spell_id
    assert summary["spell_index"] == env.spell.spell_index
    assert summary["source"] == SOURCE_ID
    assert summary["target"] == TARGET_ID
    assert summary["dependencies"] == ["dep-1"]
    assert summary["options"]["move_creations"] is True
    assert summary["options"]["include_dependencies"] is False
    assert summary["options"]["invalidate_after_transfer"] is False
    assert summary["snapshot"]["in_target_registry"] is False
    assert summary["snapshot"]["in_target_spellbook"] is False
    pending = env.change_control_manager.get_pending_change(env.spell_index.id)
    assert pending is not None


def test_preflight_raises_when_deps_unresolvable() -> None:
    """
    Verify preflight rejects when dependencies cannot resolve on target.

    Raises:
        RuntimeError: When dependencies are not resolvable.
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


def test_preflight_collects_contract_and_cluster_borrowers() -> None:
    """
    Verify preflight detects contract and cluster borrowers.

    Contract:
    - Borrowers include entries for contract and cluster types.
    """
    env = build_environment(include_contract=True, include_cluster=True)
    transfer = TransferOfOwnership(
        source_conduit=env.source,
        target_conduit=env.target,
        spell=env.spell,
    )
    summary = transfer.preflight()
    borrowers = summary["borrowers"]
    assert any(b["type"] == "contract" for b in borrowers)
    assert any(b["type"] == "cluster" for b in borrowers)


def test_resolve_spell_accepts_spell_object() -> None:
    """
    Verify _resolve_spell returns the spell object directly.

    Contract:
    - When spell input has spell_id, it is returned as-is.
    """
    env = build_environment()
    transfer = TransferOfOwnership(
        source_conduit=env.source,
        target_conduit=env.target,
        spell=env.spell,
    )
    assert transfer._resolve_spell() is env.spell


def test_resolve_spell_uses_spell_index_lookup() -> None:
    """
    Verify _resolve_spell uses the spellbook lookup for SpellIndex input.

    Contract:
    - SpellIndex input returns the spell stored in the source spellbook.
    """
    env = build_environment()
    transfer = TransferOfOwnership(
        source_conduit=env.source,
        target_conduit=env.target,
        spell=env.spell_index,
    )
    assert transfer._resolve_spell() is env.spell


def test_resolve_spell_uses_spell_id_string() -> None:
    """
    Verify _resolve_spell resolves by spell id when given a string.

    Contract:
    - String input uses conduit.get_spell_by_id.
    """
    env = build_environment()
    transfer = TransferOfOwnership(
        source_conduit=env.source,
        target_conduit=env.target,
        spell=env.spell.spell_id,
    )
    assert transfer._resolve_spell() is env.spell


def test_resolve_spell_raises_for_unrecognized_input() -> None:
    """
    Verify _resolve_spell raises for unsupported spell inputs.

    Raises:
        RuntimeError: When the spell cannot be resolved.
    """
    env = build_environment()
    transfer = TransferOfOwnership(
        source_conduit=env.source,
        target_conduit=env.target,
        spell=object(),
    )
    with pytest.raises(RuntimeError, match="Unable to resolve"):
        transfer._resolve_spell()


def test_execute_moves_registry_and_spellbook_and_clears_change_intent() -> None:
    """
    Verify execute flips registry ownership and clears change intent.

    Contract:
    - Registry and spellbook move to target.
    - Change-control entry is cleared.
    """
    env = build_environment()
    transfer = TransferOfOwnership(
        source_conduit=env.source,
        target_conduit=env.target,
        spell=env.spell,
        move_creations=False,
        include_dependencies=False,
        force_unshare=True,
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
    assert env.spell._owner_conduit_id == TARGET_ID
    assert env.change_control_manager.get_pending_change(env.spell_index.id) is None
    assert any(call["spell_index"] == env.spell_index for call in env.states_system.mark_calls)


def test_execute_move_creations_transfers_creations() -> None:
    """
    Verify move_creations transfers creations to the target.

    Contract:
    - Extracted creations move from source to target.
    """
    env = build_environment(source_creations={DEFAULT_SPELL_ID: ["obj-1"]})
    transfer = TransferOfOwnership(
        source_conduit=env.source,
        target_conduit=env.target,
        spell=env.spell,
        move_creations=True,
        include_dependencies=False,
        force_unshare=True,
        invalidate_after_transfer=False,
    )
    transfer.preflight()
    transfer.execute()
    assert env.source_creations.get_creations(DEFAULT_SPELL_ID) == []
    assert env.target_creations.get_creations(DEFAULT_SPELL_ID) == ["obj-1"]


def test_execute_teardown_creations_removes_from_source() -> None:
    """
    Verify teardown removes creations without transferring them.

    Contract:
    - Source creations are extracted and target remains empty.
    """
    env = build_environment(source_creations={DEFAULT_SPELL_ID: ["obj-1"]})
    transfer = TransferOfOwnership(
        source_conduit=env.source,
        target_conduit=env.target,
        spell=env.spell,
        move_creations=False,
        include_dependencies=False,
        force_unshare=True,
        invalidate_after_transfer=False,
    )
    transfer.preflight()
    transfer.execute()
    assert env.source_creations.get_creations(DEFAULT_SPELL_ID) == []
    assert env.target_creations.get_creations(DEFAULT_SPELL_ID) == []


def test_execute_force_unshare_removes_contract_entries() -> None:
    """
    Verify force_unshare removes spell entries from contracts.

    Contract:
    - Contract wards receive remove calls for the spell.
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
    assert env.contract_ward_a.remove_calls
    assert env.contract_ward_b.remove_calls


def test_execute_repoint_skips_blocked_target_policy() -> None:
    """
    Verify repointing skips when target policy blocks inbound links.

    Contract:
    - No link or contract-add calls are made.
    """
    env = build_environment(include_contract=True, target_policy=Policies.block_all, contract_details_in_a=True)
    transfer = TransferOfOwnership(
        source_conduit=env.source,
        target_conduit=env.target,
        spell=env.spell,
        force_unshare=False,
        invalidate_after_transfer=False,
    )
    transfer.preflight()
    transfer.execute()
    assert env.target_ward.link_calls == []
    assert env.target_ward.add_calls == []


def test_execute_repoint_adds_to_target_and_removes_from_source() -> None:
    """
    Verify repointing adds contract entries on target and removes source entries.

    Contract:
    - Target ward links and adds the spell.
    - Source-side contract ward removes the spell entry.
    """
    env = build_environment(
        include_contract=True,
        contract_details_in_a=True,
        contract_details_in_b=False,
        target_policy=Policies.default,
        peer_policy=Policies.default,
    )
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
    assert len(env.contract_ward_a.remove_calls) == 1


def test_execute_marks_dependencies_dirty_when_configured() -> None:
    """
    Verify dependency spell lineages are marked dirty when configured.

    Contract:
    - mark_structural_change is called for each dependency.
    """
    env = build_environment(
        dependencies=["dep-1", "dep-2"],
        source_has_deps=True,
        target_has_deps=True,
    )
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
    marked_ids = {call["spell_index"].current for call in env.states_system.mark_calls}
    assert marked_ids == {"dep-1", "dep-2"}


def test_transfer_owned_dependencies_invokes_subtransfer(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Verify owned dependency transfer instantiates and executes sub-transfer.

    Contract:
    - Each owned dependency triggers a sub-transfer execute call.
    """
    env = build_environment(
        dependencies=["dep-1"],
        source_has_deps=True,
        target_has_deps=True,
    )
    recorded: List[Any] = []

    class FakeTransfer:
        """
        Stub transfer used to record dependency executions.
        """

        def __init__(self, **kwargs: Any) -> None:
            """
            Capture the dependency spell from kwargs.

            Args:
                kwargs: TransferOfOwnership init arguments.
            """
            self.spell = kwargs["spell"]

        def execute(self) -> None:
            """
            Record the executed spell.
            """
            recorded.append(self.spell)

    monkeypatch.setattr(transfer_module, "TransferOfOwnership", FakeTransfer)

    transfer = TransferOfOwnership(
        source_conduit=env.source,
        target_conduit=env.target,
        spell=env.spell,
        include_dependencies=True,
        invalidate_after_transfer=False,
    )
    transfer._transfer_owned_dependencies(["dep-1"])
    assert recorded == [env.dependency_spells["dep-1"]]


def test_mark_lineage_disabled_registers_rollback_and_disables() -> None:
    """
    Verify mark_lineage_disabled sets disabled validity and records rollback.

    Contract:
    - State validity becomes disabled with transfer_in_progress reason.
    - A rollback action is registered.
    """
    env = build_environment()
    state = FakeState(validity=SpellValidity.valid, change_reason=SpellStateChangeReason.validation_passed)
    env.states_system._states[env.spell_index.id] = state
    transfer = TransferOfOwnership(
        source_conduit=env.source,
        target_conduit=env.target,
        spell=env.spell,
    )
    transfer._mark_lineage_disabled(env.spell_index)
    assert state.validity == SpellValidity.disabled
    assert state.change_reason == SpellStateChangeReason.transfer_in_progress
    assert transfer._rollback_actions


def test_lift_disable_sets_gated_or_unknown() -> None:
    """
    Verify lift_disable sets validity based on gated flag.

    Contract:
    - gated=True uses SpellValidity.gated and structure_changed reason.
    - gated=False uses SpellValidity.unknown and explicit_mark reason.
    """
    env = build_environment()
    state = FakeState(validity=SpellValidity.disabled, change_reason=SpellStateChangeReason.transfer_in_progress)
    env.states_system._states[env.spell_index.id] = state
    transfer = TransferOfOwnership(
        source_conduit=env.source,
        target_conduit=env.target,
        spell=env.spell,
    )
    transfer._lift_disable(env.spell_index, gated=True)
    assert state.validity == SpellValidity.gated
    assert state.change_reason == SpellStateChangeReason.structure_changed
    transfer._lift_disable(env.spell_index, gated=False)
    assert state.validity == SpellValidity.unknown
    assert state.change_reason == SpellStateChangeReason.explicit_mark


def test_record_incident_emits_failure_and_warning() -> None:
    """
    Verify incident reporting emits failure and revalidation warning incidents.

    Contract:
    - A failure incident is emitted.
    - A revalidation warning is emitted when no revalidator is registered.
    """
    env = build_environment()
    transfer = TransferOfOwnership(
        source_conduit=env.source,
        target_conduit=env.target,
        spell=env.spell,
    )
    summary = {
        "spell_id": env.spell.spell_id,
        "spell_index": env.spell.spell_index,
        "source": env.source._id,
        "target": env.target._id,
        "borrowers": [],
        "dependencies": [],
        "creations": {},
        "op_id": "op-1",
        "options": {},
    }
    transfer._record_incident(summary, RuntimeError("boom"))
    kinds = [incident["kind"] for incident in env.incident_manager.incidents]
    assert kinds == [
        "ownership_transfer_failed",
        "ownership_transfer_needs_revalidation",
    ]


def test_assert_ownership_raises_when_not_owner() -> None:
    """
    Verify ownership enforcement rejects non-owner spells.

    Raises:
        RuntimeError: When the source conduit does not own the spell.
    """
    env = build_environment()
    env.spell._owner_conduit_id = "other-owner"
    transfer = TransferOfOwnership(
        source_conduit=env.source,
        target_conduit=env.target,
        spell=env.spell,
    )
    with pytest.raises(RuntimeError, match="does not own"):
        transfer._assert_ownership(env.spell)


def test_assert_ownership_allows_owner() -> None:
    """
    Verify ownership enforcement passes for the source owner.

    Contract:
    - No exception is raised when the spell is owned by the source conduit.
    """
    env = build_environment()
    transfer = TransferOfOwnership(
        source_conduit=env.source,
        target_conduit=env.target,
        spell=env.spell,
    )
    transfer._assert_ownership(env.spell)


def test_deps_resolvable_on_target_true_when_empty() -> None:
    """
    Verify empty dependency lists are considered resolvable.

    Contract:
    - Empty dependency lists return True.
    """
    env = build_environment()
    transfer = TransferOfOwnership(
        source_conduit=env.source,
        target_conduit=env.target,
        spell=env.spell,
    )
    assert transfer._deps_resolvable_on_target([]) is True


def test_deps_resolvable_on_target_false_when_missing() -> None:
    """
    Verify dependency checks fail when any dependency is missing on target.

    Contract:
    - Missing dependency returns False.
    """
    env = build_environment(dependencies=["dep-1", "dep-2"], target_has_deps=True)
    with env.target._spellbook._lock:
        for idx, spell in list(env.target._spellbook._spells.items()):
            if spell.spell_id == "dep-2":
                env.target._spellbook._spells.pop(idx, None)
                env.target._spellbook._lookup_spells.pop(spell._key, None)
                break
    transfer = TransferOfOwnership(
        source_conduit=env.source,
        target_conduit=env.target,
        spell=env.spell,
    )
    assert transfer._deps_resolvable_on_target(["dep-1", "dep-2"]) is False


def test_deps_resolvable_on_target_false_when_error() -> None:
    """
    Verify dependency checks fail when target lookup raises.

    Contract:
    - Exceptions in resolution return False.
    """
    env = build_environment(dependencies=["dep-1"], target_has_deps=True)

    def boom(spell_id: str, frame_name: str) -> Any:
        """
        Raise an error to simulate dependency lookup failure.

        Args:
            spell_id: Spell id being requested.
            frame_name: Frame name for the lookup.
        Raises:
            RuntimeError: Always raised to simulate a failure.
        """
        raise RuntimeError("boom")

    env.target.get_spell_by_id = boom
    transfer = TransferOfOwnership(
        source_conduit=env.source,
        target_conduit=env.target,
        spell=env.spell,
    )
    assert transfer._deps_resolvable_on_target(["dep-1"]) is False


def test_mark_lineage_dirty_records_structural_change() -> None:
    """
    Verify marking lineage dirty records a structural change.

    Contract:
    - mark_structural_change is called with structure_changed reason.
    """
    env = build_environment()
    transfer = TransferOfOwnership(
        source_conduit=env.source,
        target_conduit=env.target,
        spell=env.spell,
    )
    transfer._mark_lineage_dirty(env.spell_index)
    assert env.states_system.mark_calls[-1]["reason"] == SpellStateChangeReason.structure_changed


def test_mark_lineage_disabled_registers_state_when_missing() -> None:
    """
    Verify mark_lineage_disabled registers a state when none exists.

    Contract:
    - A state is created and set to disabled.
    """
    env = build_environment()
    transfer = TransferOfOwnership(
        source_conduit=env.source,
        target_conduit=env.target,
        spell=env.spell,
    )
    assert env.states_system.get_by_index_id(env.spell_index.id) is None
    transfer._mark_lineage_disabled(env.spell_index)
    state = env.states_system.get_by_index_id(env.spell_index.id)
    assert state is not None
    assert state.validity == SpellValidity.disabled


def test_register_rollback_ignores_none() -> None:
    """
    Verify None rollback actions are ignored.

    Contract:
    - No rollback action is recorded for None.
    """
    env = build_environment()
    transfer = TransferOfOwnership(
        source_conduit=env.source,
        target_conduit=env.target,
        spell=env.spell,
    )
    transfer._register_rollback(None)
    assert transfer._rollback_actions == []


def test_rollback_restores_cluster_shares_from_snapshot() -> None:
    """
    Verify rollback restores cluster shares captured in the snapshot.

    Contract:
    - Missing cluster share entries are re-added.
    """
    env = build_environment(include_cluster=True)
    env.cluster.shared_spells[SOURCE_ID].clear()
    transfer = TransferOfOwnership(
        source_conduit=env.source,
        target_conduit=env.target,
        spell=env.spell,
    )
    transfer._preflight_summary = {
        "snapshot": {"cluster_shares": [{"cluster": "cluster-1", "owner_id": SOURCE_ID}]}
    }
    transfer._rollback()
    assert env.spell_index in env.cluster.shared_spells[SOURCE_ID]


def test_snapshot_current_state_reflects_target_registry_and_spellbook() -> None:
    """
    Verify snapshot reflects registry and spellbook presence on target.

    Contract:
    - Snapshot captures registry and spellbook presence for target.
    """
    env = build_environment()
    env.frame._spell_registry[TARGET_ID].add(env.spell_index)
    with env.target._spellbook._lock:
        env.target._spellbook._spells[env.spell_index] = env.spell
        env.target._spellbook._lookup_spells[env.spell._key] = env.spell_index
    transfer = TransferOfOwnership(
        source_conduit=env.source,
        target_conduit=env.target,
        spell=env.spell,
    )
    snapshot = transfer._snapshot_current_state(env.spell)
    assert snapshot["in_target_registry"] is True
    assert snapshot["in_target_spellbook"] is True


def test_restore_cluster_shares_noop_when_already_present() -> None:
    """
    Verify restoring cluster shares does not duplicate existing entries.

    Contract:
    - Existing shares remain unchanged.
    """
    env = build_environment(include_cluster=True)
    transfer = TransferOfOwnership(
        source_conduit=env.source,
        target_conduit=env.target,
        spell=env.spell,
    )
    before = set(env.cluster.shared_spells[SOURCE_ID])
    transfer._restore_cluster_shares(
        [{"cluster": "cluster-1", "owner_id": SOURCE_ID}],
        env.spell,
    )
    after = set(env.cluster.shared_spells[SOURCE_ID])
    assert after == before


def test_move_creations_no_extracted_no_rollback() -> None:
    """
    Verify move_creations skips when no creations exist.

    Contract:
    - No rollback action is recorded when nothing is extracted.
    """
    env = build_environment()
    transfer = TransferOfOwnership(
        source_conduit=env.source,
        target_conduit=env.target,
        spell=env.spell,
    )
    transfer._move_creations(env.spell)
    assert transfer._rollback_actions == []


def test_teardown_creations_no_extracted_no_rollback() -> None:
    """
    Verify teardown_creations skips when no creations exist.

    Contract:
    - No rollback action is recorded when nothing is extracted.
    """
    env = build_environment()
    transfer = TransferOfOwnership(
        source_conduit=env.source,
        target_conduit=env.target,
        spell=env.spell,
    )
    transfer._teardown_creations(env.spell)
    assert transfer._rollback_actions == []


def test_unshare_everywhere_registers_rollback_and_restores() -> None:
    """
    Verify unshare registers rollback actions and restores on rollback.

    Contract:
    - Contract removal is performed.
    - Rollback re-adds the contract entry.
    """
    env = build_environment(include_contract=True, contract_details_in_a=True, contract_details_in_b=False)
    transfer = TransferOfOwnership(
        source_conduit=env.source,
        target_conduit=env.target,
        spell=env.spell,
    )
    transfer._unshare_everywhere([{"type": "contract"}], env.spell)
    assert len(env.contract_ward_a.remove_calls) == 1
    transfer._rollback()
    assert len(env.contract_ward_a.add_calls) == 1


def test_repoint_borrowers_skips_peer_outbound_only() -> None:
    """
    Verify repointing skips peers with outbound_only policy.

    Contract:
    - No link or add is performed when peer policy blocks inbound use.
    """
    env = build_environment(
        include_contract=True,
        contract_details_in_a=True,
        contract_details_in_b=False,
        peer_policy=Policies.outbound_only,
    )
    transfer = TransferOfOwnership(
        source_conduit=env.source,
        target_conduit=env.target,
        spell=env.spell,
        force_unshare=False,
    )
    transfer._repoint_borrowers([{"type": "contract"}], env.spell)
    assert env.target_ward.link_calls == []
    assert env.target_ward.add_calls == []


def test_transfer_owned_dependencies_skips_non_owned(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Verify transfer skips dependencies not owned by the source.

    Contract:
    - No sub-transfer is created for non-owned dependencies.
    """
    env = build_environment(dependencies=["dep-1"], source_has_deps=True, target_has_deps=True)
    env.dependency_spells["dep-1"]._owner_conduit_id = TARGET_ID
    recorded: List[Any] = []

    class FakeTransfer:
        """
        Stub transfer used to detect unintended sub-transfer creation.
        """

        def __init__(self, **kwargs: Any) -> None:
            """
            Record any initialization that would indicate execution.

            Args:
                kwargs: TransferOfOwnership init arguments.
            """
            recorded.append(kwargs.get("spell"))

        def execute(self) -> None:
            """
            No-op execute for the stub transfer.
            """
            return None

    monkeypatch.setattr(transfer_module, "TransferOfOwnership", FakeTransfer)
    transfer = TransferOfOwnership(
        source_conduit=env.source,
        target_conduit=env.target,
        spell=env.spell,
        include_dependencies=True,
    )
    transfer._transfer_owned_dependencies(["dep-1"])
    assert recorded == []


def test_dirty_dependencies_marks_all_existing() -> None:
    """
    Verify dirtying dependencies marks each existing dependency.

    Contract:
    - All existing dependency lineages are marked dirty.
    """
    env = build_environment(dependencies=["dep-1", "dep-2"], source_has_deps=True, target_has_deps=True)
    transfer = TransferOfOwnership(
        source_conduit=env.source,
        target_conduit=env.target,
        spell=env.spell,
    )
    transfer._dirty_dependencies(["dep-1", "dep-2"])
    marked = {call["spell_index"].current for call in env.states_system.mark_calls}
    assert marked == {"dep-1", "dep-2"}


def test_record_change_intent_idempotent() -> None:
    """
    Verify repeated change-intent registration with same op_id is ignored.

    Contract:
    - Duplicate calls with the same op_id do not register twice.
    """
    env = build_environment()
    transfer = TransferOfOwnership(
        source_conduit=env.source,
        target_conduit=env.target,
        spell=env.spell,
    )
    summary = transfer.preflight()
    transfer._record_change_intent(summary)
    assert len(env.change_control_manager._register_calls) == 1


def test_clear_change_intent_calls_manager() -> None:
    """
    Verify change-control clear invokes the manager.

    Contract:
    - clear_pending_change is called for the spell index.
    """
    env = build_environment()
    transfer = TransferOfOwnership(
        source_conduit=env.source,
        target_conduit=env.target,
        spell=env.spell,
    )
    transfer._clear_change_intent(env.spell_index)
    assert env.change_control_manager._clear_calls == [env.spell_index.id]


def test_execute_failure_rolls_back_registry_and_records_incident() -> None:
    """
    Verify execute failure triggers rollback and incident reporting.

    Contract:
    - Registry and spellbook ownership are restored.
    - A failure incident is recorded.
    """
    env = build_environment()
    transfer = TransferOfOwnership(
        source_conduit=env.source,
        target_conduit=env.target,
        spell=env.spell,
        move_creations=True,
        force_unshare=True,
        invalidate_after_transfer=False,
    )
    transfer.preflight()

    def boom(_: Any) -> None:
        raise RuntimeError("boom")

    transfer._move_creations = boom
    with pytest.raises(RuntimeError, match="boom"):
        transfer.execute()
    assert env.spell_index in env.frame._spell_registry[SOURCE_ID]
    assert env.spell_index not in env.frame._spell_registry[TARGET_ID]
    with env.source._spellbook._lock:
        assert env.spell_index in env.source._spellbook._spells
    with env.target._spellbook._lock:
        assert env.spell_index not in env.target._spellbook._spells
    kinds = [incident["kind"] for incident in env.incident_manager.incidents]
    assert "ownership_transfer_failed" in kinds


def test_spell_in_registry_true_when_present() -> None:
    """
    Verify registry lookup returns True for a present index.

    Contract:
    - Presence in the registry yields True.
    """
    env = build_environment()
    transfer = TransferOfOwnership(
        source_conduit=env.source,
        target_conduit=env.target,
        spell=env.spell,
    )
    assert transfer._spell_in_registry(env.source, env.spell_index) is True


def test_spell_in_registry_false_when_absent() -> None:
    """
    Verify registry lookup returns False for a missing index.

    Contract:
    - Absence in the registry yields False.
    """
    env = build_environment()
    env.frame._spell_registry[SOURCE_ID].clear()
    transfer = TransferOfOwnership(
        source_conduit=env.source,
        target_conduit=env.target,
        spell=env.spell,
    )
    assert transfer._spell_in_registry(env.source, env.spell_index) is False


def test_spell_in_registry_false_on_error() -> None:
    """
    Verify registry lookup returns False on internal errors.

    Contract:
    - Exceptions during registry access yield False.
    """
    env = build_environment()
    transfer = TransferOfOwnership(
        source_conduit=env.source,
        target_conduit=env.target,
        spell=env.spell,
    )
    transfer._aether = object()
    assert transfer._spell_in_registry(env.source, env.spell_index) is False


def test_spell_in_spellbook_true_when_present() -> None:
    """
    Verify spellbook lookup returns True for a present spell.

    Contract:
    - Presence in the spellbook yields True.
    """
    env = build_environment()
    transfer = TransferOfOwnership(
        source_conduit=env.source,
        target_conduit=env.target,
        spell=env.spell,
    )
    assert transfer._spell_in_spellbook(env.source, env.spell) is True


def test_spell_in_spellbook_false_when_absent() -> None:
    """
    Verify spellbook lookup returns False for a missing spell.

    Contract:
    - Absence in the spellbook yields False.
    """
    env = build_environment()
    with env.source._spellbook._lock:
        env.source._spellbook._spells.pop(env.spell_index, None)
        env.source._spellbook._lookup_spells.pop(env.spell._key, None)
    transfer = TransferOfOwnership(
        source_conduit=env.source,
        target_conduit=env.target,
        spell=env.spell,
    )
    assert transfer._spell_in_spellbook(env.source, env.spell) is False


def test_spell_in_spellbook_false_on_error() -> None:
    """
    Verify spellbook lookup returns False when locking fails.

    Contract:
    - Exceptions during spellbook inspection yield False.
    """
    env = build_environment()
    env.source._spellbook._lock = None
    transfer = TransferOfOwnership(
        source_conduit=env.source,
        target_conduit=env.target,
        spell=env.spell,
    )
    assert transfer._spell_in_spellbook(env.source, env.spell) is False


def test_snapshot_cluster_shares_only_for_source_owner() -> None:
    """
    Verify cluster snapshot includes only source-owned shares.

    Contract:
    - Only shares for the source owner are returned.
    """
    env = build_environment(include_cluster=True)
    env.cluster.add_shared_spell("other-owner", env.spell_index)
    transfer = TransferOfOwnership(
        source_conduit=env.source,
        target_conduit=env.target,
        spell=env.spell,
    )
    snapshot = transfer._snapshot_cluster_shares(env.spell)
    assert snapshot
    assert all(entry["owner_id"] == SOURCE_ID for entry in snapshot)


def test_snapshot_cluster_shares_empty_when_no_match() -> None:
    """
    Verify cluster snapshot is empty when the spell is not shared.

    Contract:
    - No matching shares yields an empty list.
    """
    env = build_environment(include_cluster=True)
    env.cluster.shared_spells[SOURCE_ID].clear()
    transfer = TransferOfOwnership(
        source_conduit=env.source,
        target_conduit=env.target,
        spell=env.spell,
    )
    snapshot = transfer._snapshot_cluster_shares(env.spell)
    assert snapshot == []


def test_restore_cluster_shares_skips_missing_cluster() -> None:
    """
    Verify cluster restore skips entries with missing clusters.

    Contract:
    - Missing clusters are ignored without error.
    """
    env = build_environment(include_cluster=False)
    transfer = TransferOfOwnership(
        source_conduit=env.source,
        target_conduit=env.target,
        spell=env.spell,
    )
    transfer._restore_cluster_shares(
        [{"cluster": "missing", "owner_id": SOURCE_ID}],
        env.spell,
    )
    assert env.frame._conduit_clusters == {}


def test_restore_contract_entry_adds_with_default_permissions() -> None:
    """
    Verify restore uses default permissions when spell lacks permissions.

    Contract:
    - Missing permissions falls back to Permissions.read.
    """
    env = build_environment()
    spell_obj = SimpleNamespace(spell_id=DEFAULT_SPELL_ID, spell_index=env.spell_index)
    transfer = TransferOfOwnership(
        source_conduit=env.source,
        target_conduit=env.target,
        spell=env.spell,
    )
    transfer._restore_contract_entry(env.source_ward, spell_obj, env.peer, existed_before=True)
    assert len(env.source_ward.add_calls) == 1
    assert env.source_ward.add_calls[0]["permissions"] == Permissions.read
    assert env.source_ward.add_calls[0]["root_spell_id"] == DEFAULT_SPELL_ID


def test_restore_contract_entry_removes_when_not_existed() -> None:
    """
    Verify restore removes the spell when it did not exist originally.

    Contract:
    - Not existed entries are removed from the contract.
    """
    env = build_environment()
    transfer = TransferOfOwnership(
        source_conduit=env.source,
        target_conduit=env.target,
        spell=env.spell,
    )
    transfer._restore_contract_entry(env.source_ward, env.spell, env.peer, existed_before=False)
    assert len(env.source_ward.remove_calls) == 1


def test_restore_contract_entry_with_fallback_uses_primary() -> None:
    """
    Verify fallback helper uses the primary ward when available.

    Contract:
    - Primary ward receives the add call.
    - Fallback ward is not invoked.
    """
    env = build_environment()
    transfer = TransferOfOwnership(
        source_conduit=env.source,
        target_conduit=env.target,
        spell=env.spell,
    )

    transfer._restore_contract_entry_with_fallback(
        primary_ward=env.source_ward,
        fallback_ward=env.target_ward,
        primary_peer=env.peer,
        fallback_peer=env.target,
        spell_obj=env.spell,
    )

    assert len(env.source_ward.add_calls) == 1
    assert env.source_ward.add_calls[0]["conduit_id"] == env.peer._id
    assert env.target_ward.add_calls == []


def test_restore_contract_entry_with_fallback_uses_fallback_on_attribute_error() -> None:
    """
    Verify fallback helper uses the fallback when primary lacks the method.

    Contract:
    - AttributeError on primary triggers fallback add call.
    """
    env = build_environment()
    transfer = TransferOfOwnership(
        source_conduit=env.source,
        target_conduit=env.target,
        spell=env.spell,
    )
    primary_ward = SimpleNamespace()

    transfer._restore_contract_entry_with_fallback(
        primary_ward=primary_ward,
        fallback_ward=env.source_ward,
        primary_peer=env.peer,
        fallback_peer=env.target,
        spell_obj=env.spell,
    )

    assert len(env.source_ward.add_calls) == 1
    assert env.source_ward.add_calls[0]["conduit_id"] == env.target._id


def test_restore_contract_entry_with_fallback_skips_fallback_on_error() -> None:
    """
    Verify fallback helper skips fallback on non-AttributeError failures.

    Contract:
    - Primary errors other than AttributeError stop the restore.
    """
    env = build_environment()

    def _boom(**_kwargs: Any) -> None:
        """
        Purpose:
            Simulate a primary ward failure during contract restoration.
        Contract:
            - Always raises RuntimeError.
        """
        raise RuntimeError("boom")

    transfer = TransferOfOwnership(
        source_conduit=env.source,
        target_conduit=env.target,
        spell=env.spell,
    )
    primary_ward = SimpleNamespace(_add_spell_to_contract=_boom)

    transfer._restore_contract_entry_with_fallback(
        primary_ward=primary_ward,
        fallback_ward=env.source_ward,
        primary_peer=env.peer,
        fallback_peer=env.target,
        spell_obj=env.spell,
    )

    assert env.source_ward.add_calls == []


def test_rollback_spellbook_move_restores_source_ownership() -> None:
    """
    Verify rollback_spellbook_move restores spell ownership to source.

    Contract:
    - Spell is removed from target spellbook and restored to source.
    - Spell owner id is set back to the source.
    """
    env = build_environment()
    with env.source._spellbook._lock, env.target._spellbook._lock:
        env.source._spellbook._spells.pop(env.spell_index, None)
        env.source._spellbook._lookup_spells.pop(env.spell._key, None)
        env.target._spellbook._spells[env.spell_index] = env.spell
        env.target._spellbook._lookup_spells[env.spell._key] = env.spell_index
    env.spell._owner_conduit_id = TARGET_ID
    transfer = TransferOfOwnership(
        source_conduit=env.source,
        target_conduit=env.target,
        spell=env.spell,
    )
    transfer._rollback_spellbook_move(env.spell, env.source._spellbook, env.target._spellbook)
    with env.source._spellbook._lock, env.target._spellbook._lock:
        assert env.spell_index in env.source._spellbook._spells
        assert env.spell_index not in env.target._spellbook._spells
        assert env.spell._key in env.source._spellbook._lookup_spells
        assert env.spell._key not in env.target._spellbook._lookup_spells
    assert env.spell._owner_conduit_id == SOURCE_ID


def test_rollback_move_creation_restores_to_source() -> None:
    """
    Verify rollback_move_creation restores a creation to the source.

    Contract:
    - Target creations are removed and re-added to the source.
    """
    env = build_environment()
    env.target_creations.restore_spell_creations(DEFAULT_SPELL_ID, ["obj-1"])
    transfer = TransferOfOwnership(
        source_conduit=env.source,
        target_conduit=env.target,
        spell=env.spell,
    )
    transfer._rollback_move_creation(env.spell, "obj-1")
    assert env.target_creations.get_creations(DEFAULT_SPELL_ID) == []
    assert env.source_creations.get_creations(DEFAULT_SPELL_ID) == ["obj-1"]


def test_rollback_creations_move_restores_source_and_clears_target() -> None:
    """
    Verify rollback_creations_move restores source creations and clears target.

    Contract:
    - Target creations are extracted and source is restored.
    """
    env = build_environment(target_creations={DEFAULT_SPELL_ID: ["old"]})
    transfer = TransferOfOwnership(
        source_conduit=env.source,
        target_conduit=env.target,
        spell=env.spell,
    )
    transfer._rollback_creations_move(DEFAULT_SPELL_ID, ["new"])
    assert env.source_creations.get_creations(DEFAULT_SPELL_ID) == ["new"]
    assert env.target_creations.get_creations(DEFAULT_SPELL_ID) == []


def test_unshare_everywhere_ignores_cluster_borrower() -> None:
    """
    Verify unshare ignores cluster borrowers without contract operations.

    Contract:
    - Cluster borrower entries do not trigger contract add/remove calls.
    """
    env = build_environment()
    transfer = TransferOfOwnership(
        source_conduit=env.source,
        target_conduit=env.target,
        spell=env.spell,
    )
    transfer._unshare_everywhere([{"type": "cluster"}], env.spell)
    assert env.source_ward.add_calls == []
    assert env.source_ward.remove_calls == []


def test_repoint_borrowers_handles_add_failure_without_remove() -> None:
    """
    Verify repointing tolerates add failures without removing old entries.

    Contract:
    - Add failures do not remove existing contract entries.
    """
    env = build_environment(include_contract=True, contract_details_in_a=True, contract_details_in_b=False)

    def failing_add(**_: Any) -> None:
        """
        Raise an error to simulate contract add failures.

        Raises:
            RuntimeError: Always raised to force the error path.
        """
        raise RuntimeError("boom")

    env.target_ward._add_spell_to_contract = failing_add
    transfer = TransferOfOwnership(
        source_conduit=env.source,
        target_conduit=env.target,
        spell=env.spell,
        force_unshare=False,
    )
    transfer._repoint_borrowers([{"type": "contract"}], env.spell)
    assert env.contract_ward_a.remove_calls == []
    assert len(env.target_ward.link_calls) == 1


def test_enumerate_borrowers_omits_contract_without_details() -> None:
    """
    Verify borrowers enumeration omits contracts without matching details.

    Contract:
    - Contracts without spell details are not returned.
    """
    env = build_environment(include_contract=True, contract_details_in_a=False, contract_details_in_b=False)
    transfer = TransferOfOwnership(
        source_conduit=env.source,
        target_conduit=env.target,
        spell=env.spell,
    )
    borrowers = transfer._enumerate_borrowers(env.spell.spell_id)
    assert borrowers == []


def test_enumerate_creations_reports_existence() -> None:
    """
    Verify creation enumeration reports the spell existence.

    Contract:
    - Existence in the returned dict matches the spell.
    """
    env = build_environment()
    env.spell.existence = "unique"
    transfer = TransferOfOwnership(
        source_conduit=env.source,
        target_conduit=env.target,
        spell=env.spell,
    )
    assert transfer._enumerate_creations(env.spell) == {"existence": "unique"}


def test_lift_disable_no_state_is_noop() -> None:
    """
    Verify lift_disable does nothing when no state exists.

    Contract:
    - No state is created when none exists.
    """
    env = build_environment()
    transfer = TransferOfOwnership(
        source_conduit=env.source,
        target_conduit=env.target,
        spell=env.spell,
    )
    transfer._lift_disable(env.spell_index, gated=True)
    assert env.states_system.get_by_index_id(env.spell_index.id) is None


def test_rollback_executes_actions_in_reverse_order() -> None:
    """
    Verify rollback executes registered actions in reverse order.

    Contract:
    - Later-registered actions run before earlier ones.
    """
    env = build_environment()
    transfer = TransferOfOwnership(
        source_conduit=env.source,
        target_conduit=env.target,
        spell=env.spell,
    )
    history: List[str] = []

    def first_action() -> None:
        """
        Record the first rollback action in history.
        """
        history.append("first")

    def second_action() -> None:
        """
        Record the second rollback action in history.
        """
        history.append("second")

    transfer._register_rollback(first_action)
    transfer._register_rollback(second_action)
    transfer._rollback()
    assert history == ["second", "first"]


def test_assert_dynamic_mode_allows_dynamic() -> None:
    """
    Verify dynamic-mode assertion passes when both conduits are dynamic.

    Contract:
    - No exception is raised for dynamic source and target conduits.
    """
    env = build_environment()
    transfer = TransferOfOwnership(
        source_conduit=env.source,
        target_conduit=env.target,
        spell=env.spell,
    )
    transfer._assert_dynamic_mode()


def test_execute_without_preflight_runs_preflight() -> None:
    """
    Verify execute invokes preflight when no summary exists.

    Contract:
    - A preflight summary is created and change intent is cleared on success.
    """
    env = build_environment()
    transfer = TransferOfOwnership(
        source_conduit=env.source,
        target_conduit=env.target,
        spell=env.spell,
        invalidate_after_transfer=True,
    )
    transfer.execute()
    assert transfer._preflight_summary["spell_id"] == env.spell.spell_id
    assert env.change_control_manager._clear_calls == [env.spell_index.id]


def test_execute_invalidate_false_sets_gated_validity() -> None:
    """
    Verify execute lifts disable into gated validity when invalidation is off.

    Contract:
    - Final state validity is gated with structure_changed reason.
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
    assert state.validity == SpellValidity.gated
    assert state.change_reason == SpellStateChangeReason.structure_changed


def test_execute_failure_lifts_disable_gated() -> None:
    """
    Verify execute failure lifts disable into gated validity for safety.

    Contract:
    - Failure path sets validity to gated with structure_changed reason.
    """
    env = build_environment()
    transfer = TransferOfOwnership(
        source_conduit=env.source,
        target_conduit=env.target,
        spell=env.spell,
        move_creations=True,
        invalidate_after_transfer=False,
    )
    transfer.preflight()

    def boom(_: Any) -> None:
        """
        Raise an error to trigger the execute failure path.

        Args:
            _: Spell object ignored by this stub.
        Raises:
            RuntimeError: Always raised to simulate failure.
        """
        raise RuntimeError("boom")

    transfer._move_creations = boom
    with pytest.raises(RuntimeError, match="boom"):
        transfer.execute()
    state = env.states_system.get_by_index_id(env.spell_index.id)
    assert state is not None
    assert state.validity == SpellValidity.gated
    assert state.change_reason == SpellStateChangeReason.structure_changed


def test_mark_lineage_dirty_swallows_exception() -> None:
    """
    Verify mark_lineage_dirty swallows state update errors.

    Contract:
    - Exceptions from mark_structural_change are suppressed.
    """
    env = build_environment()

    def failing_mark(*, spell_index: SpellIndex, reason: SpellStateChangeReason) -> None:
        """
        Raise an error to simulate state update failure.

        Args:
            spell_index: SpellIndex being marked.
            reason: Reason for the change.
        Raises:
            RuntimeError: Always raised to simulate failure.
        """
        raise RuntimeError("boom")

    env.states_system.mark_structural_change = failing_mark
    transfer = TransferOfOwnership(
        source_conduit=env.source,
        target_conduit=env.target,
        spell=env.spell,
    )
    transfer._mark_lineage_dirty(env.spell_index)
    assert env.states_system.mark_calls == []


def test_rollback_continues_after_exception() -> None:
    """
    Verify rollback continues even if an action raises.

    Contract:
    - Subsequent rollback actions still execute.
    """
    env = build_environment()
    transfer = TransferOfOwnership(
        source_conduit=env.source,
        target_conduit=env.target,
        spell=env.spell,
    )
    history: List[str] = []

    def ok_action() -> None:
        """
        Record a successful rollback action.
        """
        history.append("ok")

    def failing_action() -> None:
        """
        Raise an error to simulate rollback failure.

        Raises:
            RuntimeError: Always raised to simulate failure.
        """
        raise RuntimeError("boom")

    transfer._register_rollback(ok_action)
    transfer._register_rollback(failing_action)
    transfer._rollback()
    assert history == ["ok"]


def test_rollback_clears_actions() -> None:
    """
    Verify rollback clears all registered actions.

    Contract:
    - Rollback leaves the action list empty.
    """
    env = build_environment()
    transfer = TransferOfOwnership(
        source_conduit=env.source,
        target_conduit=env.target,
        spell=env.spell,
    )

    def noop_action() -> None:
        """
        Provide a rollback action that does nothing.
        """
        return None

    transfer._register_rollback(noop_action)
    transfer._rollback()
    assert transfer._rollback_actions == []


def test_flip_registry_and_spellbooks_respects_existing_target_entry() -> None:
    """
    Verify flipping preserves target spellbook entries when already present.

    Contract:
    - Source spellbook entries are removed.
    - Target spellbook retains the spell without duplication.
    """
    env = build_environment()
    with env.target._spellbook._lock:
        env.target._spellbook._spells[env.spell_index] = env.spell
        env.target._spellbook._lookup_spells[env.spell._key] = env.spell_index
    env.frame._spell_registry[TARGET_ID].add(env.spell_index)
    transfer = TransferOfOwnership(
        source_conduit=env.source,
        target_conduit=env.target,
        spell=env.spell,
    )
    transfer._flip_registry_and_spellbooks(env.spell)
    assert env.spell_index not in env.frame._spell_registry[SOURCE_ID]
    assert env.spell_index in env.frame._spell_registry[TARGET_ID]
    with env.source._spellbook._lock, env.target._spellbook._lock:
        assert env.spell_index not in env.source._spellbook._spells
        assert env.spell_index in env.target._spellbook._spells
    assert env.spell._owner_conduit_id == TARGET_ID


def test_flip_registry_and_spellbooks_moves_spell_id_map() -> None:
    """
    Verify flipping updates spell_id maps for source and target spellbooks.

    Contract:
    - Source spell_id map loses the entry.
    - Target spell_id map gains the entry.
    - SpellIndex owner references point to the target book.
    """
    env = build_environment()
    transfer = TransferOfOwnership(
        source_conduit=env.source,
        target_conduit=env.target,
        spell=env.spell,
    )
    transfer._flip_registry_and_spellbooks(env.spell)
    spell_id = env.spell_index.current
    assert spell_id not in env.source._spellbook._spells_by_id
    assert env.target._spellbook._spells_by_id[spell_id] is env.spell
    assert env.spell.spell_index._owner_spellbook is env.target._spellbook
    assert env.spell.spell_index._owner_spell is env.spell


def test_flip_registry_and_spellbooks_raises_on_registry_failure() -> None:
    """
    Verify registry errors surface as a RuntimeError.

    Raises:
        RuntimeError: When registry removal fails.
    """
    env = build_environment()
    transfer = TransferOfOwnership(
        source_conduit=env.source,
        target_conduit=env.target,
        spell=env.spell,
    )

    def failing_remove(conduit_id: str, indices: set[SpellIndex], frame_name: str) -> None:
        """
        Raise an error to simulate registry removal failure.

        Args:
            conduit_id: Conduit id owning the indices.
            indices: Spell indices requested for removal.
            frame_name: Frame name for the registry.
        Raises:
            RuntimeError: Always raised to simulate failure.
        """
        raise RuntimeError("boom")

    transfer._aether._remove_spells_from_aether = failing_remove
    with pytest.raises(RuntimeError, match="Failed to flip registry"):
        transfer._flip_registry_and_spellbooks(env.spell)


def test_flip_registry_and_spellbooks_raises_on_spellbook_failure() -> None:
    """
    Verify spellbook errors surface as a RuntimeError.

    Raises:
        RuntimeError: When spellbook operations fail.
    """
    env = build_environment()

    class FailingLock:
        """
        Context manager that raises on entry to simulate lock failure.
        """

        def __enter__(self) -> "FailingLock":
            """
            Raise an error to simulate lock acquisition failure.

            Raises:
                RuntimeError: Always raised to simulate failure.
            """
            raise RuntimeError("lock boom")

        def __exit__(self, exc_type: Any, exc: Any, tb: Any) -> bool:
            """
            Exit the context manager without suppressing exceptions.

            Args:
                exc_type: Exception type if any.
                exc: Exception instance if any.
                tb: Traceback if any.
            Returns:
                False to avoid swallowing exceptions.
            """
            return False

    env.source._spellbook._lock = FailingLock()
    transfer = TransferOfOwnership(
        source_conduit=env.source,
        target_conduit=env.target,
        spell=env.spell,
    )
    with pytest.raises(RuntimeError, match="Failed to flip spellbooks"):
        transfer._flip_registry_and_spellbooks(env.spell)


def test_unshare_everywhere_uses_spell_permissions_on_rollback() -> None:
    """
    Verify unshare rollback restores permissions from the spell.

    Contract:
    - Rollback uses the spell permissions when present.
    """
    env = build_environment(include_contract=True, contract_details_in_a=True, contract_details_in_b=False)
    env.spell.permissions = Permissions.create
    transfer = TransferOfOwnership(
        source_conduit=env.source,
        target_conduit=env.target,
        spell=env.spell,
    )
    transfer._unshare_everywhere([{"type": "contract"}], env.spell)
    transfer._rollback()
    assert env.contract_ward_a.add_calls
    assert env.contract_ward_a.add_calls[0]["permissions"] == Permissions.create


def test_repoint_borrowers_skips_target_inbound_only() -> None:
    """
    Verify repointing skips when target policy blocks outbound links.

    Contract:
    - No link or add calls are made when target is inbound-only.
    """
    env = build_environment(include_contract=True, target_policy=Policies.inbound_only, contract_details_in_a=True)
    transfer = TransferOfOwnership(
        source_conduit=env.source,
        target_conduit=env.target,
        spell=env.spell,
    )
    transfer._repoint_borrowers([{"type": "contract"}], env.spell)
    assert env.target_ward.link_calls == []
    assert env.target_ward.add_calls == []


def test_repoint_borrowers_registers_two_rollbacks() -> None:
    """
    Verify repointing registers rollback actions for contract mutations.

    Contract:
    - Two rollback actions are registered for the contract path.
    """
    env = build_environment(include_contract=True, contract_details_in_a=True, contract_details_in_b=False)
    transfer = TransferOfOwnership(
        source_conduit=env.source,
        target_conduit=env.target,
        spell=env.spell,
    )
    transfer._repoint_borrowers([{"type": "contract"}], env.spell)
    assert len(transfer._rollback_actions) == 2


def test_repoint_borrowers_removes_only_when_existed() -> None:
    """
    Verify repointing removes only existing contract entries.

    Contract:
    - Only wards that had the spell detail are removed.
    """
    env = build_environment(include_contract=True, contract_details_in_a=False, contract_details_in_b=True)
    transfer = TransferOfOwnership(
        source_conduit=env.source,
        target_conduit=env.target,
        spell=env.spell,
    )
    transfer._repoint_borrowers([{"type": "contract"}], env.spell)
    assert env.contract_ward_a.remove_calls == []
    assert len(env.contract_ward_b.remove_calls) == 1


def test_enumerate_borrowers_dedup_contracts() -> None:
    """
    Verify borrower enumeration deduplicates contract entries.

    Contract:
    - Contracts with details on both sides yield a single entry.
    """
    env = build_environment(include_contract=True, contract_details_in_a=True, contract_details_in_b=True)
    transfer = TransferOfOwnership(
        source_conduit=env.source,
        target_conduit=env.target,
        spell=env.spell,
    )
    borrowers = transfer._enumerate_borrowers(env.spell.spell_id)
    contracts = [b for b in borrowers if b["type"] == "contract"]
    assert len(contracts) == 1


def test_enumerate_borrowers_cluster_matches_previous_version() -> None:
    """
    Verify borrower enumeration detects cluster shares by prior versions.

    Contract:
    - Spell ids present in a SpellIndex version set are matched.
    """
    env = build_environment(include_cluster=True)
    history_index = SpellIndex(env.spell.spell_id)
    history_index.update("new-version")
    env.cluster.shared_spells[SOURCE_ID] = {history_index}
    transfer = TransferOfOwnership(
        source_conduit=env.source,
        target_conduit=env.target,
        spell=env.spell,
    )
    borrowers = transfer._enumerate_borrowers(env.spell.spell_id)
    assert any(b["type"] == "cluster" for b in borrowers)


def test_enumerate_dependencies_returns_copy() -> None:
    """
    Verify dependency enumeration returns a decoupled list.

    Contract:
    - Mutating the returned list does not change the spell's dependencies.
    """
    env = build_environment(dependencies=["dep-1", "dep-2"])
    transfer = TransferOfOwnership(
        source_conduit=env.source,
        target_conduit=env.target,
        spell=env.spell,
    )
    deps = transfer._enumerate_dependencies(env.spell)
    deps.append("dep-3")
    assert env.spell.dependencies == ["dep-1", "dep-2"]


def test_record_incident_skips_warning_when_revalidator_present() -> None:
    """
    Verify incident reporting skips warning when revalidator exists.

    Contract:
    - Only the failure incident is emitted.
    """
    env = build_environment()

    def revalidate_stub() -> None:
        """
        Stand-in revalidator to suppress warning incidents.
        """
        return None

    env.change_control_manager._revalidate_fn = revalidate_stub
    transfer = TransferOfOwnership(
        source_conduit=env.source,
        target_conduit=env.target,
        spell=env.spell,
    )
    summary = {
        "spell_id": env.spell.spell_id,
        "spell_index": env.spell.spell_index,
        "source": env.source._id,
        "target": env.target._id,
        "borrowers": [],
        "dependencies": [],
        "creations": {},
        "op_id": "op-2",
        "options": {},
    }
    transfer._record_incident(summary, RuntimeError("boom"))
    kinds = [incident["kind"] for incident in env.incident_manager.incidents]
    assert kinds == ["ownership_transfer_failed"]


def test_clear_change_intent_swallows_exceptions() -> None:
    """
    Verify clear_change_intent suppresses manager exceptions.

    Contract:
    - Manager errors are ignored to keep cleanup best-effort.
    """
    env = build_environment()
    called = {"value": False}

    def failing_clear(index_id: str) -> None:
        """
        Record the call and raise an error.

        Args:
            index_id: SpellIndex id requested for clearing.
        Raises:
            RuntimeError: Always raised to simulate failure.
        """
        called["value"] = True
        raise RuntimeError("boom")

    env.change_control_manager.clear_pending_change = failing_clear
    transfer = TransferOfOwnership(
        source_conduit=env.source,
        target_conduit=env.target,
        spell=env.spell,
    )
    transfer._clear_change_intent(env.spell_index)
    assert called["value"] is True


def test_execute_clears_rollback_actions_on_success() -> None:
    """
    Verify execute clears rollback actions after success.

    Contract:
    - Rollback action list is empty after successful execute.
    """
    env = build_environment()
    transfer = TransferOfOwnership(
        source_conduit=env.source,
        target_conduit=env.target,
        spell=env.spell,
        invalidate_after_transfer=False,
    )

    def dummy_action() -> None:
        """
        Provide a dummy rollback action for cleanup verification.
        """
        return None

    transfer._register_rollback(dummy_action)
    transfer.execute()
    assert transfer._rollback_actions == []


def test_record_change_intent_registers_when_op_id_changes() -> None:
    """
    Verify change intent registers again when op_id differs.

    Contract:
    - A different op_id triggers a new registration.
    """
    env = build_environment()
    transfer = TransferOfOwnership(
        source_conduit=env.source,
        target_conduit=env.target,
        spell=env.spell,
    )
    summary = transfer.preflight()
    summary["op_id"] = "different-op"
    transfer._record_change_intent(summary)
    assert len(env.change_control_manager._register_calls) == 2


def test_record_change_intent_swallows_exceptions() -> None:
    """
    Verify change intent registration suppresses manager errors.

    Contract:
    - Exceptions from register_pending_change are ignored.
    """
    env = build_environment()
    transfer = TransferOfOwnership(
        source_conduit=env.source,
        target_conduit=env.target,
        spell=env.spell,
    )
    called = {"value": False}

    def failing_register(*, spell_index: SpellIndex, reason: str, metadata: Dict[str, Any]) -> None:
        """
        Record the call and raise an error.

        Args:
            spell_index: SpellIndex for the pending change.
            reason: Reason for the pending change.
            metadata: Metadata for the pending change.
        Raises:
            RuntimeError: Always raised to simulate failure.
        """
        called["value"] = True
        raise RuntimeError("boom")

    env.change_control_manager.register_pending_change = failing_register
    summary = {
        "spell_id": env.spell.spell_id,
        "spell_index": env.spell.spell_index,
        "source": env.source._id,
        "target": env.target._id,
        "borrowers": [],
        "dependencies": [],
        "creations": {},
        "op_id": "op-3",
        "options": {},
    }
    transfer._record_change_intent(summary)
    assert called["value"] is True


def test_record_incident_swallows_exceptions() -> None:
    """
    Verify incident reporting suppresses manager errors.

    Contract:
    - Exceptions from incident creation are ignored.
    """
    env = build_environment()
    transfer = TransferOfOwnership(
        source_conduit=env.source,
        target_conduit=env.target,
        spell=env.spell,
    )

    def failing_incident(**_: Any) -> None:
        """
        Raise an error to simulate incident creation failure.

        Raises:
            RuntimeError: Always raised to simulate failure.
        """
        raise RuntimeError("boom")

    env.incident_manager.create_incident = failing_incident
    summary = {
        "spell_id": env.spell.spell_id,
        "spell_index": env.spell.spell_index,
        "source": env.source._id,
        "target": env.target._id,
        "borrowers": [],
        "dependencies": [],
        "creations": {},
        "op_id": "op-4",
        "options": {},
    }
    transfer._record_incident(summary, RuntimeError("boom"))
    assert env.incident_manager.incidents == []


def test_deps_resolvable_on_target_true_when_all_present() -> None:
    """
    Verify dependency checks pass when all deps are resolvable on target.

    Contract:
    - All resolvable dependencies return True.
    """
    env = build_environment(dependencies=["dep-1", "dep-2"], target_has_deps=True)
    transfer = TransferOfOwnership(
        source_conduit=env.source,
        target_conduit=env.target,
        spell=env.spell,
    )
    assert transfer._deps_resolvable_on_target(["dep-1", "dep-2"]) is True


def test_dirty_dependencies_skips_missing_spell() -> None:
    """
    Verify missing dependency spells are skipped when dirtying.

    Contract:
    - Only existing dependency lineages are marked dirty.
    """
    env = build_environment(dependencies=["dep-1"], source_has_deps=True)
    transfer = TransferOfOwnership(
        source_conduit=env.source,
        target_conduit=env.target,
        spell=env.spell,
    )
    transfer._dirty_dependencies(["dep-1", "dep-missing"])
    marked = {call["spell_index"].current for call in env.states_system.mark_calls}
    assert marked == {"dep-1"}


def test_transfer_owned_dependencies_marks_dirty_when_invalidate_true(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Verify dependency transfers mark lineage dirty when invalidation is enabled.

    Contract:
    - Each transferred dependency triggers a structural change mark.
    """
    env = build_environment(dependencies=["dep-1"], source_has_deps=True, target_has_deps=True)
    recorded: List[Any] = []

    class FakeTransfer:
        """
        Stub transfer used to record dependency executions.
        """

        def __init__(self, **kwargs: Any) -> None:
            """
            Capture the dependency spell from kwargs.

            Args:
                kwargs: TransferOfOwnership init arguments.
            """
            self.spell = kwargs["spell"]

        def execute(self) -> None:
            """
            Record the executed spell.
            """
            recorded.append(self.spell)

    monkeypatch.setattr(transfer_module, "TransferOfOwnership", FakeTransfer)
    transfer = TransferOfOwnership(
        source_conduit=env.source,
        target_conduit=env.target,
        spell=env.spell,
        include_dependencies=True,
        invalidate_after_transfer=True,
    )
    transfer._transfer_owned_dependencies(["dep-1"])
    assert recorded == [env.dependency_spells["dep-1"]]
    assert env.states_system.mark_calls


def test_transfer_owned_dependencies_continues_after_exception(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Verify dependency transfer continues when a dependency lookup fails.

    Contract:
    - Later dependencies still trigger sub-transfer execution.
    """
    env = build_environment(dependencies=["dep-1", "dep-2"], source_has_deps=True, target_has_deps=True)
    recorded: List[Any] = []

    class FakeTransfer:
        """
        Stub transfer used to record successful dependency execution.
        """

        def __init__(self, **kwargs: Any) -> None:
            """
            Capture the dependency spell from kwargs.

            Args:
                kwargs: TransferOfOwnership init arguments.
            """
            self.spell = kwargs["spell"]

        def execute(self) -> None:
            """
            Record the executed spell.
            """
            recorded.append(self.spell)

    monkeypatch.setattr(transfer_module, "TransferOfOwnership", FakeTransfer)

    original_lookup = env.source.get_spell_by_id

    def lookup_with_failure(spell_id: str, frame_name: str) -> Optional[Any]:
        """
        Raise for dep-1 and delegate for other spell ids.

        Args:
            spell_id: Spell id requested.
            frame_name: Frame name for the lookup.
        Returns:
            Spell object or None when not found.
        Raises:
            RuntimeError: When dep-1 is requested.
        """
        if spell_id == "dep-1":
            raise RuntimeError("boom")
        return original_lookup(spell_id, frame_name)

    env.source.get_spell_by_id = lookup_with_failure
    transfer = TransferOfOwnership(
        source_conduit=env.source,
        target_conduit=env.target,
        spell=env.spell,
        include_dependencies=True,
    )
    transfer._transfer_owned_dependencies(["dep-1", "dep-2"])
    assert recorded == [env.dependency_spells["dep-2"]]


def test_move_creations_registers_rollback_and_restores() -> None:
    """
    Verify move_creations registers rollback and rollback restores creations.

    Contract:
    - Rollback returns creations to the source and clears target.
    """
    env = build_environment(source_creations={DEFAULT_SPELL_ID: ["obj-1"]})
    transfer = TransferOfOwnership(
        source_conduit=env.source,
        target_conduit=env.target,
        spell=env.spell,
    )
    transfer._move_creations(env.spell)
    assert env.source_creations.get_creations(DEFAULT_SPELL_ID) == []
    assert env.target_creations.get_creations(DEFAULT_SPELL_ID) == ["obj-1"]
    transfer._rollback()
    assert env.source_creations.get_creations(DEFAULT_SPELL_ID) == ["obj-1"]
    assert env.target_creations.get_creations(DEFAULT_SPELL_ID) == []


def test_teardown_creations_registers_rollback_and_restores() -> None:
    """
    Verify teardown_creations registers rollback and restores creations.

    Contract:
    - Rollback restores creations to the source.
    """
    env = build_environment(source_creations={DEFAULT_SPELL_ID: ["obj-1"]})
    transfer = TransferOfOwnership(
        source_conduit=env.source,
        target_conduit=env.target,
        spell=env.spell,
    )
    transfer._teardown_creations(env.spell)
    assert env.source_creations.get_creations(DEFAULT_SPELL_ID) == []
    transfer._rollback()
    assert env.source_creations.get_creations(DEFAULT_SPELL_ID) == ["obj-1"]


def test_rollback_without_snapshot_does_not_alter_cluster() -> None:
    """
    Verify rollback with no snapshot leaves cluster shares unchanged.

    Contract:
    - Cluster shares remain intact when snapshot is missing.
    """
    env = build_environment(include_cluster=True)
    original = set(env.cluster.shared_spells[SOURCE_ID])
    transfer = TransferOfOwnership(
        source_conduit=env.source,
        target_conduit=env.target,
        spell=env.spell,
    )
    transfer._preflight_summary = {}
    transfer._rollback()
    assert set(env.cluster.shared_spells[SOURCE_ID]) == original


def test_restore_cluster_shares_skips_missing_owner_id() -> None:
    """
    Verify restore skips entries missing the owner_id.

    Contract:
    - Missing owner_id entries do not modify cluster shares.
    """
    env = build_environment(include_cluster=True)
    env.cluster.shared_spells[SOURCE_ID].clear()
    transfer = TransferOfOwnership(
        source_conduit=env.source,
        target_conduit=env.target,
        spell=env.spell,
    )
    transfer._restore_cluster_shares([{"cluster": "cluster-1"}], env.spell)
    assert env.cluster.shared_spells.get(SOURCE_ID, set()) == set()


def test_restore_cluster_shares_skips_missing_cluster_name() -> None:
    """
    Verify restore skips entries missing the cluster name.

    Contract:
    - Missing cluster names do not modify cluster shares.
    """
    env = build_environment(include_cluster=True)
    env.cluster.shared_spells[SOURCE_ID].clear()
    transfer = TransferOfOwnership(
        source_conduit=env.source,
        target_conduit=env.target,
        spell=env.spell,
    )
    transfer._restore_cluster_shares([{"owner_id": SOURCE_ID}], env.spell)
    assert env.cluster.shared_spells.get(SOURCE_ID, set()) == set()


def test_snapshot_current_state_includes_cluster_shares() -> None:
    """
    Verify snapshot includes cluster share descriptors.

    Contract:
    - Cluster shares are present in the snapshot.
    """
    env = build_environment(include_cluster=True)
    transfer = TransferOfOwnership(
        source_conduit=env.source,
        target_conduit=env.target,
        spell=env.spell,
    )
    snapshot = transfer._snapshot_current_state(env.spell)
    assert snapshot["cluster_shares"]


def test_spell_in_registry_non_default_frame() -> None:
    """
    Verify registry lookup works for non-default frames.

    Contract:
    - Spell presence is detected in a named frame.
    """
    env = build_environment()
    frame = FakeFrame()
    frame._spell_registry[SOURCE_ID] = {env.spell_index}
    env.aether._aetheric_frames["frame-1"] = frame
    env.source._aetheric_frame = "frame-1"
    transfer = TransferOfOwnership(
        source_conduit=env.source,
        target_conduit=env.target,
        spell=env.spell,
    )
    assert transfer._spell_in_registry(env.source, env.spell_index) is True


def test_execute_include_dependencies_calls_transfer_owned_dependencies() -> None:
    """
    Verify execute delegates to owned dependency transfer when enabled.

    Contract:
    - Dependency list from preflight is passed to _transfer_owned_dependencies.
    """
    env = build_environment(dependencies=["dep-1"], source_has_deps=True, target_has_deps=True)
    transfer = TransferOfOwnership(
        source_conduit=env.source,
        target_conduit=env.target,
        spell=env.spell,
        include_dependencies=True,
        invalidate_after_transfer=False,
    )
    captured: List[str] = []

    def capture_deps(deps: List[str]) -> None:
        """
        Capture the dependency list passed by execute.

        Args:
            deps: Dependency list passed by execute.
        """
        captured.extend(deps)

    transfer._transfer_owned_dependencies = capture_deps
    transfer.execute()
    assert captured == ["dep-1"]


def test_execute_include_dependencies_skips_dirty_dependencies() -> None:
    """
    Verify execute does not dirty dependencies when include_dependencies is True.

    Contract:
    - _dirty_dependencies is not called when include_dependencies is enabled.
    """
    env = build_environment(dependencies=["dep-1"], source_has_deps=True, target_has_deps=True)
    transfer = TransferOfOwnership(
        source_conduit=env.source,
        target_conduit=env.target,
        spell=env.spell,
        include_dependencies=True,
        mark_dependencies_dirty=True,
        invalidate_after_transfer=False,
    )
    called = {"value": False}

    def mark_called(_: List[str]) -> None:
        """
        Record any unintended calls to dirty dependencies.
        """
        called["value"] = True

    transfer._dirty_dependencies = mark_called
    transfer._transfer_owned_dependencies = lambda _: None
    transfer.execute()
    assert called["value"] is False


def test_flip_registry_and_spellbooks_adds_to_target_when_source_missing() -> None:
    """
    Verify flipping adds to target even when source registry entry is missing.

    Contract:
    - Target registry gains the spell index regardless of source registry state.
    """
    env = build_environment()
    env.frame._spell_registry[SOURCE_ID].clear()
    transfer = TransferOfOwnership(
        source_conduit=env.source,
        target_conduit=env.target,
        spell=env.spell,
    )
    transfer._flip_registry_and_spellbooks(env.spell)
    assert env.spell_index in env.frame._spell_registry[TARGET_ID]
    assert env.spell_index not in env.frame._spell_registry[SOURCE_ID]


def test_unshare_everywhere_no_contracts_no_error() -> None:
    """
    Verify unshare handles empty contract sets without error.

    Contract:
    - No contract add/remove calls occur when there are no contracts.
    """
    env = build_environment()
    transfer = TransferOfOwnership(
        source_conduit=env.source,
        target_conduit=env.target,
        spell=env.spell,
    )
    transfer._unshare_everywhere([{"type": "contract"}], env.spell)
    assert env.source_ward.add_calls == []
    assert env.source_ward.remove_calls == []


def test_mark_lineage_disabled_swallows_register_lineage_error() -> None:
    """
    Verify mark_lineage_disabled suppresses register_lineage errors.

    Contract:
    - Exceptions from register_lineage are ignored.
    """
    env = build_environment()

    def failing_register(spell_index: SpellIndex, spell: Any) -> None:
        """
        Raise an error to simulate registration failure.

        Args:
            spell_index: SpellIndex being registered.
            spell: Spell object for the lineage.
        Raises:
            RuntimeError: Always raised to simulate failure.
        """
        raise RuntimeError("boom")

    env.states_system.register_lineage = failing_register
    transfer = TransferOfOwnership(
        source_conduit=env.source,
        target_conduit=env.target,
        spell=env.spell,
    )
    transfer._mark_lineage_disabled(env.spell_index)
    assert env.states_system.get_by_index_id(env.spell_index.id) is None


def test_repoint_borrowers_ignores_cluster_borrower() -> None:
    """
    Verify repointing ignores cluster borrower entries.

    Contract:
    - Cluster borrowers do not trigger link or contract updates.
    """
    env = build_environment()
    transfer = TransferOfOwnership(
        source_conduit=env.source,
        target_conduit=env.target,
        spell=env.spell,
    )
    transfer._repoint_borrowers([{"type": "cluster"}], env.spell)
    assert env.target_ward.link_calls == []
    assert env.target_ward.add_calls == []
