"""Direct unit tests for the phase-11 discovery seam."""

from typing import Optional, Tuple

import pytest

from melder.aether.spellbook.spell_compiler.codegen_creation_system.codegen_creation_discovery_system.codegen_creation_discovery import (
    CodegenCreationDiscovery,
)
from melder.aether.spellbook.spell_compiler.codegen_creation_system.codegen_creation_discovery_system.codegen_creation_discovery_strategy import (
    CodegenCreationDiscoveryStrategy,
)
from melder.aether.spellbook.spell_compiler.codegen_creation_system.codegen_creation_discovery_system.codegen_creation_discovery_strategy_builder import (
    CodegenCreationDiscoveryStrategyBuilder,
)
from melder.aether.spellbook.spell_compiler.codegen_creation_system.codegen_creation_discovery_system.codegen_creation_discovery_system import (
    CodegenCreationDiscoverySystem,
)
from melder.aether.spellbook.spell_compiler.codegen_creation_system.codegen_creation_discovery_system.strategies.fallback_no_overrides_codegen_creation_discovery_strategy import (
    FallbackNoOverridesCodegenCreationDiscoveryStrategy,
)
from melder.aether.spellbook.spell_compiler.codegen_creation_system.codegen_creation_discovery_system.strategies.generalized_codegen_creation_discovery_strategy import (
    GeneralizedCodegenCreationDiscoveryStrategy,
)
from melder.aether.spellbook.spell_compiler.codegen_planner.spell_codegen_plan import (
    SpellCodegenPlan,
)


class _ModelProbe:
    """Minimal processor-model double for discovery tests."""

    def __init__(self, label: str) -> None:
        """Store one visible label for test assertions."""
        self.label = label


class _DiscoveryStrategyProbe(CodegenCreationDiscoveryStrategy):
    """Programmable phase-11 discovery strategy double for facade tests."""

    def __init__(
            self,
            strategy_id: str,
            discovery: Optional[CodegenCreationDiscovery],
    ) -> None:
        """Store the stable id and programmed discovery result."""
        self._strategy_id = strategy_id
        self._discovery = discovery
        self.calls = []

    @property
    def strategy_id(self) -> str:
        """Return the stable test strategy id."""
        return self._strategy_id

    def discover(
            self,
            spell_codegen_model: _ModelProbe,
            spell_codegen_plan: SpellCodegenPlan,
    ) -> Optional[CodegenCreationDiscovery]:
        """Record the model/plan pair and return the programmed result."""
        self.calls.append((spell_codegen_model, spell_codegen_plan))
        return self._discovery


class _DiscoveryStrategyBuilderProbe:
    """Minimal builder double for phase-11 discovery-system tests."""

    def __init__(self, strategies: Tuple[CodegenCreationDiscoveryStrategy, ...]) -> None:
        """Store the strategy tuple returned by the probe."""
        self._strategies = strategies
        self.cleanup_called = False

    def cleanup(self) -> None:
        """Record one cleanup call."""
        self.cleanup_called = True

    def registered_strategy_names(self) -> Tuple[str, ...]:
        """Return the stored strategy ids in order."""
        return tuple(strategy.strategy_id for strategy in self._strategies)

    def get_strategies(
            self,
            strategy_names: Tuple[str, ...],
    ) -> Tuple[CodegenCreationDiscoveryStrategy, ...]:
        """Return the stored strategy tuple for the requested ids."""
        assert strategy_names == self.registered_strategy_names()
        return self._strategies


def _make_plan(selected_strategy_id: str) -> SpellCodegenPlan:
    """Build a minimal plan stub for phase-11 discovery tests."""
    return SpellCodegenPlan(
        processor_strategy_ids=(),
        plan_strategy_ids=(),
        no_overrides_plan=None,
        overrides_plan=None,
        metadata={"selected_strategy_id": selected_strategy_id},
    )


def test_generalized_codegen_creation_discovery_strategy_claims_generalized_plan() -> None:
    """The default phase-11 generalized strategy should claim generalized planner output only."""
    discovery = GeneralizedCodegenCreationDiscoveryStrategy().discover(
        _ModelProbe("model"),
        _make_plan("generalized_codegen_plan"),
    )

    assert discovery is not None
    assert discovery.selected_strategy_ids == (
        "generalized_creation_context_setup_codegen_creation",
        "generalized_no_overrides_codegen_creation",
        "generalized_overrides_codegen_creation",
        "general_creation_context_codegen_creation",
    )
    assert discovery.discovery_reason == "default_generalized_plan_codegen_creation_chain"


def test_generalized_codegen_creation_discovery_strategy_declines_non_generalized_plan() -> None:
    """The generalized phase-11 strategy should decline non-generalized planner output."""
    discovery = GeneralizedCodegenCreationDiscoveryStrategy().discover(
        _ModelProbe("model"),
        _make_plan("other_plan"),
    )

    assert discovery is None


def test_fallback_no_overrides_codegen_creation_discovery_strategy_returns_fallback_result() -> None:
    """The fallback phase-11 strategy should always return the no-overrides creation chain."""
    discovery = FallbackNoOverridesCodegenCreationDiscoveryStrategy().discover(
        _ModelProbe("model"),
        _make_plan("other_plan"),
    )

    assert discovery is not None
    assert discovery.selected_strategy_ids == (
        "generalized_no_overrides_codegen_creation",
    )
    assert discovery.discovery_reason == "fallback_no_overrides_creation_strategy"


def test_codegen_creation_discovery_strategy_builder_registers_default_strategies() -> None:
    """The phase-11 discovery builder should register the generalized and fallback strategies in order."""
    builder = CodegenCreationDiscoveryStrategyBuilder()

    assert builder.registered_strategy_names() == (
        "generalized_codegen_creation_discovery",
        "fallback_no_overrides_codegen_creation_discovery",
    )
    assert isinstance(
        builder.get_strategy("generalized_codegen_creation_discovery"),
        GeneralizedCodegenCreationDiscoveryStrategy,
    )
    assert isinstance(
        builder.get_strategy("fallback_no_overrides_codegen_creation_discovery"),
        FallbackNoOverridesCodegenCreationDiscoveryStrategy,
    )
    with pytest.raises(RuntimeError, match="missing strategy 'missing_creation_discovery'"):
        builder.get_strategy("missing_creation_discovery")


def test_codegen_creation_discovery_system_returns_first_claiming_strategy() -> None:
    """The phase-11 discovery facade should stop at the first claiming strategy."""
    first = _DiscoveryStrategyProbe(
        "first",
        CodegenCreationDiscovery(
            selected_strategy_ids=("a",),
            discovery_reason="claimed_by_first",
        ),
    )
    second = _DiscoveryStrategyProbe(
        "second",
        CodegenCreationDiscovery(
            selected_strategy_ids=("b",),
            discovery_reason="should_not_run",
        ),
    )
    system = CodegenCreationDiscoverySystem()
    system._strategy_builder = _DiscoveryStrategyBuilderProbe((first, second))
    model = _ModelProbe("model")
    plan = _make_plan("generalized_codegen_plan")

    discovery = system.discover(model, plan)

    assert discovery.selected_strategy_ids == ("a",)
    assert discovery.discovery_reason == "claimed_by_first"
    assert len(first.calls) == 1
    assert second.calls == []


def test_codegen_creation_discovery_system_skips_declining_strategy() -> None:
    """The phase-11 discovery facade should continue until a strategy claims the pair."""
    first = _DiscoveryStrategyProbe("first", None)
    second = _DiscoveryStrategyProbe(
        "second",
        CodegenCreationDiscovery(
            selected_strategy_ids=("b",),
            discovery_reason="claimed_by_second",
        ),
    )
    system = CodegenCreationDiscoverySystem()
    system._strategy_builder = _DiscoveryStrategyBuilderProbe((first, second))
    model = _ModelProbe("model")
    plan = _make_plan("other_plan")

    discovery = system.discover(model, plan)

    assert discovery.selected_strategy_ids == ("b",)
    assert discovery.discovery_reason == "claimed_by_second"
    assert first.calls == [(model, plan)]
    assert second.calls == [(model, plan)]


def test_codegen_creation_discovery_system_raises_when_no_strategy_claims_pair() -> None:
    """The phase-11 discovery facade should fail hard when no strategy claims the pair."""
    first = _DiscoveryStrategyProbe("first", None)
    second = _DiscoveryStrategyProbe("second", None)
    system = CodegenCreationDiscoverySystem()
    system._strategy_builder = _DiscoveryStrategyBuilderProbe((first, second))

    with pytest.raises(
            RuntimeError,
            match="could not select a creation discovery result",
    ):
        system.discover(_ModelProbe("model"), _make_plan("other_plan"))


def test_codegen_creation_discovery_system_cleanup_cleans_builder() -> None:
    """The phase-11 discovery facade should cleanup its owned builder and drop the reference."""
    builder = _DiscoveryStrategyBuilderProbe(())
    system = CodegenCreationDiscoverySystem()
    system._strategy_builder = builder

    system.cleanup()

    assert builder.cleanup_called is True
    assert not hasattr(system, "_strategy_builder")
