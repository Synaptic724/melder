# Task: Implement Frame-Scoped Named ACL Contracts And Rift Selection
- Completed: 2026-04-13T12:00:15Z
- Summary: Archived the first named-contract implementation cut after the later separate-family chain refactor superseded it as the live model.

## Metadata
- Task ID: TASK-2026-04-11-implement-frame-scoped-named-acl-contracts-and-rift-selection
- Story: STORY-2026-04-11-investigate-multi-contract-frame-policy-model
- Status: done
- Owner: codex
- Priority: p0
- Created: 2026-04-11T00:12:09Z
- Updated: 2026-04-11T09:47:25Z

## Objective
Add per-frame named ACL contract registration, seed `"default"` automatically,
reject duplicate names on the same frame, and let Rift select the named
contract for a targeted frame.

## Ticket Contract
- ENTRY_GATE: the current-model audit and target-model definition are complete
  enough that the first implementation cut is explicit.
- EXECUTION_BOUNDARY: frame-local named ACL config registry, default seeding,
  duplicate-name rejection, Rift-side selected contract-name binding, Nexus
  viewer projection updates, and focused tests only.
- DEPENDENCIES:
  - tickets/tasks/2026-04-11_audit_current_nexus_acl_model_and_migration_seams.md
  - tickets/tasks/2026-04-11_define_frame_scoped_contract_registry_and_rift_binding_model.md
  - src/melder/aether/nexus/acl/frame_acl_container.py
  - src/melder/aether/nexus/frame_acl_manager.py
  - src/melder/aether/nexus/nexus.py
  - src/melder/aether/nexus/rift/frame_link/frame_link_contract.py
  - src/melder/aether/nexus/rift/rift.py
  - src/melder/utilities/interfaces/interfaces.py
  - tests/unit/melder/aether/test_frame_acl_container.py
  - tests/unit/melder/aether/test_frame_acl_manager.py
  - tests/unit/melder/aether/test_nexus.py
- EXIT_GATE: one frame can own many named ACL configs, `"default"` is seeded
  automatically, duplicate names fail, and Rift viewer projection consumes the
  selected named contract instead of always the frame's current config.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if the first cut forces
  separation of ACL/codegen registries or a broader ACL-history rewrite.

## Scope Boundaries
- In scope:
  - named ACL configs per frame
  - `"default"` seeding
  - duplicate-name rejection
  - selected contract names on `FrameLinkContract`
  - Rift target selection of contract name
  - Nexus viewer-build path using selected named config
  - focused tests
- Out of scope:
  - separate codegen registry
  - broad ACL chain redesign
  - access-mode runtime behavior

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: the user approved the first implementation cut after the
  current-model audit and target-model definition were documented.

## Steps / Checklist
- [ ] Add per-frame named ACL config storage to `FrameACLContainer`.
- [ ] Seed `"default"` from the current restrictive default config.
- [ ] Add manager/Nexus facade methods for named registration/lookup/listing.
- [ ] Extend `FrameLinkContract` to carry selected contract names per frame.
- [ ] Extend `Rift.target_frame(...)` to accept/select contract names.
- [ ] Update Nexus viewer projection/cache paths to use selected named configs.
- [ ] Add/update focused tests.
- [ ] Document findings, implementation, and validation in `## Notes`.

## Deliverables
- named ACL config registry per frame
- Rift-selected contract name binding
- updated viewer projection path
- focused tests

## Files / Paths Impacted
- src/melder/aether/nexus/acl/frame_acl_container.py
- src/melder/aether/nexus/frame_acl_manager.py
- src/melder/aether/nexus/nexus.py
- src/melder/aether/nexus/rift/frame_link/frame_link_contract.py
- src/melder/aether/nexus/rift/rift.py
- src/melder/utilities/interfaces/interfaces.py
- tests/unit/melder/aether/test_frame_acl_container.py
- tests/unit/melder/aether/test_frame_acl_manager.py
- tests/unit/melder/aether/test_nexus.py
- codex/context_compass/attention_board.md

## Validation
- Not run.
- Recommended commands:
  - `python -m pytest -q tests/unit/melder/aether/test_frame_acl_container.py tests/unit/melder/aether/test_frame_acl_manager.py tests/unit/melder/aether/test_nexus.py`

## Risks / Rollback Notes
- Risk: the first cut accidentally breaks the existing chain semantics.
  Rollback: keep the chain in place and add the named registry as a parallel
  selection layer only.

## Applicable Anti-Patterns
- [ ] No status transition without evidence-backed transition reason.
- [ ] No implementation/validation from `UNKNOWN` or `HYPOTHESIS`.
- [ ] No closure without acceptance confirmation and board-sync completion.

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
- ARTIFACTS_REQUIRED: false
- ARTIFACT_PATHS:
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: n/a

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-04-11T00:12:09Z
  TYPE: PLAN
  CLAIM: The first cut is intentionally narrow. We are not replacing the ACL
    chain; we are layering named per-frame selection on top of the typed config
    model that already exists.
  EVIDENCE:
  - tickets/tasks/2026-04-11_audit_current_nexus_acl_model_and_migration_seams.md:1-170
  - tickets/tasks/2026-04-11_define_frame_scoped_contract_registry_and_rift_binding_model.md:1-122
  - user_instruction: "go ahead and implement this"
  IMPACT: The implementation can stay incremental and low-risk instead of
    turning into an ACL subsystem rewrite.
  NEXT: patch `FrameACLContainer` first so the per-frame named registry and
    `"default"` seeding exist before changing Rift selection.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-11T00:12:09Z
  TYPE: FACT
  CLAIM: The first implementation cut is now landed in source. `FrameACLContainer`
    owns a per-frame named configuration dictionary seeded with `"default"`,
    duplicate names are rejected, `FrameACLManager` and `Nexus` expose named
    registration/lookup/listing facades, `FrameLinkContract` now carries selected
    contract names per frame, `Rift.target_frame(...)` accepts `contract_name`,
    and Nexus viewer projection now resolves the selected named config instead of
    always using the frame's current selected chain node.
  EVIDENCE:
  - src/melder/aether/nexus/acl/frame_acl_container.py:185-203
  - src/melder/aether/nexus/acl/frame_acl_container.py:322-476
  - src/melder/aether/nexus/frame_acl_manager.py:323-392
  - src/melder/aether/nexus/nexus.py:1204-1285
  - src/melder/aether/nexus/nexus.py:1548-1959
  - src/melder/aether/nexus/rift/frame_link/frame_link_contract.py:42-167
  - src/melder/aether/nexus/rift/frame_link/frame_link_contract.py:206-400
  - src/melder/aether/nexus/rift/rift.py:410-510
  - src/melder/utilities/interfaces/interfaces.py:2564-2595
  - src/melder/utilities/interfaces/interfaces.py:6384-6394
  - tests/unit/melder/aether/test_frame_acl_container.py:17-131
  - tests/unit/melder/aether/test_frame_acl_manager.py:111-225
  - tests/unit/melder/aether/test_frame_link_contract_profiles.py:78-164
  - tests/unit/melder/aether/test_nexus.py:803-874
  IMPACT: The lane is ready for focused validation; if tests pass, the first
    named-contract selection seam will be proven end to end.
  NEXT: run the focused ACL container/manager/frame-link/Nexus unit slice and
    fix any contract drift the tests expose.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-11T00:12:09Z
  TYPE: MEASURE
  CLAIM: The first focused unit slice is close but not green yet. Three failures
    surfaced and all are test-surface drift, not runtime contract collapse:
    - two new manager tests forgot to import `FrameACLConfiguration`
    - one `FrameLinkContract.describe()` expectation is stale because the summary
      now includes `selected_contract_names_by_frame_name`
  EVIDENCE:
  - tests/unit/melder/aether/test_frame_acl_manager.py:173-225
  - tests/unit/melder/aether/test_frame_link_contract_profiles.py:222-226
  - validation_result: `python -m pytest -q tests/unit/melder/aether/test_frame_acl_container.py tests/unit/melder/aether/test_frame_acl_manager.py tests/unit/melder/aether/test_frame_link_contract_profiles.py tests/unit/melder/aether/test_nexus.py` -> 3 failed, 88 passed
  IMPACT: The next step is a narrow test repair pass, not a runtime redesign.
  NEXT: fix the missing import and update the stale frame-link summary expectation,
    then rerun the focused unit slice.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-11T00:12:09Z
  TYPE: MEASURE
  CLAIM: The first named-contract implementation cut is now green on the focused
    unit slice. A frame can own many named ACL configurations with `"default"`
    seeded automatically, duplicate names on the same frame fail fast, `Rift`
    now carries selected contract names per targeted frame, and Nexus viewer
    projection now consumes the selected named config instead of always the
    frame's current selected chain node.
  EVIDENCE:
  - src/melder/aether/nexus/acl/frame_acl_container.py:185-203
  - src/melder/aether/nexus/acl/frame_acl_container.py:322-476
  - src/melder/aether/nexus/frame_acl_manager.py:323-392
  - src/melder/aether/nexus/nexus.py:1204-1285
  - src/melder/aether/nexus/nexus.py:1548-1959
  - src/melder/aether/nexus/rift/frame_link/frame_link_contract.py:42-167
  - src/melder/aether/nexus/rift/frame_link/frame_link_contract.py:206-400
  - src/melder/aether/nexus/rift/rift.py:410-510
  - tests/unit/melder/aether/test_frame_acl_container.py:17-131
  - tests/unit/melder/aether/test_frame_acl_manager.py:111-225
  - tests/unit/melder/aether/test_frame_link_contract_profiles.py:78-226
  - tests/unit/melder/aether/test_nexus.py:803-874
  - validation_result: `python -m pytest -q tests/unit/melder/aether/test_frame_acl_container.py tests/unit/melder/aether/test_frame_acl_manager.py tests/unit/melder/aether/test_frame_link_contract_profiles.py tests/unit/melder/aether/test_nexus.py` -> 91 passed
  IMPACT: The first migration seam is proven well enough to review before we
    decide whether the next cut should add named codegen contracts, migrate more
    public Nexus APIs, or generalize the cache/selection model further.
  NEXT: review this first named-contract cut and decide the next implementation slice.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-11T00:12:09Z
  TYPE: FACT
  CLAIM: One small public-contract cleanup landed after the green runtime test pass.
    `IRift.target_frame(...)` now exposes the new `contract_name` argument, and
    `INexus` now exposes the named ACL configuration facade methods so the public
    protocol matches the runtime seam we just implemented.
  EVIDENCE:
  - src/melder/utilities/interfaces/interfaces.py:2564-2616
  - src/melder/utilities/interfaces/interfaces.py:6384-6395
  - src/melder/utilities/interfaces/interfaces.py:6577-6606
  IMPACT: The exported protocol layer is no longer lagging behind the runtime.
  NEXT: leave the tranche in review and decide the next contract-registry expansion.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
This task implements the first narrow cut of the frame-scoped named contract model.
