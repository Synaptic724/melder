# Task: RiftEngine Core and Codegen Validation Pipeline

## Metadata
- Task ID: TASK-2026-02-25-riftengine-and-codegen-pipeline
- Story: STORY-2026-02-25-aethericrift-implementation
- Status: done
- Owner: codex
- Priority: p0
- Created: 2026-02-25T10:57:22Z
- Updated: 2026-03-15T22:05:00Z
- Created By: e3098096-e1f8-4279-b98f-082737b2cca9

## Objective
Implement the system-wide RiftEngine that lives on the Aether singleton,
including the CodeBlock registry, AST parsing, structural validation
(allowlist), symbol resolution against CapabilityManifest, and lane
classification (safe vs mutation).

## Ticket Contract
- ENTRY_GATE: design artifacts approved, implementation story ready
- EXECUTION_BOUNDARY: RiftEngine module and codegen pipeline internals only
- DEPENDENCIES: codegen_validation_pipeline_design.md,
  aethericrift_facade_and_profile_architecture.md (Section 1)
- EXIT_GATE: RiftEngine passes unit tests for AST validation, symbol
  resolution, and lane classification
- FAILURE_ESCALATION: raise DECISION_REQUEST if AST allowlist or lane
  classification rules are ambiguous

## Scope Boundaries
- In scope:
  - CodeBlock model (block_id, source, source_hash, manifest_id, policy_hash)
  - AST parse using stdlib `ast.parse`
  - Structural validation: walk AST nodes against allowlist, deny forbidden constructs
  - Symbol resolution: resolve Name/Attribute/Call against CapabilityManifest
  - Lane classification: safe (default) vs mutation (ClassDef/FunctionDef/graph-modifying)
  - CodeBlock registry and hashing
- Out of scope:
  - Governed execution (Phase 3 — Workspace task)
  - FrameProfile/ConduitProfile (Phase 2 — Profiles task)
  - AethericRift facade / RiftContext (Phase 1b — Facade task)
  - Audit/observability emission (Phase 4 deferred)

## State Transition Event
- from_state: draft
- to_state: ready
- transition_reason: design artifacts approved and implementation story created.

## Steps / Checklist
- [ ] Create `CodeBlock` model with immutable fields per design.
- [ ] Implement `RiftEngine` class with CodeBlock registry.
- [ ] Implement AST parse stage (stdlib `ast.parse`).
- [ ] Implement structural validation with configurable allowlist per design tables.
- [ ] Implement symbol resolution against `CapabilityManifest` interface.
- [ ] Implement lane classification (safe vs mutation) per design rules.
- [ ] Wire RiftEngine into Aether singleton.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- `RiftEngine` class with CodeBlock registry and validation pipeline.
- `CodeBlock` model.
- `CapabilityManifest` interface/protocol.
- Unit tests for AST validation, symbol resolution, and lane classification.

## Files / Paths Impacted
- src/melder/aether/aetheric_rift/ (new package)
- src/melder/aether/aether.py (RiftEngine wiring)

## Validation
- Not run.
- Recommended commands:
  - `pytest tests/aetheric_rift/test_ast_validation.py -v`
  - `pytest tests/aetheric_rift/test_symbol_resolution.py -v`
  - `pytest tests/aetheric_rift/test_lane_classification.py -v`

## Risks / Rollback Notes
- Risk: AST allowlist too restrictive for useful agent workflows.
  Rollback: expand allowlist based on agent testing feedback.
- Risk: symbol resolution performance under large manifests.
  Rollback: add caching layer in follow-up task.

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
- [ ] Notes quality maintained (`SCORE_0_TO_10` >= `workflow.ticket_microcycle.minimum_note_score`)
- [ ] Applicable anti-pattern checks are clear or escalated with evidence.
- [ ] Acceptance criteria reviewed with user and confirmed
- [ ] Board sync completed for successor routing or closure anchor update.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: false
- ARTIFACT_PATHS:
  - none
- DISPOSITION: delete_on_close
- CLEANUP_TRIGGER: n/a

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-02-25T10:57:22Z
  TYPE: PLAN
  CLAIM: This task implements the codegen validation pipeline design artifact stages 1-5 (intake through lane classification). Governed execution and result/audit are deferred to the Workspace task.
  EVIDENCE:
  - tickets/artifacts/codegen_validation_pipeline_design.md:30-87
  - tickets/artifacts/codegen_validation_pipeline_design.md:115-158
  - tickets/artifacts/aethericrift_facade_and_profile_architecture.md:17-23
  IMPACT: Completing this task provides the validation substrate for all downstream AethericRift phases.
  NEXT: begin implementation of CodeBlock model and RiftEngine class.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

## Context / Handoff Summary
First implementation task for AethericRift. Covers the codegen validation pipeline (stages 1-5) and RiftEngine as system-wide infrastructure. Downstream tasks (facade, profiles, workspace) depend on this task completing first.


## Completion Summary
- Completed: 2026-03-15T22:05:00Z
- Summary: Superseded or completed during AR packaging cleanup; retained for historical reference.

