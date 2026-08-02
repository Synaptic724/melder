# Epic: Migrate Frame Posture Ownership Into AethericFrame
- Completed: 2026-05-16T15:47:45Z
- Summary: Closed after moving frame posture ownership into AethericFrame, relocating bind lifecycle to the frame, removing test/runtime compat shims, and validating the full suite (8181 passed).


## Metadata
- Epic ID: EPIC-2026-05-16-migrate-frame-posture-ownership-into-aetheric-frame
- Status: done
- Owner: codex
- Agent Name: codex_0
- Priority: p0
- Created: 2026-05-16T13:30:44Z
- Updated: 2026-05-16T15:47:45Z
- Target Window: 2026-Q2
- Related Program/Initiative: Runtime configuration ownership correction

## Problem / Opportunity
The current runtime still has mixed authority for frame posture. We agreed that
frame posture must be owned by `AethericFrameConfiguration` and live on
`AethericFrame`, while `SpellbookConfiguration` must stay a local rich config
only. The current code drifted by:

- embedding frame posture back into `SpellbookConfiguration`
- making `Spellbook` derive frame posture instead of only consuming it
- letting `Conduit` synthesize frame posture from rich config

That is the wrong owner model for this repo and it is what needs to be fixed.

## MRP Alignment (Most Reasonable Product)
The MRP is not â€œfinish the whole config system in one pass.â€ The MRP is:

- remove frame posture fields from `SpellbookConfiguration`
- make `AethericFrameConfiguration` the only owner of frame posture
- move runtime readers to that owner
- then add the real frame-owned lifecycle methods in bounded slices

That gets the owner boundary right first before any wider cleanup.

## Ticket Contract
- ENTRY_GATE: the user explicitly restated the correct owner model and asked
  for a fresh epic with explicit steps instead of more half-migrated changes.
- EXECUTION_BOUNDARY: owner-boundary migration only; no broad unrelated runtime
  redesign and no attempt to finish every config concern in one pass.
- DEPENDENCIES:
  - `src/melder/aether/aetheric_frame.py`
  - `src/melder/aether/aetheric_frame_configuration.py`
  - `src/melder/spellbook/configuration/spellbook_configuration.py`
  - `src/melder/spellbook/spellbook.py`
  - `src/melder/spellbook/spellbook_creation_system.py`
  - `src/melder/aether/conduit/conduit.py`
  - focused tests under `tests/unit`, `tests/component`, and `tests/integration`
- EXIT_GATE: frame posture ownership is fully in `AethericFrame` /
  `AethericFrameConfiguration`, the rich config is local-only, and the steps
  are complete story-by-story with acceptance.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` only if one of the current
  runtime readers proves that a field we thought was frame-global is actually
  local-only or vice versa.

## Goals (Outcomes)
- Remove frame posture from `SpellbookConfiguration`.
- Make `AethericFrameConfiguration` the only frame posture owner.
- Give `AethericFrame` the real lifecycle for that config.
- Make `Spellbook` only consume frame-owned posture.
- Make `Conduit` consume real frame posture instead of synthesizing it.

## Non-Goals (Explicit Exclusions)
- Reworking override-local behavior in the same pass.
- Reworking hooks into a separate subsystem.
- Solving every shared rich-config policy question before the owner split is done.
- Cleaning every prior drifted ticket in this pass.

## Scope Boundaries
- In scope:
  - frame-posture field migration
  - frame-owned lifecycle methods
  - direct runtime reader reroutes
  - focused validation and cleanup of old-owner tests
- Out of scope:
  - unrelated AR/Nexus redesign
  - new product-facing config APIs beyond what the owner model requires

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: the current lane drifted, the user explicitly asked for a
  reset epic with staged work, and the correct owner split is now explicit.

## Success Metrics
- `SpellbookConfiguration` no longer owns frame posture.
- `AethericFrameConfiguration` is the sole posture owner.
- `AethericFrame` owns posture lifecycle.
- runtime readers stop synthesizing posture from rich config.

## Requirements (Functional + Non-Functional)
- Functional:
  - move `system_state`, `ai_native_enabled`, `rift_enabled`, and
    `shared_framewide_spellbook_configuration` into frame posture only
  - remove the corresponding rich-config ownership paths
  - add frame-owned default/init/freeze semantics
  - reroute runtime reads to the frame-owned posture
- Non-functional:
  - no backward-compat shims
  - no mixed source-of-truth paths left behind
  - bounded story/task slices only

## Constraints / Assumptions
- `overrides_enabled` remains Spellbook-local.
- the default user path still matters:
  - spawn spellbook
  - bind
  - conjure
  - meld
- shared rich `SpellbookConfiguration` can be handled later, but only after the
  owner split is clean.

## Dependencies / External References
- `codex/context_compass/system_docs/src_architecture.md`
- `codex/context_compass/system_docs/src_components.md`
- `codex/context_compass/tickets/epics/2026-05-16_explicit_aetheric_frame_configuration_and_spellbook_local_config_epic.md`

## Milestones (Track Progress)
- [ ] Milestone 1: remove frame posture from `SpellbookConfiguration`
- [ ] Milestone 2: make `AethericFrame` own posture lifecycle
- [ ] Milestone 3: reroute remaining runtime readers to the frame owner
- [ ] Milestone 4: validate and clean test ownership expectations

## Stories (Required to Complete)
- [ ] Story: STORY-2026-05-16-remove-frame-posture-from-spellbook-configuration - strip frame posture out of the rich local config and reroute direct readers
- [ ] Story: STORY-2026-05-16-add-aetheric-frame-owned-configuration-lifecycle - add frame-owned default/configure/freeze semantics
- [ ] Story: STORY-2026-05-16-consume-frame-owned-posture-in-spellbook-and-conduit - make Spellbook and Conduit consume the frame owner only
- [ ] Story: STORY-2026-05-16-validate-frame-posture-owner-migration - update and run focused tests for the final owner model

## Tasks (Cross-Cutting or Epic-Level)
- [ ] Task: finish one slice at a time; do not carry half-migrated owner paths across slices
- [ ] Task: keep Ticket Microcycle notes current before each new slice
- [ ] Task: verify no direct `get_property("system_state" | "ai_native_enabled" | "rift_enabled")` calls remain in runtime after Milestone 3

## Acceptance Criteria (Epic Done)
- `SpellbookConfiguration` is local-only.
- `AethericFrameConfiguration` is frame-owned and canonical.
- `AethericFrame` owns the lifecycle of frame posture.
- `Spellbook` and `Conduit` stop synthesizing frame posture from rich config.

## Risks / Mitigations
- Risk: half-migrated source-of-truth paths reappear.
  Mitigation: finish one owner slice fully before the next.
- Risk: tests keep asserting old ownership.
  Mitigation: move those assertions to frame-config tests as part of each slice.

## Applicable Anti-Patterns
- [ ] No epic-state transition without a clean owner model.
- [ ] No mixed posture ownership between frame config and rich config.
- [ ] No â€œtemporaryâ€ fallback paths left behind.

## Validation / Test Approach
- Focused unit/component/integration rings per slice.
- No repo-wide sweep required until the final owner move is stable.

## Rollout / Adoption Plan
1. Strip frame posture from `SpellbookConfiguration`.
2. Add frame-owned lifecycle methods.
3. Move runtime readers.
4. Revisit shared rich-config policy only after the owner model is clean.

## Open Questions
- Exact frame method names for default/configure/freeze.
- Whether the first frame-owned lifecycle slice should freeze during conjure only or allow explicit pre-conjure finalization too.

## Decision Log
- 2026-05-16T13:30:44Z: Reset the lane into explicit slices after drift.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: false
- ARTIFACT_PATHS:
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: none

## Notes
- DATETIME: 2026-05-16T13:30:44Z
  TYPE: DECISION
  CLAIM: The lane must stop trying to â€œfinish the modelâ€ in one pass. The only
    safe next step is to remove frame posture from `SpellbookConfiguration`
    first, because every later lifecycle or sharing decision is cleaner once
    the owner boundary is correct.
  EVIDENCE:
  - user_instruction: "just move the fucken variables out of spellbook configuration"
  - user_instruction: "keep SpellbookConfiguration as the local rich config only"
  IMPACT: The first active task under this epic is the posture-field removal and
    direct-reader reroute, not the full frame lifecycle.
  NEXT: open the first task and route the board to it.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Closure Confirmation
- [ ] Work walkthrough shared with user
- [ ] Acceptance criteria confirmed by user
- [ ] Applicable anti-pattern checks are clear or escalated with evidence.

## Noting Behavior
- Note focus: program-level owner boundaries, slice order, and stop conditions.
- Add notes when owner decisions or slice order change.
- Keep notes append-only and preserve UNKNOWN-first promotion discipline.

## Context / Handoff Summary
This epic replaces the drifted all-at-once config work with explicit owner-model
slices.

