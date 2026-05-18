from typing import Optional, List
# Melder imports
from melder.spellbook.spell_crafter.profiles.resolution_profile import (
    SpellResolutionFrame,
)
from melder.spellbook.spell_crafter.spell_requirements_finder.spell_requirements import (
    SpellRequirements,
)
from melder.spellbook.spell_crafter.symbolic_graph.spell_symbolic_graph import (
    SpellSymbolicGraph,
)
from melder.spellbook.spell_crafter.validation.spell_validation_issue import (
    SpellValidationIssue,
)
from melder.utilities.general_base.cleanable import Cleanable
from melder.utilities.interfaces.ispell import ISpell
from melder.utilities.interfaces.ispellbook import ISpellbook
from melder.utilities.synchronization.cancellation_event_signal import (
    CancellationEvent,
)
from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg

class SpellValidationContext(Cleanable):
    """
    Per-spell context passed to each validation strategy.

    This is intentionally rich and future-proof; strategies are free to use
    whichever parts they care about and ignore the rest.

    Attributes
    ----------
    spell:
        The spell being validated.
    spellbook:
        The owning Spellbook, if any (may be None).
    requirements:
        Phase 1 requirements artifact, if already computed.
    symbolic_graph:
        Phase 2 symbolic graph, if already computed.
    resolution_frame:
        Phase 3 resolution frame / DAG summary, if already computed.
    cancel_event:
        Optional cancellation token for long-running validations.
    issues:
        Shared, mutable list that all strategies append issues into.

    Contract:
    - Holds one spell plus the validation artifacts already produced for that
      spell in earlier phases.
    - Strategies may read any field and append issues, but they do not own the
      shared issues list.
    - Optional artifact cleanup is controlled by `cleanup_artifacts`; the
      caller decides whether the context owns those artifacts for teardown.
    """
    __melder_internal__ = _mrg.sentinel
    __slots__ = Cleanable.__slots__ + [
        "spell",
        "spellbook",
        "requirements",
        "symbolic_graph",
        "resolution_frame",
        "cancel_event",
        "issues",
        "_cleanup_artifacts",
    ]

    def __init__(
            self,
            spell: 'ISpell',
            spellbook: Optional['ISpellbook'],
            requirements: Optional['SpellRequirements'],
            symbolic_graph: Optional['SpellSymbolicGraph'],
            resolution_frame: Optional['SpellResolutionFrame'],
            cancel_event: Optional['CancellationEvent'],
            issues: List['SpellValidationIssue'],
            cleanup_artifacts: bool = True,
    ) -> None:
        """
        Initialize one per-spell validation context.

        Args:
            spell: Spell currently being validated.
            spellbook: Owning spellbook when available.
            requirements: Phase 1 requirements artifact when available.
            symbolic_graph: Phase 2 symbolic graph when available.
            resolution_frame: Phase 3 resolution frame when available.
            cancel_event: Optional cancellation signal for long-running
                validation.
            issues: Shared issue list that strategies append into.
            cleanup_artifacts: True when context cleanup should also clean owned
                artifact objects.
        Contract:
            - `spell` and `issues` are required.
            - Holds references only; it does not clone the incoming artifacts.
            - The shared `issues` list remains owned by the caller even when
              this context is cleaned.
        """
        super().__init__()

        if spell is None:
            raise ValueError("spell cannot be None.")
        if issues is None:
            raise ValueError("issues list cannot be None.")

        self.spell: Optional['ISpell'] = spell
        self.spellbook: Optional['ISpellbook'] = spellbook
        self.requirements: Optional['SpellRequirements'] = requirements
        self.symbolic_graph: Optional['SpellSymbolicGraph'] = symbolic_graph
        self.resolution_frame: Optional['SpellResolutionFrame'] = resolution_frame
        self.cancel_event: Optional['CancellationEvent'] = cancel_event

        # NOTE: this list is shared with the caller (SpellValidationSystem);
        # cleanup must not mutate the underlying list contents.
        self.issues: List['SpellValidationIssue'] = issues
        self._cleanup_artifacts: bool = cleanup_artifacts

    def cleanup(self) -> None:
        """
        Deterministically drop heavy references held by the context.

        Important:
            We deliberately **do not** clear ``issues`` here, because the
            caller (SpellValidationSystem) hands that list into the final
            SpellValidationResult. We only detach our own reference.
        """
        if self._cleaned:
            return

        # Clean up owned artifacts if requested.
        if self._cleanup_artifacts:
            for artifact in (self.requirements, self.symbolic_graph, self.resolution_frame):
                if isinstance(artifact, Cleanable):
                    try:
                        artifact.cleanup()
                    except Exception:
                        pass
        self._cleaned = True
        # Drop references to help GC.
        del self.spell
        del self.spellbook
        del self.requirements
        del self.symbolic_graph
        del self.resolution_frame
        del self.cancel_event

        # Detach our reference to the shared issues list without mutating it.
        del self.issues

