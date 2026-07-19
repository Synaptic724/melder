# Epic: Live Creation Visibility Probe For Static Access
- Completed: 2026-04-09T21:59:36Z
- Summary: Completed the live-creation probe epic by landing the canonical no-create query primitive and tests.


## Metadata
- Epic ID: EPIC-2026-04-09-live-creation-visibility-probe-for-static-access
- Status: done
- Owner: codex
- Priority: p1
- Created: 2026-04-09T00:09:30Z
- Updated: 2026-04-09T21:59:36Z
- Target Window: 2026-Q2
- Related Program/Initiative: Rift static-access backend primitives

## Problem / Opportunity
Static access mode needs one reliable way to answer:
- "is this target already live right now?"

That answer must not:
- create anything
- fork a second resolution model from `meld(...)`
- bypass the real existence and scope semantics already owned by Melder

The current runtime already has the right ingredients:
- `Meld` owns spell resolution semantics
- `Creations` owns live object storage
- `SpellSpace` adds spellspace-specific scope
- `Conduit` is the natural public facade

What is missing is one first-class no-create query primitive that mirrors meld
lookup semantics and reports whether a live creation already exists.

## MRP Alignment (Most Reasonable Product)
The reasonable product is not a broad static-access layer yet. It is one small,
correct primitive:
- `Meld` owns the real live-creation lookup
- `Conduit` facades it
- static-access code can build on that later

## Ticket Contract
- ENTRY_GATE: the user explicitly wants the first static-mode backend
  primitive but requested investigation and planning first, not immediate code edits.
- EXECUTION_BOUNDARY: define and later implement only the no-create live
  creation visibility probe on `Meld` plus a `Conduit` facade.
- DEPENDENCIES:
  - tickets/artifacts/2026-04-08_rift_access_modes_static_capability_dynamic_model.md
  - src/melder/aether/conduit/meld/meld.py
  - src/melder/aether/conduit/conduit.py
  - src/melder/aether/conduit/creations/creations.py
  - src/melder/aether/conduit/spell_space/spell_space.py
  - src/melder/utilities/interfaces/interfaces.py
  - tickets/stories/2026-04-09_design_and_stage_live_creation_visibility_probe_story.md
  - tickets/artifacts/2026-04-09_live_creation_visibility_probe_design.md
- EXIT_GATE: the design and later implementation define one canonical live
  creation query path that reuses meld lookup semantics and does not create.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if existence-scope semantics are
  too divergent for one single probe to cover cleanly.

## Goals (Outcomes)
- Reuse `Meld` spell lookup semantics for a no-create query.
- Surface one public `Conduit` facade.
- Keep creation storage ownership in `Creations`.
- Avoid push-based publication or hot-path hooks in Meld/cleanup.

## Non-Goals (Explicit Exclusions)
- Full static mode implementation.
- Capability mode implementation.
- ACL redesign.
- Any hot-path publication hooks in `Meld` or cleanup/GC paths.

## Scope Boundaries
- In scope:
  - live creation visibility query
  - `Meld` ownership of the real logic
  - `Conduit` facade
  - focused unit tests
- Out of scope:
  - full endpoint layer
  - viewer changes
  - static-handle return mechanics

## State Transition Event
- from_state: draft
- to_state: draft
- transition_reason: created to preserve the live-creation probe as its own
  implementation lane after investigation completed.

## Success Metrics
- One accepted ownership decision: `Meld` owns, `Conduit` facades.
- One accepted query contract that does not create.
- One accepted plan for how existence scopes are handled.

## Requirements (Functional + Non-Functional)
- Functional:
  - resolve the spell exactly the way `meld(...)` would
  - inspect live object state without creating
  - return a simple bool facade and preserve room for richer status later
- Non-functional:
  - no hot-path tax on meld
  - no second lookup model
  - no fake "static" conduit tricks

## Constraints / Assumptions
- `Meld` already owns the correct lookup semantics.
- `Creations` is the storage backend, not the public API owner.
- static mode later can build on this primitive.

## Dependencies / External References
- Rift access-mode artifact for the static/capability/dynamic split.

## Milestones (Track Progress)
- [ ] Milestone 1: Lock the design and implementation plan
- [ ] Milestone 2: Implement the `Meld` primitive and `Conduit` facade

## Stories (Required to Complete)
- [ ] Story: STORY-2026-04-09-design-and-stage-live-creation-visibility-probe

## Tasks (Cross-Cutting or Epic-Level)
- [ ] Task: execute the first implementation task for the probe
- [ ] Task: Verify Ticket Microcycle enforcement across active tickets/stories/tasks.

## Acceptance Criteria (Epic Done)
- The runtime has one canonical no-create live-creation query path and focused
  tests proving it.

## Risks / Mitigations
- Risk: existence-scope edge cases are more complex than a bool-only API can express.
  Mitigation: keep the public first cut bool-shaped, but design the internal
  ownership so richer status can be added later.

## Applicable Anti-Patterns
- [ ] No epic-state transition without story-level evidence.
- [ ] No closure while required stories are incomplete or unaccepted.
- [ ] No program claims without source evidence from story/task notes.

## Validation / Test Approach
- Focus on unit tests around `Meld`, `Conduit`, and creation-scope behavior.

## Rollout / Adoption Plan
- First land the probe.
- Later wire static mode to consume it.

## Open Questions
- Which existence scopes should be supported in the first cut?
- Should the public API stay bool-only or expose a richer status summary immediately?

## Decision Log
- Created after investigation confirmed that `Meld` is the correct owner for a
  no-create live-creation query.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - tickets/artifacts/2026-04-09_live_creation_visibility_probe_design.md
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: keep until the probe is implemented and the resulting
  contract is merged into canonical docs or intentionally retired.

## Notes
- DATETIME: 2026-04-09T00:09:30Z
  TYPE: FACT
  CLAIM: Deep investigation confirmed that `Meld` should own the new no-create
    probe and `Conduit` should only facade it. `Creations` is the correct live
    storage backend but not the correct public API owner because it does not
    know spell-resolution semantics, contracted-vs-owned lookups, or scope
    resolution rules.
  EVIDENCE:
  - src/melder/aether/conduit/meld/meld.py:32-55
  - src/melder/aether/conduit/meld/meld.py:297-366
  - src/melder/aether/conduit/creations/creations.py:27-33
  - src/melder/aether/conduit/creations/creations.py:392-491
  - src/melder/aether/conduit/spell_space/spell_space.py:7-23
  - src/melder/aether/conduit/conduit.py:2476-2506
  IMPACT: The implementation path is now clear enough to stage properly rather
    than improvise from chat memory.
  NEXT: create the story/task/artifact for the probe and stop at planning.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Closure Confirmation
- [x] Work walkthrough shared with user
- [x] Acceptance criteria confirmed by user
- [x] Applicable anti-pattern checks are clear or escalated with evidence.

## Noting Behavior
- Note focus: program-level direction, cross-story tradeoffs, and tranche order.
- Add notes when priorities, sequencing, or scope boundaries change.
- Reference story/task evidence instead of duplicating tactical execution logs.
- Keep notes append-only and preserve UNKNOWN-first promotion discipline.

## Context / Handoff Summary
This epic isolates the live-creation visibility probe from the broader static
mode discussion. The core outcome is one no-create query primitive owned by
`Meld` and surfaced through `Conduit`.

