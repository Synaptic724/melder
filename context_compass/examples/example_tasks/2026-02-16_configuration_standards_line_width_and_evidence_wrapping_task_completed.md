

Completed: 2026-02-16T17:52:39Z
Summary: YAML is authoritative for ticket microcycle thresholds
  (`expansion_gate_max_files: 5`, `minimum_note_score: 7`), and policy docs now
  defer to config without duplicated numeric defaults.

# Task: Configuration Standards for Line Width and Evidence Wrapping

## Metadata
- Task ID: TASK-2026-02-16-configuration-standards-line-width-and-evidence-wrapping
- Story: STORY-2026-02-16-context-compass-ticket-design-and-system-interaction-model
- Status: done
- Owner: codex
- Priority: p1
- Created: 2026-02-16T17:16:01Z
- Updated: 2026-02-16T17:52:39Z

## Objective
Create and enforce formatting standards that define line-width targets and
EVIDENCE wrapping behavior, with policy anchored in a core standards doc and
wired to `config/context_compass_config.yaml`.

## Scope Boundaries
- In scope:
- Add `configuration_standards.md` as canonical formatting standard.
- Add config keys for line width and EVIDENCE wrapping in YAML.
- Update workflow/policy/template docs to reference and apply the standard.
- Out of scope:
- Full retrofit of all historical archived/completed tickets.

## Steps / Checklist
- [x] Add `configuration_standards.md` with objective rules and examples.
- [x] Wire standards into `config/context_compass_config.yaml`.
- [x] Update policy and template docs to reference the standards and config.
- [x] Align microcycle thresholds between YAML config and policy docs.
- [x] Normalize active ticket/board `EVIDENCE` fields to one-path-per-line style.
- [x] Wrap template/policy prose lines that exceed the 120-char hard cap.
- [x] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [x] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- Core standards document with line-width and EVIDENCE formatting contract.
- Config YAML section for formatting standard values.
- Policy/template references updated to point to canonical standards.

## Files / Paths Impacted
- `context_compass/config/context_compass_config.yaml`
- `context_compass/agent_onboarding/default/general/skills/configuration_standards.md`
- `context_compass/agent_onboarding/default/general/skills/workflow.md`
- `context_compass/SKILLS.MD`
- `context_compass/agent_onboarding/agent/general/skills/ticketing.md`
- `context_compass/templates/epic_template.md`
- `context_compass/templates/story_template.md`
- `context_compass/templates/task_template.md`
- `context_compass/README.md`
- `context_compass/agent_onboarding/default/general/skills/attention_board.md`
- `context_compass/stories/2026-02-16_context_compass_ticket_design_and_system_interaction_model_story.md`
- `context_compass/tasks/2026-02-16_ticket_system_interaction_topology_map_task.md`
- `context_compass/stories/2026-02-16_context_compass_abstract_system_mapping_story.md`
- `context_compass/stories/2026-02-16_context_compass_improvement_rubric_and_opportunity_investigation_story.md`
- `context_compass/tasks/2026-02-16_ticket_design_rubric_and_template_contract_task.md`
- `context_compass/tasks/2026-02-16_ticket_lifecycle_state_machine_contract_task.md`
- `context_compass/tasks/2026-02-16_datetime_default_standardization_task.md`
- `context_compass/tasks/2026-02-16_attention_board_resume_hierarchy_switch_trigger_schema_task.md`

## Validation
- Executed checks:
  - `rg -n "configuration_standards|line width|hard cap|EVIDENCE" context_compass/README.md context_compass/agent_onboarding/default/general/skills/workflow.md context_compass/SKILLS.MD context_compass/agent_onboarding/agent/general/skills/ticketing.md context_compass/templates/epic_template.md context_compass/templates/story_template.md context_compass/templates/task_template.md context_compass/agent_onboarding/default/general/skills/configuration_standards.md`
  - `rg -n "viewer_tool_read_limit|read_loc_max|documentation_format|line_length|evidence" context_compass/config/context_compass_config.yaml context_compass/agent_onboarding/default/general/skills/configuration_standards.md context_compass/agent_onboarding/default/general/skills/workflow.md context_compass/README.md`
  - `rg -n "EVIDENCE" context_compass/templates/epic_template.md context_compass/templates/story_template.md context_compass/templates/task_template.md`
  - `rg -n "minimum_note_score|expansion_gate_max_files" context_compass/config/context_compass_config.yaml context_compass/agent_onboarding/default/general/skills/workflow.md context_compass/agent_onboarding/agent/general/skills/ticketing.md context_compass/templates/task_template.md`
  - `rg -n "EVIDENCE: .*?, .*" context_compass/agent_onboarding/default/general/skills/attention_board.md context_compass/stories/2026-02-16_context_compass_ticket_design_and_system_interaction_model_story.md context_compass/stories/2026-02-16_context_compass_abstract_system_mapping_story.md context_compass/stories/2026-02-16_context_compass_improvement_rubric_and_opportunity_investigation_story.md context_compass/tasks/2026-02-16_ticket_system_interaction_topology_map_task.md context_compass/tasks/2026-02-16_ticket_design_rubric_and_template_contract_task.md context_compass/tasks/2026-02-16_ticket_lifecycle_state_machine_contract_task.md context_compass/tasks/2026-02-16_datetime_default_standardization_task.md context_compass/tasks/2026-02-16_attention_board_resume_hierarchy_switch_trigger_schema_task.md`
  - `powershell -Command "$files=@('context_compass/templates/epic_template.md','context_compass/templates/story_template.md','context_compass/templates/task_template.md','context_compass/agent_onboarding/default/general/skills/workflow.md','context_compass/agent_onboarding/agent/general/skills/ticketing.md'); foreach($f in $files){$i=0; Get-Content $f | ForEach-Object { $i++; if($_.Length -gt 120){\\\"$f`t$i`t$($_.Length)`t$_\\\"} }}"` (no matches)
- Recommended commands:
  - `rg -n "configuration_standards|line width|hard cap|EVIDENCE" context_compass`
  - `rg -n "formatting|line_length|evidence" context_compass/config/context_compass_config.yaml`
  - `rg -n "minimum_note_score|expansion_gate_max_files" context_compass/config/context_compass_config.yaml context_compass/agent_onboarding/default/general/skills/workflow.md context_compass/agent_onboarding/agent/general/skills/ticketing.md`

## Risks / Rollback Notes
- Risk: strict width rules may reduce readability in edge cases.
  Mitigation: allow exceptions only for unbreakable tokens while preserving
  the hard cap rule for prose.

## Done Checklist
- [x] Steps complete and checked off
- [x] Deliverables produced and linked
- [x] Documentation updated (if needed)
- [x] Validation status recorded
- [x] Unknown-first discipline followed (`UNKNOWN` promoted to `FACT` only with evidence)
- [x] Notes quality maintained (`SCORE_0_TO_10` >= configured minimum score)
- [x] Acceptance criteria reviewed with user and confirmed

## Notes
- DATETIME: 2026-02-16T17:48:15Z
  TYPE: MEASURE
  CLAIM: YAML is now authoritative with `expansion_gate_max_files: 5` and
    `minimum_note_score: 7`; workflow/ticketing docs were updated to reference
    config authority without hardcoded numeric defaults.
  EVIDENCE:
  - context_compass/config/context_compass_config.yaml:13-14
  - context_compass/agent_onboarding/default/general/skills/workflow.md:97-99
  - context_compass/agent_onboarding/agent/general/skills/ticketing.md:105-106
  IMPACT: Ticket microcycle gating now reads as a single source-of-truth model
    (config first, policy docs non-duplicative).
  NEXT: Confirm acceptance with user, then route to
    `tasks/2026-02-16_ticket_lifecycle_state_machine_contract_task.md`.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-02-16T17:46:57Z
  TYPE: FACT
  CLAIM: Microcycle thresholds are still hardcoded as `10/8` in config and
    mirrored as "current defaults" in workflow/ticketing docs, so the active
    user-approved target (`5/7`) is not yet authoritative.
  EVIDENCE:
  - context_compass/config/context_compass_config.yaml:13-14
  - context_compass/agent_onboarding/default/general/skills/workflow.md:97-98
  - context_compass/agent_onboarding/agent/general/skills/ticketing.md:106-107
  IMPACT: Threshold drift causes policy ambiguity and weakens the YAML-source-
    of-truth contract for ticket microcycle behavior.
  NEXT: Set YAML thresholds to `expansion_gate_max_files: 5` and
    `minimum_note_score: 7`, then remove/update stale numeric defaults in
    policy docs.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-02-16T17:32:49Z
  TYPE: FACT
  CLAIM: Remediation pass is complete: microcycle thresholds are YAML-aligned,
    policy/template docs are config-driven, and active notes now use one-path-
    per-line multi-evidence formatting.
  EVIDENCE:
  - context_compass/config/context_compass_config.yaml:10-14
  - context_compass/agent_onboarding/default/general/skills/workflow.md:83-99
  - context_compass/agent_onboarding/agent/general/skills/ticketing.md:42-107
  - context_compass/templates/epic_template.md:73-83
  - context_compass/templates/story_template.md:55-65
  - context_compass/templates/task_template.md:22-60
  - context_compass/agent_onboarding/default/general/skills/attention_board.md:22-181
  - context_compass/tasks/2026-02-16_ticket_system_interaction_topology_map_task.md:100-168
  IMPACT: Ticket formatting and note-quality behavior are now deterministic and
    governed by `config/context_compass_config.yaml` rather than split
    hard-coded rules.
  NEXT: Walk through remediated standards with user and confirm acceptance for
    lifecycle-task promotion.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-02-16T17:28:50Z
  TYPE: PLAN
  CLAIM: Follow-up remediation is required to make ticketing standards fully
    YAML-driven and actively enforced in note formatting.
  EVIDENCE:
  - context_compass/config/context_compass_config.yaml:11-14
  - context_compass/agent_onboarding/default/general/skills/workflow.md:84-85
  - context_compass/agent_onboarding/agent/general/skills/ticketing.md:45-45
  - context_compass/agent_onboarding/default/general/skills/attention_board.md:62-95
  IMPACT: Threshold drift and mixed evidence styles weaken consistency and make
    standards harder to apply objectively.
  NEXT: Patch config/policy/template thresholds and normalize active evidence
    blocks to one-path-per-line format.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-02-16T17:16:01Z
  TYPE: PLAN
  CLAIM: This task introduces a config-backed formatting contract so standards
    are explicit and shared across workflow, templates, and ticket notes.
  EVIDENCE:
  - context_compass/config/context_compass_config.yaml:1-20
  - context_compass/agent_onboarding/default/general/skills/workflow.md:23-47
  - context_compass/SKILLS.MD:34-56
  IMPACT: Formatting quality can be applied consistently without relying on
    ad-hoc style memory.
  NEXT: Create the core standards doc and wire config keys.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-02-16T17:19:53Z
  TYPE: FACT
  CLAIM: Implemented a canonical configuration standards document and wired
    formatting policy values into config, workflow, skills, ticketing, README,
    and templates.
  EVIDENCE:
  - context_compass/agent_onboarding/default/general/skills/configuration_standards.md:1-53
  - context_compass/config/context_compass_config.yaml:1-29
  - context_compass/agent_onboarding/default/general/skills/workflow.md:94-109
  - context_compass/SKILLS.MD:51-57
  - context_compass/agent_onboarding/agent/general/skills/ticketing.md:73-100
  - context_compass/templates/epic_template.md:75-80
  - context_compass/templates/story_template.md:57-62
  - context_compass/templates/task_template.md:50-55
  IMPACT: Line-width and EVIDENCE style now have one canonical contract with
    explicit configuration linkage.
  NEXT: Confirm user acceptance, then promote lifecycle-contract task.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-02-16T17:19:53Z
  TYPE: MEASURE
  CLAIM: Read-window limits are now explicitly line-based and aligned at 500 for
    both view-per-read and LOC chunking.
  EVIDENCE:
  - context_compass/config/context_compass_config.yaml:28-29
  - context_compass/agent_onboarding/default/general/skills/configuration_standards.md:14-20
  - context_compass/tasks/archive/2026-02-15_enforce_dump_chunked_500_line_onboarding_task_completed.md:108-117
  IMPACT: Tool/read behavior matches empirically validated 500-line operational
    limits and avoids ambiguous unit interpretation.
  NEXT: Keep these values stable unless new measured evidence supports change.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
Remediation pass is complete and this task is done. Standards are now
YAML-driven for threshold behavior with `expansion_gate_max_files: 5` and
`minimum_note_score: 7`; active notes use one-path-per-line evidence blocks,
and policy/template hard-cap lines are wrapped.




