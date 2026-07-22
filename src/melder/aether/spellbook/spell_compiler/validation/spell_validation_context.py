from typing import TYPE_CHECKING, Any, Dict, Optional, List, ClassVar

if TYPE_CHECKING:
    from melder.aether.spellbook.spell import Spell
    from melder.aether.spellbook.spellbook import Spellbook
    from melder.aether.spellbook.spell_compiler.profiles.resolution_profile import (
        SpellResolutionFrame,
    )
    from melder.aether.spellbook.spell_compiler.spell_requirements_finder.spell_requirements import (
        SpellRequirements,
    )
    from melder.aether.spellbook.spell_compiler.symbolic_graph.spell_symbolic_graph import (
        SpellSymbolicGraph,
    )
    from melder.utilities.synchronization.cancellation_event_signal import (
        CancellationEvent,
    )



# Melder imports
from melder.aether.spellbook.spell_compiler.validation.spell_validation_issue import (
    SpellValidationIssue,
)
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
    cancel_event:
        Optional cancellation token for long-running validations.
    issues:
        Shared, mutable list that all strategies append issues into.
    validation_pass_cache:
        Optional dict shared by every per-spell validation in one scheduler
        pass. Strategies may memoize pass-invariant artifacts here (for
        example the frame-wide binding graph). Entries must be treated as
        immutable once published; the dict's lifetime is exactly one pass,
        so no invalidation protocol exists or is needed. None on single-spell
        validation paths, where strategies fall back to local computation.

    Contract:
    - Holds one spell plus the validation artifacts already produced for that
      spell in earlier phases.
    - Strategies may read any field and append issues, but they do not own the
      shared issues list.
    - Optional artifact cleanup is controlled by `cleanup_artifacts`; the
      caller decides whether the context owns those artifacts for teardown.

    Registration:
        MELDER KERNEL - guarded. A compiler validation carrier; not user-bindable.

    Subsystem Context:
        The read-model of the `validation` package: `SpellValidationSystem` builds
        one per spell and passes it to every `SpellValidationStrategy`, which read
        its fields and append `SpellValidationIssue` into its shared issues list.

    System Context:
        Phase 4 (validation) of the conjure pipeline, after Phases 1-3 have
        produced the requirements, symbolic graph, and resolution frame. It
        carries those artifacts to the strategies but performs no validation itself.
    """
    __melder_internal__: ClassVar[object] = _mrg.sentinel
    __ast_helper_access__: str = "internal"
    __agent_purpose__: str = (
        "access: internal. Phase-4 per-spell validation context handed to each strategy: the "
        "spell, spellbook, and the Phase 1/2/3 artifacts, plus the shared mutable issues list "
        "and an optional pass-scoped memo cache. Strategies read fields and append issues; they "
        "do not own the list."
    )
    __slots__ = Cleanable.__slots__ + [
        "spell",
        "spellbook",
        "requirements",
        "symbolic_graph",
        "resolution_frame",
        "cancel_event",
        "issues",
        "validation_pass_cache",
        "_cleanup_artifacts",
    ]

    def __init__(
            self,
            spell: Spell,
            spellbook: Optional[Spellbook],
            requirements: Optional[SpellRequirements],
            symbolic_graph: Optional[SpellSymbolicGraph],
            resolution_frame: Optional[SpellResolutionFrame],
            cancel_event: Optional[CancellationEvent],
            issues: List['SpellValidationIssue'],
            cleanup_artifacts: bool = True,
            validation_pass_cache: Optional[Dict[str, Any]] = None,
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
            validation_pass_cache: Optional pass-scoped memo dict shared across
                all spells validated in one scheduler pass; None on
                single-spell paths.
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

        self.spell: Spell = spell
        self.spellbook: Optional[Spellbook] = spellbook
        self.requirements: Optional[SpellRequirements] = requirements
        self.symbolic_graph: Optional[SpellSymbolicGraph] = symbolic_graph
        self.resolution_frame: Optional[SpellResolutionFrame] = resolution_frame
        self.cancel_event: Optional[CancellationEvent] = cancel_event

        # NOTE: this list is shared with the caller (SpellValidationSystem);
        # cleanup must not mutate the underlying list contents.
        self.issues: List['SpellValidationIssue'] = issues
        self.validation_pass_cache: Optional[Dict[str, Any]] = validation_pass_cache
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
        del self.validation_pass_cache

        # Detach our reference to the shared issues list without mutating it.
        del self.issues

