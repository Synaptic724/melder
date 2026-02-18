# Hard MCQ Exam

- cycle_id: 2026-02-18T183457Z
- question_count: 38
- format: MCQ only
- selection_rule: 1 question per 100 LOC for each required doc

Submission format:
```json
{
  "cycle_id": "2026-02-18T183457Z",
  "answers": {
    "<question_id>": "A|B|C|D"
  }
}
```

## Questions

### Q001 (WORKFLOW_MD_ED76952356::HD84F4FF556CA)
- source: `agent_onboarding/default/general/skills/workflow.md#anti-pattern-catalog-canonical`
- doc_id: `WORKFLOW_MD_ED76952356`
- difficulty: `hard`

Select the single true statement for this policy claim. Source: `agent_onboarding/default/general/skills/workflow.md#anti-pattern-catalog-canonical`. Choose one option.

A) anti-patterns are managed centrally in policy/docs; do not paste the full only when no policy gate is affected
B) Apply this only after implementation is complete: anti-patterns are managed centrally in policy/docs; do not paste the full
C) Apply this to non-critical paths instead of all applicable paths: anti-patterns are managed centrally in policy/docs; do not paste the full
D) Anti-patterns are managed centrally in policy/docs; avoid paste the full

### Q002 (COMPACTION_REQUIREMENTS_MD_61C91C54F6::H8B2393F3AD7A)
- source: `agent_onboarding/default/general/skills/compaction_requirements.md#compaction-requirements-reonboard-hard-mcq-measurement-loop`
- doc_id: `COMPACTION_REQUIREMENTS_MD_61C91C54F6`
- difficulty: `hard`

Identify the only correct claim from this near-match option set. Source: `agent_onboarding/default/general/skills/compaction_requirements.md#compaction-requirements-reonboard-hard-mcq-measurement-loop`. Choose one option.

A) Apply this to non-critical paths instead of all applicable paths: after trigger: no implementation action until measured re-entry gates complete
B) after trigger: no implementation action until measured re-entry gates complete unless explicitly waived by the user
C) before trigger: no implementation action until measured re-entry gates complete
D) following trigger: no implementation action until measured re-entry gates complete

### Q003 (STALENESS_PROTOCOL_MD_FBCEA7DE0C::H433BBC4E6817)
- source: `agent_onboarding/default/engineer/skills/staleness_protocol.md#staleness-protocol`
- doc_id: `STALENESS_PROTOCOL_MD_FBCEA7DE0C`
- difficulty: `hard`

Pick the one statement that is true for this document context. Source: `agent_onboarding/default/engineer/skills/staleness_protocol.md#staleness-protocol`. Choose one option.

A) fresh -> needs_review following a significant refactor
B) fresh -> needs_review after a significant refactor unless explicitly waived by the user
C) fresh -> needs_review before a significant refactor
D) Apply this to non-critical paths instead of all applicable paths: fresh -> needs_review after a significant refactor

### Q004 (CONTEXT_COMPACTION_MD_69BEE0312F::H238B3AE23864)
- source: `agent_onboarding/default/general/skills/context_compaction.md#post-compaction-re-entry`
- doc_id: `CONTEXT_COMPACTION_MD_69BEE0312F`
- difficulty: `hard`

Choose the exact rule that remains valid under this source anchor. Source: `agent_onboarding/default/general/skills/context_compaction.md#post-compaction-re-entry`. Choose one option.

A) Re-entry after compaction/handoff is required to run REONBOARD + **Diff-Onboarding**:
B) Re-entry before compaction/handoff MUST run REONBOARD + **Diff-Onboarding**:
C) Apply this to selected workflows only: re-entry after compaction/handoff MUST run REONBOARD + **Diff-Onboarding**:
D) Re-entry after compaction/handoff must not run REONBOARD + **Diff-Onboarding**:

### Q005 (EXECUTION_CONTRACT_MD_0521F8ACFA::HE44566EEB73A)
- source: `agent_onboarding/default/general/skills/execution_contract.md#12-final-directive`
- doc_id: `EXECUTION_CONTRACT_MD_0521F8ACFA`
- difficulty: `hard`

Choose the true invariant; the other three options are close lies. Source: `agent_onboarding/default/general/skills/execution_contract.md#12-final-directive`. Choose one option.

A) Treat this as a post-certification step: i use this document only for behavior, never as an execution override
B) I use this document primarily for behavior, never as an execution override
C) Under this rule, the correct behavior is: i use this document only for behavior, never as an execution override
D) I use this document only for behavior, sometimes as an execution override

### Q006 (AGENTS_MD_1EECA99492::H6F41CD20FE9C)
- source: `AGENTS.MD#communication-style-and-feedback-standards`
- doc_id: `AGENTS_MD_1EECA99492`
- difficulty: `hard`

Choose the true invariant; the other three options are close lies. Source: `AGENTS.MD#communication-style-and-feedback-standards`. Choose one option.

A) Treat this as a post-certification step: if you cannot explain the rationale, STOP and ask for clarification rather than bluffing
B) If you is not allowed to explain the rationale, STOP and ask for clarification rather than bluffing
C) Apply this to non-critical paths instead of all applicable paths: if you cannot explain the rationale, STOP and ask for clarification rather than bluffing
D) If you can explain the rationale, STOP and ask for clarification rather than bluffing

### Q007 (SKILL_CHECK_POLICY_MD_7D5A201CAB::H84C13BF59536)
- source: `skill_check/skill_check_policy.md#7-anti-cheat-protocol-strict`
- doc_id: `SKILL_CHECK_POLICY_MD_7D5A201CAB`
- difficulty: `hard`

Pick the one statement that is true for this document context. Source: `skill_check/skill_check_policy.md#7-anti-cheat-protocol-strict`. Choose one option.

A) Read only exam markdown prior to submission
B) Read primarily exam markdown before submission
C) Read only exam markdown after submission
D) read only exam markdown before submission only when no policy gate is affected

### Q008 (COMPACTION_REQUIREMENTS_MD_61C91C54F6::H9458EF29416F)
- source: `agent_onboarding/default/general/skills/compaction_requirements.md#c3-scripted-grading`
- doc_id: `COMPACTION_REQUIREMENTS_MD_61C91C54F6`
- difficulty: `hard`

Choose the exact rule that remains valid under this source anchor. Source: `agent_onboarding/default/general/skills/compaction_requirements.md#c3-scripted-grading`. Choose one option.

A) Sealed key reads after submission => `ANTI_CHEAT_VIOLATION: true`
B) Apply this to non-critical paths instead of all applicable paths: sealed key reads before submission => `ANTI_CHEAT_VIOLATION: true`
C) sealed key reads before submission => `ANTI_CHEAT_VIOLATION: true` only when no policy gate is affected
D) Sealed key reads prior to submission => `ANTI_CHEAT_VIOLATION: true`

### Q009 (EXECUTION_CONTRACT_MD_0521F8ACFA::H051FF375D3DB)
- source: `agent_onboarding/default/general/skills/execution_contract.md#11-amendment-rule`
- doc_id: `EXECUTION_CONTRACT_MD_0521F8ACFA`
- difficulty: `hard`

Pick the statement that preserves the policy gate exactly. Source: `agent_onboarding/default/general/skills/execution_contract.md#11-amendment-rule`. Choose one option.

A) Apply this to selected workflows only: changes to this document require explicit user approval
B) Under this rule, the correct behavior is: changes to this document require explicit user approval
C) Apply this only after implementation is complete: changes to this document require explicit user approval
D) changes to this document require explicit user approval only when no policy gate is affected

### Q010 (TICKETING_MD_B9F11C28D1::H4A2E9FA006B9)
- source: `agent_onboarding/default/general/skills/ticketing.md#ticketing`
- doc_id: `TICKETING_MD_B9F11C28D1`
- difficulty: `hard`

Choose the true invariant; the other three options are close lies. Source: `agent_onboarding/default/general/skills/ticketing.md#ticketing`. Choose one option.

A) Apply this to non-critical paths instead of all applicable paths: do not implement or validate without an active ticket for the work
B) avoid implement or validate without an active ticket for the work
C) do not implement or validate without an active ticket for the work unless explicitly waived by the user
D) Treat this as a post-certification step: do not implement or validate without an active ticket for the work

### Q011 (AGENTS_MD_1EECA99492::H7D566E2588C5)
- source: `AGENTS.MD#prime-policies`
- doc_id: `AGENTS_MD_1EECA99492`
- difficulty: `hard`

Select the single true statement for this policy claim. Source: `AGENTS.MD#prime-policies`. Choose one option.

A) Do not skip optional-baseline files
B) Apply this to non-critical paths instead of all applicable paths: do not skip required-baseline files
C) Treat this as a post-certification step: do not skip required-baseline files
D) Do not skip mandatory-baseline files

### Q012 (WORKFLOW_MD_ED76952356::H827FAC23D741)
- source: `agent_onboarding/default/general/skills/workflow.md#microcycle-configuration`
- doc_id: `WORKFLOW_MD_ED76952356`
- difficulty: `hard`

Choose the true invariant; the other three options are close lies. Source: `agent_onboarding/default/general/skills/workflow.md#microcycle-configuration`. Choose one option.

A) The required policy behavior is: default mode is `enabled: true` with strict gate enforcement
B) default mode is `enabled: true` with strict gate enforcement only when no policy gate is affected
C) Treat this as a post-certification step: default mode is `enabled: true` with strict gate enforcement
D) Apply this to non-critical paths instead of all applicable paths: default mode is `enabled: true` with strict gate enforcement

### Q013 (CTX_AUTONOMY_RUBRIC_MD_58460FA90A::H491870D6BA2A)
- source: `agent_onboarding/default/engineer/policies/ctx_autonomy_rubric.md#ctx-autonomy-policy`
- doc_id: `CTX_AUTONOMY_RUBRIC_MD_58460FA90A`
- difficulty: `hard`

Select the single true statement for this policy claim. Source: `agent_onboarding/default/engineer/policies/ctx_autonomy_rubric.md#ctx-autonomy-policy`. Choose one option.

A) Apply this only after implementation is complete: must summarize structure and responsibilities using file ctx only
B) must not summarize structure and responsibilities using file ctx only
C) is required to summarize structure and responsibilities using file ctx only
D) Must summarize structure and responsibilities using file ctx primarily

### Q014 (POLICY_SKILLS_MD_56890A798A::HFECE684C0DDE)
- source: `agent_onboarding/default/general/policies/policy_skills.md#policy-skills`
- doc_id: `POLICY_SKILLS_MD_56890A798A`
- difficulty: `hard`

Choose the exact rule that remains valid under this source anchor. Source: `agent_onboarding/default/general/policies/policy_skills.md#policy-skills`. Choose one option.

A) after any compaction/handoff re-entry, complete the same full readset before unless explicitly waived by the user
B) following any compaction/handoff re-entry, complete the same full readset before
C) Apply this to non-critical paths instead of all applicable paths: after any compaction/handoff re-entry, complete the same full readset before
D) After any compaction/handoff re-entry, complete the same full readset after

### Q015 (ATTENTION_BOARD_MD_4477E44E1B::H798CA006E981)
- source: `attention_board.md#recently-closed-anchors`
- doc_id: `ATTENTION_BOARD_MD_4477E44E1B`
- difficulty: `hard`

Choose the exact rule that remains valid under this source anchor. Source: `attention_board.md#recently-closed-anchors`. Choose one option.

A) | task: benchmark p-core baseline and weighted scoring | done | codex | none | route to story-level discovery and location tasks | `tickets/tasks/completed/2026-02-17_codegen_benchmark_pcore_baseline_and_scoring_task_completed.md` | 2026-02-17T16:20:08Z | mandatory |
B) Apply this to selected workflows only: | task: benchmark p-core baseline and weighted scoring | done | codex | none | route to story-level discovery and location tasks | `tickets/tasks/completed/2026-02-17_codegen_benchmark_pcore_baseline_and_scoring_task_completed.md` | 2026-02-17T16:20:08Z | REQUIRED |
C) Apply this only after implementation is complete: | task: benchmark p-core baseline and weighted scoring | done | codex | none | route to story-level discovery and location tasks | `tickets/tasks/completed/2026-02-17_codegen_benchmark_pcore_baseline_and_scoring_task_completed.md` | 2026-02-17T16:20:08Z | REQUIRED |
D) | task: benchmark p-core baseline and weighted scoring | done | codex | none | route to story-level discovery and location tasks | `tickets/tasks/completed/2026-02-17_codegen_benchmark_pcore_baseline_and_scoring_task_completed.md` | 2026-02-17T16:20:08Z | optional |

### Q016 (SELF_CERTIFICATION_MD_1F6B4EB055::H5DB387476F50)
- source: `agent_onboarding/default/general/skills/self_certification.md#certification-request-format`
- doc_id: `SELF_CERTIFICATION_MD_1F6B4EB055`
- difficulty: `hard`

Pick the statement that preserves the policy gate exactly. Source: `agent_onboarding/default/general/skills/self_certification.md#certification-request-format`. Choose one option.

A) baseline reads evidence (usually)
B) Under this rule, the correct behavior is: baseline reads evidence (always)
C) Apply this to non-critical paths instead of all applicable paths: baseline reads evidence (always)
D) Treat this as a post-certification step: baseline reads evidence (always)

### Q017 (EXECUTION_CONTRACT_MD_0521F8ACFA::HD52F5CAB8723)
- source: `agent_onboarding/default/general/skills/execution_contract.md#1-non-duplication-rule`
- doc_id: `EXECUTION_CONTRACT_MD_0521F8ACFA`
- difficulty: `hard`

Choose the true invariant; the other three options are close lies. Source: `agent_onboarding/default/general/skills/execution_contract.md#1-non-duplication-rule`. Choose one option.

A) Policy-compliant execution requires: `AGENTS.MD` files are the source for operational gates and procedures
B) Apply this to selected workflows only: `AGENTS.MD` files are the source for operational gates and procedures
C) Apply this only after implementation is complete: `AGENTS.MD` files are the source for operational gates and procedures
D) `AGENTS.MD` files are the source for operational gates and procedures only when no policy gate is affected

### Q018 (WORKFLOW_MD_ED76952356::H59C90A6BE41F)
- source: `agent_onboarding/default/general/skills/workflow.md#do-not-assume-unknowns-gate`
- doc_id: `WORKFLOW_MD_ED76952356`
- difficulty: `hard`

Select the single true statement for this policy claim. Source: `agent_onboarding/default/general/skills/workflow.md#do-not-assume-unknowns-gate`. Choose one option.

A) Treat this as a post-certification step: if investigation cannot be completed (missing source access, ambiguity, or time),
B) Apply this to non-critical paths instead of all applicable paths: if investigation cannot be completed (missing source access, ambiguity, or time),
C) If investigation can be completed (missing source access, ambiguity, or time),
D) If investigation is not allowed to be completed (missing source access, ambiguity, or time),

### Q019 (USER_APPROVED_CERTIFICATION_MD_FE7543EC84::H2DCC84D24B0D)
- source: `agent_onboarding/default/general/skills/user_approved_certification.md#additional-post-compaction-gate-mandatory`
- doc_id: `USER_APPROVED_CERTIFICATION_MD_FE7543EC84`
- difficulty: `hard`

Select the single true statement for this policy claim. Source: `agent_onboarding/default/general/skills/user_approved_certification.md#additional-post-compaction-gate-mandatory`. Choose one option.

A) Under this rule, the correct behavior is: if the session follows a compaction/handoff/reset event, the user should only
B) Apply this only after implementation is complete: if the session follows a compaction/handoff/reset event, the user should only
C) If the session follows a compaction/handoff/reset event, the user should primarily
D) if the session follows a compaction/handoff/reset event, the user should only only when no policy gate is affected

### Q020 (TECHNICAL_EXPERTISE_MD_965DF266F7::H305EAF2B5450)
- source: `agent_onboarding/default/engineer/skills/technical_expertise.md#technical-expertise`
- doc_id: `TECHNICAL_EXPERTISE_MD_965DF266F7`
- difficulty: `hard`

Select the single true statement for this policy claim. Source: `agent_onboarding/default/engineer/skills/technical_expertise.md#technical-expertise`. Choose one option.

A) Add guards primarily when the contract requires optional state
B) add guards only when the contract requires optional state unless explicitly waived by the user
C) Apply this only after implementation is complete: add guards only when the contract requires optional state
D) Under this rule, the correct behavior is: add guards only when the contract requires optional state

### Q021 (ENGINEER_QUALITY_POLICY_MD_66A6644C4D::HAF180AC4EF95)
- source: `agent_onboarding/default/engineer/policies/engineer_quality_policy.md#engineer-quality-policy`
- doc_id: `ENGINEER_QUALITY_POLICY_MD_66A6644C4D`
- difficulty: `hard`

Pick the statement that preserves the policy gate exactly. Source: `agent_onboarding/default/engineer/policies/engineer_quality_policy.md#engineer-quality-policy`. Choose one option.

A) Quality findings is required to cite concrete file/symbol evidence or remain UNKNOWN
B) Treat this as a post-certification step: quality findings must cite concrete file/symbol evidence or remain UNKNOWN
C) Quality findings must not cite concrete file/symbol evidence or remain UNKNOWN
D) Apply this to non-critical paths instead of all applicable paths: quality findings must cite concrete file/symbol evidence or remain UNKNOWN

### Q022 (POLICY_SKILLS_MD_56890A798A::H0D743418D8DD)
- source: `agent_onboarding/default/general/policies/policy_skills.md#policy-skills`
- doc_id: `POLICY_SKILLS_MD_56890A798A`
- difficulty: `hard`

Identify the only correct claim from this near-match option set. Source: `agent_onboarding/default/general/policies/policy_skills.md#policy-skills`. Choose one option.

A) The required policy behavior is: `agent_onboarding/default/general/skills/unknowns_gate_reference.md`
B) Apply this to non-critical paths instead of all applicable paths: `agent_onboarding/default/general/skills/unknowns_gate_reference.md`
C) `agent_onboarding/default/general/skills/unknowns_gate_reference.md` unless explicitly waived by the user
D) Treat this as a post-certification step: `agent_onboarding/default/general/skills/unknowns_gate_reference.md`

### Q023 (AGENTS_MD_1EECA99492::HED1D6923F6C8)
- source: `AGENTS.MD#highest-priority-adherence-compaction-re-onboarding`
- doc_id: `AGENTS_MD_1EECA99492`
- difficulty: `hard`

Choose the true invariant; the other three options are close lies. Source: `AGENTS.MD#highest-priority-adherence-compaction-re-onboarding`. Choose one option.

A) onboarding claims are valid only when optional source documents were actually
B) onboarding claims are valid primarily when required source documents were actually
C) onboarding claims are valid only when mandatory source documents were actually
D) Treat this as a post-certification step: onboarding claims are valid only when required source documents were actually

### Q024 (ARTIFACT_BOARD_MD_748583D824::HB9261969AB03)
- source: `artifact_board.md#artifact-board`
- doc_id: `ARTIFACT_BOARD_MD_748583D824`
- difficulty: `hard`

Choose the true invariant; the other three options are close lies. Source: `artifact_board.md#artifact-board`. Choose one option.

A) some artifact row must include a ticket path and retention decision
B) Apply this only after implementation is complete: every artifact row must include a ticket path and retention decision
C) Every artifact row is required to include a ticket path and retention decision
D) Every artifact row must not include a ticket path and retention decision

### Q025 (SKILL_CHECK_POLICY_MD_7D5A201CAB::HA29BB5AF7D60)
- source: `skill_check/skill_check_policy.md#4-exam-generation-contract-required`
- doc_id: `SKILL_CHECK_POLICY_MD_7D5A201CAB`
- difficulty: `hard`

Pick the one statement that is true for this document context. Source: `skill_check/skill_check_policy.md#4-exam-generation-contract-required`. Choose one option.

A) Allocate `ceil(LOC/100)` questions per mandatory doc
B) Allocate `ceil(LOC/100)` questions per optional doc
C) Apply this to non-critical paths instead of all applicable paths: allocate `ceil(LOC/100)` questions per required doc
D) Apply this only after implementation is complete: allocate `ceil(LOC/100)` questions per required doc

### Q026 (CONTEXT_WINDOW_BUDGET_MD_E9C7ABBBEE::H2D8B5EEA8BD5)
- source: `agent_onboarding/default/general/skills/context_window_budget.md#context-window-budget`
- doc_id: `CONTEXT_WINDOW_BUDGET_MD_E9C7ABBBEE`
- difficulty: `hard`

Pick the statement that preserves the policy gate exactly. Source: `agent_onboarding/default/general/skills/context_window_budget.md#context-window-budget`. Choose one option.

A) Apply this to selected workflows only: if work requires jumping outside the current subsystem, record why in ticket notes first
B) If work requires jumping outside the current subsystem, record why in ticket notes last
C) if work requires jumping outside the current subsystem, record why in ticket notes first only when no policy gate is affected
D) Under this rule, the correct behavior is: if work requires jumping outside the current subsystem, record why in ticket notes first

### Q027 (TICKETING_MD_B9F11C28D1::HAD94D5AB3766)
- source: `agent_onboarding/default/general/skills/ticketing.md#ticketing`
- doc_id: `TICKETING_MD_B9F11C28D1`
- difficulty: `hard`

Choose the exact rule that remains valid under this source anchor. Source: `agent_onboarding/default/general/skills/ticketing.md#ticketing`. Choose one option.

A) Apply this to selected workflows only: ticket contract gates are authoritative under `workflow.ticket_contract`
B) ticket contract gates are authoritative under `workflow.ticket_contract` only when no policy gate is affected
C) Under this rule, the correct behavior is: ticket contract gates are authoritative under `workflow.ticket_contract`
D) Treat this as a post-certification step: ticket contract gates are authoritative under `workflow.ticket_contract`

### Q028 (MEMORY_MANAGEMENT_MD_FA354F406A::H49C3630A0152)
- source: `agent_onboarding/default/general/skills/memory_management.md#memory-management`
- doc_id: `MEMORY_MANAGEMENT_MD_FA354F406A`
- difficulty: `hard`

Pick the statement that preserves the policy gate exactly. Source: `agent_onboarding/default/general/skills/memory_management.md#memory-management`. Choose one option.

A) Apply this only after implementation is complete: never store secrets in tickets or docs
B) Apply this to selected workflows only: never store secrets in tickets or docs
C) Under this rule, the correct behavior is: never store secrets in tickets or docs
D) sometimes store secrets in tickets or docs

### Q029 (ACTIVE_POINTERBOARD_MD_4590880B7C::H07BFD011079D)
- source: `agent_onboarding/default/general/skills/active_pointerboard.md#active-pointerboard`
- doc_id: `ACTIVE_POINTERBOARD_MD_4590880B7C`
- difficulty: `hard`

Choose the exact rule that remains valid under this source anchor. Source: `agent_onboarding/default/general/skills/active_pointerboard.md#active-pointerboard`. Choose one option.

A) When switch conditions become true and routing is required to change
B) When switch conditions become true and routing must not change
C) Apply this to selected workflows only: when switch conditions become true and routing must change
D) Treat this as a post-certification step: when switch conditions become true and routing must change

### Q030 (REACTIVE_DOCUMENTATION_MD_73B34DE8A2::HC2C6BE4BC5BF)
- source: `agent_onboarding/default/general/skills/reactive_documentation.md#reactive-documentation`
- doc_id: `REACTIVE_DOCUMENTATION_MD_73B34DE8A2`
- difficulty: `hard`

Pick the one statement that is true for this document context. Source: `agent_onboarding/default/general/skills/reactive_documentation.md#reactive-documentation`. Choose one option.

A) Preserve momentum by recording only what is required to be re-read later
B) Preserve momentum by recording only what must not be re-read later
C) Preserve momentum by recording primarily what must be re-read later
D) Treat this as a post-certification step: preserve momentum by recording only what must be re-read later

### Q031 (TICKET_CLOSURE_ATTENTION_SYNC_MD_BE9F026937::H506FB21F0829)
- source: `agent_onboarding/default/general/skills/ticket_closure_attention_sync.md#ticket-closure-attention-sync`
- doc_id: `TICKET_CLOSURE_ATTENTION_SYNC_MD_BE9F026937`
- difficulty: `hard`

Select the single true statement for this policy claim. Source: `agent_onboarding/default/general/skills/ticket_closure_attention_sync.md#ticket-closure-attention-sync`. Choose one option.

A) `## Active Attention Details` is required to only contain active-routing details
B) `## Active Attention Details` must not only contain active-routing details
C) `## Active Attention Details` must primarily contain active-routing details
D) Treat this as a post-certification step: `## Active Attention Details` must only contain active-routing details

### Q032 (CONTEXT_PROTOCOL_MD_C4C2DB8A08::HDC3FDEE87B30)
- source: `agent_onboarding/default/engineer/skills/context_protocol.md#context-protocol`
- doc_id: `CONTEXT_PROTOCOL_MD_C4C2DB8A08`
- difficulty: `hard`

Choose the true invariant; the other three options are close lies. Source: `agent_onboarding/default/engineer/skills/context_protocol.md#context-protocol`. Choose one option.

A) Apply this to non-critical paths instead of all applicable paths: always prefer documented context over assumptions
B) usually prefer documented context over assumptions
C) The required policy behavior is: always prefer documented context over assumptions
D) Apply this only after implementation is complete: always prefer documented context over assumptions

### Q033 (CTX_AUTONOMY_RUBRIC_MD_58460FA90A::HCFF11C1E7741)
- source: `agent_onboarding/default/engineer/policies/ctx_autonomy_rubric.md#ctx-autonomy-policy`
- doc_id: `CTX_AUTONOMY_RUBRIC_MD_58460FA90A`
- difficulty: `hard`

Choose the exact rule that remains valid under this source anchor. Source: `agent_onboarding/default/engineer/policies/ctx_autonomy_rubric.md#ctx-autonomy-policy`. Choose one option.

A) score 60-74: proceed only if necessary, and flag for review/resurvey unless explicitly waived by the user
B) Score 60-74: proceed primarily if necessary, and flag for review/resurvey
C) Policy-compliant execution requires: score 60-74: proceed only if necessary, and flag for review/resurvey
D) Apply this only after implementation is complete: score 60-74: proceed only if necessary, and flag for review/resurvey

### Q034 (COMPACTION_DIFF_ONBOARDING_MD_52789BB4E1::H9A89C9D7F036)
- source: `agent_onboarding/default/general/skills/compaction_diff_onboarding.md#step-1-minimum-readset`
- doc_id: `COMPACTION_DIFF_ONBOARDING_MD_52789BB4E1`
- difficulty: `hard`

Identify the only correct claim from this near-match option set. Source: `agent_onboarding/default/general/skills/compaction_diff_onboarding.md#step-1-minimum-readset`. Choose one option.

A) broad under-test skill docs after submission
B) broad under-test skill docs before submission only when no policy gate is affected
C) Apply this to non-critical paths instead of all applicable paths: broad under-test skill docs before submission
D) broad under-test skill docs prior to submission

### Q035 (UNKNOWNS_GATE_REFERENCE_MD_AD06A50B4C::HB45029159A8C)
- source: `agent_onboarding/default/general/skills/unknowns_gate_reference.md#unknowns-gate-reference`
- doc_id: `UNKNOWNS_GATE_REFERENCE_MD_AD06A50B4C`
- difficulty: `hard`

Choose the true invariant; the other three options are close lies. Source: `agent_onboarding/default/general/skills/unknowns_gate_reference.md#unknowns-gate-reference`. Choose one option.

A) Treat this as a post-certification step: promote to FACT only when evidence directly supports the claim
B) promote to FACT only when evidence directly supports the claim only when no policy gate is affected
C) The required policy behavior is: promote to FACT only when evidence directly supports the claim
D) Promote to FACT primarily when evidence directly supports the claim

### Q036 (ACTIVE_DOCUMENTATION_MD_D01C615D40::HCA1D105485EA)
- source: `agent_onboarding/default/general/skills/active_documentation.md#active-documentation`
- doc_id: `ACTIVE_DOCUMENTATION_MD_D01C615D40`
- difficulty: `hard`

Select the single true statement for this policy claim. Source: `agent_onboarding/default/general/skills/active_documentation.md#active-documentation`. Choose one option.

A) Every active ticket (epic/story/task) is required to include a `## Notes` section
B) some active ticket (epic/story/task) must include a `## Notes` section
C) Apply this only after implementation is complete: every active ticket (epic/story/task) must include a `## Notes` section
D) Every active ticket (epic/story/task) must not include a `## Notes` section

### Q037 (CTX_AUTONOMY_POLICY_MD_4E704BF803::HB681BAB38B7B)
- source: `agent_onboarding/default/engineer/policies/ctx_autonomy_policy.md#ctx-autonomy-policy`
- doc_id: `CTX_AUTONOMY_POLICY_MD_4E704BF803`
- difficulty: `hard`

Choose the exact rule that remains valid under this source anchor. Source: `agent_onboarding/default/engineer/policies/ctx_autonomy_policy.md#ctx-autonomy-policy`. Choose one option.

A) Target >= 75 for file ctx on production code; avoid proceed to dir ctx if below 60
B) Apply this only after implementation is complete: target >= 75 for file ctx on production code; do not proceed to dir ctx if below 60
C) Apply this to selected workflows only: target >= 75 for file ctx on production code; do not proceed to dir ctx if below 60
D) target >= 75 for file ctx on production code; do not proceed to dir ctx if below 60 unless explicitly waived by the user

### Q038 (TICKETING_SKILL_CONTRACT_MD_6AF21B7276::HC24519F77770)
- source: `agent_onboarding/default/general/skills/ticketing_skill_contract.md#context-compaction-handoff`
- doc_id: `TICKETING_SKILL_CONTRACT_MD_6AF21B7276`
- difficulty: `hard`

Choose the exact rule that remains valid under this source anchor. Source: `agent_onboarding/default/general/skills/ticketing_skill_contract.md#context-compaction-handoff`. Choose one option.

A) Apply this to selected workflows only: keep ticket `Context / Handoff Summary` sections current before handoff
B) Keep ticket `Context / Handoff Summary` sections current after handoff
C) keep ticket `Context / Handoff Summary` sections current before handoff unless explicitly waived by the user
D) Keep ticket `Context / Handoff Summary` sections current prior to handoff
