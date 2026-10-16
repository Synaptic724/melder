# Story: managed_quantity_pool - ManagedSpellQuantity, the exhaustion error and the pools in the root's Creations

- Completed: 2026-10-15T13:54:48Z
- Summary: landed 0.2.8243 - `ManagedSpellQuantity` (the pool: sizes per mode, reserve, put_back, abandon,
  adopt, destroy_object, cleanup, describe), `ManagedSpellExhaustedError`, the Creations pool map (ensure/get,
  pools cleaned first, the `managed` extract/restore row, purge 0), owner stamping, the meld-door probes and
  purge store, the static rooms. Release-note section "`Existence.managed_spell_quantity`: objects leased from a
  root-owned pool and released back" extended.

## Metadata
- Story ID: STORY-2026-10-15-managed_quantity_pool
- Epic: EPIC-2026-10-14-managed_spell_quantity (tickets/epics/2026-10-14_managed_spell_quantity_epic.md); story 3 of 7
- Status: done
- Owner: user
- Agent Name: melder_0
- Agent Role: synaptic_python_developer
- Priority: p1
- Created: 2026-10-15T09:29:51Z
- Updated: 2026-10-15T13:54:48Z

## User Narrative
As an agent, I want each managed spell's objects kept in a pool owned by its root, reused on the next lease and
disposed with the root, so that a pooled object costs a deque pop instead of a build.

## Value / MRP Alignment
The pool is the structure Melder must get right: accounting per mode, the queue's wait, elastic retention reused from
the kernel pools, disposal of idle objects and recorded children, and a store integration that no resolution path can
mistake for an object.

## Ticket Contract
- ENTRY_GATE: S2 closed;
  system_docs/patches/active/managed_spell_quantity_2026_10_15/component_patch_managed_quantity_pool.md and
  system_docs/patches/active/managed_spell_quantity_2026_10_15/code_description_patch_managed_quantity_pool.md
  (concurrency, state machine) written and linked; U3-U6 and U10 answered from source; the mapping note recorded.
- EXECUTION_BOUNDARY: src/melder/aether/conduit/creations/managed_spell_quantity.py (new),
  src/melder/utilities/custom_exceptions/managed_spell_exhausted_error.py (new),
  src/melder/aether/conduit/creations/creations.py, src/melder/aether/spellbook/spell.py (`_add_owned_conduit`),
  src/melder/aether/conduit/meld/conduit_meld.py and spellspace_meld.py (store readers); their tests.
  AbstractElasticPool is reused, not changed.
- DEPENDENCIES: S2 (the Spell fields).
- EXIT_GATE: its tests green under `-X gil=0` and `-X gil=1`; the touched modules' existing suites green; one notch
  taken from `__version__` at landing with the running release note's managed section extended; the epic's Build
  Specification updated with what this story settled; story closed (completed folder, board sync)
- FAILURE_ESCALATION: DECISION_REQUEST if a change would alter an existing member's behaviour, an existing spell id or
  record, or the frame -> conduit -> Book lock order; CONFLICT when the source contradicts the epic's Build
  Specification (fix the spec first); BLOCKER when a gate cannot be met

## Requirements (Functional)
- ManagedSpellQuantity as in the epic's B2: sizes per mode, `reserve`, `put_back`, `abandon`, `adopt`,
  `destroy_object`, `create_object` refusing, `cleanup`, `describe`; no reference to out objects.
- ManagedSpellExhaustedError (a MeldExecutionError) with the B11 texts.
- Creations as in B3: `_managed_quantities`, `ensure_managed_quantity` (called from `_add_owned_conduit` for managed
  spells), pools disposed before the disposable registry, the `managed` extract/restore row.
- Store readers: purge of a managed spell returns 0 and touches nothing; the live-creation probe answers from the pool
  (U4).

## Requirements (Non-Functional)
- Warm paths lock-free; the pool lock a leaf; no user code under any Melder lock.
- At least 20 tests per 100 LOC of the pool (concurrency and lifecycle code).

## Scope Boundaries
- In scope: the pool class, the error, Creations, owner stamping, the store readers.
- Out of scope: the registry calls (S4 wires register/unregister), codegen (S5), transfer (S6).

## State Transition Event
- from_state: in_progress
- to_state: done
- transition_reason: acceptance criteria met with red-then-green tests in both GIL modes and the touched unit,
  component and integration suites green; notched 0.2.8243 (delegated routine closure under the owner's go-ahead).
- earlier: ready -> in_progress (S2 closed, 0.2.8242, corrected to TYPE_CHECKING by owner ruling; S3 started).

## Dependencies / Related Work
- EPIC-2026-10-14-managed_spell_quantity Build Specification B2, B3, B9, B10; the elastic FACT note of
  2026-10-15T08:52:31Z.

## Tasks (Implementation Checklist)
- [x] Read AbstractElasticPool cleanup and describe (U6), the kernel pool arguments in Conduit.__init__ (U5),
      Creations clear_all / reset_for_pool (U3), the ConduitMeld / SpellSpaceMeld readers (U4),
      define_conduit_into_spells (U10).
- [x] Component and code-description patches; mapping note.
- [x] Red tests: per-mode unit tests, the multithreaded stress test, Creations integration tests.
- [x] Implement; green in both GIL modes; the creations and conduit suites.
- [x] Notch, release note, epic spec update, close, board sync.
- [x] Enforce Ticket Microcycle across all linked tasks.
- [x] Record meaningful attributed findings in supported Notes/comments or authorized linked evidence.

## Acceptance Criteria
- Per mode: accounting, refusal, waits, timeouts, served-by-release, trims, resets, raising resets.
- Stress: limited_quantity never exceeds its limit; queue never hangs.
- Teardown disposes idle objects and every recorded child; purge leaves managed spells untouched.

## Validation / Test Plan
- tests/unit/melder/aether/conduit/creations/test_managed_spell_quantity.py,
  test_managed_spell_quantity_multithreaded.py, test_creations_managed_quantities.py; both GIL modes.

## UX / API / Data Notes
- Public: ManagedSpellExhaustedError (root export with S4).

## Risks / Mitigations
- Destroy failures during teardown -> one ExceptionGroup shaped like Creations'.
- A late release after teardown -> RuntimeError naming the spell (B11).

## Applicable Anti-Patterns
- [ ] No story-state transition without linked task-state evidence.
- [ ] No closure while required tasks remain active or un-routed.
- [ ] No cross-task synthesis claims without ticket-note evidence pointers.
- [ ] No `src/` edit before the component patch and the mapping note exist.

## Open Questions
- U3, U4, U5, U6, U10 (epic B2/B3) - read in source before the patch.

## Decision Log
- 2026-10-15 (melder_0): pools in their own map, disposed first (epic Decision Log).

## Artifact Links (Optional)
Qualified independent reviewer acceptance and direct closure follow shared `ticketing.md`;
this does not make independent review mandatory for every ticket.

- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - system_docs/patches/active/managed_spell_quantity_2026_10_15/architecture_patch.md
  - system_docs/patches/active/managed_spell_quantity_2026_10_15/component_patch_managed_quantity_pool.md
  - system_docs/patches/active/managed_spell_quantity_2026_10_15/code_description_patch_managed_quantity_pool.md
  - artifacts/managed_spell_quantity_20261015/ (this story's runs and scripts)
- DISPOSITION: promote_to_documentation (patch docs); retain_as_reference (artifacts)
- CLEANUP_TRIGGER: patch docs promoted and archived at S7; artifacts retained

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS:
  - none
- CONTEXT_TOPICS:
  - the ManagedSpellQuantity pool and its Creations integration
- IF_UNKNOWN: none

## Contribution Attribution
- Ticket/Work Author(s): melder_0 (synaptic_python_developer); prose, design, implementation and tests of this story;
  created 2026-10-15T09:29:51Z; evidence in Notes.
- Published By: UNKNOWN (a local ticket file; not published)
- Independent Review: none yet

## Notes
- DATETIME: 2026-10-15T09:29:51Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: PLAN
  CLAIM: Opened ready behind S2. Model: fable_0's probe_deque_holder.py (the settled shape) on AbstractElasticPool's
    retention; Creations cleanup 306-363, extract 1302-1375, restore 1377-1474.
  EVIDENCE:
  - context_compass/artifacts/managed_shell_spike_20261014/probe_deque_holder.py:28-104
  - src/melder/utilities/general_base/abstract_elastic_pool.py:13-599
  - src/melder/aether/conduit/creations/creations.py:306-363
  IMPACT: Names the read set for U3-U6 and U10.
  NEXT: Start after S2 closes.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-15T09:32:42Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: PLAN
  CLAIM: Carried from S1's search: the Nexus static rooms treat many and unique_per_spell_space as having no stored
    object (no static access, never "live"); a managed spell has no stored object either and joins those sets here,
    together with `meld_existing_spell`'s managed branch (the reuse-only meld finds nothing stored for it).
  EVIDENCE:
  - src/melder/nexus/rift/command_system/static_command_system.py:195-240
  - src/melder/nexus/rift/command_system/static_command_system.py:615-635
  - src/melder/nexus/rift/frame_viewer/static_frame_viewer.py:280-300
  IMPACT: Adds two Nexus files to S3's boundary.
  NEXT: Read `meld_existing_spell` and the static-room callers when S3 starts.
  REREAD: REQUIRED
  SCORE_0_TO_10: 7

- DATETIME: 2026-10-15T12:51:09Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: U3-U6 and U10 read in source on 0.2.8242. U6: `AbstractElasticPool.cleanup` marks cleaned, destroys the idle
    objects one by one UNDER `_lock`, stops at the first raising destroy (the rest stay idle, undestroyed) and keeps
    every field; a trim destroys outside the lock and re-pools the rest when one raises; a fixed-capacity pool
    (`max_idle == baseline_idle`) evicts the oldest on a return above the baseline. U5: Conduit builds both kernel pools
    with `baseline_idle=20, max_idle=256` and every other argument defaulted (stretch 0, settle 1800 s, decay 10% per
    600 s). U3: `reset_for_pool` (and `clear_all` through it) runs only on a lesser's store at pool return and a
    spellspace's store at exit - never on a root store. U4: `ConduitMeld._get_purge_creations` raises "Unsupported
    purge existence" for managed, `SpellSpaceMeld.purge` refuses all but many / unique_per_spell_space ("purge it from
    its authorized conduit"), and both live-creation probes raise "Unsupported existence". U10: conjure stamps only the
    Book's active spells (`define_conduit_into_spells` walks `_spells`); a post-conjure bind or bind_inactive stamps the
    new spell, the transfer flip stamps the active member, and `_apply_notch` stamps nothing - a version parked before
    conjure has no owner store until a later stamp (true for every existence today).
  EVIDENCE:
  - src/melder/utilities/general_base/abstract_elastic_pool.py:228-249
  - src/melder/utilities/general_base/abstract_elastic_pool.py:480-599
  - src/melder/aether/conduit/conduit.py:350-366
  - src/melder/aether/conduit/conduit.py:655-690
  - src/melder/aether/conduit/spell_space/spell_space.py:290-300
  - src/melder/aether/conduit/spell_space/spell_space.py:415-445
  - src/melder/aether/conduit/creations/creations.py:1082-1300
  - src/melder/aether/conduit/creations/creations.py:1302-1572
  - src/melder/aether/conduit/meld/conduit_meld.py:150-270
  - src/melder/aether/conduit/meld/conduit_meld.py:983-1104
  - src/melder/aether/conduit/meld/spellspace_meld.py:174-239
  - src/melder/aether/conduit/meld/spellspace_meld.py:895-1045
  - src/melder/aether/spellbook/spellbook_creation_system.py:1331-1376
  - src/melder/aether/spellbook/spell.py:1661-1711
  - src/melder/aether/spellbook/spellbook.py:3826-4000
  IMPACT: The pool overrides cleanup (detach under the lock, destroy outside it, aggregate); elastic is baseline
    min(20, limit) / max limit with the kernel defaults; clear and reset never meet a pool; purge routes managed to a
    store that returns 0; the probes answer from the owner store's pool; ensure runs at every stamp and the S5 miss
    must not assume a pool exists.
  NEXT: Write the component and code-description patches and the mapping note.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-15T12:54:26Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: PLAN
  CLAIM: Patch-section -> implementation -> validation mapping (read after the architecture patch). Pool sizes and
    state -> `ManagedSpellQuantity.__init__` from the Spell -> unit sizes per mode. reserve per mode -> `reserve` ->
    accounting, limited refusal (type, text), queue wait / timeout / served-by-release / woken by cleanup. put_back ->
    reset order, raising reset (destroy, free, propagate), trim through the base rebalance with a fake clock, after
    cleanup. abandon / adopt / destroy_object -> notes on the build error, orphan records, children disposal, count.
    cleanup -> detach under the lock, destroy outside, aggregate, idempotent. Error type -> new
    `ManagedSpellExhaustedError(MeldExecutionError)` -> unit. Creations -> `_managed_quantities`, ensure / get,
    cleanup order (pools first), extract / restore rows, purge 0 -> Creations unit tests. Spell stamping ->
    `_add_owned_conduit` ensures for managed spells -> integration (conjure, post-conjure bind and bind_inactive, root
    teardown). Meld doors -> ConduitMeld purge store and both probes -> unit with doubles plus integration. Stress ->
    multithreaded file (limited never above N; queue no hang). Red first, both GIL modes.
  EVIDENCE:
  - context_compass/system_docs/patches/active/managed_spell_quantity_2026_10_15/architecture_patch.md:1-106
  - context_compass/system_docs/patches/active/managed_spell_quantity_2026_10_15/component_patch_managed_quantity_pool.md:1-83
  - context_compass/system_docs/patches/active/managed_spell_quantity_2026_10_15/code_description_patch_managed_quantity_pool.md:1-60
  IMPACT: The S3 patch gate is met: both patches exist, are linked, and every section maps to code and a test.
  NEXT: Write the red tests.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-15T13:54:48Z
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

- DATETIME: 2026-10-15T13:54:48Z
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

- DATETIME: 2026-10-15T13:54:48Z
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
  - context_compass/artifacts/managed_spell_quantity_20261015/runs/s3_red_gil0.txt:1-60
  - context_compass/artifacts/managed_spell_quantity_20261015/runs/s3_green_new_gil0.txt:1-4
  - context_compass/artifacts/managed_spell_quantity_20261015/runs/s3_green_new_gil1.txt:1-12
  - context_compass/artifacts/managed_spell_quantity_20261015/runs/s3_component_rest_gil0.txt:1-23
  IMPACT: The pool and its store integration are proven in both modes; the touched suites hold.
  NEXT: Notch 0.2.8243, release note, close, board sync, rebuild.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

## Closure Confirmation
- [ ] Work walkthrough shared with user
- [ ] Criteria, required tests/reviews and delegated acceptance or reserved-owner disposition recorded
- [ ] Applicable anti-pattern checks are clear or escalated with evidence.

## Noting Behavior
- Note focus: cross-task synthesis, dependency flow, and state-transition logic.
- Add notes when task routing changes, gate decisions are made, or risks shift.
- Reference child-task notes for evidence instead of duplicating tactical detail.
- Keep notes append-only and preserve UNKNOWN-first promotion discipline.
- Multiple meaningful comments may hold evidence directly; no forced body copy before ordinary
  continuation. Current scope/state/decisions/handoff stay coherent at material transitions.

## Context / Handoff Summary
- Scope: S3 - the pool, the error, Creations, owner stamping, the store readers, the static rooms.
- State: done; landed 0.2.8243 (Notes of the completion datetime).
- Next: S4 (STORY-2026-10-15-release_managed_spell) registers the pools with `ReleaseManagedSpell`.

## Project-Specific Additions
<!-- BEGIN USER-DEFINED: project_fields -->
<!-- END USER-DEFINED: project_fields -->

<!--
Anything this project needs on every ticket of this kind goes in the region
above: extra fields, a compliance checklist, a link to a local convention.

The region is yours. An upgrade replaces every other line of this template with
the new version's text and carries this region across untouched, so a local
addition here is not a divergence you re-resolve on every upgrade - which is
what editing the rest of the template would cost you.
-->
