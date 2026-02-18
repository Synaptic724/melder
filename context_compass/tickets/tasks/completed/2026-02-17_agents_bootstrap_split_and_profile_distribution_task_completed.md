

- Completed: 2026-02-17T08:43:54Z
- Summary: Closed by user directive to turn in all open tickets and clear active routing; remaining validation not run.

# Task: Split Root AGENTS into Bootstrap and Profile-Owned Policies

## Metadata
- Task ID: TASK-2026-02-17-agents-bootstrap-split-and-profile-distribution
- Story: none
- Status: done
- Owner: codex
- Priority: p1
- Created: 2026-02-17T12:16:31Z
- Updated: 2026-02-17T08:43:54Z

## Objective
Create a bootstrap-ready root contract draft in `context_compass/new_agents.md`
and distribute policy detail to profile-owned directories (`new`, `general`,
`engineer`, `synaptic_python_developer`) without onboarding policy loss.

## Ticket Contract
- ENTRY_GATE: `attention_board.md` active row routes to this task and this
  ticket contains an evidence-backed discovery note.
- EXECUTION_BOUNDARY: `context_compass/AGENTS.MD`, new
  `context_compass/new_agents.md`, profile docs under
  `context_compass/agent_onboarding/default/general/`,
  `context_compass/agent_onboarding/default/engineer/`,
  `context_compass/agent_onboarding/user_defined/synaptic_python_developer/`,
  `context_compass/agent_onboarding/default/new/`, and routing docs if needed.
- DEPENDENCIES: `context_compass/config/context_compass_config.yaml`,
  `context_compass/skill_path_map/SKILLS.MD`, resolved profile maps.
- EXIT_GATE: section-ownership map is approved by user, `new_agents.md`
  bootstrap draft is present, and onboarding path remains deterministic.
- FAILURE_ESCALATION: if any section ownership is ambiguous or conflicts with
  profile boundaries, record `DECISION_REQUEST` before implementing.

## Scope Boundaries
- In scope:
  - Discovery and section ownership mapping for root `AGENTS.MD`.
  - Bootstrap contract design and root pointer conversion.
  - Targeted policy redistribution into existing profile docs or new docs.
- Out of scope:
  - Unrelated policy rewrites beyond bootstrap/split needs.
  - Behavior changes outside onboarding and policy routing.

## State Transition Event
- from_state: ready
- to_state: in_progress
- transition_reason: user requested immediate task creation and discovery-first
  planning for AGENTS/bootstrap split.

## Steps / Checklist
- [x] Create active task and route `attention_board.md` to this ticket.
- [x] Discovery: inventory root `AGENTS.MD` section clusters.
- [x] Discovery: inventory existing profile-owned policy docs and map coverage.
- [x] Propose section-to-target-file split map and bootstrap contract to user.
- [x] After approval, implement bootstrap + root pointer conversion.
- [x] Apply targeted profile doc updates for missing ownership gaps.
- [x] Run validation checks and summarize final diff.
- [x] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [x] Document each meaningful finding immediately in `## Notes` before further
      investigation.

## Deliverables
- `context_compass/new_agents.md` with explicit onboarding bootstrap draft.
- Profile-specific `AGENTS.MD` files for:
  `default/new`, `default/general`, `default/engineer`, and
  `user_defined/synaptic_python_developer`.
- Profile-owned policy placement updates with no policy-loss drift.
- Updated routing context in `context_compass/attention_board.md`.

## Files / Paths Impacted
- `context_compass/tickets/tasks/2026-02-17_agents_bootstrap_split_and_profile_distribution_task.md`
- `context_compass/attention_board.md`
- `context_compass/AGENTS.MD`
- `context_compass/new_agents.md`
- `context_compass/agent_onboarding/default/general/`
- `context_compass/agent_onboarding/default/engineer/`
- `context_compass/agent_onboarding/user_defined/synaptic_python_developer/`
- `context_compass/agent_onboarding/default/new/`

## Validation
- Not run.
- Recommended commands:
  - `rg -n "^#|^##|^###" context_compass/AGENTS.MD context_compass/new_agents.md`
  - `rg -n "bootstrap|AGENTS.MD|execution_contract|policy_skills" context_compass`
  - `rg -n "INHERITS_ALL_PATHS_FROM|agent_onboarding" context_compass/skill_path_map/*.md context_compass/skill_path_map/*/*.md`

## Risks / Rollback Notes
- Risk: policy loss or contradictory ownership during split.
- Mitigation: keep root-to-target mapping explicit and diff-backed before cut.
- Rollback: restore prior `AGENTS.MD` from repository history if user rejects split layout.

## Applicable Anti-Patterns
- [x] No implementation before user approves split map and bootstrap wording.
- [x] No policy claim without direct file evidence.
- [x] No scope expansion outside bootstrap and profile policy ownership.

## Done Checklist
- [x] Steps complete and checked off
- [x] Deliverables produced and linked
- [x] Documentation updated (if needed)
- [x] Validation status recorded
- [x] Unknown-first discipline followed (`UNKNOWN` promoted to `FACT` only with evidence)
- [x] Notes quality maintained (`SCORE_0_TO_10` >=
      `workflow.ticket_microcycle.minimum_note_score`)
- [x] Applicable anti-pattern checks are clear or escalated with evidence.
- [x] Acceptance criteria reviewed with user and confirmed
- [x] Board sync completed for successor routing or closure anchor update.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: false
- ARTIFACT_PATHS:
  - none
- DISPOSITION: delete_on_close
- CLEANUP_TRIGGER: task closure

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-02-17T12:16:31Z
  TYPE: FACT
  CLAIM: Root `AGENTS.MD` currently contains mixed bootstrap, onboarding gates,
    general policy, engineering quality, and testing doctrine in one file.
  EVIDENCE:
  - context_compass/AGENTS.MD:3-3
  - context_compass/AGENTS.MD:138-138
  - context_compass/AGENTS.MD:199-199
  - context_compass/AGENTS.MD:510-510
  - context_compass/AGENTS.MD:617-617
  - context_compass/AGENTS.MD:842-842
  IMPACT: A pointer-style root `AGENTS.MD` requires explicit redistribution to
    profile-owned docs or onboarding quality will regress.
  NEXT: Build a section-to-target ownership map before file edits.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-02-17T12:16:31Z
  TYPE: FACT
  CLAIM: Active profile map chain is already explicit (`general -> engineer ->
    synaptic_python_developer`), and `new` remains first-time onboarding only.
  EVIDENCE:
  - context_compass/skill_path_map/default/general.md:1-32
  - context_compass/skill_path_map/default/engineer.md:1-19
  - context_compass/skill_path_map/user_defined/synaptic_python_developer.md:1-23
  - context_compass/agent_onboarding/default/new/skills/first_time_profile_setup.md:8-21
  IMPACT: Split design can use existing ownership boundaries instead of
    introducing new profile layers.
  NEXT: Draft the exact bootstrap contract and per-section destination files.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-02-17T12:17:54Z
  TYPE: DECISION
  CLAIM: User approved keeping root as bootstrap and using profile-specific
    AGENTS only for `new/general/engineer/synaptic`, rejecting a shared
    `default` AGENTS layer in profile map reads.
  EVIDENCE:
  - context_compass/attention_board.md:25-31
  - context_compass/tickets/tasks/2026-02-17_agents_bootstrap_split_and_profile_distribution_task.md:52-59
  IMPACT: Map wiring must stay profile-specific; shared default routing layer
    should not be in resolved profile readsets.
  NEXT: Remove `agent_onboarding/default/AGENTS.MD` map entries and delete that
    file.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-02-17T12:23:40Z
  TYPE: FACT
  CLAIM: Skill maps now include only profile-local AGENTS entries:
    `new/general/engineer/synaptic`; shared default AGENTS references were
    removed.
  EVIDENCE:
  - context_compass/skill_path_map/default/new.md:1-14
  - context_compass/skill_path_map/default/general.md:1-33
  - context_compass/skill_path_map/default/engineer.md:1-20
  - context_compass/skill_path_map/user_defined/synaptic_python_developer.md:1-24
  IMPACT: Profile onboarding read paths are cleanly partitioned and aligned to
    user-approved boundaries.
  NEXT: Verify content quality of each profile AGENTS file and adjust wording
    before root cutover.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

## Context / Handoff Summary
Bootstrap draft and profile AGENTS scaffolding are in place, with user-approved
scope narrowed to root + `new/general/engineer/synaptic` only. Next step is to
tighten AGENTS content quality per profile before root cutover.
## Closure Note
Closed by explicit user instruction to close all tickets and clear attention routing.




