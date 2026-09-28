"""Rare-path ownership of shared context input replacement and publication."""

from collections.abc import Iterable
from typing import TYPE_CHECKING, Optional, Self

from melder.utilities.general_base.cleanable import Cleanable

if TYPE_CHECKING:
    from types import TracebackType
    from melder.aether.spellbook.spell import Spell
    from melder.utilities.synchronization.creation_gate import CreationGate


class CreationContextRebuild(Cleanable):
    """Hold an affected set of index gates through rebuild or explicit abort.

    Purpose:
        A conduit-local rebuild (structural, resolution or deferred phases)
        replaces a spell's phase-11 plan and resets its shared CreationContext
        while other conduits may be melding the same spell. This window makes
        that safe: no admitted meld is using the old context or plan when the
        phases replace them, and no meld reads the gap between Phase 5 clearing
        the plan and Phase 11 republishing it (2026-09-26 flake: "Cannot build
        CreationContext before spell_codegen_creation exists" and use of a
        cleaned context).

    Contract:
        Gate transition locks serialize only overlapping producers. They are
        acquired by stable index id before any gate is frozen, then admission
        is frozen and existing readers/builders drain before input mutation.
        Ordinary admission remains lock-free. Phase workers borrow this
        enclosing authority and must not acquire the held gate locks again.

        The retained Spell tuple and gate/posture ledger are required to release
        exactly the resources acquired by this operation, even when publication
        changes live fields. They are not copies of runtime graph or policy data.

        Successful exit publishes contexts from completed inputs before the
        gates reopen. A spell without a present plan is left unpublished for
        its next meld's normal validation path. Failure preserves its cause for
        unpublished contexts and wakes pending selectors. The original
        exception is never suppressed.

    Lock order:
        Enter this window BEFORE taking `spell._lock`. A dynamic meld holds its
        index ticket while an `Existence.unique` build takes the spell lock
        (2026-09-25 slot guards), so draining tickets while holding the spell
        lock would wait for a reader that waits for the producer. Callers must
        not hold a ticket on an affected gate (they would drain themselves);
        Meld runs every producer before it admits.

    Ownership:
        Borrows Spells and gates; owns only its one-operation resource ledger.
        Cleanup reopens only gates this operation found enabled, releases locks
        in reverse order, and drops borrowed references. It never cleans a gate.
    """

    __slots__ = ("_spells", "_held_gates", "_finalize_contexts")

    def __init__(
            self,
            spells: Iterable[Spell],
            *,
            finalize_contexts: bool = True,
    ) -> None:
        """Capture one deduplicated affected set and an initially empty lease ledger."""
        super().__init__()
        self._spells = tuple(dict.fromkeys(spells))
        self._held_gates: list[tuple[CreationGate, bool]] = []
        self._finalize_contexts = finalize_contexts

    def cleanup(self) -> None:
        """Restore prior admission posture and release every borrowed lock once."""
        if self._cleaned:
            return
        self._cleaned = True
        while self._held_gates:
            gate, was_enabled = self._held_gates.pop()
            try:
                if was_enabled and not gate.is_closed():
                    gate.open()
            finally:
                gate._lock.release()
        del self._held_gates
        del self._spells
        del self._finalize_contexts

    def __enter__(self) -> Self:
        """Reserve ordered producer ownership, freeze entrances and drain readers.

        An acquisition/drain exception unwinds the already-acquired resources
        before propagating. No phase state has been changed at this point.
        """
        self.check_cleaned()
        gates = {
            spell.spell_index.id: spell._creation_gate
            for spell in self._spells
            if spell._creation_gate is not None
        }
        try:
            for index_id in sorted(gates):
                gate = gates[index_id]
                gate._lock.acquire()
                self._held_gates.append((gate, gate.enabled))
            for gate, _ in self._held_gates:
                gate.close()
            for gate, _ in self._held_gates:
                # 1 ms poll: this is the rare rebuild path, and the default
                # 100 ms step made every contended rebuild wait a whole step
                # (measured 2026-09-26: concurrency file 1.05 s -> 1.98 s).
                gate.close_and_drain(interval=0.001)
            for spell in self._spells:
                spell._creation_context_failure = None
            return self
        except BaseException:
            # Resource unwinding, not error recovery: cancellation and ordinary
            # failures must both release the producer locks before propagating.
            self.cleanup()
            raise

    def __exit__(
            self,
            exc_type: Optional[type[BaseException]],
            exc_value: Optional[BaseException],
            traceback: Optional[TracebackType],
    ) -> None:
        """Publish completed inputs or record failure, then release producer ownership."""
        try:
            if exc_value is not None:
                self._abort(exc_value)
            elif self._finalize_contexts:
                try:
                    self._publish_completed_contexts()
                except BaseException as error:
                    self._abort(error)
                    raise
        finally:
            self.cleanup()

    def _publish_completed_contexts(self) -> None:
        """
        Publish a context for each affected spell whose phase-11 plan is present.

        Contract:
            - Runs before the gates reopen, so the first meld admitted after the
              window finds a ready context instead of electing a builder.
            - Skips spells without a factory and spells that still hold a
              context (the window did not reset them).
            - A constructed spell without a phase-11 plan (only structural
              phases ran, or resolution stopped on a validation error) is left
              unpublished; its next meld runs the normal validation path. It is
              NOT marked resolution_required: that routes the deferred 8-11
              lane, which cannot compile a spell without a Phase-5 blueprint.
            - Resolution flags stay with the producers that ran the phases.

        Raises:
            RuntimeError:
                Propagated from the factory when a present plan cannot build.
        """
        for spell in self._spells:
            factory = spell._creation_context_factory
            if factory is None or spell._creation_context is not None:
                continue
            if (
                    not spell.is_existing_creation
                    and spell._compiler_artifact._spell_codegen_creation is None
            ):
                continue
            factory.get_or_build_for_spell(spell)

    def _abort(self, error: BaseException) -> None:
        """Expose failure without leaving an unpublished Spell permanently pending."""
        for spell in self._spells:
            if spell._creation_context is not None:
                continue
            spell._creation_context_failure = error
            switch = spell._creation_context_switch
            state = switch.state
            if state:
                switch.advance(-state)
