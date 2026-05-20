from typing import Any, Dict, Optional

from mypy_extensions import mypyc_attr

from melder.aether.spellbook.spell_compiler.spell_compiler_artifact import (
    SpellCompilerArtifact,
)
from melder.aether.spellbook.spell_compiler.phases.shared_compiler_executions import (
    SharedCompilerExecutions,
)
from melder.aether.spellbook.spell_compiler.blueprints.execution_plan import (
    ExecutionPlan,
)
from melder.aether.spellbook.spell_compiler.blueprints.phase12_no_overrides_executor import (
    compile_phase12_no_overrides_executor,
    compile_phase12_no_overrides_executor_from_plan,
)
from melder.utilities.interfaces.ispellbook import ISpellbook
from melder.utilities.interfaces.ispell import ISpell


@mypyc_attr(native_class=True)
class CompilerPhase12:
    """
    Compiler phase 12 surface.

    Purpose:
        Expose the no-overrides executor compilation behavior through a
        compiler-owned phase class.

    Contract:
        - Slot-only phase surface with no explicit `__init__`.
        - Directly ports the canonical `SpellCrafter` phase-12 helper behavior.
        - Consumes artifact-held phase-11/12 handoff state instead of
          recomputing the compile signature/transient schema through phase 11.
        - Does not own spell or artifact lifecycle.
    """

    __slots__ = ()

    def compile_no_overrides_executor(
            self,
            spellbook: ISpellbook,
            spell: ISpell,
            artifact: SpellCompilerArtifact,
    ) -> None:
        """
        Compile and cache the spell-scoped Phase 12 no-overrides executor.

        Purpose:
            Consume exported Phase 11 IR and build the callable artifact used
            by CreationContext no-overrides fast paths.
        Contract:
            - Prefers the artifact-held no-overrides plan handoff when present.
            - Reuses existing executor when IR signature is unchanged.
            - Stores None when no compatible transient IR exists.
            - Never mutates Phase 11 plans.
        Args:
            spellbook:
                Spellbook providing explicit spell lookup context for payload
                compile fallback.
            spell:
                Spell whose phase-12 executor is being materialized.
            artifact:
                Compiler artifact holding phase-11/12 handoff state.
        Returns:
            None.
        """
        plan = artifact._execution_plan_phase11_no_overrides
        if plan is not None:
            self.compile_no_overrides_executor_from_plan(
                spell,
                artifact,
                plan,
            )
            return

        SharedCompilerExecutions.capture_phase8_11_codegen_ir_if_dirty(
            artifact
        )
        if artifact._codegen_ir is None:
            self.compile_no_overrides_executor_from_payload(
                spellbook,
                spell,
                artifact,
                None,
            )
            return

        phase8_11 = artifact._codegen_ir["phase8_11"]
        execution_payload = phase8_11.get("execution")
        if not execution_payload:
            self.compile_no_overrides_executor_from_payload(
                spellbook,
                spell,
                artifact,
                None,
            )
            return

        no_overrides_payload = execution_payload.get("no_overrides")
        self.compile_no_overrides_executor_from_payload(
            spellbook,
            spell,
            artifact,
            no_overrides_payload,
        )

    def compile_no_overrides_executor_from_plan(
            self,
            spell: ISpell,
            artifact: SpellCompilerArtifact,
            plan: Optional[ExecutionPlan],
    ) -> None:
        """
        Compile/cache phase12 no-overrides executor from a Phase11 plan object.

        Purpose:
            Consume the artifact-held phase-11/12 handoff state without
            recomputing the compile signature/transient schema through phase 11.
        Contract:
            - Stores `None` executor/signature when the plan is missing or empty.
            - Reuses existing executor when the artifact-held plan signature is
              unchanged.
            - Raises when compilation fails for a non-empty plan.
        Args:
            plan:
                Phase11 no-overrides execution plan or `None`.
        Returns:
            None.
        """
        if plan is None or not plan.steps:
            artifact._phase12_no_overrides_executor = None
            artifact._phase12_no_overrides_executor_signature = None
            spell.resolution_complete = False
            return

        transient_schema = artifact._phase11_no_overrides_transient_schema
        plan_signature = artifact._phase11_no_overrides_plan_signature
        if plan_signature is None:
            raise RuntimeError(
                "Phase 12 no-overrides compile requires an artifact-held "
                "phase11 plan signature."
            )
        if (
                plan_signature == artifact._phase12_no_overrides_executor_signature
                and artifact._phase12_no_overrides_executor is not None
        ):
            spell.resolution_complete = True
            return

        compiled_executor = compile_phase12_no_overrides_executor_from_plan(
            plan=plan,
            transient_schema=transient_schema,
        )
        if len(plan.steps) > 0 and compiled_executor is None:
            raise RuntimeError(
                "Phase 12 no-overrides executor compilation failed for a non-empty plan."
            )
        artifact._phase12_no_overrides_executor = compiled_executor
        artifact._phase12_no_overrides_executor_signature = plan_signature
        spell.resolution_complete = True

    def compile_no_overrides_executor_from_payload(
            self,
            spellbook: ISpellbook,
            spell: ISpell,
            artifact: SpellCompilerArtifact,
            no_overrides_payload: Optional[Dict[str, Any]],
    ) -> None:
        """
        Compile/cache phase12 no-overrides executor from a payload mapping.

        Purpose:
            Compile from exported phase8-11 payloads when codegen-ir readers
            trigger lazy capture or when payload-only compile paths are used.
            Compile from exported payload without requiring phase 11 plan schema
            capture.
        Contract:
            - Stores `None` executor/signature when payload is missing.
            - Reuses existing executor when the payload signature is unchanged.
            - Raises on malformed payload shape for non-empty plans.
        Args:
            spellbook:
                Spellbook providing explicit spell lookup context for payload
                compilation.
            spell:
                Spell whose phase-12 executor cache is being updated.
            artifact:
                Compiler artifact receiving compiled executor state.
            no_overrides_payload:
                Phase11 no-overrides payload dictionary or `None`.
        Returns:
            None.
        Raises:
            RuntimeError:
                If required payload fields are absent or if payload rows are
                missing while a non-empty compile would be expected.
        """
        if not no_overrides_payload:
            artifact._phase12_no_overrides_executor = None
            artifact._phase12_no_overrides_executor_signature = None
            spell.resolution_complete = False
            return

        required_payload_fields = (
            "signature",
            "step_count",
            "root_spell_id",
        )
        for field_name in required_payload_fields:
            if field_name not in no_overrides_payload:
                raise RuntimeError(
                    "Phase 12 no-overrides IR payload is missing required field "
                    f"'{field_name}'."
                )

        has_steps_rows = "steps_rows" in no_overrides_payload and bool(
            no_overrides_payload.get("steps_rows")
        )
        if not has_steps_rows:
            raise RuntimeError(
                "Phase 12 no-overrides IR payload must provide non-empty "
                "'steps_rows'."
            )

        payload_signature = no_overrides_payload["signature"]
        if (
                payload_signature == artifact._phase12_no_overrides_executor_signature
                and artifact._phase12_no_overrides_executor is not None
        ):
            spell.resolution_complete = True
            return

        compiled_executor = compile_phase12_no_overrides_executor(
            codegen_ir=no_overrides_payload,
            spell_lookup=spellbook._spell_id_pool,
        )
        if no_overrides_payload.get("step_count", 0) > 0 and compiled_executor is None:
            raise RuntimeError(
                "Phase 12 no-overrides executor compilation failed for a non-empty plan."
            )
        artifact._phase12_no_overrides_executor = compiled_executor
        artifact._phase12_no_overrides_executor_signature = payload_signature
        spell.resolution_complete = True
