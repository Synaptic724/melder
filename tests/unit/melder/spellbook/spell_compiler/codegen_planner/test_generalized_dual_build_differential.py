"""
Differential contract test: generalized dual-variant plan build.

Purpose:
    Pin `SpellGeneralizedCodegenPlanBuilder.build_dual()` to the two-build
    baseline it replaced (phase-10 single-pass work, patch lane
    generalized_singleton_specialization_2026_07_01): for identical model
    inputs the dual build must produce lane plans FIELD-FOR-FIELD equal to
    running `build()` once per variant - all 24 step contract attributes plus
    spell/spec identity, index maps, fast-path arrays, and transient plans.

Method:
    Synthetic models exercise mixed existences, override/contract keys,
    multi-instance-key path occurrences, contract payloads with positional
    overrides, existing-creation refs, and disposal-bearing many steps.
"""

import sys
from types import SimpleNamespace
from typing import Any


def _ensure_import_roots_on_path() -> None:
    """
    Purpose:
        Make `melder` imports resolve under plain CLI pytest runs.
    Contract:
        - Mirrors the efficacy probe's preamble; no-op in PyCharm runs and
          under the suite conftest (which adds src/).
    Returns:
        None.
    """
    if "." not in sys.path:
        sys.path.insert(0, ".")
    if "src" not in sys.path:
        sys.path.insert(0, "src")


_ensure_import_roots_on_path()

from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spell_compiler.codegen_planner.data.spell_generalized_codegen_lane_plan import (
    SpellGeneralizedCodegenPlanBuilder,
    SpellGeneralizedCodegenPlanVariant,
)
from melder.aether.spellbook.spell_compiler.codegen_creation_system.shared_assets.codegen_creation_schema_helpers import (
    CodegenCreationSchemaHelpers,
)


def param(name):
    return SimpleNamespace(
        name=name, is_keyword_only=False, is_var_keyword=False,
        is_var_positional=False)

def make_spell(callable_kind="class", param_names=None):
    requirements = None
    if param_names is not None:
        requirements = SimpleNamespace(
            parameters=[param(n) for n in param_names])
    return SimpleNamespace(
        is_class_spell=callable_kind == "class",
        is_method_spell=False,
        is_lambda_spell=callable_kind == "lambda",
        is_existing_creation=False,
        spell_index=SimpleNamespace(selected_spell_id="sid"),
        requirements=requirements,
        spell=object(),
        user_created_object=None,
    )

def source(deps=(), override_key=None, contract_key=None):
    return SimpleNamespace(
        dependency_keys=list(deps), override_key=override_key,
        contract_key=contract_key)

def spec(param_sources=None, allow_list=False, uses_pos=False, payload=None):
    return SimpleNamespace(
        param_sources=dict(param_sources or {}),
        allow_list_aggregation=allow_list,
        uses_positional_override=uses_pos,
        contract_payload=payload)

def make_model(records, keys_by_spell, specs_by_key, order, root_key,
               shared=(), canonical=None):
    return SimpleNamespace(
        graph_shape=SimpleNamespace(
            path_registry=SimpleNamespace(depth=lambda p: len(str(p))),
            root_spell_id=root_key[0]),
        order_shape=SimpleNamespace(execution_order=list(order)),
        instance_shape=SimpleNamespace(
            shared_spell_ids=set(shared),
            instance_keys_by_spell_id=keys_by_spell,
            root_instance_key=root_key,
            canonical_occurrences_by_spell_id=canonical or {}),
        injection_shape=SimpleNamespace(
            instance_specs_by_instance_key=specs_by_key),
        spell_runtime_shape=SimpleNamespace(records_by_spell_id=records),
    )

def record(existence, disposal=(), user_obj=None, spell=None):
    built = spell or make_spell()
    built.user_created_object = user_obj
    return SimpleNamespace(
        existence=existence,
        disposal_method_names=list(disposal),
        user_created_object=user_obj,
        spell=built,
        has_disposal_methods=bool(disposal))

STEP_ATTRS = (
    "instance_key", "occurrence", "existence", "creations_target_kind",
    "shared_instance", "dependency_keys", "dependency_keys_by_param",
    "dependency_resolution_order", "override_keys", "override_match_prefix",
    "override_match_prefix_len", "expects_overrides", "contract_keys",
    "allow_list_aggregation", "uses_positional_override", "contract_payload",
    "contract_positional_override", "has_contract_payload", "lock_hint",
    "use_spell_lock_hint", "requires_spellspace", "owner_conduit_required",
    "must_register", "disposal_method_names",
)
# Override-lane metadata now lives on SHARED steps and is stripped at ROW
# build for the no-overrides lane (include_override_metadata=False), so the
# no-overrides STEP comparison excludes these five fields and the ROW
# comparison (the real downstream contract) covers them instead.
OVERRIDE_STEP_ATTRS = (
    "override_keys", "override_match_prefix", "override_match_prefix_len",
    "expects_overrides", "contract_keys",
)
NEUTRAL_STEP_ATTRS = tuple(
    attr for attr in STEP_ATTRS if attr not in OVERRIDE_STEP_ATTRS
)
PLAN_ATTRS = (
    "lane_id", "root_spell_id", "root_instance_key", "spell_id_step_index",
    "optimistic_object_refs_by_spell_id", "available_param_by_spell_id",
    "fast_has_contract_payloads", "fast_has_existing_creations",
)

def compare_plans(old, new, label):
    no_overrides_lane = label.endswith("/no_overrides")
    include_override_metadata = not no_overrides_lane
    step_attrs = NEUTRAL_STEP_ATTRS if no_overrides_lane else STEP_ATTRS
    for attr in PLAN_ATTRS:
        ov, nv = getattr(old, attr), getattr(new, attr)
        assert ov == nv, (label, attr, ov, nv)
    assert len(old.steps) == len(new.steps), label
    for i, (os_, ns_) in enumerate(zip(old.steps, new.steps)):
        for attr in step_attrs:
            ov, nv = getattr(os_, attr), getattr(ns_, attr)
            assert ov == nv, (label, i, attr, ov, nv)
        assert os_.spell is ns_.spell, (label, i, "spell identity")
        assert os_.inject_spec is ns_.inject_spec, (label, i, "spec identity")
        # The downstream contract: manifest rows must be byte-identical to
        # the historical two-build output under each lane's strip flag.
        old_row = CodegenCreationSchemaHelpers.build_phase11_step_ir_row(
            os_, include_override_metadata=include_override_metadata,
        )
        new_row = CodegenCreationSchemaHelpers.build_phase11_step_ir_row(
            ns_, include_override_metadata=include_override_metadata,
        )
        assert old_row == new_row, (label, i, "row divergence")
    for attr in dir(old):
        if attr.startswith("fast_") and attr != "fast_transient_plan":
            ov, nv = getattr(old, attr), getattr(new, attr)
            assert ov == nv, (label, attr)
    otp, ntp = old.fast_transient_plan, new.fast_transient_plan
    assert (otp is None) == (ntp is None), (label, "transient presence")
    if otp is not None:
        for attr in dir(otp):
            if not attr.startswith("_") and not callable(getattr(otp, attr)):
                assert getattr(otp, attr) == getattr(ntp, attr), (label, attr)

def run_case(label, model):
    old_no = SpellGeneralizedCodegenPlanBuilder(
        state=model, plan_variant=SpellGeneralizedCodegenPlanVariant.NO_OVERRIDES,
    ).build()
    old_ov = SpellGeneralizedCodegenPlanBuilder(
        state=model, plan_variant=SpellGeneralizedCodegenPlanVariant.OVERRIDES,
    ).build()
    new_no, new_ov = SpellGeneralizedCodegenPlanBuilder(
        state=model, plan_variant=SpellGeneralizedCodegenPlanVariant.NO_OVERRIDES,
    ).build_dual()
    compare_plans(old_no, new_no, f"{label}/no_overrides")
    compare_plans(old_ov, new_ov, f"{label}/overrides")
    assert new_no.metadata["plan_family"] == "generalized"
    assert new_ov.metadata["plan_family"] == "generalized"
    # Sharing contract: one step list, two plan-owned list objects.
    assert new_no.steps is not new_ov.steps, label
    for i in range(len(new_no.steps)):
        assert new_no.steps[i] is new_ov.steps[i], (label, i, "not shared")


def test_dual_build_matches_two_build_mixed_existences_with_override_and_contract_keys() -> None:
    """Dual build equals the two-build baseline for this model shape."""
    run_case("mixed", make_model(
        records={
            "u1": record(Existence.unique, disposal=["close"]),
            "c1": record(Existence.unique_per_conduit,
                         spell=make_spell(param_names=["dep"])),
            "root": record(Existence.many,
                           spell=make_spell(param_names=["a", "b"])),
        },
        keys_by_spell={
            "u1": [("u1", None)], "c1": [("c1", None)], "root": [("root", None)],
        },
        specs_by_key={
            ("u1", None): spec(),
            ("c1", None): spec({"dep": source([("u1", None)], override_key="ov_dep")}),
            ("root", None): spec({
                "a": source([("u1", None)]),
                "b": source([("c1", None)], contract_key="ck_b"),
            }),
        },
        order=["u1", "c1", "root"],
        root_key=("root", None),
        shared=("u1",),
        canonical={"u1": ("u1", None), "c1": ("c1", None), "root": ("root", None)},
    ))


def test_dual_build_matches_two_build_all_many_fast_transient_graph() -> None:
    """Dual build equals the two-build baseline for this model shape."""
    run_case("transient", make_model(
        records={
            "m1": record(Existence.many), "m2": record(Existence.many),
            "root": record(Existence.many,
                           spell=make_spell(param_names=["x", "y"])),
        },
        keys_by_spell={
            "m1": [("m1", None)], "m2": [("m2", None)], "root": [("root", None)],
        },
        specs_by_key={
            ("m1", None): spec(), ("m2", None): spec(),
            ("root", None): spec({
                "x": source([("m1", None)]), "y": source([("m2", None)]),
            }),
        },
        order=["m1", "m2", "root"],
        root_key=("root", None),
        canonical={"m1": ("m1", None), "m2": ("m2", None), "root": ("root", None)},
    ))


def test_dual_build_matches_two_build_multi_instance_key_payload_and_positional() -> None:
    """Dual build equals the two-build baseline for this model shape."""
    run_case("multikey_payload", make_model(
        records={
            "dep": record(Existence.many),
            "root": record(Existence.unique_per_spell_space),
        },
        keys_by_spell={
            "dep": [("dep", "pathA"), ("dep", "pathB")], "root": [("root", None)],
        },
        specs_by_key={
            ("dep", "pathA"): spec(payload={"cfg": 1}),
            ("dep", "pathB"): spec(payload={"__args__": (1, 2), "z": 3}, uses_pos=True),
            ("root", None): spec({
                "d": source([("dep", "pathA"), ("dep", "pathB")], override_key="ov"),
            }, allow_list=True),
        },
        order=["dep", "root"],
        root_key=("root", None),
        canonical={"dep": ("dep", "pathA"), "root": ("root", None)},
    ))


def test_dual_build_matches_two_build_existing_creation_and_disposal_bearing_many() -> None:
    """Dual build equals the two-build baseline for this model shape."""
    run_case("existing_disposal", make_model(
        records={
            "e1": record(Existence.unique, user_obj=object()),
            "md": record(Existence.many, disposal=["dispose"]),
            "root": record(Existence.unique_per_conduit_lineage),
        },
        keys_by_spell={
            "e1": [("e1", None)], "md": [("md", None)], "root": [("root", None)],
        },
        specs_by_key={
            ("e1", None): spec(), ("md", None): spec(),
            ("root", None): spec({
                "a": source([("e1", None)]), "b": source([("md", None)]),
            }),
        },
        order=["e1", "md", "root"],
        root_key=("root", None),
        canonical={"e1": ("e1", None), "md": ("md", None), "root": ("root", None)},
    ))
