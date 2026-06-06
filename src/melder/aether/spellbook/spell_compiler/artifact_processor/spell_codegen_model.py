from typing import TYPE_CHECKING, Any, Dict, List, Optional, Tuple

from melder.aether.spellbook.existence.existence import Existence
from melder.utilities.general_base.cleanable import Cleanable

if TYPE_CHECKING:
    from melder.aether.spellbook.spell_compiler.artifact_processor.data.spell_injection_analysis import (
        SpellInjectionAnalysis,
    )
    from melder.aether.spellbook.spell_compiler.artifact_processor.data.spell_occurrence_contract_analysis import (
        SpellOccurrenceContractAnalysis,
    )
    from melder.aether.spellbook.spell_compiler.artifact_processor.data.spell_occurrence_instance_analysis import (
        SpellOccurrenceInstanceAnalysis,
    )
    from melder.aether.spellbook.spell_compiler.artifact_processor.data.spell_occurrence_order_analysis import (
        SpellOccurrenceOrderAnalysis,
    )
    from melder.aether.spellbook.spell_compiler.artifact_processor.data.spell_override_targeting_analysis import (
        SpellOverrideTargetingAnalysis,
    )
    from melder.aether.spellbook.spell_compiler.artifact_processor.data.spell_runtime_analysis import (
        SpellRuntimeAnalysis,
    )
    from melder.aether.spellbook.spell_compiler.spell_analyzer.data.spell_occurrence_graph_analysis import (
        SpellOccurrenceGraphAnalysis,
    )


class SpellCodegenModel(Cleanable):
    """
    Processor-owned codegen model for one spell.

    Purpose:
        Hold the fitted processor output that later planner strategies should
        consume. The model is section-first: it stores the real occurrence-
        derived shapes directly instead of forcing the processor facade to
        reinterpret old phase artifacts into an adapter bag.

    Contract:
        - `graph_shape` is analyzer-owned truth borrowed into the model shell.
        - `order_shape`, `instance_shape`, and `contract_shape` are processor-
          owned sections populated by processor strategies.
        - Top-level scalar fields are compatibility selectors only. They should
          be populated by the shell builder or the strategies that genuinely own
          the corresponding facts.
        - The processor facade must not recompute strategy-family decisions
          after strategies run.
    """

    __slots__ = Cleanable.__slots__ + [
        "build_kind",
        "existence",
        "route_family",
        "graph_shape",
        "order_shape",
        "instance_shape",
        "contract_shape",
        "injection_shape",
        "override_targeting_shape",
        "spell_runtime_shape",
        "node_count",
        "root_dependency_count",
        "max_depth",
        "max_width",
        "shared_node_count",
        "graph_family",
        "max_dependency_count",
        "dependency_arity_histogram",
        "has_calln",
        "contract_payload_count",
        "call_shape_family",
        "target_spec_count",
        "targeted_socket_count",
        "targeted_spell_count",
        "max_targets_per_spec",
        "max_target_path_depth",
        "root_positional_override_relevant",
        "override_shape_family",
        "fast_transient_eligible",
        "assessment",
        "applied_strategy_ids",
    ]

    def __init__(
            self,
            *,
            build_kind: str = "unknown",
            existence: Optional[Existence] = None,
            route_family: str = "unknown",
            graph_shape: Optional[SpellOccurrenceGraphAnalysis] = None,
            order_shape: Optional[SpellOccurrenceOrderAnalysis] = None,
            instance_shape: Optional[SpellOccurrenceInstanceAnalysis] = None,
            contract_shape: Optional[SpellOccurrenceContractAnalysis] = None,
            injection_shape: Optional[SpellInjectionAnalysis] = None,
            override_targeting_shape: Optional[SpellOverrideTargetingAnalysis] = None,
            spell_runtime_shape: Optional[SpellRuntimeAnalysis] = None,
            node_count: int = 0,
            root_dependency_count: int = 0,
            max_depth: int = 0,
            max_width: int = 0,
            shared_node_count: int = 0,
            graph_family: str = "unclassified",
            max_dependency_count: int = 0,
            dependency_arity_histogram: Tuple[Tuple[int, int], ...] = (),
            has_calln: bool = False,
            contract_payload_count: int = 0,
            call_shape_family: str = "unclassified",
            target_spec_count: int = 0,
            targeted_socket_count: int = 0,
            targeted_spell_count: int = 0,
            max_targets_per_spec: int = 0,
            max_target_path_depth: int = 0,
            root_positional_override_relevant: bool = False,
            override_shape_family: str = "unclassified",
            fast_transient_eligible: bool = False,
    ) -> None:
        """
        Build one processor-owned codegen model shell.

        Purpose:
            Give the processor one mutable model surface that starts with raw
            section homes and a minimal set of compatibility selectors, then let
            processor strategies fit the rest directly.

        Contract:
            - All 4 section homes are explicit on construction.
            - `graph_shape` may be borrowed from analyzer-owned artifact truth.
            - `order_shape`, `instance_shape`, `contract_shape`,
              `injection_shape`, `override_targeting_shape`, and
              `spell_runtime_shape` are
              expected to be filled by processor strategies later in the same
              processor pass.
            - Mutable `assessment` and `applied_strategy_ids` are always
              initialized empty.
        """
        super().__init__()
        self.build_kind: str = build_kind
        self.existence: Optional[Existence] = existence
        self.route_family: str = route_family
        self.graph_shape: Optional[SpellOccurrenceGraphAnalysis] = graph_shape
        self.order_shape: Optional[SpellOccurrenceOrderAnalysis] = order_shape
        self.instance_shape: Optional[SpellOccurrenceInstanceAnalysis] = (
            instance_shape
        )
        self.contract_shape: Optional[SpellOccurrenceContractAnalysis] = (
            contract_shape
        )
        self.injection_shape: Optional[SpellInjectionAnalysis] = injection_shape
        self.override_targeting_shape: Optional[SpellOverrideTargetingAnalysis] = (
            override_targeting_shape
        )
        self.spell_runtime_shape: Optional[SpellRuntimeAnalysis] = (
            spell_runtime_shape
        )
        self.node_count: int = node_count
        self.root_dependency_count: int = root_dependency_count
        self.max_depth: int = max_depth
        self.max_width: int = max_width
        self.shared_node_count: int = shared_node_count
        self.graph_family: str = graph_family
        self.max_dependency_count: int = max_dependency_count
        self.dependency_arity_histogram: Tuple[Tuple[int, int], ...] = (
            dependency_arity_histogram
        )
        self.has_calln: bool = has_calln
        self.contract_payload_count: int = contract_payload_count
        self.call_shape_family: str = call_shape_family
        self.target_spec_count: int = target_spec_count
        self.targeted_socket_count: int = targeted_socket_count
        self.targeted_spell_count: int = targeted_spell_count
        self.max_targets_per_spec: int = max_targets_per_spec
        self.max_target_path_depth: int = max_target_path_depth
        self.root_positional_override_relevant: bool = (
            root_positional_override_relevant
        )
        self.override_shape_family: str = override_shape_family
        self.fast_transient_eligible: bool = fast_transient_eligible
        self.assessment: Dict[str, Any] = {}
        self.applied_strategy_ids: List[str] = []

    def cleanup(self) -> None:
        """
        Deterministically release model-owned state.

        Contract:
            - Idempotent cleanup.
            - Does not cleanup borrowed analyzer-owned `graph_shape`.
            - Best-effort cleans processor-owned `order_shape`,
              `instance_shape`, `contract_shape`, `injection_shape`,
              `override_targeting_shape`, and
              `spell_runtime_shape`.
            - Clears mutable assessment/provenance containers.
        """
        if self._cleaned:
            return

        self._cleaned = True
        if self.order_shape is not None:
            try:
                self.order_shape.cleanup()
            except Exception:
                pass
        if self.instance_shape is not None:
            try:
                self.instance_shape.cleanup()
            except Exception:
                pass
        if self.contract_shape is not None:
            try:
                self.contract_shape.cleanup()
            except Exception:
                pass
        if self.injection_shape is not None:
            try:
                self.injection_shape.cleanup()
            except Exception:
                pass
        if self.override_targeting_shape is not None:
            try:
                self.override_targeting_shape.cleanup()
            except Exception:
                pass
        if self.spell_runtime_shape is not None:
            try:
                self.spell_runtime_shape.cleanup()
            except Exception:
                pass
        self.assessment.clear()
        self.applied_strategy_ids.clear()

        del self.build_kind
        del self.existence
        del self.route_family
        del self.graph_shape
        del self.order_shape
        del self.instance_shape
        del self.contract_shape
        del self.injection_shape
        del self.override_targeting_shape
        del self.spell_runtime_shape
        del self.node_count
        del self.root_dependency_count
        del self.max_depth
        del self.max_width
        del self.shared_node_count
        del self.graph_family
        del self.max_dependency_count
        del self.dependency_arity_histogram
        del self.has_calln
        del self.contract_payload_count
        del self.call_shape_family
        del self.target_spec_count
        del self.targeted_socket_count
        del self.targeted_spell_count
        del self.max_targets_per_spec
        del self.max_target_path_depth
        del self.root_positional_override_relevant
        del self.override_shape_family
        del self.fast_transient_eligible
        del self.assessment
        del self.applied_strategy_ids

    def snapshot_applied_strategy_ids(self) -> Tuple[str, ...]:
        """
        Return the applied processor strategy ids as an immutable row.

        Returns:
            Tuple[str, ...]:
                Ordered processor strategy identifiers recorded so far.
        """
        return tuple(self.applied_strategy_ids)

    def section_names(self) -> Tuple[str, ...]:
        """
        Return the stable section labels represented in this model.

        Returns:
            Tuple[str, ...]:
                Immutable section-name row for diagnostics and assertions.
        """
        return (
            "graph_shape",
            "order_shape",
            "instance_shape",
            "contract_shape",
            "injection_shape",
            "override_targeting_shape",
            "spell_runtime_shape",
            "assessment",
        )
