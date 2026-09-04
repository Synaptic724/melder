# Task: Prepare the ordered disposal implementation contract

## Metadata
- Task ID: TASK-2026-09-04-ordered-disposal-patch-contract
- Story: STORY-2026-09-04-ordered-disposal-binding
- Story Ticket: `tickets/stories/2026-09-04_ordered_disposal_binding_story.md`
- Epic Ticket: `tickets/epics/2026-09-02_ordered_live_spell_disposal_epic.md`
- Status: ready
- Owner: codex
- Agent Name: codex_1
- Priority: p1
- Created: 2026-09-04T21:17:27Z
- Updated: 2026-09-04T21:17:27Z

## Objective
Turn the accepted phased design into the patch artifacts required for scoped source edits.
Preserve the owner decisions exactly; do not reopen settled questions or implement runtime code.

## Ticket Contract
- ENTRY_GATE: Complete ContextCompass re-entry, read current discovery sections, and route here.
- EXECUTION_BOUNDARY: Patch design artifacts, their generated indexes, ticket/artifact links,
  and evidence reads needed to define configuration, binding, runtime, and replay contracts.
- DEPENDENCIES: `tickets/tasks/2026-09-02_ordered_spell_disposal_contract_discovery_task.md`.
- EXIT_GATE: Required patch artifacts exist, are indexed/linked, and map each change to a
  child implementation task and verification. No product edit occurs in this task.
- FAILURE_ESCALATION: Record technical unknowns in the affected later task; do not substitute
  private-mutation defenses, a new DI family, or an unrelated architecture redesign.

## Scope Boundaries
- In scope: one patch lane named `ordered_disposal_priority_2026_09_04`.
- Out of scope: executing the later implementation tasks, commits, pushes, publication.

## State Transition Event
- from_state: draft
- to_state: ready
- transition_reason: Owner requested concrete tasks and durable post-compaction instructions.

## Required Reading and Evidence
- Discovery current design: `tickets/tasks/2026-09-02_ordered_spell_disposal_contract_discovery_task.md`,
  sections Phase 1 Design, Configuration Change Map, Evidence, Context / Handoff Summary.
- `agent_onboarding/default/engineer/skills/patch_framework_gating.md`
- `agent_onboarding/default/engineer/skills/patch_artifact_consumption.md`
- Before authoring, read the design instructions:
  `agent_onboarding/default/design_engineer/skills/patch_framework_design.md`.
  `agent_onboarding/default/design_engineer/skills/architecture_patch_contracts.md`.
  `agent_onboarding/default/design_engineer/skills/component_patch_contracts.md`.
  `agent_onboarding/default/design_engineer/skills/code_description_patch_contracts.md`.
- Navigation: verified `system_docs/src_components_index.md`, relevant configuration/binding,
  Creations, and Crystallizer slices; verify graph indexes before using their ranges.
- Source anchors:
  `src/melder/aether/spellbook/bind/bind.py:310-633`
  `src/melder/aether/spellbook/spell.py:287-497`
  `src/melder/aether/conduit/creations/creations.py:197-354`
  `src/melder/crystallizer/crystals/spell_crystal.py:143-339`

## Accepted Contract to Carry Forward
- Store a LIST; combine both input groups once at Spell creation.
- `enforce_priority_disposal_methods=False` by default: Spell names, then book names.
- True: matching book names first in configuration order, then remaining Spell names.
- First occurrence wins for duplicate names; missing profile methods are skipped.
- Empty Spell input leaves book methods applicable; keep class-profile-only matching.
- Bind's SHA includes the resolved ordered values. Do not move matching to conjure or remove
  disposal names from the fingerprint. No post-creation mutation protocol is requested.
- Spell owns the final list. Runtime consumers use it directly; real serialized/hash value
  boundaries must be distinguished from defensive live-list snapshots.
- Preserve cleanup failure posture and lifetime routing. No new getter/probe/lock system.

## Steps / Checklist
- [ ] Read patch-authoring policy and current design; avoid superseded historical proposals.
- [ ] Create architecture and component contracts for producers, runtime, and persistence.
- [ ] Add the code-description contract for order composition, list ownership, and replay joins.
- [ ] Describe pre-bind False availability, setup/freeze behavior, and reload backfill reporting.
- [ ] Map changes and evidence to the eight downstream tasks; keep unresolved graft host policy
      explicit in the replay task rather than silently deciding it.
- [ ] Generate indexes, link actual artifacts, and add artifact-board rows after files exist.
- [ ] Append evidence and the next step before switching to configuration implementation.

## Deliverables
Planned outputs, not existing artifacts yet, under
`system_docs/patches/active/ordered_disposal_priority_2026_09_04/`:
- `architecture_patch.md`
- `component_patch_configuration_binding.md`
- `component_patch_runtime_disposal.md`
- `component_patch_crystallizer_replay.md`
- `code_description_patch_disposal_flow.md`
- Corresponding generated indexes.

## Files / Paths Impacted
- The planned patch directory, this task/story/epic, attention_board.md, artifact_board.md.
- No production source changes.

## Validation
- Not run; ticket created only.
- Validate links, heading/index structure, scope/task mapping, and absence of contradictory
  tuple/default-True/override-only instructions in current patch contracts.

## Risks / Rollback Notes
Historical discovery notes include rejected designs. Read current named sections first.
Remove or revise only this task's newly authored drafts if the scope needs correction.

## Applicable Anti-Patterns
- [ ] No fabricated source verification or full-file read claims.
- [ ] No implementation before patch artifacts exist and consumption mapping is recorded.

## Done Checklist
- [ ] Patch contracts and indexes exist; source claims carry evidence.
- [ ] Tickets and artifact board link the actual outputs and disposition.
- [ ] Handoff states the exact next task and any remaining unknowns.
- [ ] Owner accepts closure; do not close unrelated discovery/review tickets.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: false during ticket creation; register planned outputs when created.
- ARTIFACT_PATHS: none yet
- DISPOSITION: promote_to_documentation
- CLEANUP_TRIGGER: merge durable deltas and remove temporary patch docs at accepted closure

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS: none
- CONTEXT_TOPICS: accepted contract, patch gates, task coverage
- IF_UNKNOWN: none

## Noting Behavior
Append scoped evidence, decisions, and one NEXT action. Do not copy the whole discovery log.

## Notes
- DATETIME: 2026-09-04T21:17:27Z
  TYPE: PLAN
  CLAIM: This is the first executable task after the owner-requested ticket decomposition.
    The patch outputs listed above are planned and have not been created.
  EVIDENCE:
  - `context_compass/tickets/tasks/2026-09-02_ordered_spell_disposal_contract_discovery_task.md:140-320`
  IMPACT: Future source edits can consume a concise current contract instead of chat history.
  NEXT: Read patch_framework_design.md and the three authoring contracts, then author this lane.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
REONBOARD first after compaction. Open this task, read the discovery's current design/map,
then author the listed patch contracts. List storage and default False are settled. The
configuration setter spelling follows the existing fluent style; no runtime work is done.
Next task: `tickets/tasks/2026-09-04_disposal_priority_configuration_task.md`.

