from typing import Any, Optional

from melder.aether.spellbook.spell_compiler.codegen_creation_system.codegen_creation.spell_codegen_creation import (
    SpellCodegenCreation,
)
from melder.aether.spellbook.spell_compiler.codegen_creation_system.spell_codegen_strategy import (
    SpellCodegenStrategy,
)
from melder.aether.spellbook.spell_compiler.codegen_planner.data.spell_generalized_codegen_lane_plan import (
    SpellGeneralizedCodegenLanePlan,
)
from melder.aether.spellbook.spell_compiler.codegen_planner.spell_codegen_plan import (
    SpellCodegenPlan,
)
from melder.aether.spellbook.spell_compiler.phases.shared_compiler_executions import (
    SharedCompilerExecutions,
)
from melder.aether.spellbook.spell_compiler.artifact_processor.spell_codegen_model import (
    SpellCodegenModel,
)
from melder.aether.spellbook.spell_compiler.codegen_creation_system.generalized_no_overrides_codegen_creation_compiler import (
    compile_no_overrides_codegen_creation_executor_from_plan,
)


class SpellGeneralizedNoOverridesCodegenCreationStrategy(
    SpellCodegenStrategy
):
    """
    Generalized no-overrides codegen creation strategy.

    Purpose:
        Port the current compiler-owned no-overrides codegen packaging into
        the codegen-creation layer by consuming the generalized no-overrides
        lane plan directly.
    """

    __slots__ = ()

    @property
    def strategy_id(self) -> str:
        """
        Return the stable no-overrides creation strategy id.
        """
        return "generalized_no_overrides_codegen_creation"

    def apply(
            self,
            spell_codegen_model: SpellCodegenModel,
            spell_codegen_plan: SpellCodegenPlan,
            spell_codegen_creation: SpellCodegenCreation,
    ) -> None:
        """
        Populate the no-overrides creation payload from the lane plan.

        Contract:
            - Requires the planner to have already produced a
              no-overrides lane plan.
            - Compiles the runtime callable from the generalized lane plan
              directly, without lifting a legacy execution-plan object.
            - Stores deterministic executor-signature provenance beside the
              compiled callable.
        """
        _ = spell_codegen_model

        no_overrides_plan = spell_codegen_plan.no_overrides_plan
        if no_overrides_plan is None:
            raise RuntimeError(
                "No-overrides codegen creation requires a no_overrides_plan."
            )

        transient_schema = SharedCompilerExecutions.build_fast_transient_schema(
            no_overrides_plan.fast_transient_plan,
        )
        compiled_executor = compile_no_overrides_codegen_creation_executor_from_plan(
            plan=no_overrides_plan,
            transient_schema=transient_schema,
        )
        executor_signature = self._build_executor_signature(
            no_overrides_plan,
            transient_schema,
        )

        spell_codegen_creation.no_overrides_executor = compiled_executor
        spell_codegen_creation.no_overrides_executor_signature = (
            executor_signature
        )
        spell_codegen_creation.metadata["no_overrides_lane_id"] = (
            no_overrides_plan.lane_id
        )
        spell_codegen_creation.metadata["no_overrides_root_spell_id"] = (
            no_overrides_plan.root_spell_id
        )
        spell_codegen_creation.metadata["no_overrides_step_count"] = (
            len(no_overrides_plan.steps)
        )
        spell_codegen_creation.metadata["no_overrides_fast_transient_available"] = (
            no_overrides_plan.fast_transient_plan is not None
        )

    @staticmethod
    def _build_executor_signature(
            no_overrides_plan: SpellGeneralizedCodegenLanePlan,
            transient_schema: Optional[dict[str, Any]],
    ) -> str:
        """
        Build the deterministic no-overrides executor signature.

        Contract:
            - Mirrors the old no-overrides executor signature semantics.
            - Uses only lane-plan and transient-schema truth.
        """
        step_signature_rows = tuple(
            SharedCompilerExecutions.build_no_overrides_codegen_creation_step_signature_row(
                step
            )
            for step in no_overrides_plan.steps
        )
        transient_signature = (
            SharedCompilerExecutions.build_fast_transient_signature(
                transient_schema
            )
        )
        root_instance_key = SharedCompilerExecutions.normalize_instance_key(
            no_overrides_plan.root_instance_key
        )
        return SharedCompilerExecutions.hash_codegen_signature(
            no_overrides_plan.root_spell_id,
            root_instance_key,
            step_signature_rows,
            transient_signature,
        )
