# Story: Aether owns one unified spell_id set

## Metadata
- Story ID: STORY-2026-08-02-aether-unified-spell-id-set
- Epic ID: EPIC-2026-08-02-process-wide-spell-id-uniqueness
- Status: ready
- Owner: cowork
- Agent Name: UNASSIGNED
- Priority: p1
- Created: 2026-08-02T20:20:00Z
- Updated: 2026-08-02T20:20:00Z

## Problem / Opportunity
Today Aether hosts ZERO spell ids. Every id-bearing method on it
(`_check_for_spell`, `_add_spells_to_aether`, `_get_all_spell_ids`) resolves a
frame and delegates. Uniqueness is therefore per-frame by construction, and the
owner has ruled it must be per-process.

## Ticket Contract
- ENTRY_GATE: `process_wide_unique_spell_ids` config landed (done); S1 preflight
  green.
- EXECUTION_BOUNDARY: `aether.py`, `aetheric_frame.py`, `aether_configuration.py`
  and their tests. Do NOT touch teardown paths - that is S3.
- DEPENDENCIES: STORY-2026-08-02-conjure-spell-id-preflight (self-match trap).
- EXIT_GATE: one process-wide set is authoritative; the check-and-set is atomic
  under one lock hold; frames read the regime once at birth.
- FAILURE_ESCALATION: `BLOCKER` if the frame lock and an Aether-level lock cannot
  be ordered without a cycle.

## Goals
- One Aether-owned id set when the regime is on.
- Atomic check-and-set at the write, replacing the `conduit_id`-only check.
- Frames read the bool at birth and never re-read it.
- Lazy-frame trigger: first frame birth installs config defaults if unconfigured.

## Non-goals
- Removal on destruction. S3. Do not fold it in - the epic says so explicitly.
- Renaming `_selected_spell_registry`. S5.

## Requirements
- R1 `AethericFrame.register_conduit_spells` performs the id sweep INSIDE its
  existing `with self._lock:` hold, so check and write are one atomic act. It
  currently checks only `conduit_id`, which cannot collide.
- R2 Self-exclusion by IDENTITY (`other_ids is spell_ids`) - the frame stores the
  live reference, so the book's own entry is the same object. Document that the
  identity check depends on the never-copy invariant.
- R3 Frames capture the regime bool at construction; the config setter is already
  freeze-guarded so it cannot change under a live world.
- R4 `import melder` still creates ZERO frames (owner ruling 2026-07-11). The
  trigger fires at FIRST FRAME BIRTH, not at Aether boot.

## Acceptance criteria
- Two frames binding the same class are refused under the default regime.
- With the regime OFF, per-frame scoping is restored and the multi-tenant shape
  works again.
- No lock-order cycle between Aether and frame locks.
- Owner-run suite green.

## Risks / Mitigations
- RISK: THE SELF-MATCH TRAP. Registering the alias earlier makes
  `_spell_id_integrity_checker` match its own ids and refuse EVERY conjure.
  MITIGATION: identity exclusion, and run the S1 guard first - its negative
  controls catch this immediately.
- RISK: `unregister_conduit_spells` pops the id entry only when the conduit's
  SpellIndex set empties. Under a unified set that coupling is wrong.
  MITIGATION: in scope here to re-think the keying; the REMOVAL semantics are S3.
- RISK: a second process-wide lock on the bind path. MITIGATION: prefer keeping
  the write under the frame lock and having the frame delegate, rather than
  introducing an Aether lock the bind path must also take.

## Validation plan
- Extend `test_spellbook_component_spell_id_integrity.py`: the "different frames"
  negative control INVERTS under the default regime and must be re-expressed as a
  regime-off test.
- Concurrency test: two threads conjuring into one frame; exactly one succeeds.

## State Transition Event
- from_state: draft
- to_state: ready
- transition_reason: config surface landed; design decided; unblocked by S1.

## Applicable Anti-Patterns
- [ ] Do not trust a field name over source in this subsystem.
- [ ] No implementation from `UNKNOWN` or `HYPOTHESIS`.

## Notes

- DATETIME: 2026-08-02T20:20:00Z
  TYPE: DECISION
  CLAIM: THE ATOMIC CHECK BELONGS AT THE FRAME WRITE, not in the Spellbook.
    `register_conduit_spells` already takes the frame RLock and already does a
    check-and-set under it - it just checks `conduit_id`, which cannot collide,
    instead of spell ids, which demonstrably can. Doing it Spellbook-side means
    fetch (frame lock) -> release -> compare (spellbook lock) -> register (frame
    lock again), and two books can both pass in that window. This is also the
    likely reason `_check_all_spells` was never wired: it takes the SPELLBOOK
    lock, so it could never have been atomic against the frame write.
  EVIDENCE:
  - src/melder/aether/aetheric_frame/aetheric_frame.py:1016-1026
  - src/melder/aether/spellbook/spellbook.py:2675-2718
  IMPACT: Decides where the authority lives and retires the dead method rather
    than reviving it.
  NEXT: Implement inside the existing lock hold; do not add a second acquisition.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-08-02T20:20:00Z
  TYPE: FACT
  CLAIM: FRAMES ARE LAZY BY OWNER RULING, which sets the trigger point.
    `aether.py:183` states "`import melder` creates ZERO frames"; the first
    Spellbook births the frame it names, and `_ensure_default_frame` lazily
    creates "default" on first use (owner ruling 2026-07-11). So there is no
    frame at Aether boot to read a config, and nothing forces `configure()`
    before the first frame exists.
  EVIDENCE:
  - src/melder/aether/aether.py:172-183
  - src/melder/aether/aether.py:323-341
  IMPACT: The regime must be captured at FRAME BIRTH with a default, and Aether
    must refuse a regime change once any frame exists - otherwise frames born
    before and after `configure()` run different regimes in one process.
  NEXT: Wire the default-install at `_ensure_frame`, not at `Aether.__init__`.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

## Context / Handoff Summary
The config surface is landed and defaults on. What remains is the set itself:
Aether owns it, frames delegate into it, and the authoritative check-and-set
moves into `register_conduit_spells` under the lock it already holds. Read the
self-match risk before touching registration timing - it breaks every conjure if
missed.
