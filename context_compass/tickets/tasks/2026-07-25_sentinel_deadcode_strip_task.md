

# Task: Remove the dead sentinel surface from the guard module and two docstrings

## Metadata
- Task ID: TASK-2026-07-25-sentinel-deadcode-strip
- Story: STORY-2026-07-25-guard-manifest-truth
- Status: done (SUPERSEDED - the target code was deleted by the owner's sweep)
- Owner: melder_1
- Agent Name: melder_1
- Priority: p2
- Created: 2026-07-25T18:19:28Z
- Updated: 2026-07-25T18:19:28Z

## Objective
Delete the sentinel machinery the manifest replaced, so the guard module stops
exposing a surface whose own docstring instructs a pattern that no longer works.

## Ticket Contract
- ENTRY_GATE: BLOCKED. Patch-framework artifacts for patch id
  `guard_manifest_truth_2026_07_25` must exist and be story-linked before any code
  edit, and a repo-wide consumer grep for `.sentinel` must come back clean.
- EXECUTION_BOUNDARY: `src/melder/__melder_registration_guard__.py`,
  `src/melder/__init__.py:156-159` (comment only), and
  `src/melder/utilities/general_base/cleanable.py:51-54` (docstring only).
- DEPENDENCIES: patch artifacts; owner instruction of 2026-07-25 adding this to the lane.
- EXIT_GATE: no sentinel property, slot, or class constant remains; owner-run suite
  green on 3.14t; durable deltas merged into the canonical system docs.
- FAILURE_ESCALATION: DECISION_REQUEST if any consumer of `.sentinel` is found, since
  removal would then be a breaking change rather than dead-code removal.

## Scope Boundaries
- In scope: `_SENTINEL` class constant, the `__slots__` entry, the `__init__` body
  assigning it, the `sentinel` property, and the two stale comment/docstring sites.
- Out of scope: `assert_allowed`, `is_internal`, `_identity_of`, the singleton
  construction lock, the manifest loader, and the `__melder_cache__` packaging defect
  the owner routed elsewhere.

## State Transition Event
- from_state: draft
- to_state: blocked
- transition_reason: Patch-framework gate is triggered - this changes code that
  requires updates to `src_architecture.md`/`src_components.md` and refreshes source
  wiring in the graph. Implementation may not start before the patch docs exist.

## Steps / Checklist
- [ ] Repo-wide grep for `.sentinel`, `_SENTINEL`, and `__melder_internal__` consumers
      outside the guard module; record the result as evidence.
- [ ] Author `architecture_patch.md` for patch id `guard_manifest_truth_2026_07_25`.
- [ ] Author `component_patch_registration_guard.md` with before/after behavior and
      interface deltas.
- [ ] Ask the owner to rule whether `code_description_patch_` is required, since the
      removal is mechanical rather than a control-flow change.
- [ ] Write the patch-section to implementation-step to validation-step mapping into
      this task's `## Notes` before any edit.
- [ ] Remove `_SENTINEL`, the `_sentinel` slot entry, the `__init__` assignment, and
      the `sentinel` property.
- [ ] Correct `__init__.py:156-159`, which still calls the guard a sentinel.
- [ ] Correct `cleanable.py:51-54`, which still describes `getattr` MRO lookup.
- [ ] Leave the guard docstring's historical account of the retired sentinel intact -
      it explains why the manifest exists and is not a live mechanism claim.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- Guard module free of dead sentinel surface.
- Two corrected comment/docstring sites.
- Patch artifacts under `system_docs/patches/active/guard_manifest_truth_2026_07_25/`.

## Files / Paths Impacted
- src/melder/__melder_registration_guard__.py
- src/melder/__init__.py
- src/melder/utilities/general_base/cleanable.py
- context_compass/system_docs/patches/active/guard_manifest_truth_2026_07_25/

## Validation
- Not run.
- Recommended commands (owner-run, 3.14t):
  - `pytest tests/unit/melder -q`
  - `pytest tests/unit/melder/test_package_public_surface.py -q`
  - `rg -n "\.sentinel|_SENTINEL" src/`

## Risks / Rollback Notes
- RISK: `sentinel` is a property on an exported class, so removal is a public-shape
  change. The owner requested it explicitly; the grep gate exists to prove no consumer
  depends on it before the edit lands.
- Rollback: git revert of three source files; no data or state migration involved.

## Applicable Anti-Patterns
- [ ] No status transition without evidence-backed transition reason.
- [ ] No implementation/validation from `UNKNOWN` or `HYPOTHESIS`.
- [ ] No closure without acceptance confirmation and board-sync completion.
- [ ] No code edit before required patch artifacts exist and are ticket-linked.
- [ ] No claim that tests ran unless they actually ran.
- [ ] No drive-by refactor of the surrounding guard logic.

## Done Checklist
- [ ] Steps complete and checked off
- [ ] Deliverables produced and linked
- [ ] Documentation updated (if needed)
- [ ] Validation status recorded
- [ ] Unknown-first discipline followed (`UNKNOWN` promoted to `FACT` only with evidence)
- [ ] Notes quality maintained (`SCORE_0_TO_10` >= 7)
- [ ] Applicable anti-pattern checks are clear or escalated with evidence.
- [ ] Acceptance criteria reviewed with user and confirmed
- [ ] Board sync completed for successor routing or closure anchor update.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - system_docs/patches/active/guard_manifest_truth_2026_07_25/architecture_patch.md
  - system_docs/patches/active/guard_manifest_truth_2026_07_25/component_patch_registration_guard.md
- DISPOSITION: promote_to_documentation
- CLEANUP_TRIGGER: at task closure, once durable deltas are merged into the canonical
  system docs.

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
- DATETIME: 2026-07-25T18:19:28Z
  TYPE: FACT
  CLAIM: The guard module retains `_SENTINEL`, a `_sentinel` slot, an `__init__` that
    assigns it, and a `sentinel` property whose docstring still instructs callers to
    assign it to `__melder_internal__` to mark a class unbindable. That instruction is
    now false: nothing reads `__melder_internal__` anywhere in `src/melder`, and the
    eight remaining textual occurrences are all docstring prose, not live stamps.
  EVIDENCE:
  - src/melder/__melder_registration_guard__.py:105-146
  - src/melder/__init__.py:156-159
  - src/melder/utilities/general_base/cleanable.py:51-54
  IMPACT: A reader following the property docstring would stamp a class and believe it
    guarded, while bind would happily register it - a silent correctness trap.
  NEXT: Run the consumer grep, then author the two patch artifacts.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-07-25T18:19:28Z
  TYPE: BLOCKER
  CLAIM: Patch-framework entry gate is unsatisfied. Required artifacts for patch id
    `guard_manifest_truth_2026_07_25` do not exist and are not story-linked, and the
    gating skill forbids system-impacting code edits until they do.
  EVIDENCE:
  - context_compass/agent_onboarding/default/engineer/skills/patch_framework_gating.md:20-34
  IMPACT: The code half of this lane cannot start; the three documentation tasks are
    unaffected and proceed independently.
  NEXT: Author `architecture_patch.md` and `component_patch_registration_guard.md`, and
    obtain the owner ruling on whether a `code_description_patch_` is required.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-07-25T18:43:26Z
  TYPE: DECISION
  CLAIM: SUPERSEDED, not completed. The owner's sweep deleted the entire guard module
    rather than just its dead sentinel surface, so this task has no target left. The
    patch gate that blocked it is moot: no code change is made by this agent.
    `__melder_registration_guard__.py` no longer exists; refusal is now a module-level
    `assert_allowed` in `bind.py` plus a `_RegistrationGuardProxy` compat shim, and
    `melder/__init__.py` neither imports nor exports any guard symbol.
  EVIDENCE:
  - src/melder/aether/spellbook/bind/bind.py:23-43
  - src/melder/aether/spellbook/bind/bind.py:308-308
  IMPACT: Closing as superseded keeps a blocked row off the board without claiming
    work that was never performed here. The two patch artifacts were never authored,
    correctly, because no system-impacting code edit occurred.
  NEXT: None. Residual code-side item recorded below for owner routing.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8
- DATETIME: 2026-07-25T18:43:26Z
  TYPE: RISK
  CLAIM: Two stale code-side docstrings survive the sweep and still teach the retired
    mechanism. `_builder.py:9` names `melder.__melder_registration_guard__` as the
    manifest's consumer, but that module is deleted and the consumer is `bind.py`.
    `cleanable.py:51-54` still describes detection via
    `getattr(candidate, "__melder_internal__", None)` walking the MRO, which is exactly
    the behavior the manifest retired.
  EVIDENCE:
  - src/melder/_build_assets/_init_manifest/_builder.py:9-9
  - src/melder/utilities/general_base/cleanable.py:51-54
  IMPACT: `cleanable.py` is referenced across ~277 files and its note is the one most
    likely to be read by someone deciding whether to guard a base class; it currently
    justifies a rule using a mechanism that no longer exists.
  NEXT: Owner routing - these are two docstring edits, deliberately not taken as a
    drive-by inside a documentation lane.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

## Context / Handoff Summary
SUPERSEDED. The owner's sweep removed the guard module outright, so there is nothing
left to strip and the patch gate never needed satisfying. Two stale code docstrings
(`_builder.py:9`, `cleanable.py:51-54`) remain and are recorded above for routing.

Original framing follows for history: blocked by the patch gate, not by unknowns - the mechanism and the dead surface are
both fully evidenced. Unblocking is two patch documents plus one owner ruling on
whether a code-description patch applies to a mechanical removal. The guard docstring's
historical account of the retired sentinel stays; only the live surface goes.
