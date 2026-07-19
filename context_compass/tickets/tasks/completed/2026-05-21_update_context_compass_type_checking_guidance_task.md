# Task: update context_compass TYPE_CHECKING guidance

- Completed: 2026-05-21T09:52:50Z
- Summary: Closed after the live `context_compass` typing guidance was updated to a `TYPE_CHECKING`-first stance and the stale anti-`TYPE_CHECKING` wording was removed from the matched docs.

## Metadata
- Task ID: TASK-2026-05-21-update-context-compass-type-checking-guidance
- Story: none
- Status: done
- Owner: codex
- Agent Name: refactor_0
- Priority: p1
- Created: 2026-05-21T09:41:45Z
- Updated: 2026-05-21T09:52:50Z

## Objective
Update `codex/context_compass` so the documented typing stance treats
`TYPE_CHECKING` as the primary enforcement path and relegates Protocol-heavy
structure enforcement to the exceptional case.

## Ticket Contract
- ENTRY_GATE: user explicitly requested a `context_compass` search/update pass
  for `TYPE_CHECKING` guidance and certification is active for `refactor_0`.
- EXECUTION_BOUNDARY:
  - `codex/context_compass/**` files that literally reference `TYPE_CHECKING`
  - directly adjacent wording in the same files when needed to keep the new
    typing stance coherent
- DEPENDENCIES:
  - `codex/context_compass/attention_board.md`
  - current user-defined `synaptic_python_developer` policy/guidance files
- EXIT_GATE:
  - every live `TYPE_CHECKING` guidance reference in `codex/context_compass`
    is inventoried
  - affected docs are updated to the new stance
  - board/task notes record what was changed and any intentionally untouched
    historical surfaces
- FAILURE_ESCALATION:
  - raise `CONFLICT` if the user-requested rewrite would require falsifying
    completed-ticket history instead of updating live policy/guidance

## Scope Boundaries
- In scope:
  - live policy docs
  - live guidance docs
  - active task/artifact docs if they carry now-wrong `TYPE_CHECKING` guidance
  - historical ticket/docs only if needed to satisfy the literal user request
- Out of scope:
  - `src/` production code
  - `tests/` code
  - non-`context_compass` documentation

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: the user requested a direct `TYPE_CHECKING` guidance sweep
  inside `context_compass`, so a bounded task is required before edits.

## Steps / Checklist
- [ ] inventory every `TYPE_CHECKING` reference under `codex/context_compass`
- [ ] separate live policy/guidance surfaces from historical record surfaces
- [ ] update the affected live guidance to the new typing stance
- [ ] decide whether any historical files should be rewritten or intentionally
      left as history
- [ ] run a focused verification search to confirm the remaining references are
      intentional
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further
      investigation.

## Deliverables
- updated `context_compass` typing guidance aligned to `TYPE_CHECKING` as the
  primary enforcement path

## Files / Paths Impacted
- `codex/context_compass/**`

## Validation
- Not run.
- Recommended commands:
  - `rg -n "TYPE_CHECKING" codex\context_compass`

## Risks / Rollback Notes
- Risk: rewriting completed tickets may falsify historical execution records.
  Rollback: keep completed-ticket history intact and confine the wording change
  to live policy/guidance unless the user explicitly requires historical edits.

## Applicable Anti-Patterns
- [ ] No status transition without evidence-backed transition reason.
- [ ] No implementation/validation from `UNKNOWN` or `HYPOTHESIS`.
- [ ] No closure without acceptance confirmation and board-sync completion.

## Done Checklist
- [ ] Steps complete and checked off
- [ ] Deliverables produced and linked
- [ ] Documentation updated (if needed)
- [ ] Validation status recorded
- [ ] Unknown-first discipline followed (`UNKNOWN` promoted to `FACT` only with evidence)
- [ ] Notes quality maintained (`SCORE_0_TO_10` >=
      `workflow.ticket_microcycle.minimum_note_score`)
- [ ] Applicable anti-pattern checks are clear or escalated with evidence.
- [ ] Acceptance criteria reviewed with user and confirmed
- [ ] Board sync completed for successor routing or closure anchor update.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: false
- ARTIFACT_PATHS:
- DISPOSITION: delete_on_close
- CLEANUP_TRIGGER: n/a

## Noting Behavior
- Note focus: exact file inventory, wording deltas, and one-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-05-21T09:41:45Z
  TYPE: FACT
  CLAIM: The current `context_compass` guidance still contains explicit anti-`TYPE_CHECKING` rules in the active `synaptic_python_developer` overlay, and the initial sweep also found `TYPE_CHECKING` references in artifacts and task-history docs.
  EVIDENCE:
  - codex/context_compass/agent_onboarding/user_defined/synaptic_python_developer/AGENTS.MD:263-263
  - codex/context_compass/agent_onboarding/user_defined/synaptic_python_developer/AGENTS.MD:320-322
  - codex/context_compass/agent_onboarding/user_defined/synaptic_python_developer/skills/python/typing.md:20-20
  - codex/context_compass/agent_onboarding/user_defined/synaptic_python_developer/skills/python/interfaces.md:25-25
  - codex/context_compass/agent_onboarding/user_defined/synaptic_python_developer/skills/python/banned_patterns.md:70-70
  IMPACT: The live typing-policy surface is directly inconsistent with the new requested stance, so those overlay docs are the first mandatory edit targets.
  NEXT: inventory the exact file set that contains literal `TYPE_CHECKING` references and classify live guidance versus historical record surfaces.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-21T09:41:45Z
  TYPE: FACT
  CLAIM: The literal `TYPE_CHECKING` inventory is small enough for a bounded doc sweep. Five files are live overlay guidance, and four more are older artifact/task/epic records that still embed the old no-`TYPE_CHECKING` stance.
  EVIDENCE:
  - codex/context_compass/agent_onboarding/user_defined/synaptic_python_developer/AGENTS.MD:263-263
  - codex/context_compass/agent_onboarding/user_defined/synaptic_python_developer/skills/synaptic_python_developer.md:240-240
  - codex/context_compass/agent_onboarding/user_defined/synaptic_python_developer/skills/python/typing.md:20-20
  - codex/context_compass/agent_onboarding/user_defined/synaptic_python_developer/skills/python/interfaces.md:25-25
  - codex/context_compass/agent_onboarding/user_defined/synaptic_python_developer/skills/python/banned_patterns.md:70-70
  - codex/context_compass/artifacts/2026-05-18_conduit_aether_refactor_plan.md:111-111
  - codex/context_compass/tickets/epics/2026-05-17_execute_first_mypyc_typing_cleanup_tranche_epic.md:26-171
  - codex/context_compass/tickets/tasks/2026-05-17_resolve_undefined_type_names_and_forward_interface_references_task.md:16-103
  - codex/context_compass/tickets/tasks/completed/2026-05-17_expand_protocol_crafter_ast_source_generation_task.md:24-29
  IMPACT: This can stay a nine-file wording pass instead of a broad repo rewrite, and the active overlay docs remain the primary correctness target.
  NEXT: patch the nine affected files so they express `TYPE_CHECKING`-first guidance and relegate Protocol/ABC structure enforcement to the exceptional case.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-21T09:41:45Z
  TYPE: FACT
  CLAIM: The doc sweep is implemented across the nine matched files. The synaptic overlay now states that `TYPE_CHECKING` is the default typing-only import path, and the older artifact/task/epic wording now points away from fake protocol shims and toward honest `TYPE_CHECKING` use.
  EVIDENCE:
  - codex/context_compass/agent_onboarding/user_defined/synaptic_python_developer/AGENTS.MD
  - codex/context_compass/agent_onboarding/user_defined/synaptic_python_developer/skills/synaptic_python_developer.md
  - codex/context_compass/agent_onboarding/user_defined/synaptic_python_developer/skills/python/typing.md
  - codex/context_compass/agent_onboarding/user_defined/synaptic_python_developer/skills/python/interfaces.md
  - codex/context_compass/agent_onboarding/user_defined/synaptic_python_developer/skills/python/banned_patterns.md
  - codex/context_compass/artifacts/2026-05-18_conduit_aether_refactor_plan.md
  - codex/context_compass/tickets/epics/2026-05-17_execute_first_mypyc_typing_cleanup_tranche_epic.md
  - codex/context_compass/tickets/tasks/2026-05-17_resolve_undefined_type_names_and_forward_interface_references_task.md
  - codex/context_compass/tickets/tasks/completed/2026-05-17_expand_protocol_crafter_ast_source_generation_task.md
  IMPACT: The live overlay no longer instructs contributors to avoid `TYPE_CHECKING`, and the older planning surfaces no longer encode the opposite stance.
  NEXT: run a focused `rg -n "TYPE_CHECKING" codex\\context_compass` verification pass and classify any remaining references as acceptable or still stale.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-21T09:41:45Z
  TYPE: MEASURE
  CLAIM: The focused verification sweep shows no remaining anti-`TYPE_CHECKING` wording. The remaining `TYPE_CHECKING` hits are the now-positive policy/docs plus the active task/board entries describing this lane.
  EVIDENCE:
  - validation_result: `rg -n "TYPE_CHECKING" codex\\context_compass`
  - validation_result: `rg -n "forbid.*TYPE_CHECKING|forbidding \`TYPE_CHECKING|without \`TYPE_CHECKING|avoid \`TYPE_CHECKING|no-\`TYPE_CHECKING" codex\\context_compass` -> exit code `1`
  IMPACT: The live `context_compass` typing stance is aligned to the requested `TYPE_CHECKING`-first policy, and only intentional explanatory references remain.
  NEXT: report the changed files and remaining intentional references to the user for acceptance.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
Active bounded `context_compass` doc/policy sweep for `TYPE_CHECKING`
guidance.
