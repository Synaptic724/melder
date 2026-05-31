from typing import Any, Dict, List, Optional, Tuple

from melder.aether.spellbook.existence.existence import Existence
from melder.utilities.general_base.cleanable import Cleanable


class SpellCodegenModel(Cleanable):
    """
    Distilled Phase 12 codegen-shape model.

    Purpose:
        Hold only the normalized planning selectors that matter for codegen
        selection. This model is intentionally not a second raw artifact bag.

    Contract:
        - Compiler-owned and stored on `SpellCompilerArtifact` during Phase 12.
        - Built from current compiler artifacts by the processor.
        - Stores only distilled planning selectors and derived shape families.
        - Does not store raw phase artifacts, raw plan objects, raw patch maps,
          spell ids, spell names, or backend-emitter cache payloads.
        - Uses `assessment` as processor scratch/provenance space until real
          processor strategies are added.
        - Uses `applied_strategy_ids` to record the ordered processor
          strategies that contributed to the final model.

    Threading:
        - No internal lock is used here.
        - Intended to be built and consumed inside one compiler pass.

    Lifecycle:
        - Built fresh for one Phase 12 run.
        - Cleared when the owning compiler artifact clears later-phase state.
    """

    __slots__ = Cleanable.__slots__ + [
        "build_kind",
        "existence",
        "route_family",
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
            build_kind: str,
            existence: Optional[Existence],
            route_family: str,
            node_count: int,
            root_dependency_count: int,
            max_depth: int,
            max_width: int,
            shared_node_count: int,
            graph_family: str,
            max_dependency_count: int,
            dependency_arity_histogram: Tuple[Tuple[int, int], ...],
            has_calln: bool,
            contract_payload_count: int,
            call_shape_family: str,
            target_spec_count: int,
            targeted_socket_count: int,
            max_targets_per_spec: int,
            max_target_path_depth: int,
            root_positional_override_relevant: bool,
            override_shape_family: str,
            fast_transient_eligible: bool,
    ) -> None:
        """
        Build one distilled codegen model.

        Args:
            build_kind:
                High-level build mode. Current scaffold values are
                `existing_creation` or `construct`.
            existence:
                Root existence family when construction applies, otherwise
                `None` for existing-creation mode.
            route_family:
                Distilled route/storage family used by later planning.
            node_count:
                Normalized node count for the spell graph.
            root_dependency_count:
                Number of direct dependencies on the root step.
            max_depth:
                Maximum graph/occurrence depth.
            max_width:
                Maximum graph width by depth level.
            shared_node_count:
                Number of shared nodes/spells in the graph.
            graph_family:
                Distilled graph-shape family such as `single`, `flat`, `chain`,
                `shared_dag`, or `complex`.
            max_dependency_count:
                Maximum dependency count across all execution steps.
            dependency_arity_histogram:
                Distilled arity histogram used by call-shape planning.
            has_calln:
                Whether generic `CALLN` behavior is required somewhere.
            contract_payload_count:
                Number of steps carrying contract payloads.
            call_shape_family:
                Distilled call-shape family.
            target_spec_count:
                Count of override target specs.
            targeted_socket_count:
                Count of targeted sockets.
            max_targets_per_spec:
                Maximum fanout count for one target spec.
            max_target_path_depth:
                Maximum target path depth.
            root_positional_override_relevant:
                Whether root positional override shape is relevant.
            override_shape_family:
                Distilled override-geometry family.
            fast_transient_eligible:
                Whether the current artifact set supports the transient fast
                path for later planning.
        """
        super().__init__()
        self.build_kind: str = build_kind
        self.existence: Optional[Existence] = existence
        self.route_family: str = route_family
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
        Deterministically release the Phase 12 codegen model.

        Contract:
            - Idempotent cleanup.
            - Clears the mutable assessment and provenance collections.
            - Drops all distilled selector fields.
        """
        if self._cleaned:
            return

        self._cleaned = True
        self.assessment.clear()
        self.applied_strategy_ids.clear()

        del self.build_kind
        del self.existence
        del self.route_family
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
        Return the stable high-level section labels represented in this model.

        Returns:
            Tuple[str, ...]:
                Immutable section-name row for diagnostics and assertions.
        """
        return (
            "build_shape",
            "route_shape",
            "graph_shape",
            "call_shape",
            "override_shape",
            "fast_path_shape",
            "assessment",
        )
