# Task: Expand Frame ACL Chain Test Surface

## Metadata
- Task ID: TASK-2026-04-05-expand-frame-acl-chain-test-surface
- Story: STORY-2026-04-05-frame-acl-configuration-chain
- Status: done
- Owner: codex
- Priority: p0
- Created: 2026-04-05T12:25:00Z
- Updated: 2026-04-05T17:50:09Z

## Objective
Add a large validation tranche for the frame ACL chain slice:
- 50 unit tests
- 20 component tests
- a few integration tests

The goal is to push the chain mechanics beyond the earlier focused surface and
make the history/current/head/rollback/container/facade behavior much harder to
break by accident.

## Ticket Contract
- ENTRY_GATE: the chain mechanics are already landed and the user explicitly
  requested a large chain-focused test expansion pass.
- EXECUTION_BOUNDARY: chain-focused tests only across unit/component/integration
  layers.
- DEPENDENCIES:
  - src/melder/aether/nexus/acl/frame_acl_configuration.py
  - src/melder/aether/nexus/acl/frame_acl_configuration_chain.py
  - src/melder/aether/nexus/acl/frame_acl_container.py
  - src/melder/aether/nexus/acl/frame_acl_builder.py
  - src/melder/aether/nexus/frame_acl_manager.py
  - src/melder/aether/nexus/nexus.py
- EXIT_GATE: the new chain validation tranche exists and the focused test run
  passes.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if the current chain semantics
  are too unstable to test at this scale without first changing behavior.

## Scope Boundaries
- In scope:
  - chain mechanics
  - config/container/builder/manager/facade interactions that directly support the chain
  - unit/component/integration tests
- Out of scope:
  - new chain behavior
  - ACL propagation engine
  - viewer/codegen integration

## State Transition Event
- from_state: in_progress
- to_state: review
- transition_reason: the requested chain test expansion tranche is landed and
  the focused unit/component/integration run passed.

## Steps / Checklist
- [ ] Inspect existing chain-focused tests and identify the current gaps.
- [ ] Add the large unit test tranche.
- [ ] Add the large component test tranche.
- [ ] Add a few integration tests.
- [ ] Run focused validation.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- expanded unit/component/integration chain tests

## Files / Paths Impacted
- tests/unit/melder/aether/
- tests/component/melder/aether/
- tests/integration/melder/aether/
- codex/context_compass/tickets/tasks/2026-04-05_expand_frame_acl_chain_test_surface_task.md
- codex/context_compass/attention_board.md

## Validation
- Completed:
  - `python -m pytest --collect-only -q tests/unit/melder/aether/test_frame_acl_chain_matrix.py`
  - `python -m pytest --collect-only -q tests/component/melder/aether/test_frame_acl_chain_component_matrix.py`
  - `python -m pytest --collect-only -q tests/integration/melder/aether/test_frame_acl_chain_integration.py`
  - `python -m pytest -q tests/unit/melder/aether/test_frame_acl_chain_matrix.py tests/component/melder/aether/test_frame_acl_chain_component_matrix.py tests/integration/melder/aether/test_frame_acl_chain_integration.py`
  - `python -m py_compile tests/unit/melder/aether/test_frame_acl_chain_matrix.py tests/component/melder/aether/test_frame_acl_chain_component_matrix.py tests/integration/melder/aether/test_frame_acl_chain_integration.py`

## Risks / Rollback Notes
- Risk: the expansion pads counts with low-value tests.
  Rollback: keep tests contract-driven and behavior-oriented even when using
  parametrized matrices.

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
  - none
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: n/a

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-04-05T12:37:00Z
  TYPE: MEASURE
  CLAIM: The expanded chain validation tranche is landed and green. The new
    unit matrix file collects exactly 50 unit tests, the new component matrix
    file collects exactly 20 component tests, and the new integration file
    collects 3 integration tests. The focused run over those new files passed
    cleanly after two test-contract fixes: store the original configuration id
    before tail-trim cleanup, and enable Nexus in the detach tests so they
    exercise the real `check_for_aetheric_frame(...)` cleanup path.
  EVIDENCE:
  - command:python -m pytest --collect-only -q tests/unit/melder/aether/test_frame_acl_chain_matrix.py
  - command:python -m pytest --collect-only -q tests/component/melder/aether/test_frame_acl_chain_component_matrix.py
  - command:python -m pytest --collect-only -q tests/integration/melder/aether/test_frame_acl_chain_integration.py
  - command:python -m pytest -q tests/unit/melder/aether/test_frame_acl_chain_matrix.py tests/component/melder/aether/test_frame_acl_chain_component_matrix.py tests/integration/melder/aether/test_frame_acl_chain_integration.py
  IMPACT: The frame ACL chain slice now has a much denser regression surface
    before the next ACL mechanics/design layer is built on top of it.
  NEXT: review the new chain test tranche and decide whether to continue into
    ACL configuration design or ask for another targeted validation slice.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-05T12:25:00Z
  TYPE: PLAN
  CLAIM: The existing chain surface is real but still narrow. We already have
    focused tests around config, chain, builder, container, manager, and a
    small component/integration slice, but the user now wants one much larger
    validation tranche before more ACL design work continues. The right shape
    is a behavior-heavy matrix:
    - unit tests for chain/config/container/builder/manager mechanics
    - component tests for Nexus/Aether/descriptor/container interactions
    - integration tests using real Spellbook/Aether/Nexus runtime paths
  EVIDENCE:
  - tests/unit/melder/aether/test_frame_acl_configuration_chain.py:1-267
  - tests/unit/melder/aether/test_frame_acl_manager.py:1-127
  - tests/component/melder/aether/test_frame_acl_component.py:1-65
  - tests/integration/melder/aether/test_aether_integration_nexus_passive_ingest.py:1-88
  IMPACT: The chain slice needs a much denser regression surface before we pile
    the next ACL design/mechanics layer on top of it.
  NEXT: add a new large unit/component/integration test matrix that targets the
    live chain behavior directly.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
This task exists to add a large chain-focused validation tranche before the
next ACL mechanics/design slice continues.
