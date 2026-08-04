# Epic: AethericRift Discovery and Design Program
- Completed: 2026-05-16T16:41:00Z
- Summary: Closed at user direction as a retained historical discovery baseline
  for later AethericRift and Rift runtime lanes.

## Metadata
- Epic ID: EPIC-2026-02-18-aethericrift-discovery-design
- Status: done
- Owner: codex
- Priority: p0
- Created: 2026-02-18T23:35:36Z
- Updated: 2026-05-16T16:41:00Z
- Target Window: 2026-Q1
- Related Program/Initiative: AethericRift Foundations

## Problem / Opportunity
AethericRift direction exists across multiple historical tickets and working
artifacts, but decisions and open questions are split across files and are not
yet reduced to one discovery-first design track we can execute confidently.

## MRP Alignment (Most Reasonable Product)
The MRP is a stable, evidence-backed design baseline that locks core boundaries
(Rift vs Melder vs CommandOps), resolves key unknowns, and produces an
implementation-ready task map without premature code-level commitments.

## Ticket Contract
- ENTRY_GATE: all discovery sources are read and user confirms discovery-first lane
- EXECUTION_BOUNDARY: architecture discovery, decision synthesis, and ticketization only
- DEPENDENCIES: AethericRift docs/tickets + user interview + MutationResearch alignment
- EXIT_GATE: discovery story accepted and design decisions converted into execution tickets
- FAILURE_ESCALATION: raise DECISION_REQUEST for boundary conflicts and BLOCKER for missing source truth

## Goals (Outcomes)
- Produce one coherent AethericRift design baseline from current artifact set.
- Resolve boundary decisions and explicitly park unresolved UNKNOWNs.
- Define discovery-to-design handoff criteria before implementation starts.
- Produce follow-up story/task breakdown for phased implementation.

## Non-Goals (Explicit Exclusions)
- Implementing AethericRift runtime code in this epic.
- Locking API signatures or module-level code details.
- Rewriting historical artifacts for style-only consistency.

## Scope Boundaries
- In scope:
- discovery synthesis for AethericRift architecture, ACL model, execution model, and orchestration boundary
- user interview capture for unresolved design choices
- Out of scope:
- production implementation and test execution
- transport/auth wrapper implementation details

## State Transition Event
- from_state: draft
- to_state: ready
- transition_reason: user requested immediate discovery-and-design kickoff for AethericRift.

## Success Metrics
- Discovery story completed with interview-backed decisions.
- Top boundary decisions marked DECISION with evidence.
- Open questions reduced to a finite, prioritized list with owners/next actions.

## Requirements (Functional + Non-Functional)
- Consolidate AethericRift boundary and mode model from current sources.
- Preserve UNKNOWN-first discipline for unresolved claims.
- Keep design output implementable, testable, and ticketized.
- Ensure direct alignment with MutationResearch lane contract and control-plane gates.

## Constraints / Assumptions
- Existing source docs include drift and duplication.
- Design output must stay transport-agnostic at Rift boundary.
- CommandOps remains orchestration owner.

## Dependencies / External References
- AethericRift/aethericriftticket111.md
- AethericRift/aethericriftticket85.md
- AethericRift/systems/codegen_guardrails.md
- AethericRift/systems/interaction_modes.md
- MutationResearch/Ticket - Forward MutationResearch Philosophical Implementation Contract.md

## Milestones (Track Progress)
- [ ] Milestone 1: Discovery interview complete and unknowns triaged.
- [ ] Milestone 2: Design baseline approved and implementation stories drafted.

## Stories (Required to Complete)
- [ ] Story: STORY-2026-02-18-aethericrift-discovery - discovery synthesis and decision capture

## Tasks (Cross-Cutting or Epic-Level)
- [ ] Task: Complete story STORY-2026-02-18-aethericrift-discovery
- [ ] Task: Verify Ticket Microcycle enforcement across active tickets/stories/tasks.

## Acceptance Criteria (Epic Done)
- Discovery story is accepted with user-confirmed decisions.
- Core boundary, ACL, and execution model decisions are explicitly recorded.
- Remaining unknowns are isolated with follow-up tasks and ownership.

## Risks / Mitigations
- Risk: historical ticket drift creates contradictory assumptions.
- Mitigation: decision matrix with evidence pointers and explicit DECISION_REQUEST gates.
- Risk: scope creep into implementation before design closure.
- Mitigation: enforce design-review checkpoint before implementation lane.

## Applicable Anti-Patterns
- [ ] No epic-state transition without story-level evidence.
- [ ] No closure while required stories are incomplete or unaccepted.
- [ ] No program claims without source evidence from story/task notes.

## Validation / Test Approach
- Validate consistency across synthesized decisions and source documents.
- Validate acceptance through user interview confirmation and checkpoint approval.

## Rollout / Adoption Plan
- Use approved baseline to spawn implementation stories/tasks in controlled slices.
- Start with lowest-risk discovery-backed surfaces first.

## Open Questions
- Session model in static profile (explicit vs ephemeral).
- ObjectRef lifecycle defaults and release policy.
- Remote ACL as separate layer vs merged with object ACL.
- AST strictness and allowed codegen subset for v1 workspace control.
- Registration contract for method/object command exposure in codegen flows.

## Decision Log
- 2026-02-18: Discovery-first and design-first lane selected before implementation.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: false
- ARTIFACT_PATHS:
  - none
- DISPOSITION: delete_on_close
- CLEANUP_TRIGGER: n/a

## Notes
- DATETIME: 2026-02-18T23:35:36Z
  TYPE: FACT
  CLAIM: Current AethericRift direction emphasizes one CallSpec engine, ACL
    intersection, and command-orchestration separation from Rift execution.
  EVIDENCE:
  - AethericRift/aethericriftticket111.md:244-249
  - AethericRift/systems/acl_stack.md:15-25
  - AethericRift/systems/commandops_bridge.md:7-24
  IMPACT: Discovery must focus on locking boundaries and unresolved policy details
    before implementation tickets are decomposed.
  NEXT: Run structured interview task to resolve top unknowns.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-02-20T12:49:54Z
  TYPE: FACT
  CLAIM: Newest top-level ticket synthesis reinforces the same program baseline:
    one CallSpec path across static/workstation, ACL intersection as arbiter,
    and CommandOps-owned long-running orchestration.
  EVIDENCE:
  - AethericRift/TICKET111_DECISIONS.md:18-37
  - AethericRift/aethericriftticket111.md:244-249
  - AethericRift/aethericrift_ticket87.md:174-179
  - AethericRift/aethericriftticket85.md:182-186
  - AethericRift/tickets_aethericRift86-64-54-87.md:2155-2160
  IMPACT: Epic can move directly into default-policy closure and implementation
    decomposition without revisiting core boundary architecture.
  NEXT: finalize interview decisions for session defaults, ObjectRef lifecycle
    defaults, and remote ACL layering strategy.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-02-20T12:54:39Z
  TYPE: FACT
  CLAIM: MutationResearch folder confirms cross-lane contract fit with
    AethericRift boundaries, while signaling that significant mutation-governance
    details remain open and should stay explicitly unresolved for now.
  EVIDENCE:
  - MutationResearch/README.md:8-17
  - MutationResearch/WORKING_MODEL.md:3-4
  - MutationResearch/Ticket - Forward MutationResearch Philosophical Implementation Contract.md:257-267
  - MutationResearch/systems/open_questions.md:1-21
  IMPACT: Epic-level decomposition can proceed on settled boundaries and lane
    mechanics, but must keep unresolved mutation policy decisions as tracked
    UNKNOWN items.
  NEXT: complete AethericRift interview closure first, then run focused
    MutationResearch policy-closure decisions.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-02-20T13:19:19Z
  TYPE: FACT
  CLAIM: Program baseline now explicitly treats codegen (not REPL semantics) as
    the prime interaction path, enforced by manifest-bound AST and symbol/member
    validation before safe-vs-mutation routing.
  EVIDENCE:
  - utilized_ticket_artifacts/Ticket - Workstation Codegen Guardrails and Capability Manifest.md:27-33
  - AethericRift/systems/codegen_guardrails.md:11-12
  - AethericRift/systems/codegen_guardrails.md:45-56
  - MutationResearch/systems/codegen_bridge.md:4-4
  IMPACT: Epic decomposition must include interview closure on AST and
    registration-surface defaults before implementation slicing.
  NEXT: complete codegen-first interview set and convert answers into execution
    stories/tasks.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-02-20T13:32:45Z
  TYPE: DECISION
  CLAIM: Program-level target audience is agent execution; human-first REPL/CLI
    ergonomics are out-of-scope for v1 architecture closure.
  EVIDENCE:
  - utilized_ticket_artifacts/Ticket - Workstation Codegen Guardrails and Capability Manifest.md:27-33
  - AethericRift/systems/codegen_guardrails.md:7-12
  - MutationResearch/systems/codegen_bridge.md:28-29
  IMPACT: Epic decomposition should focus on agent-governed compile/exec,
    manifest validation, and machine-readable feedback contracts.
  NEXT: close interview defaults and split implementation stories accordingly.
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
Discovery/design epic now includes integrated findings from newest top-level
AethericRift tickets. Next step is interview-driven closure on unresolved
default-policy unknowns before implementation ticket decomposition.
