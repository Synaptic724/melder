# Epic: Explicit AST Metadata Rollout For Melder Classes

## Metadata
- Epic ID: EPIC-2026-04-07-explicit-ast-metadata-rollout-for-melder-classes
- Status: draft
- Owner: codex
- Priority: p1
- Created: 2026-04-07T11:48:01Z
- Updated: 2026-04-07T11:48:01Z
- Target Window: 2026-Q2
- Related Program/Initiative: Melder agent-facing class surface

## Problem / Opportunity
The viewer AST experiment proved there is real value in agent-facing class
surface introspection, but the current metadata contract is only explicitly set
on the current viewer/profile/helper experiment classes plus the top-level
system-doc objects. A broader Melder rollout still needs deliberate class-level
metadata coverage:
- `_ast_helper_access`
- `__agent_purpose__`

Without that, the shared AST helper cannot describe important concrete classes
predictably across the wider runtime.

## MRP Alignment (Most Reasonable Product)
If Melder is going to be an AI-native runtime, important classes need explicit,
LLM-readable purpose and access metadata at the class level. The MRP here is
not “AST on every object immediately”; it is a deliberate rollout plan so the
shared AST helper can operate predictably across the right runtime surfaces.

## Ticket Contract
- ENTRY_GATE: the current viewer AST experiment is accepted as the proving
  ground for the shared helper and the direct-class metadata contract.
- EXECUTION_BOUNDARY: discovery/design and later rollout planning for explicit
  class-level AST metadata only.
- DEPENDENCIES:
  - tickets/tasks/2026-04-06_implement_actionable_viewer_profile_tool_compositions.md
  - tickets/epics/2026-04-07_agent_exposable_class_surface_contract_discovery_epic.md
  - src/melder/utilities/helpers/class_surface_ast_describer.py
  - src/melder/utilities/general_base/cleanable.py
- EXIT_GATE: the epic defines the rollout order, class-selection rules,
  required metadata semantics, and acceptance criteria for later subsystem
  rollout stories/tasks.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if the rollout target set is too
  large or too ambiguous to stage safely.

## Goals (Outcomes)
- Define where `_ast_helper_access` must be explicit.
- Define where `__agent_purpose__` must be bespoke rather than generic.
- Define rollout order by subsystem.
- Define review criteria for good LLM-purpose strings.

## Non-Goals (Explicit Exclusions)
- Immediate repo-wide semantic rewrite.
- Mutation-system work.
- Replacing runtime docs with AST output.

## Scope Boundaries
- In scope:
  - explicit AST metadata rollout planning
  - subsystem prioritization
  - quality rules for `__agent_purpose__`
- Out of scope:
  - runtime feature work unrelated to AST metadata
  - broad codemod execution right now

## State Transition Event
- from_state: draft
- to_state: draft
- transition_reason: created as a future planning lane so the AST metadata
  rollout is not lost.

## Success Metrics
- One accepted rollout sequence by subsystem.
- One accepted minimum contract for class-level metadata.
- One accepted quality rubric for LLM-purpose strings.

## Requirements (Functional + Non-Functional)
- Functional:
  - identify target classes/subsystems
  - define required metadata fields
  - define private/public rules
- Non-functional:
  - avoid semantic drift
  - keep object purposes concise and high-signal
  - avoid noisy generic metadata spam

## Constraints / Assumptions
- Concrete class metadata is preferred over inherited semantic fallback.
- Private classes should still expose high-level purpose.
- Rollout should remain reviewable by subsystem.

## Dependencies / External References
- Viewer AST proving ground in the active viewer task.

## Milestones (Track Progress)
- [ ] Milestone 1: Define rollout rules and target classes
- [ ] Milestone 2: Stage subsystem stories/tasks for later execution

## Stories (Required to Complete)
- [ ] Story: STORY-TBD - AST metadata rollout rules and quality rubric
- [ ] Story: STORY-TBD - subsystem-by-subsystem rollout planning

## Tasks (Cross-Cutting or Epic-Level)
- [ ] Task: create the rollout-rules story when this lane is activated
- [ ] Task: create the first subsystem rollout task set when this lane is activated
- [ ] Task: Verify Ticket Microcycle enforcement across active tickets/stories/tasks.

## Acceptance Criteria (Epic Done)
- The rollout plan exists and is accepted.
- The target subsystems and metadata rules are explicit.

## Risks / Mitigations
- Risk: broad metadata rollout becomes noisy or low-signal.
  Mitigation: require subsystem staging and a quality rubric for purpose text.

## Applicable Anti-Patterns
- [ ] No epic-state transition without story-level evidence.
- [ ] No closure while required stories are incomplete or unaccepted.
- [ ] No program claims without source evidence from story/task notes.

## Validation / Test Approach
- Discovery validation only until the lane is activated.

## Rollout / Adoption Plan
- Defer until the lane is explicitly activated.

## Open Questions
- Which subsystems should be first?
- Which classes are truly important enough to justify bespoke purpose text?
- What is the minimum acceptable `__agent_purpose__` quality bar?

## Decision Log
- Created as a future rollout-planning epic after the viewer AST experiment
  proved useful.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: false
- ARTIFACT_PATHS:
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: n/a

## Notes
- DATETIME: 2026-04-07T11:48:01Z
  TYPE: PLAN
  CLAIM: We need a durable reminder that the AST metadata contract still
    requires a much wider Melder rollout. This epic exists to hold that future
    planning lane without polluting the active viewer task.
  EVIDENCE:
  - user_instruction: "add this to an EPIC so we remember to do this"
  IMPACT: The rollout will not be lost when we move off the current viewer lane.
  NEXT: leave this epic dormant until you explicitly activate the rollout work.
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
This is a future planning epic only. The current viewer AST experiment already
proved value; this epic exists to remember the later broader metadata rollout.
