# Task: Hold the compiled executor in the warm meld entry - drop the forwarding lane frame if the slot swap allows

## Metadata
- Completed: 2026-09-27T22:26:33Z
- Summary: Dropped on evidence: the executor slots are self-replacing (cold -> hot on first execution; with the
  opt-in specializer hot -> specialized and a deopt re-pin later), so a held executor saves ~10 ns (or ~20 on
  `many` roots by skipping the route door) at the cost of a kernel contract and the specializer. No source
  landed; no notch.
- Task ID: TASK-2026-09-27-hold-executor-in-warm-entry
- Story: STORY-2026-09-27-pgo-strategy-exploration
- Status: done
- Owner: cowork
- Agent Name: fable_0
- Priority: p2
- Created: 2026-09-27T22:24:23Z
- Updated: 2026-09-27T22:26:33Z

## Objective
A warm hit calls `captured_context._no_overrides_instance_executor(meld)`, a forwarding closure that calls the
compiled builder: one Python frame (~20 ns, 3-4 points of a warm creation on the VM). The entry could hold the
builder itself if the slot never swaps in place after the successful meld that mints the entry. Today's rule
(read per hit) exists because phase-11 hydration swaps the slot on first execution (cold door -> hot door). The
task reads every writer of the executor slots to decide whether a later in-place swap exists (specialization,
deopt, rehydration) and, only if none can follow the mint, changes the four readers to call the held builder.
Lands after melder_0's scope-exit lane (M0-63/F0-5), because it touches `conduit.py` and `spell_space.py` again.

## Ticket Contract
- ENTRY_GATE: routed on `attention_board.md`; owner: "keep iterating" (2026-09-27T22:24:23Z); melder_0's ACK on
  F0-5 before any edit to conduit.py/spell_space.py.
- EXECUTION_BOUNDARY: reads of `creation_context.py` and the three hydrators (solo, many_only, generalized) and
  the specializer; edits only in the four readers, the two mints and `Meld` (entry shape), with patch docs first;
  tests under `tests/component/melder/aether/conduit/`.
- DEPENDENCIES: the closed task 0d (name/class registry); melder_0's landing on the front-door files.
- EXIT_GATE: either a FACT that a later in-place swap exists (lever dropped, task closes with the evidence) or the
  change landed with tests proving specialization/deopt/rehydration still take effect through a held executor,
  suites green on the VM, measured on the dispatch experiment.
- FAILURE_ESCALATION: BLOCKER if the read finds a swap the entry cannot observe; DECISION_REQUEST if the gain
  measures under 3% on the shapes people write.

## Scope Boundaries
- In scope: the executor slot lifecycle; the entry shape; the four readers' call.
- Out of scope: PGO proper; codegen changes; anything in melder_0's claimed files beyond the two warm lanes.

## State Transition Event
- from_state: in_progress
- to_state: done
- transition_reason: The read settled it (self-replacing slots, specializer swaps after the mint);
  dropped 2026-09-27T22:26:33Z.

## Steps / Checklist
- [x] Read every writer of `_no_overrides_instance_executor` / `_overrides_executor` (context init, the three
      hydrators, the specializer) and classify each as first-execution swap or later swap.
- [x] Decide: hold the builder (with which guard) or drop the lever; record the FACT/DECISION (dropped).
- [ ] If held: patch docs, entry shape change in `Meld`, both mints, the four readers; tests for specialization,
      deopt and rehydration through a held executor; suites; experiment; land after melder_0's ACK.
- [x] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [x] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- The swap-lifecycle FACT with evidence; the lever landed or dropped on it.

## Files / Paths Impacted
- src/melder/aether/conduit/meld/creation_context/creation_context.py (read)
- src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/*/hydration/*.py (read)
- src/melder/aether/conduit/meld/meld.py, conduit_meld.py, spellspace_meld.py, conduit.py, spell_space.py
  (edit, if held)

## Validation
- Not run.
- Recommended commands:
  - `python -X gil=0 -m pytest tests/component/melder/aether/conduit -q -p no:cacheprovider`
  - `python -X gil=0 tests/experimentation/meld_entry_dispatch_experiment.py`

## Risks / Rollback Notes
- A held executor that outlives an in-place swap serves a stale door (a deopt missed is a correctness bug); the
  read decides before any edit. Rollback: the four readers go back to the per-hit slot read.

## Applicable Anti-Patterns
- [x] No status transition without evidence-backed transition reason.
- [x] No implementation/validation from `UNKNOWN` or `HYPOTHESIS`.
- [x] No closure without acceptance confirmation and board-sync completion.
- [x] No edit to conduit.py/spell_space.py before melder_0's ACK on F0-5 (none made).

## Done Checklist
- [x] Steps complete and checked off
- [x] Deliverables produced and linked
- [x] Documentation updated (if needed) - none needed
- [x] Validation status recorded (no code change; Not run)
- [x] Unknown-first discipline followed (`UNKNOWN` promoted to `FACT` only with evidence)
- [x] Notes quality maintained (`SCORE_0_TO_10` >=
      `workflow.ticket_microcycle.minimum_note_score`)
- [x] Applicable anti-pattern checks are clear or escalated with evidence.
- [x] Acceptance criteria reviewed with user and confirmed (owner: close own tickets)
- [x] Board sync completed for successor routing or closure anchor update.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: false
- ARTIFACT_PATHS:
  - none yet (patch docs only if the lever is held)
- DISPOSITION: promote_to_documentation
- CLEANUP_TRIGGER: at closure.

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS:
  - none
- CONTEXT_TOPICS:
  - executor slot lifecycle; hydration; specialization; deopt
- IF_UNKNOWN: none

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-09-27T22:24:23Z
  TYPE: PLAN
  CLAIM: Slot writers found by search (to be READ, not trusted from the hit list): `CreationContext.__init__`
    (creation_context.py:166-168), `solo_hydrator.py:162-168`, `many_only_hydrator.py:162-168`,
    `generalized_hydrator.py:214-234` and three later sites at 658, 723 and 742 that look like the singleton
    specializer's swap and deopt. If the generalized family swaps after the first execution, a held executor is
    unsafe there; the solo and many_only families may still qualify.
  EVIDENCE:
  - src/melder/aether/conduit/meld/creation_context/creation_context.py:160-170
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/generalized/hydration/generalized_hydrator.py:640-760
  IMPACT: The read decides the lever; nothing is edited before it.
  NEXT: read `creation_context.py` whole and `generalized_hydrator.py` 600-760, then the two small hydrators.
  REREAD: REQUIRED
  SCORE_0_TO_10: 7

- DATETIME: 2026-09-27T22:26:33Z
  TYPE: FACT
  CLAIM: Read whole: `CreationContext` (class contract: the executor slots are SELF-REPLACING; readers must re-read
    per call), the solo hydrator's cold->hot swap (`_cold_no_overrides_door` hydrates once and `_swap_hot_doors`
    publishes all three slots on first execution; never again), the generalized hydrator's first publish
    (`_hydrate_once`/`_swap_hot_doors`, same shape) and its later sites: with
    `generalized_singleton_specialization_enabled` (default False) a specializing wrapper is installed, it swaps
    the instance slot hot -> specialized on a LATER call after a post-success attempt on the leader thread,
    `_deopt_notify` re-pins the plain doors after 3 guard misses, and a rebuilt context re-publishes the resolved
    door on its next wrapper call. So with the default configuration the slot is stable after the mint until the
    context is replaced (caught by the identity guard); with the opt-in specializer it swaps twice more.
    What holding would save: the entry already unpacks the context, so holding the same door saves one
    attribute load (~10 ns); the prototype's 3-4 points came from holding the INNER executor and skipping the
    route door, which is only possible for `many` roots (the other routes' door IS the store read) and bypasses
    the door's posture logic and the specializer.
  EVIDENCE:
  - src/melder/aether/conduit/meld/creation_context/creation_context.py:12-110
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/solo/hydration/solo_hydrator.py:150-175
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/generalized/hydration/generalized_hydrator.py:196-240
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/generalized/hydration/generalized_hydrator.py:600-758
  - src/melder/aether/spellbook/configuration/spellbook_configuration.py:152-156
  IMPACT: The lever buys ~10 ns generally or ~20 ns on `many` roots, breaks a documented kernel contract and the
    opt-in specializer's swap/deopt, and needs posture special-casing in four readers: not worth the squeeze.
  NEXT: close this task as dropped on the evidence; the warm lane is at its floor short of an API change.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-27T22:26:33Z
  TYPE: DECISION
  CLAIM: Lever dropped. The remaining per-meld cost on the user paths is `Conduit.meld`'s own frame and keyword
    marshaling (~150 of the 177 ns of a direct singleton meld on the VM) plus the constructor; the guard ladder
    is four loads. The only bigger cut would be a leaner public entry shape (positional-only or item access),
    which is an API question for the owner, not an optimization. One free tip for users: passing the class
    positionally (`conduit.meld(Cls)`) avoids the keyword marshaling of `spell=Cls` (~25-40 ns measured).
  EVIDENCE:
  - artifacts/pgo_strategies_20260927/door_and_site_attribution_20260927.md
  - artifacts/pgo_strategies_20260927/vm_meld_entry_dispatch_after_change_gil0_20260927.md
  IMPACT: The exploration story's levers are exhausted at the door; PGO proper parked; the story can close.
  NEXT: none.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

## Context / Handoff Summary
STATE 2026-09-27T22:24:23Z: IN_PROGRESS. Opened; the swap-lifecycle read is next. Resume from the latest note's NEXT.
STATE 2026-09-27T22:26:33Z: DONE. Dropped on the evidence; no source change.

## Project-Specific Additions
<!-- BEGIN USER-DEFINED: project_fields -->
<!-- END USER-DEFINED: project_fields -->
