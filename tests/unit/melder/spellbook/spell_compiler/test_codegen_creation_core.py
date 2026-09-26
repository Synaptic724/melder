"""Focused unit tests for the phase-11 codegen-creation contract."""

from types import SimpleNamespace
from typing import Any, Tuple

import pytest

import melder.aether.spellbook.spell_compiler.codegen_creation_system.strategies.many_only.steps.many_only_no_overrides_codegen_creation_step as many_only_no_overrides_step_module
from melder.aether.spellbook.spell_compiler.codegen_creation_system.codegen_creation.spell_codegen_creation import (
    SpellCodegenCreation,
)
from melder.aether.spellbook.spell_compiler.codegen_creation_system.codegen_creation_discovery_system.codegen_creation_discovery_system import (
    CodegenCreationDiscovery,
    CodegenCreationDiscoverySystem,
)
from melder.aether.spellbook.spell_compiler.codegen_creation_system.codegen_creation_system import (
    CodegenCreationSystem,
)
from melder.aether.spellbook.spell_compiler.codegen_creation_system.spell_codegen_strategy_builder import (
    SpellCodegenStrategyBuilder,
)
from melder.aether.spellbook.spell_compiler.codegen_creation_system.strategies.generalized.generalized_codegen_creation_strategy import (
    GeneralizedCodegenCreationStrategy,
)
from melder.aether.spellbook.spell_compiler.codegen_creation_system.strategies.many_only.many_only_codegen_creation_strategy import (
    ManyOnlyCodegenCreationStrategy,
)
from melder.aether.spellbook.spell_compiler.codegen_creation_system.strategies.many_only.many_only_codegen_creation_state import (
    ManyOnlyCodegenCreationState,
)
from melder.aether.spellbook.spell_compiler.codegen_creation_system.strategies.many_only.steps.many_only_no_overrides_codegen_creation_step import (
    ManyOnlyNoOverridesCodegenCreationStep,
)
from melder.aether.spellbook.spell_compiler.codegen_creation_system.strategies.solo.solo_codegen_creation_strategy import (
    SoloCodegenCreationStrategy,
)
import melder.aether.spellbook.spell_compiler.codegen_creation_system.strategies.solo.steps.solo_no_overrides_codegen_creation_step as solo_no_overrides_step_module
import melder.aether.spellbook.spell_compiler.codegen_creation_system.strategies.solo.steps.solo_overrides_codegen_creation_step as solo_overrides_step_module
from melder.aether.spellbook.spell_compiler.codegen_planner.spell_codegen_plan import (
    SpellCodegenPlan,
)


class _CleanupProbe:
    """Simple cleanup double used to prove previous-creation cleanup."""

    def __init__(self) -> None:
        self.cleanup_called = False

    def cleanup(self) -> None:
        self.cleanup_called = True


class _CreationStrategyProbe:
    """Minimal creation strategy double for facade tests."""

    def __init__(self, strategy_id: str) -> None:
        self.strategy_id = strategy_id

    def apply(
            self,
            spell_codegen_model: Any,
            spell_codegen_plan: Any,
            spell_codegen_creation: SpellCodegenCreation,
    ) -> None:
        _ = spell_codegen_model
        _ = spell_codegen_plan
        spell_codegen_creation.metadata[self.strategy_id] = True


class _StrategyBuilderProbe:
    """Minimal strategy-builder double for creation-system facade tests."""

    def __init__(self, strategies: Tuple[Any, ...]) -> None:
        self._strategies = strategies
        self.requested_strategy_ids: Tuple[str, ...] = ()
        self.cleanup_called = False

    def cleanup(self) -> None:
        self.cleanup_called = True

    def get_strategies(self, strategy_ids: Tuple[str, ...]) -> Tuple[Any, ...]:
        self.requested_strategy_ids = strategy_ids
        return self._strategies


class _DiscoveryProbe:
    """Minimal discovery-system double for creation-system facade tests."""

    def __init__(self, discovery: CodegenCreationDiscovery) -> None:
        self._discovery = discovery
        self.discovered_pair: Tuple[Any, Any] | None = None

    def discover(
            self,
            spell_codegen_model: Any,
            spell_codegen_plan: Any,
    ) -> CodegenCreationDiscovery:
        self.discovered_pair = (spell_codegen_model, spell_codegen_plan)
        return self._discovery


def test_codegen_creation_discovery_system_selects_generalized_chain_by_default() -> None:
    """The discovery system should extend the generalized chain with the final creation-context strategy."""
    discovery = CodegenCreationDiscoverySystem().discover(
        object(),
        SpellCodegenPlan(
            processor_strategy_ids=(),
            plan_strategy_ids=("generalized_codegen_plan",),
            no_overrides_plan=None,
            overrides_plan=None,
            metadata={"selected_strategy_id": "generalized_codegen_plan"},
        ),
    )

    assert discovery.selected_strategy_ids == (
        "generalized_codegen_creation",
    )


def test_codegen_creation_discovery_system_selects_solo_family() -> None:
    """The discovery system should route solo planner output to the solo creation family."""
    discovery = CodegenCreationDiscoverySystem().discover(
        object(),
        SpellCodegenPlan(
            processor_strategy_ids=(),
            plan_strategy_ids=("generalized_solo_codegen_plan",),
            no_overrides_plan=None,
            overrides_plan=None,
            metadata={"selected_strategy_id": "generalized_solo_codegen_plan"},
        ),
    )

    assert discovery.selected_strategy_ids == (
        "solo_codegen_creation",
    )


def test_codegen_creation_discovery_system_selects_many_only_family() -> None:
    """The discovery system should route many-only planner output to the many-only creation family."""
    discovery = CodegenCreationDiscoverySystem().discover(
        object(),
        SpellCodegenPlan(
            processor_strategy_ids=(),
            plan_strategy_ids=("many_only_codegen_plan",),
            no_overrides_plan=None,
            overrides_plan=None,
            metadata={"selected_strategy_id": "many_only_codegen_plan"},
        ),
    )

    assert discovery.selected_strategy_ids == (
        "many_only_codegen_creation",
    )


def test_codegen_creation_discovery_system_rejects_a_plan_no_family_claims() -> None:
    """A plan none of the three families claims fails discovery: there is no fallback family (2026-09-26)."""
    with pytest.raises(RuntimeError, match="could not select a creation discovery result"):
        CodegenCreationDiscoverySystem().discover(
            object(),
            SpellCodegenPlan(
                processor_strategy_ids=(),
                plan_strategy_ids=(),
                no_overrides_plan=None,
                overrides_plan=None,
                metadata={"selected_strategy_id": "other_plan"},
            ),
        )


def test_spell_codegen_strategy_builder_registers_extended_order() -> None:
    """The real strategy builder should expose the solo, many-only and generalized creation families."""
    builder = SpellCodegenStrategyBuilder()

    assert builder.registered_strategy_names() == (
        "solo_codegen_creation",
        "many_only_codegen_creation",
        "generalized_codegen_creation",
    )
    assert isinstance(
        builder.get_strategy("solo_codegen_creation"),
        SoloCodegenCreationStrategy,
    )
    assert isinstance(
        builder.get_strategy("many_only_codegen_creation"),
        ManyOnlyCodegenCreationStrategy,
    )
    with pytest.raises(RuntimeError, match="missing strategy 'missing_creation'"):
        builder.get_strategy("missing_creation")


def test_spell_codegen_creation_cleanup_cleans_metadata() -> None:
    """The creation container should only carry the two runtime doors plus metadata."""
    creation = SpellCodegenCreation(
        selected_strategy_ids=("setup",),
        discovery_reason="reason",
        no_overrides_executor=lambda caller_creations: ("plain", True),
        overrides_executor=lambda caller_creations, overrides: ("override", False),
        metadata={"hello": "world"},
        no_overrides_code_object=object(),
        overrides_code_object=object(),
    )

    creation.cleanup()

    assert not hasattr(creation, "metadata")


def test_codegen_creation_system_build_requires_model_and_plan_first() -> None:
    """The creation facade should fail hard until both model and plan exist."""
    system = CodegenCreationSystem()
    missing_model = type(
        "ArtifactProbe",
        (),
        {
            "_spell_codegen_model": None,
            "_spell_codegen_plan": object(),
        },
    )()
    missing_plan = type(
        "ArtifactProbe",
        (),
        {
            "_spell_codegen_model": object(),
            "_spell_codegen_plan": None,
        },
    )()

    with pytest.raises(RuntimeError, match="artifact._spell_codegen_model first"):
        system.build(missing_model)
    with pytest.raises(RuntimeError, match="artifact._spell_codegen_plan first"):
        system.build(missing_plan)


def test_codegen_creation_system_build_runs_selected_strategy_chain_and_cleans_previous() -> None:
    """The creation facade should publish the new artifact and cleanup the superseded one."""
    system = CodegenCreationSystem()
    strategy_a = _CreationStrategyProbe("a")
    strategy_b = _CreationStrategyProbe("b")
    builder = _StrategyBuilderProbe((strategy_a, strategy_b))
    discovery = _DiscoveryProbe(
        CodegenCreationDiscovery(
            selected_strategy_ids=("a", "b"),
            discovery_reason="picked-by-test",
        )
    )
    previous_creation = _CleanupProbe()
    model = object()
    plan = SimpleNamespace(
        plan_family_id="generalized",
        candidate_codegen_style_ids=("generalized_default",),
    )
    artifact = type(
        "ArtifactProbe",
        (),
        {
            "_spell_codegen_model": model,
            "_spell_codegen_plan": plan,
            "_spell_codegen_creation": previous_creation,
        },
    )()
    system._strategy_builder = builder
    system._discovery_system = discovery

    system.build(artifact)

    creation = artifact._spell_codegen_creation
    assert isinstance(creation, SpellCodegenCreation)
    assert discovery.discovered_pair == (model, plan)
    assert builder.requested_strategy_ids == ("a", "b")
    assert creation.selected_strategy_ids == ("a", "b")
    assert creation.discovery_reason == "picked-by-test"
    assert creation.metadata["a"] is True
    assert creation.metadata["b"] is True
    assert previous_creation.cleanup_called is True


def test_many_only_no_overrides_step_records_many_executor_and_signature(
        monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The many-only no-overrides step should use the many-only helper surface."""
    plan = SpellCodegenPlan(
        processor_strategy_ids=(),
        plan_strategy_ids=(),
        no_overrides_plan=type(
            "LanePlanProbe",
            (),
            {
                "lane_id": "many_only_no_overrides",
                "root_spell_id": "root",
                "root_instance_key": ("root", None),
                "steps": (object(), object()),
                "step_call_modes": (0, 1),
                "root_step_index": 0,
                "step_has_disposal_methods": (False, False),
            },
        )(),
        overrides_plan=None,
        metadata={},
    )
    creation = SpellCodegenCreation(
        selected_strategy_ids=(),
        discovery_reason=None,
        no_overrides_executor=None,
        overrides_executor=None,
        metadata={},
    )

    monkeypatch.setattr(
        many_only_no_overrides_step_module.ManyOnlyCodegenCreationHelpers,
        "build_no_overrides_step_signature_row",
        lambda step: ("step", id(step)),
    )
    monkeypatch.setattr(
        many_only_no_overrides_step_module.ManyOnlyCodegenCreationHelpers,
        "normalize_instance_key",
        lambda instance_key: instance_key,
    )
    monkeypatch.setattr(
        many_only_no_overrides_step_module.ManyOnlyCodegenCreationHelpers,
        "hash_signature",
        lambda *parts: "sig:{0}".format(len(parts)),
    )
    monkeypatch.setattr(
        many_only_no_overrides_step_module,
        "compile_no_overrides_codegen_creation_executor_from_plan",
        lambda *, plan, return_compiled_code_object=False: (
            ("executor", plan.lane_id),
            "code-object",
        ) if return_compiled_code_object else ("executor", plan.lane_id),
    )

    state = ManyOnlyCodegenCreationState(
        spell_codegen_model=object(),
        spell_codegen_plan=plan,
        spell_codegen_creation=creation,
    )
    ManyOnlyNoOverridesCodegenCreationStep().apply(state)

    assert creation.no_overrides_executor == ("executor", "many_only_no_overrides")
    assert state.base_no_overrides_executor == ("executor", "many_only_no_overrides")
    assert creation.no_overrides_code_object == "code-object"
    assert creation.metadata["no_overrides_plan_kind"] == "many_only_no_overrides"


def test_solo_codegen_creation_strategy_builds_solo_owned_runtime_doors(
        monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    The solo phase-11 family publishes lazy cold doors and manifest metadata.

    Manifest-first contract: phase 11 compiles nothing for this family. The
    published doors are cold closures that hydrate on first meld, code-object
    fields stay None (the manifest is the cache currency), and runtime
    metadata carries the lazy-hydration parity keys. The legacy eager compile
    seams are patched with sentinels purely to prove the strategy never calls
    them at phase-11 time.
    """
    sentinel_no_overrides = lambda caller_creations=None, owner_creations=None, caller_creations_lock_held=False: "plain"
    sentinel_overrides = lambda caller_creations, overrides, caller_creations_lock_held=False: "override"
    monkeypatch.setattr(
        solo_no_overrides_step_module,
        "compile_solo_no_overrides_codegen_creation_executor",
        lambda **kwargs: (sentinel_no_overrides, "code-object"),
    )
    monkeypatch.setattr(
        solo_overrides_step_module,
        "compile_solo_overrides_codegen_creation_executor",
        lambda **kwargs: (sentinel_overrides, "code-object"),
    )

    root_spell = SimpleNamespace(
        spell_id="root",
        spell_name="root",
        spell_index=SimpleNamespace(selected_spell_id="root"),
        spell=lambda: "instance",
        has_disposal_methods=False,
        disposal_method_names=(),
        is_existing_creation=False,
        _owner_creations=object(),
    )
    model = SimpleNamespace(
        build_kind="construct",
        route_family="many",
        graph_shape=SimpleNamespace(root_spell_id="root"),
        spell_runtime_shape=SimpleNamespace(
            spell_count=1,
            records_by_spell_id={
                "root": SimpleNamespace(
                    spell=root_spell,
                    has_disposal_methods=False,
                )
            },
        ),
    )
    plan = SpellCodegenPlan(
        processor_strategy_ids=(),
        plan_strategy_ids=("generalized_solo_codegen_plan",),
        no_overrides_plan=SimpleNamespace(lane_id="solo_no_overrides"),
        overrides_plan=SimpleNamespace(lane_id="solo_overrides"),
        metadata={"selected_strategy_id": "generalized_solo_codegen_plan"},
    )
    creation = SpellCodegenCreation(
        selected_strategy_ids=(),
        discovery_reason=None,
        no_overrides_executor=None,
        overrides_executor=None,
        metadata={},
    )

    SoloCodegenCreationStrategy().apply(model, plan, creation)

    assert callable(creation.no_overrides_executor)
    assert callable(creation.overrides_executor)
    # Lazy-door contract: nothing compiles at phase 11, so the published
    # doors are cold sentinel-free closures and code objects stay None.
    assert creation.no_overrides_executor is not sentinel_no_overrides
    assert creation.overrides_executor is not sentinel_overrides
    assert creation.no_overrides_code_object is None
    assert creation.overrides_code_object is None
    assert "resolve_route_key" not in creation.metadata
    assert "fast_transient_no_overrides_enabled" not in creation.metadata
    assert creation.metadata["hydration"] == "lazy_first_meld"
    assert creation.metadata["no_overrides_step_count"] == 1
    assert creation.metadata["override_step_count"] == 1
