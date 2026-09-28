from typing import TYPE_CHECKING, Any, Dict, List



# Melder imports
from melder.aether.spellbook.spell_compiler.validation.spell_validation_issue import SpellValidationIssue
from melder.aether.spellbook.spell_compiler.validation.strategies.spell_validation_strategy import SpellValidationStrategy
if TYPE_CHECKING:
    from melder.aether.spellbook.spell_compiler.validation.spell_validation_context import SpellValidationContext


class SelfDependencyStrategy(SpellValidationStrategy):
    """
    Detect trivial self-dependencies (a spell depending on itself).

    This is always a configuration bug and is treated as an error.

    Contract:
    - Checks only for direct self-dependency, not longer dependency cycles.
    - Phase 3 records a parameter that resolves to the spell itself instead of
      aborting (2026-09-26), so this check is what refuses such a spell; the
      message names the parameter when the Phase-3 topology is available.
    - Emits validation issues into the supplied context; it does not mutate the
      dependency graph.

    Registration:
        MELDER KERNEL. A built-in strategy; registered, never bound.

    Subsystem Context:
        One built-in of the `validation/strategies` family, registered into
        `SpellValidationSystem`. Sibling to `CircularDependencyStrategy`, which
        catches the multi-hop cycles this one deliberately does not.

    System Context:
        Phase 4 (validation) of the conjure pipeline. Its error marks the spell
        broken and aborts conjure.

    AGENT_ACCESS: internal

    AGENT_PURPOSE:
        access: internal. Phase-4 strategy: emits one SELF_DEPENDENCY error if a spell's
        dependency list contains its own selected_spell_id. Direct self-dependency only, not
        longer cycles.
    """

    __slots__ = SpellValidationStrategy.__slots__

    def __init__(self) -> None:
        """
        Initialize the self-dependency strategy.

        Contract:
            Seeds the stable strategy name/description published through the
            validation pipeline.
        """
        super().__init__(
            name="self_dependency",
            description="Detects spells that directly depend on themselves.",
        )

    def validate(self, context: SpellValidationContext) -> None:
        """
        Detect whether the current spell directly depends on itself.

        Contract:
        - Stops early if the validation context has been cancelled.
        - Emits one `SELF_DEPENDENCY` error when the current spell id is found
          in its own dependency list. The message names the constructor
          parameter(s) that resolve to the spell when they are known
          (`_self_parameter_names`) and stays generic otherwise; `details` then
          also carries `parameter_names`.
        """
        self.check_cleaned()

        cancel_event = context.cancel_event
        if cancel_event is not None and cancel_event.is_set:
            cancel_event.throw_if_set()

        spell = context.spell
        deps: List[str] = spell.dependencies
        if not deps:
            return

        root_id = spell.spell_index.selected_spell_id
        if root_id is None:
            return
        if root_id in deps:
            names = self._self_parameter_names(context, root_id)
            if len(names) == 1:
                cause = f"its constructor parameter {names[0]!r} resolves to this same spell"
                fix = "Remove that parameter or give it a default."
            elif names:
                listed = ", ".join(repr(name) for name in names)
                cause = f"its constructor parameters {listed} resolve to this same spell"
                fix = "Remove those parameters or give them defaults."
            else:
                cause = "one of its constructor parameters resolves to this same spell"
                fix = "Remove that parameter or give it a default."
            details: Dict[str, Any] = {"spell_id": root_id}
            if names:
                details["parameter_names"] = list(names)
            context.issues.append(
                SpellValidationIssue(
                    severity="error",
                    code="SELF_DEPENDENCY",
                    message=f"Spell {spell.spell_name!r} depends on itself: {cause}. {fix}",
                    details=details,
                )
            )

    @staticmethod
    def _self_parameter_names(context: SpellValidationContext, root_id: str) -> List[str]:
        """
        Name the constructor parameters that resolved to the spell itself.

        Contract:
            - Reads the live spell's Phase-3 local topology, reachable when the
              context carries the spellbook, and returns the names of the sockets
              whose `target_spell_ids` include `root_id`, in constructor order.
            - Returns an empty list without a spellbook or without a topology
              (stand-in spells, or a dependency list set without Phase 3).

        Args:
            context: Validation context of the spell under validation.
            root_id: The spell's selected version id.

        Returns:
            List[str]: Parameter names that resolve to the spell itself.
        """
        if context.spellbook is None:
            return []
        spell = context.spell
        topology = spell._spell_system_states.get_local_topology(spell.spell_index)
        if topology is None:
            return []
        return [socket.param_name for socket in topology.iter_sockets() if root_id in socket.target_spell_ids]
