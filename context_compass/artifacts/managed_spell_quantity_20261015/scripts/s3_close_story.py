"""S3 turn-in: Notes, completion summary, status, state transition, tasks and handoff of the pool story."""
import pathlib
import sys

NOW = sys.argv[1]
PATH = pathlib.Path("context_compass/tickets/stories/2026-10-15_managed_quantity_pool_story.md")
text = PATH.read_text(encoding="utf-8")


def swap(old: str, new: str) -> None:
    global text
    assert text.count(old) == 1, old[:80]
    text = text.replace(old, new)


swap(
    "# Story: managed_quantity_pool - ManagedSpellQuantity, the exhaustion error and the pools in the root's Creations\n",
    "# Story: managed_quantity_pool - ManagedSpellQuantity, the exhaustion error and the pools in the root's Creations\n"
    "\n"
    f"- Completed: {NOW}\n"
    "- Summary: landed 0.2.8243 - `ManagedSpellQuantity` (the pool: sizes per mode, reserve, put_back, abandon,\n"
    "  adopt, destroy_object, cleanup, describe), `ManagedSpellExhaustedError`, the Creations pool map (ensure/get,\n"
    "  pools cleaned first, the `managed` extract/restore row, purge 0), owner stamping, the meld-door probes and\n"
    "  purge store, the static rooms. Release-note section \"`Existence.managed_spell_quantity`: objects leased from a\n"
    "  root-owned pool and released back\" extended.\n",
)
swap("- Status: in_progress\n", "- Status: done\n")
swap("- Updated: 2026-10-15T12:54:26Z\n", f"- Updated: {NOW}\n")
swap(
    """## State Transition Event
- from_state: ready
- to_state: in_progress
- transition_reason: S2 closed (0.2.8242, corrected to TYPE_CHECKING by owner ruling); S3 starts.
""",
    """## State Transition Event
- from_state: in_progress
- to_state: done
- transition_reason: acceptance criteria met with red-then-green tests in both GIL modes and the touched unit,
  component and integration suites green; notched 0.2.8243 (delegated routine closure under the owner's go-ahead).
- earlier: ready -> in_progress (S2 closed, 0.2.8242, corrected to TYPE_CHECKING by owner ruling; S3 started).
""",
)
swap(
    """- [ ] Red tests: per-mode unit tests, the multithreaded stress test, Creations integration tests.
- [ ] Implement; green in both GIL modes; the creations and conduit suites.
- [ ] Notch, release note, epic spec update, close, board sync.
- [ ] Enforce Ticket Microcycle across all linked tasks.
- [ ] Record meaningful attributed findings in supported Notes/comments or authorized linked evidence.
""",
    """- [x] Red tests: per-mode unit tests, the multithreaded stress test, Creations integration tests.
- [x] Implement; green in both GIL modes; the creations and conduit suites.
- [x] Notch, release note, epic spec update, close, board sync.
- [x] Enforce Ticket Microcycle across all linked tasks.
- [x] Record meaningful attributed findings in supported Notes/comments or authorized linked evidence.
""",
)
notes = f"""- DATETIME: {NOW}
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: S3 built. `ManagedSpellQuantity(AbstractElasticPool)` sizes itself per mode (elastic min(20, limit) /
    limit with the kernel defaults; limited and queue fixed at the limit); `reserve` counts a place under the leaf
    lock (elastic also notes pressure), refuses a full limited pool, waits a queue on a Condition over the base
    lock with one deadline; `put_back` runs resets outside every lock, destroys on a raising reset and propagates,
    notifies a queue waiter and runs the base elastic band; `adopt`/`abandon`/`destroy_object` keep id-keyed
    children records (orphans on id reuse); `create_object` and `acquire` refuse; `cleanup` drains under the lock
    (popleft per object), swaps the maps, wakes all waiters, disposes outside and aggregates. The error is
    `ManagedSpellExhaustedError(MeldExecutionError)`. Creations keeps `_managed_quantities` (ensure, get, pools
    cleaned before the registry with failures flattened into the store's group, the `managed` extract/restore row,
    purge 0); `Spell._add_owned_conduit` ensures for managed spells; ConduitMeld purges managed from the caller's
    store (0); both probes answer from the owner store's pool through `Meld._describe_managed_pool_status`; the
    static rooms treat managed like `many`.
  EVIDENCE:
  - src/melder/aether/conduit/creations/managed_spell_quantity.py:14-890
  - src/melder/utilities/custom_exceptions/managed_spell_exhausted_error.py:1-174
  - src/melder/aether/conduit/creations/creations.py:320-390
  - src/melder/aether/conduit/creations/creations.py:1108-1210
  - src/melder/aether/conduit/creations/creations.py:1437-1644
  - src/melder/aether/spellbook/spell.py:1661-1718
  - src/melder/aether/conduit/meld/conduit_meld.py:211-280
  - src/melder/aether/conduit/meld/meld.py:773-811
  - src/melder/nexus/rift/command_system/static_command_system.py:205-245
  IMPACT: S4 registers pools where a store takes or gives one up (ensure, extract, restore, cleanup); S5 leases
    through `_idle.pop()`, `reserve`, `abandon` and `adopt`; S6 moves the pool as a store row.
  NEXT: Notch, release note, closure.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: {NOW}
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: DECISION
  CLAIM: Choices made inside the patch. (1) A limited pool at its limit serves an object released since the plan's
    empty pop instead of refusing, so the refusal always means every object is out. (2) `adopt` into a torn-down pool
    disposes the object and its children and raises the torn-down error (a retired pool owns nothing, as Creations
    refuses a publish into a cleaned store). (3) After cleanup the pool keeps its scalar fields as documented
    tombstones and deletes the borrowed Spell, so plans, waiters and releases racing teardown reach the torn-down
    RuntimeError. (4) `ensure` re-points a kept pool at a Spell rebound under the same id. (5) `meld_existing_spell`
    keeps its generic refusal for managed; no branch was needed. (6) The probe helper sits on the Meld base, shared
    by both doors. (7) The component purge test that iterated `list(Existence)` (written for six members) now covers
    the six storing lifetimes, and a new test pins managed purge: 0, no lock taken, pool kept.
  EVIDENCE:
  - src/melder/aether/conduit/creations/managed_spell_quantity.py:429-459
  - src/melder/aether/conduit/creations/managed_spell_quantity.py:612-657
  - src/melder/aether/conduit/creations/managed_spell_quantity.py:191-250
  - src/melder/aether/conduit/meld/conduit_meld.py:733-890
  - tests/component/melder/aether/conduit/test_conduit_component_purge.py:580-668
  IMPACT: S5's miss can rely on reserve never refusing while an object is idle; S4 must read a pool's Spell only
    through `spell` (it raises after cleanup).
  NEXT: Turn in S3, then S4.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: {NOW}
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: MEASURE
  CLAIM: Red then green on the device VM (CPython 3.14.7t). Red: the five new modules' tests failed to import and
    the store-reader, static-room and stamp tests failed (10 failed, 5 passed; the static-viewer test was then
    tightened to fail red). Green in both GIL modes: the new tests plus the purge component file (190); unit aether
    and spellbook (6792), the rest of unit (1970); component spellbook (819) and the rest (1545; its two failures
    before the test fix were the six-member purge test meeting managed); integration aether (785) and multithreading
    (54); conduit (308, gil0), conduit + spellbook + MR + live_sim (995, gil1), spellbook + MR + live_sim (687,
    gil0); a crystallizer smoke shard (restore part 0 and the managed record suite, 19, gil0). Not run: the rest of
    the crystallizer integration tree (S3 changes no crystallizer code). Density: 67 pool tests for 330 code lines
    (20.3 per 100).
  EVIDENCE:
  - context_compass/artifacts/managed_spell_quantity_20261015/runs/s3_red_gil0.txt:1-40
  - context_compass/artifacts/managed_spell_quantity_20261015/runs/s3_green_new_gil0.txt:1-3
  - context_compass/artifacts/managed_spell_quantity_20261015/runs/s3_green_new_gil1.txt:1-8
  - context_compass/artifacts/managed_spell_quantity_20261015/runs/s3_component_rest_gil0.txt:1-25
  IMPACT: The pool and its store integration are proven in both modes; the touched suites hold.
  NEXT: Notch 0.2.8243, release note, close, board sync, rebuild.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

"""
swap("## Closure Confirmation\n", notes + "## Closure Confirmation\n")
swap(
    """## Context / Handoff Summary
- Scope: S3 - the pool, the error, Creations.
- State: ready, blocked on S2.
- Next: read the U3-U6/U10 sites.
""",
    """## Context / Handoff Summary
- Scope: S3 - the pool, the error, Creations, owner stamping, the store readers, the static rooms.
- State: done; landed 0.2.8243 (Notes of the completion datetime).
- Next: S4 (STORY-2026-10-15-release_managed_spell) registers the pools with `ReleaseManagedSpell`.
""",
)
PATH.write_text(text, encoding="utf-8")
print("story closed in place")
