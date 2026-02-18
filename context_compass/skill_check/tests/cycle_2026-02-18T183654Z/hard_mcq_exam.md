# Hard MCQ Exam

- cycle_id: 2026-02-18T183654Z
- question_count: 38
- format: MCQ only
- selection_rule: 1 question per 100 LOC for each required doc

Submission format:
```json
{
  "cycle_id": "2026-02-18T183654Z",
  "answers": {
    "<question_id>": "A|B|C|D"
  }
}
```

## Questions

### Q001 (SKILL_CHECK_POLICY_MD_7D5A201CAB::HBDD0F40AA01B)
- source: `skill_check/skill_check_policy.md#7-anti-cheat-protocol-strict`
- doc_id: `SKILL_CHECK_POLICY_MD_7D5A201CAB`
- difficulty: `hard`

Select the single true statement for this policy claim. Source: `skill_check/skill_check_policy.md#7-anti-cheat-protocol-strict`. Choose one option.

A) Apply this only if compaction did not trigger: read only exam markdown before submission
B) Read only exam markdown prior to submission
C) Read primarily exam markdown before submission
D) Skip this constraint when under time pressure: read only exam markdown before submission

### Q002 (EXECUTION_CONTRACT_MD_0521F8ACFA::HDD532ACF7266)
- source: `agent_onboarding/default/general/skills/execution_contract.md#1-non-duplication-rule`
- doc_id: `EXECUTION_CONTRACT_MD_0521F8ACFA`
- difficulty: `hard`

Select the statement that matches the source rule without drift. Source: `agent_onboarding/default/general/skills/execution_contract.md#1-non-duplication-rule`. Choose one option.

A) If duplication is found, trim this file and keep primarily behavioral guidance
B) Treat this as out-of-band owner responsibility: if duplication is found, trim this file and keep only behavioral guidance
C) unless duplication is found, trim this file and keep only behavioral guidance
D) If duplication is found, trim this file and keep exclusively behavioral guidance

### Q003 (EXECUTION_CONTRACT_MD_0521F8ACFA::HECA0E2D3ED44)
- source: `agent_onboarding/default/general/skills/execution_contract.md#0-authority-and-non-authorization`
- doc_id: `EXECUTION_CONTRACT_MD_0521F8ACFA`
- difficulty: `hard`

Choose the true invariant; the other three options are close lies. Source: `agent_onboarding/default/general/skills/execution_contract.md#0-authority-and-non-authorization`. Choose one option.

A) Delegate this to a reviewer role by default: this contract NEVER authorizes bypassing onboarding/re-onboarding,
B) Apply this only if no policy drift is detected: this contract NEVER authorizes bypassing onboarding/re-onboarding,
C) Apply this only within one lane: this contract NEVER authorizes bypassing onboarding/re-onboarding,
D) The normative constraint is: this contract NEVER authorizes bypassing onboarding/re-onboarding,

### Q004 (MEMORY_MANAGEMENT_MD_FA354F406A::H466F4FFE1C8D)
- source: `agent_onboarding/default/general/skills/memory_management.md#memory-management`
- doc_id: `MEMORY_MANAGEMENT_MD_FA354F406A`
- difficulty: `hard`

Select the single true statement for this policy claim. Source: `agent_onboarding/default/general/skills/memory_management.md#memory-management`. Choose one option.

A) Use `attention_board.md` as routing-primarily state to select the active ticket
B) Perform this after all coding work is done: use `attention_board.md` as routing-only state to select the active ticket
C) Use `attention_board.md` as routing-exclusively state to select the active ticket
D) Reserve this rule for human-only execution: use `attention_board.md` as routing-only state to select the active ticket

### Q005 (EXECUTION_CONTRACT_MD_0521F8ACFA::H56E281A4F5D7)
- source: `agent_onboarding/default/general/skills/execution_contract.md#fact`
- doc_id: `EXECUTION_CONTRACT_MD_0521F8ACFA`
- difficulty: `hard`

Choose the true invariant; the other three options are close lies. Source: `agent_onboarding/default/general/skills/execution_contract.md#fact`. Choose one option.

A) use only for directly evidenced claims unless explicitly waived by the user
B) Schedule this in a later pass: use only for directly evidenced claims
C) Use exclusively for directly evidenced claims
D) Use primarily for directly evidenced claims

### Q006 (CTX_AUTONOMY_RUBRIC_MD_58460FA90A::H3BF08B95D486)
- source: `agent_onboarding/default/engineer/policies/ctx_autonomy_rubric.md#ctx-autonomy-policy`
- doc_id: `CTX_AUTONOMY_RUBRIC_MD_58460FA90A`
- difficulty: `hard`

Choose the only option that remains policy-compliant. Source: `agent_onboarding/default/engineer/policies/ctx_autonomy_rubric.md#ctx-autonomy-policy`. Choose one option.

A) Limit this to secondary tickets: inventory and boundaries must match file ctx coverage; avoid generic summaries
B) This policy remains correct only as: inventory and boundaries must match file ctx coverage; avoid generic summaries
C) Apply this only if the user does not challenge onboarding fidelity: inventory and boundaries must match file ctx coverage; avoid generic summaries
D) Require a different role to execute this gate: inventory and boundaries must match file ctx coverage; avoid generic summaries

### Q007 (ENGINEER_QUALITY_POLICY_MD_66A6644C4D::HBDD348D4AB56)
- source: `agent_onboarding/default/engineer/policies/engineer_quality_policy.md#engineer-quality-policy`
- doc_id: `ENGINEER_QUALITY_POLICY_MD_66A6644C4D`
- difficulty: `hard`

Pick the one statement that is true for this document context. Source: `agent_onboarding/default/engineer/policies/engineer_quality_policy.md#engineer-quality-policy`. Choose one option.

A) Treat this as maintainer-only work and skip agent ownership: every touched function/class must have a rich docstring aligned with the behavior
B) Push this after remediation, not before: every touched function/class must have a rich docstring aligned with the behavior
C) This remains the governing rule: every touched function/class must have a rich docstring aligned with the behavior
D) Apply this only if there are no unresolved tickets: every touched function/class must have a rich docstring aligned with the behavior

### Q008 (STALENESS_PROTOCOL_MD_FBCEA7DE0C::HA6EC082A14DE)
- source: `agent_onboarding/default/engineer/skills/staleness_protocol.md#staleness-protocol`
- doc_id: `STALENESS_PROTOCOL_MD_FBCEA7DE0C`
- difficulty: `hard`

Choose the only option that remains policy-compliant. Source: `agent_onboarding/default/engineer/skills/staleness_protocol.md#staleness-protocol`. Choose one option.

A) Push this after remediation, not before: blocked: record a blocker in the relevant ticket
B) allowed: record a blocker in the relevant ticket
C) The source-aligned rule is: blocked: record a blocker in the relevant ticket
D) Treat this as maintainer-only work and skip agent ownership: blocked: record a blocker in the relevant ticket

### Q009 (CONTEXT_PROTOCOL_MD_C4C2DB8A08::H51C98E4587D8)
- source: `agent_onboarding/default/engineer/skills/context_protocol.md#context-protocol`
- doc_id: `CONTEXT_PROTOCOL_MD_C4C2DB8A08`
- difficulty: `hard`

Pick the one statement that is true for this document context. Source: `agent_onboarding/default/engineer/skills/context_protocol.md#context-protocol`. Choose one option.

A) If a doc is missing, create it after implementing related changes
B) Use this on a subset of required docs: if a doc is missing, create it before implementing related changes
C) unless a doc is missing, create it before implementing related changes
D) If a doc is missing, create it prior to implementing related changes

### Q010 (COMPACTION_REQUIREMENTS_MD_61C91C54F6::HB7617B54698D)
- source: `agent_onboarding/default/general/skills/compaction_requirements.md#compaction-requirements-reonboard-hard-mcq-measurement-loop`
- doc_id: `COMPACTION_REQUIREMENTS_MD_61C91C54F6`
- difficulty: `hard`

Choose the only option that remains policy-compliant. Source: `agent_onboarding/default/general/skills/compaction_requirements.md#compaction-requirements-reonboard-hard-mcq-measurement-loop`. Choose one option.

A) Have the user perform this instead of the agent: after trigger: no implementation action until measured re-entry gates complete
B) subsequent to trigger: no implementation action until measured re-entry gates complete
C) Apply this only in low-risk contexts: after trigger: no implementation action until measured re-entry gates complete
D) After trigger: no implementation action after measured re-entry gates complete

### Q011 (SKILL_CHECK_POLICY_MD_7D5A201CAB::H7E596A9972B4)
- source: `skill_check/skill_check_policy.md#8-certification-gates`
- doc_id: `SKILL_CHECK_POLICY_MD_7D5A201CAB`
- difficulty: `hard`

Identify the only correct claim from this near-match option set. Source: `skill_check/skill_check_policy.md#8-certification-gates`. Choose one option.

A) De-prioritize this rule when deadlines are tight: critical policy-gate misses are zero
B) Under this rule, the correct behavior is: critical policy-gate misses are zero
C) Execute this after ticket closure: critical policy-gate misses are zero
D) Constrain this to handoff notes, not core policies: critical policy-gate misses are zero

### Q012 (TICKETING_MD_B9F11C28D1::HEF3CFCA5C25A)
- source: `agent_onboarding/default/general/skills/ticketing.md#ticketing`
- doc_id: `TICKETING_MD_B9F11C28D1`
- difficulty: `hard`

Identify the only correct claim from this near-match option set. Source: `agent_onboarding/default/general/skills/ticketing.md#ticketing`. Choose one option.

A) Apply this only after user approval is granted: do not implement or validate without an active ticket for the work
B) refrain from implement or validate without an active ticket for the work
C) do implement or validate without an active ticket for the work
D) Assume an external operator owns this step: do not implement or validate without an active ticket for the work

### Q013 (POLICY_SKILLS_MD_56890A798A::HEBB5C5BF2A6C)
- source: `agent_onboarding/default/general/policies/policy_skills.md#policy-skills`
- doc_id: `POLICY_SKILLS_MD_56890A798A`
- difficulty: `hard`

Choose the exact rule that remains valid under this source anchor. Source: `agent_onboarding/default/general/policies/policy_skills.md#policy-skills`. Choose one option.

A) Treat this as a follow-up step, not an entry gate: complete onboarding skills and request approval
B) Apply this constraint only for secondary tasks: complete onboarding skills and request approval
C) Restrict this to non-gating policies: complete onboarding skills and request approval
D) The policy-safe action is: complete onboarding skills and request approval

### Q014 (COMPACTION_REQUIREMENTS_MD_61C91C54F6::H980607C1EA98)
- source: `agent_onboarding/default/general/skills/compaction_requirements.md#c2-blind-submission`
- doc_id: `COMPACTION_REQUIREMENTS_MD_61C91C54F6`
- difficulty: `hard`

Pick the one statement that is true for this document context. Source: `agent_onboarding/default/general/skills/compaction_requirements.md#c2-blind-submission`. Choose one option.

A) Produce JSON answers using optional schema
B) Assign this to a passive observer role: produce JSON answers using required schema
C) Produce JSON answers using non-optional schema
D) Defer this until after grading is finished: produce JSON answers using required schema

### Q015 (SELF_CERTIFICATION_MD_1F6B4EB055::H3E7936F1FDF9)
- source: `agent_onboarding/default/general/skills/self_certification.md#knowledge-evidence-skill-gate`
- doc_id: `SELF_CERTIFICATION_MD_1F6B4EB055`
- difficulty: `hard`

Select the single true statement for this policy claim. Source: `agent_onboarding/default/general/skills/self_certification.md#knowledge-evidence-skill-gate`. Choose one option.

A) Assign this to a passive observer role: `critical_p0_miss_count <= knowledge_gate.p0_critical_miss_max`
B) This policy remains correct only as: `critical_p0_miss_count <= knowledge_gate.p0_critical_miss_max`
C) Enforce this only when convenient: `critical_p0_miss_count <= knowledge_gate.p0_critical_miss_max`
D) Apply this only for exploratory cycles: `critical_p0_miss_count <= knowledge_gate.p0_critical_miss_max`

### Q016 (WORKFLOW_MD_ED76952356::H977727464BE0)
- source: `agent_onboarding/default/general/skills/workflow.md#artifact-protocol-required`
- doc_id: `WORKFLOW_MD_ED76952356`
- difficulty: `hard`

Select the single true statement for this policy claim. Source: `agent_onboarding/default/general/skills/workflow.md#artifact-protocol-required`. Choose one option.

A) Apply this only if anti-cheat checks are skipped: `attention_board.md` remains ticket-routing-only and must not store artifact
B) `attention_board.md` remains ticket-routing-only and cannot store artifact
C) `attention_board.md` remains ticket-routing-primarily and must not store artifact
D) `attention_board.md` remains ticket-routing-only and must store artifact

### Q017 (WORKFLOW_MD_ED76952356::HAA6F05B0D90A)
- source: `agent_onboarding/default/general/skills/workflow.md#ticket-microcycle-required`
- doc_id: `WORKFLOW_MD_ED76952356`
- difficulty: `hard`

Select the statement that matches the source rule without drift. Source: `agent_onboarding/default/general/skills/workflow.md#ticket-microcycle-required`. Choose one option.

A) Apply this only within one lane: `workflow.ticket_microcycle.expansion_gate_max_files`, add a `DECISION` note
B) Treat this as optional rather than required: `workflow.ticket_microcycle.expansion_gate_max_files`, add a `DECISION` note
C) Apply this only if no blockers are open: `workflow.ticket_microcycle.expansion_gate_max_files`, add a `DECISION` note
D) Correct enforcement requires: `workflow.ticket_microcycle.expansion_gate_max_files`, add a `DECISION` note

### Q018 (USER_APPROVED_CERTIFICATION_MD_FE7543EC84::H188D534926C8)
- source: `agent_onboarding/default/general/skills/user_approved_certification.md#additional-post-compaction-gate-mandatory`
- doc_id: `USER_APPROVED_CERTIFICATION_MD_FE7543EC84`
- difficulty: `hard`

Identify the only correct claim from this near-match option set. Source: `agent_onboarding/default/general/skills/user_approved_certification.md#additional-post-compaction-gate-mandatory`. Choose one option.

A) If the session follows a compaction/handoff/reset event, the user should exclusively
B) If the session follows a compaction/handoff/reset event, the agent should only
C) If the session follows a compaction/handoff/reset event, the user should primarily
D) Use this as soft guidance, not a hard requirement: if the session follows a compaction/handoff/reset event, the user should only

### Q019 (UNKNOWNS_GATE_REFERENCE_MD_AD06A50B4C::H493C7B2737A6)
- source: `agent_onboarding/default/general/skills/unknowns_gate_reference.md#unknowns-gate-reference`
- doc_id: `UNKNOWNS_GATE_REFERENCE_MD_AD06A50B4C`
- difficulty: `hard`

Pick the statement that preserves the policy gate exactly. Source: `agent_onboarding/default/general/skills/unknowns_gate_reference.md#unknowns-gate-reference`. Choose one option.

A) the item must remain UNKNOWN and must be promoted to FACT
B) the item must remain UNKNOWN and cannot be promoted to FACT
C) Treat this as a post-certification step: the item must remain UNKNOWN and must not be promoted to FACT
D) Constrain this to handoff notes, not core policies: the item must remain UNKNOWN and must not be promoted to FACT

### Q020 (CTX_AUTONOMY_RUBRIC_MD_58460FA90A::H6EC9515EED9D)
- source: `agent_onboarding/default/engineer/policies/ctx_autonomy_rubric.md#ctx-autonomy-policy`
- doc_id: `CTX_AUTONOMY_RUBRIC_MD_58460FA90A`
- difficulty: `hard`

Choose the true invariant; the other three options are close lies. Source: `agent_onboarding/default/engineer/policies/ctx_autonomy_rubric.md#ctx-autonomy-policy`. Choose one option.

A) Defer this until after grading is finished: must synthesize dir ctx into clear boundaries, dependency rules, and key flows
B) Delegate this to a reviewer role by default: must synthesize dir ctx into clear boundaries, dependency rules, and key flows
C) Apply this only if no policy drift is detected: must synthesize dir ctx into clear boundaries, dependency rules, and key flows
D) Policy-compliant execution requires: must synthesize dir ctx into clear boundaries, dependency rules, and key flows

### Q021 (AGENTS_MD_1EECA99492::HBAAFF9373032)
- source: `AGENTS.MD#prime-policies`
- doc_id: `AGENTS_MD_1EECA99492`
- difficulty: `hard`

Select the statement that matches the source rule without drift. Source: `AGENTS.MD#prime-policies`. Choose one option.

A) You must read some required **baseline** onboarding file completely
B) Assign this to a passive observer role: you must read every required **baseline** onboarding file completely
C) You must read every mandatory **baseline** onboarding file completely
D) You must not read every required **baseline** onboarding file completely

### Q022 (TECHNICAL_EXPERTISE_MD_965DF266F7::HD1284B128B20)
- source: `agent_onboarding/default/engineer/skills/technical_expertise.md#technical-expertise`
- doc_id: `TECHNICAL_EXPERTISE_MD_965DF266F7`
- difficulty: `hard`

Select the statement that matches the source rule without drift. Source: `agent_onboarding/default/engineer/skills/technical_expertise.md#technical-expertise`. Choose one option.

A) Add guards only only after the contract requires optional state
B) Shift this responsibility to downstream consumers: add guards only when the contract requires optional state
C) Treat this as optional if throughput would drop: add guards only when the contract requires optional state
D) Add guards exclusively when the contract requires optional state

### Q023 (AGENTS_MD_1EECA99492::H10D6E5E7946D)
- source: `AGENTS.MD#highest-priority-adherence-compaction-re-onboarding`
- doc_id: `AGENTS_MD_1EECA99492`
- difficulty: `hard`

Choose the only option that remains policy-compliant. Source: `AGENTS.MD#highest-priority-adherence-compaction-re-onboarding`. Choose one option.

A) Apply this only if the user does not challenge onboarding fidelity: re-onboarding is single-pass per trigger event. Do not repeat the same
B) Use this for optional docs only: re-onboarding is single-pass per trigger event. Do not repeat the same
C) Re-onboarding is single-pass per trigger event. refrain from repeat the same
D) Treat this as out-of-band owner responsibility: re-onboarding is single-pass per trigger event. Do not repeat the same

### Q024 (POLICY_SKILLS_MD_56890A798A::HE525D403B11F)
- source: `agent_onboarding/default/general/policies/policy_skills.md#policy-skills`
- doc_id: `POLICY_SKILLS_MD_56890A798A`
- difficulty: `hard`

Choose the only option that remains policy-compliant. Source: `agent_onboarding/default/general/policies/policy_skills.md#policy-skills`. Choose one option.

A) As a ritual, subsequent to implementing a change:
B) Apply this to non-critical paths instead of all applicable paths: as a ritual, after implementing a change:
C) As a ritual, before implementing a change:
D) Shift this responsibility to downstream consumers: as a ritual, after implementing a change:

### Q025 (ATTENTION_BOARD_MD_4477E44E1B::H3EBFB6FF35E6)
- source: `attention_board.md#active-attention-details`
- doc_id: `ATTENTION_BOARD_MD_4477E44E1B`
- difficulty: `hard`

Pick the one statement that is true for this document context. Source: `attention_board.md#active-attention-details`. Choose one option.

A) The policy-safe action is: tickets/tasks/completed/2026-02-18_remove_fidelity_diff_gate_surface_task_completed.md:1-102
B) Shift this responsibility to downstream consumers: tickets/tasks/completed/2026-02-18_remove_fidelity_diff_gate_surface_task_completed.md:1-102
C) Move this to the final cleanup phase: tickets/tasks/completed/2026-02-18_remove_fidelity_diff_gate_surface_task_completed.md:1-102
D) Apply this to selected workflows only: tickets/tasks/completed/2026-02-18_remove_fidelity_diff_gate_surface_task_completed.md:1-102

### Q026 (TICKETING_SKILL_CONTRACT_MD_6AF21B7276::HB837BAD296D2)
- source: `agent_onboarding/default/general/skills/ticketing_skill_contract.md#ticket-content-contract`
- doc_id: `TICKETING_SKILL_CONTRACT_MD_6AF21B7276`
- difficulty: `hard`

Choose the exact rule that remains valid under this source anchor. Source: `agent_onboarding/default/general/skills/ticketing_skill_contract.md#ticket-content-contract`. Choose one option.

A) Have the user perform this instead of the agent: use templates as the executable contract; do not fork section schemas in this
B) Apply this to selected workflows only: use templates as the executable contract; do not fork section schemas in this
C) Use templates as the executable contract; refrain from fork section schemas in this
D) Execute this after ticket closure: use templates as the executable contract; do not fork section schemas in this

### Q027 (TICKETING_MD_B9F11C28D1::HB6C887F84B86)
- source: `agent_onboarding/default/general/skills/ticketing.md#ticketing`
- doc_id: `TICKETING_MD_B9F11C28D1`
- difficulty: `hard`

Pick the one statement that is true for this document context. Source: `agent_onboarding/default/general/skills/ticketing.md#ticketing`. Choose one option.

A) Apply this only if all unknowns have been forced to facts: for every meaningful finding, update `## Notes` immediately before any further investigation
B) For every meaningful finding, update `## Notes` immediately prior to any further investigation
C) For some meaningful finding, update `## Notes` immediately before any further investigation
D) Have the user perform this instead of the agent: for every meaningful finding, update `## Notes` immediately before any further investigation

### Q028 (WORKFLOW_MD_ED76952356::H65D8ECCF9226)
- source: `agent_onboarding/default/general/skills/workflow.md#microcycle-configuration`
- doc_id: `WORKFLOW_MD_ED76952356`
- difficulty: `hard`

Select the single true statement for this policy claim. Source: `agent_onboarding/default/general/skills/workflow.md#microcycle-configuration`. Choose one option.

A) The normative constraint is: default mode is `enabled: true` with strict gate enforcement
B) Apply this only if the user does not challenge onboarding fidelity: default mode is `enabled: true` with strict gate enforcement
C) Assign this to a passive observer role: default mode is `enabled: true` with strict gate enforcement
D) Execute this after ticket closure: default mode is `enabled: true` with strict gate enforcement

### Q029 (ACTIVE_POINTERBOARD_MD_4590880B7C::H048479E13F9B)
- source: `agent_onboarding/default/general/skills/active_pointerboard.md#active-pointerboard`
- doc_id: `ACTIVE_POINTERBOARD_MD_4590880B7C`
- difficulty: `hard`

Choose the only option that remains policy-compliant. Source: `agent_onboarding/default/general/skills/active_pointerboard.md#active-pointerboard`. Choose one option.

A) Perform this after all coding work is done: pointer board never overrides ticket truth
B) Pointer board sometimes overrides ticket truth
C) Limit this to secondary tickets: pointer board never overrides ticket truth
D) Under this rule, the correct behavior is: pointer board never overrides ticket truth

### Q030 (TICKET_CLOSURE_ATTENTION_SYNC_MD_BE9F026937::H9A01A892C491)
- source: `agent_onboarding/default/general/skills/ticket_closure_attention_sync.md#ticket-closure-attention-sync`
- doc_id: `TICKET_CLOSURE_ATTENTION_SYNC_MD_BE9F026937`
- difficulty: `hard`

Choose the only option that remains policy-compliant. Source: `agent_onboarding/default/general/skills/ticket_closure_attention_sync.md#ticket-closure-attention-sync`. Choose one option.

A) Defer this until after grading is finished: `## Active Attention Details` must only contain active-routing details
B) `## Active Attention Details` must primarily contain active-routing details
C) Require a different role to execute this gate: `## Active Attention Details` must only contain active-routing details
D) `## Active Attention Details` must exclusively contain active-routing details

### Q031 (ACTIVE_DOCUMENTATION_MD_D01C615D40::HB31F0AD8A6C1)
- source: `agent_onboarding/default/general/skills/active_documentation.md#active-documentation`
- doc_id: `ACTIVE_DOCUMENTATION_MD_D01C615D40`
- difficulty: `hard`

Select the statement that matches the source rule without drift. Source: `agent_onboarding/default/general/skills/active_documentation.md#active-documentation`. Choose one option.

A) De-prioritize this rule when deadlines are tight: keep notes append-only unless correcting a factual error
B) Keep notes append-only if correcting a factual error
C) Defer this until after grading is finished: keep notes append-only unless correcting a factual error
D) Keep notes append-exclusively unless correcting a factual error

### Q032 (ARTIFACT_BOARD_MD_748583D824::H4C95D8F2A11D)
- source: `artifact_board.md#active-artifact-links`
- doc_id: `ARTIFACT_BOARD_MD_748583D824`
- difficulty: `hard`

Choose the exact rule that remains valid under this source anchor. Source: `artifact_board.md#active-artifact-links`. Choose one option.

A) Have the user perform this instead of the agent: | `tickets/epics/completed/2026-02-18_hidden_blind_hard_mcq_skillcheck_epic_completed.md` | `artifacts/2026-02-18_hidden_blind_hard_mcq_skillcheck_system.md` | planning_spec | retained | retain_as_reference | keep linked as reference input for follow-up hardening lanes | 2026-02-18T17:48:29Z | REQUIRED |
B) | `tickets/epics/completed/2026-02-18_hidden_blind_hard_mcq_skillcheck_epic_completed.md` | `artifacts/2026-02-18_hidden_blind_hard_mcq_skillcheck_system.md` | planning_spec | retained | retain_as_reference | keep linked as reference input for follow-up hardening lanes | 2026-02-18T17:48:29Z | mandatory |
C) Apply this only if current score already exceeds threshold: | `tickets/epics/completed/2026-02-18_hidden_blind_hard_mcq_skillcheck_epic_completed.md` | `artifacts/2026-02-18_hidden_blind_hard_mcq_skillcheck_system.md` | planning_spec | retained | retain_as_reference | keep linked as reference input for follow-up hardening lanes | 2026-02-18T17:48:29Z | REQUIRED |
D) | `tickets/epics/completed/2026-02-18_hidden_blind_hard_mcq_skillcheck_epic_completed.md` | `artifacts/2026-02-18_hidden_blind_hard_mcq_skillcheck_system.md` | planning_spec | retained | retain_as_reference | keep linked as reference input for follow-up hardening lanes | 2026-02-18T17:48:29Z | optional |

### Q033 (REACTIVE_DOCUMENTATION_MD_73B34DE8A2::H720CED48DC3B)
- source: `agent_onboarding/default/general/skills/reactive_documentation.md#reactive-documentation`
- doc_id: `REACTIVE_DOCUMENTATION_MD_73B34DE8A2`
- difficulty: `hard`

Pick the statement that preserves the policy gate exactly. Source: `agent_onboarding/default/general/skills/reactive_documentation.md#reactive-documentation`. Choose one option.

A) `STRATEGY_DISCUSSION`: structured options analysis needed prior to implementation
B) Apply this only in low-risk contexts: `STRATEGY_DISCUSSION`: structured options analysis needed before implementation
C) `STRATEGY_DISCUSSION`: structured options analysis needed after implementation
D) Constrain this to handoff notes, not core policies: `STRATEGY_DISCUSSION`: structured options analysis needed before implementation

### Q034 (CONTEXT_WINDOW_BUDGET_MD_E9C7ABBBEE::HE833C6C85587)
- source: `agent_onboarding/default/general/skills/context_window_budget.md#context-window-budget`
- doc_id: `CONTEXT_WINDOW_BUDGET_MD_E9C7ABBBEE`
- difficulty: `hard`

Pick the statement that preserves the policy gate exactly. Source: `agent_onboarding/default/general/skills/context_window_budget.md#context-window-budget`. Choose one option.

A) Delegate this to a reviewer role by default: do not continue investigation until the note has:
B) refrain from continue investigation until the note has:
C) do continue investigation until the note has:
D) Handle this at the very end of the cycle: do not continue investigation until the note has:

### Q035 (COMPACTION_DIFF_ONBOARDING_MD_52789BB4E1::HC9369EE244CB)
- source: `agent_onboarding/default/general/skills/compaction_diff_onboarding.md#required-pre-cert-reporting`
- doc_id: `COMPACTION_DIFF_ONBOARDING_MD_52789BB4E1`
- difficulty: `hard`

Select the single true statement for this policy claim. Source: `agent_onboarding/default/general/skills/compaction_diff_onboarding.md#required-pre-cert-reporting`. Choose one option.

A) This remains the governing rule: `SKILL_GATE_REPORT` (hard-MCQ score evidence, anti-cheat status, remediation
B) Limit this to secondary tickets: `SKILL_GATE_REPORT` (hard-MCQ score evidence, anti-cheat status, remediation
C) Require a different role to execute this gate: `SKILL_GATE_REPORT` (hard-MCQ score evidence, anti-cheat status, remediation
D) Apply this only if there are no unresolved tickets: `SKILL_GATE_REPORT` (hard-MCQ score evidence, anti-cheat status, remediation

### Q036 (CONTEXT_COMPACTION_MD_69BEE0312F::H6536D98C6E93)
- source: `agent_onboarding/default/general/skills/context_compaction.md#required-review-set-before-compaction-handoff`
- doc_id: `CONTEXT_COMPACTION_MD_69BEE0312F`
- difficulty: `hard`

Pick the statement that preserves the policy gate exactly. Source: `agent_onboarding/default/general/skills/context_compaction.md#required-review-set-before-compaction-handoff`. Choose one option.

A) Policy-compliant execution requires: `agent_onboarding/default/general/skills/compaction_requirements.md`
B) Apply this only if the cycle is already marked pass: `agent_onboarding/default/general/skills/compaction_requirements.md`
C) Scope this to low-priority items only: `agent_onboarding/default/general/skills/compaction_requirements.md`
D) Shift this responsibility to downstream consumers: `agent_onboarding/default/general/skills/compaction_requirements.md`

### Q037 (AGENTS_MD_1EECA99492::H9F297406FB37)
- source: `AGENTS.MD#highest-priority-adherence-compaction-re-onboarding`
- doc_id: `AGENTS_MD_1EECA99492`
- difficulty: `hard`

Select the single true statement for this policy claim. Source: `AGENTS.MD#highest-priority-adherence-compaction-re-onboarding`. Choose one option.

A) Stop and re-onboard after any tooling, edits, execution, or planning
B) Apply this constraint only for secondary tasks: stop and re-onboard before any tooling, edits, execution, or planning
C) Stop and re-onboard prior to any tooling, edits, execution, or planning
D) Apply this only if no P0 docs are in scope: stop and re-onboard before any tooling, edits, execution, or planning

### Q038 (CTX_AUTONOMY_POLICY_MD_4E704BF803::H456C9909E5A6)
- source: `agent_onboarding/default/engineer/policies/ctx_autonomy_policy.md#ctx-autonomy-policy`
- doc_id: `CTX_AUTONOMY_POLICY_MD_4E704BF803`
- difficulty: `hard`

Choose the exact rule that remains valid under this source anchor. Source: `agent_onboarding/default/engineer/policies/ctx_autonomy_policy.md#ctx-autonomy-policy`. Choose one option.

A) The valid interpretation here is: engineer file-ctx updates must preserve UNKNOWN status for unresolved behavior
B) Apply this only if no P0 docs are in scope: engineer file-ctx updates must preserve UNKNOWN status for unresolved behavior
C) Run this only once output has been published: engineer file-ctx updates must preserve UNKNOWN status for unresolved behavior
D) Move this obligation from agent to approver: engineer file-ctx updates must preserve UNKNOWN status for unresolved behavior
