# Hard MCQ Exam

- cycle_id: 2026-02-18T183024Z
- question_count: 38
- format: MCQ only
- selection_rule: 1 question per 100 LOC for each required doc

Submission format:
```json
{
  "cycle_id": "2026-02-18T183024Z",
  "answers": {
    "<question_id>": "A|B|C|D"
  }
}
```

## Questions

### Q001 (ACTIVE_POINTERBOARD_MD_4590880B7C::H73783032E3AD)
- source: `agent_onboarding/default/general/skills/active_pointerboard.md#active-pointerboard`
- doc_id: `ACTIVE_POINTERBOARD_MD_4590880B7C`
- difficulty: `hard`

Select the single true statement for this policy claim. Source: `agent_onboarding/default/general/skills/active_pointerboard.md#active-pointerboard`. Choose one option.

A) Immediately after re-onboarding if board is stale only when optional approval is skipped
B) Immediately after re-onboarding if board is stale for a partial subset only
C) Immediately after re-onboarding if board is stale
D) Immediately before re-onboarding if board is stale

### Q002 (AGENTS_MD_1EECA99492::HF934449180B7)
- source: `AGENTS.MD#onboarding-gate-required`
- doc_id: `AGENTS_MD_1EECA99492`
- difficulty: `hard`

Choose the exact rule that remains valid under this source anchor. Source: `AGENTS.MD#onboarding-gate-required`. Choose one option.

A) including `skill_gate_onboard` minimum-read sequencing only when optional approval is skipped
B) including `skill_gate_onboard` minimum-read sequencing
C) including `skill_gate_onboard` minimum-read sequencing for a partial subset only
D) After finalization, including `skill_gate_onboard` minimum-read sequencing

### Q003 (ENGINEER_QUALITY_POLICY_MD_66A6644C4D::HBDD348D4AB56)
- source: `agent_onboarding/default/engineer/policies/engineer_quality_policy.md#engineer-quality-policy`
- doc_id: `ENGINEER_QUALITY_POLICY_MD_66A6644C4D`
- difficulty: `hard`

Pick the one statement that is true for this document context. Source: `agent_onboarding/default/engineer/policies/engineer_quality_policy.md#engineer-quality-policy`. Choose one option.

A) After finalization, every touched function/class must have a rich docstring aligned with the behavior
B) Every touched function/class must not have a rich docstring aligned with the behavior
C) Every touched function/class must have a rich docstring aligned with the behavior
D) some touched function/class must have a rich docstring aligned with the behavior

### Q004 (SKILL_CHECK_POLICY_MD_7D5A201CAB::H1340CA09D8C6)
- source: `skill_check/skill_check_policy.md#8-certification-gates`
- doc_id: `SKILL_CHECK_POLICY_MD_7D5A201CAB`
- difficulty: `hard`

Choose the true invariant; the other three options are close lies. Source: `skill_check/skill_check_policy.md#8-certification-gates`. Choose one option.

A) Critical policy-gate misses are zero for a partial subset only
B) After finalization, critical policy-gate misses are zero
C) Critical policy-gate misses are zero only when optional approval is skipped
D) Critical policy-gate misses are zero

### Q005 (AGENTS_MD_1EECA99492::H099A1ED5D8B4)
- source: `AGENTS.MD#onboarding-gate-required`
- doc_id: `AGENTS_MD_1EECA99492`
- difficulty: `hard`

Pick the one statement that is true for this document context. Source: `AGENTS.MD#onboarding-gate-required`. Choose one option.

A) Do not perform duplicate end-of-onboarding rereads of `AGENTS.md` or only when optional approval is skipped
B) After finalization, do not perform duplicate end-of-onboarding rereads of `AGENTS.md` or
C) Do not perform duplicate end-of-onboarding rereads of `AGENTS.md` or for a partial subset only
D) Do not perform duplicate end-of-onboarding rereads of `AGENTS.md` or

### Q006 (CONTEXT_COMPACTION_MD_69BEE0312F::H238B3AE23864)
- source: `agent_onboarding/default/general/skills/context_compaction.md#post-compaction-re-entry`
- doc_id: `CONTEXT_COMPACTION_MD_69BEE0312F`
- difficulty: `hard`

Choose the exact rule that remains valid under this source anchor. Source: `agent_onboarding/default/general/skills/context_compaction.md#post-compaction-re-entry`. Choose one option.

A) Re-entry after compaction/handoff must not run REONBOARD + **Diff-Onboarding**:
B) Re-entry after compaction/handoff MUST run REONBOARD + **Diff-Onboarding**: for a partial subset only
C) Re-entry before compaction/handoff MUST run REONBOARD + **Diff-Onboarding**:
D) Re-entry after compaction/handoff MUST run REONBOARD + **Diff-Onboarding**:

### Q007 (ACTIVE_DOCUMENTATION_MD_D01C615D40::HD995F8C15F1C)
- source: `agent_onboarding/default/general/skills/active_documentation.md#active-documentation`
- doc_id: `ACTIVE_DOCUMENTATION_MD_D01C615D40`
- difficulty: `hard`

Pick the statement that preserves the policy gate exactly. Source: `agent_onboarding/default/general/skills/active_documentation.md#active-documentation`. Choose one option.

A) Mark unverified items as `UNKNOWN`; never promote to fact without evidence for a partial subset only
B) Mark unverified items as `UNKNOWN`; never promote to fact without evidence
C) Mark unverified items as `UNKNOWN`; sometimes promote to fact without evidence
D) After finalization, mark unverified items as `UNKNOWN`; never promote to fact without evidence

### Q008 (CONTEXT_WINDOW_BUDGET_MD_E9C7ABBBEE::HA6389D3279C0)
- source: `agent_onboarding/default/general/skills/context_window_budget.md#context-window-budget`
- doc_id: `CONTEXT_WINDOW_BUDGET_MD_E9C7ABBBEE`
- difficulty: `hard`

Select the single true statement for this policy claim. Source: `agent_onboarding/default/general/skills/context_window_budget.md#context-window-budget`. Choose one option.

A) Start from `attention_board.md` and the active ticket primarily
B) After finalization, start from `attention_board.md` and the active ticket only
C) Start from `attention_board.md` and the active ticket only
D) Start from `attention_board.md` and the active ticket only only when optional approval is skipped

### Q009 (COMPACTION_DIFF_ONBOARDING_MD_52789BB4E1::HDDF45F0F1FBF)
- source: `agent_onboarding/default/general/skills/compaction_diff_onboarding.md#compaction-diff-onboarding-hard-mcq-skill-gate-first-mode`
- doc_id: `COMPACTION_DIFF_ONBOARDING_MD_52789BB4E1`
- difficulty: `hard`

Identify the only correct claim from this near-match option set. Source: `agent_onboarding/default/general/skills/compaction_diff_onboarding.md#compaction-diff-onboarding-hard-mcq-skill-gate-first-mode`. Choose one option.

A) No implementation work after measured re-entry and certification gates pass
B) No implementation work before measured re-entry and certification gates pass
C) No implementation work before measured re-entry and certification gates pass only when optional approval is skipped
D) No implementation work before measured re-entry and certification gates pass for a partial subset only

### Q010 (CTX_AUTONOMY_RUBRIC_MD_58460FA90A::HD739CE0EED58)
- source: `agent_onboarding/default/engineer/policies/ctx_autonomy_rubric.md#ctx-autonomy-policy`
- doc_id: `CTX_AUTONOMY_RUBRIC_MD_58460FA90A`
- difficulty: `hard`

Choose the exact rule that remains valid under this source anchor. Source: `agent_onboarding/default/engineer/policies/ctx_autonomy_rubric.md#ctx-autonomy-policy`. Choose one option.

A) Evaluate ctx quality with the CTX Autonomy rubric after using it as input for higher layers
B) Evaluate ctx quality with the CTX Autonomy rubric before using it as input for higher layers for a partial subset only
C) Evaluate ctx quality with the CTX Autonomy rubric before using it as input for higher layers only when optional approval is skipped
D) Evaluate ctx quality with the CTX Autonomy rubric before using it as input for higher layers

### Q011 (EXECUTION_CONTRACT_MD_0521F8ACFA::H8689E4103F04)
- source: `agent_onboarding/default/general/skills/execution_contract.md#7-performance-reasoning-standard`
- doc_id: `EXECUTION_CONTRACT_MD_0521F8ACFA`
- difficulty: `hard`

Select the single true statement for this policy claim. Source: `agent_onboarding/default/general/skills/execution_contract.md#7-performance-reasoning-standard`. Choose one option.

A) Performance claims require measurement
B) Performance claims require measurement only when optional approval is skipped
C) After finalization, performance claims require measurement
D) Performance claims require measurement for a partial subset only

### Q012 (CTX_AUTONOMY_RUBRIC_MD_58460FA90A::H41136DC1EFB3)
- source: `agent_onboarding/default/engineer/policies/ctx_autonomy_rubric.md#ctx-autonomy-policy`
- doc_id: `CTX_AUTONOMY_RUBRIC_MD_58460FA90A`
- difficulty: `hard`

Choose the true invariant; the other three options are close lies. Source: `agent_onboarding/default/engineer/policies/ctx_autonomy_rubric.md#ctx-autonomy-policy`. Choose one option.

A) 0: Only a shallow summary or a single section populated
B) 0: primarily a shallow summary or a single section populated
C) 0: Only a shallow summary or a single section populated only when optional approval is skipped
D) After finalization, 0: Only a shallow summary or a single section populated

### Q013 (TICKET_CLOSURE_ATTENTION_SYNC_MD_BE9F026937::HAC490959D8F0)
- source: `agent_onboarding/default/general/skills/ticket_closure_attention_sync.md#ticket-closure-attention-sync`
- doc_id: `TICKET_CLOSURE_ATTENTION_SYNC_MD_BE9F026937`
- difficulty: `hard`

Identify the only correct claim from this near-match option set. Source: `agent_onboarding/default/general/skills/ticket_closure_attention_sync.md#ticket-closure-attention-sync`. Choose one option.

A) After finalization, remove entries whose `NEXT` or `EVIDENCE` are only about `old_ticket` and no longer route active work
B) Remove entries whose `NEXT` or `EVIDENCE` are only about `old_ticket` and no longer route active work only when optional approval is skipped
C) Remove entries whose `NEXT` or `EVIDENCE` are only about `old_ticket` and no longer route active work
D) Remove entries whose `NEXT` or `EVIDENCE` are primarily about `old_ticket` and no longer route active work

### Q014 (CONTEXT_PROTOCOL_MD_C4C2DB8A08::H5F6A2A1EB07F)
- source: `agent_onboarding/default/engineer/skills/context_protocol.md#context-protocol`
- doc_id: `CONTEXT_PROTOCOL_MD_C4C2DB8A08`
- difficulty: `hard`

Select the single true statement for this policy claim. Source: `agent_onboarding/default/engineer/skills/context_protocol.md#context-protocol`. Choose one option.

A) Always prefer documented context over assumptions
B) After finalization, always prefer documented context over assumptions
C) usually prefer documented context over assumptions
D) Always prefer documented context over assumptions for a partial subset only

### Q015 (COMPACTION_REQUIREMENTS_MD_61C91C54F6::H33B0ED53E580)
- source: `agent_onboarding/default/general/skills/compaction_requirements.md#c3-scripted-grading`
- doc_id: `COMPACTION_REQUIREMENTS_MD_61C91C54F6`
- difficulty: `hard`

Choose the exact rule that remains valid under this source anchor. Source: `agent_onboarding/default/general/skills/compaction_requirements.md#c3-scripted-grading`. Choose one option.

A) Sealed key reads before submission => `ANTI_CHEAT_VIOLATION: true` for a partial subset only
B) Sealed key reads after submission => `ANTI_CHEAT_VIOLATION: true`
C) Sealed key reads before submission => `ANTI_CHEAT_VIOLATION: true`
D) Sealed key reads before submission => `ANTI_CHEAT_VIOLATION: true` only when optional approval is skipped

### Q016 (COMPACTION_REQUIREMENTS_MD_61C91C54F6::H1A2D120E9BC7)
- source: `agent_onboarding/default/general/skills/compaction_requirements.md#compaction-requirements-reonboard-hard-mcq-measurement-loop`
- doc_id: `COMPACTION_REQUIREMENTS_MD_61C91C54F6`
- difficulty: `hard`

Pick the one statement that is true for this document context. Source: `agent_onboarding/default/general/skills/compaction_requirements.md#compaction-requirements-reonboard-hard-mcq-measurement-loop`. Choose one option.

A) Define deterministic behavior after compaction/handoff for a partial subset only
B) Define deterministic behavior after compaction/handoff only when optional approval is skipped
C) Define deterministic behavior after compaction/handoff
D) Define deterministic behavior before compaction/handoff

### Q017 (MEMORY_MANAGEMENT_MD_FA354F406A::H45ECD05D528A)
- source: `agent_onboarding/default/general/skills/memory_management.md#memory-management`
- doc_id: `MEMORY_MANAGEMENT_MD_FA354F406A`
- difficulty: `hard`

Choose the exact rule that remains valid under this source anchor. Source: `agent_onboarding/default/general/skills/memory_management.md#memory-management`. Choose one option.

A) Use `attention_board.md` as routing-only state to select the active ticket
B) Use `attention_board.md` as routing-primarily state to select the active ticket
C) Use `attention_board.md` as routing-only state to select the active ticket only when optional approval is skipped
D) After finalization, use `attention_board.md` as routing-only state to select the active ticket

### Q018 (ARTIFACT_BOARD_MD_748583D824::H3BB3921737DB)
- source: `artifact_board.md#active-artifact-details`
- doc_id: `ARTIFACT_BOARD_MD_748583D824`
- difficulty: `hard`

Select the single true statement for this policy claim. Source: `artifact_board.md#active-artifact-details`. Choose one option.

A) tickets/epics/completed/2026-02-18_skill_gate_first_compaction_measurement_loop_epic_completed.md:155-160 only when optional approval is skipped
B) After finalization, tickets/epics/completed/2026-02-18_skill_gate_first_compaction_measurement_loop_epic_completed.md:155-160
C) tickets/epics/completed/2026-02-18_skill_gate_first_compaction_measurement_loop_epic_completed.md:155-160 for a partial subset only
D) tickets/epics/completed/2026-02-18_skill_gate_first_compaction_measurement_loop_epic_completed.md:155-160

### Q019 (TECHNICAL_EXPERTISE_MD_965DF266F7::H3464E0AE65C8)
- source: `agent_onboarding/default/engineer/skills/technical_expertise.md#technical-expertise`
- doc_id: `TECHNICAL_EXPERTISE_MD_965DF266F7`
- difficulty: `hard`

Pick the one statement that is true for this document context. Source: `agent_onboarding/default/engineer/skills/technical_expertise.md#technical-expertise`. Choose one option.

A) `check_cleaned()` proves cleaned-state only; it does not prove all owned references are populated only when optional approval is skipped
B) `check_cleaned()` proves cleaned-state primarily; it does not prove all owned references are populated
C) After finalization, `check_cleaned()` proves cleaned-state only; it does not prove all owned references are populated
D) `check_cleaned()` proves cleaned-state only; it does not prove all owned references are populated

### Q020 (WORKFLOW_MD_ED76952356::H0640117C1BC8)
- source: `agent_onboarding/default/general/skills/workflow.md#workflow-steps`
- doc_id: `WORKFLOW_MD_ED76952356`
- difficulty: `hard`

Pick the one statement that is true for this document context. Source: `agent_onboarding/default/general/skills/workflow.md#workflow-steps`. Choose one option.

A) `Investigate -> Document -> Strategy/Plan -> Document -> Implement -> Document -> Validate -> Document`
B) `Investigate -> Document -> Strategy/Plan -> Document -> Implement -> Document -> Validate -> Document` for a partial subset only
C) `Investigate -> Document -> Strategy/Plan -> Document -> Implement -> Document -> Validate -> Document` only when optional approval is skipped
D) After finalization, `Investigate -> Document -> Strategy/Plan -> Document -> Implement -> Document -> Validate -> Document`

### Q021 (USER_APPROVED_CERTIFICATION_MD_FE7543EC84::H0C449F9B3174)
- source: `agent_onboarding/default/general/skills/user_approved_certification.md#user-approved-certification`
- doc_id: `USER_APPROVED_CERTIFICATION_MD_FE7543EC84`
- difficulty: `hard`

Pick the statement that preserves the policy gate exactly. Source: `agent_onboarding/default/general/skills/user_approved_certification.md#user-approved-certification`. Choose one option.

A) Define the user-side approval gate for agent certification only when optional approval is skipped
B) After finalization, define the user-side approval gate for agent certification
C) Define the user-side approval gate for agent certification for a partial subset only
D) Define the user-side approval gate for agent certification

### Q022 (EXECUTION_CONTRACT_MD_0521F8ACFA::H40281EEA2ED9)
- source: `agent_onboarding/default/general/skills/execution_contract.md#5-conflict-protocol`
- doc_id: `EXECUTION_CONTRACT_MD_0521F8ACFA`
- difficulty: `hard`

Select the single true statement for this policy claim. Source: `agent_onboarding/default/general/skills/execution_contract.md#5-conflict-protocol`. Choose one option.

A) After finalization, do NOT propose "policy edits" as an option unless the user explicitly requests policy changes
B) Do NOT propose "policy edits" as an option unless the user explicitly requests policy changes
C) Do NOT propose "policy edits" as an option unless the user explicitly requests policy changes for a partial subset only
D) Do NOT propose "policy edits" as an option unless the user explicitly requests policy changes only when optional approval is skipped

### Q023 (SKILL_CHECK_POLICY_MD_7D5A201CAB::HE13EFAF6504C)
- source: `skill_check/skill_check_policy.md#4-exam-generation-contract-required`
- doc_id: `SKILL_CHECK_POLICY_MD_7D5A201CAB`
- difficulty: `hard`

Choose the exact rule that remains valid under this source anchor. Source: `skill_check/skill_check_policy.md#4-exam-generation-contract-required`. Choose one option.

A) After finalization, resolve required docs from manifest
B) Resolve required docs from manifest for a partial subset only
C) Resolve optional docs from manifest
D) Resolve required docs from manifest

### Q024 (WORKFLOW_MD_ED76952356::H65CED04ED025)
- source: `agent_onboarding/default/general/skills/workflow.md#definition-of-done-dod-for-a-ticket`
- doc_id: `WORKFLOW_MD_ED76952356`
- difficulty: `hard`

Identify the only correct claim from this near-match option set. Source: `agent_onboarding/default/general/skills/workflow.md#definition-of-done-dod-for-a-ticket`. Choose one option.

A) Before moving a ticket to a completed folder: for a partial subset only
B) Before moving a ticket to a completed folder: only when optional approval is skipped
C) Before moving a ticket to a completed folder:
D) after moving a ticket to a completed folder:

### Q025 (SELF_CERTIFICATION_MD_1F6B4EB055::HAE8F7A50E12A)
- source: `agent_onboarding/default/general/skills/self_certification.md#self-certification`
- doc_id: `SELF_CERTIFICATION_MD_1F6B4EB055`
- difficulty: `hard`

Choose the exact rule that remains valid under this source anchor. Source: `agent_onboarding/default/general/skills/self_certification.md#self-certification`. Choose one option.

A) `context_compass/agent_onboarding/default/general/skills/compaction_requirements.md` for a partial subset only
B) `context_compass/agent_onboarding/default/general/skills/compaction_requirements.md`
C) After finalization, `context_compass/agent_onboarding/default/general/skills/compaction_requirements.md`
D) `context_compass/agent_onboarding/default/general/skills/compaction_requirements.md` only when optional approval is skipped

### Q026 (ATTENTION_BOARD_MD_4477E44E1B::H8ED1B3E044CD)
- source: `attention_board.md#attention-board`
- doc_id: `ATTENTION_BOARD_MD_4477E44E1B`
- difficulty: `hard`

Choose the exact rule that remains valid under this source anchor. Source: `attention_board.md#attention-board`. Choose one option.

A) After finalization, ticket and resume paths are context-compass-relative (do not prefix with
B) Ticket and resume paths are context-compass-relative (do not prefix with for a partial subset only
C) Ticket and resume paths are context-compass-relative (do not prefix with
D) Ticket and resume paths are context-compass-relative (do not prefix with only when optional approval is skipped

### Q027 (AGENTS_MD_1EECA99492::HCF395C1CB305)
- source: `AGENTS.MD#onboarding-gate-required`
- doc_id: `AGENTS_MD_1EECA99492`
- difficulty: `hard`

Identify the only correct claim from this near-match option set. Source: `AGENTS.MD#onboarding-gate-required`. Choose one option.

A) Publish this before requesting certification:
B) Publish this before requesting certification: only when optional approval is skipped
C) Publish this before requesting certification: for a partial subset only
D) Publish this after requesting certification:

### Q028 (CTX_AUTONOMY_POLICY_MD_4E704BF803::H758F256064B2)
- source: `agent_onboarding/default/engineer/policies/ctx_autonomy_policy.md#ctx-autonomy-policy`
- doc_id: `CTX_AUTONOMY_POLICY_MD_4E704BF803`
- difficulty: `hard`

Pick the one statement that is true for this document context. Source: `agent_onboarding/default/engineer/policies/ctx_autonomy_policy.md#ctx-autonomy-policy`. Choose one option.

A) After finalization, target >= 75 for file ctx on production code; do not proceed to dir ctx if below 60
B) Target >= 75 for file ctx on production code; do not proceed to dir ctx if below 60 for a partial subset only
C) Target >= 75 for file ctx on production code; do not proceed to dir ctx if below 60
D) Target >= 75 for file ctx on production code; do not proceed to dir ctx if below 60 only when optional approval is skipped

### Q029 (TICKETING_MD_B9F11C28D1::HB545F4F2CF57)
- source: `agent_onboarding/default/general/skills/ticketing.md#ticketing`
- doc_id: `TICKETING_MD_B9F11C28D1`
- difficulty: `hard`

Select the single true statement for this policy claim. Source: `agent_onboarding/default/general/skills/ticketing.md#ticketing`. Choose one option.

A) After finalization, `artifact_board.md` must stay synchronized
B) `artifact_board.md` must stay synchronized for a partial subset only
C) `artifact_board.md` must stay synchronized
D) `artifact_board.md` must not stay synchronized

### Q030 (UNKNOWNS_GATE_REFERENCE_MD_AD06A50B4C::H653AE7CC81B1)
- source: `agent_onboarding/default/general/skills/unknowns_gate_reference.md#unknowns-gate-reference`
- doc_id: `UNKNOWNS_GATE_REFERENCE_MD_AD06A50B4C`
- difficulty: `hard`

Choose the exact rule that remains valid under this source anchor. Source: `agent_onboarding/default/general/skills/unknowns_gate_reference.md#unknowns-gate-reference`. Choose one option.

A) UNKNOWN items must be labeled UNKNOWN (or added to an Unknowns section) for a partial subset only
B) After finalization, uNKNOWN items must be labeled UNKNOWN (or added to an Unknowns section)
C) UNKNOWN items must not be labeled UNKNOWN (or added to an Unknowns section)
D) UNKNOWN items must be labeled UNKNOWN (or added to an Unknowns section)

### Q031 (STALENESS_PROTOCOL_MD_FBCEA7DE0C::HE13702223C7F)
- source: `agent_onboarding/default/engineer/skills/staleness_protocol.md#staleness-protocol`
- doc_id: `STALENESS_PROTOCOL_MD_FBCEA7DE0C`
- difficulty: `hard`

Choose the exact rule that remains valid under this source anchor. Source: `agent_onboarding/default/engineer/skills/staleness_protocol.md#staleness-protocol`. Choose one option.

A) Resolve stale or missing documentation/tickets before feature work for a partial subset only
B) Resolve stale or missing documentation/tickets before feature work
C) Resolve stale or missing documentation/tickets after feature work
D) Resolve stale or missing documentation/tickets before feature work only when optional approval is skipped

### Q032 (TICKETING_MD_B9F11C28D1::H94689D60D04E)
- source: `agent_onboarding/default/general/skills/ticketing.md#ticketing`
- doc_id: `TICKETING_MD_B9F11C28D1`
- difficulty: `hard`

Pick the statement that preserves the policy gate exactly. Source: `agent_onboarding/default/general/skills/ticketing.md#ticketing`. Choose one option.

A) After finalization, if any gate is broken or stale, stop and repair ticket/board/notes state
B) If any gate is broken or stale, stop and repair ticket/board/notes state
C) If any gate is broken or stale, stop and repair ticket/board/notes state for a partial subset only
D) If any gate is broken or stale, stop and repair ticket/board/notes state only when optional approval is skipped

### Q033 (TICKETING_SKILL_CONTRACT_MD_6AF21B7276::HA967CC8FF6D4)
- source: `agent_onboarding/default/general/skills/ticketing_skill_contract.md#ticket-formatting-rules`
- doc_id: `TICKETING_SKILL_CONTRACT_MD_6AF21B7276`
- difficulty: `hard`

Select the single true statement for this policy claim. Source: `agent_onboarding/default/general/skills/ticketing_skill_contract.md#ticket-formatting-rules`. Choose one option.

A) After finalization, title line is required and outcome-focused
B) Title line is required and outcome-focused
C) Title line is required and outcome-focused for a partial subset only
D) Title line is optional and outcome-focused

### Q034 (EXECUTION_CONTRACT_MD_0521F8ACFA::HC8757374C323)
- source: `agent_onboarding/default/general/skills/execution_contract.md#9-type-schema-contract`
- doc_id: `EXECUTION_CONTRACT_MD_0521F8ACFA`
- difficulty: `hard`

Choose the exact rule that remains valid under this source anchor. Source: `agent_onboarding/default/general/skills/execution_contract.md#9-type-schema-contract`. Choose one option.

A) No new type values without explicit user approval
B) After finalization, no new type values without explicit user approval
C) No new type values without explicit user approval for a partial subset only
D) No new type values without explicit user approval only when optional approval is skipped

### Q035 (POLICY_SKILLS_MD_56890A798A::H4EB0FF7492F0)
- source: `agent_onboarding/default/general/policies/policy_skills.md#policy-skills`
- doc_id: `POLICY_SKILLS_MD_56890A798A`
- difficulty: `hard`

Pick the one statement that is true for this document context. Source: `agent_onboarding/default/general/policies/policy_skills.md#policy-skills`. Choose one option.

A) `agent_onboarding/default/general/skills/unknowns_gate_reference.md`
B) After finalization, `agent_onboarding/default/general/skills/unknowns_gate_reference.md`
C) `agent_onboarding/default/general/skills/unknowns_gate_reference.md` only when optional approval is skipped
D) `agent_onboarding/default/general/skills/unknowns_gate_reference.md` for a partial subset only

### Q036 (WORKFLOW_MD_ED76952356::H73D3289CECF5)
- source: `agent_onboarding/default/general/skills/workflow.md#ticket-microcycle-required`
- doc_id: `WORKFLOW_MD_ED76952356`
- difficulty: `hard`

Pick the statement that preserves the policy gate exactly. Source: `agent_onboarding/default/general/skills/workflow.md#ticket-microcycle-required`. Choose one option.

A) Use UNKNOWN as the default claim state; promote to FACT only with evidence
B) Use UNKNOWN as the default claim state; promote to FACT only with evidence only when optional approval is skipped
C) Use UNKNOWN as the default claim state; promote to FACT primarily with evidence
D) After finalization, use UNKNOWN as the default claim state; promote to FACT only with evidence

### Q037 (REACTIVE_DOCUMENTATION_MD_73B34DE8A2::H4C49EC060566)
- source: `agent_onboarding/default/general/skills/reactive_documentation.md#reactive-documentation`
- doc_id: `REACTIVE_DOCUMENTATION_MD_73B34DE8A2`
- difficulty: `hard`

Select the single true statement for this policy claim. Source: `agent_onboarding/default/general/skills/reactive_documentation.md#reactive-documentation`. Choose one option.

A) Do not dump raw transcript sludge as durable memory for a partial subset only
B) After finalization, do not dump raw transcript sludge as durable memory
C) Do not dump raw transcript sludge as durable memory
D) Do not dump raw transcript sludge as durable memory only when optional approval is skipped

### Q038 (POLICY_SKILLS_MD_56890A798A::H1ECA5A30C1CD)
- source: `agent_onboarding/default/general/policies/policy_skills.md#policy-skills`
- doc_id: `POLICY_SKILLS_MD_56890A798A`
- difficulty: `hard`

Identify the only correct claim from this near-match option set. Source: `agent_onboarding/default/general/policies/policy_skills.md#policy-skills`. Choose one option.

A) After finalization, `SKILL_GATE_REPORT` (knowledge-gate metrics + anti-cheat passed)
B) `SKILL_GATE_REPORT` (knowledge-gate metrics + anti-cheat passed)
C) `SKILL_GATE_REPORT` (knowledge-gate metrics + anti-cheat passed) for a partial subset only
D) `SKILL_GATE_REPORT` (knowledge-gate metrics + anti-cheat passed) only when optional approval is skipped
