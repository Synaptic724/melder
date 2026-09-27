"""September plan, part 2: rebuild window, Meld producers and admitted dynamic doors (2026-09-26).

Usage: python apply_sept_window_doors.py <repo_root>
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from patch_util import replace_block

root = pathlib.Path(sys.argv[1])
rebuild = root / "src/melder/aether/conduit/meld/creation_context/creation_context_rebuild.py"
meld = root / "src/melder/aether/conduit/meld/meld.py"
conduit_meld = root / "src/melder/aether/conduit/meld/conduit_meld.py"
spellspace_meld = root / "src/melder/aether/conduit/meld/spellspace_meld.py"

# ---------------------------------------------------------------- CreationContextRebuild
replace_block(rebuild,
'''    """Hold an affected set of index gates through rebuild or explicit abort.

    Contract:
        Gate transition locks serialize only overlapping producers. They are
        acquired by stable index id before any gate is frozen, then admission
        is frozen and existing readers/builders drain before input mutation.
        Ordinary admission remains lock-free. Phase workers borrow this
        enclosing authority and must not acquire the held gate locks again.

        The retained Spell tuple and gate/posture ledger are required to release
        exactly the resources acquired by this operation, even when publication
        changes live fields. They are not copies of runtime graph or policy data.

        Successful exit publishes contexts from completed inputs. Invalidated
        dependencies whose plans were not rebuilt become explicitly deferred.
        Failure preserves its cause for unpublished contexts and wakes pending
        selectors. The original exception is never suppressed.''',
'''    """Hold an affected set of index gates through rebuild or explicit abort.

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
        Meld runs every producer before it admits.''')
replace_block(rebuild,
'''    def _publish_completed_contexts(self) -> None:
        """Publish usable replacements; leave unplanned dependencies explicitly deferred."""
        for spell in self._spells:
            factory = spell._creation_context_factory
            if factory is None or spell._creation_context is not None:
                continue
            if (
                    not spell.is_existing_creation
                    and spell._compiler_artifact._spell_codegen_creation is None
            ):
                spell.resolution_required = True
                spell.resolution_complete = False
                continue
            factory.get_or_build_for_spell(spell)
            spell.resolution_required = False
            spell.resolution_complete = True''',
'''    def _publish_completed_contexts(self) -> None:
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
            factory.get_or_build_for_spell(spell)''')

replace_block(rebuild,
"""            for gate, _ in self._held_gates:
                gate.close_and_drain()""",
"""            for gate, _ in self._held_gates:
                # 1 ms poll: this is the rare rebuild path, and the default
                # 100 ms step made every contended rebuild wait a whole step
                # (measured 2026-09-26: concurrency file 1.05 s -> 1.98 s).
                gate.close_and_drain(interval=0.001)""")

# ---------------------------------------------------------------- Meld imports
replace_block(meld,
'''from abc import ABC, abstractmethod
from annotationlib import Format''',
'''from abc import ABC, abstractmethod
from annotationlib import Format
from contextlib import AbstractContextManager, nullcontext''')
replace_block(meld,
'''from melder.aether.conduit.meld.contracts.spell_contract import SpellContract
from melder.aether.spellbook.existence.existence import Existence
if TYPE_CHECKING:''',
'''from melder.aether.conduit.meld.contracts.spell_contract import SpellContract
from melder.aether.conduit.meld.creation_context.creation_context_rebuild import (
    CreationContextRebuild,
)
from melder.aether.spellbook.existence.existence import Existence
if TYPE_CHECKING:''')
replace_block(meld,
'''    from melder.aether.conduit.meld.creation_context.creation_context import CreationContext

class Meld(Cleanable, ABC):''',
'''    from melder.aether.conduit.meld.creation_context.creation_context import CreationContext
    from melder.utilities.synchronization.creation_gate import CreationGate

class Meld(Cleanable, ABC):''')

# ---------------------------------------------------------------- Meld helpers
replace_block(meld,
'''    def _ensure_lineage_resolvable(self, spell: Spell) -> None:''',
'''    @staticmethod
    def _rebuild_window(spell: Spell) -> AbstractContextManager[object]:
        """
        Return the rebuild window a producer enters before taking `spell._lock`.

        Contract:
            - Dynamic ownership (`spell._creation_gate` set): a
              CreationContextRebuild over this one spell. It freezes the
              spell-index gate, drains admitted melds, and on exit publishes
              the rebuilt context (when the plan is present) before reopening.
            - Automatic ownership: a no-op context; automatic melds take no
              index ticket and are unchanged.
            - Phase 5 local resolution republishes only to its target
              (2026-09-19), so the target is the whole affected set.

        Args:
            spell: Spell whose phases are about to be rerun.

        Returns:
            AbstractContextManager[object]:
                The window to enter, outermost, before `spell._lock`.
        """
        if spell._creation_gate is None:
            return nullcontext()
        return CreationContextRebuild((spell,))

    def _execute_admitted(
            self,
            spell: Spell,
            creation_gate: CreationGate,
            override_map: Optional[Dict[str, Any]],
            with_created: bool,
    ) -> Any:
        """
        Run one dynamic meld's context read and execution under one index ticket.

        Purpose:
            Dynamic spells share one CreationContext across conduits, and a
            conduit-local rebuild replaces it. Holding the spell-index ticket
            from before the context read until the executor returns means a
            rebuild window either waits for this meld to finish or has finished
            before it reads, so the meld never uses a cleaned context or builds
            from a missing plan (2026-09-26).

        Contract:
            - Admits exactly one ticket and unregisters it exactly once, on
              success or failure. The context's own `execute*` wrappers (which
              admit again) are not used; their executor slots are called here.
            - After admission, a spell that became `resolution_required` while
              this meld was parked releases the ticket, runs the existing
              deferred path, and admits again (input-generation recheck).
            - `with_created` selects the hooks-lane result `(instance, created)`;
              otherwise the instance alone is returned.

        Args:
            spell: Target spell, already validated for this conduit.
            creation_gate: The spell's `_creation_gate`.
            override_map: Normalized overrides, or None.
            with_created: True for the hooks lane.

        Returns:
            Any:
                `(instance, created)` when `with_created`, else the instance.

        Raises:
            RuntimeError:
                When the gate is terminally closed, or when no context can be
                built or published.
            Exception:
                Executor and deferred-resolution failures propagate unchanged.
        """
        creation_gate.admit_ticket()
        while spell.resolution_required:
            creation_gate.unregister_ticket()
            self._ensure_runtime_resolution_ready(spell)
            creation_gate.admit_ticket()
        try:
            # Warm read inlined (one lock-free state read and one slot read,
            # as the doors do); the cold path elects a builder via the spell.
            if spell._creation_context_switch.fast_state >= 2:
                creation_context = spell._creation_context
            else:
                creation_context = spell._get_or_build_creation_context()
            if with_created:
                if override_map is None:
                    return creation_context._no_overrides_executor(self)
                return creation_context._overrides_executor(self, override_map)
            if override_map is None:
                return creation_context._no_overrides_instance_executor(self)
            return creation_context._overrides_executor(self, override_map)[0]
        finally:
            creation_gate.unregister_ticket()

    def _ensure_lineage_resolvable(self, spell: Spell) -> None:''')

# ---------------------------------------------------------------- Meld producers
replace_block(meld,
'''        Threading:
            Structural reruns are serialized under `spell._lock` so concurrent
            meld calls do not race duplicate validation work.''',
'''        Threading:
            Structural reruns are serialized under `spell._lock` so concurrent
            meld calls do not race duplicate validation work. Under dynamic
            ownership the rerun first enters the spell's rebuild window (see
            `_rebuild_window`): the index gate is frozen and drained before the
            spell lock is taken, because Phase 3 resets the shared context.''')
replace_block(meld,
'''        if self._gated_validation_required(spell):
            with spell._lock:
                if self._gated_validation_required(spell):
                    self._get_spell_compiler_system().run_structural_phases(''',
'''        if self._gated_validation_required(spell):
            with self._rebuild_window(spell), spell._lock:
                if self._gated_validation_required(spell):
                    self._get_spell_compiler_system().run_structural_phases(''')
replace_block(meld,
'''        with spell._lock:
            if not spell.resolution_required:
                return''',
'''        # Rebuild window first (dynamic only), then the spell lock: see
        # `_rebuild_window`. Phase 11 resets the shared context.
        with self._rebuild_window(spell), spell._lock:
            if not spell.resolution_required:
                return''')
replace_block(meld,
'''        if resolution_validity is SpellValidity.unknown or resolution_validity is SpellValidity.gated:
            with spell._lock:''',
'''        if resolution_validity is SpellValidity.unknown or resolution_validity is SpellValidity.gated:
            # Rebuild window first (dynamic only), then the spell lock: Phase 5
            # clears the plan and resets the shared context that other
            # conduits' admitted melds may be using. See `_rebuild_window`.
            with self._rebuild_window(spell), spell._lock:''')

# ---------------------------------------------------------------- Doors
NO_HOOKS_OLD = '''        if not (meld_hooks or spell_hooks_enabled):
            if target_spell._creation_context_switch.fast_state >= 2:
                creation_context = target_spell._creation_context
            else:
                creation_context = target_spell._get_or_build_creation_context()
            if creation_context is None:
                raise RuntimeError("Spell returned no live CreationContext.")
            # Hot path: in non-dynamic mode dispatch the phase-11 runtime door
            # directly so the no-hooks lane skips the `execute_no_hooks`
            # wrapper frame. The executor reference is read through the live
            # context on this normal-lane pass; the only place it is retained
            # is the guarded fast-door entry built below, whose per-call
            # context-identity guard prevents a recompiled/cleaned context
            # from ever serving a stale executor.
            if creation_context._dynamic_environment:
                instance = creation_context.execute_no_hooks(
                    self,
                    override_map,
                )
            elif override_map is None:'''
NO_HOOKS_NEW = '''        if not (meld_hooks or spell_hooks_enabled):
            # Dynamic spells carry their spell-index gate. They admit the
            # index ticket BEFORE reading the context and hold it through
            # execution, so a rebuild window cannot clean or replace the
            # context under this meld (2026-09-26). Automatic spells take the
            # unchanged lock-free lane below.
            creation_gate = target_spell._creation_gate
            if creation_gate is None:
                if target_spell._creation_context_switch.fast_state >= 2:
                    creation_context = target_spell._creation_context
                else:
                    creation_context = target_spell._get_or_build_creation_context()
                if creation_context is None:
                    raise RuntimeError("Spell returned no live CreationContext.")
            # Hot path: in non-dynamic mode dispatch the phase-11 runtime door
            # directly so the no-hooks lane skips the `execute_no_hooks`
            # wrapper frame. The executor reference is read through the live
            # context on this normal-lane pass; the only place it is retained
            # is the guarded fast-door entry built below, whose per-call
            # context-identity guard prevents a recompiled/cleaned context
            # from ever serving a stale executor.
            if creation_gate is not None:
                instance = self._execute_admitted(
                    target_spell,
                    creation_gate,
                    override_map,
                    False,
                )
            elif override_map is None:'''
replace_block(conduit_meld, NO_HOOKS_OLD, NO_HOOKS_NEW)
replace_block(spellspace_meld, NO_HOOKS_OLD, NO_HOOKS_NEW)

HOOKS_OLD = '''            if target_spell._creation_context_switch.fast_state >= 2:
                creation_context = target_spell._creation_context
            else:
                creation_context = target_spell._get_or_build_creation_context()
            if creation_context is None:
                raise RuntimeError("Spell returned no live CreationContext.")
            instance, created = creation_context.execute(
                self,
                override_map,
            )'''
HOOKS_NEW = '''            creation_gate = target_spell._creation_gate
            if creation_gate is not None:
                # Dynamic: one index ticket from before the context read until
                # the executor returns (see `Meld._execute_admitted`).
                instance, created = self._execute_admitted(
                    target_spell,
                    creation_gate,
                    override_map,
                    True,
                )
            else:
                if target_spell._creation_context_switch.fast_state >= 2:
                    creation_context = target_spell._creation_context
                else:
                    creation_context = target_spell._get_or_build_creation_context()
                if creation_context is None:
                    raise RuntimeError("Spell returned no live CreationContext.")
                instance, created = creation_context.execute(
                    self,
                    override_map,
                )'''
replace_block(conduit_meld, HOOKS_OLD, HOOKS_NEW)
replace_block(spellspace_meld, HOOKS_OLD, HOOKS_NEW)
