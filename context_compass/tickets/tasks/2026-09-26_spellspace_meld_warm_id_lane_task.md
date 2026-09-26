

# Task: P4 - SpellSpace.meld serves warm id melds from the spellspace door's fast-door entry

## Metadata
- Task ID: TASK-2026-09-26-spellspace-meld-warm-id-lane
- Story: STORY-2026-09-26-gauntlet-runtime-speed
- Status: in_progress
- Owner: user
- Agent Name: melder_2
- Priority: p1
- Created: 2026-09-26T19:13:34Z
- Updated: 2026-09-26T19:15:24Z

## Objective
A warm `space.meld(spell_id=...)` call, the scoped call shape the gauntlet uses, returns from `SpellSpace.meld`
through the spellspace door's fast-door entry. It skips the door frame and its keyword marshaling. Results,
errors, hooks and the cache-emit check stay identical to calling the door.

## Ticket Contract
- ENTRY_GATE: VM A/B, suites with saved logs (3.14t gil 0 and 1, 3.14.7 GIL build), a flat 30k soak, and
  equivalence checked against the source, all in the measure task notes and re-validated on the 19:06Z tree.
  Owner go-ahead for clean levers (17:32:38Z, repeated ~19:00Z). NOTICE to melder_0 before the meld.py docstring
  edit.
- EXECUTION_BOUNDARY: `SpellSpace.meld` (body and docstring) in spell_space.py; one docstring sentence in meld.py
  (the `Meld._fast_meld_doors` reader list); one new component test file; the version notch and one release-note
  bullet under "Faster warm melds". No change to the doors, executors, stores, public signatures or cache format.
- DEPENDENCIES: melder_0 owns meld.py and the door guard ladder. The lane mirrors that ladder, so any ladder
  change must update all four readers. melder_0's inlined `Conduit.meld` id lane is the model. melder_0's R1
  claims the 0.2.67 notch, so P4 takes the next free notch after it.
- EXIT_GATE: the device tree is byte-identical to the validated copy; the owner runs the Windows gauntlet; the
  owner accepts.
- FAILURE_ESCALATION: CONFLICT if meld.py or spell_space.py changed since the copy (re-anchor and re-validate);
  BLOCKER on any regression. Rollback restores the two files and deletes the test file.

## Scope Boundaries
- In scope: `SpellSpace.meld`; the reader-list sentence in `Meld._fast_meld_doors`; the version notch and release
  note bullet for this change.
- Out of scope: the active-scope documentation question (RISK in the measure task, owner decision); the door
  guard ladder itself; thread-affine pools (lever 2); `SpellSpace.purge`.

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: Validated on the VM copy, then re-validated on the 19:06Z tree (suites, A/B, micro); apply
  next.

## Steps / Checklist
- [x] Prototype and A/B on the VM copy (measure task notes).
- [x] Equivalence against the source: the door's fast path, scope checks, call shapes.
- [x] Suites with saved logs (3.14t gil 0/1, GIL build); 30k-iteration soak; re-run on the 19:06Z tree.
- [x] NOTICE melder_0; apply with --check first; verify byte-identity with the validated copy.
- [ ] Version notch (next free after melder_0's R1) and one release-note bullet.
- [ ] Owner-run gauntlet on Windows; same-run ratios against owner_run_20260926.txt.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- src/melder/aether/conduit/spell_space/spell_space.py
- src/melder/aether/conduit/meld/meld.py (docstring sentence only)
- tests/component/melder/aether/conduit/test_spellspace_component_warm_id_lane.py (new)
- src/melder/__version__.py and release_docs/next_version_release.md (notch and bullet)

## Files / Paths Impacted
- src/melder/aether/conduit/spell_space/spell_space.py
- src/melder/aether/conduit/meld/meld.py
- tests/component/melder/aether/conduit/test_spellspace_component_warm_id_lane.py
- src/melder/__version__.py
- release_docs/next_version_release.md

## Validation
- VM copy (device tree 19:06Z plus apply_p4.py), CPython 3.14.7t -X gil=0: every listed suite passed. The only
  failures are the 3 pre-existing build-asset and version-stamp cases, identical on the base copy. -X gil=1 and
  the 3.14.7 GIL build (subset): all passed. New test: 8/8 on P4; on the base copy its 3 lane-specific cases fail
  (17:55Z run). Logs: artifacts/gauntlet_runtime_speed_20260926/vm_runs/p4_suites_1906.txt and p4_suites.txt.
- Owner machine: Not run.
- Recommended commands:
  - python -m pytest tests/component/melder/aether tests/unit/melder/spellbook tests/component/melder/spellbook -q
  - python benchmarks/testing_other_di/real_world_gauntlet_gil_runner.py

## Risks / Rollback Notes
- The lane adds a fourth copy of the guard ladder; a future ladder change must update every reader. Mitigation:
  the reader list in `Meld._fast_meld_doors` names all four, and the new tests count door entries, so a
  diverging reader fails a test.
- The gain is modest on the VM (about -17% per cached space meld, -2% to -3% per gauntlet cycle); the Windows
  effect is unmeasured until the owner runs it.
- Rollback: restore the two files and delete the test file; nothing persisted depends on this change.

## Applicable Anti-Patterns
- [ ] No status transition without evidence-backed transition reason.
- [ ] No implementation/validation from `UNKNOWN` or `HYPOTHESIS`.
- [ ] No closure without acceptance confirmation and board-sync completion.
- [ ] No gain claimed from a VM number alone; the owner-run number decides.

## Done Checklist
- [ ] Steps complete and checked off
- [ ] Deliverables produced and linked
- [ ] Documentation updated (if needed)
- [ ] Validation status recorded
- [ ] Unknown-first discipline followed (`UNKNOWN` promoted to `FACT` only with evidence)
- [ ] Notes quality maintained (`SCORE_0_TO_10` >=
      `workflow.ticket_microcycle.minimum_note_score`)
- [ ] Applicable anti-pattern checks are clear or escalated with evidence.
- [ ] Acceptance criteria reviewed with user and confirmed
- [ ] Board sync completed for successor routing or closure anchor update.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - artifacts/gauntlet_runtime_speed_20260926/p4_spellspace_warm_lane/
  - artifacts/gauntlet_runtime_speed_20260926/vm_runs/p4_ab_fresh_thread.txt
  - artifacts/gauntlet_runtime_speed_20260926/vm_runs/p4_gauntlet_shape.txt
  - artifacts/gauntlet_runtime_speed_20260926/vm_runs/soak_base_30k.txt
  - artifacts/gauntlet_runtime_speed_20260926/vm_runs/soak_p4_30k.txt
  - artifacts/gauntlet_runtime_speed_20260926/vm_runs/p4_suites.txt
  - artifacts/gauntlet_runtime_speed_20260926/vm_runs/p4_suites_1906.txt
  - artifacts/gauntlet_runtime_speed_20260926/vm_runs/p4_ab_fresh_thread_1910.txt
  - artifacts/gauntlet_runtime_speed_20260926/vm_runs/p4_gauntlet_shape_1911.txt
  - artifacts/gauntlet_runtime_speed_20260926/vm_runs/p4_cached_meld_1913.txt
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: task closure; the owner confirms retention.

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS:
  - none
- CONTEXT_TOPICS:
  - none
- IF_UNKNOWN: none

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-09-26T19:13:34Z
  TYPE: PLAN
  CLAIM: Task opened from the measure task, where the evidence lives: A/B and soak (MEASURE), equivalence against
    the source (FACT), suites with logs (MEASURE), no patch docs (DECISION), re-validation on the 19:06Z tree
    (MEASURE). Apply sequence:
    - NOTICE melder_0 (M2-7).
    - cmp spell_space.py and meld.py against the validated base copy.
    - Run apply_p4.py against the device tree with --check, then for real.
    - Add the test file with CRLF, like its siblings.
    - cmp the three device files against the validated copy.
    - Take the next free version notch after melder_0's R1 and add one bullet under "Faster warm melds".
  EVIDENCE:
  - tickets/tasks/2026-09-26_measure_gauntlet_scope_cycle_costs_task.md:652-678
  - tickets/tasks/2026-09-26_measure_gauntlet_scope_cycle_costs_task.md:680-697
  - tickets/tasks/2026-09-26_measure_gauntlet_scope_cycle_costs_task.md:748-763
  - tickets/tasks/2026-09-26_measure_gauntlet_scope_cycle_costs_task.md:765-791
  - artifacts/gauntlet_runtime_speed_20260926/p4_spellspace_warm_lane/apply_p4.py:1-155
  IMPACT: The apply runs from a validated, anchored script, and every step can be checked.
  NEXT: Send the NOTICE to melder_0 (M2-7) with its alert line.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-09-26T19:15:10Z
  TYPE: FACT
  CLAIM: P4 applied to the device tree at 19:15:00Z, after NOTICE M2-7. Before the apply, the device's
    spell_space.py and meld.py equalled the validated 19:06Z base and the test file was absent. apply_p4.py passed
    --check and was applied. All three device files are byte-identical (cmp) to the copy that passed the suites:
    spell_space.py sha256 b53033cc...ce67c, meld.py 0a8fb807...bf07d6, and the new test (CRLF like its siblings)
    07a8b14c...034d2. The same two sha256 values came out of an independent apply of the script to staged device
    copies in the cloud workspace at 18:06Z.
  EVIDENCE:
  - src/melder/aether/conduit/spell_space/spell_space.py:455-560
  - artifacts/gauntlet_runtime_speed_20260926/p4_spellspace_warm_lane/apply_p4.py:1-155
  - artifacts/gauntlet_runtime_speed_20260926/vm_runs/p4_suites_1906.txt:1-41
  IMPACT: The owner's next gauntlet run measures P4. Still open: the version notch and the release-note bullet,
    which wait for melder_0's R1 (0.2.67) to land first.
  NEXT: Watch __version__.py; once R1 is in, notch to the next free version and add one bullet under "Faster warm
    melds".
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

## Context / Handoff Summary
Applied to the device tree at 19:15:00Z, byte-identical to the copy that passed the suites (re-validated on the
19:06Z tree: about -17% per cached space meld, -2% to -3% per gauntlet cycle, 30k soak flat, equivalence read
against the source). Next: version notch and release-note bullet once melder_0's R1 (0.2.67) is in; then the
owner's Windows gauntlet run and acceptance.

## Project-Specific Additions
<!-- BEGIN USER-DEFINED: project_fields -->
<!-- END USER-DEFINED: project_fields -->
