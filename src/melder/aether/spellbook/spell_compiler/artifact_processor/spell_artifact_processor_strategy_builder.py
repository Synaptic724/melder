from typing import Dict, Tuple

from melder.utilities.general_base.cleanable import Cleanable

from melder.aether.spellbook.spell_compiler.artifact_processor.spell_artifact_processor_strategy import (
    SpellArtifactProcessorStrategy,
)
from melder.aether.spellbook.spell_compiler.artifact_processor.strategies.spell_occurrence_contract_processor_strategy import (
    SpellOccurrenceContractProcessorStrategy,
)
from melder.aether.spellbook.spell_compiler.artifact_processor.strategies.spell_injection_processor_strategy import (
    SpellInjectionProcessorStrategy,
)
from melder.aether.spellbook.spell_compiler.artifact_processor.strategies.spell_existence_occurrence_processor_strategy import (
    SpellExistenceOccurrenceProcessorStrategy,
)
from melder.aether.spellbook.spell_compiler.artifact_processor.strategies.spell_occurrence_instance_processor_strategy import (
    SpellOccurrenceInstanceProcessorStrategy,
)
from melder.aether.spellbook.spell_compiler.artifact_processor.strategies.spell_occurrence_order_processor_strategy import (
    SpellOccurrenceOrderProcessorStrategy,
)
from melder.aether.spellbook.spell_compiler.artifact_processor.strategies.spell_override_targeting_processor_strategy import (
    SpellOverrideTargetingProcessorStrategy,
)
from melder.aether.spellbook.spell_compiler.artifact_processor.strategies.spell_runtime_processor_strategy import (
    SpellRuntimeProcessorStrategy,
)


class SpellArtifactProcessorStrategyBuilder(Cleanable):
    """
    Registry holder for processor strategies.

    Purpose:
        Own the default processor strategy objects keyed by stable strategy name
        so the processor can consume them later through explicit strategy-chain
        selection.

    Contract:
        - This object does not consume spells or artifacts.
        - This object does not build or return `SpellArtifactProcessor`.
        - It owns a single named strategy registry.
        - `_load_defaults()` populates the current built-in strategies into
          that registry.
        - Later compiler code can ask for strategies by name or ask for a
          deterministic ordered tuple of strategies for one processor chain.
    """

    __slots__ = Cleanable.__slots__ + [
        "_strategies_by_name",
    ]

    def __init__(self) -> None:
        """
        Build one empty processor strategy registry and load defaults.

        Contract:
            - The registry always starts empty before default loading.
            - Default strategy registration happens through `_load_defaults()`.
        """
        super().__init__()
        self._strategies_by_name: Dict[str, SpellArtifactProcessorStrategy] = {}
        self._load_defaults()

    def cleanup(self) -> None:
        """
        Clean up internal references.
        """
        if self._cleaned:
            return
        self._cleaned = True
        self._strategies_by_name.clear()
        del self._strategies_by_name

    def _load_defaults(self) -> None:
        """
        Populate the default processor strategy registry.

        Purpose:
            Keep the built-in processor strategy wiring in one explicit place
            instead of spreading that registration across processor call sites.

        Contract:
            - Clears and rebuilds the registry each time it runs.
            - Keys are the strategies' stable `strategy_id` values.
            - Current defaults are the 3 occurrence-derived processor
              strategies plus runtime, injection, and override-targeting
              fitting strategies.
            - Registration order is execution order.
        """
        order_strategy = SpellOccurrenceOrderProcessorStrategy()
        instance_strategy = SpellOccurrenceInstanceProcessorStrategy()
        contract_strategy = SpellOccurrenceContractProcessorStrategy()
        runtime_strategy = SpellRuntimeProcessorStrategy()
        existence_occurrence_strategy = SpellExistenceOccurrenceProcessorStrategy()
        injection_strategy = SpellInjectionProcessorStrategy()
        override_targeting_strategy = SpellOverrideTargetingProcessorStrategy()

        self._strategies_by_name[order_strategy.strategy_id] = order_strategy
        self._strategies_by_name[instance_strategy.strategy_id] = instance_strategy
        self._strategies_by_name[contract_strategy.strategy_id] = contract_strategy
        self._strategies_by_name[runtime_strategy.strategy_id] = runtime_strategy
        self._strategies_by_name[
            existence_occurrence_strategy.strategy_id
        ] = existence_occurrence_strategy
        self._strategies_by_name[injection_strategy.strategy_id] = injection_strategy
        self._strategies_by_name[
            override_targeting_strategy.strategy_id
        ] = override_targeting_strategy

    def get_strategy(
            self,
            strategy_name: str,
    ) -> SpellArtifactProcessorStrategy:
        """
        Return one registered processor strategy by stable name.

        Args:
            strategy_name:
                Stable strategy name / id.

        Returns:
            SpellArtifactProcessorStrategy:
                Registered processor strategy.

        Raises:
            RuntimeError:
                If no strategy is registered under that name.
        """
        strategy = self._strategies_by_name.get(strategy_name)
        if strategy is not None:
            return strategy
        raise RuntimeError(
            "SpellArtifactProcessorStrategyBuilder is missing strategy "
            f"'{strategy_name}'."
        )

    def get_strategies(
            self,
            strategy_names: Tuple[str, ...],
    ) -> Tuple[SpellArtifactProcessorStrategy, ...]:
        """
        Return a deterministic ordered tuple of strategies by stable name.

        Args:
            strategy_names:
                Ordered strategy names to resolve.

        Returns:
            Tuple[SpellArtifactProcessorStrategy, ...]:
                Ordered strategy tuple for later processor chaining.
        """
        return tuple(
            self.get_strategy(strategy_name)
            for strategy_name in strategy_names
        )

    def registered_strategy_names(self) -> Tuple[str, ...]:
        """
        Return the currently registered strategy names in deterministic order.

        Returns:
            Tuple[str, ...]:
                Registered strategy names in execution order.
        """
        return tuple(self._strategies_by_name.keys())
