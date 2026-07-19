# Epic: Implement Crystallizer Configuration And Activation

## Metadata
- Epic ID: EPIC-2026-05-04-implement-crystallizer-configuration-and-activation
- Status: in_progress
- Owner: codex
- Agent Name: codex_0
- Priority: p0
- Created: 2026-05-04T22:18:15Z
- Updated: 2026-05-04T22:18:15Z
- Target Window: 2026-Q2
- Related Program/Initiative: Crystallizer runtime ownership and loader policy foundation

## Problem / Opportunity
The crystallizer package now has meaningful `SpellCrystal` and
`SyntheticModule` objects, but the facade/configuration side is still empty.
That leaves an important policy seam in the wrong place:
- `SpellCrystal` currently accepts `user_source_root_paths` directly
- there is no singleton crystallizer root like `Nexus`
- there is no central activation gate proving crystallizer configuration was
  explicitly configured, validated, and frozen before live use

## MRP Alignment (Most Reasonable Product)
The MRP is not "all crystallizer behavior." The MRP is the first honest
ownership and policy root:
- configuration owns crystallizer policy inputs
- crystallizer owns activation/configured state
- lower-level objects stop pretending they own config policy directly

## Ticket Contract
- ENTRY_GATE: the user explicitly redirected `user_source_root_paths` out of
  `SpellCrystal` constructor ownership and requested a singleton/root pattern
  modeled after Spellbook configuration and Nexus activation.
- EXECUTION_BOUNDARY: configuration/root activation slice only:
  - `src/melder/crystallizer/configuration/`
  - `src/melder/crystallizer/crystallizer.py`
  - light interface/wiring updates needed by that slice
- DEPENDENCIES:
  - `src/melder/spellbook/configuration/configuration.py`
  - `src/melder/aether/nexus/configuration/nexus_configuration.py`
  - `src/melder/aether/nexus/nexus.py`
  - existing crystallizer artifact stack
- EXIT_GATE: crystallizer has one real configuration object, one singleton
  root, explicit configured/activated gates, and a clear path for future
  policy migration out of low-level constructors.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if the config/root slice forces
  a larger redesign of crystal/module identity than this tranche can safely own.

## Goals (Outcomes)
- Define `CrystallizerConfiguration`.
- Define its fluent API and freeze/finalize behavior.
- Move `user_source_root_paths` into crystallizer configuration as the first
  real policy field.
- Define singleton `Crystallizer` activation/configured state.
- Make future loader/crystal construction pull policy from crystallizer-owned
  config rather than passing raw roots around ad hoc.

## Non-Goals (Explicit Exclusions)
- Full loader implementation.
- Full persistence adapter implementation.
- Full crystal/module identity redesign.
- Immediate refactor of every crystallizer callsite.

## Scope Boundaries
- In scope:
  - crystallizer config
  - singleton facade/root
  - configured/activated state checks
  - initial policy field migration
- Out of scope:
  - broad crystallizer behavior implementation
  - package manager or persistence runtime
  - mutation semantics

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: the user explicitly requested the first configuration and
  singleton activation slice as the next crystallizer foundation.

## Success Metrics
- One accepted crystallizer configuration/root lane exists.
- Config policy has an explicit home.
- The singleton activation gate is real and testable.

## Requirements (Functional + Non-Functional)
- Functional:
  - typed property bag
  - validation
  - freeze/finalize
  - fluent `with_*` API
  - singleton root
  - configured and activated checks
- Non-functional:
  - thread-safe
  - explicit failure semantics
  - no hidden global mutation after activation
  - matches repo configuration style

## Constraints / Assumptions
- `user_source_root_paths` is crystallizer policy, not spell identity.
- Crystallizer config should follow the repo's mutable-then-freeze pattern.
- Crystallizer singleton behavior should look more like Nexus than Spellbook.

## Dependencies / External References
- `src/melder/spellbook/configuration/configuration.py`
- `src/melder/aether/nexus/configuration/nexus_configuration.py`
- `src/melder/aether/nexus/nexus.py`
- crystallizer philosophy artifact stack

## Milestones (Track Progress)
- [ ] Milestone 1: configuration class exists and validates
- [ ] Milestone 2: singleton root exists with configured/activated gates
- [ ] Milestone 3: first policy field migration path is explicit

## Stories (Required to Complete)
- [ ] Story: implement `CrystallizerConfiguration`
- [ ] Story: implement singleton `Crystallizer` activation root

## Tasks (Cross-Cutting or Epic-Level)
- [ ] Task: stage the first implementation slice in code
- [ ] Task: verify activation/configuration behavior with focused tests
- [ ] Task: Verify Ticket Microcycle enforcement across active tickets/stories/tasks.

## Acceptance Criteria (Epic Done)
- `CrystallizerConfiguration` exists with a real fluent config contract.
- `Crystallizer` exists as a singleton root with explicit configured and
  activated gates.
- The user-source-root policy has a real home outside the crystal constructor.

## Risks / Mitigations
- Risk: config leaks back down into low-level objects ad hoc.
  Mitigation: keep config ownership explicit at the root/facade layer.
- Risk: singleton state becomes magical.
  Mitigation: require explicit activation and validation/freeze.

## Applicable Anti-Patterns
- [ ] No epic-state transition without story-level evidence.
- [ ] No closure while required stories are incomplete or unaccepted.
- [ ] No program claims without source evidence from story/task notes.

## Validation / Test Approach
- Focused unit validation for configuration and root activation behavior.

## Rollout / Adoption Plan
- Implement the config/root slice first.
- Then migrate lower-level crystallizer callers to consume root-owned policy.

## Open Questions
- Should future crystal construction pull a prebuilt classification context
  from Crystallizer rather than raw root paths directly?
- Should activation and configuration installation be separate verbs or one
  merged operation?

## Decision Log
- 2026-05-04T22:18:15Z: Opened to stage the first crystallizer
  configuration/root ownership slice after the user rejected keeping source
  root policy in `SpellCrystal.__init__`.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: false
- ARTIFACT_PATHS:
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: none

## Notes
- DATETIME: 2026-05-04T22:18:15Z
  TYPE: PLAN
  CLAIM: The next crystallizer foundation slice is configuration and root
    activation, not more low-level crystal growth. `user_source_root_paths`
    needs a real policy home, and the singleton/freeze/activate pattern should
    be modeled after the existing repo configuration systems rather than left
    implicit.
  EVIDENCE:
  - user_instruction: "move this user defined root path into the configuration as its first configurable"
  - user_instruction: "make a CrystallizerConfiguration class"
  - user_instruction: "build the crystallzier class and make it a singleton like the nexus class"
  IMPACT: The next implementation pass should establish explicit crystallizer
    ownership and policy state before widening the loader.
  NEXT: implement the config/root slice in code and validate it directly.
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
This epic owns the first crystallizer configuration/root slice: config home for
policy, singleton root ownership, and explicit activation semantics.
