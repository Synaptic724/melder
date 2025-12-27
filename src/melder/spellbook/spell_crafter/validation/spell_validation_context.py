from typing import Optional, List
# Melder imports
from melder.utilities.general_base.cleanable import Cleanable
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
    scanner:
        Convenience SpellbookScanner bound to ``spellbook`` (or None).
    cancel_event:
        Optional cancellation token for long-running validations.
    issues:
        Shared, mutable list that all strategies append issues into.
    """
    __melder_internal__ = _mrg.sentinel
    __slots__ = Cleanable.__slots__ + [
        "spell",
        "spellbook",
        "requirements",
        "symbolic_graph",
        "resolution_frame",
        "scanner",
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
            scanner: Optional['SpellbookScanner'],
            cancel_event: Optional['CancellationEvent'],
            issues: List['SpellValidationIssue'],
            cleanup_artifacts: bool = True,
    ) -> None:
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
        self.scanner: Optional['SpellbookScanner'] = scanner
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

        # Clean up scanner if we created one.
        if self.scanner is not None:
            try:
                self.scanner.cleanup()
            except Exception:
                pass

        # Clean up owned artifacts if requested.
        if self._cleanup_artifacts:
            for artifact in (self.requirements, self.symbolic_graph, self.resolution_frame):
                if isinstance(artifact, Cleanable):
                    try:
                        artifact.cleanup()
                    except Exception:
                        pass

        # Drop references to help GC.
        self.spell = None
        self.spellbook = None
        self.requirements = None
        self.symbolic_graph = None
        self.resolution_frame = None
        self.scanner = None
        self.cancel_event = None

        # Detach our reference to the shared issues list without mutating it.
        self.issues = None

        self._cleaned = True
