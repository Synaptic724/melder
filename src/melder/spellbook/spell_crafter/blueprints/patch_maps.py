from dataclasses import dataclass
from enum import IntEnum
from typing import Dict, List, Optional

from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg
from melder.spellbook.spell_crafter.blueprints.root_resolution_blueprint import (
    RootResolutionBlueprint,
)
from melder.spellbook.spell_crafter.dag.dag_index import SocketRef
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


@dataclass(frozen=True)
class MutationEdgePatch:
    """
    Internal

    Phase 10 mutation edge patch descriptor.

    Purpose:
        Capture a potential edge rewrite for a mutation contract socket.

    Contract:
        - child_spell_id identifies the dependent spell node.
        - param_name identifies the parameter the mutation targets.
        - old_parent_id is set when a single existing parent matches; otherwise None.
        - new_parent_id is populated at apply time by the mutation logic.

    Attributes:
        child_spell_id (str):
            Spell id of the dependent node.
        param_name (str):
            Parameter name associated with the mutation contract.
        old_parent_id (Optional[str]):
            Prior parent id when resolvable to a single node; otherwise None.
        new_parent_id (Optional[str]):
            Replacement parent id to apply; None until resolved.
    """
    __melder_internal__ = _mrg.sentinel
    child_spell_id: str
    param_name: str
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
        self._root_spell_id = None
        self._targets_by_spec = None
        self._specificity_by_spec = None

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
            - Does not mutate internal maps.
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
        self.check_cleaned()
        if spell_override is None:
            return {}

        per_socket: Dict[SocketRef, tuple[_Specificity, object]] = {}

        for raw_key, value in spell_override.items():
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

        return {socket: val for socket, (spec_level, val) in per_socket.items()}


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
        self._root_spell_id = None
        self._targets_by_spec = None

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


class PatchMapBuilder(object):
    """
    Internal

    Phase 10 compiler that precomputes override and mutation patch maps.

    Purpose:
        Convert a Phase 5 RootResolutionBlueprint into override and mutation
        patch maps used by the meld runtime.

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
        "_blueprint",
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
        self._blueprint = blueprint

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
        root_spell_id = self._blueprint.root_spell_id
        targets_by_spec: Dict[str, List[SocketRef]] = {}
        specificity_by_spec: Dict[str, _Specificity] = {}

        sockets = list(self._blueprint.socket_refs or [])
        by_name: Dict[str, List[SocketRef]] = {}
        for socket in sockets:
            by_name.setdefault(socket.param_name, []).append(socket)
            path_key = ">".join(socket.param_path)
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
        root_spell_id = self._blueprint.root_spell_id
        targets_by_spec: Dict[str, List[MutationEdgePatch]] = {}

        sockets = [
            ref for ref in (self._blueprint.socket_refs or [])
            if ref.socket_kind is SocketKind.MUTATION_CONTRACT
        ]
        by_name: Dict[str, List[SocketRef]] = {}
        for socket in sockets:
            by_name.setdefault(socket.param_name, []).append(socket)
            path_key = ">".join(socket.param_path)
            targets_by_spec[path_key] = _build_mutation_patches(
                blueprint=self._blueprint,
                socket_ref=socket,
            )

        for name, matches in by_name.items():
            broadcast_key = f"**{name}"
            targets_by_spec[broadcast_key] = _build_mutation_patches_for_group(
                blueprint=self._blueprint,
                socket_refs=matches,
            )
            if len(matches) == 1:
                unique_key = f"*{name}"
                targets_by_spec[unique_key] = _build_mutation_patches(
                    blueprint=self._blueprint,
                    socket_ref=matches[0],
                )

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
