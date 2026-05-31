from typing import TYPE_CHECKING, Dict, List, Optional, Tuple

from melder.aether.spellbook.spell_compiler.artifact_processor.data.spell_override_targeting_analysis import (
    SpellOverrideTargetRef,
    SpellOverrideTargetingAnalysis,
)
from melder.aether.spellbook.spell_compiler.artifact_processor.spell_artifact_processor_strategy import (
    SpellArtifactProcessorStrategy,
)
from melder.aether.spellbook.spell_compiler.dag.target_spec import (
    TargetSpecKind,
)

if TYPE_CHECKING:
    from melder.aether.spellbook.spell import Spell
    from melder.aether.spellbook.spell_compiler.artifact_processor.spell_codegen_model import (
        SpellCodegenModel,
    )
    from melder.aether.spellbook.spell_compiler.spell_compiler_artifact import (
        SpellCompilerArtifact,
    )


class SpellOverrideTargetingProcessorStrategy(SpellArtifactProcessorStrategy):
    """
    Fit the override-targeting section of `SpellCodegenModel`.

    Purpose:
        Derive normalized override-targeting truth directly from the rooted
        blueprint sockets so the processor does not depend on old Phase 10
        patch-map objects.
    """

    __slots__ = ()

    @property
    def strategy_id(self) -> str:
        """
        Return the stable processor strategy id.
        """
        return "spell_override_targeting_processor"

    def process(
            self,
            spell: "Spell",
            artifact: "SpellCompilerArtifact",
            model: "SpellCodegenModel",
    ) -> None:
        """
        Fit the override-targeting model section.

        Contract:
            - Reads rooted blueprint truth from `artifact._root_blueprint_phase5`.
            - Writes only `model.override_targeting_shape` plus compatible
              top-level override-targeting selectors.
            - Does not read old `OverridePatchMap` objects.
        """
        _ = spell
        root_blueprint = artifact._root_blueprint_phase5
        if root_blueprint is None:
            raise RuntimeError(
                "SpellOverrideTargetingProcessorStrategy requires Phase 5 root blueprint truth."
            )
        root_blueprint.ensure_dag_index_built()

        targets_by_spec: Dict[str, Tuple[SpellOverrideTargetRef, ...]] = {}
        specificity_by_spec: Dict[str, int] = {}
        path_depth_histogram: Dict[int, int] = {}
        by_name: Dict[str, List[SpellOverrideTargetRef]] = {}

        for socket_ref in root_blueprint.socket_refs:
            target_ref = SpellOverrideTargetRef(
                node_id=socket_ref.node_id,
                param_path_id=socket_ref.param_path_id,
                param_name=socket_ref.param_name,
                socket_kind_value=socket_ref.socket_kind.value,
            )
            by_name.setdefault(socket_ref.param_name, []).append(target_ref)

            path_key = root_blueprint.path_registry.format_path(socket_ref.param_path_id)
            targets_by_spec[path_key] = (target_ref,)
            specificity_by_spec[path_key] = 3

            depth = root_blueprint.path_registry.depth(socket_ref.param_path_id)
            path_depth_histogram[depth] = path_depth_histogram.get(depth, 0) + 1

        for param_name, targets in by_name.items():
            broadcast_key = self._build_target_key(
                kind=TargetSpecKind.BROADCAST,
                param_name=param_name,
            )
            unique_key = self._build_target_key(
                kind=TargetSpecKind.UNIQUE,
                param_name=param_name,
            )
            target_tuple = tuple(targets)
            targets_by_spec[broadcast_key] = target_tuple
            targets_by_spec[unique_key] = target_tuple
            specificity_by_spec[broadcast_key] = 1
            specificity_by_spec[unique_key] = 2

        override_targeting_shape = SpellOverrideTargetingAnalysis(
            targets_by_spec=targets_by_spec,
            specificity_by_spec=specificity_by_spec,
            path_depth_histogram=tuple(sorted(path_depth_histogram.items())),
        )
        previous_override_targeting_shape = model.override_targeting_shape
        model.override_targeting_shape = override_targeting_shape
        model.target_spec_count = override_targeting_shape.target_spec_count
        model.targeted_socket_count = override_targeting_shape.targeted_socket_count
        model.targeted_spell_count = override_targeting_shape.targeted_spell_count
        model.max_targets_per_spec = override_targeting_shape.max_targets_per_spec
        model.max_target_path_depth = override_targeting_shape.max_target_path_depth
        model.override_shape_family = self._override_shape_family(
            target_spec_count=override_targeting_shape.target_spec_count,
            max_targets_per_spec=override_targeting_shape.max_targets_per_spec,
            max_target_path_depth=override_targeting_shape.max_target_path_depth,
        )
        self._cleanup_previous(
            previous_override_targeting_shape,
            override_targeting_shape,
        )

    @staticmethod
    def _cleanup_previous(
            previous: Optional[SpellOverrideTargetingAnalysis],
            current: SpellOverrideTargetingAnalysis,
    ) -> None:
        """
        Best-effort cleanup for one superseded override-targeting section.
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
        raise RuntimeError("Unsupported override target key kind.")

    @staticmethod
    def _override_shape_family(
            *,
            target_spec_count: int,
            max_targets_per_spec: int,
            max_target_path_depth: int,
    ) -> str:
        """
        Classify override-targeting geometry into one planner-facing family.
        """
        if target_spec_count <= 0:
            return "none"
        if max_target_path_depth > 1:
            return "deep"
        if max_targets_per_spec <= 1:
            return "simple"
        if max_targets_per_spec > 1:
            return "wide"
        return "complex"
