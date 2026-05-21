"""Unit tests for current shared compiler execution helper exports."""

import pickle
from types import SimpleNamespace
from typing import Any

import pytest

from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spell_compiler.phases.shared_compiler_executions import (
    SharedCompilerExecutions,
)
from melder.aether.spellbook.spell_compiler.spell_compiler_artifact import (
    SpellCompilerArtifact,
)
from melder.aether.spellbook.spell_compiler.spell_requirements_finder.parameter_di_shape import (
    ParameterDIShape,
)
from melder.aether.spellbook.spell_types.spell_types import SpellType


def _make_spell_stub(spell_id: str) -> Any:
    """Build a minimal spell stub for shared IR export tests."""
    return SimpleNamespace(
        spell_id=spell_id,
        spell_index=SimpleNamespace(current=spell_id),
        dependencies=[],
        user_created_object=None,
        existence=Existence.unique,
        is_existing_creation=False,
        spell_type=SpellType.SPELL,
        has_disposal_methods=False,
        disposal_method_names=(),
        resolution_complete=False,
    )


def _make_dependency(
        *,
        param_name: str,
        position: int,
        di_shape: ParameterDIShape,
        is_optional: bool = False,
        is_collection: bool = False,
        contract_key: Any = None,
        contract_late_binding: Any = None,
) -> Any:
    """Build a minimal symbolic dependency stub."""
    return SimpleNamespace(
        param_name=param_name,
        position=position,
        di_shape=di_shape,
        is_optional=is_optional,
        is_collection=is_collection,
        contract_key=contract_key,
        contract_late_binding=contract_late_binding,
    )


def _make_phase11_plan_stub(
        *,
        plan_variant: Any,
        root_spell_id: str,
        step_spell_ids: tuple[str, ...],
) -> Any:
    """Build a minimal execution-plan stub for shared IR export tests."""
    steps = []
    for spell_id in step_spell_ids:
        steps.append(
            SimpleNamespace(
                instance_key=(spell_id, None),
                spell=_make_spell_stub(spell_id),
                existence=Existence.unique,
                creations_target_kind="owned",
                shared_instance=False,
                dependency_resolution_order=(("dep", ((f"{spell_id}-dep", None),)),),
                override_match_prefix=None,
                override_match_prefix_len=0,
                override_keys=(),
                expects_overrides=False,
                contract_keys=(),
                allow_list_aggregation=False,
                uses_positional_override=False,
                contract_positional_override=None,
                has_contract_payload=False,
                contract_payload=None,
                lock_hint="none",
                use_spell_lock_hint=False,
                requires_spellspace=False,
                owner_conduit_required=False,
                must_register=False,
                disposal_method_names=(),
            )
        )

    return SimpleNamespace(
        plan_variant=plan_variant,
        root_spell_id=root_spell_id,
        steps=steps,
        fast_transient_plan=None,
        root_instance_key=(root_spell_id, None),
        spell_id_step_index={
            step.spell.spell_index.current: index
            for index, step in enumerate(steps)
        },
        optimistic_object_refs_by_spell_id={},
        available_param_by_spell_id={},
    )


def test_capture_phase2_5_codegen_ir_exports_required_fields() -> None:
    """Phase 2-5 IR export should include the required normalized payload fields."""
    artifact = SpellCompilerArtifact("root")
    spell = _make_spell_stub("root")
    dependencies = (
        _make_dependency(
            param_name="alpha",
            position=0,
            di_shape=ParameterDIShape.SINGLE_BY_ANNOTATION,
            is_optional=False,
        ),
        _make_dependency(
            param_name="beta",
            position=1,
            di_shape=ParameterDIShape.SPELL_CONTRACT,
            is_optional=True,
        ),
    )
    artifact._symbolic_graph = SimpleNamespace(dependencies=dependencies)
    artifact._resolution_frame = SimpleNamespace(
        ordered_node_ids=("dep", "root"),
    )
    spell.dependencies = ["dep-b", "dep-a"]
    artifact._validated_phase4 = True
    artifact._is_broken = False
    artifact._validation_result_phase4 = SimpleNamespace(
        issues=(
            SimpleNamespace(code="I-B"),
            SimpleNamespace(code="I-A"),
        ),
    )
    root_blueprint = SimpleNamespace(
        root_spell_id="root",
        root_lineage_id="lineage-root",
        ordered_node_ids=["dep", "root"],
        socket_refs=[
            SimpleNamespace(
                node_id="dep",
                param_name="beta",
                param_path_id=7,
                socket_kind=SimpleNamespace(value="spell_contract"),
            ),
            SimpleNamespace(
                node_id="dep",
                param_name="alpha",
                param_path_id=2,
                socket_kind=SimpleNamespace(value="normal"),
            ),
        ],
    )

    class _Node:
        def __init__(self, node_id: str) -> None:
            self.id = node_id
            self.dependents: set[Any] = set()
            self.incoming_params: dict[Any, str] = {}

    parent_a = _Node("dep-a")
    parent_b = _Node("dep-b")
    child_root = _Node("root")
    parent_a.dependents.add(child_root)
    parent_b.dependents.add(child_root)
    child_root.incoming_params[parent_a] = "alpha"
    child_root.incoming_params[parent_b] = "beta"
    root_blueprint.dag = SimpleNamespace(
        nodes={
            "dep-b": parent_b,
            "dep-a": parent_a,
            "root": child_root,
        },
        _socket_kinds={
            (parent_b, child_root): SimpleNamespace(value="spell_contract"),
            (parent_a, child_root): SimpleNamespace(value="normal"),
        },
    )
    artifact._root_blueprint_phase5 = root_blueprint
    artifact._spell_system_index_phase5 = SimpleNamespace(
        nodes={"z": object(), "a": object()},
    )

    SharedCompilerExecutions.capture_phase2_5_codegen_ir(spell, artifact)
    payload = artifact._codegen_ir["phase2_5"]
    signatures = artifact._codegen_ir["signatures"]
    first_signature = payload["signature"]

    assert set(payload.keys()) == {
        "symbolic_dependencies",
        "local_ordered_node_ids",
        "dependency_ids",
        "phase4_validated",
        "phase4_is_broken",
        "phase4_issue_codes",
        "phase5_root_spell_id",
        "phase5_root_lineage_id",
        "phase5_root_ordered_node_ids",
        "phase5_socket_ref_count",
        "phase5_socket_rows",
        "phase5_dag_edge_rows",
        "phase5_index_spell_ids",
        "signature",
    }
    assert payload["phase5_index_spell_ids"] == ("a", "z")
    assert payload["phase5_root_spell_id"] == "root"
    assert payload["phase5_root_lineage_id"] == "lineage-root"
    assert payload["phase5_socket_ref_count"] == 2
    assert payload["phase5_socket_rows"] == (
        ("dep", "alpha", 2, "normal"),
        ("dep", "beta", 7, "spell_contract"),
    )
    assert payload["phase5_dag_edge_rows"] == (
        ("dep-a", "root", "alpha", "normal"),
        ("dep-b", "root", "beta", "spell_contract"),
    )
    assert signatures["phase2_5"] == first_signature

    SharedCompilerExecutions.capture_phase2_5_codegen_ir(spell, artifact)
    assert artifact._codegen_ir["phase2_5"]["signature"] == first_signature


def test_capture_phase2_5_codegen_ir_signature_changes_on_phase5_schema_rows() -> None:
    """Phase 2-5 IR signature should change when Phase 5 schema rows change."""
    artifact = SpellCompilerArtifact("root")

    class _Node:
        def __init__(self, node_id: str) -> None:
            self.id = node_id
            self.dependents: set[Any] = set()
            self.incoming_params: dict[Any, str] = {}

    root_blueprint = SimpleNamespace(
        root_spell_id="root",
        root_lineage_id="lineage-root",
        ordered_node_ids=["dep-a", "root"],
        socket_refs=[
            SimpleNamespace(
                node_id="dep-a",
                param_name="alpha",
                param_path_id=1,
                socket_kind=SimpleNamespace(value="normal"),
            ),
        ],
    )
    parent_a = _Node("dep-a")
    child_root = _Node("root")
    parent_a.dependents.add(child_root)
    child_root.incoming_params[parent_a] = "alpha"
    root_blueprint.dag = SimpleNamespace(
        nodes={
            "dep-a": parent_a,
            "root": child_root,
        },
        _socket_kinds={
            (parent_a, child_root): SimpleNamespace(value="normal"),
        },
    )
    artifact._root_blueprint_phase5 = root_blueprint
    SharedCompilerExecutions.capture_phase2_5_codegen_ir(_make_spell_stub("root"), artifact)
    first_signature = artifact._codegen_ir["phase2_5"]["signature"]

    changed_blueprint = SimpleNamespace(
        root_spell_id="root",
        root_lineage_id="lineage-root",
        ordered_node_ids=["dep-a", "root"],
        socket_refs=[
            SimpleNamespace(
                node_id="dep-a",
                param_name="alpha",
                param_path_id=9,
                socket_kind=SimpleNamespace(value="normal"),
            ),
        ],
    )
    changed_parent = _Node("dep-a")
    changed_child = _Node("root")
    changed_parent.dependents.add(changed_child)
    changed_child.incoming_params[changed_parent] = "alpha_changed"
    changed_blueprint.dag = SimpleNamespace(
        nodes={
            "dep-a": changed_parent,
            "root": changed_child,
        },
        _socket_kinds={
            (changed_parent, changed_child): SimpleNamespace(value="normal"),
        },
    )
    artifact._root_blueprint_phase5 = changed_blueprint
    SharedCompilerExecutions.capture_phase2_5_codegen_ir(_make_spell_stub("root"), artifact)
    second_signature = artifact._codegen_ir["phase2_5"]["signature"]

    assert second_signature != first_signature


def test_capture_phase8_11_codegen_ir_exports_sorted_payloads() -> None:
    """Phase 8-11 IR export should normalize sorted occurrence/injection/patch payloads."""
    artifact = SpellCompilerArtifact("root")
    artifact._occurrence_plan_phase8 = SimpleNamespace(
        execution_order=("step-b", "step-a"),
        root_instance_key=("root", None),
        shared_spell_ids={"z", "a"},
        contract_dependencies_complete=True,
        occurrence_graph={
            ("root", 0): {
                "alpha": [("a", 1), ("b", 2)],
                "beta": [("a", 1)],
            },
            ("a", 1): {},
            ("b", 2): {},
        },
        instance_keys_by_spell_id={
            "root": [("root", None)],
            "a": [("a", 3), ("a", 1)],
        },
        canonical_occurrences_by_spell_id={
            "root": ("root", 0),
            "a": ("a", 1),
        },
        contract_overrides_by_occurrence={
            ("a", 1): {"x": 7, "__args__": [1, 2]},
        },
        contract_overrides_by_spell_id={
            "a": [(("a", 1), {"x": 7, "__args__": [1, 2]})],
        },
    )
    socket_ref_a = SimpleNamespace(
        node_id="dep-a",
        param_name="arg",
        param_path_id=3,
        socket_kind=SimpleNamespace(value="normal"),
    )
    socket_ref_b = SimpleNamespace(
        node_id="dep-b",
        param_name="arg",
        param_path_id=1,
        socket_kind=SimpleNamespace(value="normal"),
    )
    mutation_patch_a = SimpleNamespace(
        child_spell_id="child-a",
        param_name="mut",
        param_path_id=2,
        old_parent_id="old-a",
    )
    mutation_patch_b = SimpleNamespace(
        child_spell_id="child-b",
        param_name="mut",
        param_path_id=5,
        old_parent_id="old-b",
    )
    artifact._injection_plan_phase9 = SimpleNamespace(
        instance_injections={
            ("z", 3): SimpleNamespace(
                allow_list_aggregation=False,
                uses_positional_override=False,
                contract_payload=None,
                param_sources={},
            ),
            ("a", 2): SimpleNamespace(
                allow_list_aggregation=True,
                uses_positional_override=True,
                contract_payload={"fixed": "ok", "__args__": [9]},
                param_sources={
                    "dep": SimpleNamespace(
                        kind="dependency",
                        dependency_keys=[("z", 3), ("a", None)],
                        override_key="dep",
                        contract_key=None,
                    ),
                    "contracted": SimpleNamespace(
                        kind="contract",
                        dependency_keys=[],
                        override_key="contracted",
                        contract_key="ckey",
                    ),
                },
            ),
            ("a", None): SimpleNamespace(
                allow_list_aggregation=False,
                uses_positional_override=False,
                contract_payload=None,
                param_sources={},
            ),
        },
    )
    artifact._override_patch_map_phase10 = SimpleNamespace(
        targets_by_spec={
            "override-z": [socket_ref_a],
            "override-a": [socket_ref_a, socket_ref_b],
        },
        specificity_by_spec={"override-z": 1, "override-a": 3},
    )
    artifact._mutation_patch_map_phase10 = SimpleNamespace(
        targets_by_spec={
            "mutation-z": [mutation_patch_b],
            "mutation-a": [mutation_patch_b, mutation_patch_a],
        },
    )
    artifact._execution_plan_phase11_no_overrides = _make_phase11_plan_stub(
        plan_variant="no_overrides_fast",
        root_spell_id="root",
        step_spell_ids=("a", "b"),
    )
    artifact._execution_plan_phase11_overrides = _make_phase11_plan_stub(
        plan_variant="overrides",
        root_spell_id="root",
        step_spell_ids=("a",),
    )
    artifact._execution_plan_phase11 = _make_phase11_plan_stub(
        plan_variant="overrides_with_mutations",
        root_spell_id="root",
        step_spell_ids=("a", "b", "c"),
    )

    SharedCompilerExecutions.capture_phase8_11_codegen_ir(artifact)
    payload = artifact._codegen_ir["phase8_11"]
    signatures = artifact._codegen_ir["signatures"]

    assert payload["occurrence"]["shared_spell_ids"] == ("a", "z")
    assert payload["occurrence"]["graph_rows"][0] == (("a", 1), ())
    assert payload["occurrence"]["instance_key_rows"] == (
        ("a", (("a", 1), ("a", 3))),
        ("root", (("root", None),)),
    )
    assert payload["occurrence"]["canonical_occurrence_rows"] == (
        ("a", ("a", 1)),
        ("root", ("root", 0)),
    )
    assert payload["occurrence"]["contract_override_rows"] == (
        (("a", 1), (("__args__", (1, 2)), ("x", 7))),
    )
    assert payload["injection"]["instance_keys"] == (
        ("a", None),
        ("a", 2),
        ("z", 3),
    )
    assert payload["injection"]["instance_rows"][1] == (
        ("a", 2),
        True,
        True,
        (("__args__", (9,)), ("fixed", "ok")),
        (
            ("contracted", "contract", (), "contracted", "ckey"),
            ("dep", "dependency", (("a", None), ("z", 3)), "dep", None),
        ),
    )
    assert payload["patch_maps"]["override_target_specs"] == (
        "override-a",
        "override-z",
    )
    assert payload["patch_maps"]["override_target_rows"] == (
        (
            "override-a",
            3,
            (
                ("dep-a", "arg", 3, "normal"),
                ("dep-b", "arg", 1, "normal"),
            ),
        ),
        (
            "override-z",
            1,
            (
                ("dep-a", "arg", 3, "normal"),
            ),
        ),
    )
    assert payload["patch_maps"]["mutation_target_specs"] == (
        "mutation-a",
        "mutation-z",
    )
    assert payload["patch_maps"]["mutation_target_rows"] == (
        (
            "mutation-a",
            (
                ("child-a", "mut", 2, "old-a"),
                ("child-b", "mut", 5, "old-b"),
            ),
        ),
        (
            "mutation-z",
            (
                ("child-b", "mut", 5, "old-b"),
            ),
        ),
    )
    assert payload["execution"]["no_overrides"]["plan_variant"] == "no_overrides_fast"
    no_overrides_payload = payload["execution"]["no_overrides"]
    first_step_row = no_overrides_payload["steps_rows"][0]
    assert first_step_row["spell_id"] == "a"
    assert first_step_row["dependency_resolution_order"] == (
        ("dep", (("a-dep", None),)),
    )
    assert no_overrides_payload["steps_rows_signature"] is not None
    assert "transient_schema" in no_overrides_payload
    assert payload["execution"]["overrides"]["plan_variant"] == "overrides"
    assert payload["execution"]["overrides_with_mutations"]["plan_variant"] == "overrides_with_mutations"
    assert signatures["phase8_11"] == payload["signature"]


def test_build_injection_instance_rows_fails_fast_on_invalid_spec_contract() -> None:
    """Injection row export should fail fast on malformed injection specs."""
    with pytest.raises(AttributeError):
        SharedCompilerExecutions.build_injection_instance_rows(
            {
                ("root", None): object(),
            }
        )


def test_build_override_target_rows_fails_fast_on_invalid_socket_ref_contract() -> None:
    """Override row export should fail fast on malformed socket refs."""
    override_patch_map = SimpleNamespace(
        targets_by_spec={"spec": [object()]},
        specificity_by_spec={"spec": 1},
    )
    with pytest.raises(AttributeError):
        SharedCompilerExecutions.build_override_target_rows(override_patch_map)


def test_build_mutation_target_rows_fails_fast_on_invalid_patch_contract() -> None:
    """Mutation row export should fail fast on malformed patch refs."""
    mutation_patch_map = SimpleNamespace(
        targets_by_spec={"spec": [object()]},
    )
    with pytest.raises(AttributeError):
        SharedCompilerExecutions.build_mutation_target_rows(mutation_patch_map)


def test_capture_phase8_11_codegen_ir_signature_stable_across_map_insertion_orders() -> None:
    """Equivalent map payloads should produce the same phase8_11 signature."""
    artifact_a = SpellCompilerArtifact("root")
    artifact_b = SpellCompilerArtifact("root")

    def _configure_artifact(artifact: SpellCompilerArtifact, reverse: bool) -> None:
        artifact._execution_plan_phase11_no_overrides = _make_phase11_plan_stub(
            plan_variant="no_overrides_fast",
            root_spell_id="root",
            step_spell_ids=("a",),
        )
        artifact._execution_plan_phase11_overrides = _make_phase11_plan_stub(
            plan_variant="overrides",
            root_spell_id="root",
            step_spell_ids=("a",),
        )
        artifact._execution_plan_phase11 = _make_phase11_plan_stub(
            plan_variant="overrides_with_mutations",
            root_spell_id="root",
            step_spell_ids=("a",),
        )
        keys = [("a", None), ("z", 3)]
        if reverse:
            keys = list(reversed(keys))
        instance_injections = {}
        for key in keys:
            instance_injections[key] = SimpleNamespace(
                allow_list_aggregation=False,
                uses_positional_override=False,
                contract_payload=None,
                param_sources={},
            )
        artifact._injection_plan_phase9 = SimpleNamespace(
            instance_injections=instance_injections,
        )
        specs = ["override-a", "override-z"]
        if reverse:
            specs = list(reversed(specs))
        artifact._override_patch_map_phase10 = SimpleNamespace(
            targets_by_spec={spec: [] for spec in specs},
            specificity_by_spec={"override-a": 3, "override-z": 1},
        )
        artifact._mutation_patch_map_phase10 = SimpleNamespace(
            targets_by_spec={spec.replace("override", "mutation"): [] for spec in specs},
        )

    _configure_artifact(artifact_a, reverse=False)
    _configure_artifact(artifact_b, reverse=True)

    SharedCompilerExecutions.capture_phase8_11_codegen_ir(artifact_a)
    SharedCompilerExecutions.capture_phase8_11_codegen_ir(artifact_b)

    assert (
        artifact_a._codegen_ir["phase8_11"]["signature"]
        == artifact_b._codegen_ir["phase8_11"]["signature"]
    )


def test_hash_codegen_signature_fastpaths_skip_pickle_for_supported_types(
        monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Scalar fastpaths should hash deterministically without hitting pickle."""

    def _pickle_boom(*args: Any, **kwargs: Any) -> bytes:
        raise AssertionError("pickle.dumps should not be called for fastpath parts")

    monkeypatch.setattr(pickle, "dumps", _pickle_boom)

    first_signature = SharedCompilerExecutions.hash_codegen_signature(
        None,
        True,
        False,
        7,
        -3.5,
        "alpha",
        b"beta",
        bytearray(b"gamma"),
    )
    second_signature = SharedCompilerExecutions.hash_codegen_signature(
        None,
        True,
        False,
        7,
        -3.5,
        "alpha",
        b"beta",
        bytearray(b"gamma"),
    )

    assert second_signature == first_signature


def test_serialize_codegen_signature_part_falls_back_to_repr_on_pickle_error() -> None:
    """Unpicklable values should serialize via stable repr bytes."""

    class _Unpicklable:
        def __reduce__(self) -> Any:
            raise TypeError("cannot pickle")

        def __repr__(self) -> str:
            return "UnpicklableStable()"

    payload = SharedCompilerExecutions.serialize_codegen_signature_part(_Unpicklable())

    assert payload == b"UnpicklableStable()"


@pytest.mark.parametrize(
    "step_overrides",
    (
        {"instance_key": ("root", 1)},
        {"existence": Existence.many},
        {"shared_instance": True},
        {"dependency_resolution_order": (("dep", (("alt-dep", None),)),)},
        {"override_match_prefix": 42, "override_match_prefix_len": 1},
        {"override_keys": ("dep", "dep2")},
        {"expects_overrides": True},
        {"contract_keys": ("dep", "contract")},
        {"allow_list_aggregation": True},
        {"uses_positional_override": True, "contract_positional_override": (1, 2)},
        {"has_contract_payload": True, "contract_payload": {"custom": "value"}},
        {"lock_hint": "spell_lock"},
        {"use_spell_lock_hint": True},
        {"requires_spellspace": True},
        {"owner_conduit_required": True},
        {"must_register": True},
        {"disposal_method_names": ("cleanup",)},
        {"creations_target_kind": 2},
    ),
)
def test_build_phase11_variant_ir_payload_signature_changes_on_step_semantics(
        step_overrides: dict[str, object],
) -> None:
    """Phase11 variant payload signatures should invalidate on semantic step changes."""
    base_plan = _make_phase11_plan_stub(
        plan_variant="no_overrides_fast",
        root_spell_id="root",
        step_spell_ids=("root",),
    )
    changed_step = _make_phase11_plan_stub(
        plan_variant="no_overrides_fast",
        root_spell_id="root",
        step_spell_ids=("root",),
    ).steps[0]
    for field_name, value in step_overrides.items():
        setattr(changed_step, field_name, value)
    changed_plan = SimpleNamespace(
        plan_variant="no_overrides_fast",
        root_spell_id="root",
        steps=(changed_step,),
        fast_transient_plan=None,
    )

    base_payload = SharedCompilerExecutions.build_phase11_variant_ir_payload(base_plan)
    changed_payload = SharedCompilerExecutions.build_phase11_variant_ir_payload(changed_plan)

    stripped_override_fields = {
        "override_match_prefix",
        "override_match_prefix_len",
        "override_keys",
        "expects_overrides",
    }
    if set(step_overrides.keys()).issubset(stripped_override_fields):
        assert changed_payload["steps_rows_signature"] == base_payload["steps_rows_signature"]
        assert changed_payload["signature"] == base_payload["signature"]
    else:
        assert changed_payload["steps_rows_signature"] != base_payload["steps_rows_signature"]
        assert changed_payload["signature"] != base_payload["signature"]


def test_build_phase11_variant_ir_payload_signature_changes_on_variant_label() -> None:
    """Phase11 variant label should contribute to the outer signature."""
    overrides_plan = _make_phase11_plan_stub(
        plan_variant="overrides",
        root_spell_id="root",
        step_spell_ids=("root",),
    )
    mutation_plan = _make_phase11_plan_stub(
        plan_variant="overrides_with_mutations",
        root_spell_id="root",
        step_spell_ids=("root",),
    )

    overrides_payload = SharedCompilerExecutions.build_phase11_variant_ir_payload(overrides_plan)
    mutation_payload = SharedCompilerExecutions.build_phase11_variant_ir_payload(mutation_plan)

    assert mutation_payload["steps_rows_signature"] == overrides_payload["steps_rows_signature"]
    assert mutation_payload["signature"] != overrides_payload["signature"]


def test_capture_phase8_11_codegen_ir_signature_changes_on_enriched_payload_semantics() -> None:
    """Phase8_11 signature should change when enriched occurrence/injection/patch data changes."""
    artifact = SpellCompilerArtifact("root")
    artifact._execution_plan_phase11_no_overrides = _make_phase11_plan_stub(
        plan_variant="no_overrides_fast",
        root_spell_id="root",
        step_spell_ids=("a",),
    )
    artifact._execution_plan_phase11_overrides = _make_phase11_plan_stub(
        plan_variant="overrides",
        root_spell_id="root",
        step_spell_ids=("a",),
    )
    artifact._execution_plan_phase11 = _make_phase11_plan_stub(
        plan_variant="overrides_with_mutations",
        root_spell_id="root",
        step_spell_ids=("a",),
    )
    artifact._occurrence_plan_phase8 = SimpleNamespace(
        execution_order=("a",),
        root_instance_key=("root", None),
        shared_spell_ids={"a"},
        contract_dependencies_complete=True,
        occurrence_graph={
            ("root", 0): {"dep": [("a", 1)]},
            ("a", 1): {},
        },
        instance_keys_by_spell_id={"a": [("a", None)]},
        canonical_occurrences_by_spell_id={"a": ("a", 1)},
        contract_overrides_by_occurrence={("a", 1): {"x": 1}},
        contract_overrides_by_spell_id={"a": [(("a", 1), {"x": 1})]},
    )
    artifact._injection_plan_phase9 = SimpleNamespace(
        instance_injections={
            ("a", None): SimpleNamespace(
                allow_list_aggregation=False,
                uses_positional_override=False,
                contract_payload=None,
                param_sources={},
            ),
        },
    )
    artifact._override_patch_map_phase10 = SimpleNamespace(
        targets_by_spec={"**dep": []},
        specificity_by_spec={"**dep": 1},
    )
    artifact._mutation_patch_map_phase10 = SimpleNamespace(
        targets_by_spec={"**mut": []},
    )
    SharedCompilerExecutions.capture_phase8_11_codegen_ir(artifact)
    first_signature = artifact._codegen_ir["phase8_11"]["signature"]

    artifact._occurrence_plan_phase8 = SimpleNamespace(
        execution_order=("a",),
        root_instance_key=("root", None),
        shared_spell_ids={"a"},
        contract_dependencies_complete=True,
        occurrence_graph={
            ("root", 0): {"dep": [("a", 2)]},
            ("a", 2): {},
        },
        instance_keys_by_spell_id={"a": [("a", None)]},
        canonical_occurrences_by_spell_id={"a": ("a", 2)},
        contract_overrides_by_occurrence={("a", 2): {"x": 2}},
        contract_overrides_by_spell_id={"a": [(("a", 2), {"x": 2})]},
    )
    artifact._injection_plan_phase9 = SimpleNamespace(
        instance_injections={
            ("a", None): SimpleNamespace(
                allow_list_aggregation=True,
                uses_positional_override=False,
                contract_payload={"fixed": "v"},
                param_sources={},
            ),
        },
    )
    artifact._override_patch_map_phase10 = SimpleNamespace(
        targets_by_spec={"**dep": []},
        specificity_by_spec={"**dep": 3},
    )
    artifact._mutation_patch_map_phase10 = SimpleNamespace(
        targets_by_spec={"**mut2": []},
    )
    SharedCompilerExecutions.capture_phase8_11_codegen_ir(artifact)
    second_signature = artifact._codegen_ir["phase8_11"]["signature"]

    assert second_signature != first_signature


def test_try_build_execution_plan_variant_from_base_returns_fresh_copied_plan() -> None:
    """Phase11 sibling-variant derivation should return a fresh copied plan."""
    base_steps = [SimpleNamespace(name="step")]
    base_plan = SimpleNamespace(
        root_spell_id="root",
        root_instance_key=("root", None),
        steps=base_steps,
        spell_id_step_index={"root": 0},
        optimistic_object_refs_by_spell_id={"root": "existing"},
        available_param_by_spell_id={"root": 1},
    )

    derived = SharedCompilerExecutions.try_build_execution_plan_variant_from_base(
        base_plan=base_plan,
        plan_variant="overrides",
    )

    assert derived is not None
    assert derived.root_spell_id == "root"
    assert derived.root_instance_key == ("root", None)
    assert derived.plan_variant == "overrides"
    assert derived.steps == base_steps
    assert derived.steps is not base_steps
    assert derived.spell_id_step_index == {"root": 0}
    assert derived.spell_id_step_index is not base_plan.spell_id_step_index
    assert derived.optimistic_object_refs_by_spell_id == {"root": "existing"}
    assert derived.available_param_by_spell_id == {"root": 1}
    assert derived.fast_plan is None
    derived.cleanup()


@pytest.mark.parametrize(
    "base_plan",
    [
        SimpleNamespace(),
        SimpleNamespace(
            root_spell_id=None,
            root_instance_key=("root", None),
            steps=[],
            spell_id_step_index={},
            optimistic_object_refs_by_spell_id={},
            available_param_by_spell_id={},
        ),
        SimpleNamespace(
            root_spell_id="root",
            root_instance_key=("root", None),
            steps=None,
            spell_id_step_index={},
            optimistic_object_refs_by_spell_id={},
            available_param_by_spell_id={},
        ),
        SimpleNamespace(
            root_spell_id="root",
            root_instance_key=("root", None),
            steps=object(),
            spell_id_step_index={},
            optimistic_object_refs_by_spell_id={},
            available_param_by_spell_id={},
        ),
    ],
)
def test_try_build_execution_plan_variant_from_base_returns_none_for_incompatible_inputs(
        base_plan: object,
) -> None:
    """Phase11 sibling-variant derivation should reject incompatible base plans."""
    assert SharedCompilerExecutions.try_build_execution_plan_variant_from_base(
        base_plan=base_plan,
        plan_variant="overrides",
    ) is None


def test_reset_phase8_11_codegen_ir_clears_resolution_complete_flag() -> None:
    """Phase8_11 IR reset should clear executor caches and resolution_complete state."""
    spell = _make_spell_stub("root")
    artifact = SpellCompilerArtifact("root")
    artifact._codegen_ir = {
        "phase2_5": {},
        "phase8_11": {"payload": 1},
        "signatures": {"phase8_11": "sig"},
    }
    artifact._phase8_11_codegen_ir_dirty = True
    artifact._phase12_no_overrides_executor = object()
    artifact._phase12_no_overrides_executor_signature = "sig"
    artifact._phase8_occurrence_plan_input_signature = "phase8"
    artifact._phase8_occurrence_plan_fast_key = ("fast",)
    artifact._phase9_injection_plan_input_signature = "phase9"
    artifact._phase10_patch_maps_input_signature = ("phase10",)
    artifact._phase11_no_overrides_input_signature = "phase11"
    artifact._phase11_no_overrides_fast_key = ("fast11",)
    spell.resolution_complete = True

    SharedCompilerExecutions.reset_phase8_11_codegen_ir(spell, artifact)

    assert artifact._codegen_ir["phase8_11"] == {}
    assert "phase8_11" not in artifact._codegen_ir["signatures"]
    assert artifact._phase8_11_codegen_ir_dirty is False
    assert artifact._phase12_no_overrides_executor is None
    assert artifact._phase12_no_overrides_executor_signature is None
    assert artifact._phase8_occurrence_plan_input_signature is None
    assert artifact._phase8_occurrence_plan_fast_key is None
    assert artifact._phase9_injection_plan_input_signature is None
    assert artifact._phase10_patch_maps_input_signature is None
    assert artifact._phase11_no_overrides_input_signature is None
    assert artifact._phase11_no_overrides_fast_key is None
    assert spell.resolution_complete is False


def test_capture_phase8_11_codegen_ir_if_dirty_only_flushes_when_dirty(monkeypatch) -> None:
    """Dirty flush helper should only export phase8_11 IR when the dirty bit is set."""
    artifact = SpellCompilerArtifact("root")
    artifact._phase8_11_codegen_ir_dirty = False
    calls: list[str] = []

    monkeypatch.setattr(
        SharedCompilerExecutions,
        "capture_phase8_11_codegen_ir",
        lambda artifact: calls.append("capture"),
    )

    SharedCompilerExecutions.capture_phase8_11_codegen_ir_if_dirty(artifact)
    assert calls == []

    artifact._phase8_11_codegen_ir_dirty = True
    SharedCompilerExecutions.capture_phase8_11_codegen_ir_if_dirty(artifact)
    assert calls == ["capture"]
