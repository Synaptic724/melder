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
    __melder_internal__ = _mrg.sentinel
    PATH = 3
    UNIQUE = 2
    BROADCAST = 1


@dataclass(frozen=True)
class MutationEdgePatch:
    __melder_internal__ = _mrg.sentinel
    child_spell_id: str
    param_name: str
    old_parent_id: Optional[str]
    new_parent_id: Optional[str]


class OverridePatchMap(Cleanable):
    """
    Internal

    Phase 10 artifact that caches TargetSpec -> SocketRef resolution.
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
        self.check_cleaned()
        return self._root_spell_id

    def apply(self, spell_override: Dict[str, object]) -> Dict[SocketRef, object]:
        """
        Compute the socket->value mapping using cached targets.
        """
        self.check_cleaned()
        if spell_override is None:
            return {}

        per_socket: Dict[SocketRef, tuple[_Specificity, object]] = {}

        for raw_key, value in spell_override.items():
            spec = TargetSpec.parse(raw_key)
            spec_key = _spec_key(spec)
            matches = self._targets_by_spec.get(spec_key)
            if not matches:
                raise RuntimeError(
                    f"No sockets found for override key '{raw_key}'."
                )
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
        super().__init__()
        if root_spell_id is None:
            raise ValueError("root_spell_id must not be None.")
        if targets_by_spec is None:
            raise ValueError("targets_by_spec must not be None.")
        self._root_spell_id = root_spell_id
        self._targets_by_spec = targets_by_spec

    def cleanup(self) -> None:
        if self._cleaned:
            return
        self._cleaned = True
        self._targets_by_spec.clear()
        self._root_spell_id = None
        self._targets_by_spec = None

    @property
    def root_spell_id(self) -> str:
        self.check_cleaned()
        return self._root_spell_id


class PatchMapBuilder(object):
    """
    Internal

    Phase 10 compiler that precomputes override and mutation patch maps.
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
        if blueprint is None:
            raise ValueError("blueprint must not be None.")
        self._blueprint = blueprint

    def build_override_patch_map(self) -> OverridePatchMap:
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
            if len(matches) == 1:
                unique_key = f"*{name}"
                targets_by_spec[unique_key] = list(matches)
                specificity_by_spec[unique_key] = _Specificity.UNIQUE

        return OverridePatchMap(
            root_spell_id=root_spell_id,
            targets_by_spec=targets_by_spec,
            specificity_by_spec=specificity_by_spec,
        )

    def build_mutation_patch_map(self) -> MutationPatchMap:
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
    patches: List[MutationEdgePatch] = []
    for socket_ref in socket_refs:
        patches.extend(
            _build_mutation_patches(
                blueprint=blueprint,
                socket_ref=socket_ref,
            )
        )
    return patches
