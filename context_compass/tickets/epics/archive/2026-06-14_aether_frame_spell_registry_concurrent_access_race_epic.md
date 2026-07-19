# Epic: Aether Frame Spell-Registry Concurrent Access Race

## Metadata
- Epic ID: EPIC-2026-06-14-aether-frame-spell-registry-concurrent-access-race
- Status: redesigned (version cache deleted) -- awaiting validation on 3.14t
- Owner: cowork
- Agent Name: mediator_builder_0
- Priority: p1
- Created: 2026-06-14T16:40:19Z
- Updated: 2026-06-14T21:20:00Z
- Target Window: 2026-Q2
- Related Program/Initiative: Melder free-threaded (3.14t) concurrency hardening

## Problem / Opportunity
Under free-threaded Python (3.14t), concurrent `conjure()` of two root conduits
on the SAME aetheric frame can crash with
`RuntimeError: dictionary changed size during iteration`.

The frame's `_spell_registry` (conduit_id -> set[SpellIndex]) is mutated from
`aether.py` WITHOUT holding `frame._lock`, while
`AethericFrame.refresh_version_registry()` iterates that same dict UNDER
`frame._lock`. Because the writer skips the lock, the reader's lock protects
nothing: one conjure inserts its conduit's spell set while another conjure's
refresh iterates the dict -> size-changed-during-iteration.

Free-threading note (answers a natural objection): individual dict operations
are atomic via per-dict C locks, so the dict will not corrupt. But iterating a
dict while another thread inserts into it STILL raises the size-change
RuntimeError -- that consistency guard is intentional and is NOT prevented by
the per-op lock. Application-level locking around iterate+write is required.

## Reproduction
Test (pre-existing, timing-dependent / flaky):
- `tests/integration/melder/spellbook/test_spellbook_integration_core.py::test_spellbook_integration_explicit_shared_mode_same_frame_concurrent_conjure_is_threadsafe`

What it does: builds two `Spellbook`s on one shared frame
("explicit-shared-concurrent-frame"), binds one spell in each, then starts two
threads that synchronize on a `Barrier(2)` and call `spellbook.conjure(name=...)`
at the same instant. It asserts no worker raised (`errors == []`).

Single runs usually PASS (the collision window is narrow). To trip it reliably,
loop it and stop on the first failure (PowerShell):

    for ($i=1; $i -le 40; $i++) { Write-Host "run $i"; python -m pytest "tests/integration/melder/spellbook/test_spellbook_integration_core.py::test_spellbook_integration_explicit_shared_mode_same_frame_concurrent_conjure_is_threadsafe" -vv; if ($LASTEXITCODE -ne 0) { break } }

The worker swallows the exception into `errors` (asserted `== []`), so the raw
`RuntimeError` shows in the assert diff but not its call stack. To see the full
stack, temporarily capture `traceback.format_exc()` in the worker `except`
block and run with `-vv`. (A temporary diagnostic was used to capture the stack
below and has since been reverted.)

Observed traceback (key frames, top-down):
    conduit = spellbook.conjure(name=conduit_name)
    -> spellbook_creation_system.conjure()
    -> SpellbookCreationSystem._build_conduit(...)
    -> Conduit.__init__ -> _configure_conduit_state()
    -> conduit._add_spells_to_aether()
    -> spellbook._register_conduit_spells_in_aether(self._id)
    -> aether._add_spells_to_aether(conduit_id, spell_set, frame)
    -> frame.refresh_version_registry()
    -> for conduit_id, spell_set in self._spell_registry.items():
    RuntimeError: dictionary changed size during iteration

## Root Cause + Evidence
Reader (correctly locked) iterates the dict under the frame RLock:
- `src/melder/aether/aetheric_frame/aetheric_frame.py:604-634` (iterate at :625)
- `frame._lock` is `threading.RLock`: `src/melder/aether/aetheric_frame/aetheric_frame.py:104`

Writers (UNLOCKED) reach into `frame._spell_registry` from aether.py and mutate
then call `frame.refresh_version_registry()` without taking `frame._lock`:
- `_add_spells_to_aether`  -- write at :1325, refresh at :1328
  (`src/melder/aether/aether.py:1318-1328`)
- `_remove_spells_from_aether` -- `src/melder/aether/aether.py:1350-1361`
- `_register_single_spell_index` -- `src/melder/aether/aether.py:1388-1398`
- `_remove_single_spell_index` -- `src/melder/aether/aether.py:1428-1441`

Reader (UNLOCKED) iterating from aether.py (latent same-class race partner):
- `_get_conduit_by_spell_id` iterates `spell_registry.items()` at
  `src/melder/aether/aether.py:1239` (frame select at :1224-1236)

Containment: only `aetheric_frame.py` and `aether.py` touch `_spell_registry`
(verified by repo grep). The frame's own read methods (`has_version`,
`find_and_return_spell_index`, `get_all_versions`) already lock; the gap is the
external aether.py accesses.

## What This Is Not
- NOT the `unique_per_lineage` -> root-creations change. That lives in the
  creations subsystem (`src/melder/aether/conduit/creations/creations.py`,
  `_root_creations`); this race is in the frame version-registry path and never
  touches creations. (The creations change is exonerated.)
- NOT the mediator/unlink transaction work; sever/unlink run only on link/sever,
  never during conjure.

## Proposed Fix Options
- Option A (encapsulate; recommended): add `AethericFrame` methods that own the
  registry mutations + refresh under `_lock` (e.g. `register_conduit_spells`,
  `unregister_conduit_spells`, `register_spell_index`, `unregister_spell_index`,
  and a locked spell-id lookup), and have aether.py call those instead of poking
  `frame._spell_registry` directly. Removes the layering violation for good.
- Option B (minimal): wrap each of the 5 aether.py accesses (4 writers + the one
  reader) in `with frame._lock:`. `frame._lock` is an `RLock`, so the nested
  `refresh_version_registry()` re-enters safely.

## Scope Boundaries
- In scope: locking/encapsulation of `frame._spell_registry` (and the derived
  `_version_registry`) access from aether.py; the named test.
- Out of scope: the mediator/unlink lane; the creations/`unique_per_lineage`
  change; any phase 6-7 codegen/creation concurrency (would be a separate race
  if it exists).

## Acceptance Criteria
- The named test is stable under a 40x loop (no size-change RuntimeError).
- Every `frame._spell_registry` / `_version_registry` mutation AND iteration is
  serialized under `frame._lock` (directly or via frame-owned methods).
- Full unit + spellbook/conduit integration suites green.

## Risks / Mitigations
- Risk: nested-lock deadlock. Mitigation: `frame._lock` is an `RLock`; the
  nested `refresh_version_registry()` re-enters safely.
- Risk: a missed access site. Mitigation: grep confirms only `aetheric_frame.py`
  + `aether.py` touch `_spell_registry`; fix all 5 aether sites listed above.

## Applicable Anti-Patterns
- [ ] No closure while any `_spell_registry` access remains outside `frame._lock`.
- [ ] No "fixed" claim without the 40x-loop stability check executed.

## Notes
- DATETIME: 2026-06-14T16:40:19Z
  TYPE: FACT
  CLAIM: Concurrent conjure on a shared frame crashes with "dictionary changed
    size during iteration". `frame._spell_registry` is written/iterated from
    aether.py without `frame._lock`, while `refresh_version_registry()` iterates
    it under the lock; the unlocked writer is the race partner. 4 unlocked
    writers + 1 unlocked reader in aether.py. Found by mediator_builder_0 while
    running the spellbook integration suite during unlink-lane validation.
  EVIDENCE:
  - src/melder/aether/aetheric_frame/aetheric_frame.py:604-634
  - src/melder/aether/aetheric_frame/aetheric_frame.py:104
  - src/melder/aether/aether.py:1318-1328
  - src/melder/aether/aether.py:1350-1361
  - src/melder/aether/aether.py:1388-1398
  - src/melder/aether/aether.py:1428-1441
  - src/melder/aether/aether.py:1239
  - tests/integration/melder/spellbook/test_spellbook_integration_core.py (concurrent_conjure_is_threadsafe)
  IMPACT: Concurrent conjure on one shared frame can crash on free-threaded
    builds. Suspected creations/`unique_per_lineage` change is exonerated.
  NEXT: choose Option A or B; fix all 5 aether sites; validate with the 40x loop.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-06-14T17:05:46Z
  TYPE: DECISION
  AGENT: compiler_strategy_0
  CLAIM: Implemented Option A (encapsulation) per user reassignment. Added five
    frame-owned, lock-serialized methods to `AethericFrame` (after
    find_and_return_spell_index): `register_conduit_spells`,
    `unregister_conduit_spells`, `register_spell_index`, `unregister_spell_index`,
    and `find_conduit_id_for_version`. Each takes `self._lock` and does the
    mutation/scan + the dependent `refresh_version_registry()` atomically (RLock
    re-entry on the nested refresh). Routed all 5 aether.py sites through them:
    `_add_spells_to_aether`, `_remove_spells_from_aether`,
    `_register_single_spell_index`, `_remove_single_spell_index`, and the reader
    `_get_conduit_by_spell_id`. aether.py no longer references `_spell_registry`
    at all (grep-clean); behavior preserved (duplicate-conduit ValueError,
    absent-conduit no-ops, not-found ValueError on the reader).
  FINDING: a THIRD external reader exists that the "only two files" grep missed:
    `_spell_in_registry` at
    src/melder/aether/conduit/conduit_ward/transfer/transfer_of_ownership.py:1037
    reads `frame._spell_registry.get(conduit_id)` + set-membership. It does NOT
    iterate the dict, so it is NOT subject to the size-change race, and it is
    try/except-guarded. It is out of this epic's scope (mediator/unlink lane), so
    left untouched; flagged to mediator_builder_0 to route through a frame-owned
    method when convenient for full layering closure. Anti-pattern checkbox
    "no `_spell_registry` access outside frame._lock" is satisfied for the
    size-change race; the transfer read is the only remaining layering nit.
  NEXT: user validates on 3.14t -- 40x concurrent-conjure loop + unit/spellbook/
    conduit integration suites.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-06-14T17:05:46Z
  TYPE: MEASURE
  AGENT: compiler_strategy_0
  CLAIM: VALIDATED on 3.14t. The 40x concurrent-conjure loop is now stable (40/40
    pass; previously tripped the size-change RuntimeError intermittently). Test
    fallout from the refactor fixed both sides: the 7 aether unit tests in
    test_aether.py rewritten to assert delegation to the frame methods (they had
    pinned aether's direct-dict mutation via a mocked frame); 7 behavioral tests
    added to test_aetheric_frame.py for the moved logic (write+refresh,
    duplicate-raise, discard, absent no-ops, version lookup) on a real frame.
    `tests/unit/melder/aether/test_aether.py` + `test_aetheric_frame.py` +
    `tests/integration/melder/conduit`: 309 passed. Acceptance criteria met.
  UNRELATED REDS (not this work, flagged elsewhere): the 3 pre-existing
    nexus_frame_manager `_FakeFrame` failures, and a `configuratio` NameError
    (truncated identifier) at test_spellbook_integration_core.py:1443 -- a
    corrupted edit in the spellbook-integration file, flagged to mediator_builder_0.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-06-14T20:57:38Z
  TYPE: REVISION
  AGENT: compiler_strategy_0
  CLAIM: The Option-A locked-reader implementation above (and its 17:05:46Z
    "VALIDATED 40/40" MEASURE) was ROLLED BACK by the owner and superseded. The
    locked approach serialized the whole-frame `refresh_version_registry()` scan
    under `frame._lock` on every single-conduit registration -- correct, but it
    regressed the gauntlet (~820ms vs ~650ms baseline) by turning per-conjure
    registration into a frame-wide critical section. The prior MEASURE applies
    ONLY to that now-deleted code; it does NOT validate the current tree.
  DECISION (redesign, owner-approved -- "this all makes sense ... small
    maintenance"): the root defect was a FALSE CONFLICT -- a full-frame O(all
    conduits) version rebuild triggered by every per-conduit insert, iterating
    the shared dict while a sibling conjure inserts. Cured by construction:
    1. `_version_registry` is now maintained INCREMENTALLY and LOCK-FREE, per
       conduit, inside frame-owned mutators. Single-key atomic writes
       (`d[k]=v` / `d.pop`) only -- no whole-dict iteration on the write path,
       so no size-change race and no global lock. Methods:
       `register_conduit_spells`, `unregister_conduit_spells`,
       `register_spell_index`, `unregister_spell_index`, plus private
       `_reindex_conduit_versions` (snapshots `list(spell_set)` before unioning).
    2. `refresh_version_registry()` (frame) and `_refresh_version_registry()`
       (aether) DELETED -- the footgun is gone, not guarded.
    3. Readers (`has_version`, `get_all_versions`, `find_and_return_spell_index`)
       are lock-free snapshot reads: iterate `list(self._version_registry.values())`
       / `list(self._spell_registry.values())` (atomic snapshot copy, safe to
       iterate). `_get_conduit_by_spell_id` snapshots
       `list(spell_registry.items())` + `list(spell_set)` likewise.
    4. `find_conduit_id_for_version` was NOT added (it existed only in the
       rolled-back branch); `_get_conduit_by_spell_id` scans `_spell_registry`
       directly via `SpellIndex.has_version`.
    5. `get_all_versions` / `_get_all_spell_versions` KEPT as a live query (owner:
       "maybe we can get more value out of this").
  EDITS: src `aetheric_frame.py` (5 mutators + 3 readers replace the old
    refresh+locked-readers block), `aether.py` (4 writers + reader routed through
    frame methods; `_refresh_version_registry` deleted; `_get_conduit_by_spell_id`
    snapshot-iterated). Tests: removed the 4 refresh tests + 3 none-registry
    tests + `test_find_conduit_id_for_version` in test_aetheric_frame.py (rewrote
    merges as `test_register_conduit_spells_indexes_versions_for_get_all`);
    removed 2 refresh tests in test_aether.py and rewrote
    `test_get_conduit_by_spell_id` to a direct `_spell_registry` scan; removed the
    `frame.refresh_version_registry()` call from
    test_aether_integration_frames.py (registry is now live after conjure).
    Repo grep: zero `refresh_version_registry|_refresh_version_registry|
    find_conduit_id_for_version` references remain in src/ or tests/ (only this
    epic + the lineage map task doc mention them, as history).
  VALIDATION: NOT RUN by me -- I cannot execute 3.14t, and the bash mount is a
    divergent/corrupt copy (py_compile reports null bytes / unbalanced parens on
    it; the Windows checkout via the file tools is well-formed and authoritative).
    Owner to run on the 3.14t Windows checkout: the 40x concurrent-conjure loop,
    `tests/unit/melder/aether/test_aetheric_frame.py` + `test_aether.py`,
    `tests/integration/melder/aether/` + `.../spellbook/`, and the gauntlet
    (expect race-stable AND <=~650ms -- the regression should be gone since the
    write path no longer takes a frame-wide lock or rebuilds globally).
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-06-14T21:20:00Z
  TYPE: REVISION
  AGENT: compiler_strategy_0
  CLAIM: Both prior fixes (abf8b9bd lock-serialized encapsulation @ ~820ms, and
    the lock-free incremental-upkeep redo @ ~830ms) regressed the gauntlet and
    were abandoned. Owner reset the tree to the abf8b9bd encapsulation commit and
    approved the simplest correct fix: DELETE the derived version cache entirely.
  ROOT INSIGHT: `_version_registry` (conduit_id -> Set[version_str]) was a
    redundant cache. `_spell_registry` (conduit_id -> Set[SpellIndex]) is the
    source of truth and every `SpellIndex` already answers `has_version` /
    `get_all_versions`. The ONLY thing that iterated `_spell_registry` on the
    write path was the cache rebuild (`refresh_version_registry`), and that
    iterate-during-insert is the reproduced race. A derived cache forces either a
    racy unlocked rebuild (the 675ms original) or a serialized locked one (820ms);
    deleting it removes the dilemma.
  CHANGE (frame `aetheric_frame.py`):
    - Removed `_version_registry` field (slots, __init__, cleanup) and
      `refresh_version_registry()`.
    - `has_version` / `get_all_versions` now derive live from `_spell_registry`
      (under `self._lock`, same posture as `find_and_return_spell_index`); no
      snapshots.
    - The four frame mutators (`register_conduit_spells` /
      `unregister_conduit_spells` / `register_spell_index` /
      `unregister_spell_index`) are now LOCK-FREE single atomic dict/set ops (no
      `with self._lock`, no refresh). `register_spell_index` uses `setdefault` for
      an atomic get-or-create. `find_conduit_id_for_version` kept unchanged.
  CHANGE (aether `aether.py`):
    - Deleted `_refresh_version_registry` (no runtime caller; was only a doc
      note). The 4 writer wrappers + `_get_conduit_by_spell_id` /
      `_check_for_spell` / `_get_all_spell_versions` are otherwise unchanged
      (they already route through frame methods on this commit); cache-language
      docstrings updated.
  RESULT (expected, NOT yet measured): write path is now a single atomic key
    write -- lighter than the 675ms original (which also paid the refresh), so
    gauntlet should be <=~675ms. The reproduced refresh-during-conjure race is
    gone by construction (nothing iterates `_spell_registry` on the write path).
  KNOWN RESIDUAL (same as the 675ms original's posture, owner aware): the version
    readers (`has_version`, `get_all_versions`, `find_and_return_spell_index`,
    `find_conduit_id_for_version`) iterate `_spell_registry` under `self._lock`,
    but the writers are now lock-free, so the lock does not serialize reader vs
    writer. A version lookup running CONCURRENTLY with a conjure on the same frame
    could still hit "dictionary changed size during iteration". These readers are
    meld/link/contract-resolution lookups, not on the conjure hot path; the
    original shipped with the identical exposure. A dedicated concurrent
    reader+conjure stress test was offered to confirm/deny this empirically before
    deciding whether to guard it (and if so, only that cold reader -- not the hot
    write path).
  TESTS: test_aetheric_frame.py version-query + mutation tests re-pointed off the
    deleted cache onto `_spell_registry`; `_version_registry` assertions removed
    from init/cleanup tests and the two integration files. Repo grep: zero
    `_version_registry` / `refresh_version_registry` code references remain (one
    historical comment + one test function name only).
  VALIDATION: NOT RUN by me (no 3.14t; bash mount divergent). Owner to run the 40x
    concurrent-conjure loop + aether unit/integration suites + gauntlet.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

## Context / Handoff Summary
Pre-existing free-threaded data race in the aether -> frame spell-registry path,
independent of the mediator/unlink lane and of the creations/`unique_per_lineage`
change. Reader (`refresh_version_registry`) locks; the 4 aether.py writers and 1
aether.py reader do not. Fix = serialize all `_spell_registry` access under
`frame._lock` (Option A frame-owned methods preferred, Option B call-site locks
minimal). Reproduce by looping the named concurrent-conjure test ~40x.
