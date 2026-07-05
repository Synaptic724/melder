"""Component tests for the new compiler object pipeline."""

import sys
from types import ModuleType
from types import SimpleNamespace

_overrides_codegen_compiler_stub = ModuleType(
    "melder.aether.spellbook.spell_compiler.codegen_creation.generalized_overrides_codegen_creation_compiler"
)
_overrides_codegen_compiler_stub.compile_overrides_codegen_creation_executor_code_object = (
    lambda *args, **kwargs: None
)
_overrides_codegen_compiler_stub.compile_overrides_codegen_creation_executor = (
    lambda *args, **kwargs: None
)
_overrides_codegen_compiler_stub._compile_overrides_codegen_creation_executor_from_code_object_with_prefilter_cache = (
    lambda *args, **kwargs: None
)
_overrides_codegen_compiler_stub.build_overrides_codegen_creation_step_target_counts_from_rows = (
    lambda *args, **kwargs: ()
)
_overrides_codegen_compiler_stub.emit_overrides_codegen_creation_executor_shape_source = (
    lambda *args, **kwargs: ""
)
sys.modules.setdefault(
    "melder.aether.spellbook.spell_compiler.codegen_creation.generalized_overrides_codegen_creation_compiler",
    _overrides_codegen_compiler_stub,
)

from melder.aether.spellbook.configuration.system_state import SystemState
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spell_compiler.artifact_processor.spell_artifact_processor import (
    SpellArtifactProcessor,
)
from melder.aether.spellbook.spell_compiler.codegen_planner.spell_codegen_planner import (
    SpellCodegenPlanner,
)
from melder.aether.spellbook.spell_compiler.spell_analyzer.data.spell_occurrence_graph_analysis import (
    SpellOccurrenceGraphAnalysis,
)
from melder.aether.spellbook.spell_compiler.spell_compiler_artifact import (
    SpellCompilerArtifact,
)


class _PathRegistryProbe:
    """Minimal path-registry double for the component pipeline slice."""

    def __init__(self) -> None:
        """Expose the root path id used by the processor strategies."""
        self.root_path_id = 0

    def depth(self, path_id: int) -> int:
        """Return a deterministic depth for the supplied path."""
        _ = path_id
        return 0

    def format_path(self, path_id: int) -> str:
        """Return one deterministic formatted path."""
        return "path:{0}".format(path_id)

    def extend_path(self, path_id: int, param_name: str) -> int:
        """Return a deterministic child path id."""
        _ = param_name
        return path_id + 1


class _DagProbe:
    """Minimal DAG double used by override and mutation strategies."""

    def get_node(self, node_id: str):
        """Return no node so mutation-parent lookup stays empty."""
        _ = node_id
        return None


def test_component_processor_and_planner_build_real_codegen_outputs() -> None:
    """The real processor and planner should cooperate over one minimal compiler artifact slice."""
    artifact = SpellCompilerArtifact("root")
    artifact._spell_codegen_model = None
    artifact._spell_codegen_plan = None
    artifact._requirements = SimpleNamespace(parameters=())
    path_registry = _PathRegistryProbe()
    artifact._root_blueprint_phase5 = SimpleNamespace(
        root_spell_id="root",
        ordered_node_ids=("root",),
        socket_refs=(),
        path_registry=path_registry,
        dag=_DagProbe(),
        ensure_dag_index_built=lambda: None,
    )
    artifact._occurrence_graph_analysis = SpellOccurrenceGraphAnalysis(
        root_spell_id="root",
        occurrence_graph={
            ("root", 0): {},
        },
        path_registry=path_registry,
        occurrence_count=1,
        edge_count=0,
        topology_dependency_count=0,
        dag_fallback_dependency_count=0,
        shared_collapse_enabled=True,
    )

    spellbook = SimpleNamespace(
        _spell_id_pool={},
        _lookup_contracted_spells={},
        _contracted_spells={},
        _aetheric_frame_configuration=SimpleNamespace(system_state=SystemState.dynamic),
        # The injection processor reads collection-socket truth from the
        # durable phase-3 topology registry; None is the documented
        # missing-topology path (no collection params inferred).
        _spell_system_states=SimpleNamespace(
            get_local_topology_by_id=lambda spell_id: None,
        ),
    )

    def _root_target() -> str:
        """Return a deterministic runtime value for the component slice."""
        return "root-value"

    spell = SimpleNamespace(
        spell_id="root",
        spell_name="root",
        spell_index=SimpleNamespace(selected_spell_id="root"),
        spell=_root_target,
        requirements=SimpleNamespace(parameters=()),
        existence=Existence.unique_per_conduit,
        is_existing_creation=False,
        is_class_spell=False,
        is_method_spell=False,
        is_lambda_spell=True,
        has_disposal_methods=False,
        disposal_method_names=(),
        user_created_object=None,
        _spellbook=spellbook,
        _compiler_artifact=artifact,
    )
    spellbook._spell_id_pool["root"] = spell

    SpellArtifactProcessor().process(spell, artifact)
    SpellCodegenPlanner().build(artifact)

    model = artifact._spell_codegen_model
    plan = artifact._spell_codegen_plan

    assert model is not None
    assert plan is not None
    assert model.order_shape.execution_order == ["root"]
    assert model.instance_shape.root_instance_key == ("root", None)
    assert model.contract_shape.contract_payload_count == 0
    assert model.injection_shape.instance_spec_count == 1
    assert model.spell_runtime_shape.spell_count == 1
    assert plan.processor_strategy_ids == model.snapshot_applied_strategy_ids()
    assert plan.plan_strategy_ids == ("generalized_codegen_plan",)
    assert plan.metadata["selected_strategy_id"] == "generalized_codegen_plan"
    assert plan.no_overrides_plan is not None
    assert plan.overrides_plan is not None

