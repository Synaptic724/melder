# Task: Preserve Python 3.14 deferred annotations during binding and meld

## Metadata
- Task ID: TASK-2026-09-13-repair-deferred-annotation-acquisition
- Story: STORY-2026-09-13-existing-instance-planning
- Status: done
- Owner: codex
- Agent Name: updater_0
- Created: 2026-09-13T20:42:12Z
- Updated: 2026-09-13T20:42:12Z
- Completed: 2026-09-13T20:42:12Z
- Summary: Python 3.14 deferred names survive annotation acquisition; 271 tests and generated-asset checks pass.

## Objective
Fix annotation NameError failures without changing provider matching, defaults, overrides or ownership.

## Record Origin
The work was executed under TASK-2026-09-13-repair-existing-instance-planning. The owner accepted
the annotation-only result and explicitly requested ticket turn-in. This completed record separates
that accepted slice from the still-open existing-object repair; the original notes remain intact.

## Ticket Contract
- ENTRY_GATE: owner reviewed the proposed patch and approved Python 3.14+ implementation.
- EXECUTION_BOUNDARY: binding-profile signatures, requirements annotation acquisition and Meld's contract reader.
- DEPENDENCIES: existing normalization/classification and the Python 3.14 annotationlib contract.
- EXIT_GATE: focused live regressions, prior annotation/default/override tests and generated assets pass.
- FAILURE_ESCALATION: record unrelated failures in their existing lanes without expanding this repair.

## Scope Boundaries
- In scope: retain ForwardRefs during inspection and feed existing dependency normalization.
- Out of scope: existing-instance planner repair, frame admission, disposal, wheel replacement and publication.

## State Transition Event
- from_state: review
- to_state: done
- transition_reason: owner explicitly accepts annotation work and requests its ticket be turned in.

## Deliverables and Validation
- [x] Updated BindingProfileStrategy class/callable signature acquisition.
- [x] Updated SpellRequirementsFinder signature and raw/fallback annotation acquisition.
- [x] Updated Meld's late-bind contract-default signature reader.
- [x] Added 15 live regressions; selected suite passes 271 tests.
- [x] Preserved defaults, explicit override identity and missing-provider validation.
- [x] Archived the obsolete test-only prototype.
- [x] Refreshed three source descriptors and verified graph/index assembly.
- [x] Rebuilt and checked all durable source assets and source/test bundles.
- [x] Owner acceptance, closure anchor and artifact retention recorded.

## Files / Paths Impacted
- src/melder/aether/spellbook/spell_compiler/spell_examiner/strategies/binding_profile_strategy.py
- src/melder/aether/spellbook/spell_compiler/spell_requirements_finder/spell_requirements_finder.py
- src/melder/aether/conduit/meld/meld.py
- tests/integration/melder/spellbook/test_deferred_annotations.py
- Generated source descriptors, graph and source/test build assets.

## Artifact Links
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - artifacts/existing_instance_planning_20260913/annotation_patch_result.md
  - artifacts/existing_instance_planning_20260913/annotation_patch_green.log
  - artifacts/existing_instance_planning_20260913/annotation_patch_green.xml
  - artifacts/existing_instance_planning_20260913/annotation_source_assets_check.log
  - artifacts/existing_instance_planning_20260913/annotation_src_bundle_check.log
  - artifacts/existing_instance_planning_20260913/annotation_live_tests_bundle_check.log
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: retained after owner acceptance; shared folder also supports the continuing instance task.

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS: none
- IF_UNKNOWN: none

## Notes
- DATETIME: 2026-09-13T20:42:12Z
  TYPE: DECISION
  CLAIM: Owner accepted annotation repair and requested closure plus continuation on the next issue.
    Completed annotation record materialized from the umbrella task without closing unresolved work.
  EVIDENCE:
  - Owner instruction to turn in the annotations ticket and continue.
  - artifacts/existing_instance_planning_20260913/annotation_patch_result.md
  - tickets/tasks/2026-09-13_repair_existing_instance_planning_task.md
  IMPACT: Annotation work is closed; existing-object planning continues independently.
  NEXT: Continue the existing-instance task at the two contract-default scanners.
  REREAD: HELPFUL
  SCORE_0_TO_10: 10

## Context / Handoff Summary
Owner-accepted local annotation repair. Source version remains 0.2.40; no replacement wheel or
downstream installation was performed. Source ownership, frame admission and disposal remain separate.
