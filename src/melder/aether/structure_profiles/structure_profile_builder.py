from collections import deque
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

from melder.aether.aetheric_frame import AethericFrame
from melder.aether.conduit.conduit import Conduit
from melder.aether.dev_ops.spell_system_states.spell_system_state import SpellSystemState
from melder.aether.dev_ops.spell_system_states.spell_validity import SpellValidity
from melder.aether.dev_ops.spell_system_states.spell_system_states import SpellSystemStates
from melder.spellbook.spell import Spell
from melder.spellbook.spell_crafter.topology.spell_local_topology import SpellLocalTopology
from melder.spellbook.spell_crafter.dag.socket_kind import SocketKind
from melder.utilities.general_base.cleanable import Cleanable
from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg

from melder.aether.structure_profiles.structure_profile_models import (
    StructureHint,
    SpellStructureRecord,
    ConduitStructureProfile,
    FrameStructureProfile,
)
from melder.utilities.helpers.id_builder import IDBuilder


class StructureProfileBuilder(Cleanable):
    """
    Build structure profiles for frames, conduits, and spells.

    Purpose:
        Generate tooling-friendly structure profiles from live runtime state
        (spell registries, spell system states, and local topologies).

    Contract:
        - Consumes truth data from live registries without mutating them.
        - Derived hints are clearly separated and include provenance.
        - cleanup() is idempotent and clears internal state.
    """
    __melder_internal__ = _mrg.sentinel
    __slots__ = Cleanable.__slots__ + [
        "_max_related",
        "_id"
    ]

    def __init__(self, *, max_related: int = 10) -> None:
        """
        Initialize the builder.

        Args:
            max_related: Default maximum related-spell count for tooling queries.
        """
        super().__init__()
        self._id: str = IDBuilder.create_id()
        self._max_related: int = max_related

    def build_frame_profile(self, frame: AethericFrame) -> FrameStructureProfile:
        """
        Build a FrameStructureProfile from an AethericFrame.

        Args:
            frame: AethericFrame instance to profile.

        Returns:
            FrameStructureProfile: Aggregated profile for the frame.
        """
        self.check_cleaned()
        frame.check_cleaned()
        spell_system_states = frame.spell_system_states

        conduit_profiles: Dict[str, ConduitStructureProfile] = {}
        spell_records: Dict[str, SpellStructureRecord] = {}

        with frame._lock:
            conduits = list(frame._conduits.values()) if frame._conduits is not None else []
            cluster_items = list(frame._conduit_clusters.items()) if frame._conduit_clusters is not None else []

        for conduit in conduits:
            profile = self.build_conduit_profile(conduit, spell_system_states=spell_system_states)
            conduit_profiles[profile.conduit_id] = profile
            spell_records.update(profile.spell_records)

        clusters: List[Dict[str, Any]] = []
        for name, cluster in cluster_items:
            try:
                cluster.check_cleaned()
            except Exception:
                continue
            try:
                cluster_summary = {
                    "name": name,
                    "auto_link_dependencies": cluster.auto_link_dependencies,
                    "members": list(cluster.get_members()),
                    "shared_spells": cluster.get_shared_spells(),
                }
            except Exception:
                continue
            clusters.append(cluster_summary)

        return FrameStructureProfile(
            frame_id=frame._id,
            frame_name=frame.name,
            conduit_profiles=conduit_profiles,
            spell_records=spell_records,
            clusters=clusters,
            max_related=self._max_related,
            derived_hints=[],
        )

    def build_conduit_profile(
            self,
            conduit: Conduit,
            *,
            spell_system_states: Optional[SpellSystemStates] = None,
    ) -> ConduitStructureProfile:
        """
        Build a ConduitStructureProfile from a Conduit.

        Args:
            conduit: Conduit instance to profile.
            spell_system_states: Optional SpellSystemStates registry for topology data.

        Returns:
            ConduitStructureProfile: Profile for the conduit.
        """
        self.check_cleaned()
        conduit.check_cleaned()
        snapshot = conduit.snapshot_state()
        spell_records: Dict[str, SpellStructureRecord] = {}

        spellbook_snapshot = snapshot.get("spellbook_snapshot") or {}
        local_spells: Dict[Any, Spell] = spellbook_snapshot.get("local_spells", {})

        state_index = self._index_spell_system_states(spell_system_states)
        for spell_index, spell in local_spells.items():
            record = self.build_spell_record(
                spell=spell,
                spell_state=state_index.get(spell_index.id) if spell_system_states is not None else None,
                topology=spell_system_states.get_local_topology(spell_index) if spell_system_states is not None else None,
            )
            spell_records[record.spell_id] = record

        return ConduitStructureProfile(
            conduit_id=snapshot.get("conduit_id"),
            conduit_name=snapshot.get("conduit_name"),
            conduit_state=snapshot.get("conduit_state"),
            dynamic_environment=snapshot.get("dynamic_environment"),
            aetheric_frame=snapshot.get("aetheric_frame"),
            spell_records=spell_records,
            derived_hints=[],
        )

    def build_spell_record(
            self,
            *,
            spell: Spell,
            spell_state: Optional[SpellSystemState],
            topology: Optional[SpellLocalTopology],
    ) -> SpellStructureRecord:
        """
        Build a SpellStructureRecord for a specific spell.

        Args:
            spell: Spell instance to profile.
            spell_state: Optional SpellSystemState for dependency metadata.
            topology: Optional SpellLocalTopology for socket metadata.

        Returns:
            SpellStructureRecord: Structured record for the spell.
        """
        self.check_cleaned()
        dependencies = self._extract_dependencies(spell_state)
        sockets = self._extract_sockets(topology)
        derived_hints = self._derive_spell_hints(spell_state, topology)
        return SpellStructureRecord(
            spell_id=spell.spell_id,
            lineage_id=spell.spell_index.id,
            owner_conduit_id=spell._owner_conduit_id,
            binding_key=spell._key,
            existence=str(spell.existence),
            spell_type=str(spell.spell_type),
            permissions=str(spell.permissions),
            dependencies=dependencies,
            sockets=sockets,
            spellmap_defaults=[],
            derived_hints=derived_hints,
        )

    def cleanup(self) -> None:
        """
        Idempotently clear builder state.
        """
        if self._cleaned:
            return
        self._max_related = None
        self._cleaned = True

    def _index_spell_system_states(
            self,
            spell_system_states: Optional[SpellSystemStates],
    ) -> Dict[str, SpellSystemState]:
        """
        Build a lineage-id index for SpellSystemState entries.
        """
        if spell_system_states is None:
            return {}
        return {state.spell_index_id: state for state in spell_system_states.iter_states()}

    def _extract_dependencies(self, spell_state: Optional[SpellSystemState]) -> Dict[str, List[str]]:
        """
        Extract dependency lists from a SpellSystemState.
        """
        if spell_state is None:
            return {"direct_dependencies": [], "direct_dependents": []}
        return {
            "direct_dependencies": list(spell_state.direct_dependencies),
            "direct_dependents": list(spell_state.direct_dependents),
        }

    def _extract_sockets(self, topology: Optional[SpellLocalTopology]) -> List[Dict[str, Any]]:
        """
        Extract socket metadata from a SpellLocalTopology.
        """
        if topology is None:
            return []
        socket_records: List[Dict[str, Any]] = []
        for socket in topology.iter_sockets():
            socket_records.append(
                {
                    "spell_id": socket.spell_id,
                    "param_name": socket.param_name,
                    "position": socket.position,
                    "socket_kind": socket.socket_kind.name,
                    "is_collection": socket.is_collection,
                    "is_optional": socket.is_optional,
                    "target_spell_ids": list(socket.target_spell_ids),
                    "dependency_key": socket.dependency_key,
                    "contract_key": socket.contract_key,
                    "contract_late_binding": socket.contract_late_binding,
                    "is_contract_socket": socket.socket_kind in (SocketKind.SPELL_CONTRACT, SocketKind.MUTATION_CONTRACT),
                }
            )
        return socket_records

    def _derive_spell_hints(
            self,
            spell_state: Optional[SpellSystemState],
            topology: Optional[SpellLocalTopology],
    ) -> List[StructureHint]:
        """
        Derive basic hints about a spell's structure.
        """
        hints: List[StructureHint] = []
        if topology is not None:
            contract_socket_count = 0
            for socket in topology.iter_sockets():
                if socket.socket_kind in (SocketKind.SPELL_CONTRACT, SocketKind.MUTATION_CONTRACT):
                    contract_socket_count += 1
            if contract_socket_count > 0:
                hints.append(
                    StructureHint(
                        kind="contract_sockets_present",
                        description=f"{contract_socket_count} contract socket(s) present",
                        confidence=0.4,
                        provenance={
                            "source": "SpellLocalTopology",
                            "method": "socket_scan",
                        },
                        scope="spell",
                    )
                )
        if spell_state is not None and spell_state.validity is not None:
            validity = spell_state.validity
            if validity is not SpellValidity.valid:
                hints.append(
                    StructureHint(
                        kind="lineage_not_valid",
                        description=f"Lineage validity is {validity}",
                        confidence=0.6,
                        provenance={
                            "source": "SpellSystemState",
                            "method": "validity_check",
                        },
                        scope="spell",
                    )
                )
        return hints


class StructureProfileTooling(Cleanable):
    """
    Tool query surfaces for structure profiles.

    Purpose:
        Provide query helpers for UI/AI tooling without mutating live state.

    Contract:
        - All methods operate on snapshots provided via FrameStructureProfile.
        - No method mutates the underlying profiles.
    """
    __melder_internal__ = _mrg.sentinel
    __slots__ = Cleanable.__slots__ + [
        "_frame_profile",
        "_id"
    ]

    def __init__(self, frame_profile: FrameStructureProfile) -> None:
        """
        Initialize tooling helpers for a frame profile.

        Args:
            frame_profile: FrameStructureProfile snapshot to query.
        """
        super().__init__()
        self._id: str = IDBuilder.create_id()
        self._frame_profile = frame_profile

    def cleanup(self) -> None:
        """
        Idempotently clear tooling references.
        """
        if self._cleaned:
            return
        self._frame_profile = None
        self._cleaned = True

    def describe_spell_structure(self, spell_id: str) -> Optional[Dict[str, Any]]:
        """
        Describe a spell structure using the frame snapshot.

        Accepts a spell id or lineage id.
        """
        self.check_cleaned()
        lineage_index = self._lineage_index()
        spell_index = self._spell_index()
        record = self._resolve_record(spell_id, lineage_index, spell_index)
        if record is None:
            return None
        dependencies = (
            {key: list(values) for key, values in record.dependencies.items()}
            if record.dependencies is not None
            else {}
        )
        sockets: List[Dict[str, Any]] = []
        if record.sockets is not None:
            for socket in record.sockets:
                socket_copy = dict(socket)
                target_ids = socket_copy.get("target_spell_ids")
                if isinstance(target_ids, list):
                    socket_copy["target_spell_ids"] = list(target_ids)
                sockets.append(socket_copy)
        derived_hints = [
            self._hint_to_dict(hint)
            for hint in (record.derived_hints or [])
        ]
        return {
            "spell_id": record.spell_id,
            "lineage_id": record.lineage_id,
            "binding_key": record.binding_key,
            "dependencies": dependencies,
            "sockets": sockets,
            "derived_hints": derived_hints,
        }

    def find_related_spells(self, spell_id: str, k: Optional[int] = None) -> List[Tuple[str, int]]:
        """
        Find related spells based on shared dependencies.

        Accepts a spell id or lineage id.
        """
        self.check_cleaned()
        lineage_index = self._lineage_index()
        spell_index = self._spell_index()
        target = self._resolve_record(spell_id, lineage_index, spell_index)
        if target is None:
            return []
        target_lineage_id = target.lineage_id
        target_deps = set(target.dependencies.get("direct_dependencies", []))
        scores: List[Tuple[str, int]] = []
        for other_id, record in self._frame_profile.spell_records.items():
            if other_id == spell_id or record.lineage_id == target_lineage_id:
                continue
            overlap = target_deps.intersection(record.dependencies.get("direct_dependencies", []))
            if overlap:
                scores.append((other_id, len(overlap)))
        scores.sort(key=lambda item: item[1], reverse=True)
        limit = k if k is not None else self._default_related_limit()
        return scores[:limit]

    def explain_dependency_path(self, root_id: str, target_id: str) -> Optional[List[str]]:
        """
        Explain a dependency path from root to target using direct dependencies.

        Accepts spell ids or lineage ids.
        """
        self.check_cleaned()
        lineage_index = self._lineage_index()
        spell_index = self._spell_index()
        root_record = self._resolve_record(root_id, lineage_index, spell_index)
        if root_record is None:
            return None
        target_record = self._resolve_record(target_id, lineage_index, spell_index)
        if target_record is None:
            return None
        graph = self._build_dependency_graph()
        lineage_path = self._shortest_path(graph, root_record.lineage_id, target_record.lineage_id)
        if lineage_path is None:
            return None
        return [self._resolve_spell_id(lineage_id, lineage_index) for lineage_id in lineage_path]

    def list_subsystems(self) -> List[Dict[str, Any]]:
        """
        List subsystem clusters captured in the frame profile.
        """
        self.check_cleaned()
        clusters: List[Dict[str, Any]] = []
        for cluster in self._frame_profile.clusters:
            cluster_copy = dict(cluster)
            members = cluster_copy.get("members")
            if isinstance(members, list):
                cluster_copy["members"] = list(members)
            shared_spells = cluster_copy.get("shared_spells")
            if isinstance(shared_spells, dict):
                cluster_copy["shared_spells"] = {
                    key: set(value) if isinstance(value, set) else value
                    for key, value in shared_spells.items()
                }
            clusters.append(cluster_copy)
        return clusters

    def recommend_next_inspection(self, spell_id: str) -> List[str]:
        """
        Recommend candidate spells for next inspection.

        Accepts a spell id or lineage id.
        """
        self.check_cleaned()
        lineage_index = self._lineage_index()
        spell_index = self._spell_index()
        record = self._resolve_record(spell_id, lineage_index, spell_index)
        if record is None:
            return []
        neighbors = set(record.dependencies.get("direct_dependencies", []))
        neighbors.update(record.dependencies.get("direct_dependents", []))
        return [
            self._resolve_spell_id(lineage_id, lineage_index)
            for lineage_id in neighbors
        ]

    def _build_dependency_graph(self) -> Dict[str, List[str]]:
        """
        Build a dependency adjacency list from the frame snapshot.
        """
        graph: Dict[str, List[str]] = {}
        for record in self._frame_profile.spell_records.values():
            if record.lineage_id is None:
                continue
            graph[record.lineage_id] = list(record.dependencies.get("direct_dependencies", []))
        return graph

    def _shortest_path(
            self,
            graph: Dict[str, List[str]],
            root_id: str,
            target_id: str,
    ) -> Optional[List[str]]:
        """
        Find the shortest dependency path using BFS.
        """
        visited = set()
        queue = deque([(root_id, [root_id])])
        while queue:
            current, path = queue.popleft()
            if current == target_id:
                return path
            if current in visited:
                continue
            visited.add(current)
            for neighbor in graph.get(current, []):
                if neighbor not in visited:
                    queue.append((neighbor, path + [neighbor]))
        return None

    def _hint_to_dict(self, hint: StructureHint) -> Dict[str, Any]:
        """
        Convert a StructureHint into a plain dictionary.
        """
        provenance = (
            dict(hint.provenance)
            if isinstance(hint.provenance, dict)
            else hint.provenance
        )
        return {
            "kind": hint.kind,
            "description": hint.description,
            "confidence": hint.confidence,
            "provenance": provenance,
            "scope": hint.scope,
        }

    def _lineage_index(self) -> Dict[str, SpellStructureRecord]:
        """
        Build a lineage-id index from the frame snapshot.
        """
        index: Dict[str, SpellStructureRecord] = {}
        for record in self._frame_profile.spell_records.values():
            if record.lineage_id is None or record.lineage_id in index:
                continue
            index[record.lineage_id] = record
        return index

    def _spell_index(self) -> Dict[str, SpellStructureRecord]:
        """
        Build a spell-id index from the frame snapshot.
        """
        return dict(self._frame_profile.spell_records)

    def _resolve_record(
            self,
            record_id: str,
            lineage_index: Dict[str, SpellStructureRecord],
            spell_index: Dict[str, SpellStructureRecord],
    ) -> Optional[SpellStructureRecord]:
        """
        Resolve a spell or lineage id to a SpellStructureRecord.
        """
        if record_id in spell_index:
            return spell_index[record_id]
        return lineage_index.get(record_id)

    def _resolve_spell_id(
            self,
            lineage_id: str,
            lineage_index: Dict[str, SpellStructureRecord],
    ) -> str:
        """
        Resolve a lineage id to a spell id when available.
        """
        record = lineage_index.get(lineage_id)
        return record.spell_id if record is not None else lineage_id

    def _default_related_limit(self) -> int:
        """
        Provide the default related-spell limit when k is omitted.
        """
        max_related = self._frame_profile.max_related
        return max_related if max_related is not None else 5
