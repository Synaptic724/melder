from typing import TYPE_CHECKING, Dict, List, Optional, Tuple

from melder.aether.spellbook.spell_compiler.artifact_processor.data.spell_mutation_targeting_analysis import (
    SpellMutationPatchRef,
    SpellMutationTargetingAnalysis,
)
from melder.aether.spellbook.spell_compiler.artifact_processor.spell_artifact_processor_strategy import (
    SpellArtifactProcessorStrategy,
)
from melder.aether.spellbook.spell_compiler.dag.socket_kind import SocketKind
from melder.aether.spellbook.spell_compiler.dag.target_spec import (
    TargetSpecKind,
)

if TYPE_CHECKING:
    from melder.aether.spellbook.spell import Spell
    from melder.aether.spellbook.spell_compiler.artifact_processor.spell_codegen_model import (
        SpellCodegenModel,
    )
    from melder.aether.spellbook.spell_compiler.artifact_processor.data.spell_override_targeting_analysis import (
        SpellOverrideTargetRef,
    )
    from melder.aether.spellbook.spell_compiler.spell_compiler_artifact import (
        SpellCompilerArtifact,
    )


class SpellMutationTargetingProcessorStrategy(SpellArtifactProcessorStrategy):
    """
    Fit the mutation-targeting section of `SpellCodegenModel`.

    Purpose:
        Derive normalized mutation-targeting truth directly from the rooted
        blueprint DAG and mutation-contract sockets so the processor does not
        depend on old `MutationPatchMap` objects.
    """

    __slots__ = ()

    @property
    def strategy_id(self) -> str:
        """
        Return the stable processor strategy id.
        """
        return "spell_mutation_targeting_processor"

    def process(
            self,
            spell: "Spell",
            artifact: "SpellCompilerArtifact",
            model: "SpellCodegenModel",
    ) -> None:
        """
        Fit the mutation-targeting model section.

        Contract:
            - Reads rooted blueprint truth from `artifact._root_blueprint_phase5`.
            - Writes only `model.mutation_targeting_shape` plus compatible
              top-level mutation-targeting selectors.
            - Does not read old `MutationPatchMap` objects.
        """
        _ = spell
        root_blueprint = artifact._root_blueprint_phase5
        if root_blueprint is None:
            raise RuntimeError(
                "SpellMutationTargetingProcessorStrategy requires Phase 5 root blueprint truth."
            )

        patches_by_spec: Dict[str, Tuple[SpellMutationPatchRef, ...]] = {}
        path_depth_histogram: Dict[int, int] = {}
        by_name: Dict[str, List[SpellMutationPatchRef]] = {}

        for socket_ref in root_blueprint.socket_refs:
            if socket_ref.socket_kind is not SocketKind.MUTATION_CONTRACT:
                continue
            patch_ref = self._build_patch_ref(
                root_blueprint=root_blueprint,
                node_id=socket_ref.node_id,
                param_name=socket_ref.param_name,
                param_path_id=socket_ref.param_path_id,
            )
            by_name.setdefault(socket_ref.param_name, []).append(patch_ref)

            path_key = root_blueprint.path_registry.format_path(socket_ref.param_path_id)
            patches_by_spec[path_key] = (patch_ref,)

            depth = root_blueprint.path_registry.depth(socket_ref.param_path_id)
            path_depth_histogram[depth] = path_depth_histogram.get(depth, 0) + 1

        for param_name, patches in by_name.items():
            broadcast_key = self._build_target_key(
                kind=TargetSpecKind.BROADCAST,
                param_name=param_name,
            )
            unique_key = self._build_target_key(
                kind=TargetSpecKind.UNIQUE,
                param_name=param_name,
            )
            patch_tuple = tuple(patches)
            patches_by_spec[broadcast_key] = patch_tuple
            patches_by_spec[unique_key] = patch_tuple

        mutation_targeting_shape = SpellMutationTargetingAnalysis(
            patches_by_spec=patches_by_spec,
            path_depth_histogram=tuple(sorted(path_depth_histogram.items())),
        )
        previous_mutation_targeting_shape = model.mutation_targeting_shape
        model.mutation_targeting_shape = mutation_targeting_shape
        model.mutation_target_spec_count = mutation_targeting_shape.target_spec_count
        model.mutation_patch_count = mutation_targeting_shape.patch_count
        model.mutation_targeted_child_spell_count = (
            mutation_targeting_shape.targeted_child_spell_count
        )
        model.max_mutation_patches_per_spec = (
            mutation_targeting_shape.max_patches_per_spec
        )
        model.max_mutation_target_path_depth = (
            mutation_targeting_shape.max_target_path_depth
        )
        self._cleanup_previous(
            previous_mutation_targeting_shape,
            mutation_targeting_shape,
        )

    @staticmethod
    def _cleanup_previous(
            previous: Optional[SpellMutationTargetingAnalysis],
            current: SpellMutationTargetingAnalysis,
    ) -> None:
        """
        Best-effort cleanup for one superseded mutation-targeting section.
        """
        if previous is None or previous is current:
            return
        try:
            previous.cleanup()
        except Exception:
            pass

    @staticmethod
    def _build_target_key(
            *,
            kind: int,
            param_name: str,
    ) -> str:
        """
        Build one normalized target-spec key string.
        """
        if kind is TargetSpecKind.BROADCAST:
            return f"**{param_name}"
        if kind is TargetSpecKind.UNIQUE:
            return f"*{param_name}"
        raise RuntimeError("Unsupported mutation target key kind.")

    @staticmethod
    def _build_patch_ref(
            *,
            root_blueprint,
            node_id: str,
            param_name: str,
            param_path_id: int,
    ) -> SpellMutationPatchRef:
        """
        Build one normalized mutation patch row from rooted blueprint truth.
        """
        old_parent_ids = []
        child_node = root_blueprint.dag.get_node(node_id)
        if child_node is not None:
            for parent_node in list(child_node.dependencies):
                incoming_param = child_node.incoming_params.get(parent_node)
                if incoming_param == param_name:
                    old_parent_ids.append(parent_node.id)

        if len(old_parent_ids) == 1:
            old_parent_id = old_parent_ids[0]
        else:
            old_parent_id = None

        return SpellMutationPatchRef(
            child_spell_id=node_id,
            param_name=param_name,
            param_path_id=param_path_id,
            old_parent_id=old_parent_id,
        )
