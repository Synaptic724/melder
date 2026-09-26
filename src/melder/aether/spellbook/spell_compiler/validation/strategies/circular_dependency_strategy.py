from typing import Dict, List, Optional

from typing import TYPE_CHECKING



# Melder imports
from melder.aether.spellbook.spell_compiler.validation.spell_validation_issue import SpellValidationIssue
from melder.aether.spellbook.spell_compiler.validation.strategies.spell_validation_strategy import SpellValidationStrategy
from melder.utilities.helpers.general_helpers import SpellInputUtils
if TYPE_CHECKING:
    from melder.aether.spellbook.spell_compiler.validation.spell_validation_context import SpellValidationContext


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
    - Words the issue for what the spell is (2026-09-26): a cycle member is told
      it is part of the cycle; a spell that only reaches a cycle is told which of
      its dependencies leads there and that it is not part of that cycle. Either
      way the spell is refused and `details["cycle"]` holds the cycle ids.

    Registration:
        MELDER KERNEL. A built-in strategy; registered, never bound.

    Subsystem Context:
        A built-in of the `validation/strategies` family; the multi-hop counterpart
        to `SelfDependencyStrategy`, and it leaves dangling ids to
        `DanglingDependenciesStrategy`.

    System Context:
        Phase 4 (validation) of the conjure pipeline. It reuses
        `validation_pass_cache` so one adjacency build serves the whole scheduler
        pass.

    AGENT_ACCESS: internal

    AGENT_PURPOSE:
        access: internal. Phase-4 strategy: DFS over the spellbook-wide dependency adjacency
        (pass-cached) from the current spell; emits CIRCULAR_DEPENDENCY (error) with the cycle
        path when a reachable cycle is found. Ignores dangling ids.
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
          found. The message names the cycle; for a spell outside the cycle it
          also names the spell's direct dependency on the route to it (see
          `_cycle_message`). `details` carries the cycle ids in both cases.
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

        # Pass-scoped memo: dependencies are final once the phase-3 group
        # barrier drops, so the frame adjacency is pass-invariant during the
        # validation group and one build serves every spell (mirrors the
        # binding-graph memo). Without a pass cache (deferred single-spell
        # paths) the adjacency is built fresh, identical to the old scan.
        pass_cache = context.validation_pass_cache
        adjacency: Optional[Dict[str, List[str]]] = None
        if pass_cache is not None:
            adjacency = pass_cache.get("circular_dependency_adjacency")
        if adjacency is None:
            adjacency = {}
            for spell_id, spell in spellbook._spell_id_pool.items():
                if cancel_event is not None and cancel_event.is_set:
                    cancel_event.throw_if_set()

                deps: List[str] = spell.dependencies
                adjacency[spell_id] = list(deps) if deps else []
            if pass_cache is not None:
                pass_cache["circular_dependency_adjacency"] = adjacency

        root_id = context.spell.spell_index.selected_spell_id
        if root_id is None:
            root_id = context.spell.spell_id

        visited: set[str] = set()
        stack: set[str] = set()
        cycle_path: List[str] = []
        # Path nodes before the cycle starts: empty when the spell is in the
        # cycle, otherwise the spell followed by any intermediates.
        route: List[str] = []

        def dfs(node_id: str, path: List[str]) -> None:
            if node_id in stack:
                # Found a cycle; extract the cycle segment from the path.
                try:
                    start_idx = path.index(node_id)
                except ValueError:
                    # Should not happen, but be defensive.
                    start_idx = 0
                cycle_path.extend(path[start_idx:])
                route.extend(path[:start_idx])
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
            # `cycle_path` already closes the loop ("A -> B -> A"): the node that
            # closes it was appended before the recursion that found it. Name
            # every member; an id appears only for a spell the book cannot name.
            pool = spellbook._spell_id_pool
            cycle_names = [
                SpellInputUtils.describe_spell_id(spell_id, pool) for spell_id in cycle_path
            ]
            lead_name: Optional[str] = None
            lead_in_cycle = False
            if route:
                # The spell is outside the cycle and reaches it through its direct
                # dependency on the route: the cycle's first node when the route is
                # only the spell, otherwise the first intermediate.
                lead_in_cycle = len(route) == 1
                lead_id = cycle_path[0] if lead_in_cycle else route[1]
                lead_name = SpellInputUtils.describe_spell_id(lead_id, pool)
            context.issues.append(
                SpellValidationIssue(
                    severity="error",
                    code="CIRCULAR_DEPENDENCY",
                    message=self._cycle_message(
                        context.spell.spell_name, cycle_names, lead_name, lead_in_cycle
                    ),
                    details={"cycle": list(cycle_path)},
                )
            )

    @staticmethod
    def _cycle_message(
        spell_name: str,
        cycle_names: List[str],
        lead_name: Optional[str],
        lead_in_cycle: bool,
    ) -> str:
        """
        Word the CIRCULAR_DEPENDENCY message for a cycle member or a cycle consumer.

        Purpose:
            Every spell from which a cycle is reachable is refused, whether or not
            it is in the cycle. The message says which case applies so the user
            fixes the cycle rather than a spell that only uses it.

        Contract:
            - Pure; formats text only.
            - `lead_name` None: the spell is a cycle member and gets the member
              wording ("is part of a dependency cycle").
            - Otherwise the spell is a consumer: the message names its direct
              dependency on the route ("which is part of a dependency cycle" when
              that dependency is a member, "which depends on itself" when it is a
              self-loop, "which depends on a dependency cycle" when it is an
              intermediate), says how to break the cycle, and states that the
              spell itself is not part of that cycle.
            - A self-loop is a two-entry cycle ("'Node' -> 'Node'"); its fix names
              the loop spell.

        Args:
            spell_name: Name of the spell under validation (quoted here).
            cycle_names: Display names of the cycle path, already quoted by
                `SpellInputUtils.describe_spell_id`, first node repeated last.
            lead_name: Quoted display name of the spell's direct dependency on the
                route to the cycle, or None when the spell is in the cycle.
            lead_in_cycle: True when `lead_name` is itself a cycle member.

        Returns:
            str: The user-facing issue message.
        """
        pretty = " -> ".join(cycle_names)
        if lead_name is None:
            return (
                f"Spell {spell_name!r} is part of a dependency cycle: {pretty}. Melder cannot "
                "build any spell in the cycle; remove one of these constructor dependencies "
                "or give that parameter a default."
            )
        self_loop = len(cycle_names) == 2
        if lead_in_cycle and self_loop:
            needs = f"it needs {lead_name}, which depends on itself ({pretty})"
        elif lead_in_cycle:
            needs = f"it needs {lead_name}, which is part of a dependency cycle: {pretty}"
        else:
            needs = f"it needs {lead_name}, which depends on a dependency cycle: {pretty}"
        if self_loop:
            fix = (
                f"Fix {cycle_names[0]} (remove that constructor dependency or give that "
                "parameter a default)"
            )
        else:
            fix = (
                "Break that cycle (remove one of those constructor dependencies or give that "
                "parameter a default)"
            )
        return (
            f"Spell {spell_name!r} cannot be built: {needs}. {fix}; "
            f"{spell_name!r} itself is not part of that cycle."
        )
