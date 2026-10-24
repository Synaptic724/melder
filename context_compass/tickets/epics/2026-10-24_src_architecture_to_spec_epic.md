

# Epic: src_architecture to its authoring spec, about 1,000 lines lighter

## Metadata
- Epic ID: EPIC-2026-10-24-src_architecture_to_spec
- Status: in_progress
- Owner: Mark (owner; scope and acceptance)
- Agent Name: melder_3
- Agent Role: synaptic_python_developer
- Priority: p2
- Created: 2026-10-24T20:58:00Z
- Updated: 2026-10-24T20:58:00Z
- Target Window: 2026-10; edits apply after the two lanes now writing the same documents land (Dependencies)
- Related Program/Initiative: system documents kept to their authoring instructions

## Problem / Opportunity
`context_compass/system_docs/src_architecture.md` is 5,645 lines (415,505 bytes). Its authoring instructions ask
for a re-entry-safe C4 document built on a 17-section contract and reject component-level deep dives in it. Most of
its length is history and component detail rather than architecture:
- `## Context / Handoff Summary` is 646 lines, a dated change log back to 2026-07-25; the Handoff Rule asks for a
  concise summary of what changed, what remains unknown and where the next reader should start.
- `## Operational Invariants` (1,350 lines) and `## Failure Modes and Error Paths` (629 lines) carry
  release-by-release history, chat quotes, ticket ids and timings inside their entries.
- `## C1 Code Map (Core Only)` (1,153 lines) carries per-version change notes beside its five contract fields.

The owner asked (chat, 2026-10-24): bring it to spec, clean out old change-log detail and keep the recent entries,
remove what the src_architecture instructions do not call for, aim at about 1,000 lines fewer if that is right, and
move component material to src_components where it belongs. His first message of the session also asked that
src_components be brought to its own spec where it is not.
EVIDENCE:
- context_compass/system_docs/src_architecture_index.md:26-91
- context_compass/agent_onboarding/default/design_engineer/skills/src_architecture_instructions.md:114-133
- context_compass/agent_onboarding/default/design_engineer/skills/src_architecture_instructions.md:350-366

## MRP Alignment (Most Reasonable Product)
The document is read whole at every engineer onboarding and ships in the wheel as the packaged architecture
hardcopy. Every line of history is paid for by every reader on every re-entry, while the history itself already
lives in git and the release notes. The core to get right is the C4 content: boundaries, sequences, the rules in
force and the failure behaviour of today, each still evidenced. Component mechanics belong one level down in
src_components, where the reading hierarchy sends a reader who needs them.

## Ticket Contract
- ENTRY_GATE: an attention_board row routes to the active story; the Content Preservation baseline is captured
  immediately before the first edit; melder_0 (F5) and melder_1 (many-child turn-in) have landed their writes to
  both documents, or an order has been agreed with them through the mailbox.
- EXECUTION_BOUNDARY: `context_compass/system_docs/src_architecture.md`, `src_components.md` and their indexes, and
  the asset rebuilds a system_docs change requires. No change to `src/`, tests, `__version__` or the release note
  (a context_compass-only change takes no notch). No change to the authoring instructions or other policy.
- DEPENDENCIES: TASK-2026-10-24-cache_file_write_failure_fails_meld (melder_0; its F5 writes both documents);
  STORY-2026-10-24-remove_many_child_holder_ownership (melder_1; its turn-in merges a patch into both).
- EXIT_GATE: Story 1 accepted with the Quality Gate passed, the preservation gate accounted, the rubric scored, both
  indexes and both asset rebuilds `--check` OK; Story 2 accepted or deferred by the owner; board and artifact sync.
- FAILURE_ESCALATION: DECISION_REQUEST when a cut would remove a rule in force or an owner ruling; CONFLICT when
  another lane writes the same sections; BLOCKER when a gate cannot pass.

## Goals (Outcomes)
- src_architecture passes its Quality Gate, the portability rule included.
- About 1,000 lines fewer, from history removed and component mechanics moved, with no rule in force lost.
- Material that moves lands in src_components to its entry contract, and is not duplicated there.
- The recent change-log entries stay; older ones are left to git and the release notes.

## Non-Goals (Explicit Exclusions)
- No change to Melder source, tests, version or release note.
- No new behaviour claims: condensing removes history and duplication, it does not restate what a rule says.
- No change to the authoring instructions or any other policy document.
- No edit of src_graph (generated).

## Scope Boundaries
- In scope: src_architecture and src_components with their indexes; this epic's tickets; the boards; the rebuild.
- Out of scope: tests_architecture and tests_components (pending set of another lane), README, `docs/`.

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: melder_3 certified by the owner, who set the scope in chat on 2026-10-24; the audit runs
  read-only while the two other lanes finish their writes to the same documents.

## Success Metrics
- src_architecture line count: about 1,000 lower, or the reason it is not recorded.
- Zero unaccounted lines in the Content Preservation Gate.
- The portability and absolute-path checks return nothing.
- Rubric score (src_architecture profile) recorded before and after.

## Requirements (Functional + Non-Functional)
- Baseline multiset of non-blank lines captured immediately before the first edit.
- Every removed line accounted for: kept, moved to a named src_components section, or history left to git (named
  revision) and the release notes.
- Each document's index regenerated in the same pass as its edit; `--check` OK.
- The asset runner and the llm_support builder, then both `--check`, on Python 3.14, as the last step.

## Constraints / Assumptions
- Shared files: re-read before each write; never overwrite another agent's change.
- Device VM: read-only git with `GIT_OPTIONAL_LOCKS=0`; load Python 3.14 per command; `TMPDIR` under /tmp.
- Approval loop (synaptic overlay): the owner's 2026-10-24 instruction confirms this scope; anything beyond it
  goes back to him first.

## Dependencies / External References
- TASK-2026-10-24-cache_file_write_failure_fails_meld (melder_0)
- STORY-2026-10-24-remove_many_child_holder_ownership (melder_1)

## Milestones (Track Progress)
- [ ] Milestone 1: audit - section and entry dispositions recorded in Story 1 Notes.
- [ ] Milestone 2: apply - the other lanes' writes landed, edits applied, gates pass.
- [ ] Milestone 3: rebuild - both builders `--check` OK; Story 1 closed.
- [ ] Milestone 4: src_components - Story 2 done or deferred by the owner.

## Stories (Required to Complete)
- [ ] Story: STORY-2026-10-24-src_architecture_trim_to_spec - audit, trim, migrate, re-index, gates, rebuild.
- [ ] Story: src_components to its own spec - planned; created when Story 1 closes (owner's first message).

## Tasks (Cross-Cutting or Epic-Level)
- [ ] Task: Agree the write order with melder_0 and melder_1 through the mailbox.
- [ ] Task: Complete story STORY-2026-10-24-src_architecture_trim_to_spec.
- [ ] Task: Verify Ticket Microcycle enforcement across active tickets/stories/tasks.

## Acceptance Criteria (Epic Done)
- Story 1 accepted: 17 contract sections in order, portability clean, about 1,000 lines lighter or the reason
  recorded, preservation gate accounted, rubric recorded, indexes and rebuilds `--check` OK.
- Story 2 accepted, or deferred by the owner.

## Risks / Mitigations
- Concurrent writers to the same documents -> apply after they land; NOTICEs; re-read before every write.
- Silent content loss -> preservation gate before and after; moved text carried verbatim.
- A rule in force removed with its history -> remove history clauses only; uncertain text stays; owner rulings are
  kept or raised as DECISION_REQUEST.
- Stale ranges -> indexes regenerated in the same pass and checked.
- Stale packaged hardcopy -> asset rebuild last.

## Applicable Anti-Patterns
- [ ] No epic-state transition without story-level evidence.
- [ ] No closure while required stories are incomplete or unaccepted.
- [ ] No program claims without source evidence from story/task notes.

## Validation / Test Approach
- `index_document.py --check` on both documents; the two portability searches; heading-order check against the
  contract; preservation multiset diff over the document and its migration targets; rubric score; the asset runner
  and llm_support builder with `--check`.

## Rollout / Adoption Plan
- A mailbox NOTICE to the active agents naming where new invariants, failure modes and handoff lines go after the
  trim, so later lanes do not regrow the history.

## Open Questions
- Where "recent" starts in the handoff log: proposed as the release-note boundary (release_docs/0.2.8227.md ends
  at 0.2.8227; the running note starts at 0.2.8228); the owner may move the line.

## Decision Log
- 2026-10-24: owner scope (chat): trim to spec, keep the recent change log, about 1,000 lines, move component
  material to src_components.
- 2026-10-24: owner (chat): the next session on this lane onboards as design_engineer.

## Artifact Links (Optional)
Qualified independent reviewer acceptance and direct closure follow shared `ticketing.md`;
this does not make independent review mandatory for every ticket.

- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - artifacts/src_architecture_to_spec_20261024/
- DISPOSITION: delete_on_close
- CLEANUP_TRIGGER: Story 1 closure, after the preservation gate is accounted

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS:
- CONTEXT_TOPICS:
- IF_UNKNOWN: none

## Contribution Attribution
- Ticket/Work Author(s): melder_3 (synaptic_python_developer); prose; revision 1 of this epic.
- Published By: UNKNOWN before publication (local files; the owner commits).
- Independent Review: none requested.

## Notes
- DATETIME: 2026-10-24T20:58:00Z
  AUTHOR: melder_3
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: PLAN
  CLAIM: One active story does the work: audit and dispositions first, read-only, then the edits once melder_0's
    F5 and melder_1's turn-in have landed their writes to both documents, then gates and the rebuild. The
    src_components conformance pass is a second story, created when the first closes.
  EVIDENCE:
  - context_compass/attention_board.md:110-111
  - context_compass/tickets/tasks/2026-10-24_cache_file_write_failure_fails_meld_task.md:79-80
  IMPACT: editing now would collide with two lanes writing the same sections; the audit does not need to wait.
  NEXT: send melder_0 and melder_1 a NOTICE asking them to report when their writes to both documents land.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

## Closure Confirmation
- [ ] Work walkthrough shared with user
- [ ] Criteria, required tests/reviews and delegated acceptance or reserved-owner disposition recorded
- [ ] Applicable anti-pattern checks are clear or escalated with evidence.

## Noting Behavior
- Note focus: program-level direction, cross-story tradeoffs, and tranche order.
- Add notes when priorities, sequencing, or scope boundaries change.
- Reference story/task evidence instead of duplicating tactical execution logs.
- Keep notes append-only and preserve UNKNOWN-first promotion discipline.
- Multiple meaningful comments may hold evidence directly; no forced body copy before ordinary
  continuation. Current scope/state/decisions/handoff stay coherent at material transitions.

## Context / Handoff Summary
Scope: src_architecture brought to its authoring spec and about 1,000 lines lighter (Story 1), then src_components
to its own spec (Story 2, planned). State: in_progress, melder_3; Story 1 audits read-only. Hold: no edit to either
document until melder_0's F5 and melder_1's turn-in land, or an order is agreed. Owner direction: the next session
on this lane onboards as design_engineer. Next: NOTICEs to melder_0 and melder_1; the audit in Story 1.

## Project-Specific Additions
<!-- BEGIN USER-DEFINED: project_fields -->
<!-- END USER-DEFINED: project_fields -->

<!--
Anything this project needs on every ticket of this kind goes in the region
above: extra fields, a compliance checklist, a link to a local convention.

The region is yours. An upgrade replaces every other line of this template with
the new version's text and carries this region across untouched, so a local
addition here is not a divergence you re-resolve on every upgrade - which is
what editing the rest of the template would cost you.
-->
