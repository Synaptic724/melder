# Epic: Preserve provider artifact ownership and plan existing instances correctly

- Completed: 2026-09-19T14:51:36Z
- Closure Basis: explicit owner request to turn in all delivered updater_0 work.
- Summary: Turned in delivered annotation, instance-planning, Protocol and provider-artifact repairs. Unperformed object-lifecycle redesign and remaining Iris cleanup/alias questions are parked in the dedicated backlog epic.
- Deferred work: tickets/epics/backlog/2026-09-13_existing_object_lifecycle_ownership_epic.md.
  Historical unchecked redesign/downstream items are deferred, not an implementation claim.


CURRENT OWNER DIRECTION (2026-09-19): provider-artifact repair is active under the current model.
The broader redesign is retired. Earlier dependency/parking statements below are superseded history.
Keep tests asserting provider usability; no xfail or expected-error conversion is authorized.


## Metadata
- Epic ID: EPIC-2026-09-13-provider-artifact-ownership-and-existing-instance-planning
- Status: done
- Owner: codex
- Agent Name: updater_0
- Author / consulting expert: knowledge_expert_0
- Priority: p1
- Created: 2026-09-13T18:03:36Z
- Updated: 2026-09-19T14:51:36Z
- Target Window: active provider-artifact repair under the current model
- Related Program/Initiative: CommandOps native provider and ActivityBootstrap acceptance

## Problem / Opportunity
Two supported CommandOps inputs expose distinct native failures in installed Melder 0.2.40.
The consultation was completed by knowledge_expert_0, reconciled by command_1 and accepted by
command_0. The owner now assigns updater_0 to reproduce the failures in Melder, repair their
native mechanisms and prove the original consuming scenarios. This epic records that assignment.

1. A borrower links a provider, imports its GraphCache Spell with read permission, late-binds
   PolicyEngine and calls validate_resolution(refresh_structural=True). A subsequent provider
   meld cannot build CreationContext because spell_codegen_creation is missing. The fresh-world
   prefix proof passes six earlier boundaries and first fails immediately after validation.
   Borrower meld and cleanup are not needed to trigger that observed failure.
2. Binding the real Iris ChannelLogger object with bind(spell=logger, existence="unique") is
   a supported existing-instance API. ActivityBootstrap passes structural validation, then
   plan_group refuses the object as non-callable. Source review identifies planning-time
   inspect.signature(instance), not evidence that logger() was executed at runtime.

Evidence is versioned to installed 0.2.40. Current checkout behavior and the final repair design
remain to be verified by updater_0. The drafter has not implemented fixes or run new tests.

## MRP Alignment (Most Reasonable Product)
Melder owns the registered object world. Borrowing visibility must preserve provider ownership,
identity and executable state; supplying an existing object must preserve its existing-object
contract throughout planning. Correct these runtime contracts where they are owned so consumers
can use ordinary native APIs without compensating wrappers or suppressed validation.

## Ticket Contract
- ENTRY_GATE: owner assignment and route exist; current-model provider repair authorized on 2026-09-19.
- EXECUTION_BOUNDARY: native reproduction, source repair and focused regression evidence for these two failures.
- DEPENDENCIES: accepted CommandOps consultation, original tests/logs and current Melder compiler/runtime source.
  The former broader-redesign prerequisite is retired by owner direction.
- EXIT_GATE: both repair stories pass their criteria; original consumer proofs pass; evidence and boards are synced.
- FAILURE_ESCALATION: record a blocker if current source differs materially or reproductions need unavailable inputs.
  Raise a concrete contract decision if the repair requires changing public ownership or lifetime semantics.

## Goals (Outcomes)
- Provider identity, state and usability survive borrower compilation, resolution and cleanup.
- Native invalidation and rebuilding respect artifact ownership and compilation visibility.
- Existing creations remain opaque supplied values at roots and inside dependency occurrences.
- Both failures have native regression coverage and an unchanged CommandOps acceptance path.

## Non-Goals (Explicit Exclusions)
- Reopening the separate Optional[T] / default-None investigation or taking other agents' repairs.
- Reworking CommandOps architecture, provider classes or Iris ownership contracts.
- Callable wrappers, fake acceptance providers, disabling validation or changing test order to mask failures.
- Releases, external publication, automatic installation into other agents' environments or unrelated refactors.

## Scope Boundaries
- In scope: ownership of Phase-5 artifact publication; artifact/context invalidation and coherent recovery;
  owned-root planning scope; existing-creation handling in the Phase-8 analyzer and Phase-9 processor;
  affected native tests and focused downstream acceptance.
- Out of scope: unrelated named-conduit work, optional-default work, shared-Iris redesign and consumer workarounds.
- command_0 and command_1 continue their other CommandOps work. updater_0 owns these native repairs.
- knowledge_expert_0 is the consultation contact and drafter, not the implementation owner.

## State Transition Event
- from_state: review
- to_state: done
- transition_reason: owner accepts turn-in of delivered scope and explicitly backlogs unperformed user-created-object work.

## Success Metrics
- All eight independent provider-prefix cases complete with the original unique GraphCache identity.
- The original end-to-end linked-provider test passes, including retained state and post-cleanup provider use.
- The original dedicated-Iris-logger ActivityBootstrap test passes with the real existing logger input.
- Native regression coverage exercises repeated/two-borrower validation and existing instances at dependency positions.
- Each result records source/package identity, exact command, outcome and any unexecuted coverage.

## Requirements (Functional + Non-Functional)
- Preserve read-contract borrowing without transferring or replacing the provider Spell or its unique creation.
- A borrower must not retire canonical provider artifacts without a coherent owner-scoped rebuilding path.
- Preserve correctness across artifact invalidation, context-door epochs and ready/resolved state gates.
- Do not rebuild provider canonical state under borrower-only visibility merely to refill a missing payload.
- Existing creations do not acquire constructor-injection requirements through signature inspection.
- Review both planning iterators; fixing only the first observed refusal leaves the second branch exposed.
- Preserve ordinary class/factory contract discovery and explicit dependency-override behavior.
- Preserve existing defaults, named/spellframe lookup and lifetime behavior in the consuming proofs.
- Retain unrelated dirty work and record evidence through ContextCompass.

## Constraints / Assumptions
- The failing package is Melder 0.2.40 on Python 3.14.7; verify current checkout/package mapping before comparison.
- The consulted mechanism is source-backed; the chosen repair is still a design decision for updater_0.
- GraphCache disposal was not demonstrated. Missing compiled artifacts must not be described as object disposal.
- refresh_structural=False was not established as a workaround and is not an accepted bypass.
- Original prefix cases each start a fresh world and perform only one final diagnostic provider lookup.
  Extra intermediate provider probes can repair state and invalidate the causal boundary.

## Dependencies / External References
Paths in this section are relative to the melder_private/context_compass root.

- Accepted source consultation and full evidence ranges:
  ../../priv_commandops/context_compass/tickets/tasks/2026-09-13_native_provider_runtime_expert_review_task.md
- Original provider boundary ticket:
  ../../priv_commandops/context_compass/tickets/tasks/2026-09-13_provider_invalidation_boundary_task.md
- Original bootstrap work and logger context:
  ../../priv_commandops/context_compass/tickets/tasks/2026-09-13_spectrum_default_bootstraps_task.md
- Provider tests, complete setup and fresh-prefix assertions (lines 1-168):
  ../../priv_commandops/tests/component/spectrum/test_linked_commandops_providers.py
- Dedicated logger test and teardown assertions (starts at line 197; recheck current end line):
  ../../priv_commandops/tests/component/spectrum/test_area_bootstraps.py
- Fresh-world reset fixture:
  ../../priv_commandops/tests/component/spectrum/conftest.py
- Observed 0.2.40 provider log, lines 1-42:
  ../../priv_commandops/context_compass/artifacts/2026-09-13_provider_invalidation_boundary/prefix_results_0240.log
- Observed 0.2.40 logger log, lines 1-31:
  ../../priv_commandops/context_compass/artifacts/2026-09-13_area_bootstraps/dedicated_logger_0240.log
- Native system entry points: system_docs/src_architecture.md, src_architecture_index.md and src_components_index.md.

## Source Mechanisms to Reproduce
These are findings from the accepted installed-source consultation. Resolve the same paths under
melder_private/src/melder and verify differences before editing; the ranges below refer to 0.2.40.

### Provider ownership failure
- spellbook/spellbook.py:1251-1307 retains the provider Spell object in the borrower visible pool.
- spellbook/spell_compiler/phases/compiler_phase_5.py:162-214,311-372,460-599 publishes artifacts
  on visible spells from _spell_id_pool, including the same borrowed provider objects.
- spellbook/spell_compiler/spell_compiler_artifact.py:365-398 clears codegen/context on attachment.
- spellbook/spellbook_creation_system.py:3084-3156 schedules plan-group roots from owned _spells.values().
- spellbook/spell.py:659-686 advances the context-door epoch and resets its selector during cleanup.
- conduit/meld/meld.py:759-891 and conduit/meld/conduit_meld.py:349-385 rely on readiness state.
- conduit/meld/creation_context/creation_context_factory.py:291-340 consumes existing Phase-11 output.
- conduit/meld/creation_context/creation_context_builder.py:68-151 refuses the missing payload.

All paths above are relative to melder/aether in the installed package. The ownership mismatch
invalidates more spells than the borrower recompiles. Existing validity/resolution flags do not
restore the provider's missing payload before its cold creation-context build.

### Existing-instance planning failure
Paths below are also relative to melder/aether. The accepted ticket contains complete ranges.

- spellbook/spell_compiler/spell_analyzer/strategies/spell_occurrence_graph_analyzer_strategy.py
  Phase-8 _iter_spell_contract_defaults inspects spell.spell for is_existing_creation; line 995.
- spellbook/spell_compiler/artifact_processor/strategies/spell_occurrence_contract_processor_strategy.py
  Phase-9 _iter_spell_contract_defaults repeats the same inspection; line 226.
- Dependency occurrences still reach these iterators even when existing creations are excluded as roots.
- spellbook/spell_compiler/spell_requirements_finder/spell_requirements_finder.py:231-257 and
  conduit/meld/creation_context/creation_context_builder.py:68-234 establish the contrasting
  no-constructor-DI and direct existing-object-return treatment.
- The public binding review confirms spell=instance, existence="unique". existing_object is internal,
  and no factory wrapper or extra public instance flag is required.

## Milestones (Track Progress)
- [ ] Reconcile checkout with the failing package; reproduce both failures before changing the implementation.
- [ ] Complete the provider artifact ownership story with native regression evidence.
- [ ] Complete the existing-instance planning story with native regression evidence.
- [ ] Verify both original CommandOps acceptance scenarios against the repaired package and hand off results.

## Stories (Required to Complete)
The story boundaries are defined here; updater_0 creates their linked story/task files before implementation.

- [ ] STORY-2026-09-13-provider-artifact-ownership: preserve provider-owned executable state through borrower
  validation, repeated validation, two borrowers, consumer resolution and consumer cleanup. Choose the repair
  after tracing owner/borrower visibility. Prove original provider Spell/object identity and retained GraphCache data.
- [ ] STORY-2026-09-13-existing-instance-planning: treat supplied instances consistently across both iterators,
  including non-callable dependency occurrences. Prove exact object identity and preserve callable factory/class DI.

Linked story records:
- tickets/stories/completed/2026-09-13_provider_artifact_ownership_story.md
- tickets/stories/completed/2026-09-13_existing_instance_planning_story.md

## Tasks (Cross-Cutting or Epic-Level)
- [x] Materialize the two story routes and tactical reproduction/repair tasks in this ContextCompass.
- [ ] Compare current source to the 0.2.40 identities in the consultation before claiming a fresh reproduction.
- [ ] Capture focused failing-then-passing native evidence without changing the consuming public contract.
- [ ] Coordinate a verified local package handoff and downstream rerun with command_0/command_1.
- [ ] Verify ticket notes, artifact disposition, acceptance and board transitions before closing the epic.

## Acceptance Criteria (Epic Done)
- Both required stories are accepted with linked source changes and executed regression evidence.
- Original provider prefix cases retain the unique provider object through every public boundary.
- Consumer PolicyEngine receives the same graph; provider state remains usable after consumer cleanup.
- Repeated validation and two-borrower cases preserve ownership, identity and correct scope semantics.
- Existing non-callable objects work as supported unique roots and transitive dependencies.
- Callable existing objects retain existing-object identity without execution as factories during planning.
- Ordinary callable/class contract-default behavior continues to pass relevant tests.
- Dedicated Iris logger, ActivityBuilder and GeneralActivity assertions pass on the original consumer path.
- No acceptance test is weakened, wrapped or supplied with a fake provider to pass.
- A report distinguishes native suite results, downstream results and any blocked/unexecuted checks.

## Risks / Mitigations
- Compiling all borrowed roots in the borrower can overwrite provider-owned state under wrong visibility.
  Mitigation: document artifact ownership and invalidation/rebuild symmetry before selecting a patch.
- Repairing only Phase 8 can hide the remaining Phase-9 defect until another path reaches it.
  Mitigation: review and cover both iterators and dependency occurrence traversal.
- Current checkout may already differ from 0.2.40. Mitigation: record versions/deltas and reproduce honestly.
- Extra provider lookups can alter runtime state. Mitigation: preserve independent original prefix probes.

## Applicable Anti-Patterns
- [ ] No epic-state transition without story-level evidence.
- [ ] No closure while required stories or downstream acceptance remain incomplete.
- [ ] No program claim without source/test evidence in linked notes.

## Validation / Test Approach
Start from the original recorded commands/test selectors in CommandOps, then build focused native regressions.
The following selectors identify the exact downstream checks; these are handoff instructions, not new test results:

- tests/component/spectrum/test_linked_commandops_providers.py::test_provider_usable_after_operation_prefix
  Run initially with --maxfail=1 to retain the first failing public boundary; run all cases after the repair.
- tests/component/spectrum/test_linked_commandops_providers.py
  Includes the complete provider borrowing, injection, retained-state and cleanup proof.
- tests/component/spectrum/test_area_bootstraps.py
  Select test_activity_root_uses_real_dedicated_logger_and_releases_builder_custody.

Use the documented project interpreter and fixture lifecycle. Record exact executable, arguments, versions,
exit codes and outputs. For downstream results, coordinate the package replacement/rerun so concurrent
CommandOps agents do not unknowingly execute a changing environment. Scope broader native validation to
compiler, contracts, existing creations, dynamic resolution, invalidation and ownership paths actually changed.

## Rollout / Adoption Plan
Implement and verify locally in Melder. Return repair references and a reproducible package handoff to the
CommandOps lead for original-scenario validation. Do not publish or silently replace another agent's environment.

## Open Questions
- Does current Melder source reproduce both recorded 0.2.40 mechanisms unchanged?
- Which artifacts are canonical per owner versus scoped to a borrower compilation snapshot?
- Is preservation sufficient, or does coherent owner-scoped rebuilding need to change readiness transitions?

## Decision Log
- Owner assigned updater_0 to reproduce and repair these two consultation findings.
- knowledge_expert_0 drafts and routes the epic; command_0/command_1 retain their other work.
- Owner directed immediate completion of this handoff without the drafter's interrupted re-onboarding.
  This scoped instruction is not an attestation of completed re-onboarding or a policy-file change.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: false for this draft; reproduction tasks register new logs when produced.
- ARTIFACT_PATHS: none created by the drafter; original evidence remains in the CommandOps tickets above.
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: owning reproduction tasks decide disposition at closure.

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS: none
- CONTEXT_TOPICS: source-backed provider ownership and existing-instance planning handoff
- IF_UNKNOWN: record unresolved repair design in the relevant story before implementation.

## Notes
- DATETIME: 2026-09-19T12:51:19Z
  TYPE: DECISION
  CLAIM: Owner retires the broader redesign and explicitly chooses to fix this artifact bug next.
    This supersedes the September 17 redesign dependency. Retain the current existing-object model
    and all corrected-behavior assertions; do not mark the seven native failures xfail.
  EVIDENCE:
  - Owner reply: Retire the broader redesign; fix the artifact bug next (Recommended).
  - tests/integration/melder/spellbook/test_provider_artifact_ownership.py:71-216
  IMPACT: Source investigation, bounded compiler repair, tests/docs/build checks are authorized.
    Native scope is provider-owned artifact publication versus borrower visibility, not object redesign.
  NEXT: Re-read the Phase-5 publication/invalidation chain, then stage the bounded patch contract.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-13T18:03:36Z
  TYPE: DECISION
  CLAIM: Owner-authorized native repair epic is ready for updater_0. Two confirmed 0.2.40 mechanisms
    are separated into required stories. Current checkout reproduction and patch selection remain his work.
  EVIDENCE:
  - ../../priv_commandops/context_compass/tickets/tasks/2026-09-13_native_provider_runtime_expert_review_task.md
  - Owner instruction to finish this epic and wake the existing agent: updater_0 task.
  IMPACT: Native repair is explicitly assigned without transferring unrelated CommandOps work.
  NEXT: updater_0 acknowledges intake and creates linked reproduction/repair tasks from the two story boundaries.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10


- DATETIME: 2026-09-13T18:09:51Z
  TYPE: DECISION
  CLAIM: updater_0 accepted the owner-authorized knowledge_expert_0 handoff after completing the
    required re-onboarding. Reproduce and repair the two named native failures in separate stories;
    preserve original GraphCache/logger inputs and acceptance tests. Optional/default, named-conduit
    work and publication remain outside this epic. No harness subagents will be used.
  EVIDENCE:
  - tickets/epics/completed/2026-09-13_provider_artifact_ownership_and_existing_instance_planning_epic.md:14-85
  - HANDOFF from knowledge_expert_0 at 2026-09-13T18:03:36Z, consumed from mailbox after recording here.
  IMPACT: Implementation ownership is accepted; verify current source and original consultation before patching.
  NEXT: Create the two linked stories/tasks and read the original source-backed consultation.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-19T14:51:36Z
  TYPE: DECISION
  CLAIM: Owner accepts turn-in of this delivered record. Turned in delivered annotation, instance-planning, Protocol and provider-artifact repairs. Unperformed object-lifecycle redesign and remaining Iris cleanup/alias questions are parked in the dedicated backlog epic.
  EVIDENCE:
  - Owner instruction to backlog user-created-object ideas and turn in all work done.
  - artifacts/updater_0_turn_in_20260919/closure_manifest.json
  IMPACT: Record closed with its historical evidence retained. Deferred requirements remain visible
    in the backlog epic; no new runtime, test, installation or release result is implied.
  NEXT: Resume deferred work only on a new explicit owner request.
  REREAD: HELPFUL
  SCORE_0_TO_10: 10

## Current Owner Direction
2026-09-19: retain the current model; broader redesign retired. Provider-artifact repair is now delivered
for review with nine original downstream provider cases passing. Protocol admission is also delivered
and linked through STORY-2026-09-19-existing-instance-protocol-admission. Earlier directions below are history.

2026-09-17: the remaining provider-artifact repair is dependent on the existing-object ownership
program. Do not present it as a standalone small repair or implement an isolated ownership policy.
Follow tickets/epics/backlog/2026-09-13_existing_object_lifecycle_ownership_epic.md for the primary design.
This is an owner-directed dependency; the update makes no new claim about the only possible technical fix.

Owner selected one issue at a time and approved the annotation-only repair after reviewing its
explanation. That repair is owner-accepted and turned in under the completed annotation task.
The owner then authorized existing-instance planning: the two scanners are corrected and native
checks pass; the original Iris test now reaches construction but fails a separate cleanup assertion.
Owner parks disposal/transfer/lifecycle in EPIC-2026-09-13-existing-object-lifecycle-ownership, preserving
the accepted default-disabled flag contract. Protocol admission is now included there too, under separate
construction, validation and ownership rules. Provider-artifact ownership remains parked separately.
Callable-object binding is a separate API question. The prior separate parking of provider-artifact
work is superseded by the ownership-program dependency above.
Frame admission now has four native rejection regressions failing and fourteen controls passing;
the proposed correction extends existing bind-time Protocol validation to supplied instances only.

- DATETIME: 2026-09-19T13:08:28Z
  TYPE: FACT
  CLAIM: The current-model provider-artifact repair now preserves canonical provider execution through
    borrower and local passes. Native qualification and all nine original CommandOps provider tests pass.
    The withdrawn broader redesign is archived; its observations remain references, not prerequisites.
  EVIDENCE:
  - tickets/tasks/completed/2026-09-13_repair_provider_artifact_ownership_task.md
  - artifacts/provider_artifact_ownership_20260913/repair_result_20260919.md
  IMPACT: Provider story is delivered for review. Earlier instance-planning/Iris cleanup evidence remains
    separate; this result does not claim that unrelated acceptance criteria were rerun or repaired.
  NEXT: Review the provider repair and existing delivered story records before program closure.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Closure Confirmation
- [ ] Work walkthrough shared with user.
- [ ] Acceptance criteria confirmed by user.
- [ ] Applicable anti-pattern checks are clear or escalated with evidence.

## Noting Behavior
Record program decisions and cross-story implications here. Keep tactical findings in child task notes.
Preserve append-only history and source-backed claims; unknown behavior stays explicitly unknown.

## Context / Handoff Summary
CLOSED BY OWNER: delivered scope is turned in; see the completion summary at the top. Any earlier
review/resume instructions below are historical. Deferred user-created-object work is parked in the
backlog epic and does not request continued implementation.

Provider artifact ownership is repaired and ready for review: all original downstream provider proofs
pass, native regressions stay correct-behavior assertions, and docs/assets are synchronized. Existing
annotation, instance-injection and Protocol repairs are retained. Broader reference/lifetime redesign
is retired. The prior real-Iris cleanup observation is separate and was not rerun by this provider repair.
