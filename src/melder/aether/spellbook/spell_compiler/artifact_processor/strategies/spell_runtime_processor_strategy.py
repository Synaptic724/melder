from typing import TYPE_CHECKING, Optional

from melder.aether.spellbook.spell_compiler.artifact_processor.data.spell_runtime_analysis import (
    SpellRuntimeAnalysis,
    SpellRuntimeRecord,
)
from melder.aether.spellbook.spell_compiler.artifact_processor.spell_artifact_processor_strategy import (
    SpellArtifactProcessorStrategy,
)

if TYPE_CHECKING:
    from melder.aether.spellbook.spell import Spell
    from melder.aether.spellbook.spell_compiler.artifact_processor.spell_codegen_model import (
        SpellCodegenModel,
    )
    from melder.aether.spellbook.spell_compiler.spell_compiler_artifact import (
        SpellCompilerArtifact,
    )


class SpellRuntimeProcessorStrategy(SpellArtifactProcessorStrategy):
    """
    Fit the runtime spell section of `SpellCodegenModel`.

    Purpose:
        Capture the static spell facts the planner needs to build execution lane
        payloads without reopening the live spellbook pool directly.
    """

    __slots__ = ()

    @property
    def strategy_id(self) -> str:
        """
        Return the stable processor strategy id.
        """
        return "spell_runtime_processor"

    def process(
            self,
            spell: "Spell",
            artifact: "SpellCompilerArtifact",
            model: "SpellCodegenModel",
    ) -> None:
        """
        Fit the runtime spell model section.

        Contract:
            - Uses execution order when present to scope the records.
            - Falls back to graph-visible spell ids when no order section exists.
            - Writes only `model.spell_runtime_shape`.
            - Borrows each Spell's resolved disposal list without conversion;
              binding has already established its order and presence flag.
        """
        _ = artifact
        spellbook = spell._spellbook
        if spellbook is None:
            raise RuntimeError(
                "SpellRuntimeProcessorStrategy requires a live owning Spellbook."
            )

        ordered_spell_ids = None
        if model.order_shape is not None:
            ordered_spell_ids = model.order_shape.execution_order
        elif model.graph_shape is not None:
            ordered_spell_ids = []
            for occurrence in model.graph_shape.occurrence_graph.keys():
                spell_id = occurrence[0]
                if spell_id not in ordered_spell_ids:
                    ordered_spell_ids.append(spell_id)
        else:
            raise RuntimeError(
                "SpellRuntimeProcessorStrategy requires graph or order truth first."
            )

        records_by_spell_id = {}
        for spell_id in ordered_spell_ids:
            spell_obj = spellbook._spell_id_pool.get(spell_id)
            if spell_obj is None:
                raise RuntimeError(
                    f"SpellRuntimeProcessorStrategy could not resolve spell_id '{spell_id}'."
                )
            records_by_spell_id[spell_id] = SpellRuntimeRecord(
                spell_id=spell_id,
                spell_name=spell_obj.spell_name,
                spell=spell_obj,
                call_target=spell_obj.spell,
                existence=spell_obj.existence,
                is_existing_creation=spell_obj.is_existing_creation,
                is_class_spell=spell_obj.is_class_spell,
                is_method_spell=spell_obj.is_method_spell,
                is_lambda_spell=spell_obj.is_lambda_spell,
                has_disposal_methods=spell_obj.has_disposal_methods,
                disposal_method_names=spell_obj.disposal_method_names,
                user_created_object=spell_obj.user_created_object,
            )

        runtime_shape = SpellRuntimeAnalysis(
            records_by_spell_id=records_by_spell_id,
        )
        previous_runtime_shape = model.spell_runtime_shape
        model.spell_runtime_shape = runtime_shape
        self._cleanup_previous(previous_runtime_shape, runtime_shape)

    @staticmethod
    def _cleanup_previous(
            previous: Optional[SpellRuntimeAnalysis],
            current: SpellRuntimeAnalysis,
    ) -> None:
        """
        Best-effort cleanup for one superseded runtime spell section.
        """
        if previous is None or previous is current:
            return
        try:
            previous.cleanup()
        except Exception:
            pass
