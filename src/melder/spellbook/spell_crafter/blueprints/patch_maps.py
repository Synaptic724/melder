from dataclasses import dataclass
from enum import IntEnum
from typing import Dict, List, Optional, Sequence

from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg
from melder.spellbook.spell_crafter.blueprints.root_resolution_blueprint import (
    RootResolutionBlueprint,
)
from melder.spellbook.spell_crafter.dag.dag_index import DagIndex, SocketRef
from melder.spellbook.spell_crafter.dag.directed_acyclic_work_graph import (
    DirectedAcyclicWorkGraph,
)
from melder.spellbook.spell_crafter.dag.socket_kind import SocketKind
from melder.spellbook.spell_crafter.dag.target_spec import TargetSpec, TargetSpecKind
from melder.utilities.general_base.cleanable import Cleanable


class _Specificity(IntEnum):
    """
    Internal

    Specificity ranking for override TargetSpec matches.

    Purpose:
        Provide a stable ordering to resolve conflicts when multiple override
        rules target the same socket.

    Contract:
        - Higher values indicate higher specificity.
        - Ordering is PATH > UNIQUE > BROADCAST.
    """
    __melder_internal__ = _mrg.sentinel
    PATH = 3
    UNIQUE = 2
    BROADCAST = 1


@dataclass(frozen=True, slots=True)
class MutationEdgePatch:
    """
    Internal

    Phase 10 mutation edge patch descriptor.

    Purpose:
        Capture a potential edge rewrite for a mutation contract socket.

    Contract:
        - child_spell_id identifies the dependent spell node.
        - param_name identifies the parameter the mutation targets.
        - param_path_id matches the socket reference path from the root.
        - old_parent_id is set when a single existing parent matches; otherwise None.
        - new_parent_id is populated at apply time by the mutation logic.

    Attributes:
        child_spell_id (str):
            Spell id of the dependent node.
        param_name (str):
            Parameter name associated with the mutation contract.
        param_path_id (int):
            PathId from the root occurrence to the socket.
        old_parent_id (Optional[str]):
            Prior parent id when resolvable to a single node; otherwise None.
        new_parent_id (Optional[str]):
            Replacement parent id to apply; None until resolved.
    """
    __melder_internal__ = _mrg.sentinel
    child_spell_id: str
    param_name: str
    param_path_id: int
    old_parent_id: Optional[str]
    new_parent_id: Optional[str]


class OverridePatchMap(Cleanable):
    """
    Internal

    Phase 10 artifact that caches TargetSpec -> SocketRef resolution.

    Purpose:
        Provide a precomputed lookup from override keys to socket references
        so runtime override application is O(matched sockets) instead of
        re-parsing the blueprint.

    Contract:
        - root_spell_id identifies the root spell used to build the map.
        - targets_by_spec and specificity_by_spec are owned and cleared on cleanup.
        - apply() raises when an override key cannot be resolved or conflicts.

    Threading:
        - Not thread-safe; treat as immutable after build.

    Lifecycle:
        - cleanup() is idempotent and clears owned collections.
    """
    __melder_internal__ = _mrg.sentinel
    __slots__ = Cleanable.__slots__ + [
        "_root_spell_id",
        "_targets_by_spec",
        "_specificity_by_spec",
        "_resolved_targets_by_raw_key",
        "_last_single_raw_key",
        "_last_single_value",
        "_last_single_override_map",
        "_last_single_socket_shape",
        "_last_multi_signature",
        "_last_multi_override_map",
        "_last_multi_socket_shape",
    ]

    def __init__(
            self,
            *,
            root_spell_id: str,
            targets_by_spec: Dict[str, List[SocketRef]],
            specificity_by_spec: Dict[str, _Specificity],
    ) -> None:
        """
        Initialize an override patch map.

        Contract:
            - All inputs must be non-None.
            - Inputs are stored by reference and treated as owned.
            - Callers must not mutate inputs after construction.

        Args:
            root_spell_id:
                Version id of the root spell used to build the map.
            targets_by_spec:
                Mapping from TargetSpec key to SocketRef list.
            specificity_by_spec:
                Mapping from TargetSpec key to specificity rank.

        Raises:
            ValueError:
                If any required input is None.
        """
        super().__init__()
        if root_spell_id is None:
            raise ValueError("root_spell_id must not be None.")
        if targets_by_spec is None:
            raise ValueError("targets_by_spec must not be None.")
        if specificity_by_spec is None:
            raise ValueError("specificity_by_spec must not be None.")
        self._root_spell_id = root_spell_id
        self._targets_by_spec = targets_by_spec
        self._specificity_by_spec = specificity_by_spec
        self._resolved_targets_by_raw_key: Dict[
            str,
            tuple[tuple[SocketRef, ...], _Specificity, tuple[tuple[object, ...], ...]],
        ] = {}
        self._last_single_raw_key: Optional[str] = None
        self._last_single_value: Optional[object] = None
        self._last_single_override_map: Optional[Dict[SocketRef, object]] = None
        self._last_single_socket_shape: Optional[tuple[tuple[object, ...], ...]] = None
        self._last_multi_signature: Optional[tuple[tuple[str, int], ...]] = None
        self._last_multi_override_map: Optional[Dict[SocketRef, object]] = None
        self._last_multi_socket_shape: Optional[tuple[tuple[object, ...], ...]] = None

    def cleanup(self) -> None:
        """
        Deterministically tear down the patch map and owned collections.

        Contract:
            - Idempotent: safe to call multiple times.
            - Clears owned containers and nulls references.
        """
        if self._cleaned:
            return
        self._cleaned = True
        self._targets_by_spec.clear()
        self._specificity_by_spec.clear()
        self._resolved_targets_by_raw_key.clear()

        del self._last_single_raw_key
        del self._last_single_value
        del self._last_single_override_map
        del self._last_single_socket_shape
        del self._last_multi_signature
        del self._last_multi_override_map
        del self._last_multi_socket_shape
        del self._root_spell_id
        del self._targets_by_spec
        del self._specificity_by_spec
        del self._resolved_targets_by_raw_key

    @property
    def root_spell_id(self) -> str:
        """
        Return the root spell id for this patch map.

        Contract:
            - Raises if the map has been cleaned.

        Returns:
            str: Root spell version id.

        Raises:
            RuntimeError:
                If the map has been cleaned.
        """
        self.check_cleaned()
        return self._root_spell_id

    def apply(self, spell_override: Dict[str, object]) -> Dict[SocketRef, object]:
        """
        Compute the socket->value mapping using cached targets.

        Contract:
            - Does not mutate phase10 target/specificity maps.
            - Memoizes raw-key target resolution for repeated runtime payloads.
            - Applies specificity rules to resolve competing overrides.
            - Mirrors DagTargetingEngine error semantics for unique/broadcast/path.

        Args:
            spell_override:
                Raw override payload keyed by TargetSpec-compatible strings.

        Returns:
            Dict[SocketRef, object]:
                Mapping of socket references to override values.

        Raises:
            ValueError:
                If a TargetSpec key is invalid (from TargetSpec.parse).
            RuntimeError:
                If no sockets match a key, if specificity is missing,
                or if conflicting overrides share the same specificity.
        """
        socket_map, _ = self.apply_with_socket_shape(
            spell_override=spell_override,
        )
        return socket_map

    def apply_with_socket_shape(
            self,
            spell_override: Dict[str, object],
    ) -> tuple[Dict[SocketRef, object], tuple[tuple[object, ...], ...]]:
        """
        Compute override sockets and deterministic socket-shape rows together.

        Contract:
            - Preserves apply() conflict/precedence semantics.
            - Returns deterministic socket shape rows for executor shape cache keys.
            - Avoids duplicate socket-shape rebuilds in runtime callers.

        Args:
            spell_override:
                Raw override payload keyed by TargetSpec-compatible strings.

        Returns:
            tuple[Dict[SocketRef, object], tuple[tuple[object, ...], ...]]:
                Socket->value map plus deterministic socket-shape rows.

        Raises:
            ValueError:
                If a TargetSpec key is invalid (from TargetSpec.parse).
            RuntimeError:
                If no sockets match a key, if specificity is missing,
                or if conflicting overrides share the same specificity.
        """
        self.check_cleaned()
        return self._apply_with_socket_shape_prechecked(
            spell_override=spell_override,
        )

    def _apply_with_socket_shape_prechecked(
            self,
            *,
            spell_override: Dict[str, object],
    ) -> tuple[Dict[SocketRef, object], tuple[tuple[object, ...], ...]]:
        """
        Internal hot-path entry for socket-shape override application.

        Purpose:
            Execute the same override map + socket-shape logic as
            `apply_with_socket_shape(...)` without repeating lifecycle checks
            when callers already hold a validated, active map instance.

        Contract:
            - Semantics match `apply_with_socket_shape(...)`.
            - Caller must ensure this map has not been cleaned.
            - Preserves conflict/precedence behavior and deterministic shape rows.

        Args:
            spell_override:
                Raw override payload keyed by TargetSpec-compatible strings.

        Returns:
            tuple[Dict[SocketRef, object], tuple[tuple[object, ...], ...]]:
                Socket->value map plus deterministic socket-shape rows.
        """
        if spell_override is None:
            return {}, ()
        if not spell_override:
            return {}, ()
        if len(spell_override) == 1:
            raw_key = next(iter(spell_override))
            value = spell_override[raw_key]
            if (
                    raw_key == self._last_single_raw_key
                    and value is self._last_single_value
            ):
                cached_map = self._last_single_override_map
                cached_shape = self._last_single_socket_shape
                if cached_map is not None and cached_shape is not None:
                    return (
                        cached_map,
                        cached_shape,
                    )
            matches, _, socket_shape = self._resolve_targets_for_raw_key(raw_key)
            if len(matches) == 1:
                override_map = {
                    matches[0]: value,
                }
            else:
                override_map = {
                    socket_ref: value
                    for socket_ref in matches
                }
            self._last_single_raw_key = raw_key
            self._last_single_value = value
            self._last_single_override_map = override_map
            self._last_single_socket_shape = socket_shape
            return (
                override_map,
                socket_shape,
            )

        multi_signature: Optional[tuple[tuple[str, int], ...]] = None
        override_count = len(spell_override)
        if override_count <= 4:
            multi_signature = tuple(
                sorted(
                    (
                        raw_key,
                        id(value),
                    )
                    for raw_key, value in spell_override.items()
                )
            )
            if multi_signature == self._last_multi_signature:
                cached_map = self._last_multi_override_map
                cached_shape = self._last_multi_socket_shape
                if cached_map is not None and cached_shape is not None:
                    return (
                        cached_map,
                        cached_shape,
                    )

        per_socket: Dict[SocketRef, tuple[_Specificity, object]] = {}

        for raw_key, value in spell_override.items():
            matches, level, _ = self._resolve_targets_for_raw_key(raw_key)

            for socket_ref in matches:
                existing = per_socket.get(socket_ref)
                if existing is None:
                    per_socket[socket_ref] = (level, value)
                    continue

                existing_level, existing_value = existing
                if level > existing_level:
                    per_socket[socket_ref] = (level, value)
                elif level == existing_level and existing_value != value:
                    raise RuntimeError(
                        f"Conflicting overrides for socket {socket_ref}: multiple rules "
                        f"with the same specificity."
                    )

        override_map = {
            socket: val
            for socket, (spec_level, val) in per_socket.items()
        }
        socket_shape = self._build_socket_shape_from_matches(
            matches=tuple(override_map),
        )
        if multi_signature is not None:
            self._last_multi_signature = multi_signature
            self._last_multi_override_map = override_map
            self._last_multi_socket_shape = socket_shape
        return (
            override_map,
            socket_shape,
        )

    def _resolve_targets_for_raw_key(
            self,
            raw_key: str,
    ) -> tuple[tuple[SocketRef, ...], _Specificity, tuple[tuple[object, ...], ...]]:
        """
        Resolve one raw override key to target sockets and specificity rank.

        Purpose:
            Cache TargetSpec parse + lookup results for repeated runtime override
            keys so hot-path apply calls avoid repeated key parsing work.

        Contract:
            - Raises the same validation errors as the previous inline apply path.
            - Caches successful resolutions by exact raw-key string.
            - Does not mutate phase10 target/specificity source maps.
        """
        cached = self._resolved_targets_by_raw_key.get(raw_key)
        if cached is not None:
            return cached

        spec = TargetSpec.parse(raw_key)
        spec_key = _spec_key(spec)
        matches = self._targets_by_spec.get(spec_key)
        if spec.kind is TargetSpecKind.PATH:
            if not matches:
                path_str = ">".join(spec.path or ())
                raise RuntimeError(
                    f"No sockets found for override path '{path_str}'."
                )
        elif spec.kind is TargetSpecKind.UNIQUE:
            count = 0 if not matches else len(matches)
            if count == 0:
                raise RuntimeError(
                    f"No sockets found for unique override '*{spec.param_name}'."
                )
            if count > 1:
                raise RuntimeError(
                    f"Unique override '*{spec.param_name}' matched {count} sockets; "
                    f"expected exactly one."
                )
        elif spec.kind is TargetSpecKind.BROADCAST:
            if not matches:
                raise RuntimeError(
                    f"No sockets found for broadcast override '**{spec.param_name}'."
                )
        else:
            raise RuntimeError(f"Unsupported TargetSpecKind: {spec.kind!r}")

        level = self._specificity_by_spec.get(spec_key)
        if level is None:
            raise RuntimeError(
                f"Specificity missing for override key '{raw_key}'."
            )

        resolved = (
            tuple(matches),
            level,
            self._build_socket_shape_from_matches(matches=tuple(matches)),
        )
        self._resolved_targets_by_raw_key[raw_key] = resolved
        return resolved

    @staticmethod
    def _build_socket_shape_from_matches(
            *,
            matches: tuple[SocketRef, ...],
    ) -> tuple[tuple[object, ...], ...]:
        """
        Build deterministic socket-shape rows from socket matches.

        Contract:
            - Returns rows sorted by (node_id, param_path_id, param_name, socket_kind).
            - Uses one/two-socket fast paths to avoid general sort overhead.
        """
        match_count = len(matches)
        if match_count == 0:
            return ()
        if match_count == 1:
            socket_ref = matches[0]
            return (
                (
                    socket_ref.node_id,
                    socket_ref.param_path_id,
                    socket_ref.param_name,
                    socket_ref.socket_kind.value,
                ),
            )
        if match_count == 2:
            first_ref = matches[0]
            second_ref = matches[1]
            first_row = (
                first_ref.node_id,
                first_ref.param_path_id,
                first_ref.param_name,
                first_ref.socket_kind.value,
            )
            second_row = (
                second_ref.node_id,
                second_ref.param_path_id,
                second_ref.param_name,
                second_ref.socket_kind.value,
            )
            if second_row < first_row:
                return (
                    second_row,
                    first_row,
                )
            return (
                first_row,
                second_row,
            )

        shape_rows: list[tuple[object, ...]] = []
        for socket_ref in matches:
            shape_rows.append(
                (
                    socket_ref.node_id,
                    socket_ref.param_path_id,
                    socket_ref.param_name,
                    socket_ref.socket_kind.value,
                )
            )
        shape_rows.sort()
        return tuple(shape_rows)


class MutationPatchMap(Cleanable):
    """
    Internal

    Phase 10 artifact that captures mutation rewires for TargetSpec keys.

    Purpose:
        Provide a precomputed mapping from mutation TargetSpec keys to the
        edge patches required to rewire the DAG.

    Contract:
        - root_spell_id identifies the root spell used to build the map.
        - targets_by_spec is owned and cleared on cleanup.

    Threading:
        - Not thread-safe; treat as immutable after build.

    Lifecycle:
        - cleanup() is idempotent and clears owned collections.
    """
    __melder_internal__ = _mrg.sentinel
    __slots__ = Cleanable.__slots__ + [
        "_root_spell_id",
        "_targets_by_spec",
    ]

    def __init__(
            self,
            *,
            root_spell_id: str,
            targets_by_spec: Dict[str, List[MutationEdgePatch]],
    ) -> None:
        """
        Initialize a mutation patch map.

        Contract:
            - All inputs must be non-None.
            - Inputs are stored by reference and treated as owned.
            - Callers must not mutate inputs after construction.

        Args:
            root_spell_id:
                Version id of the root spell used to build the map.
            targets_by_spec:
                Mapping from TargetSpec key to MutationEdgePatch list.

        Raises:
            ValueError:
                If any required input is None.
        """
        super().__init__()
        if root_spell_id is None:
            raise ValueError("root_spell_id must not be None.")
        if targets_by_spec is None:
            raise ValueError("targets_by_spec must not be None.")
        self._root_spell_id = root_spell_id
        self._targets_by_spec = targets_by_spec

    def cleanup(self) -> None:
        """
        Deterministically tear down the mutation patch map.

        Contract:
            - Idempotent: safe to call multiple times.
            - Clears owned containers and nulls references.
        """
        if self._cleaned:
            return
        self._cleaned = True
        self._targets_by_spec.clear()
        del self._root_spell_id
        del self._targets_by_spec

    @property
    def root_spell_id(self) -> str:
        """
        Return the root spell id for this patch map.

        Contract:
            - Raises if the map has been cleaned.

        Returns:
            str: Root spell version id.

        Raises:
            RuntimeError:
                If the map has been cleaned.
        """
        self.check_cleaned()
        return self._root_spell_id

    def apply(self, mutation_override: Dict[str, object]) -> List[MutationEdgePatch]:
        """
        Compute mutation patches for the supplied override payload.

        Contract:
            - Does not mutate internal maps.
            - Enforces PATH/UNIQUE/BROADCAST cardinality semantics.
            - Returns a list of patches with new_parent_id populated.

        Args:
            mutation_override:
                Mapping of override_key -> target spell id.

        Returns:
            List[MutationEdgePatch]:
                Patches to apply for the mutation override payload.

        Raises:
            ValueError:
                If a TargetSpec key is invalid (from TargetSpec.parse).
            RuntimeError:
                If no sockets match a key, if a unique key matches multiple
                sockets, or if targets are invalid.
        """
        self.check_cleaned()
        if not mutation_override:
            return []
        if not isinstance(mutation_override, dict):
            raise RuntimeError("mutation_override must be a dict of override_key -> spell_id.")

        patches: List[MutationEdgePatch] = []
        for raw_key, target_id in mutation_override.items():
            if not isinstance(raw_key, str) or not raw_key.strip():
                raise RuntimeError(f"Invalid mutation_override key: {raw_key!r}.")
            if not isinstance(target_id, str) or not target_id.strip():
                raise RuntimeError(
                    f"Invalid mutation_override target for key {raw_key!r}: "
                    "expected non-empty spell_id string."
                )

            spec = TargetSpec.parse(raw_key)
            spec_key = _spec_key(spec)
            matches = self._targets_by_spec.get(spec_key)

            if spec.kind is TargetSpecKind.PATH:
                if not matches:
                    path_str = ">".join(spec.path or ())
                    raise RuntimeError(
                        f"No mutation sockets found for override path '{path_str}'."
                    )
            elif spec.kind is TargetSpecKind.UNIQUE:
                count = 0 if not matches else len(matches)
                if count == 0:
                    raise RuntimeError(
                        f"No mutation sockets found for unique override '*{spec.param_name}'."
                    )
                if count > 1:
                    raise RuntimeError(
                        f"Unique override matched multiple mutation sockets for "
                        f"'*{spec.param_name}'."
                    )
            elif spec.kind is TargetSpecKind.BROADCAST:
                if not matches:
                    raise RuntimeError(
                        f"No mutation sockets found for broadcast override '**{spec.param_name}'."
                    )
            else:
                raise RuntimeError(f"Unsupported TargetSpecKind: {spec.kind!r}")

            for patch in matches:
                patches.append(
                    MutationEdgePatch(
                        child_spell_id=patch.child_spell_id,
                        param_name=patch.param_name,
                        param_path_id=patch.param_path_id,
                        old_parent_id=patch.old_parent_id,
                        new_parent_id=target_id,
                    )
                )

        return patches


def apply_override_patch_map(
        *,
        override_patch_map: OverridePatchMap,
        override_payload: object,
) -> Dict[SocketRef, object]:
    """
    Apply a Phase 10 OverridePatchMap with runtime normalization.

    Contract:
        - Non-dict overrides normalize to {} before apply().
    """
    raw_overrides = override_payload if isinstance(override_payload, dict) else {}
    return override_patch_map.apply(raw_overrides)


def apply_mutation_patch_map(
        *,
        blueprint: RootResolutionBlueprint,
        mutation_patch_map: MutationPatchMap,
        mutation_override: Dict[str, object],
) -> RootResolutionBlueprint:
    """
    Apply mutation overrides using a Phase 10 MutationPatchMap.

    Contract:
        - Returns the original blueprint when no overrides are supplied.
        - Clones the DAG and rewires mutation edges per patch map output.
        - Preserves root identity metadata from the source blueprint.
    """
    if not mutation_override:
        return blueprint

    patches = mutation_patch_map.apply(mutation_override)

    source = blueprint
    new_dag = DirectedAcyclicWorkGraph()
    for node_id in source.dag.nodes.keys():
        new_dag.add_node(node_id)
    for parent_key, parent_node in source.dag.nodes.items():
        for child_node in parent_node.dependents:
            child_key = child_node.id
            param_name = child_node.incoming_params.get(parent_node)
            socket_kind = source.dag._socket_kinds.get((parent_node, child_node))
            new_dag.add_dependency(
                parent_key=parent_key,
                child_key=child_key,
                param_name=param_name,
                socket_kind=socket_kind,
            )

    for patch in patches:
        child_id = patch.child_spell_id
        param_name = patch.param_name
        target_id = patch.new_parent_id
        child_node = new_dag.get_node(child_id)
        if child_node is None:
            continue

        to_remove = []
        for parent in list(child_node.dependencies):
            incoming_param = child_node.incoming_params.get(parent)
            if incoming_param == param_name:
                to_remove.append((parent.id, child_id, incoming_param))
        for parent_id, c_id, pname in to_remove:
            try:
                parent_node = new_dag.get_node(parent_id)
                if parent_node is not None:
                    child_node.dependencies.discard(parent_node)
                    parent_node.dependents.discard(child_node)
                    new_dag._socket_kinds.pop((parent_node, child_node), None)
            except Exception:
                pass

        if target_id is None:
            continue
        new_dag.add_node(target_id)
        new_dag.add_dependency(
            parent_key=target_id,
            child_key=child_id,
            param_name=param_name,
            socket_kind=SocketKind.MUTATION_CONTRACT,
        )

    ordered_ids = new_dag.collect_dependency_ids()

    new_socket_refs = list(source.socket_refs)
    new_index = DagIndex(path_registry=source.path_registry.clone())
    for ref in new_socket_refs:
        new_index.add_socket(ref)
    for patch in patches:
        if patch.new_parent_id is None:
            continue
        new_ref = SocketRef(
            node_id=patch.new_parent_id,
            param_name=patch.param_name,
            param_path_id=patch.param_path_id,
            socket_kind=SocketKind.MUTATION_CONTRACT,
        )
        new_socket_refs.append(new_ref)
        new_index.add_socket(new_ref)

    return RootResolutionBlueprint(
        root_spell_id=source.root_spell_id,
        root_lineage_id=source.root_lineage_id,
        dag=new_dag,
        ordered_node_ids=ordered_ids,
        socket_refs=new_socket_refs,
        dag_index=new_index,
    )


def apply_phase10_mutation_overrides(
        *,
        blueprint: RootResolutionBlueprint,
        mutation_patch_map: Optional[MutationPatchMap],
        mutation_override: Dict[str, object],
) -> RootResolutionBlueprint:
    """
    Apply Phase 10 mutation overrides with required patch-map validation.

    Contract:
        - Requires a mutation patch map when mutation_override is non-empty.
        - Returns the original blueprint when mutation_override is empty.
    """
    if not mutation_override:
        return blueprint
    if mutation_patch_map is None:
        raise RuntimeError(
            "Phase 10 mutation patch map is required for mutation overrides."
        )
    return apply_mutation_patch_map(
        blueprint=blueprint,
        mutation_patch_map=mutation_patch_map,
        mutation_override=mutation_override,
    )


def apply_phase10_override_payload(
        *,
        override_patch_map: Optional[OverridePatchMap],
        override_payload: object,
) -> Dict[SocketRef, object]:
    """
    Apply Phase 10 override payloads with required patch-map validation.

    Contract:
        - Requires an override patch map to normalize and apply overrides.
    """
    if override_patch_map is None:
        raise RuntimeError(
            "Phase 10 override patch map is required for meld execution."
        )
    return apply_override_patch_map(
        override_patch_map=override_patch_map,
        override_payload=override_payload,
    )


class PatchMapBuilder(object):
    """
    Internal

    Phase 10 compiler that precomputes override and mutation patch maps.

    Purpose:
        Convert a Phase 5 RootResolutionBlueprint into override and mutation
        patch maps used by CreationContext execution.

    Contract:
        - Does not mutate the provided blueprint.
        - Uses socket_refs and dag data from the blueprint.

    Threading:
        - Not thread-safe; use from a single planner thread.

    Lifecycle:
        - Builder does not own the blueprint and performs no cleanup.
    """
    __melder_internal__ = _mrg.sentinel
    __slots__ = [
        "_cleaned",
        "_blueprint",
        "_path_spec_key_by_id",
    ]

    def __init__(
            self,
            *,
            blueprint: RootResolutionBlueprint,
    ) -> None:
        """
        Initialize the patch map builder.

        Contract:
            - blueprint must be non-None.
            - The blueprint reference is stored as-is; no copy is made.

        Args:
            blueprint:
                Phase 5 root blueprint used to derive patch targets.

        Raises:
            ValueError:
                If blueprint is None.
        """
        if blueprint is None:
            raise ValueError("blueprint must not be None.")
        self._cleaned: bool = False
        self._blueprint = blueprint
        self._path_spec_key_by_id: Dict[int, str] = {}

    def cleanup(self) -> None:
        """
        Release borrowed blueprint references and owned memoized path state.

        Purpose:
            Mark the builder dead after one compile pass so the phase planner
            does not retain unnecessary references between runs.

        Contract:
            - Idempotent.
            - Does not mutate the borrowed root blueprint.
            - Clears only builder-owned cache state and borrowed references.

        Returns:
            None.
        """
        if self._cleaned:
            return

        self._cleaned = True
        self._path_spec_key_by_id.clear()
        del self._path_spec_key_by_id
        del self._blueprint

    def _require_active(self) -> None:
        """
        Raise when the builder is used after cleanup.

        Returns:
            None.

        Raises:
            RuntimeError:
                If the builder has already been cleaned.
        """
        if self._cleaned:
            raise RuntimeError("PatchMapBuilder has already been cleaned.")

    def _get_path_spec_key(self, path_id: int) -> str:
        """
        Return the canonical path key for a PathId with local memoization.

        Contract:
            - Returns stable `'a>b>c'` path keys produced by the blueprint path registry.
            - Reuses cached values for repeated PathIds within this builder lifetime.
            - Does not mutate blueprint path state.

        Args:
            path_id:
                Interned path id from the root blueprint registry.

        Returns:
            str:
                Canonical patch-map path key.
        """
        self._require_active()
        path_key = self._path_spec_key_by_id.get(path_id)
        if path_key is not None:
            return path_key
        path_key = self._blueprint.path_registry.format_path(path_id)
        self._path_spec_key_by_id[path_id] = path_key
        return path_key

    def build_override_patch_map(self) -> OverridePatchMap:
        """
        Build the override patch map from the root blueprint.

        Contract:
            - Targets are keyed by explicit path, unique-by-name, and broadcast forms.
            - Specificity is assigned per key using the _Specificity enum.
            - Does not mutate the blueprint.

        Returns:
            OverridePatchMap: Compiled override patch map for the root spell.
        """
        self._require_active()
        root_spell_id = self._blueprint.root_spell_id
        targets_by_spec: Dict[str, List[SocketRef]] = {}
        specificity_by_spec: Dict[str, _Specificity] = {}

        sockets = list(self._blueprint.socket_refs or [])
        by_name: Dict[str, List[SocketRef]] = {}
        for socket in sockets:
            by_name.setdefault(socket.param_name, []).append(socket)
            path_key = self._get_path_spec_key(socket.param_path_id)
            targets_by_spec[path_key] = [socket]
            specificity_by_spec[path_key] = _Specificity.PATH

        for name, matches in by_name.items():
            broadcast_key = f"**{name}"
            targets_by_spec[broadcast_key] = list(matches)
            specificity_by_spec[broadcast_key] = _Specificity.BROADCAST
            unique_key = f"*{name}"
            targets_by_spec[unique_key] = list(matches)
            specificity_by_spec[unique_key] = _Specificity.UNIQUE

        return OverridePatchMap(
            root_spell_id=root_spell_id,
            targets_by_spec=targets_by_spec,
            specificity_by_spec=specificity_by_spec,
        )

    def build_mutation_patch_map(self) -> MutationPatchMap:
        """
        Build the mutation patch map from the root blueprint.

        Contract:
            - Only mutation-contract sockets are included.
            - Targets are keyed by explicit path, unique-by-name, and broadcast forms.
            - Does not mutate the blueprint.

        Returns:
            MutationPatchMap: Compiled mutation patch map for the root spell.
        """
        self._require_active()
        root_spell_id = self._blueprint.root_spell_id
        targets_by_spec: Dict[str, List[MutationEdgePatch]] = {}

        sockets = [
            ref for ref in (self._blueprint.socket_refs or [])
            if ref.socket_kind is SocketKind.MUTATION_CONTRACT
        ]
        by_name: Dict[str, List[SocketRef]] = {}
        for socket in sockets:
            by_name.setdefault(socket.param_name, []).append(socket)
            path_key = self._get_path_spec_key(socket.param_path_id)
            targets_by_spec[path_key] = _build_mutation_patches(
                blueprint=self._blueprint,
                socket_ref=socket,
            )

        for name, matches in by_name.items():
            grouped_patches = _build_mutation_patches_for_group(
                blueprint=self._blueprint,
                socket_refs=matches,
            )
            broadcast_key = f"**{name}"
            targets_by_spec[broadcast_key] = list(grouped_patches)
            unique_key = f"*{name}"
            targets_by_spec[unique_key] = list(grouped_patches)

        return MutationPatchMap(
            root_spell_id=root_spell_id,
            targets_by_spec=targets_by_spec,
        )


def _spec_key(spec: TargetSpec) -> str:
    """
    Return the canonical lookup key for a TargetSpec.

    Contract:
        - PATH -> "a>b>c" form.
        - UNIQUE -> "*param".
        - BROADCAST -> "**param".

    Args:
        spec:
            Parsed TargetSpec instance.

    Returns:
        str: Canonical key used by patch maps.

    Raises:
        RuntimeError:
            If spec.kind is unsupported.
    """
    if spec.kind is TargetSpecKind.BROADCAST:
        return f"**{spec.param_name}"
    if spec.kind is TargetSpecKind.UNIQUE:
        return f"*{spec.param_name}"
    if spec.kind is TargetSpecKind.PATH:
        return ">".join(spec.path or ())
    raise RuntimeError(f"Unsupported TargetSpecKind: {spec.kind}")


def _build_mutation_patches(
        *,
        blueprint: RootResolutionBlueprint,
        socket_ref: SocketRef,
) -> List[MutationEdgePatch]:
    """
    Build mutation edge patches for a single socket reference.

    Contract:
        - Uses the blueprint DAG to find the prior parent for this parameter.
        - If exactly one matching parent exists, old_parent_id is set to it.
        - If none or multiple parents match, old_parent_id is None.

    Args:
        blueprint:
            Root blueprint providing DAG context.
        socket_ref:
            Socket reference describing the mutation contract parameter.

    Returns:
        List[MutationEdgePatch]:
            A list containing a single patch descriptor.
    """
    child_id = socket_ref.node_id
    child_node = blueprint.dag.get_node(child_id) if blueprint.dag is not None else None
    old_parents: List[str] = []
    if child_node is not None:
        for parent in list(child_node.dependencies):
            param_name = child_node.incoming_params.get(parent)
            if param_name == socket_ref.param_name:
                old_parents.append(parent.id)

    if len(old_parents) == 1:
        old_parent_id = old_parents[0]
    else:
        old_parent_id = None

    return [
        MutationEdgePatch(
            child_spell_id=child_id,
            param_name=socket_ref.param_name,
            param_path_id=socket_ref.param_path_id,
            old_parent_id=old_parent_id,
            new_parent_id=None,
        )
    ]


def _build_mutation_patches_for_group(
        *,
        blueprint: RootResolutionBlueprint,
        socket_refs: List[SocketRef],
) -> List[MutationEdgePatch]:
    """
    Build mutation patches for a group of socket references.

    Contract:
        - Returns the concatenation of per-socket patches.
        - Does not mutate the blueprint.

    Args:
        blueprint:
            Root blueprint providing DAG context.
        socket_refs:
            Socket references to expand into patches.

    Returns:
        List[MutationEdgePatch]:
            Aggregated list of patch descriptors.
    """
    patches: List[MutationEdgePatch] = []
    for socket_ref in socket_refs:
        patches.extend(
            _build_mutation_patches(
                blueprint=blueprint,
                socket_ref=socket_ref,
            )
        )
    return patches
