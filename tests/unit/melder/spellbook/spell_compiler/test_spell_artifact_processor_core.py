"""Direct unit tests for the artifact processor facade, builder, and model."""

from types import SimpleNamespace
from typing import Any, Dict, List, Optional, Tuple

import pytest

from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spell_compiler.artifact_processor.spell_artifact_processor import (
    SpellArtifactProcessor,
)
from melder.aether.spellbook.spell_compiler.artifact_processor.spell_artifact_processor_strategy_builder import (
    SpellArtifactProcessorStrategyBuilder,
)
from melder.aether.spellbook.spell_compiler.artifact_processor.spell_codegen_model import (
    SpellCodegenModel,
)


class _PathRegistryProbe:
    """Minimal path-registry double exposing root id and depth lookups."""

    def __init__(self, depths: Dict[int, int]) -> None:
        """Store deterministic path depths by path id."""
        self.root_path_id = 0
        self._depths = depths

    def depth(self, path_id: int) -> int:
        """Return the configured depth for the supplied path id."""
        return self._depths[path_id]


class _OccurrenceGraphProbe:
    """Minimal occurrence graph analysis double for processor-shell tests."""

    def __init__(self) -> None:
        """Populate one deterministic occurrence graph."""
        self.occurrence_count = 4
        self.root_spell_id = "spell-1"
        self.path_registry = _PathRegistryProbe(
            {
                0: 0,
                1: 1,
                2: 1,
                3: 2,
            }
        )
        self.occurrence_graph = {
            ("spell-1", 0): {"dep": [("dep-1", 1), ("dep-2", 2)]},
            ("dep-1", 1): {},
            ("dep-2", 2): {"leaf": [("leaf", 3)]},
            ("leaf", 3): {},
        }


class _CleanupTracker:
    """Simple cleanup double recording whether cleanup was invoked."""

    def __init__(self) -> None:
        """Start with cleanup not yet called."""
        self.cleanup_called = False

    def cleanup(self) -> None:
        """Record one cleanup call."""
        self.cleanup_called = True


class _ProcessorStrategyProbe:
    """Minimal processor strategy double used by facade tests."""

    def __init__(
            self,
            strategy_id: str,
            events: List[str],
    ) -> None:
        """Store the stable strategy id and the shared event sink."""
        self.strategy_id = strategy_id
        self._events = events

    def process(
            self,
            spell: Any,
            artifact: Any,
            model: SpellCodegenModel,
    ) -> None:
        """Record strategy execution and mutate one visible model field."""
        _ = spell
        _ = artifact
        self._events.append(self.strategy_id)
        model.assessment[self.strategy_id] = True


class _ProcessorBuilderProbe:
    """Minimal builder double for processor facade tests."""

    def __init__(
            self,
            strategies: Tuple[Any, ...],
    ) -> None:
        """Store the ordered strategy tuple for later resolution."""
        self._strategies = strategies
        self.requested_strategy_ids: Tuple[str, ...] = ()
        self.cleanup_called = False

    def cleanup(self) -> None:
        """Record one cleanup call."""
        self.cleanup_called = True

    def registered_strategy_names(self) -> Tuple[str, ...]:
        """Return the configured strategy ids in order."""
        return tuple(strategy.strategy_id for strategy in self._strategies)

    def get_strategies(
            self,
            strategy_ids: Tuple[str, ...],
    ) -> Tuple[Any, ...]:
        """Return the configured strategies and record the requested ids."""
        self.requested_strategy_ids = strategy_ids
        return self._strategies


def test_spell_artifact_processor_builder_registers_default_order() -> None:
    """The real processor builder should expose the stable default registry order."""
    builder = SpellArtifactProcessorStrategyBuilder()

    assert builder.registered_strategy_names() == (
        "spell_occurrence_order_processor",
        "spell_occurrence_instance_processor",
        "spell_occurrence_contract_processor",
        "spell_runtime_processor",
        "spell_injection_processor",
        "spell_override_targeting_processor",
        "spell_mutation_targeting_processor",
    )
    with pytest.raises(RuntimeError, match="missing strategy 'missing_processor'"):
        builder.get_strategy("missing_processor")


def test_build_model_shell_uses_existing_creation_route_family() -> None:
    """Existing-creation spells should map to the existing-creation route family."""
    graph_shape = _OccurrenceGraphProbe()
    artifact = SimpleNamespace(_occurrence_graph_analysis=graph_shape)
    spell = SimpleNamespace(
        is_existing_creation=True,
        existence=Existence.unique_per_conduit,
    )

    model = SpellArtifactProcessor._build_model_shell(
        spell=spell,
        artifact=artifact,
    )

    assert model.build_kind == "existing_creation"
    assert model.existence is None
    assert model.route_family == "existing_creation"
    assert model.node_count == 4
    assert model.root_dependency_count == 2
    assert model.max_depth == 2
    assert model.max_width == 2


def test_spell_artifact_processor_process_publishes_model_and_cleans_previous() -> None:
    """The processor facade should publish the new model and cleanup the superseded one."""
    events: List[str] = []
    processor = SpellArtifactProcessor()
    processor._strategy_builder = _ProcessorBuilderProbe(
        (
            _ProcessorStrategyProbe("first", events),
            _ProcessorStrategyProbe("second", events),
        )
    )
    previous_model = _CleanupTracker()
    artifact = SimpleNamespace(
        _spell_codegen_model=previous_model,
        _occurrence_graph_analysis=_OccurrenceGraphProbe(),
    )
    spell = SimpleNamespace(
        is_existing_creation=False,
        existence=Existence.unique_per_conduit,
    )

    processor.process(spell, artifact)

    model = artifact._spell_codegen_model
    assert isinstance(model, SpellCodegenModel)
    assert processor._strategy_builder.requested_strategy_ids == ("first", "second")
    assert events == ["first", "second"]
    assert model.assessment["processor_ready"] is True
    assert model.assessment["strategy_count"] == 2
    assert model.assessment["applied_strategy_ids"] == ("first", "second")
    assert model.applied_strategy_ids == ["first", "second"]
    assert previous_model.cleanup_called is True


def test_spell_codegen_model_cleanup_cleans_owned_sections_only() -> None:
    """Model cleanup should clean owned sections but leave borrowed graph truth alone."""
    graph_shape = _CleanupTracker()
    order_shape = _CleanupTracker()
    instance_shape = _CleanupTracker()
    contract_shape = _CleanupTracker()
    injection_shape = _CleanupTracker()
    override_targeting_shape = _CleanupTracker()
    mutation_targeting_shape = _CleanupTracker()
    spell_runtime_shape = _CleanupTracker()
    model = SpellCodegenModel(
        build_kind="construct",
        existence=Existence.unique_per_conduit,
        route_family="unique_per_conduit",
        graph_shape=graph_shape,
        order_shape=order_shape,
        instance_shape=instance_shape,
        contract_shape=contract_shape,
        injection_shape=injection_shape,
        override_targeting_shape=override_targeting_shape,
        mutation_targeting_shape=mutation_targeting_shape,
        spell_runtime_shape=spell_runtime_shape,
    )

    assert model.section_names() == (
        "graph_shape",
        "order_shape",
        "instance_shape",
        "contract_shape",
        "injection_shape",
        "override_targeting_shape",
        "mutation_targeting_shape",
        "spell_runtime_shape",
        "assessment",
    )

    model.cleanup()

    assert graph_shape.cleanup_called is False
    assert order_shape.cleanup_called is True
    assert instance_shape.cleanup_called is True
    assert contract_shape.cleanup_called is True
    assert injection_shape.cleanup_called is True
    assert override_targeting_shape.cleanup_called is True
    assert mutation_targeting_shape.cleanup_called is True
    assert spell_runtime_shape.cleanup_called is True
    assert not hasattr(model, "assessment")
