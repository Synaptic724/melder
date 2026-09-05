# Task: Prepare the ordered disposal implementation contract

## Metadata
- Task ID: TASK-2026-09-04-ordered-disposal-patch-contract
- Story: STORY-2026-09-04-ordered-disposal-binding
- Story Ticket: `tickets/stories/completed/2026-09-04_ordered_disposal_binding_story.md`
- Epic Ticket: `tickets/epics/completed/2026-09-02_ordered_live_spell_disposal_epic.md`
- Status: done
- Completed: 2026-09-05T14:22:02Z
- Summary: Established and consumed phase contracts; durable decisions promoted to canonical documentation.
- Owner: codex
- Agent Name: codex_1
- Priority: p1
- Created: 2026-09-04T21:17:27Z
- Updated: 2026-09-05T14:22:02Z

## Objective
Turn the accepted phased design into the patch artifacts required for scoped source edits.
Preserve the owner decisions exactly; do not reopen settled questions or implement runtime code.

## Ticket Contract
- ENTRY_GATE: Complete ContextCompass re-entry, read current discovery sections, and route here.
- EXECUTION_BOUNDARY: Patch design artifacts, their generated indexes, ticket/artifact links,
  and evidence reads needed to define configuration, binding, runtime, and replay contracts.
- DEPENDENCIES: `tickets/tasks/completed/2026-09-02_ordered_spell_disposal_contract_discovery_task.md`.
- EXIT_GATE: Required patch artifacts exist, are indexed/linked, and map each change to a
  child implementation task and verification. No product edit occurs in this task.
- FAILURE_ESCALATION: Record technical unknowns in the affected later task; do not substitute
  private-mutation defenses, a new DI family, or an unrelated architecture redesign.

## Scope Boundaries
- In scope: one patch lane named `ordered_disposal_priority_2026_09_04`.
- Out of scope: executing the later implementation tasks, commits, pushes, publication.

## State Transition Event
- from_state: in_progress
- to_state: done
- transition_reason: Owner accepted delivery and requested this closure; completed at 2026-09-05T14:22:02Z.

## Required Reading and Evidence
- Discovery current design: `tickets/tasks/completed/2026-09-02_ordered_spell_disposal_contract_discovery_task.md`,
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
- [x] Read patch-authoring policy and current design; avoid superseded historical proposals.
- [x] Create architecture and component contracts for producers, runtime, and persistence.
- [x] Add the code-description contract for order composition, list ownership, and replay joins.
- [x] Describe pre-bind False availability, setup/freeze behavior, and reload backfill reporting.
- [x] Map changes and evidence to the eight downstream tasks; keep unresolved graft host policy
      explicit in the replay task rather than silently deciding it.
- [x] Generate indexes, link actual artifacts, and add artifact-board rows after files exist.
- [x] Append evidence and the next step before switching to configuration implementation.

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
- [x] No fabricated source verification or full-file read claims.
- [x] No implementation before patch artifacts exist and consumption mapping is recorded.

## Done Checklist
- [x] Patch contracts and indexes exist; source claims carry evidence.
- [x] Tickets and artifact board link the actual outputs and disposition.
- [x] Handoff states the exact next task and any remaining unknowns.
- [x] Owner accepts closure; do not close unrelated discovery/review tickets.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: false (closed)
- ARTIFACT_PATHS: none active
- DISPOSITION: promote_to_documentation
- CLEANUP_TRIGGER: owner-accepted closure 2026-09-05T14:22:02Z
- Durable contracts: source architecture/components, source docstrings, README, configuration guide,
  and committed regression tests. Temporary patches/probes/validation scratch are removed at closure.
- Historical artifact citations in Notes are retained; tracked patches are recoverable from Git history.

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
  - `context_compass/tickets/tasks/completed/2026-09-02_ordered_spell_disposal_contract_discovery_task.md:140-320`
  IMPACT: Future source edits can consume a concise current contract instead of chat history.
  NEXT: Read patch_framework_design.md and the three authoring contracts, then author this lane.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-04T21:49:58Z
  TYPE: PLAN
  CLAIM: Certification renewed as codex_1. The owner requested a holistic read of the epic's
    components and change contacts before implementation. This pass covers producers,
    compiler/cache propagation, runtime disposal/transfer, configuration transport, and
    active/staged/graft replay. It does not authorize implementing those later phases.
  EVIDENCE:
  - Owner direction in the active conversation, 2026-09-04
  - `context_compass/tickets/epics/completed/2026-09-02_ordered_live_spell_disposal_epic.md:115-180`
  - `context_compass/tickets/tasks/completed/2026-09-04_disposal_priority_configuration_task.md:14-36`
  IMPACT: The small configuration change must satisfy the later consumers without moving
    matching to disposal time, reviving tuple/snapshot proposals, or changing scope.
  NEXT: Read verified component sections, then inspect the relevant complete source methods.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-04T21:51:57Z
  TYPE: FACT
  CLAIM: Component sections map three separate responsibilities: configuration/binding
    establish policy and identity, compiled creation routes disposal metadata into the
    lifetime-owned registry, and Crystallizer records/replays the established values.
    Nexus-managed books use the ordinary Spellbook construction path. Method order within
    an object is distinct from reverse object-creation order and inter-scope cleanup order.
  EVIDENCE:
  - `context_compass/system_docs/src_components.md:339-603`
  - `context_compass/system_docs/src_components.md:705-794`
  - `context_compass/system_docs/src_components.md:2021-2144`
  - `context_compass/system_docs/src_components.md:2294-2783`
  - `context_compass/system_docs/src_components.md:1027-1267`
  - `context_compass/system_docs/src_components.md:4902-4961`
  - `context_compass/system_docs/src_components.md:7575-7767`
  - `context_compass/system_docs/src_components.md:7939-8007`
  IMPACT: These are navigation/design findings, not renewed source-behavior proofs. The
    component index matches 8,394 lines and its hash; the graph index matches 25,706 lines
    and its hash. Source methods must settle which transforms need edits versus retention.
  NEXT: Trace producer initialization/matching/hash, then compiler, runtime, and replay seams.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-04T21:54:14Z
  TYPE: FACT
  CLAIM: Producer source confirms that supplied configurations are adopted without default
    loading/validation, while ordinary new books load defaults. Configuration starts empty;
    optional defaults appear at validation. set_property enforces registration and lifecycle,
    while type validation is later. Both bind paths latch the first candidate collection as
    a book-wide frozenset. Bind matches class-profile names, fingerprints the matched values,
    then constructs Spell, which freezes them again. Conjure only checks type/flag consistency.
  EVIDENCE:
  - `src/melder/aether/spellbook/configuration/spellbook_configuration.py:114-160`
  - `src/melder/aether/spellbook/configuration/spellbook_configuration.py:202-256`
  - `src/melder/aether/spellbook/configuration/spellbook_configuration.py:398-481`
  - `src/melder/aether/spellbook/configuration/spellbook_configuration.py:559-652`
  - `src/melder/aether/spellbook/spellbook.py:5423-5475`
  - `src/melder/aether/spellbook/spellbook.py:4754-4961`
  - `src/melder/aether/spellbook/spellbook.py:5030-5295`
  - `src/melder/aether/spellbook/bind/bind.py:310-485`
  - `src/melder/aether/spellbook/bind/bind.py:534-631`
  - `src/melder/aether/spellbook/spell.py:287-497`
  - `src/melder/aether/spellbook/spell_compiler/spell_examiner/strategies/binding_profile_strategy.py:70-132`
  - `src/melder/aether/spellbook/spellbook.py:6547-6561`
  IMPACT: Configuration must supply the priority default before bind. Eager default state
    must stay writable during assembly and must not disappear from missing-record backfill
    reporting. Later producer work removes the shared candidate latch, matches both groups
    once, and hashes exactly the resolved order before the Spell reaches any runtime consumer.
    Generic reload documentation overstates immediate type checking; invalid types currently
    fail at final validation. Do not silently change that unrelated behavior.
  NEXT: Trace compiler metadata/signature/namespace handoffs into lifetime-specific registration.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-04T21:57:25Z
  TYPE: FACT
  CLAIM: Compiler source contact classification is recorded in the compiler task: actual
    live-value copies differ from direct-reference executor arrays and schema/hash values.
    Solo and generalized registration preserve lifetime-specific stores; the new priority
    flag belongs upstream, not inside these generated disposal registration paths.
  EVIDENCE:
  - `context_compass/tickets/tasks/completed/2026-09-04_ordered_disposal_compiler_propagation_task.md`
  - `src/melder/aether/spellbook/spell_compiler/codegen_planner/data/spell_generalized_codegen_lane_plan.py:2625-2670`
  - `src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/generalized/compilers/generalized_no_overrides_codegen_creation_compiler.py:1500-1583`
  IMPACT: No new runtime configuration reads, locks, or lifetime routing changes are needed
    for this ordering feature. Runtime verification remains a later task, not a read claim.
  NEXT: Read Creations registration, cleanup, and extraction/restoration plus its direct caller.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-04T21:58:36Z
  TYPE: FACT
  CLAIM: Runtime source tracing confirms the ordering fix belongs in metadata propagation,
    not the cleanup algorithm. The Creations task records the six copy sites and lifetime
    safety constraint; the direct Conduit caller and subclass delegation need no new policy.
  EVIDENCE:
  - `context_compass/tickets/tasks/completed/2026-09-04_ordered_disposal_creations_task.md`
  - `src/melder/aether/conduit/creations/creations.py:148-262`
  - `src/melder/aether/conduit/creations/creations.py:502-614`
  IMPACT: Preserve two-registry separation and genuine detach-before-dispose operations.
    No extra method-presence probing, configuration reads, or locks are part of this feature.
  NEXT: Trace configuration carriers and SpellCrystal through active/staged restore and graft.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-04T22:01:28Z
  TYPE: FACT
  CLAIM: Configuration transport and resolved-list replay are distinct paths, now source
    traced and recorded in their own tasks. Generic carriers and Nexus defaults need tests,
    while SpellCrystal sorting and three inactive forwarding gaps require later source edits.
    Recorded SHA joins make same-policy order preservation a replay requirement.
  EVIDENCE:
  - `context_compass/tickets/tasks/completed/2026-09-04_disposal_configuration_roundtrip_task.md`
  - `context_compass/tickets/tasks/completed/2026-09-04_ordered_disposal_crystal_replay_task.md`
  - `src/melder/crystallizer/crystal_loader_system/restore_engine.py:1734-2095`
  - `src/melder/crystallizer/crystal_loader_system/graft_runner.py:371-554`
  IMPACT: The initial configuration task supplies schema/default/fluent/reload behavior only.
    No actual cleanup ordering or replay completion can be claimed from that first slice.
    The epic's later tasks retain their explicit dependencies and verification obligations.
  NEXT: Finish the validation/documentation contact map and summarize the complete dependency chain.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-04T22:04:01Z
  TYPE: FACT
  CLAIM: Holistic component/source information gathering is complete across producers,
    compiler metadata, Creations, configuration carriers, Nexus construction, and replay.
    Test and asset contacts are recorded in their tasks. Existing direct-store order tests
    need upstream integration coverage; workflows check committed outputs and do not rebuild
    them automatically. No product files or generated assets were modified.
  EVIDENCE:
  - `context_compass/tickets/tasks/completed/2026-09-04_ordered_disposal_compiler_propagation_task.md`
  - `context_compass/tickets/tasks/completed/2026-09-04_ordered_disposal_creations_task.md`
  - `context_compass/tickets/tasks/completed/2026-09-04_disposal_configuration_roundtrip_task.md`
  - `context_compass/tickets/tasks/completed/2026-09-04_ordered_disposal_crystal_replay_task.md`
  - `context_compass/tickets/tasks/completed/2026-09-04_ordered_disposal_docs_assets_task.md`
  - `context_compass/tickets/tasks/completed/2026-09-04_ordered_disposal_end_to_end_validation_task.md`
  IMPACT: The configuration slice is informed by the full dependency chain. This is not
    whole-file review of every large compiler/Spellbook/restore module, runtime validation,
    or completion of the patch-artifact task. Its artifact checklist remains open.
  NEXT: Write the scoped patch contracts from this evidence, then implement only the selected
    configuration task; leave Bind/Spell/runtime/replay implementation to their own tasks.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-04T22:08:04Z
  TYPE: MEASURE
  CLAIM: Reference validation checked 109 source/test/workflow ranges across 42 files in
    the seven updated child tasks: all files exist and every range is in bounds. Two newly
    written workflow end ranges were corrected before the final pass. Scoped diff checking
    reported no whitespace errors. No pytest, cache-rehydration, or replay execution occurred.
  EVIDENCE:
  - `context_compass/tickets/epics/completed/2026-09-02_ordered_live_spell_disposal_epic.md:166-203`
  - PowerShell reference/count check and git diff --check output, 2026-09-04T22:08:04Z
  IMPACT: Durable reading pointers are usable; structural validation does not establish
    runtime behavior. Source notes distinguish inspected methods/blocks from whole-file reads.
  NEXT: Prepare patch artifacts, then implement the selected configuration slice with its tests.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-04T22:24:50Z
  TYPE: DECISION
  CLAIM: Owner selected configuration-only implementation. The architecture patch is scoped
    to that slice, with one configuration component contract and a default/reload control-flow
    contract. Six files (three contracts and their generated indexes) are linked and consumed.
    The former combined configuration/binding filename is replaced by a single-component
    filename, following the authoring contract. Later component contracts remain pending.
  EVIDENCE:
  - `system_docs/patches/active/ordered_disposal_priority_2026_09_04/architecture_patch.md:3-16`
  - `system_docs/patches/active/ordered_disposal_priority_2026_09_04/component_patch_spellbook_configuration.md:1-45`
  - `system_docs/patches/active/ordered_disposal_priority_2026_09_04/code_description_patch_spellbook_configuration.md:1-38`
  - `context_compass/agent_onboarding/default/design_engineer/skills/component_patch_contracts.md:25-30`
  IMPACT: The configuration entry gate is satisfied without declaring the full epic's patch
    program complete. No later component may implement from this configuration-only contract.
  NEXT: Execute disposal_priority_configuration; extend the patch before the later source phases.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-05T14:22:02Z
  TYPE: DECISION
  CLAIM: Owner accepted this deliverable and requested closure of the ordered-disposal program.
    Established and consumed phase contracts; durable decisions promoted to canonical documentation.
  EVIDENCE: tickets/tasks/completed/2026-09-04_ordered_disposal_end_to_end_validation_task.md
  IMPACT: Ticket history is retained under completed. Registered temporary artifacts are disposed
    at accepted closure; durable behavior is in canonical docs, examples, source, and regression tests.
    Linux/hosted checks and unrelated recording/name-lookup findings retain their documented scope.
  NEXT: none; this work item is closed.
  REREAD: HELPFUL
  SCORE_0_TO_10: 10

## Context / Handoff Summary
CLOSED: 2026-09-05T14:22:02Z. Established and consumed phase contracts; durable decisions promoted to canonical documentation.
Program record: tickets/epics/completed/2026-09-02_ordered_live_spell_disposal_epic.md
No active work remains in this ticket. Prior handoff text below is historical.

### Historical handoff at closure
REONBOARD first after compaction. Holistic reading is complete and recorded in this task,
the epic's Holistic Change Map, and the compiler/Creations/transport/replay/assets/validation
child notes. Use those current findings alongside the discovery's design. Author the scoped
patch contracts before each later component. The configuration gate is complete and its
successor task is implemented/in review with 115 focused tests. List storage and default
False are settled; no runtime ordering or replay implementation has been performed.
Next task: `tickets/tasks/completed/2026-09-04_disposal_priority_configuration_task.md`.
