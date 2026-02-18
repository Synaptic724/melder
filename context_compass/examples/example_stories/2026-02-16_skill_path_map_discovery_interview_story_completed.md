

Completed: 2026-02-17T11:57:04Z
Summary: Closed by explicit user directive to close all currently open tickets.

# Story: Skill Path Map Discovery Interview

## Metadata
- Story ID: STORY-2026-02-16-skill-path-map-discovery-interview
- Epic: EPIC-2026-02-16-skill-path-map-onboarding-state-machine-generalization
- Status: done
- Owner: codex
- Priority: p0
- Created: 2026-02-16T23:21:16Z
- Updated: 2026-02-17T11:57:04Z

## User Narrative
As the system owner, I want a structured discovery interview for onboarding
state-machine redesign, so that we can align on constraints before we
reorganize skills, careers, and path routing.

## Value / MRP Alignment
This story reduces redesign risk by converting broad intent into explicit,
approved requirements for state transitions, configuration authority, and
language-neutral skill-path routing.

## Ticket Contract
- ENTRY_GATE: active board row routes to this story.
- EXECUTION_BOUNDARY: discovery, requirements alignment, and decision capture
  for onboarding/state-machine redesign only.
- DEPENDENCIES: epic context, current onboarding policy docs, and user
  interview participation.
- EXIT_GATE: interview outputs captured, open questions ranked, and follow-on
  implementation tickets/stories/tasks defined.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` when requirements conflict or
  scope exceeds discovery boundaries.

## Requirements (Functional)
- Define initial onboarding state candidates and transition triggers.
- Define expected shape and ownership of `skill_path_map`.
- Define first-time onboarding vs returning-agent path behavior.
- Identify what must stay mandatory vs what can be configurable.
- Define folder-layer contract:
  `agent_onboarding/default/{general,engineer}` ->
  `agent_onboarding/user_defined/synaptic_python_developer`.

## Requirements (Non-Functional)
- Keep discovery outputs compact and evidence-backed.
- Preserve UNKNOWN-first discipline for unverified assumptions.
- Keep proposed model language-neutral and repository-agnostic.
- Keep `user_defined/synaptic_python_developer` committed in-repo as a public
  exemplar profile users can reuse.

## Scope Boundaries
- In scope:
- structured interview prompts and decision capture
- current-system gap inventory for onboarding model
- prioritization of follow-on design/implementation tasks
- Out of scope:
- full implementation of new onboarding architecture
- repo-wide migration execution in this story

## State Transition Event
- from_state: review
- to_state: done
- transition_reason: user requested closing all tickets as done.

## Dependencies / Related Work
- `tickets/epics/2026-02-16_skill_path_map_onboarding_state_machine_generalization_epic.md`
- `context_compass/AGENTS.MD`
- `context_compass/config/context_compass_config.yaml`

## Tasks (Implementation Checklist)
- [x] Task: TASK-2026-02-16-general-python-user-profile-split-contract -
      define folder split and profile precedence contract.
- [x] Task: TASK-2026-02-17-general-to-engineer-programming-skill-migration -
      relocate programming-oriented skills from general to engineer.
- [x] Task: TASK-2026-02-17-backlog-folder-migration-to-ticket-type-roots -
      relocate shared backlog root into lane-local backlog folders.
- [x] Task: TASK-2026-02-17-ticket-root-and-agent-default-structure-migration -
      move ticket lanes under `tickets/` and onboarding baseline under
      `agent_onboarding/default/`.
- [x] Task: TASK-2026-02-17-root-docs-profile-skill-folder-migration -
      move scoped root docs into profile skill folders, with `SKILLS.MD`
      explicitly carved out for separate handling.
- [x] Task: TASK-2026-02-17-profile-bias-partition-and-agents-bootstrap-decomposition -
      classify and map generic vs user-defined policy/rule content, then plan
      AGENTS bootstrap decomposition before migration.
- [x] Task: TASK-2026-02-16-skill-path-map-current-onboarding-map -
      map current onboarding states, gates, and transitions.
- [x] Task: TASK-2026-02-16-skill-path-map-schema-options -
      define `skill_path_map` schema options and tradeoffs.
- [x] Task: TASK-2026-02-16-skill-path-map-language-decoupling-analysis -
      identify Python-coupled assumptions and neutral alternatives.
- [x] Task: TASK-2026-02-16-skill-path-map-first-time-onboarding-flow -
      define first-time user onboarding path and default behavior.
- [x] Enforce Ticket Microcycle across all linked tasks.
- [x] Require meaningful-finding note updates during discovery/implementation.

## Acceptance Criteria
- Interview question set is completed with user answers captured.
- Required state-machine decisions are documented or explicitly UNKNOWN.
- Follow-on tasks are defined and prioritized for implementation planning.

## Validation / Test Plan
- Validate through user-review discussion and acceptance of captured decisions.
- Confirm every decision entry has evidence or UNKNOWN label.

## UX / API / Data Notes
- N/A for this discovery story; implementation details are deferred to child
  tasks.

## Risks / Mitigations
- Risk: discovery drift into implementation details.
  Mitigation: enforce discovery-only scope and spin out tasks for implementation.
- Risk: ambiguous ownership of config and policy precedence.
  Mitigation: capture explicit precedence decisions during interview.

## Applicable Anti-Patterns
- [x] No story-state transition without linked task-state evidence.
- [x] No closure while required tasks remain active or un-routed.
- [x] No cross-task synthesis claims without ticket-note evidence pointers.

## Open Questions
- Which onboarding states are mandatory for all repositories?
- Where should `skill_path_map` live and how should it be validated?
- What is the minimum first-time onboarding path for public users?
- How should career/skill paths be selected and overridden?

## Decision Log
- 2026-02-16: Story created to run structured interview before redesign.
- 2026-02-16: Keep `user_defined/synaptic_python_developer` in-repo (not
  gitignored) as a canonical public example profile.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: false
- ARTIFACT_PATHS:
  - artifacts/2026-02-16_skill_path_map_discovery_interview_notes.md
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: after implementation planning stories are accepted

## Notes
- DATETIME: 2026-02-16T23:21:16Z
  TYPE: PLAN
  CLAIM: This story will run a direct interview/discovery pass with the user to
    define state-machine and `skill_path_map` requirements before implementation.
  EVIDENCE:
  - tickets/epics/2026-02-16_skill_path_map_onboarding_state_machine_generalization_epic.md:1-40
  - context_compass/AGENTS.MD:8-34
  - context_compass/agent_onboarding/default/general/skills/workflow.md:23-40
  IMPACT: Redesign work can proceed with explicit constraints instead of
    assumption-driven architecture changes.
  NEXT: present interview prompts and capture user decisions in notes.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-02-16T23:31:33Z
  TYPE: DECISION
  CLAIM: The profile layering model will keep a committed
    `user_defined/synaptic_python_developer` profile in-repo so users can study
    and reuse a concrete advanced implementation example.
  EVIDENCE:
  - tickets/stories/2026-02-16_skill_path_map_discovery_interview_story.md:33-45
  - tickets/epics/2026-02-16_skill_path_map_onboarding_state_machine_generalization_epic.md:35-43
  IMPACT: We avoid hidden/local-only profile behavior and provide a clear
    reference implementation for public onboarding customization.
  NEXT: capture this as a hard requirement in the epic and define the first
    migration task for general/default split.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-02-16T23:32:11Z
  TYPE: PLAN
  CLAIM: First concrete child task is created to formalize the
    `general -> python_developer -> synaptic_python_developer` split contract
    and YAML default-profile behavior.
  EVIDENCE:
  - tickets/tasks/2026-02-16_general_python_user_profile_split_contract_task.md:1-42
  - tickets/stories/2026-02-16_skill_path_map_discovery_interview_story.md:63-75
  IMPACT: Discovery now has an executable work unit for contract-first
    organization before broader migration.
  NEXT: route active board row to the new task and begin current-tree mapping.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-02-16T23:45:25Z
  TYPE: DECISION
  CLAIM: Discovery lane naming is now `general + engineer + user_defined`
    (with `synaptic_python_developer` exemplar), and the first task is mapping
    reallocation candidates from current `general` into `engineer`.
  EVIDENCE:
  - tickets/tasks/2026-02-16_general_python_user_profile_split_contract_task.md:13-18
  - tickets/tasks/2026-02-16_general_python_user_profile_split_contract_task.md:49-52
  - attention_board.md:26-43
  IMPACT: Story execution is aligned to the new folder contract and ready for a
    matrix-style migration proposal.
  NEXT: review reallocation matrix with user and spin out migration tranche
    tasks.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-02-16T23:54:45Z
  TYPE: MEASURE
  CLAIM: skills-map and profile-map scaffold are implemented with config authority:
    `new` default first-time profile, `engineer` inheriting `general`, and
    committed `synaptic_python_developer` exemplar path.
  EVIDENCE:
  - skill_path_map/SKILLS.MD:1-40
  - config/context_compass_config.yaml:3-34
  - skill_path_map/default/engineer.md:1-12
  - skill_path_map/user_defined/synaptic_python_developer.md:1-2
  IMPACT: Story can now proceed to tranche-1 migration task planning with
    concrete skills-map semantics already in place.
  NEXT: confirm tranche-1 move set and start migration tasks.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-02-17T00:05:54Z
  TYPE: DECISION
  CLAIM: skills-map schema is finalized as `default/` + `user_defined/` map paths
    with strict path-only map content, and README files are designated as
    user-facing only (excluded from agent route-map reads).
  EVIDENCE:
  - config/context_compass_config.yaml:30-36
  - skill_path_map/SKILLS.MD:25-32
  - skill_path_map/README.md:7-11
  - tickets/tasks/2026-02-16_general_python_user_profile_split_contract_task.md:236-253
  IMPACT: Story-level requirements are now concrete enough to start
    migration-tranche tasks without additional schema redesign.
  NEXT: choose next task lane: migration tranche planning or skills-map-shim
    retirement.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-02-17T00:25:17Z
  TYPE: DECISION
  CLAIM: Execution moved into a dedicated migration task for ownership
    realignment: programming, architecture, and code-construction skills are
    being relocated from general into engineer.
  EVIDENCE:
  - tickets/tasks/2026-02-17_general_to_engineer_programming_skill_migration_task.md:1-137
  - attention_board.md:26-52
  IMPACT: Story now has a concrete implementation lane for the
    general-vs-engineer split before any skills-map rewiring tranche.
  NEXT: complete relocation and manifest/index updates, then return to split
    contract follow-through.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-02-17T00:35:32Z
  TYPE: DECISION
  CLAIM: A follow-on housekeeping task was added to relocate backlog storage
    into lane-local folders (`tickets/epics/backlog`,
    `tickets/stories/backlog`, and `tickets/tasks/backlog`) and define this
    layout in workflow docs.
  EVIDENCE:
  - tickets/tasks/2026-02-17_backlog_folder_migration_to_ticket_type_roots_task.md:1-154
  - attention_board.md:26-52
  IMPACT: Ticket taxonomy is now consistent across active, backlog, and
    completed lanes.
  NEXT: confirm backlog migration acceptance and close or continue as directed.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-02-17T00:49:55Z
  TYPE: DECISION
  CLAIM: Structural migration task was added and executed to shift
    `epics/stories/tasks` under `tickets/` and consolidate onboarding from
    `agent_onboarding/agent` into `agent_onboarding/default`.
  EVIDENCE:
  - tickets/tasks/2026-02-17_ticket_root_and_agent_default_structure_migration_task.md:1-119
  - attention_board.md:26-45
  IMPACT: Story execution now runs on the new repository topology while keeping
    routing readable during ongoing reorganization.
  NEXT: confirm this migration with user, then continue next restructuring
    tranche.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-02-17T01:01:31Z
  TYPE: DECISION
  CLAIM: Added a new child task for migrating selected root operational docs
    into profile skill folders, with `context_compass/SKILLS.MD` explicitly
    excluded from this tranche.
  EVIDENCE:
  - tickets/tasks/2026-02-17_root_docs_profile_skill_folder_migration_task.md:1-138
  - attention_board.md:26-45
  IMPACT: Root-doc placement and reroute work can proceed without coupling this
    tranche to SKILLS skills-map decisions.
  NEXT: route active board row to the new task and map target destination
    folders before move execution.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-02-17T01:12:15Z
  TYPE: MEASURE
  CLAIM: The root-doc migration child task completed scoped implementation:
    selected root operational docs were moved under
    `agent_onboarding/default/general/skills/` and canonical reroutes were
    applied, while `context_compass/SKILLS.MD` remained excluded.
  EVIDENCE:
  - tickets/tasks/2026-02-17_root_docs_profile_skill_folder_migration_task.md:1-151
  - agent_onboarding/default/general/skills/attention_board.md:23-56
  IMPACT: Story-level onboarding profile restructuring now includes
    profile-localized operational docs and updated canonical routing anchors.
  NEXT: get user acceptance on this child task, then continue the next
    restructuring tranche.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-02-17T01:17:23Z
  TYPE: DECISION
  CLAIM: User accepted and turned in the two structural migration child tasks;
    both were moved to `tickets/tasks/completed/` and board closed anchors were
    synced.
  EVIDENCE:
  - tickets/tasks/completed/2026-02-17_root_docs_profile_skill_folder_migration_task_completed.md:1-20
  - tickets/tasks/completed/2026-02-17_ticket_root_and_agent_default_structure_migration_task_completed.md:1-20
  - agent_onboarding/default/general/skills/attention_board.md:636-649
  IMPACT: Story-level migration execution is archived cleanly and active
    routing remains on the split-contract task for next-tranche work.
  NEXT: continue split-contract discovery/implementation and prioritize the
    next remaining child task.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-02-17T01:30:29Z
  TYPE: PLAN
  CLAIM: Added a new discovery task for AGENTS/profile partitioning so we can
    discuss and approve migration mapping tomorrow before editing policy bodies.
  EVIDENCE:
  - tickets/tasks/2026-02-17_profile_bias_partition_and_agents_bootstrap_decomposition_task.md:1-151
  - agent_onboarding/default/general/skills/attention_board.md:26-48
  IMPACT: Story now has an explicit lane for separating generic defaults from
    `synaptic_python_developer` preferences without rushing implementation.
  NEXT: walk through classification rubric and destination matrix with user,
    then start approved migration tranche.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Closure Confirmation
- [x] Work walkthrough shared with user
- [x] Acceptance criteria confirmed by user
- [x] Applicable anti-pattern checks are clear or escalated with evidence.

## Noting Behavior
- Note focus: cross-task synthesis, dependency flow, and state-transition logic.
- Add notes when task routing changes, gate decisions are made, or risks shift.
- Reference child-task notes for evidence instead of duplicating tactical detail.
- Keep notes append-only and preserve UNKNOWN-first promotion discipline.

## Context / Handoff Summary
Story remains active with routing now centered on the split-contract task.
Two structural migration child tasks were turned in and archived to completed.
Next step is to discuss the new AGENTS/profile partition task and approve
classification + destination mapping before migration edits.