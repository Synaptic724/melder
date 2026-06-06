"""Direct unit tests for the phase-10 discovery seam."""

from typing import Optional, Tuple

import pytest

from melder.aether.spellbook.spell_compiler.codegen_planner.codegen_plan_discovery_system.codegen_plan_discovery import (
    CodegenPlanDiscovery,
)
from melder.aether.spellbook.spell_compiler.codegen_planner.codegen_plan_discovery_system.codegen_plan_discovery_strategy import (
    CodegenPlanDiscoveryStrategy,
)
from melder.aether.spellbook.spell_compiler.codegen_planner.codegen_plan_discovery_system.codegen_plan_discovery_strategy_builder import (
    CodegenPlanDiscoveryStrategyBuilder,
)
from melder.aether.spellbook.spell_compiler.codegen_planner.codegen_plan_discovery_system.codegen_plan_discovery_system import (
    CodegenPlanDiscoverySystem,
)
from melder.aether.spellbook.spell_compiler.codegen_planner.codegen_plan_discovery_system.strategies.generalized_codegen_plan_discovery_strategy import (
    GeneralizedCodegenPlanDiscoveryStrategy,
)


class _ModelProbe:
    """Minimal processor-model double for discovery tests."""

    def __init__(self, label: str) -> None:
        """Store one visible label for test assertions."""
        self.label = label


class _DiscoveryStrategyProbe(CodegenPlanDiscoveryStrategy):
    """Programmable discovery strategy double for facade tests."""

    def __init__(
            self,
            strategy_id: str,
            discovery: Optional[CodegenPlanDiscovery],
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
    ) -> Optional[CodegenPlanDiscovery]:
        """Record the model and return the programmed discovery result."""
        self.calls.append(spell_codegen_model)
        return self._discovery


class _DiscoveryStrategyBuilderProbe:
    """Minimal builder double for discovery-system tests."""

    def __init__(self, strategies: Tuple[CodegenPlanDiscoveryStrategy, ...]) -> None:
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
    ) -> Tuple[CodegenPlanDiscoveryStrategy, ...]:
        """Return the stored strategy tuple for the requested ids."""
        assert strategy_names == self.registered_strategy_names()
        return self._strategies


def test_generalized_codegen_plan_discovery_strategy_returns_generalized_result() -> None:
    """The default phase-10 discovery strategy should preserve the generalized selection result."""
    discovery = GeneralizedCodegenPlanDiscoveryStrategy().discover(
        _ModelProbe("model")
    )

    assert discovery is not None
    assert discovery.selected_strategy_id == "generalized_codegen_plan"
    assert discovery.discovery_reason == "default_generalized_model_native_strategy"


def test_codegen_plan_discovery_strategy_builder_registers_generalized_default() -> None:
    """The phase-10 discovery strategy builder should expose the generalized strategy by default."""
    builder = CodegenPlanDiscoveryStrategyBuilder()

    assert builder.registered_strategy_names() == (
        "generalized_codegen_plan_discovery",
    )
    strategy = builder.get_strategy("generalized_codegen_plan_discovery")
    assert isinstance(strategy, GeneralizedCodegenPlanDiscoveryStrategy)
    with pytest.raises(RuntimeError, match="missing strategy 'missing_plan_discovery'"):
        builder.get_strategy("missing_plan_discovery")


def test_codegen_plan_discovery_strategy_builder_get_strategies_preserves_order() -> None:
    """The phase-10 discovery builder should preserve requested discovery order."""
    builder = CodegenPlanDiscoveryStrategyBuilder()

    strategies = builder.get_strategies(
        ("generalized_codegen_plan_discovery",)
    )

    assert len(strategies) == 1
    assert isinstance(strategies[0], GeneralizedCodegenPlanDiscoveryStrategy)


def test_codegen_plan_discovery_system_returns_first_claiming_strategy() -> None:
    """The phase-10 discovery facade should stop at the first claiming strategy."""
    first = _DiscoveryStrategyProbe(
        "first",
        CodegenPlanDiscovery(
            selected_strategy_id="strategy_a",
            discovery_reason="claimed_by_first",
        ),
    )
    second = _DiscoveryStrategyProbe(
        "second",
        CodegenPlanDiscovery(
            selected_strategy_id="strategy_b",
            discovery_reason="should_not_run",
        ),
    )
    system = CodegenPlanDiscoverySystem()
    system._strategy_builder = _DiscoveryStrategyBuilderProbe((first, second))

    discovery = system.discover(_ModelProbe("model"))

    assert discovery.selected_strategy_id == "strategy_a"
    assert discovery.discovery_reason == "claimed_by_first"
    assert len(first.calls) == 1
    assert second.calls == []


def test_codegen_plan_discovery_system_skips_declining_strategy() -> None:
    """The phase-10 discovery facade should continue until a strategy claims the model."""
    first = _DiscoveryStrategyProbe("first", None)
    second = _DiscoveryStrategyProbe(
        "second",
        CodegenPlanDiscovery(
            selected_strategy_id="strategy_b",
            discovery_reason="claimed_by_second",
        ),
    )
    system = CodegenPlanDiscoverySystem()
    system._strategy_builder = _DiscoveryStrategyBuilderProbe((first, second))
    model = _ModelProbe("model")

    discovery = system.discover(model)

    assert discovery.selected_strategy_id == "strategy_b"
    assert discovery.discovery_reason == "claimed_by_second"
    assert first.calls == [model]
    assert second.calls == [model]


def test_codegen_plan_discovery_system_raises_when_no_strategy_claims_model() -> None:
    """The phase-10 discovery facade should fail hard when no strategy claims the model."""
    first = _DiscoveryStrategyProbe("first", None)
    second = _DiscoveryStrategyProbe("second", None)
    system = CodegenPlanDiscoverySystem()
    system._strategy_builder = _DiscoveryStrategyBuilderProbe((first, second))

    with pytest.raises(
            RuntimeError,
            match="could not select a plan discovery result",
    ):
        system.discover(_ModelProbe("model"))


def test_codegen_plan_discovery_system_cleanup_cleans_builder() -> None:
    """The phase-10 discovery facade should cleanup its owned builder and drop the reference."""
    builder = _DiscoveryStrategyBuilderProbe(())
    system = CodegenPlanDiscoverySystem()
    system._strategy_builder = builder

    system.cleanup()

    assert builder.cleanup_called is True
    assert not hasattr(system, "_strategy_builder")
