"""Contract tests for Phase 11 execution path in MeldEngine."""
from types import SimpleNamespace
from typing import Any, Dict

import pytest

from melder.aether.conduit.meld.meld_engine.meld_engine import MeldEngine
from melder.spellbook.existence.existence import Existence
from melder.spellbook.spell_crafter.blueprints.execution_plan import ExecutionPlan, ExecutionPlanStep
from melder.spellbook.spell_crafter.blueprints.injection_plan import InjectionSpec, ParamSource
from melder.spellbook.spell_crafter.dag.resolution_frame.resolution_frame import ResolutionFrame
from melder.spellbook.bind.spell_index import SpellIndex
from melder.utilities.custom_exceptions.meld_execution_error import MeldExecutionError


class _SpellStub:
    """
    Spell stub providing callable execution and existence metadata.
    """

    def __init__(
        self,
        *,
        spell_id: str,
        spell_fn,
        existence: Existence = Existence.unique,
    ) -> None:
        """
        Initialize the spell stub with a callable.
        """
        self.spell_index = SpellIndex(spell_id)
        self.spell_id = spell_id
        self.spell_name = spell_id
        self.spell = spell_fn
        self.existence = existence
        self.is_existing_creation = False
        self.is_class_spell = True
        self.is_method_spell = False
        self.is_lambda_spell = False
        self.user_created_object = None
        self.has_disposal_methods = False
        self.disposal_method_names = []
        self._lock = SimpleNamespace(__enter__=lambda *a, **k: None, __exit__=lambda *a, **k: None)
        self._owner_creations = None


class _ContextStub:
    """
    Context stub providing only the cancel_event and creations info.
    """

    def __init__(self) -> None:
        """
        Initialize with no cancellation or creations.
        """
        self.cancel_event = None
        self.caller_creations = None
        self.owner_creations = None
        self.caller_creations_lock_held = False


class _TestEngine(MeldEngine):
    """
    Test-only engine that bypasses creation locking.
    """

    def _resolve_spell_instance(self, spell, *, construct_fn):
        return construct_fn(), True


def _make_engine(
    *,
    root_spell: _SpellStub,
    spell_lookup: Dict[str, _SpellStub],
) -> MeldEngine:
    """
    Build a MeldEngine with a simplified context and frame.
    """
    context = _ContextStub()
    frame = ResolutionFrame(overrides={})
    engine = _TestEngine(
        context=context,
        root_spell=root_spell,
        dag=None,
        resolution_frame=None,
        requirements=None,
        frame=frame,
        blueprint=None,
        override_map={},
        spell_lookup=spell_lookup,
        system_states=None,
        occurrence_plan=None,
        injection_plan=None,
    )
    return engine


def test_run_execution_plan_rejects_root_mismatch() -> None:
    """
    Purpose:
        Ensure execution plan root mismatch raises MeldExecutionError.
    Contract:
        - Plan root id must match the root spell id.
    """
    root = _SpellStub(spell_id="root", spell_fn=lambda: "root")
    engine = _make_engine(root_spell=root, spell_lookup={"root": root})
    plan = ExecutionPlan(
        root_spell_id="other",
        root_instance_key=("root", None),
        steps=[],
    )

    with pytest.raises(MeldExecutionError):
        engine.run_execution_plan(plan)


def test_run_execution_plan_raises_on_missing_spell() -> None:
    """
    Purpose:
        Ensure missing spell ids in the lookup raise MeldExecutionError.
    Contract:
        - Each step's spell_id must exist in the spell_lookup.
    """
    root = _SpellStub(spell_id="root", spell_fn=lambda: "root")
    engine = _make_engine(root_spell=root, spell_lookup={"root": root})
    step = ExecutionPlanStep(
        spell_id="missing",
        instance_key=("missing", None),
        occurrence=("missing", ()),
        existence=Existence.unique,
        creation_target="owner",
        action="reuse",
        inject_spec=None,
        register=True,
    )
    plan = ExecutionPlan(
        root_spell_id="root",
        root_instance_key=("root", None),
        steps=[step],
    )

    with pytest.raises(MeldExecutionError):
        engine.run_execution_plan(plan)


def test_run_execution_plan_builds_kwargs_from_injection_spec() -> None:
    """
    Purpose:
        Ensure Phase 11 uses InjectionSpec to build kwargs.
    Contract:
        - Dependency instance results are passed to the callable.
    """
    dep = _SpellStub(spell_id="dep", spell_fn=lambda: "dep")
    root = _SpellStub(spell_id="root", spell_fn=lambda dep: {"dep": dep})
    engine = _make_engine(root_spell=root, spell_lookup={"root": root, "dep": dep})

    dep_step = ExecutionPlanStep(
        spell_id="dep",
        instance_key=("dep", None),
        occurrence=("dep", ()),
        existence=Existence.unique,
        creation_target="owner",
        action="reuse",
        inject_spec=None,
        register=True,
    )
    param_sources = {
        "dep": ParamSource(kind="dependency", dependency_keys=[("dep", None)]),
    }
    inject_spec = InjectionSpec(
        param_sources=param_sources,
        allow_list_aggregation=False,
        uses_positional_override=False,
        contract_payload=None,
    )
    root_step = ExecutionPlanStep(
        spell_id="root",
        instance_key=("root", None),
        occurrence=("root", ()),
        existence=Existence.unique,
        creation_target="owner",
        action="reuse",
        inject_spec=inject_spec,
        register=True,
    )
    plan = ExecutionPlan(
        root_spell_id="root",
        root_instance_key=("root", None),
        steps=[dep_step, root_step],
    )

    result = engine.run_execution_plan(plan)

    assert result == {"dep": "dep"}


def test_run_execution_plan_uses_empty_kwargs_without_spec() -> None:
    """
    Purpose:
        Validate Phase 11 uses empty kwargs when inject_spec is None.
    Contract:
        - Spell callable receives no dependency kwargs.
    """
    root = _SpellStub(spell_id="root", spell_fn=lambda: "root")
    engine = _make_engine(root_spell=root, spell_lookup={"root": root})

    step = ExecutionPlanStep(
        spell_id="root",
        instance_key=("root", None),
        occurrence=("root", ()),
        existence=Existence.unique,
        creation_target="owner",
        action="reuse",
        inject_spec=None,
        register=True,
    )
    plan = ExecutionPlan(
        root_spell_id="root",
        root_instance_key=("root", None),
        steps=[step],
    )

    result = engine.run_execution_plan(plan)

    assert result == "root"


def test_run_execution_plan_raises_on_missing_dependency() -> None:
    """
    Purpose:
        Ensure missing dependency results raise MeldExecutionError.
    Contract:
        - A missing dependency key in instance_results raises.
    """
    root = _SpellStub(spell_id="root", spell_fn=lambda dep: dep)
    engine = _make_engine(root_spell=root, spell_lookup={"root": root})

    param_sources = {
        "dep": ParamSource(kind="dependency", dependency_keys=[("dep", None)]),
    }
    inject_spec = InjectionSpec(
        param_sources=param_sources,
        allow_list_aggregation=False,
        uses_positional_override=False,
        contract_payload=None,
    )
    step = ExecutionPlanStep(
        spell_id="root",
        instance_key=("root", None),
        occurrence=("root", ()),
        existence=Existence.unique,
        creation_target="owner",
        action="reuse",
        inject_spec=inject_spec,
        register=True,
    )
    plan = ExecutionPlan(
        root_spell_id="root",
        root_instance_key=("root", None),
        steps=[step],
    )

    with pytest.raises(MeldExecutionError):
        engine.run_execution_plan(plan)


def test_run_execution_plan_falls_back_when_root_missing() -> None:
    """
    Purpose:
        Validate fallback to root-only construction when root is missing.
    Contract:
        - Missing root result triggers _construct_root_only fallback.
    """
    root = _SpellStub(spell_id="root", spell_fn=lambda: "root")
    dep = _SpellStub(spell_id="dep", spell_fn=lambda: "dep")
    engine = _make_engine(root_spell=root, spell_lookup={"root": root, "dep": dep})
    step = ExecutionPlanStep(
        spell_id="dep",
        instance_key=("dep", None),
        occurrence=("dep", ()),
        existence=Existence.unique,
        creation_target="owner",
        action="reuse",
        inject_spec=None,
        register=True,
    )
    plan = ExecutionPlan(
        root_spell_id="root",
        root_instance_key=("root", None),
        steps=[step],
    )

    result = engine.run_execution_plan(plan)

    assert result == "root"


def test_run_execution_plan_handles_list_dependencies() -> None:
    """
    Purpose:
        Validate list aggregation for multiple dependencies.
    Contract:
        - Multiple dependency results are provided as a list.
    """
    dep_a = _SpellStub(spell_id="a", spell_fn=lambda: "a")
    dep_b = _SpellStub(spell_id="b", spell_fn=lambda: "b")
    root = _SpellStub(spell_id="root", spell_fn=lambda deps: {"deps": deps})
    engine = _make_engine(root_spell=root, spell_lookup={"root": root, "a": dep_a, "b": dep_b})

    step_a = ExecutionPlanStep(
        spell_id="a",
        instance_key=("a", None),
        occurrence=("a", ()),
        existence=Existence.unique,
        creation_target="owner",
        action="reuse",
        inject_spec=None,
        register=True,
    )
    step_b = ExecutionPlanStep(
        spell_id="b",
        instance_key=("b", None),
        occurrence=("b", ()),
        existence=Existence.unique,
        creation_target="owner",
        action="reuse",
        inject_spec=None,
        register=True,
    )
    param_sources = {
        "deps": ParamSource(kind="dependency", dependency_keys=[("a", None), ("b", None)]),
    }
    inject_spec = InjectionSpec(
        param_sources=param_sources,
        allow_list_aggregation=True,
        uses_positional_override=False,
        contract_payload=None,
    )
    root_step = ExecutionPlanStep(
        spell_id="root",
        instance_key=("root", None),
        occurrence=("root", ()),
        existence=Existence.unique,
        creation_target="owner",
        action="reuse",
        inject_spec=inject_spec,
        register=True,
    )
    plan = ExecutionPlan(
        root_spell_id="root",
        root_instance_key=("root", None),
        steps=[step_a, step_b, root_step],
    )

    result = engine.run_execution_plan(plan)

    assert result == {"deps": ["a", "b"]}


def test_run_execution_plan_applies_contract_payload() -> None:
    """
    Purpose:
        Ensure contract payload values are applied in the execution path.
    Contract:
        - Contract payload keys are appended to kwargs.
    """
    root = _SpellStub(spell_id="root", spell_fn=lambda **kwargs: kwargs)
    engine = _make_engine(root_spell=root, spell_lookup={"root": root})

    inject_spec = InjectionSpec(
        param_sources={},
        allow_list_aggregation=False,
        uses_positional_override=False,
        contract_payload={"extra": "payload"},
    )
    step = ExecutionPlanStep(
        spell_id="root",
        instance_key=("root", None),
        occurrence=("root", ()),
        existence=Existence.unique,
        creation_target="owner",
        action="reuse",
        inject_spec=inject_spec,
        register=True,
    )
    plan = ExecutionPlan(
        root_spell_id="root",
        root_instance_key=("root", None),
        steps=[step],
    )

    result = engine.run_execution_plan(plan)

    assert result["extra"] == "payload"


def test_run_execution_plan_applies_positional_override() -> None:
    """
    Purpose:
        Validate positional overrides flow through execution plan kwargs.
    Contract:
        - __args__ payload is passed to the callable.
    """
    root = _SpellStub(spell_id="root", spell_fn=lambda *args, **kwargs: {"args": args})
    engine = _make_engine(root_spell=root, spell_lookup={"root": root})

    inject_spec = InjectionSpec(
        param_sources={},
        allow_list_aggregation=False,
        uses_positional_override=True,
        contract_payload={"__args__": [1, 2]},
    )
    step = ExecutionPlanStep(
        spell_id="root",
        instance_key=("root", None),
        occurrence=("root", ()),
        existence=Existence.unique,
        creation_target="owner",
        action="reuse",
        inject_spec=inject_spec,
        register=True,
    )
    plan = ExecutionPlan(
        root_spell_id="root",
        root_instance_key=("root", None),
        steps=[step],
    )

    result = engine.run_execution_plan(plan)

    assert result["args"] == (1, 2)
