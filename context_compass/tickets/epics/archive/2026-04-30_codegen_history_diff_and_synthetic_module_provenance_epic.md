# Epic: Codegen History Diff And Synthetic Module Provenance

## Metadata
- Epic ID: EPIC-2026-04-30-codegen-history-diff-and-synthetic-module-provenance
- Status: in_progress
- Owner: codex
- Agent Name: codex_0
- Updated: 2026-05-02T23:48:49Z
- Priority: p0
- Created: 2026-04-30T00:00:00Z
- Updated: 2026-04-30T00:00:00Z
- Target Window: 2026-Q2
- Related Program/Initiative: Crystallizer software-truth and Rift/codegen retention model

## Problem / Opportunity
All codegen already lives in a `SyntheticModule`, but the current system does
not yet define a full retention policy for those modules or the objects they
produce. We need a clear model for:
- keeping a bounded recent history of synthetic modules
- dropping older transient codegens safely
- diffing workstation state across each codegen transaction
- tracking objects created by codegen so later save/pin actions are cheap
- classifying dependencies by source domain:
  - local space
  - site-library
  - codegen / synthetic

Without this, the system has no durable and explicit answer for:
- which codegen modules still matter
- which ones are only recent history
- what workstation state was actually changed by codegen
- what dependency closure must stay alive when a saved object or bind comes
  from synthetic code

## MRP Alignment (Most Reasonable Product)
The MRP is not a perfect universal provenance engine. The MRP is:
- bounded synthetic-module history
- explicit workstation diffing between codegens
- enough object/provenance tracking that later save/pin actions are cheap
- enough dependency classification that synthetic modules can be retained,
  activated, and eventually crystallized coherently

## Ticket Contract
- ENTRY_GATE: codegen already yields synthetic modules and the user explicitly
  approved designing bounded codegen history plus workstation diff retention.
- EXECUTION_BOUNDARY: define the epic-level architecture and retention model for:
  - codegen history
  - workstation diffs
  - codegen-created object tracking
  - synthetic-module dependency/provenance enrichment
- DEPENDENCIES:
  - `src/melder/crystallizer/synthetic_module.py`
  - Rift workstation and codegen runtime surfaces
  - current crystallizer design direction
- EXIT_GATE: the history, diff, retention, and dependency-classification model
  is explicit enough to stage implementation stories without guessing.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if the retention model proves to
  conflict with the current synthetic-module activation/bind direction.

## Goals (Outcomes)
- Define bounded synthetic-module history with ordered dropout.
- Define workstation diff capture around codegen transactions.
- Define what object-level tracking is worth keeping for later save/pin actions.
- Define how `SyntheticModule` should classify dependencies by source domain.
- Define the retention boundary between:
  - transient recent codegen history
  - pinned/retained synthetic modules
  - modules made durable by workstation or bind activity

## Non-Goals (Explicit Exclusions)
- Implement the whole subsystem in this epic.
- Finalize every possible persistence-table shape.
- Solve full restore/bootstrap semantics here.
- Solve every bind provenance detail for all object categories.

## Scope Boundaries
- In scope:
  - codegen history policy
  - workstation diff policy
  - codegen-created object tracking policy
  - dependency/provenance classification for synthetic modules
- Out of scope:
  - full implementation
  - broad product UX
  - unrelated Melder/CommandOps features

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: the user explicitly requested an epic capturing bounded
  codegen history, workstation diffs, object tracking, and dependency
  provenance for synthetic modules.

## Success Metrics
- The bounded history model is explicit and easy to implement.
- The workstation diff model is explicit and tied to codegen transactions.
- The object-tracking model is narrow enough to stay useful and not explode.
- `SyntheticModule` provenance/dependency classes are explicit enough to guide
  activation, retention, and later crystallization behavior.

## Requirements (Functional + Non-Functional)
- Functional:
  - define ordered history with dropout
  - define pin/retain conditions
  - define workstation diff snapshots and comparisons
  - define tracking hooks for codegen-created objects
  - define source-domain dependency classes for synthetic modules
- Non-functional:
  - bounded memory growth
  - explicit state transitions
  - no hidden retention magic
  - no reliance on guessing when a direct transaction diff can answer it

## Constraints / Assumptions
- All codegen already lives in a `SyntheticModule`.
- Not all synthetic modules are activated.
- Objects created by codegen may later be saved or bound, so tracking their
  provenance early can make later decisions cheap.
- Workstation diffs are likely a better retention signal than post-hoc
  speculation.
- Bounded history should prefer simple ordered-drop semantics first.

## Dependencies / External References
- Current crystallizer direction
- Rift workstation surface
- Codegen transaction model

## Milestones (Track Progress)
- [ ] Milestone 1: define bounded synthetic-module history and dropout policy
- [ ] Milestone 2: define workstation diff and object-tracking policy
- [ ] Milestone 3: define synthetic-module dependency/provenance classes

## Stories (Required to Complete)
- [ ] Story: define bounded codegen history and pinned-module retention policy
- [ ] Story: define workstation diff capture across codegen transactions
- [ ] Story: define codegen-created object provenance tracking policy
- [ ] Story: define synthetic-module dependency and source-domain classification

## Tasks (Cross-Cutting or Epic-Level)
- [ ] Task: define `OrderedDict`-style recent module history semantics
- [ ] Task: define dropout/eviction policy for non-pinned module history
- [ ] Task: define workstation before/after diff payload shape
- [ ] Task: define object-tracking payload shape for codegen-created objects
- [ ] Task: define local/site-library/synthetic dependency categories

## Acceptance Criteria (Epic Done)
- Recent history, dropout, and pinning are explicit.
- Workstation diff semantics are explicit.
- Object tracking for later save/pin actions is explicit.
- Synthetic-module dependency classes are explicit.
- The direction is concrete enough to stage implementation tasks.

## Risks / Mitigations
- Risk: object tracking becomes too broad and noisy.
  Mitigation: keep the first design focused on tracking what later save/pin
  actions actually need.
- Risk: retention rules become magical and hard to reason about.
  Mitigation: keep the state machine explicit and bounded.
- Risk: dependency classification becomes too vague.
  Mitigation: define source-domain classes directly in the epic.

## Applicable Anti-Patterns
- [ ] No epic-state transition without evidence-backed scope.
- [ ] No hidden retention heuristics when transaction diffs can answer the question.
- [ ] No unbounded synthetic-module history.

## Validation / Test Approach
- Design-only in this epic.
- Validation is coherence of the retention model and readiness for
  implementation slicing.

## Rollout / Adoption Plan
- First define the retention and diff model.
- Then stage implementation slices in Rift/workstation/codegen/crystallizer.
- Then validate the behavior against real codegen usage.

## Open Questions
- What exact conditions pin a synthetic module versus leaving it in recent history?
- How far should object tracking go before it becomes noise?
- What dependency closure should be retained automatically when a tracked object
  is later saved or bound?

## Decision Log
- 2026-04-30T00:00:00Z: Opened this epic to capture bounded codegen history,
  workstation diff retention, object tracking, and synthetic-module dependency
  provenance as one coherent design lane.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: false
- ARTIFACT_PATHS:
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: none

## Notes
- DATETIME: 2026-04-30T00:00:00Z
  TYPE: FACT
  CLAIM: The user wants one epic that covers both the bounded synthetic-module
    history idea and the workstation diff/object-tracking idea, with dependency
    provenance on `SyntheticModule` rich enough to distinguish local,
    site-library, and codegen/synthetic origins.
  EVIDENCE:
  - user_instruction: "make an epic to describe both the idea of a diff, and the orderedict idea with dropout"
  - user_instruction: "we want to track objects that are created by codegen just because if an agent does want to save it we can easily do that"
  - user_instruction: "each synthetic module probably needs features to detect all the dependencies it has if it comes from site-library or from local space or codegen"
  IMPACT: The next design lane is not just module activation. It is the full
    retention/provenance model around codegen outputs and workstation effects.
  NEXT: use this epic to stage the implementation stories rather than treating
    module history and workstation diffs as separate ad hoc ideas.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Closure Confirmation
- [ ] Work walkthrough shared with user
- [ ] Acceptance criteria confirmed by user
- [ ] Applicable anti-pattern checks are clear or escalated with evidence.

## Noting Behavior
- Note focus: program-level direction, cross-story tradeoffs, and retention semantics.
- Add notes when history, diff, or provenance rules change.
- Keep notes append-only and preserve UNKNOWN-first promotion discipline.

## Context / Handoff Summary
This epic owns the design of bounded codegen history, workstation diffs,
codegen-created object tracking, and synthetic-module dependency/provenance
classification.
