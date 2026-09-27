"""Apply the reader-side CreationContext cold-path fix (2026-09-26) to a source tree.

Usage: python apply_fix.py <repo_root>

Edits are exact, line-normalized block replacements: each old block must match
the stated number of times (ignoring CR), and replaced lines keep the dominant
line ending of the block they replace, so mixed CRLF/LF files stay as they are.
"""
import pathlib
import sys
from collections import Counter


def replace_block(path: pathlib.Path, old: str, new: str, count: int = 1) -> None:
    raw = path.read_bytes().decode("utf-8")
    lines = raw.splitlines(keepends=True)
    norm = [line.rstrip("\r\n") for line in lines]
    old_lines = old.split("\n")
    n = len(old_lines)
    hits = [i for i in range(len(norm) - n + 1) if norm[i:i + n] == old_lines]
    if len(hits) != count:
        raise SystemExit(f"{path}: expected {count} match(es), found {len(hits)}:\n{old_lines[0]}")
    for i in reversed(hits):
        endings = Counter(lines[j][len(norm[j]):] for j in range(i, i + n))
        ending = endings.most_common(1)[0][0] or "\n"
        last_ending = lines[i + n - 1][len(norm[i + n - 1]):]
        new_lines = [text + ending for text in new.split("\n")]
        new_lines[-1] = new.split("\n")[-1] + last_ending
        lines[i:i + n] = new_lines
    path.write_bytes("".join(lines).encode("utf-8"))
    print(f"patched {path} ({count})")


root = pathlib.Path(sys.argv[1])
factory = root / "src/melder/aether/conduit/meld/creation_context/creation_context_factory.py"
spell = root / "src/melder/aether/spellbook/spell.py"
conduit_meld = root / "src/melder/aether/conduit/meld/conduit_meld.py"
spellspace_meld = root / "src/melder/aether/conduit/meld/spellspace_meld.py"

# --- CreationContextFactory: class docstring -------------------------------------------
replace_block(factory,
"""        - Get-or-build path is lock-free and race-tolerant.""",
"""        - The ready path is lock-free; the cold build path runs under the
          owning spell's lock, one builder per spell at a time.""")
replace_block(factory,
"""    Threading:
        Deliberately LOCK-FREE and race-tolerant. Two threads may build a
        context for the same spell concurrently; both builds are equivalent and
        the spell owns whichever lands, so the loser is simply discarded rather
        than being an error worth locking against.""",
"""    Threading:
        The ready path (an open switch with a published context) takes no lock.
        The cold path takes the owning spell's `_lock`, the same re-entrant lock
        a conduit-local resolution rerun holds across phases 5-11, so a context
        is never built from the gap between Phase 5 clearing the plan and
        Phase 11 republishing it. Cache staging runs after that lock is
        released.""")
replace_block(factory,
"""        The lock-free choice is worth understanding rather than copying
        blindly. Context construction is IDEMPOTENT and side-effect-free with
        respect to shared state: two racing builds produce equivalent objects,
        and the spell's slot is the single point of truth for which one wins.
        Taking a lock here would serialize the cold path of every distinct
        spell for no correctness gain - and under free-threaded 3.14t that
        contention would be paid on every core.""",
"""        The ready path stays lock-free because it runs on every meld. The cold
        path is locked per spell because a build is only correct while the
        spell's phase-11 plan is present, and that plan is replaced under the
        same lock when a conduit revalidates the spell (2026-09-26: concurrent
        first melds from linked conduits raised "Cannot build CreationContext
        before spell_codegen_creation exists"). The lock is per spell, so cold
        builds of different spells never contend, and the cold path runs once
        per published context.""")

# --- CreationContextFactory.get_or_build_for_spell --------------------------------------
replace_block(factory,
'''        """
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
        creation_context_switch = spell._creation_context_switch
        if creation_context_switch.state >= 2:
            creation_context = spell._creation_context
            if creation_context is None:
                raise RuntimeError(
                    "Spell creation context switch is open but no context is published."
                )
            return creation_context
        switch_state = creation_context_switch.selector()
        if switch_state == 1:
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
'''        """
        Return the spell-owned context, building it on the cold path.

        Contract:
            - Ready path: when the switch is open (state >= 2) and a context is
              published, returns it without taking any lock.
            - Cold path: otherwise takes `spell._lock`, rechecks, and when the
              spell is still not ready builds from the current phase-11 plan,
              publishes the result into `spell._creation_context` and opens the
              switch to state `2`. Callers that queued on the lock return the
              context the first builder published; no second build happens.
            - A conduit-local resolution rerun holds `spell._lock` across
              phases 5-11 (Phase 5 clears the plan and resets this context,
              Phase 11 republishes the plan), so the cold path waits for a
              rebuild in flight instead of reading the gap (2026-09-26).
            - An open switch with an empty slot is the instant inside a reset
              between clearing the slot and resetting the switch; it takes the
              cold path.
            - A failed build publishes nothing and leaves the switch unchanged,
              so the next caller builds again. The switch's selector election
              is not used: the spell lock is the election.
            - Cache staging runs after the spell lock is released, because it
              takes `spellbook._lock` and `Spellbook._add_hooks_to_spell` takes
              a spell lock while holding the spellbook lock.
            - Context ownership remains on Spell (`spell._creation_context`).
            - Does not inspect `CreationContext.is_cleaned`.

        Threading:
            Resets that do not hold the spell lock (frame-wide Phase 5 at
            conjure, notch of an outgoing member, spell teardown and ownership
            transfer) are not serialized with the cold path; a build that
            overlaps one can still fail in `CreationContextBuilder.build`.

        Args:
            spell:
                Spell whose context is returned.

        Returns:
            CreationContext:
                Spell-owned published or newly built context.

        Raises:
            RuntimeError:
                Propagated from `CreationContextBuilder.build` when the spell
                has no phase-11 plan to build from.
        """
        creation_context_switch = spell._creation_context_switch
        if creation_context_switch.state >= 2:
            creation_context = spell._creation_context
            if creation_context is not None:
                return creation_context
        with spell._lock:
            creation_context = spell._creation_context
            if creation_context_switch.state >= 2 and creation_context is not None:
                return creation_context
            creation_gate, index_id = self._resolve_runtime_gate_for_spell(spell)
            creation_context = CreationContextBuilder.build(
                spell,
                dynamic_environment=self._dynamic_environment,
                creation_gate=creation_gate,
                creation_gate_index_id=index_id,
            )
            spell._creation_context = creation_context
            self._set_creation_context_switch_open(spell)
        self._stage_cache_after_publish(spell, creation_context)
        return creation_context''')

# --- Spell._get_or_build_creation_context -----------------------------------------------
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
            it while requesting a rebuild.

        Returns:
            Any:
                Spell-owned CreationContext instance.

        Raises:
            RuntimeError:
                If the spell has no configured CreationContextFactory.
        """
        creation_context_switch = self._creation_context_switch
        if creation_context_switch.state >= 2:
            return self._creation_context
        creation_context_factory = self._creation_context_factory
        if creation_context_factory is None:
            raise RuntimeError("Spell has no configured CreationContextFactory.")
        return creation_context_factory.get_or_build_for_spell(self)''',
'''        Contract:
            - Requires the spell to have an initialized factory.
            - Returns a published context without locking when the switch is
              open (state >= 2) and the slot holds a context.
            - Otherwise delegates to `CreationContextFactory.get_or_build_for_spell`,
              whose cold path takes this spell's `_lock`, rechecks readiness
              and builds from the current phase-11 plan. A conduit-local phase
              run owns the same lock while it clears and republishes phase-11
              state, so a competing conduit waits for that rebuild instead of
              building from the transient artifact gap (2026-09-26).
            - Returns a live CreationContext instance bound to this spell; it
              never returns None.

        Threading:
            The ready path stays one lock-free state read and one slot read.
            The slot is read once into a local so the None check and the return
            see the same object: a reset clears the slot before it resets the
            switch, so an open switch can briefly sit beside an empty slot, and
            that case takes the cold path. The lock is re-entrant because phase
            and ownership callers may already hold it while requesting a
            rebuild.

        Returns:
            Any:
                Spell-owned CreationContext instance.

        Raises:
            RuntimeError:
                If the spell has no configured CreationContextFactory, or
                propagated from the factory when no phase-11 plan exists.
        """
        creation_context_switch = self._creation_context_switch
        if creation_context_switch.state >= 2:
            creation_context = self._creation_context
            if creation_context is not None:
                return creation_context
        creation_context_factory = self._creation_context_factory
        if creation_context_factory is None:
            raise RuntimeError("Spell has no configured CreationContextFactory.")
        return creation_context_factory.get_or_build_for_spell(self)''')

# --- Meld doors (two per file) -----------------------------------------------------------
DOOR_OLD = '''            if target_spell._creation_context_switch.fast_state >= 2:
                creation_context = target_spell._creation_context
            else:
                creation_context = target_spell._get_or_build_creation_context()
            if creation_context is None:
                raise RuntimeError("Spell returned no live CreationContext.")'''
DOOR_NEW = '''            if target_spell._creation_context_switch.fast_state >= 2:
                creation_context = target_spell._creation_context
            else:
                creation_context = None
            if creation_context is None:
                # Cold path: the spell builds its context under its own lock.
                # Also taken when a revalidation reset the context between the
                # two reads above; the cold path then waits for that rebuild
                # instead of failing the meld (2026-09-26).
                creation_context = target_spell._get_or_build_creation_context()'''
replace_block(conduit_meld, DOOR_OLD, DOOR_NEW, count=2)
replace_block(spellspace_meld, DOOR_OLD, DOOR_NEW, count=2)
