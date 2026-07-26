from typing import TYPE_CHECKING, Dict, List, Optional, Set, Tuple

if TYPE_CHECKING:
    from melder.aether.spellbook.spellbook import Spellbook
    from melder.aether.spellbook.spell_compiler.spell_requirements_finder.spell_parameter_requirements import (
        SpellParameterRequirement,
    )
    from melder.aether.spellbook.spell_compiler.validation.spell_validation_context import (
        SpellValidationContext,
    )
    from melder.utilities.synchronization.cancellation_event_signal import CancellationEvent



from melder.aether.conduit.meld.contracts.spell_contract import SpellContract
from melder.aether.conduit.meld.contracts.spell_map import SpellMap
from melder.aether.spellbook.spell_compiler.spell_requirements_finder.parameter_di_shape import (
    ParameterDIShape,
)
from melder.aether.spellbook.spell_compiler.validation.spell_validation_issue import (
    SpellValidationIssue,
)
from melder.aether.spellbook.spell_compiler.validation.strategies.spell_validation_strategy import (
    SpellValidationStrategy,
)
from melder.utilities.helpers.general_helpers import SpellInputUtils


class BindingResolutionCycleStrategy(SpellValidationStrategy):
    """
    Detect binding-key cycles implied by spell requirements.

    Purpose:
        Catch dependency loops that are not obvious from spell IDs but are
        visible when modeling resolution by binding keys.

    Contract:
        - Builds a binding-key graph from available requirements.
        - Reports cycles reachable from the spell under validation.
        - Does not mutate spells, spellbooks, or requirements.

    Registration:
        MELDER KERNEL. A built-in strategy; registered, never bound.

    Subsystem Context:
        A built-in of the `validation/strategies` family; the binding-KEY counterpart
        to `CircularDependencyStrategy` (which works at the spell-id level). Both are
        pass-cached.

    System Context:
        Phase 4 (validation) of the conjure pipeline. It models resolution by
        canonical binding key, catching cycles that only appear once
        SpellMap/SpellContract/annotation targets are normalized.

    AGENT_ACCESS: internal

    AGENT_PURPOSE:
        access: internal. Phase-4 strategy: builds a binding-KEY adjacency graph from the pool's
        Phase-1 requirements (pass-cached) and emits BINDING_RESOLUTION_CYCLE (error) per cycle
        reachable from the current spell's key. Catches loops invisible at the spell-id level.
    """

    __slots__ = SpellValidationStrategy.__slots__

    def __init__(self) -> None:
        """
        Initialize the binding resolution cycle strategy.
        """
        super().__init__(
            name="binding_resolution_cycle",
            description="Detects binding-key dependency cycles implied by requirements.",
        )

    def validate(self, context: SpellValidationContext) -> None:
        """
        Detect binding-key cycles reachable from the current spell.

        Purpose:
            Surface resolution loops that can cause re-entrancy during meld.
        Contract:
            - Scans available requirements to build a binding-key graph.
            - The graph is pass-invariant (a pure function of the pool's
              phase-1 requirements, which are frozen by the phase barrier
              before phase 4 starts), so it is built once per validation pass
              through `context.validation_pass_cache` and reused read-only by
              every spell validated in that pass. Single-spell paths carry no
              pass cache and build locally.
            - Emits at least one diagnostic per reachable cycle.
            - Skips validation if the spellbook is unavailable.
        Args:
            context: SpellValidationContext for the spell under validation.
        Returns:
            None.
        Raises:
            OperationCancelledError:
                If ``cancel_event`` is set during scanning or traversal.
        Threading:
            - Pass-cache publication is a single idempotent dict-key write;
              concurrent phase-4 workers may build the graph redundantly but
              always publish equal values, so the race is benign.
        """
        self.check_cleaned()

        cancel_event = context.cancel_event
        if cancel_event is not None and cancel_event.is_set:
            cancel_event.throw_if_set()

        spell = context.spell
        spellbook = context.spellbook
        if spell is None or spellbook is None:
            return

        root_key = spell.key

        pass_cache = context.validation_pass_cache
        binding_graph: Optional[
            Dict[Tuple[str, str], Set[Tuple[str, str]]]
        ] = None
        if pass_cache is not None:
            binding_graph = pass_cache.get("binding_resolution_graph")
        if binding_graph is None:
            binding_graph = self._build_binding_graph(spellbook, cancel_event)
            if pass_cache is not None:
                pass_cache["binding_resolution_graph"] = binding_graph

        cycles = self._detect_cycles(root_key, binding_graph, cancel_event)
        if not cycles:
            return

        cycle_key_set: Set[Tuple[str, str]] = set()
        for cycle in cycles:
            cycle_key_set.update(cycle)

        binding_to_spells: Dict[Tuple[str, str], List[str]] = {}
        for spell_id, spell_instance in spellbook._spell_id_pool.items():
            if cancel_event is not None and cancel_event.is_set:
                cancel_event.throw_if_set()
            spell_key = spell_instance.key
            if spell_key not in cycle_key_set:
                continue
            existing = binding_to_spells.get(spell_key)
            if existing is None:
                binding_to_spells[spell_key] = [spell_id]
            else:
                existing.append(spell_id)

        for cycle in cycles:
            cycle_keys = [self._format_key(key) for key in cycle]
            cycle_spells = {
                self._format_key(key): sorted(binding_to_spells.get(key, []))
                for key in cycle
            }
            context.issues.append(
                SpellValidationIssue(
                    severity="error",
                    code="BINDING_RESOLUTION_CYCLE",
                    message=(
                        f"Spell {spell.spell_name!r} participates in a binding resolution "
                        f"cycle: {' -> '.join(cycle_keys)}."
                    ),
                    details={
                        "spell_id": spell.spell_index.selected_spell_id,
                        "root_binding_key": self._format_key(root_key),
                        "cycle_keys": cycle_keys,
                        "cycle_spells": cycle_spells,
                    },
                )
            )

    def _build_binding_graph(
        self,
        spellbook: Spellbook,
        cancel_event: Optional[CancellationEvent],
    ) -> Dict[Tuple[str, str], Set[Tuple[str, str]]]:
        """
        Build the frame-wide binding-key adjacency graph from pool truth.

        Purpose:
            Model every spell's DI requirements as binding-key edges so cycle
            traversal can run per spell against one shared structure.
        Contract:
            - Pure read over `spellbook._spell_id_pool` and each spell's
              phase-1 requirements; mutates nothing on spells or spellbook.
            - Spell node keys come from `Spell.key`, the bind-time normalized
              canonical key, so no per-build re-normalization happens here.
            - The result is treated as immutable by all consumers; pass-cache
              reuse depends on that.
        Args:
            spellbook: Owning Spellbook whose local pool should be modeled.
            cancel_event: Optional cancellation signal checked per spell.
        Returns:
            Dict[Tuple[str, str], Set[Tuple[str, str]]]:
                Binding-key adjacency map.
        Raises:
            OperationCancelledError:
                If ``cancel_event`` is set during the pool sweep.
        """
        binding_graph: Dict[Tuple[str, str], Set[Tuple[str, str]]] = {}

        for spell_id, spell_instance in spellbook._spell_id_pool.items():
            if cancel_event is not None and cancel_event.is_set:
                cancel_event.throw_if_set()

            requirements = spell_instance.requirements
            if requirements is None:
                continue
            if requirements.cleaned:
                continue
            try:
                parameters = requirements.parameters
            except RuntimeError:
                continue

            spell_key = spell_instance.key
            adjacency: Optional[Set[Tuple[str, str]]] = None
            for param in parameters:
                target_key = self._binding_key_for_requirement(param)
                if target_key is None:
                    continue
                if adjacency is None:
                    adjacency = binding_graph.get(spell_key)
                    if adjacency is None:
                        adjacency = set()
                        binding_graph[spell_key] = adjacency
                adjacency.add(target_key)

        return binding_graph

    def _binding_key_for_requirement(
        self,
        requirement: SpellParameterRequirement,
    ) -> Optional[Tuple[str, str]]:
        """
        Map a parameter requirement to a binding key when applicable.

        Purpose:
            Normalize dependency requirements into canonical binding keys.
        Contract:
            - Returns None for non-DI parameters.
            - Uses SpellMap / SpellContract canonical keys.
        Args:
            requirement: SpellParameterRequirement to normalize.
        Returns:
            Optional[Tuple[str, str]]: Canonical binding key or None.
        """
        if requirement.di_shape is ParameterDIShape.SINGLE_BY_ANNOTATION:
            if requirement.annotation is None:
                return None
            return SpellInputUtils.normalize_spell_key(
                spellframe=requirement.annotation,
                binding_name=None,
            )

        if requirement.di_shape is ParameterDIShape.COLLECTION_BY_ANNOTATION:
            element = requirement.collection_element_annotation
            if element is None:
                return None
            return SpellInputUtils.normalize_spell_key(
                spellframe=element,
                binding_name=None,
            )

        if requirement.di_shape is ParameterDIShape.SPELLMAP_DEFAULT:
            spellmap = requirement.spellmap_default
            if not isinstance(spellmap, SpellMap):
                return None
            return spellmap.canonical_key

        if requirement.di_shape is ParameterDIShape.SPELL_CONTRACT:
            contract = requirement.default_value
            if not isinstance(contract, SpellContract):
                return None
            return contract.canonical_key

        return None

    def _detect_cycles(
        self,
        root_key: Tuple[str, str],
        graph: Dict[Tuple[str, str], Set[Tuple[str, str]]],
        cancel_event: Optional[CancellationEvent],
    ) -> List[List[Tuple[str, str]]]:
        """
        Detect cycles reachable from the root binding key.

        Purpose:
            Traverse binding-key edges and return any cycles encountered.
        Contract:
            - Returns a list of cycles, each represented as a list of keys.
            - Returns an empty list when no cycles are reachable.
        Args:
            root_key: Binding key for the spell under validation.
            graph: Binding-key adjacency map.
            cancel_event: Optional cancellation signal.
        Returns:
            list[list[tuple[str, str]]]: Detected cycles.
        """
        visited: Set[Tuple[str, str]] = set()
        stack: List[Tuple[str, str]] = []
        stack_index: Dict[Tuple[str, str], int] = {}
        cycles: List[List[Tuple[str, str]]] = []
        seen_cycles: Set[Tuple[Tuple[str, str], ...]] = set()

        def _walk(node_key: Tuple[str, str]) -> None:
            if cancel_event is not None and cancel_event.is_set:
                cancel_event.throw_if_set()

            if node_key in stack_index:
                start = stack_index[node_key]
                cycle = stack[start:] + [node_key]
                normalized = self._normalize_cycle(cycle)
                if normalized not in seen_cycles:
                    seen_cycles.add(normalized)
                    cycles.append(list(normalized))
                return

            if node_key in visited:
                return

            visited.add(node_key)
            stack_index[node_key] = len(stack)
            stack.append(node_key)

            for neighbor in graph.get(node_key, ()):
                _walk(neighbor)

            stack.pop()
            stack_index.pop(node_key, None)

        _walk(root_key)
        return cycles

    def _normalize_cycle(
        self,
        cycle: List[Tuple[str, str]],
    ) -> Tuple[Tuple[str, str], ...]:
        """
        Normalize a cycle so duplicate detection is stable.

        Purpose:
            Ensure cycle comparisons are independent of traversal order.
        Contract:
            - Produces a tuple representation starting at the smallest key.
            - Preserves the closing node to keep the cycle explicit.
        Args:
            cycle: Cycle list including the repeated start/end key.
        Returns:
            Tuple[Tuple[str, str], ...]: Normalized cycle representation.
        """
        if len(cycle) < 2:
            return tuple(cycle)

        trimmed = cycle[:-1]
        min_index = 0
        for idx in range(1, len(trimmed)):
            if trimmed[idx] < trimmed[min_index]:
                min_index = idx
        rotated = trimmed[min_index:] + trimmed[:min_index]
        rotated.append(rotated[0])
        return tuple(rotated)

    def _format_key(self, key: Tuple[str, str]) -> str:
        """
        Format a binding key for diagnostics.

        Purpose:
            Render a canonical binding key as a short string.
        Contract:
            - Always returns "frame_key:binding_key".
        Args:
            key: Canonical binding key tuple.
        Returns:
            str: Formatted key string.
        """
        return f"{key[0]}:{key[1]}"
