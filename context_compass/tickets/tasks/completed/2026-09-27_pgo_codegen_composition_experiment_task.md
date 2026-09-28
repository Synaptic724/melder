

# Task: PGO codegen composition experiment - is the juice worth the squeeze?

## Metadata
- Task ID: TASK-2026-09-27-pgo-codegen-composition-experiment
- Story: STORY-2026-09-27-pgo-strategy-exploration
- Status: done
- Owner: cowork
- Agent Name: fable_0
- Priority: p1
- Created: 2026-09-27T19:43:17Z
- Updated: 2026-09-27T19:43:17Z
- Completed: 2026-09-27T19:43:17Z
- Summary: `tests/experimentation/pgo_codegen_composition_experiment.py` measures ten compositions (solo, wide,
  deep, diamond, mixed, alternating; singleton and transient variants) against hand-written ideal PGO bodies:
  an ideal body saves 180-540 ns and exactly 3 Python calls per creation (the door), plus one C call per
  singleton dependency; constructors cannot be removed. Directional VM run recorded; the owner decides.

## Objective
Owner directive (2026-09-27T19:43:17Z): before designing PGO, mock it up over a range of object compositions and measure what
codegen could remove per creation (calls and time) and whether 1000 creations of a common shape get enough
back to justify the effort.

## Ticket Contract
- ENTRY_GATE: the PGO exploration story routed on the board.
- EXECUTION_BOUNDARY: one new file under `tests/experimentation/`; artifacts under
  `artifacts/pgo_strategies_20260927/`; no src edits.
- DEPENDENCIES: melder 0.2.82 on the device tree; the VM venv (3.14.7t).
- EXIT_GATE: the experiment runs on 3.14t, the report is recorded, the verdict is reported to the owner.
- FAILURE_ESCALATION: none.

## Scope Boundaries
- In scope: the ceiling (ideal PGO body vs today's warm meld) per composition.
- Out of scope: profiling cost, regeneration cost, guards under mutation - the story's later tasks.

## State Transition Event
- from_state: draft
- to_state: done
- transition_reason: Experiment written, run on the VM and recorded in one pass (2026-09-27T19:43:17Z); closure pre-approved.

## Steps / Checklist
- [x] Experiment file: ten compositions, five arms, ns/creation, Python and C calls, objects, threads 1-2.
- [x] VM run (GIL disabled) recorded under artifacts/pgo_strategies_20260927/.
- [x] Warm-meld call trace recorded.
- [x] Run Ticket Microcycle during execution.
- [x] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- tests/experimentation/pgo_codegen_composition_experiment.py
- artifacts/pgo_strategies_20260927/vm_composition_run_gil0_20260927.md
- artifacts/pgo_strategies_20260927/warm_meld_call_trace_20260927.md

## Files / Paths Impacted
- tests/experimentation/pgo_codegen_composition_experiment.py (new; no src change, no notch)

## Validation
- VM run: `python -X gil=0 tests/experimentation/pgo_codegen_composition_experiment.py` completed for all ten
  compositions; every arm's returned object tree is shape-checked before timing. Owner-run: Not run.

## Risks / Rollback Notes
- Delete the file to roll back.

## Applicable Anti-Patterns
- [x] No perf claim from agent-side runs beyond "directional".

## Done Checklist
- [x] Steps complete and checked off
- [x] Deliverables produced and linked
- [x] Documentation updated (if needed)
- [x] Validation status recorded
- [x] Unknown-first discipline followed (`UNKNOWN` promoted to `FACT` only with evidence)
- [x] Notes quality maintained (`SCORE_0_TO_10` >=
      `workflow.ticket_microcycle.minimum_note_score`)
- [x] Applicable anti-pattern checks are clear or escalated with evidence.
- [x] Acceptance criteria reviewed with user and confirmed (closure pre-approved; verdict reported in chat)
- [x] Board sync completed for successor routing or closure anchor update.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - artifacts/pgo_strategies_20260927/vm_composition_run_gil0_20260927.md
  - artifacts/pgo_strategies_20260927/warm_meld_call_trace_20260927.md
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: promoted into the catalogue when a strategy ships.

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS: none
- CONTEXT_TOPICS: PGO ceiling; door cost; singleton reads.
- IF_UNKNOWN: none

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-09-27T19:43:17Z
  TYPE: MEASURE
  CLAIM: VM (3.14.7t, GIL disabled, 2 cores; directional). A warm `many` meld costs a constant door of ~183 ns
    and 3 Python calls (`Conduit.meld`, the creation-context template lane, the compiled executor's own frame)
    plus one `dict.get` for the fast-door lookup, then one Python call per constructed object and one
    `dict.get` per singleton dependency read. The ideal PGO body (singletons closed over with one int-compare
    guard each, transients inline positional) saves per creation: solo 183 ns (63%), wide8_singleton 433 ns
    (50%), chain8_singleton 193 ns (51%), chain6_alternating 229 ns (44%), diamond 249 ns (37%), mixed3s4t 349 ns
    (32%), chain8_transient 540 ns (32%), diamond_transient 257 ns (27%), wide8_transient 354 ns (24%),
    wide16_transient 377 ns (14%). Saved Python calls are exactly 3 in every composition; saved C calls equal
    the singleton reads. Per transient site the executor's own overhead is ~20-25 ns (wide16: 2732 vs 2355 ns
    for 17 constructors); per singleton read ~45 ns above a bare dict.get. The guard cost is 0-7 ns per
    guard (guarded vs floor within noise on most shapes). `pgo_store` (store reads kept, no guards) captures
    most of the singleton win (wide8_singleton 364 of 433 ns), so the win is the site machinery around the
    read, not the lookup. At 2 threads every arm inflates 3-4x on this 2-core VM; the real/ideal ratio widens
    on singleton-heavy shapes (solo 3.5x, wide8_singleton 2.1x) and narrows on transient-heavy ones (1.3x).
  EVIDENCE:
  - artifacts/pgo_strategies_20260927/vm_composition_run_gil0_20260927.md
  - artifacts/pgo_strategies_20260927/warm_meld_call_trace_20260927.md
  - tests/experimentation/pgo_codegen_composition_experiment.py:1-60
  IMPACT: The codegen already emits one call per object; PGO cannot remove constructors. The whole ceiling is
    the door (constant, every composition) plus the singleton-read machinery (grows with singleton deps). Per
    1000 creations the ceiling is 0.2-0.5 ms; per million, 0.2-0.5 s.
  NEXT: owner decides whether that ceiling is worth the squeeze; if yes, the door and the singleton-read
    site are the two levers, and neither needs a profile to find - only the singleton-as-constant guard does.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

## Context / Handoff Summary
STATE 2026-09-27T19:43:17Z: DONE. Experiment recorded; verdict with the owner.

## Project-Specific Additions
<!-- BEGIN USER-DEFINED: project_fields -->
<!-- END USER-DEFINED: project_fields -->
