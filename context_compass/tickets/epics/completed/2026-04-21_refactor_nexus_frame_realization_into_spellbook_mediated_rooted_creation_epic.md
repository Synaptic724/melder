# Epic: Refactor Nexus Frame Realization Into Spellbook-Mediated Rooted Creation
- Completed: 2026-04-22T11:14:18Z
- Summary: Closed during the 2026-04-22 rebaseline after the rooted Spellbook-mediated creation contract landed and its direct fallout was split, cleaned, and accepted into the new baseline.

## Metadata
- Epic ID: EPIC-2026-04-21-refactor-nexus-frame-realization-into-spellbook-mediated-rooted-creation
- Status: done
- Owner: codex
- Priority: p0
- Created: 2026-04-21T23:59:50Z
- Updated: 2026-04-22T11:14:18Z
- Target Window: 2026-Q2
- Related Program/Initiative: Nexus-managed frame creation and Rift/Nexus lifecycle correctness

## Problem / Opportunity
The current Nexus-managed frame authoring path is architecturally inverted.

Today the live `NexusFrameManager` flow can:
- ensure a frame directly through `Aether`
- bind configuration directly into the frame
- publish descriptor/ACL state
- only optionally bootstrap a root conduit afterward
- return the frame object itself

That breaks the runtime grammar the rest of the repo is built around:
- `Spellbook` is the normal frame-scoped creation surface
- `Spellbook.conjure(...)` is the normal root-conduit creation surface
- agents need a usable rooted workspace, not an empty frame shell
- the frame itself is not supposed to be the object passed around

The opportunity is to make Nexus-managed creation repo-native:
- create through `Spellbook`
- conjure a root conduit by default
- allow the agent/user to name that root conduit
- return the rooted conduit
- stop exposing frame-first empty-shell creation as the public Nexus-facing result

## MRP Alignment (Most Reasonable Product)
The MRP is not “Nexus can create frames.”
The MRP is “Nexus can create agent-usable rooted workspaces using the same
runtime grammar as the rest of Melder.”

If Nexus bypasses `Spellbook` and directly injects configuration into
`AethericFrame`, then the system has two contradictory creation models:
- the repo-native Spellbook/conjure path
- a Nexus-only frame-first shortcut

That is not a trustworthy foundation. The right MRP is one coherent creation
grammar where Nexus-managed creation is still Spellbook-mediated and yields a
usable rooted conduit immediately.

## Ticket Contract
- ENTRY_GATE: the current Nexus frame-authoring seams are understood well
  enough to state the contract break explicitly.
- EXECUTION_BOUNDARY: investigation, design, and implementation planning for
  Nexus/Rift-managed frame realization, Spellbook mediation, root-conduit
  defaults, and public return-shape corrections.
- DEPENDENCIES:
  - src/melder/aether/aether.py
  - src/melder/aether/aetheric_frame.py
  - src/melder/spellbook/spellbook.py
  - src/melder/aether/nexus/nexus.py
  - src/melder/aether/nexus/nexus_frame_manager.py
  - src/melder/aether/nexus/nexus_frame_configuration.py
  - src/melder/aether/nexus/nexus_frame_builder.py
  - tickets/tasks/2026-04-21_constrain_nexus_frame_manager_creation_by_mode_task.md
- EXIT_GATE: the program has an explicit, source-backed implementation plan and
  follow-on story/task slices that remove the frame-first empty-shell Nexus path.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if aligning Nexus creation to
  Spellbook mediation forces a wider public-API redesign than this epic should
  own alone.

## Goals (Outcomes)
- Replace frame-first Nexus realization with Spellbook-mediated creation.
- Require a root conduit by default for Nexus-facing creation.
- Let the caller explicitly name the root conduit.
- Stop returning a frame object from the Nexus-facing creation contract.
- Align Nexus-managed creation with the repo’s normal Spellbook/conjure grammar.

## Non-Goals (Explicit Exclusions)
- Auto-provisioning Nexus frames as a general policy.
- Rewriting unrelated RiftSpace or viewer behavior.
- Reopening the already-landed frame-link API lane.
- Mutating lower Melder frame semantics without evidence and explicit design decisions.

## Scope Boundaries
- In scope:
  - current Rift/Nexus frame creation flow
  - Nexus frame builder/configuration semantics
  - Spellbook-mediated realization requirements
  - root-conduit defaulting and naming
  - public return-shape contract for Nexus-facing creation
- Out of scope:
  - broad Aether lifecycle redesign beyond what this lane proves necessary
  - unrelated ACL or viewer work
  - CommandOps/product orchestration concerns

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: the current source is explicit enough to show the
  contract break, and the user has now given the corrected design direction in
  concrete terms.

## Success Metrics
- One canonical epic owns the Nexus/Rift/Spellbook creation-model correction.
- The contract break is described in source-backed terms instead of chat-only frustration.
- The follow-on implementation slices are explicit enough to execute without re-litigating the model.

## Requirements (Functional + Non-Functional)
- Functional:
  - Nexus-managed creation must go through `Spellbook`, not direct frame config injection alone.
  - Nexus-facing creation must yield a rooted conduit, not an empty frame shell.
  - The caller must have a way to name the root conduit.
  - Nexus-managed creation must stop returning the frame object as the public result.
  - The frame must still become available through the existing descriptor/ACL/publication flow after rooted creation.
- Non-functional:
  - preserve explicit creation; no hidden auto-provisioning
  - preserve deterministic cleanup and ownership boundaries
  - avoid introducing a second contradictory runtime grammar

## Constraints / Assumptions
- Current source evidence shows the lower runtime already allows frame-first existence via
  `Aether._ensure_frame(...)`, even though that is not the desired Nexus-facing contract.
- The current `NexusFrameManager` path is already the right place to correct the public
  Nexus-facing behavior without pretending the rest of the runtime already enforces the invariant.
- The caller should not need to hold or pass around the frame object to make the workspace usable.

## Dependencies / External References
- `src/melder/aether/aether.py`
- `src/melder/aether/aetheric_frame.py`
- `src/melder/spellbook/spellbook.py`
- `src/melder/aether/nexus/nexus.py`
- `src/melder/aether/nexus/nexus_frame_manager.py`

## Milestones (Track Progress)
- [x] Milestone 1: Document the current broken creation grammar and the corrected contract.
- [x] Milestone 2: Define the new Nexus-facing creation API/result shape and root-conduit naming model.
- [x] Milestone 3: Implement the Spellbook-mediated rooted creation flow.

## Stories (Required to Complete)
- [x] Story: STORY-2026-04-22-design-and-implement-rooted-spellbook-mediated-nexus-creation

## Tasks (Cross-Cutting or Epic-Level)
- [x] Task: verify the full current Rift/Nexus/Spellbook creation sequence from source
- [x] Task: define the root-conduit naming contract for caller-provided and default names
- [x] Task: define the public return-shape migration from frame to conduit
- [x] Task: Verify Ticket Microcycle enforcement across active tickets/stories/tasks.

## Acceptance Criteria (Epic Done)
- Nexus-facing frame creation no longer bypasses Spellbook mediation.
- Nexus-facing creation yields a rooted conduit by default.
- The root conduit can be named explicitly by the caller.
- The public Nexus-facing creation result is no longer the frame object.
- The new creation grammar is documented and validated clearly enough that agents can use it safely.

## Risks / Mitigations
- Risk: the lower runtime still tolerates conduitless frames, so the fix can
  drift into partial band-aids if the return shape and creation surface are not
  corrected together.
  Mitigation: treat Spellbook mediation + rooted conduit + return-shape change
  as one coherent contract, not separate optional improvements.
- Risk: caller naming of the root conduit can get lost in a “default root”
  shortcut.
  Mitigation: make root-conduit naming an explicit first-class requirement in
  the design story.

## Applicable Anti-Patterns
- [ ] No epic-state transition without story-level evidence.
- [ ] No closure while required stories are incomplete or unaccepted.
- [ ] No program claims without source evidence from story/task notes.

## Validation / Test Approach
- Discovery first: source-backed investigation of the current creation chain.
- Then focused unit/component/integration tests around:
  - Nexus-managed rooted creation
  - root-conduit naming
  - return shape
  - descriptor/publication state after Spellbook-mediated creation

## Rollout / Adoption Plan
- Lock the current broken contract in writing.
- Design the corrected rooted Spellbook-mediated path.
- Implement the new path behind the existing Nexus/Rift surfaces.
- Update architecture/components docs and frame-authoring tests in the same lane.

## Open Questions
- Should the default root-conduit name be fixed (`"root"`) or derived from caller/context?
- Do we keep a private frame-only internal primitive at all, or remove it completely from Nexus-managed creation?
- How should the new conduit-returning result interact with existing callers/tests that currently expect a frame?

## Decision Log
- 2026-04-21: The user explicitly set the contract direction:
  Nexus-facing creation must be Spellbook-mediated, root-conduit-first, caller-nameable,
  and should return the conduit rather than the frame.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: false
- ARTIFACT_PATHS:
  - none
- DISPOSITION: delete_on_close
- CLEANUP_TRIGGER: n/a

## Notes
- DATETIME: 2026-04-21T23:59:50Z
  TYPE: FACT
  CLAIM: The current Nexus-managed frame creation path is frame-first and
    Aether-mediated before it is Spellbook-mediated. `NexusFrameManager.create(...)`
    ensures the frame, binds configuration directly, publishes descriptor/ACL
    state, and only optionally bootstraps a root conduit afterward.
  EVIDENCE:
  - src/melder/aether/nexus/nexus_frame_manager.py:173-317
  - src/melder/aether/nexus/nexus_frame_manager.py:239-317
  IMPACT: The current public Nexus-facing creation grammar is architecturally
    inverted relative to the rest of the repo.
  NEXT: encode the corrected Spellbook-mediated rooted-creation contract at the
    epic level and stage the investigation story.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-21T23:59:50Z
  TYPE: FACT
  CLAIM: The lower runtime already allows frame-first existence before any
    conduit exists. `Aether._ensure_frame(...)` creates `AethericFrame`
    immediately, `AethericFrame.__init__` starts with an empty conduit map, and
    `Spellbook.__init__` ensures the frame before `Spellbook.conjure(...)`
    creates the conduit.
  EVIDENCE:
  - src/melder/aether/aether.py:376-420
  - src/melder/aether/aetheric_frame.py:42-98
  - src/melder/spellbook/spellbook.py:136-186
  - src/melder/spellbook/spellbook.py:3379-3473
  IMPACT: Fixing Nexus-facing creation is not just a `NexusFrameManager` tweak;
    it is a deliberate correction of the public creation contract against a
    lower runtime that still tolerates conduitless frame shells.
  NEXT: make the investigation story trace the entire current Rift/Nexus/Spellbook
    creation flow so the implementation lane can correct it coherently.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-21T23:59:50Z
  TYPE: DECISION
  CLAIM: The corrected Nexus-facing creation contract for this epic is:
    - do not bypass Spellbook
    - conjure a root conduit by default
    - let the caller name that root conduit
    - return the rooted conduit, not the frame
    - do not treat an empty frame shell as an acceptable public result
  EVIDENCE:
  - src/melder/aether/nexus/rift/rift.py:948-972
  - src/melder/aether/nexus/nexus.py:2052-2092
  - user_instruction: "the configuration should not bypass the spellbook"
  - user_instruction: "then conjure the conduit and then return the fucken conduit not the frame"
  IMPACT: The follow-on stories should optimize for a rooted usable workspace
    result instead of another frame-first authoring variant.
  NEXT: create the first investigation story for the full current Rift/Nexus
    creation process.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-22T10:41:57Z
  TYPE: DECISION
  CLAIM: The main implementation slice under this epic is complete. Nexus/Rift-facing
    managed creation is now Spellbook-mediated, rooted by default, root-conduit-nameable,
    and conduit-returning. The remaining direct downstream cleanup was split into a
    separate fallout epic so this epic no longer has to stay open as a vague catch-all.
  EVIDENCE:
  - tickets/tasks/2026-04-22_implement_rooted_spellbook_mediated_nexus_creation_task.md:1-217
  - tickets/epics/2026-04-22_cleanup_stale_fallout_from_rooted_nexus_creation_refactor_epic.md:1-152
  IMPACT: This epic can move to review state and stay focused on acceptance of the main
    rooted creation contract instead of mixing implementation completion with fallout triage.
  NEXT: review the landed epic scope against the implementation task and the spun-out
    fallout epic, then either accept this epic or open another explicit follow-on lane.
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
This epic exists to correct the current Nexus-managed frame creation grammar so
it becomes Spellbook-mediated, root-conduit-first, caller-nameable, and
conduit-returning instead of frame-first and optionally rooted. That main slice
is now implemented and validated, and the remaining direct downstream cleanup
has been isolated into the separate fallout epic rather than left implicit here.
