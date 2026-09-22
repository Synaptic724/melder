# Task: Add local hook setters, registration and modification tracking

## Metadata
- Task ID: TASK-2026-09-22-add-local-hook-setters-and-tracking
- Status: ready
- Owner: codex
- Agent Name: updater_0
- Created: 2026-09-22T09:57:45Z
- Updated: 2026-09-22T10:13:25Z
- Related discovery: TASK-2026-09-22-investigate-pooled-conduit-hook-reset

## Objective
Implement the owner's first bounded slice: Conduit hook setting, explicit Meld registration that
creates a local merged copy, and observable local-modification/configuration-hook flags. Decide lock
placement from actual semantics and a small local measurement; do not add locking to ordinary Meld.

## Ticket Contract
- ENTRY_GATE: Owner explicitly requested these runtime additions. Patch contracts before source edits.
- EXECUTION_BOUNDARY: Conduit/Meld registration, setter, flags/properties, initialization/cleanup,
  focused tests and documentation. Benchmark flag/count/mutex reads without changing runtime behavior.
- DEPENDENCIES: Existing local/lineage rules and method-only mutation contract; source/test map reads.
- EXIT_GATE: New methods and flags tested; concurrency contract explicit; source review ready.
- FAILURE_ESCALATION: Keep root-wide propagation/pool-baseline policy out of this first slice.

## Scope Boundaries
- In scope: Conduit.set_conduit_hooks, Meld.register_meld_hooks, existing hook mutation paths,
  local-copy tracking and Conduit.spellbook_configuration_hooks_set.
- Out of scope: broad hook framework/IDs, Bind changes, root broadcast updates, graduation, generated assets.
- Pool restoration remains a following slice with its pending fixed/current-owner baseline decision.
- Direct list/dict mutation is unsupported. Do not add mutation scans or proxies.

## State Transition Event
- from_state: in_progress
- to_state: ready
- transition_reason: Owner redirects to focused pool/SpellSpace and bind-graduation investigation before code.

## Work
- [x] Measure simple no-change reads in the user's free-threaded environment.
- [ ] Record patch contract and map its sections to source/tests.
- [ ] Implement local registration/setter/flags with rich contracts and cleanup.
- [ ] Run focused tests and inspect the source changes before reporting.

## Validation
Runtime tests: Not run. Read-cost benchmark completed; see the measurement note below.
Use .venv_new with uv, offline/no-sync and Python -X gil=0.
Prove additive versus replacement behavior, parent-map isolation, flags, method-only tracking,
cleanup and unchanged ordinary Meld hook dispatch. No generated assets before owner code approval.

## Artifact Links
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - artifacts/local_hook_tracking_20260922/
- DISPOSITION: retain_as_reference

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS: none

## Notes
- DATETIME: 2026-09-22T09:57:45Z
  TYPE: PLAN
  CLAIM: Owner requested Conduit setting, Meld local registration and modified flags, then proposed
    spellbook_configuration_hooks_set to distinguish empty from configured baselines. Public hook
    mutation is the supported seam. Compare count/bool/mutex cost before making a speed claim.
  EVIDENCE:
  - Owner's API/flag request and subsequent mutex/count question.
  - src/melder/aether/conduit/conduit.py:1657-1711
  - src/melder/aether/conduit/meld/meld.py:1264-1307
  IMPACT: Code/test work is authorized for this slice; broad standardization and generators remain held.
  NEXT: Run the small read-cost measurement and select mutation/read locking boundaries.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-22T10:13:25Z
  TYPE: MEASURE
  CLAIM: The retained read-cost run used Python 3.14.7 free-threaded with GIL disabled, seven
    repeats of one million calls each. Median ns/call: flag 18.44; dict truth 23.32; len(dict)>0
    27.90; uncontended RLock-protected read 84.93; false flag bypassing lock 22.17. These include
    wrapper-call overhead and measure one thread without contention, not Melder throughput.
  EVIDENCE:
  - artifacts/local_hook_tracking_20260922/read_cost.json:1-29
  - artifacts/local_hook_tracking_20260922/read_cost.py
  IMPACT: This measurement does not support replacing a simple flag/count read with a mutex for
    speed. It does not decide correctness or justify a new lock on ordinary meld execution.
  NEXT: Complete the owner's requested pool/SpellSpace and bind-graduation investigation first.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

## Context / Handoff Summary
Implementation is held while the owner-requested pool/SpellSpace and bind-graduation investigation
is active. No runtime source edits have been made. Conduit setter semantics were asked: replace only
supplied events versus the whole local setup; no answer yet. Independent Meld registration/tracking
remains authorized after that investigation. Flag cost measurement is complete.
