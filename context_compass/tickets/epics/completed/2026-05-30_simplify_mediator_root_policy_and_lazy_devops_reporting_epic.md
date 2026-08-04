# Epic: Simplify Mediator Root Policy And Lazy DevOps Reporting

## Metadata
- Epic ID: EPIC-2026-05-30-simplify-mediator-root-policy-and-lazy-devops-reporting
- Status: completed
- Owner: codex
- Agent Name: searcher_0
- Priority: p1
- Created: 2026-05-30T10:28:39Z
- Updated: 2026-06-16T23:04:23Z
- Target Window: 2026-Q2
- Related Program/Initiative: DevOps transaction policy cleanup and reporting ownership simplification

## Problem / Opportunity
The current mediator policy surface is overlapping and semantically muddy. One
frame can currently express root arbitration through:
- `change_control_mode`
- `allow_multiple_root_transactions`
- `queue_competing_root_transactions`
- `max_transaction_wait_time_in_seconds`

That makes the root-session gate harder to reason about than it should be.
At the same time, `DevopsIdentity.update_metadata(...)` triggers immediate
registry refresh, so cheap runtime identity updates force the caller thread to
participate in registry-maintenance work on the hot path.

These are separate symptoms of the same design problem:
- runtime ownership state
- admission policy
- reporting/derived topology maintenance
are not separated cleanly enough.

## MRP Alignment (Most Reasonable Product)
The right foundation is not a bigger pile of flags. The right foundation is:
- one honest root-arbitration policy model
- one clear separation between identity truth and derived reporting
- one mediator-owned place where transaction-era registry updates happen

That gives us a control-plane surface that is easier to reason about and
cheaper in hot runtime paths.

## Ticket Contract
- ENTRY_GATE: the current config and eager-refresh seams are evidenced from live source before implementation starts.
- EXECUTION_BOUNDARY:
  - `src/melder/aether/aetheric_frame/aetheric_frame_configuration.py`
  - `src/melder/aether/aetheric_frame/dev_ops/change_control_manager/change_control_manager.py`
  - `src/melder/aether/aetheric_frame/dev_ops/change_control_manager/transaction_manager/transaction_mediator.py`
  - `src/melder/aether/aetheric_frame/dev_ops/devops_identity.py`
  - `src/melder/aether/aetheric_frame/dev_ops/devops_information_registry.py`
  - directly implicated strategy/runtime callsites only
- DEPENDENCIES:
  - `tickets/tasks/2026-05-24_make_parallel_root_transactions_default_task.md`
  - `tickets/tasks/completed/2026-05-22_add_pending_transaction_start_queue_task.md`
  - `tickets/tasks/2026-05-23_investigate_spellbook_conduit_devops_dependency_cleanup_task.md`
- EXIT_GATE: the new policy surface is explicit, eager identity refresh is removed from the hot path, and the replacement mediator-owned registry update path is accepted.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if the replacement policy surface still needs a second layer for strategy-local arbitration.

## Goals (Outcomes)
- Replace the overlapping root-session config surface with one clearer policy model.
- Remove eager `DevopsIdentity -> DevopsInformationRegistry.refresh_identity(...)` churn from runtime update paths.
- Move necessary registry refresh/update work onto mediator-owned request/session paths.
- Keep the registry useful for topology and transaction lookup without making identity updates responsible for maintaining it eagerly.

## Non-Goals (Explicit Exclusions)
- Delete the transaction mediator.
- Redesign conflict or embargo semantics in the same slice.
- Broad devops registry rewrites unrelated to root-session policy or eager refresh.
- Full `DevopsInformationStrategy` architecture in the first cut if a smaller mediator-owned refresh seam is enough.

## Scope Boundaries
- In scope:
  - root-session policy/config cleanup
  - eager identity refresh removal
  - mediator-owned registry update seam
- Out of scope:
  - broader transaction-family redesign
  - unrelated performance refactors
  - wider spellbook/conduit ownership changes

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: the config overlap and eager identity refresh seam are now explicit enough to justify a dedicated umbrella.

## Success Metrics
- Root-session policy is explainable through one primary config concept instead of overlapping knobs.
- Identity updates no longer trigger registry rebuild work on the caller thread.
- Registry updates still happen correctly for admission/reporting paths where they are actually needed.

## Requirements (Functional + Non-Functional)
- Preserve current correctness for transaction registration and topology lookup.
- Preserve public runtime behavior unless a deliberate policy rename/replacement is accepted.
- Keep hot-path work lower after the eager refresh removal.
- Keep docstrings/comments aligned if runtime semantics change.

## Constraints / Assumptions
- The current code is authoritative over older task wording.
- The first implementation slice should stay small and reviewable.
- Warning behavior is observability, not a good primary arbitration model.

## Dependencies / External References
- `src/melder/aether/aetheric_frame/aetheric_frame_configuration.py`
- `src/melder/aether/aetheric_frame/dev_ops/change_control_manager/change_control_manager.py`
- `src/melder/aether/aetheric_frame/dev_ops/change_control_manager/transaction_manager/transaction_mediator.py`
- `src/melder/aether/aetheric_frame/dev_ops/devops_identity.py`
- `src/melder/aether/aetheric_frame/dev_ops/devops_information_registry.py`

## Milestones (Track Progress)
- [x] Milestone 1: Define the replacement root-policy model.
- [x] Milestone 2: Remove eager identity refresh from runtime update paths.
- [x] Milestone 3: Land mediator-owned registry refresh/update responsibility.

## Stories (Required to Complete)
- [x] Story: replace overlapping mediator root-session config with one clearer arbitration model.
- [x] Story: decouple `DevopsIdentity` metadata updates from eager registry maintenance.
- [x] Story: define the DevOps transaction control-plane philosophy and open questions.

## Tasks (Cross-Cutting or Epic-Level)
- [ ] Task: investigate and plan the exact config replacement and registry-refresh move.
- [ ] Task: implement the config replacement.
- [ ] Task: implement mediator-owned registry refresh/update flow.
- [ ] Task: Verify Ticket Microcycle enforcement across active tickets/stories/tasks.

## Acceptance Criteria (Epic Done)
- The dedicated config cleanup and lazy-registry-update stories are accepted.
- Eager `update_metadata(...) -> refresh_identity(...)` is gone from the hot path.
- The new root-session config surface is documented and coherent.

## Risks / Mitigations
- Risk: removing eager refresh breaks derived spellbook/conduit relation updates.
  Mitigation: move that work to explicit mediator/request/session seams instead of silently dropping it.
- Risk: renaming or replacing the config surface widens into a public-API cleanup.
  Mitigation: keep the first cut narrowly on semantics and direct callsites.

## Applicable Anti-Patterns
- [ ] No epic-state transition without story-level evidence.
- [ ] No closure while required stories are incomplete or unaccepted.
- [ ] No program claims without source evidence from story/task notes.

## Validation / Test Approach
- Focus first on the directly implicated unit/integration rings around frame config, mediator behavior, and devops registry/identity behavior.
- Do not claim runtime speed gains without measurement.

## Rollout / Adoption Plan
- Start with one small semantic slice:
  - define the replacement root policy surface
  - remove eager identity refresh
- Then wire the mediator-owned registry update path and validate behavior.

## Open Questions
- Should the replacement root policy be a single enum or an enum plus timeout only for queued mode?
- Should registry update live at request admission, session registration, or strategy on_start/on_end hooks?

## Decision Log
- Decision: this deserves its own epic instead of pretending the performance epic owns the semantic policy problem.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: false
- ARTIFACT_PATHS:
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: user-directed after the redesign direction is accepted

## Notes
- DATETIME: 2026-05-30T10:28:39Z
  TYPE: FACT
  CLAIM: The current root-session policy and identity-refresh model are both
    explicit design seams now. The frame config and mediator both carry
    overlapping root-arbitration knobs, while `DevopsIdentity.update_metadata(...)`
    immediately triggers registry refresh work on the same caller thread.
  EVIDENCE:
  - src/melder/aether/aetheric_frame/aetheric_frame_configuration.py:85-95
  - src/melder/aether/aetheric_frame/aetheric_frame_configuration.py:380-558
  - src/melder/aether/aetheric_frame/dev_ops/change_control_manager/transaction_manager/transaction_mediator.py:113-193
  - src/melder/aether/aetheric_frame/dev_ops/change_control_manager/transaction_manager/transaction_mediator.py:929-972
  - src/melder/aether/aetheric_frame/dev_ops/devops_identity.py:272-290
  - src/melder/aether/aetheric_frame/dev_ops/devops_information_registry.py:384-426
  IMPACT: The next execution slice can stay narrow and high signal: config cleanup plus lazy registry update.
  NEXT: create the tactical task for the first investigation/plan slice and route the board to it.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Closure Confirmation
- [ ] Work walkthrough shared with user
- [ ] Acceptance criteria confirmed by user
- [ ] Applicable anti-pattern checks are clear or escalated with evidence.

## Noting Behavior
- Note focus: program-level direction, cross-story tradeoffs, and tranche order.
- Add notes when priorities, sequencing, or scope boundaries change.
- Reference story/task evidence instead of duplicating tactical execution logs.
- Keep notes append-only and preserve UNKNOWN-first promotion discipline.

## Context / Handoff Summary
This epic exists because the mediator root-session policy surface and the eager
identity-driven registry refresh path are separate but related design problems.
The immediate next step is a small investigation/plan slice that defines the
replacement config model and the mediator-owned registry-update seam.


## Closure
- DATETIME: 2026-06-16T23:04:23Z
  TYPE: DECISION
  CLAIM: Epic CLOSED (user accepted 2026-06-14). All three milestones verified
    complete in live source. M1 one root-policy model: change_control_mode /
    allow_multiple_root_transactions / queue_competing_root_transactions are
    gone; only max_transaction_wait_time_in_seconds remains. M2 eager identity
    refresh removed: DevopsIdentity.update_metadata is local-only (no implicit
    registry refresh); refresh_registry/refresh_identity are explicit with no
    eager callers. M3 mediator-owned registry update: commit-delta fact
    baselines (apply_commit_delta -> report_fact) + eager relational mirrors.
    All three stories done (two via the scope-acquisition control plane,
    STORY-2026-06-12 completed; one via the philosophy story, 2026-06-05
    completed). The plane also delivered per-family claim modes + the unlink and
    the three SpellIndex (notch/add/remove) transactions on this surface.
  EVIDENCE:
  - src/melder/aether/aetheric_frame/dev_ops/devops_identity.py:272-292
  - codex/context_compass/tickets/stories/completed/2026-06-12_implement_scope_acquisition_control_plane_story.md
  - codex/context_compass/tickets/tasks/2026-06-14_spell_index_transactions_backend_task.md
  IMPACT: Mediator root-policy simplification + lazy devops reporting delivered.
  NEXT: none (SpellIndex member-store seams = general_0; mutation transaction +
    info-strategy probe/audit extensions = separate future work).
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
