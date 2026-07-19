# Task: Remove Read Locks From Live Probe And Add Existing Only Meld
- Completed: 2026-04-13T12:00:15Z
- Summary: Closed the live-probe read-path cleanup lane after the cold-path `meld_existing_spell(...)` seam landed and the later runtime work built on it as settled substrate.

## Metadata
- Task ID: TASK-2026-04-12-remove-read-locks-from-live-probe-and-add-existing-only-meld
- Story: STORY-2026-04-11-precision-acl-target-model-and-descriptor-validation
- Status: done
- Owner: codex
- Priority: p0
- Created: 2026-04-12T13:29:59Z
- Updated: 2026-04-12T14:10:13Z

## Objective
Remove the extra read-side locks from the live-status probe path and add an
`existing_only` option to `meld(...)` so callers can demand “return an
already-existing object or fail” without triggering creation.

## Ticket Contract
- ENTRY_GATE: the user explicitly directed removal of the read-side locks on
  the live probe path and approved adding an optional existing-only meld path.
- EXECUTION_BOUNDARY: `Meld`, `Conduit` meld wrapper, focused protocol updates,
  focused tests, and board/artifact routing only.
- DEPENDENCIES:
  - src/melder/aether/conduit/meld/meld.py
  - src/melder/aether/conduit/conduit.py
  - src/melder/utilities/interfaces/interfaces.py
  - tests/unit/melder/aether/test_nexus.py
- EXIT_GATE: the live probe path no longer takes extra explicit read locks, an
  `existing_only` meld option exists on the meld seam, and the focused runtime
  ring is green.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if `meld_existing_spell(...)` semantics for
  unsupported lifecycles (`many`, spellspace-bound ambiguity) require broader
  lifecycle policy changes than this tranche should own.

## Scope Boundaries
- In scope:
  - remove explicit read-side locks from the live-status probe path in `Meld`
  - remove the conduit-side wrapper lock on spell-index lookup
  - add `meld_existing_spell(...)` to `Meld` and `Conduit`
  - focused protocol/test updates
- Out of scope:
  - broad lock pass outside this read path
  - static viewer redesign
  - capability handle design

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: the user explicitly approved the narrow read-path lock
  removal and the `existing_only` meld compromise.

## Steps / Checklist
- [x] Stage patch docs and route the new task from the board.
- [x] Remove extra read-side locks from the live probe path in `Meld`.
- [x] Remove the conduit-side spell-index lookup wrapper lock.
- [x] Add `existing_only` to the meld seam.
- [x] Update focused tests.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- lock-stripped live probe path
- `existing_only` meld path
- focused tests

## Files / Paths Impacted
- src/melder/aether/conduit/meld/meld.py
- src/melder/aether/conduit/conduit.py
- src/melder/utilities/interfaces/interfaces.py
- tests/unit/melder/aether/test_nexus.py
- codex/context_compass/attention_board.md
- codex/context_compass/artifact_board.md

## Validation
- Ran:
  - `python -m py_compile src/melder/aether/conduit/meld/meld.py src/melder/aether/conduit/conduit.py src/melder/utilities/interfaces/interfaces.py tests/unit/melder/aether/conduit/meld/test_meld.py tests/unit/melder/aether/conduit/test_conduit_facade.py`
  - `python -m pytest -q tests/unit/melder/aether/conduit/meld/test_meld.py tests/unit/melder/aether/conduit/test_conduit_facade.py`
  - `python -m pytest -q tests/component/melder/aether/conduit/test_conduit_component_creations.py tests/component/melder/aether/conduit/test_conduit_component_meld_gating.py tests/integration/melder/conduit/test_conduit_integration_existence.py`

## Risks / Rollback Notes
- Risk: `meld_existing_spell(...)` accidentally falls through to creation for lifecycles
  where existing retrieval should fail.
  Rollback: fail fast for unsupported/non-live cases and keep creation logic
  unchanged for normal meld calls.

## Applicable Anti-Patterns
- [ ] No status transition without evidence-backed transition reason.
- [ ] No implementation/validation from `UNKNOWN` or `HYPOTHESIS`.
- [ ] No closure without acceptance confirmation and board-sync completion.

## Done Checklist
- [x] Steps complete and checked off
- [x] Deliverables produced and linked
- [ ] Documentation updated (if needed)
- [x] Validation status recorded
- [x] Unknown-first discipline followed (`UNKNOWN` promoted to `FACT` only with evidence)
- [x] Notes quality maintained (`SCORE_0_TO_10` >=
      `workflow.ticket_microcycle.minimum_note_score`)
- [x] Applicable anti-pattern checks are clear or escalated with evidence.
- [ ] Acceptance criteria reviewed with user and confirmed
- [ ] Board sync completed for successor routing or closure anchor update.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - system_docs/patches/active/live_probe_lock_removal_and_existing_only_meld/architecture_patch.md
  - system_docs/patches/active/live_probe_lock_removal_and_existing_only_meld/component_patch_meld.md
  - system_docs/patches/active/live_probe_lock_removal_and_existing_only_meld/component_patch_conduit.md
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: keep until the runtime read-path cleanup and `existing_only`
  meld path are merged into canonical runtime docs or intentionally retired.

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-04-12T13:29:59Z
  TYPE: FACT
  CLAIM: The live probe path still takes explicit read-side locks in
    `Meld._describe_spell_live_creation_status(...)`, and `Conduit.get_spell_by_index_id(...)`
    still wraps Spellbook lookup in an extra conduit lock. For the current
    static/live-check usage, these are observational reads over already
    internally synchronized data structures and do not need extra external
    locking. The user also approved a better retrieval compromise than more
    ad-hoc helpers: add `existing_only` to the meld seam so callers can demand
    reuse-or-fail without triggering creation.
  EVIDENCE:
  - src/melder/aether/conduit/meld/meld.py:634-766
  - src/melder/aether/conduit/conduit.py:1632-1668
  - user_direction: "remove them"
  - user_direction: "add an optional on meld to return if exists instead of generating a new one and to throw if it doesn't"
  IMPACT: We can keep this slice narrow and performance-oriented without
    reopening the broader static/capability design.
  NEXT: create patch docs and implement the read-path lock removal plus the
    `existing_only` meld option.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-12T13:39:20Z
  TYPE: FACT
  CLAIM: The runtime read-path cleanup is now landed in source. The live probe
    path in `Meld._describe_spell_live_creation_status(...)` no longer takes
    the extra explicit read-side locks around creations/owner lookups, and the
    meld seam now carries `existing_only` through both `Meld.meld(...)` and
    `Conduit.meld(...)`. `existing_only=True` now returns an already-live object
    or fails without entering any creation path.
  EVIDENCE:
  - src/melder/aether/conduit/meld/meld.py:217-402
  - src/melder/aether/conduit/meld/meld.py:462-562
  - src/melder/aether/conduit/meld/meld.py:634-763
  - src/melder/aether/conduit/conduit.py:1632-1667
  - src/melder/aether/conduit/conduit.py:2440-2553
  - src/melder/utilities/interfaces/interfaces.py:3471-3489
  - src/melder/utilities/interfaces/interfaces.py:5310-5361
  IMPACT: The static/live-check and reuse-or-fail path now has the explicit
    meld contract the user asked for without the previous extra read locks.
  NEXT: record the focused and nearby validation result, then review whether
    the next step is wiring static command retrieval onto `existing_only` meld
    or cleaning the Spellbook scan locks separately.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-12T13:39:20Z
  TYPE: MEASURE
  CLAIM: The read-path cleanup and `meld_existing_spell(...)` slice is green on the
    focused unit ring and a targeted conduit component/integration ring. The
    updated unit tests for meld/conduit facade behavior pass, and the nearby
    real conduit creation/existence flows still pass with the new meld
    parameter in place.
  EVIDENCE:
  - validation_result: `python -m py_compile src/melder/aether/conduit/meld/meld.py src/melder/aether/conduit/conduit.py src/melder/utilities/interfaces/interfaces.py tests/unit/melder/aether/conduit/meld/test_meld.py tests/unit/melder/aether/conduit/test_conduit_facade.py` -> success
  - validation_result: `python -m pytest -q tests/unit/melder/aether/conduit/meld/test_meld.py tests/unit/melder/aether/conduit/test_conduit_facade.py` -> 123 passed
  - validation_result: `python -m pytest -q tests/component/melder/aether/conduit/test_conduit_component_creations.py tests/component/melder/aether/conduit/test_conduit_component_meld_gating.py tests/integration/melder/conduit/test_conduit_integration_existence.py` -> 19 passed
  IMPACT: This runtime slice is stable enough for review or for the next static
    retrieval step instead of more local repair.
  NEXT: summarize the landed behavior and ask whether to wire static command
    retrieval onto `existing_only` meld or keep going on the lock cleanup lane.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-12T14:10:13Z
  TYPE: DECISION
  CLAIM: The `existing_only` flag approach is now superseded. The user wants
    the hot `meld(...)` path kept as clean as possible, with no extra branch or
    helper-sharing burden on the fast path. The runtime should instead expose a
    separate cold-path method:
    - `Meld.meld_existing_spell(...)`
    - `Conduit.meld_existing_spell(...)`
    This method should carry the same identity inputs as `meld(...)`, but only
    return an already-existing live object or fail without creating.
  EVIDENCE:
  - user_direction: "make a new meld method call it, meld_existing_spell"
  - user_direction: "leave the fast path alone"
  - user_direction: "we do not want shared helpers"
  IMPACT: The current `existing_only` parameter should be removed from the meld
    seam and replaced with a distinct cold-path method before we build more on
    top of it.
  NEXT: remove `existing_only` from `Meld.meld(...)` and `Conduit.meld(...)`,
    add `meld_existing_spell(...)` on both surfaces, and update the focused
    tests.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-12T14:11:50Z
  TYPE: FACT
  CLAIM: The lifecycle support contract for the new cold-path retrieval method
    is now explicit. `meld_existing_spell(...)` should support only lifecycles
    that can resolve to one deterministic already-live object:
    - existing user-created object
    - `unique_per_conduit`
    - `unique`
    - `unique_per_conduit_cluster`
    - `unique_per_conduit_lineage`
    - `unique_per_spell_space` when an active spellspace exists
    It should fail fast for `many`, because picking one instance out of a many
    bucket is not acceptable.
  EVIDENCE:
  - user_direction: "this shouldn't work on all existences"
  - user_direction: "no we don't reject unique per spellspace, if there is a spellspace active we return that unique"
  IMPACT: The new cold-path retrieval method can stay narrow and deterministic
    without inventing policy for ambiguous lifecycles.
  NEXT: implement `meld_existing_spell(...)` on `Meld` and `Conduit` with this
    exact lifecycle support matrix and remove the current `existing_only`
    parameter from the hot `meld(...)` path.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-12T14:10:13Z
  TYPE: FACT
  CLAIM: The final runtime seam now matches the superseding design. The hot
    `meld(...)` path no longer carries the `existing_only` branch, and the
    cold-path reuse-only behavior now lives on:
    - `Meld.meld_existing_spell(...)`
    - `Conduit.meld_existing_spell(...)`
    The implementation supports:
    - existing object
    - `unique_per_conduit`
    - `unique`
    - `unique_per_conduit_cluster`
    - `unique_per_conduit_lineage`
    - `unique_per_spell_space` with an active spellspace
    and rejects:
    - `many`
  EVIDENCE:
  - src/melder/aether/conduit/meld/meld.py:217-397
  - src/melder/aether/conduit/meld/meld.py:397-538
  - src/melder/aether/conduit/conduit.py:2440-2554
  - src/melder/aether/conduit/conduit.py:2557-2628
  - src/melder/utilities/interfaces/interfaces.py:3491-3501
  - src/melder/utilities/interfaces/interfaces.py:5395-5422
  IMPACT: The runtime now preserves the fast `meld(...)` path while still
    providing the explicit reuse-only seam static or other callers can target.
  NEXT: summarize the landed seam and decide whether the next step is wiring
    static command retrieval onto `meld_existing_spell(...)` or cleaning the
    remaining Spellbook scan locks.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
This task strips extra read-side locks from the live probe path and adds an
explicit `existing_only` option to the meld seam.

