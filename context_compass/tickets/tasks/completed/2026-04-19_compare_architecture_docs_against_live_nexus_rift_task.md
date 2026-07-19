# Task: Compare Architecture Docs Against Live Nexus Rift
- Completed: 2026-04-19T16:37:39Z
- Summary: Closed during the 2026-04-19 backlog cleanup pass after review/completed-downstream state.


## Metadata
- Task ID: TASK-2026-04-19-compare-architecture-docs-against-live-nexus-rift
- Story:
- Status: done
- Owner: codex
- Priority: p0
- Created: 2026-04-19T00:20:00Z
- Updated: 2026-04-19T16:37:39Z

## Objective
Compare the current AR architecture/component docs to the live `Nexus` /
`Rift` / `RiftSpace` implementation and identify the concrete drift.

## Ticket Contract
- ENTRY_GATE: user explicitly asked for a comparison of the existing
  architecture/component docs against the live Nexus/Rift implementation.
- EXECUTION_BOUNDARY: investigation only across:
  - `codex/context_compass/system_docs/src_architecture.md`
  - `codex/context_compass/system_docs/src_components.md`
  - `src/melder/aether/nexus/nexus.py`
  - `src/melder/aether/nexus/rift/rift.py`
  - `src/melder/aether/nexus/rift/rift_space/rift_space.py`
  - directly related viewer/projection helpers only when needed for proof
- DEPENDENCIES:
  - codex/context_compass/system_docs/src_architecture.md
  - codex/context_compass/system_docs/src_components.md
  - src/melder/aether/nexus/nexus.py
  - src/melder/aether/nexus/rift/rift.py
  - src/melder/aether/nexus/rift/rift_space/rift_space.py
- EXIT_GATE: the concrete doc/code drift is mapped with evidence and the next
  cleanup order is explicit.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if the comparison expands beyond
  bounded Nexus/Rift/room ownership and lifecycle seams.

## Scope Boundaries
- In scope:
  - current docs vs current Nexus/Rift/room implementation
  - ownership drift
  - lifecycle/refresh drift
  - room-kind and surface drift
- Out of scope:
  - immediate code changes
  - repo-wide doc sweep
  - unrelated lower runtime architecture

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: bounded investigation requested directly by the user.

## Steps / Checklist
- [ ] Read the relevant doc sections in `src_architecture.md`.
- [ ] Read the relevant doc sections in `src_components.md`.
- [ ] Read the live `Nexus` / `Rift` / `RiftSpace` seams.
- [ ] Record the concrete mismatches with evidence.
- [ ] Propose a cleanup order.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- evidence-backed drift map
- proposed cleanup order

## Files / Paths Impacted
- codex/context_compass/tickets/tasks/2026-04-19_compare_architecture_docs_against_live_nexus_rift_task.md
- codex/context_compass/attention_board.md

## Validation
- Not run.

## Risks / Rollback Notes
- Risk: older historical doc drift may appear alongside live runtime drift.
- Rollback: investigation only.

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
- CLEANUP_TRIGGER: none

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-04-19T00:26:00Z
  TYPE: FACT
  CLAIM: The docs still under-describe the current refresh/orchestration split.
    Live code now has:
    - `Nexus` owning projection compilation plus ACL-change fan-out
    - `Rift` owning frame contracts and per-Rift refresh orchestration
    - `RiftSpace` owning installed projections plus viewer rebuild
    The docs capture parts of this, but not the whole operational chain as one
    coherent ownership model.
  EVIDENCE:
  - src/melder/aether/nexus/nexus.py:1797-1984
  - src/melder/aether/nexus/rift/rift.py:348-547
  - src/melder/aether/nexus/rift/rift_space/rift_space.py:373-680
  - codex/context_compass/system_docs/src_architecture.md:452-507
  - codex/context_compass/system_docs/src_components.md:500-590
  IMPACT: The docs are not wildly wrong anymore, but they still do not present
    the live `Nexus -> Rift -> RiftSpace` projection/viewer refresh chain as a
    single explicit contract.
  NEXT: record the concrete drift areas by category so cleanup can be ordered.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-04-19T00:26:00Z
  TYPE: FACT
  CLAIM: `src_architecture.md` and `src_components.md` still carry historical
    room/command references that no longer match the live tree:
    - `dynamic_rift_space.py`
    - `dynamic_command_system.py`
    - selected-target-driven command wording
    The live code uses `capability` / `codegen` room classes and the command
    surface is now projection-driven.
  EVIDENCE:
  - src/melder/aether/nexus/rift/rift_space/rift_space.py:42-84
  - src/melder/aether/nexus/rift/rift.py:50-65
  - codex/context_compass/system_docs/src_architecture.md:992-998
  - codex/context_compass/system_docs/src_architecture.md:1159-1165
  - codex/context_compass/system_docs/src_components.md:711-752
  - codex/context_compass/system_docs/src_components.md:1901-1950
  - codex/context_compass/system_docs/src_components.md:2362-2375
  IMPACT: Some of the room/command sections are still half historical and need
    a broader AR documentation sweep than the tiny drift cleanup lane.
  NEXT: separate â€œalready fixedâ€ drift from â€œstill remainingâ€ drift in the user
    summary.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-04-19T00:26:00Z
  TYPE: FACT
  CLAIM: One meaningful new architectural delta since the original docs is that
    the ACL-driven projection refresh barrier is now config-backed through
    `NexusConfiguration`. The flow exists in code and is mentioned briefly in
    docs, but the config surface and its effect on refresh orchestration are
    not yet woven through the main AR ownership sections.
  EVIDENCE:
  - src/melder/aether/nexus/configuration/nexus_configuration.py:63-88
  - src/melder/aether/nexus/configuration/nexus_configuration.py:243-268
  - src/melder/aether/nexus/nexus.py:1914-1984
  - codex/context_compass/system_docs/src_architecture.md:501-507
  - codex/context_compass/system_docs/src_components.md:2003-2010
  IMPACT: The docs acknowledge the refresh barrier, but not yet at the same
    level of completeness as the rest of the Nexus/Rift governance story.
  NEXT: report this as one of the live doc/code drift categories instead of
    pretending the current docs are fully caught up.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

## Context / Handoff Summary
This task compares the current architecture/component docs to the live
Nexus/Rift/room implementation and maps the concrete drift.