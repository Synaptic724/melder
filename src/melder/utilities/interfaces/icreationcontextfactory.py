from typing import Optional, Protocol, runtime_checkable

from melder.aether.conduit.meld.creation_context.creation_context import CreationContext
from melder.utilities.interfaces.icleanable import ICleanable
@runtime_checkable
class ICreationContextFactory(ICleanable, Protocol):
    """
    Produce spell-shaped `CreationContext` instances.

    Purpose:
        Keep Meld front-door logic minimal by centralizing context construction
        behind one factory contract.

    Contract:
        - Factory does not own shared caches outside spell ownership.
        - Spell owns the context lifecycle through `spell._creation_context`.
        - Get-or-build path is lock-free and race-tolerant.
        - Factory delegates all shape rules to `CreationContextBuilder`.
        - In dynamic mode, the factory resolves /creates one spell-index gate
          and injects it into built contexts for runtime execution admission.
    """

    def build_for_spell(self, spell: "ISpell") -> CreationContext:
        """
        Build one fresh context for the spell without publishing it back onto
        the spell.

        Args:
            spell: Spell that conceptually owns the built context.

        Returns:
            CreationContext: New spell-shaped context ready for runtime use.
        """
        ...

    def build_and_bind_for_spell(self, spell: "ISpell") -> CreationContext:
        """
        Build one CreationContext and bind it onto the target spell.

        Contract:
            - Always builds a fresh context from the current spell state.
            - Replaces any existing spell-owned context reference.
            - Best-effort cleans replaced context.
            - Opens the spell-owned CounterSwitch latch after publish.
            - Does not use spell lock primitives.
        """
        ...

    def get_or_build_for_spell(self, spell: "ISpell") -> CreationContext:
        """
        Resolve one spell-owned context via spell-level CounterSwitch election.

        Contract:
            - Uses `spell._creation_context_switch.selector()` for one-leader
              get-or-build election.
            - Leader builds/publishes context and opens latch to state `2`.
            - Followers block while pending (`state == 1`) and then read cache.
            - Context ownership remains on Spell (`spell._creation_context`).
            - Does not use `spell._lock` for hot-path access/publication.
            - Does not inspect `CreationContext.is_cleaned`; switch state is
              treated as the single source of truth for readiness.
            - Single selector pass: no retry loops.

        Returns:
            CreationContext:
                Spell-owned cached or newly built context.
        """
        ...

    def rebuild_for_spell(self, spell: "ISpell") -> CreationContext:
        """
        Force rebuild and replace the spell-owned CreationContext.

        Contract:
            - Ignores existing context cache hit.
            - Useful for explicit runtime rebind flows.
        """
        ...

