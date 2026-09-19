# Task: Reject incompatible supplied Protocol providers during bind

## Metadata
- Task ID: TASK-2026-09-19-repair-existing-instance-protocol-admission
- Story: STORY-2026-09-19-existing-instance-protocol-admission
- Status: review
- Owner: codex
- Agent Name: updater_0
- Priority: p1
- Created: 2026-09-19T11:36:38Z
- Updated: 2026-09-19T11:52:48Z

## Objective
Extend Bind's established Protocol admission check to the actual supplied instance and prove normal
compiler/injection behavior remains intact without changing the existing-object model.

## Ticket Contract
- ENTRY_GATE: owner authorization, matching attention row and linked patch contracts before runtime edits.
- EXECUTION_BOUNDARY: Bind._bind_logic/_structurally_implements_protocol; focused tests, docs and assets.
- DEPENDENCIES: completed investigation, retained red cases and accepted earlier instance planner repair.
- EXIT_GATE: native regressions/controls pass, docs and generated assets current, exact evidence recorded.
- FAILURE_ESCALATION: distinguish changed admission expectations from unrelated suite failures; do not
  redesign Protocol semantics, compiler, disposal or ownership without a separately selected contract.

## Scope Boundaries
- In scope: ClassBindingProfile and existing InstanceBindingProfile/OtherBindingProfile admission parity.
- Out of scope: constructor calls, broader lifetimes, external registration APIs, inherited Protocol or
  annotation-only field enforcement, continuous post-bind validation, release/version changes.

## State Transition Event
- from_state: in_progress
- to_state: review
- transition_reason: repaired admission and 334 native checks pass; docs and generated assets are synchronized.

## Steps / Checklist
- [x] Create/read patch contracts and record implementation/validation mapping.
- [x] Read target source/tests fully; extend native actual-instance and staged/compiler-path regressions.
- [x] Repair Bind's existing gate and helper contract; preserve other classifications and ordering.
- [x] Run focused native tests and record results before documentation work.
- [x] Update authored docs/descriptor, rebuild indexes, graph and required build assets/bundles.
- [x] Verify diff, documentation and build checks, then present completed repair for review.

## Deliverables
Narrow runtime patch, permanent regressions, synchronized public/system docs and generated assets.

## Files / Paths Impacted
- src/melder/aether/spellbook/bind/bind.py
- tests/unit/melder/spellbook/bind/test_bind.py
- tests/component/melder/spellbook/test_existing_instance_protocol_admission.py
- tests/integration/melder/spellbook/test_existing_instance_protocol_injection.py
- docs/beginner/registration.md
- context_compass/system_docs/src_architecture.md and src_components.md, relevant Bind entries only.
- context_compass/system_docs/graph/melder/aether/spellbook/bind/bind.json and generated graph/index outputs.
- Generated source/package documentation, bind-guard and repository support bundles through existing runners.

## Required Rereads / Resume Order
1. This task's latest Notes and linked story; no need to restart the broader owned-object discovery.
2. artifacts/existing_instance_protocol_20260919/findings.md and test_protocol_paths.py.
3. Verified src_components Binding Pipeline and compiler slices; graph Bind slice; then bind.py in full.
4. Target tests and their existing runtime fixture; public registration docs and relevant build runners.

## Validation
Native red baseline: 10 failed/247 passed. Patched primary suite: 267 passed; additional binding and
guard controls: 67 passed. Total 334 focused checks. Index/graph, all source assets and all repository
corpora verify. Full suite and coverage: Not run. Exact commands/results are in the validation artifact.

## Risks / Rollback Notes
Checking the class instead of the value misclassifies instance-only and shadowed members. Broader
checker changes could break unrelated class registrations. Roll back this bounded gate/helper/test/doc
delta together if needed; preserve all unrelated working-tree changes.

## Applicable Anti-Patterns
- [x] No production claims based only on the diagnostic probe.
- [x] No compiler changes or cache redesign inferred from an admission defect.
- [x] No unrelated formatting or test cleanup.

## Done Checklist
- [x] Implementation and permanent regressions complete.
- [x] Documentation and generated assets synchronized.
- [x] Validation and remaining limits recorded.
- [x] Review handed to owner; board reflects actual state.

## Artifact Links
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - system_docs/patches/active/existing_instance_protocol_2026_09_19/
  - artifacts/existing_instance_protocol_repair_20260919/
- DISPOSITION: promote_to_documentation for patches; retain_as_reference for evidence.
- CLEANUP_TRIGGER: apply patch cleanup at accepted closure; retain regression/build evidence.

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS: none
- IF_UNKNOWN: record the precise unresolved source question in Notes.

## Noting Behavior
Record each completed source/edit/validation tranche before continuing; one concrete next action.

## Notes
- DATETIME: 2026-09-19T11:36:38Z
  TYPE: DECISION
  CLAIM: Owner approves Bind admission parity for supplied objects. Reuse is_instance for instance/other
    profiles, pass the actual value and retain direct-public-member semantics. No compiler edit is indicated.
  EVIDENCE:
  - Owner's current implementation request.
  - artifacts/existing_instance_protocol_20260919/findings.md:111-172
  - tickets/tasks/2026-09-19_investigate_existing_instance_protocol_validation_task.md:208-234
  IMPACT: This task owns the repair; prior investigation stays immutable evidence, not acceptance proof.
  NEXT: Establish patch contracts and finish required source/test reads before runtime editing.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-19T11:42:00Z
  TYPE: DECISION
  CLAIM: Patch contracts are authored and consumed in architecture/component/control-flow order.
    Mapping: architecture invariants -> preserve unique/reference/compiler behavior -> native path tests;
    component before/after -> extend existing is_instance gate and candidate typing -> profile-family and
    actual-instance cases; gate ordering -> keep preceding checks -> existing guard and new existence controls.
    Bind and the complete unit/component targets were read; the fixture owns isolated dynamic worlds.
  EVIDENCE:
  - system_docs/patches/active/existing_instance_protocol_2026_09_19/architecture_patch.md:7-46
  - system_docs/patches/active/existing_instance_protocol_2026_09_19/component_patch_bind.md:6-35
  - system_docs/patches/active/existing_instance_protocol_2026_09_19/code_description_patch_bind.md:6-30
  - src/melder/aether/spellbook/bind/bind.py:324-523
  - tests/integration/melder/spellbook/test_existing_instance_planning.py:73-100
  IMPACT: Entry gate is satisfied. Only one production helper call exists; no keyword callers prevent
    naming its input candidate. No production compiler edits are planned.
  NEXT: Add permanent regression cases and apply the bounded Bind correction.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-09-19T11:44:05Z
  TYPE: MEASURE
  CLAIM: Permanent regression baseline is 10 failed and 247 passed. Failures are precisely the
    missing instance/other admission and native missing, non-callable, shadowed and staged cases.
    Compatible injection, instance-only members and prior Bind controls pass before the production edit.
  EVIDENCE:
  - artifacts/existing_instance_protocol_repair_20260919/red.log
  - artifacts/existing_instance_protocol_repair_20260919/red.xml
  IMPACT: Native regressions expose the agreed defect without the diagnostic admission plugin.
  NEXT: Extend the established Bind Protocol gate to existing profiles and run the same suite.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-09-19T11:44:05Z
  TYPE: FACT
  CLAIM: Bind now applies its existing helper to class or is_instance profiles, passes the supplied
    target unchanged and reports Existing object for supplied failures. The helper uses candidate: object
    with the same direct-dictionary member loop. No compiler, lifetime, fingerprint or storage code changed.
  EVIDENCE:
  - src/melder/aether/spellbook/bind/bind.py:475-503
  - src/melder/aether/spellbook/bind/bind.py:881-930
  IMPACT: Missing instance admission is repaired at the common boundary; tests must now prove the result.
  NEXT: Run native Bind, Protocol admission/injection and existing-instance planning regressions.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-09-19T11:44:29Z
  TYPE: MEASURE
  CLAIM: Patched native suite passes 267 tests in 0.86 seconds, including all ten red regressions,
    actual-instance/staged checks, four compiler injection routes and the existing-instance planner suite.
  EVIDENCE:
  - artifacts/existing_instance_protocol_repair_20260919/green.log
  - artifacts/existing_instance_protocol_repair_20260919/green.xml
  IMPACT: The bounded Bind repair works without compiler changes; permanent native evidence replaces
    the earlier simulation for this patch. Full repository suite and coverage are not claimed.
  NEXT: Synchronize the relevant public/system docs and generated build assets.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-09-19T11:48:52Z
  TYPE: FACT
  CLAIM: Public registration docs and Bind-specific architecture/component contracts now describe actual
    instance checks and unchanged limits. Measured Bind extent is 932 lines. Canonical extractor/merge
    refreshed only the Bind descriptor, whose class semantics were re-read and accepted; graph/index rebuilt.
    Sixty-seven additional fluent-binding, component and internal-registration controls pass.
  EVIDENCE:
  - docs/beginner/registration.md:14-25
  - src/melder/aether/spellbook/bind/bind.py:333-536
  - src/melder/aether/spellbook/bind/bind.py:881-929
  - artifacts/existing_instance_protocol_repair_20260919/binding_controls.log
  IMPACT: 334 focused tests pass across the two green runs. Existing source ClassVar F401 predates this
    patch; it is left unchanged. Full graph preflight exposes unrelated unstamped/stale nodes and cache
    inventory; only the selected descriptor is refreshed. Existing docs also contain portability leaks,
    so no full-document quality-pass or score is claimed by this targeted repair.
  NEXT: Verify preservation/indexes and rebuild/check source assets and repository corpora.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-19T11:52:48Z
  TYPE: MEASURE
  CLAIM: Source assets and src/tests/other corpora are regenerated and their checks pass. The new
    integration file is included through the builder's explicit include-untracked mode. Authored doc
    preservation differences are solely measured dates/ranges/citations, with no unaccounted content loss.
  EVIDENCE:
  - artifacts/existing_instance_protocol_repair_20260919/validation.md
  - artifacts/existing_instance_protocol_repair_20260919/source_assets_check.log
  - artifacts/existing_instance_protocol_repair_20260919/bundles_check.log
  - artifacts/existing_instance_protocol_repair_20260919/doc_removed_lines.json
  IMPACT: The approved repair is delivered for review; no broader ownership/compiler work or release
    change is included. Pre-existing lint/doc/graph limitations remain explicitly recorded.
  NEXT: Owner reviews the bounded repair; formal ticket closure remains pending acceptance.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
IMPLEMENTED, review pending: actual-instance Protocol admission in Bind, preserving current checker
coverage and unique-only reference semantics. Ten red regressions now pass; 334 focused checks total.
Compiler is unchanged. Source assets, graph/indexes and all repository corpora rebuilt and verified.
Read artifacts/existing_instance_protocol_repair_20260919/validation.md for commands and explicit limits.
Do not restart the broader owned-object discovery or claim the diagnostic plugin is the shipped fix.
Owner acceptance is the only remaining ticket-closure action; no release/version action was requested.
