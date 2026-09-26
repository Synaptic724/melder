"""September plan, part 1: Spell gate/failure fields and factory failure release (2026-09-26).

Usage: python apply_sept_spell_factory.py <repo_root>
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from patch_util import replace_block

root = pathlib.Path(sys.argv[1])
spell = root / "src/melder/aether/spellbook/spell.py"
factory = root / "src/melder/aether/conduit/meld/creation_context/creation_context_factory.py"

# ---------------------------------------------------------------- Spell fields
replace_block(spell,
'''        "user_created_object",
    ]''',
'''        "user_created_object",
        # Appended, not alphabetized: new slots go last so the offsets of the
        # hot fast-door slots (`_door_epoch`, `_creation_context`) stay put.
        "_creation_context_failure",
        "_creation_gate",
    ]''')
replace_block(spell,
'''    from melder.utilities.synchronization.creation_gate_controller import (
        CreationGateController,
    )''',
'''    from melder.utilities.synchronization.creation_gate import CreationGate
    from melder.utilities.synchronization.creation_gate_controller import (
        CreationGateController,
    )''')
replace_block(spell,
'''        # Spell-owned selector latch for one-leader CreationContext publication.
        self._creation_context_switch: CounterSwitch = CounterSwitch(state=0)''',
'''        # Spell-owned selector latch for one-leader CreationContext publication.
        self._creation_context_switch: CounterSwitch = CounterSwitch(state=0)
        # Cause of the last failed context build or rebuild window. Melds that
        # waited on that build report it; a new rebuild window clears it.
        self._creation_context_failure: Optional[BaseException] = None
        # Borrowed spell-index CreationGate, set only under dynamic ownership.
        # A dynamic meld holds one ticket on it from before it reads the
        # context until its executor returns; a rebuild window freezes and
        # drains it before phases replace the plan. The frame's
        # CreationGateController owns the gate's lifecycle.
        self._creation_gate: Optional[CreationGate] = None''')
replace_block(spell,
'''            - Leaves `_creation_context_factory` as `None`.
        """
        if self._creation_context_factory is not None:
            try:
                self._creation_context_factory.cleanup()
            except Exception:
                pass
            self._creation_context_factory = None''',
'''            - Leaves `_creation_context_factory` as `None`.
            - Drops the borrowed spell-index gate reference with it (the
              gate is resolved again when a factory is configured); the gate
              itself is owned by the frame's CreationGateController.
        """
        if self._creation_context_factory is not None:
            try:
                self._creation_context_factory.cleanup()
            except Exception:
                pass
            self._creation_context_factory = None
        self._creation_gate = None''')
replace_block(spell,
'''        Contract:
            - Replaces any existing factory instance.
            - Stores dynamic mode on the spell for runtime metadata.
            - Requires a non-null CreationGateController.''',
'''        Contract:
            - Replaces any existing factory instance.
            - Stores dynamic mode on the spell for runtime metadata.
            - Requires a non-null CreationGateController.
            - In dynamic mode, resolves (creating when absent) the stable
              spell-index CreationGate and keeps it on `_creation_gate` so
              meld doors can admit before reading the context; None in
              automatic mode.''')
replace_block(spell,
'''        self._creation_context_factory = CreationContextFactory(
            dynamic_environment=self._dynamic_environment,
            creation_gate_controller=creation_gate_controller,
        )''',
'''        self._creation_context_factory = CreationContextFactory(
            dynamic_environment=self._dynamic_environment,
            creation_gate_controller=creation_gate_controller,
        )
        self._creation_gate = (
            self._creation_context_factory.resolve_spell_index_gate(self)
        )''')
replace_block(spell,
'''            del self._creation_context_factory
            del self._creation_context_switch''',
'''            del self._creation_context_factory
            del self._creation_context_failure
            del self._creation_context_switch
            del self._creation_gate''')
replace_block(spell,
'''        Contract:
            - Requires the spell to have an initialized factory.
            - Returns a ready state-2 context without locking.
            - Serializes only the cold/rebuild path under the spell RLock and
              rechecks readiness after acquiring it. A conduit-local phase run
              owns the same lock while it clears and republishes phase-11
              state, so a competing conduit cannot build from the transient
              artifact gap.
            - Delegates build/get policy to CreationContextFactory.
            - Returns a live CreationContext instance bound to this spell.

        Threading:
            The normal ready-context path remains one lock-free state read and
            one context read. Only state 0/1 retrieval takes `_lock`; the lock
            is re-entrant because phase and ownership callers may already hold
            it while requesting a rebuild.''',
'''        Contract:
            - Requires the spell to have an initialized factory.
            - Returns a ready state-2 context without locking.
            - Delegates build/get policy to CreationContextFactory, whose cold
              path elects one builder through `_creation_context_switch`.
            - Returns a live CreationContext instance bound to this spell.

        Threading:
            The ready path is one lock-free state read and one context read.
            It takes no lock: in dynamic mode the caller already holds a
            spell-index ticket on `_creation_gate`, and every conduit-local
            rebuild (structural, resolution and deferred phases) runs inside
            a CreationContextRebuild window that freezes that gate and drains
            its tickets before phases replace the plan or reset this context,
            so an admitted caller never sees the rebuild gap and never holds a
            context that is cleaned under it (2026-09-26). Resets outside
            those windows (ownership restamps, notch, teardown, transfer) are
            not drained.''')

# ---------------------------------------------------------------- Factory
replace_block(factory,
'''    from melder.utilities.synchronization.creation_gate import CreationGate''',
'''    from melder.utilities.synchronization.creation_gate import CreationGate''')
replace_block(factory,
'''    Threading:
        Deliberately LOCK-FREE and race-tolerant. Two threads may build a
        context for the same spell concurrently; both builds are equivalent and
        the spell owns whichever lands, so the loser is simply discarded rather
        than being an error worth locking against.''',
'''    Threading:
        LOCK-FREE on the ready path. The cold path elects exactly one builder
        through the spell's CounterSwitch (followers park until it publishes).
        A builder that fails records the cause on the spell and releases its
        claim, so followers wake and report that cause instead of waiting for
        a publication that will never come. Input stability comes from the
        spell-index gate: dynamic melds build and execute while holding a
        ticket, and rebuild windows drain those tickets before phases replace
        the plan (see CreationContextRebuild).''')
replace_block(factory,
'''        The lock-free choice is worth understanding rather than copying
        blindly. Context construction is IDEMPOTENT and side-effect-free with
        respect to shared state: two racing builds produce equivalent objects,
        and the spell's slot is the single point of truth for which one wins.
        Taking a lock here would serialize the cold path of every distinct
        spell for no correctness gain - and under free-threaded 3.14t that
        contention would be paid on every core.''',
'''        The ready path stays lock-free because it runs on every meld; the
        cold path is a per-spell election, never a global lock, so cold builds
        of different spells never contend. The factory does not guard its
        inputs: a build reads the spell's phase-11 plan, and keeping that plan
        present during the build is the rebuild window's job, not the
        factory's.''')
replace_block(factory,
'''    def get_or_build_for_spell(self, spell: "Spell") -> "CreationContext":
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
        """''',
'''    def resolve_spell_index_gate(self, spell: "Spell") -> Optional[CreationGate]:
        """
        Return the shared spell-index CreationGate the spell's contexts use.

        Contract:
            - Automatic mode: returns None (no runtime admission gate).
            - Dynamic mode: returns the controller's gate for the spell's
              stable index id, creating it on first use exactly as
              `build_for_spell` would.

        Args:
            spell: Spell whose index gate is resolved.

        Returns:
            Optional[CreationGate]:
                The gate borrowed from the frame's controller, or None.
        """
        return self._resolve_runtime_gate_for_spell(spell)[0]

    def get_or_build_for_spell(self, spell: "Spell") -> "CreationContext":
        """
        Resolve one spell-owned context via spell-level CounterSwitch election.

        Contract:
            - Uses `spell._creation_context_switch.selector()` for one-leader
              get-or-build election.
            - Leader builds/publishes context and opens latch to state `2`,
              then clears any recorded build failure.
            - Leader failure records the exception on
              `spell._creation_context_failure`, releases its claim (state
              1 -> 0, which wakes followers) and re-raises the original.
            - Followers block while pending (`state == 1`) and then read the
              published context; a follower woken by a failed leader raises
              RuntimeError chained from the recorded cause.
            - Context ownership remains on Spell (`spell._creation_context`).
            - Does not use `spell._lock` for hot-path access/publication.
            - Does not inspect `CreationContext.is_cleaned`; switch state is
              treated as the single source of truth for readiness.
            - Single selector pass: no retry loops.

        Args:
            spell: Spell whose context is resolved.

        Returns:
            CreationContext:
                Spell-owned cached or newly built context.

        Raises:
            RuntimeError:
                Propagated from `CreationContextBuilder.build` for the leader;
                raised for a follower when no context was published.
        """''')
replace_block(factory,
'''        if switch_state == 1:
            creation_gate, index_id = self._resolve_runtime_gate_for_spell(spell)
            built_creation_context = CreationContextBuilder.build(
                spell,
                dynamic_environment=self._dynamic_environment,
                creation_gate=creation_gate,
                creation_gate_index_id=index_id,
            )
            spell._creation_context = built_creation_context
            creation_context_switch.advance(1)
            self._stage_cache_after_publish(spell, built_creation_context)
            return built_creation_context
        creation_context = spell._creation_context
        if creation_context is None:
            raise RuntimeError(
                "Spell creation context was not published by the selected builder."
            )
        return creation_context''',
'''        if switch_state == 1:
            creation_gate, index_id = self._resolve_runtime_gate_for_spell(spell)
            try:
                built_creation_context = CreationContextBuilder.build(
                    spell,
                    dynamic_environment=self._dynamic_environment,
                    creation_gate=creation_gate,
                    creation_gate_index_id=index_id,
                )
            except BaseException as error:
                # Release the claim so parked followers wake and report this
                # cause; a pending latch with no builder would park them forever.
                spell._creation_context_failure = error
                if creation_context_switch.state == 1:
                    creation_context_switch.advance(-1)
                raise
            spell._creation_context = built_creation_context
            creation_context_switch.advance(1)
            spell._creation_context_failure = None
            self._stage_cache_after_publish(spell, built_creation_context)
            return built_creation_context
        creation_context = spell._creation_context
        if creation_context is None:
            failure = spell._creation_context_failure
            if failure is not None:
                raise RuntimeError(
                    "Spell creation context was not published: the selected "
                    f"builder failed ({type(failure).__name__}: {failure})."
                ) from failure
            raise RuntimeError(
                "Spell creation context was not published by the selected builder."
            )
        return creation_context''')
