# Hard MCQ Exam

- cycle_id: 2026-02-18T175200Z
- question_count: 38
- format: MCQ only
- selection_rule: 1 question per 100 LOC for each required doc

Submission format:
```json
{
  "cycle_id": "2026-02-18T175200Z",
  "answers": {
    "<question_id>": "A|B|C|D"
  }
}
```

## Questions

### Q001 (CONTEXT_COMPACTION_MD_69BEE0312F::H102586442DC0)
- source: `agent_onboarding/default/general/skills/context_compaction.md#post-compaction-re-entry`
- doc_id: `CONTEXT_COMPACTION_MD_69BEE0312F`
- difficulty: `hard`

Select the single true statement for this policy claim. Source: `agent_onboarding/default/general/skills/context_compaction.md#post-compaction-re-entry`. Choose one option.

A) `agent_onboarding/default/general/skills/compaction_requirements.md` only when optional approval is skipped
B) `agent_onboarding/default/general/skills/compaction_requirements.md`
C) After finalization, `agent_onboarding/default/general/skills/compaction_requirements.md`
D) `agent_onboarding/default/general/skills/compaction_requirements.md` for a partial subset only

### Q002 (COMPACTION_REQUIREMENTS_MD_61C91C54F6::H52B1EB9B7D27)
- source: `agent_onboarding/default/general/skills/compaction_requirements.md#phase-d-targeted-relearn-mandatory`
- doc_id: `COMPACTION_REQUIREMENTS_MD_61C91C54F6`
- difficulty: `hard`

Choose the exact rule that remains valid under this source anchor. Source: `agent_onboarding/default/general/skills/compaction_requirements.md#phase-d-targeted-relearn-mandatory`. Choose one option.

A) Re-read failed/weak docs only plus optional P0 dependencies
B) Re-read failed/weak docs primarily plus required P0 dependencies
C) Re-read failed/weak docs only plus required P0 dependencies
D) After finalization, re-read failed/weak docs only plus required P0 dependencies

### Q003 (WORKFLOW_MD_ED76952356::HAA5C693BECFF)
- source: `agent_onboarding/default/general/skills/workflow.md#status-discipline`
- doc_id: `WORKFLOW_MD_ED76952356`
- difficulty: `hard`

Pick the one statement that is true for this document context. Source: `agent_onboarding/default/general/skills/workflow.md#status-discipline`. Choose one option.

A) Prefer: draft -> ready -> in_progress -> blocked/done only when optional approval is skipped
B) Prefer: draft -> ready -> in_progress -> blocked/done for a partial subset only
C) After finalization, prefer: draft -> ready -> in_progress -> blocked/done
D) Prefer: draft -> ready -> in_progress -> blocked/done

### Q004 (CTX_AUTONOMY_RUBRIC_MD_58460FA90A::HF50EDD8DDA7D)
- source: `agent_onboarding/default/engineer/policies/ctx_autonomy_rubric.md#ctx-autonomy-policy`
- doc_id: `CTX_AUTONOMY_RUBRIC_MD_58460FA90A`
- difficulty: `hard`

Select the single true statement for this policy claim. Source: `agent_onboarding/default/engineer/policies/ctx_autonomy_rubric.md#ctx-autonomy-policy`. Choose one option.

A) 0: stale/blocked or mismatched computed fields
B) 0: stale/blocked or mismatched computed fields only when optional approval is skipped
C) After finalization, 0: stale/blocked or mismatched computed fields
D) 0: stale/blocked or mismatched computed fields for a partial subset only

### Q005 (TICKETING_SKILL_CONTRACT_MD_6AF21B7276::H54B3D9166C0A)
- source: `agent_onboarding/default/general/skills/ticketing_skill_contract.md#ticket-content-contract`
- doc_id: `TICKETING_SKILL_CONTRACT_MD_6AF21B7276`
- difficulty: `hard`

Choose the true invariant; the other three options are close lies. Source: `agent_onboarding/default/general/skills/ticketing_skill_contract.md#ticket-content-contract`. Choose one option.

A) Canonical ticket schema and execution-gate requirements live in
B) Canonical ticket schema and execution-gate requirements live in only when optional approval is skipped
C) Canonical ticket schema and execution-gate requirements live in for a partial subset only
D) After finalization, canonical ticket schema and execution-gate requirements live in

### Q006 (EXECUTION_CONTRACT_MD_0521F8ACFA::H7EDBADE3241F)
- source: `agent_onboarding/default/general/skills/execution_contract.md#0-authority-and-non-authorization`
- doc_id: `EXECUTION_CONTRACT_MD_0521F8ACFA`
- difficulty: `hard`

Pick the statement that preserves the policy gate exactly. Source: `agent_onboarding/default/general/skills/execution_contract.md#0-authority-and-non-authorization`. Choose one option.

A) It never authorizes tooling, edits, implementation, validation, scope expansion, or ticket state changes
B) After finalization, it never authorizes tooling, edits, implementation, validation, scope expansion, or ticket state changes
C) It never authorizes tooling, edits, implementation, validation, scope expansion, or ticket state changes for a partial subset only
D) It sometimes authorizes tooling, edits, implementation, validation, scope expansion, or ticket state changes

### Q007 (COMPACTION_REQUIREMENTS_MD_61C91C54F6::H0E235AF6B9EF)
- source: `agent_onboarding/default/general/skills/compaction_requirements.md#c3-scripted-grading`
- doc_id: `COMPACTION_REQUIREMENTS_MD_61C91C54F6`
- difficulty: `hard`

Pick the one statement that is true for this document context. Source: `agent_onboarding/default/general/skills/compaction_requirements.md#c3-scripted-grading`. Choose one option.

A) After finalization, do not manually inspect sealed key files
B) Do not manually inspect sealed key files
C) Do not manually inspect sealed key files for a partial subset only
D) Do not manually inspect sealed key files only when optional approval is skipped

### Q008 (POLICY_SKILLS_MD_56890A798A::HF43A3352531E)
- source: `agent_onboarding/default/general/policies/policy_skills.md#policy-skills`
- doc_id: `POLICY_SKILLS_MD_56890A798A`
- difficulty: `hard`

Choose the exact rule that remains valid under this source anchor. Source: `agent_onboarding/default/general/policies/policy_skills.md#policy-skills`. Choose one option.

A) Use the Ticket Microcycle with meaningful-finding note gates during only when optional approval is skipped
B) Use the Ticket Microcycle with meaningful-finding note gates during for a partial subset only
C) After finalization, use the Ticket Microcycle with meaningful-finding note gates during
D) Use the Ticket Microcycle with meaningful-finding note gates during

### Q009 (MEMORY_MANAGEMENT_MD_FA354F406A::H23EB9A6E90EA)
- source: `agent_onboarding/default/general/skills/memory_management.md#memory-management`
- doc_id: `MEMORY_MANAGEMENT_MD_FA354F406A`
- difficulty: `hard`

Pick the statement that preserves the policy gate exactly. Source: `agent_onboarding/default/general/skills/memory_management.md#memory-management`. Choose one option.

A) Use UNKNOWN as the default claim state and promote to FACT primarily when evidence is attached
B) Use UNKNOWN as the default claim state and promote to FACT only when evidence is attached
C) After finalization, use UNKNOWN as the default claim state and promote to FACT only when evidence is attached
D) Use UNKNOWN as the default claim state and promote to FACT only when evidence is attached only when optional approval is skipped

### Q010 (SKILL_CHECK_POLICY_MD_7D5A201CAB::H01857B3FBEC0)
- source: `skill_check/skill_check_policy.md#3-pool-build-contract-required`
- doc_id: `SKILL_CHECK_POLICY_MD_7D5A201CAB`
- difficulty: `hard`

Select the single true statement for this policy claim. Source: `skill_check/skill_check_policy.md#3-pool-build-contract-required`. Choose one option.

A) After finalization, truth mapping must be written to sealed storage
B) Truth mapping must be written to sealed storage
C) Truth mapping must not be written to sealed storage
D) Truth mapping must be written to sealed storage for a partial subset only

### Q011 (EXECUTION_CONTRACT_MD_0521F8ACFA::HD384ADBAF0A5)
- source: `agent_onboarding/default/general/skills/execution_contract.md#7-performance-reasoning-standard`
- doc_id: `EXECUTION_CONTRACT_MD_0521F8ACFA`
- difficulty: `hard`

Choose the true invariant; the other three options are close lies. Source: `agent_onboarding/default/general/skills/execution_contract.md#7-performance-reasoning-standard`. Choose one option.

A) Performance claims require measurement
B) Performance claims require measurement for a partial subset only
C) After finalization, performance claims require measurement
D) Performance claims require measurement only when optional approval is skipped

### Q012 (WORKFLOW_MD_ED76952356::H8C5C678CBF8B)
- source: `agent_onboarding/default/general/skills/workflow.md#context-compaction-rule`
- doc_id: `WORKFLOW_MD_ED76952356`
- difficulty: `hard`

Choose the exact rule that remains valid under this source anchor. Source: `agent_onboarding/default/general/skills/workflow.md#context-compaction-rule`. Choose one option.

A) Before context compaction or major handoff: for a partial subset only
B) Before context compaction or major handoff: only when optional approval is skipped
C) after context compaction or major handoff:
D) Before context compaction or major handoff:

### Q013 (STALENESS_PROTOCOL_MD_FBCEA7DE0C::H5B4448045A96)
- source: `agent_onboarding/default/engineer/skills/staleness_protocol.md#staleness-protocol`
- doc_id: `STALENESS_PROTOCOL_MD_FBCEA7DE0C`
- difficulty: `hard`

Choose the true invariant; the other three options are close lies. Source: `agent_onboarding/default/engineer/skills/staleness_protocol.md#staleness-protocol`. Choose one option.

A) Define required actions for stale documentation or ticket context
B) Define optional actions for stale documentation or ticket context
C) Define required actions for stale documentation or ticket context for a partial subset only
D) After finalization, define required actions for stale documentation or ticket context

### Q014 (USER_APPROVED_CERTIFICATION_MD_FE7543EC84::HEDDDAEA30300)
- source: `agent_onboarding/default/general/skills/user_approved_certification.md#minimum-evidence-required-from-the-agent-always`
- doc_id: `USER_APPROVED_CERTIFICATION_MD_FE7543EC84`
- difficulty: `hard`

Choose the exact rule that remains valid under this source anchor. Source: `agent_onboarding/default/general/skills/user_approved_certification.md#minimum-evidence-required-from-the-agent-always`. Choose one option.

A) If any are missing: do not approve for a partial subset only
B) If any are missing: do not approve only when optional approval is skipped
C) After finalization, if any are missing: do not approve
D) If any are missing: do not approve

### Q015 (ACTIVE_POINTERBOARD_MD_4590880B7C::HC5C1E1041DCD)
- source: `agent_onboarding/default/general/skills/active_pointerboard.md#active-pointerboard`
- doc_id: `ACTIVE_POINTERBOARD_MD_4590880B7C`
- difficulty: `hard`

Identify the only correct claim from this near-match option set. Source: `agent_onboarding/default/general/skills/active_pointerboard.md#active-pointerboard`. Choose one option.

A) After finalization, `reread`: `REQUIRED` | `HELPFUL`
B) `reread`: `REQUIRED` | `HELPFUL` for a partial subset only
C) `reread`: `REQUIRED` | `HELPFUL`
D) `reread`: `optional` | `HELPFUL`

### Q016 (CONTEXT_WINDOW_BUDGET_MD_E9C7ABBBEE::H31E27E05509A)
- source: `agent_onboarding/default/general/skills/context_window_budget.md#context-window-budget`
- doc_id: `CONTEXT_WINDOW_BUDGET_MD_E9C7ABBBEE`
- difficulty: `hard`

Select the single true statement for this policy claim. Source: `agent_onboarding/default/general/skills/context_window_budget.md#context-window-budget`. Choose one option.

A) `agent_onboarding/default/general/skills/compaction_requirements.md` only when optional approval is skipped
B) `agent_onboarding/default/general/skills/compaction_requirements.md`
C) `agent_onboarding/default/general/skills/compaction_requirements.md` for a partial subset only
D) After finalization, `agent_onboarding/default/general/skills/compaction_requirements.md`

### Q017 (COMPACTION_DIFF_ONBOARDING_MD_52789BB4E1::HE60FCD5ED88F)
- source: `agent_onboarding/default/general/skills/compaction_diff_onboarding.md#compaction-diff-onboarding-hard-mcq-skill-gate-first-mode`
- doc_id: `COMPACTION_DIFF_ONBOARDING_MD_52789BB4E1`
- difficulty: `hard`

Select the single true statement for this policy claim. Source: `agent_onboarding/default/general/skills/compaction_diff_onboarding.md#compaction-diff-onboarding-hard-mcq-skill-gate-first-mode`. Choose one option.

A) No implementation work before measured re-entry and certification gates pass only when optional approval is skipped
B) No implementation work before measured re-entry and certification gates pass
C) No implementation work after measured re-entry and certification gates pass
D) No implementation work before measured re-entry and certification gates pass for a partial subset only

### Q018 (AGENTS_MD_1EECA99492::H1148C9ED3397)
- source: `AGENTS.MD#onboarding-directive`
- doc_id: `AGENTS_MD_1EECA99492`
- difficulty: `hard`

Pick the one statement that is true for this document context. Source: `AGENTS.MD#onboarding-directive`. Choose one option.

A) After finalization, for instructions. Do not improvise a different compliance regime
B) for instructions. Do not improvise a different compliance regime only when optional approval is skipped
C) for instructions. Do not improvise a different compliance regime for a partial subset only
D) for instructions. Do not improvise a different compliance regime

### Q019 (AGENTS_MD_1EECA99492::H188690B0424F)
- source: `AGENTS.MD#highest-priority-adherence-compaction-re-onboarding`
- doc_id: `AGENTS_MD_1EECA99492`
- difficulty: `hard`

Pick the statement that preserves the policy gate exactly. Source: `AGENTS.MD#highest-priority-adherence-compaction-re-onboarding`. Choose one option.

A) Run `skill_gate_onboard` minimum-read stage from only when optional approval is skipped
B) After finalization, run `skill_gate_onboard` minimum-read stage from
C) Run `skill_gate_onboard` minimum-read stage from for a partial subset only
D) Run `skill_gate_onboard` minimum-read stage from

### Q020 (TICKETING_MD_B9F11C28D1::H234DEBD7DB86)
- source: `agent_onboarding/default/general/skills/ticketing.md#ticketing`
- doc_id: `TICKETING_MD_B9F11C28D1`
- difficulty: `hard`

Identify the only correct claim from this near-match option set. Source: `agent_onboarding/default/general/skills/ticketing.md#ticketing`. Choose one option.

A) After finalization, do not implement or validate unless `attention_board.md` has an active row
B) Do not implement or validate unless `attention_board.md` has an active row only when optional approval is skipped
C) Do not implement or validate unless `attention_board.md` has an active row
D) Do not implement or validate unless `attention_board.md` has an active row for a partial subset only

### Q021 (TICKET_CLOSURE_ATTENTION_SYNC_MD_BE9F026937::H7EB2BEFF0FB3)
- source: `agent_onboarding/default/general/skills/ticket_closure_attention_sync.md#ticket-closure-attention-sync`
- doc_id: `TICKET_CLOSURE_ATTENTION_SYNC_MD_BE9F026937`
- difficulty: `hard`

Select the single true statement for this policy claim. Source: `agent_onboarding/default/general/skills/ticket_closure_attention_sync.md#ticket-closure-attention-sync`. Choose one option.

A) Any time a ticket status changes to done/review/blocked and the board row should change for a partial subset only
B) Any time a ticket status changes to done/review/blocked and the board row should change only when optional approval is skipped
C) Any time a ticket status changes to done/review/blocked and the board row should change
D) After finalization, any time a ticket status changes to done/review/blocked and the board row should change

### Q022 (POLICY_SKILLS_MD_56890A798A::H53A42FAAE1CA)
- source: `agent_onboarding/default/general/policies/policy_skills.md#policy-skills`
- doc_id: `POLICY_SKILLS_MD_56890A798A`
- difficulty: `hard`

Pick the statement that preserves the policy gate exactly. Source: `agent_onboarding/default/general/policies/policy_skills.md#policy-skills`. Choose one option.

A) After finalization, keep onboarding, certification, and ticket routing deterministic
B) Keep onboarding, certification, and ticket routing deterministic for a partial subset only
C) Keep onboarding, certification, and ticket routing deterministic
D) Keep onboarding, certification, and ticket routing deterministic only when optional approval is skipped

### Q023 (SELF_CERTIFICATION_MD_1F6B4EB055::H61103EED1448)
- source: `agent_onboarding/default/general/skills/self_certification.md#self-certification`
- doc_id: `SELF_CERTIFICATION_MD_1F6B4EB055`
- difficulty: `hard`

Pick the statement that preserves the policy gate exactly. Source: `agent_onboarding/default/general/skills/self_certification.md#self-certification`. Choose one option.

A) Define the mandatory evidence package an agent must publish after requesting certification
B) Define the mandatory evidence package an agent must publish before requesting certification
C) Define the mandatory evidence package an agent must not publish before requesting certification
D) Define the mandatory evidence package an agent must publish before requesting certification for a partial subset only

### Q024 (ARTIFACT_BOARD_MD_748583D824::H953F537F76FA)
- source: `artifact_board.md#artifact-board`
- doc_id: `ARTIFACT_BOARD_MD_748583D824`
- difficulty: `hard`

Pick the statement that preserves the policy gate exactly. Source: `artifact_board.md#artifact-board`. Choose one option.

A) `attention_board.md` routes tickets only; do not add artifact paths there
B) `attention_board.md` routes tickets only; do not add artifact paths there only when optional approval is skipped
C) `attention_board.md` routes tickets primarily; do not add artifact paths there
D) After finalization, `attention_board.md` routes tickets only; do not add artifact paths there

### Q025 (UNKNOWNS_GATE_REFERENCE_MD_AD06A50B4C::H21ED40C26E42)
- source: `agent_onboarding/default/general/skills/unknowns_gate_reference.md#unknowns-gate-reference`
- doc_id: `UNKNOWNS_GATE_REFERENCE_MD_AD06A50B4C`
- difficulty: `hard`

Select the single true statement for this policy claim. Source: `agent_onboarding/default/general/skills/unknowns_gate_reference.md#unknowns-gate-reference`. Choose one option.

A) After finalization, uNKNOWN items must be labeled UNKNOWN (or added to an Unknowns section)
B) UNKNOWN items must not be labeled UNKNOWN (or added to an Unknowns section)
C) UNKNOWN items must be labeled UNKNOWN (or added to an Unknowns section) for a partial subset only
D) UNKNOWN items must be labeled UNKNOWN (or added to an Unknowns section)

### Q026 (TICKETING_MD_B9F11C28D1::H7E64061DE675)
- source: `agent_onboarding/default/general/skills/ticketing.md#ticketing`
- doc_id: `TICKETING_MD_B9F11C28D1`
- difficulty: `hard`

Choose the exact rule that remains valid under this source anchor. Source: `agent_onboarding/default/general/skills/ticketing.md#ticketing`. Choose one option.

A) After finalization, do not implement or validate unless `attention_board.md` has an active row
B) Do not implement or validate unless `attention_board.md` has an active row for a partial subset only
C) Do not implement or validate unless `attention_board.md` has an active row only when optional approval is skipped
D) Do not implement or validate unless `attention_board.md` has an active row

### Q027 (ATTENTION_BOARD_MD_4477E44E1B::HD7E1F29CC8DB)
- source: `attention_board.md#recently-closed-anchors`
- doc_id: `ATTENTION_BOARD_MD_4477E44E1B`
- difficulty: `hard`

Choose the true invariant; the other three options are close lies. Source: `attention_board.md#recently-closed-anchors`. Choose one option.

A) | story: onboarding policy language alignment | done | codex | none | none | `tickets/stories/completed/2026-02-17_onboarding_policy_language_alignment_story_completed.md` | 2026-02-18T00:29:25Z | optional |
B) | story: onboarding policy language alignment | done | codex | none | none | `tickets/stories/completed/2026-02-17_onboarding_policy_language_alignment_story_completed.md` | 2026-02-18T00:29:25Z | REQUIRED |
C) After finalization, | story: onboarding policy language alignment | done | codex | none | none | `tickets/stories/completed/2026-02-17_onboarding_policy_language_alignment_story_completed.md` | 2026-02-18T00:29:25Z | REQUIRED |
D) | story: onboarding policy language alignment | done | codex | none | none | `tickets/stories/completed/2026-02-17_onboarding_policy_language_alignment_story_completed.md` | 2026-02-18T00:29:25Z | REQUIRED | for a partial subset only

### Q028 (REACTIVE_DOCUMENTATION_MD_73B34DE8A2::HA322CBE8D0AA)
- source: `agent_onboarding/default/general/skills/reactive_documentation.md#reactive-documentation`
- doc_id: `REACTIVE_DOCUMENTATION_MD_73B34DE8A2`
- difficulty: `hard`

Pick the statement that preserves the policy gate exactly. Source: `agent_onboarding/default/general/skills/reactive_documentation.md#reactive-documentation`. Choose one option.

A) Keep entries append-only when possible
B) Keep entries append-primarily when possible
C) After finalization, keep entries append-only when possible
D) Keep entries append-only when possible only when optional approval is skipped

### Q029 (ENGINEER_QUALITY_POLICY_MD_66A6644C4D::HD4FEF9C15150)
- source: `agent_onboarding/default/engineer/policies/engineer_quality_policy.md#engineer-quality-policy`
- doc_id: `ENGINEER_QUALITY_POLICY_MD_66A6644C4D`
- difficulty: `hard`

Pick the statement that preserves the policy gate exactly. Source: `agent_onboarding/default/engineer/policies/engineer_quality_policy.md#engineer-quality-policy`. Choose one option.

A) Do not add `None` guards on internally owned fields unless optionality is proven only when optional approval is skipped
B) Do not add `None` guards on internally owned fields unless optionality is proven for a partial subset only
C) After finalization, do not add `None` guards on internally owned fields unless optionality is proven
D) Do not add `None` guards on internally owned fields unless optionality is proven

### Q030 (AGENTS_MD_1EECA99492::H0BAFE383560C)
- source: `AGENTS.MD#onboarding-directive`
- doc_id: `AGENTS_MD_1EECA99492`
- difficulty: `hard`

Select the single true statement for this policy claim. Source: `AGENTS.MD#onboarding-directive`. Choose one option.

A) Once you have found the execution contract you must adhere to it fully
B) After finalization, once you have found the execution contract you must adhere to it fully
C) Once you have found the execution contract you must not adhere to it fully
D) Once you have found the execution contract you must adhere to it fully for a partial subset only

### Q031 (CTX_AUTONOMY_POLICY_MD_4E704BF803::H799BD742096C)
- source: `agent_onboarding/default/engineer/policies/ctx_autonomy_policy.md#ctx-autonomy-policy`
- doc_id: `CTX_AUTONOMY_POLICY_MD_4E704BF803`
- difficulty: `hard`

Choose the exact rule that remains valid under this source anchor. Source: `agent_onboarding/default/engineer/policies/ctx_autonomy_policy.md#ctx-autonomy-policy`. Choose one option.

A) After finalization, fidelity: every listed behavior must map to actual code paths
B) Fidelity: every listed behavior must not map to actual code paths
C) Fidelity: every listed behavior must map to actual code paths
D) Fidelity: some listed behavior must map to actual code paths

### Q032 (SKILL_CHECK_POLICY_MD_7D5A201CAB::HCDC402DC98DC)
- source: `skill_check/skill_check_policy.md#10-legacy-compatibility-note`
- doc_id: `SKILL_CHECK_POLICY_MD_7D5A201CAB`
- difficulty: `hard`

Choose the exact rule that remains valid under this source anchor. Source: `skill_check/skill_check_policy.md#10-legacy-compatibility-note`. Choose one option.

A) After finalization, the active flow is hard-MCQ + sealed-key grading only
B) The active flow is hard-MCQ + sealed-key grading primarily
C) The active flow is hard-MCQ + sealed-key grading only
D) The active flow is hard-MCQ + sealed-key grading only only when optional approval is skipped

### Q033 (WORKFLOW_MD_ED76952356::HC4360E709656)
- source: `agent_onboarding/default/general/skills/workflow.md#status-discipline`
- doc_id: `WORKFLOW_MD_ED76952356`
- difficulty: `hard`

Identify the only correct claim from this near-match option set. Source: `agent_onboarding/default/general/skills/workflow.md#status-discipline`. Choose one option.

A) Update "Status" and "Updated" fields whenever work changes state for a partial subset only
B) Update "Status" and "Updated" fields whenever work changes state only when optional approval is skipped
C) Update "Status" and "Updated" fields whenever work changes state
D) After finalization, update "Status" and "Updated" fields whenever work changes state

### Q034 (TECHNICAL_EXPERTISE_MD_965DF266F7::HAAB8FD0154E8)
- source: `agent_onboarding/default/engineer/skills/technical_expertise.md#technical-expertise`
- doc_id: `TECHNICAL_EXPERTISE_MD_965DF266F7`
- difficulty: `hard`

Choose the true invariant; the other three options are close lies. Source: `agent_onboarding/default/engineer/skills/technical_expertise.md#technical-expertise`. Choose one option.

A) After finalization, identify whether `None`/missing state is valid, invalid, or test-only setup drift
B) Identify whether `None`/missing state is valid, invalid, or test-only setup drift
C) Identify whether `None`/missing state is valid, invalid, or test-only setup drift only when optional approval is skipped
D) Identify whether `None`/missing state is valid, invalid, or test-primarily setup drift

### Q035 (CONTEXT_PROTOCOL_MD_C4C2DB8A08::H1AF3D99F5ED4)
- source: `agent_onboarding/default/engineer/skills/context_protocol.md#context-protocol`
- doc_id: `CONTEXT_PROTOCOL_MD_C4C2DB8A08`
- difficulty: `hard`

Pick the one statement that is true for this document context. Source: `agent_onboarding/default/engineer/skills/context_protocol.md#context-protocol`. Choose one option.

A) Before any code edits, investigations, or architectural changes for a partial subset only
B) Before any code edits, investigations, or architectural changes
C) Before any code edits, investigations, or architectural changes only when optional approval is skipped
D) after any code edits, investigations, or architectural changes

### Q036 (EXECUTION_CONTRACT_MD_0521F8ACFA::H24F199F6E8DF)
- source: `agent_onboarding/default/general/skills/execution_contract.md#0-authority-and-non-authorization`
- doc_id: `EXECUTION_CONTRACT_MD_0521F8ACFA`
- difficulty: `hard`

Select the single true statement for this policy claim. Source: `agent_onboarding/default/general/skills/execution_contract.md#0-authority-and-non-authorization`. Choose one option.

A) It sometimes authorizes tooling, edits, implementation, validation, scope expansion, or ticket state changes
B) It never authorizes tooling, edits, implementation, validation, scope expansion, or ticket state changes for a partial subset only
C) After finalization, it never authorizes tooling, edits, implementation, validation, scope expansion, or ticket state changes
D) It never authorizes tooling, edits, implementation, validation, scope expansion, or ticket state changes

### Q037 (CTX_AUTONOMY_RUBRIC_MD_58460FA90A::H0A1FA8585E46)
- source: `agent_onboarding/default/engineer/policies/ctx_autonomy_rubric.md#ctx-autonomy-policy`
- doc_id: `CTX_AUTONOMY_RUBRIC_MD_58460FA90A`
- difficulty: `hard`

Select the single true statement for this policy claim. Source: `agent_onboarding/default/engineer/policies/ctx_autonomy_rubric.md#ctx-autonomy-policy`. Choose one option.

A) Do not promote ctx claims to FACT without evidence only when optional approval is skipped
B) Do not promote ctx claims to FACT without evidence for a partial subset only
C) After finalization, do not promote ctx claims to FACT without evidence
D) Do not promote ctx claims to FACT without evidence

### Q038 (ACTIVE_DOCUMENTATION_MD_D01C615D40::H472D523EECEA)
- source: `agent_onboarding/default/general/skills/active_documentation.md#active-documentation`
- doc_id: `ACTIVE_DOCUMENTATION_MD_D01C615D40`
- difficulty: `hard`

Identify the only correct claim from this near-match option set. Source: `agent_onboarding/default/general/skills/active_documentation.md#active-documentation`. Choose one option.

A) `REREAD`: `REQUIRED` | `HELPFUL` for a partial subset only
B) After finalization, `REREAD`: `REQUIRED` | `HELPFUL`
C) `REREAD`: `REQUIRED` | `HELPFUL`
D) `REREAD`: `optional` | `HELPFUL`
