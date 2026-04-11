from typing import Dict, List
# Melder imports
from melder.spellbook.spell_crafter.validation.spell_validation_context import SpellValidationContext
from melder.spellbook.spell_crafter.validation.spell_validation_issue import SpellValidationIssue
from melder.spellbook.spell_crafter.validation.strategies.spell_validation_strategy import SpellValidationStrategy


class CircularDependencyStrategy(SpellValidationStrategy):
    """
    Detect circular dependency chains in the spell dependency graph.

    This uses the *Spellbook-level* view of dependencies:

        spell_id -> spell.dependencies (spell_id list)

    and looks for cycles reachable from the spell being validated.

    Contract:
    - Traverses the spellbook-wide dependency graph by spell/version id.
    - Reports only cycles reachable from the spell currently under validation.
    - Emits validation issues into the supplied context; it does not mutate the
      graph or try to break cycles automatically.
    """

    __slots__ = SpellValidationStrategy.__slots__

    def __init__(self) -> None:
        """
        Initialize the circular dependency strategy.

        Contract:
            Seeds the stable strategy name/description published through the
            validation pipeline.
        """
        super().__init__(
            name="circular_dependency",
            description="Detects cycles in the spell dependency graph.",
        )

    def validate(self, context: SpellValidationContext) -> None:
        """
        Detect circular dependency paths reachable from the current spell.

        Contract:
        - Stops early if the validation context has been cancelled.
        - Uses the spellbook-wide adjacency map as the source of dependency
          truth for this strategy.
        - Emits one `CIRCULAR_DEPENDENCY` issue when a reachable cycle is
          found.
        - Ignores dangling dependency ids here so the dedicated dangling
          dependency strategy can report them separately.
        """
        self.check_cleaned()

        cancel_event = context.cancel_event
        if cancel_event is not None and cancel_event.is_set:
            cancel_event.throw_if_set()

        spellbook = context.spellbook
        if spellbook is None:
            # Without a Spellbook, we cannot reason about global cycles.
            return

        # Build adjacency: version_id -> [dependency_ids...]
        adjacency: Dict[str, List[str]] = {}
        for spell_id, spell in spellbook._spell_id_pool.items():
            if cancel_event is not None and cancel_event.is_set:
                cancel_event.throw_if_set()

            deps: List[str] = spell.dependencies
            adjacency[spell_id] = list(deps) if deps else []

        root_id = context.spell.spell_index.current

        visited: set[str] = set()
        stack: set[str] = set()
        cycle_path: List[str] = []

        def dfs(node_id: str, path: List[str]) -> None:
            if node_id in stack:
                # Found a cycle; extract the cycle segment from the path.
                try:
                    start_idx = path.index(node_id)
                except ValueError:
                    # Should not happen, but be defensive.
                    start_idx = 0
                cycle_path.extend(path[start_idx:])
                return

            if node_id in visited:
                return

            visited.add(node_id)
            stack.add(node_id)

            for dep_id in adjacency.get(node_id, []):
                if cancel_event is not None and cancel_event.is_set:
                    cancel_event.throw_if_set()

                if dep_id not in adjacency:
                    # Dangling dependency – another strategy will handle it.
                    continue
                path.append(dep_id)
                dfs(dep_id, path)
                path.pop()
                if cycle_path:
                    return

            stack.remove(node_id)

        dfs(root_id, [root_id])

        if cycle_path:
            # Format as "A -> B -> C -> A"
            pretty = " -> ".join(cycle_path + [cycle_path[0]])
            context.issues.append(
                SpellValidationIssue(
                    severity="error",
                    code="CIRCULAR_DEPENDENCY",
                    message=(
                        f"Circular dependency detected starting from spell "
                        f"{context.spell.spell_name!r}: {pretty}."
                    ),
                    details={"cycle": list(cycle_path)},
                )
            )
