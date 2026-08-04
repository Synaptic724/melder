# Task: Document Codex CLI Native Sandbox Vs CommandOps Container Sandbox
- Completed: 2026-05-10T00:06:36Z
- Summary: Closed after the Codex-local versus CommandOps-container sandbox
  comparison artifact was written, source-backed, and linked into the
  open-questions lane.

## Metadata
- Task ID: TASK-2026-05-06-document-codex-cli-native-sandbox-vs-commandops-container-sandbox
- Story:
- Epic: EPIC-2026-05-03-general-open-questions
- Status: done
- Owner: codex
- Agent Name: codex_0
- Priority: p0
- Created: 2026-05-06T10:27:13Z
- Updated: 2026-05-10T00:06:36Z

## Objective
Capture one durable artifact that explains:
- how Codex CLI actually implements local sandboxing
- how that differs from the planned CommandOps sandbox direction
- why the planned sandbox path will use Docker Compose for general users and
  K3s/Kubernetes for business and enterprise deployment tiers

## Ticket Contract
- ENTRY_GATE: the user explicitly requested a large artifact describing Codex
  CLI sandbox design, the practical differences from the planned
  CommandOps container model, and the planned Compose/K3s/Kubernetes
  deployment direction.
- EXECUTION_BOUNDARY:
  - `codex/context_compass/artifacts/`
  - `codex/context_compass/artifact_board.md`
  - `codex/context_compass/attention_board.md`
  - `codex/context_compass/tickets/epics/2026-05-03_general_open_questions_epic.md`
  - this task ticket
- DEPENDENCIES:
  - `<local-path>/Downloads/codex-main/codex-rs/README.md`
  - `<local-path>/Downloads/codex-main/codex-rs/linux-sandbox/README.md`
  - `<local-path>/Downloads/codex-main/codex-rs/shell-escalation/README.md`
  - `<local-path>/Downloads/codex-main/codex-rs/windows-sandbox-rs/`
  - current user-approved CommandOps sandbox direction from active chat
- EXIT_GATE: the new sandbox-design artifact exists, the owning epic and
  artifact board both point to it clearly, and the task notes record the
  observed Codex facts plus the planned CommandOps design direction.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` only if the observed Codex
  source contradicts the current planned container-first CommandOps direction
  strongly enough that the user needs to choose between incompatible models.

## Scope Boundaries
- In scope:
  - Codex CLI local sandbox architecture from source
  - native-process sandbox vs container/pod sandbox comparison
  - planned CommandOps sandbox layering and deployment tiers
  - artifact and ticket/board wiring
- Out of scope:
  - implementing the CommandOps sandbox
  - changing Melder or Rift runtime code
  - production container manifests

## State Transition Event
- from_state: draft
- to_state: review
- transition_reason: the requested artifact lane is implemented and wired into
  the open-questions epic as a durable sandbox-design reference.

## Steps / Checklist
- [x] Inspect the local `codex-main` source tree for the real sandbox design.
- [x] Write the sandbox-design artifact.
- [x] Link the artifact into the owning epic and artifact board.
- [x] Route the lane on `attention_board.md`.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- one sandbox-design artifact covering Codex CLI vs planned CommandOps sandboxing

## Files / Paths Impacted
- codex/context_compass/tickets/tasks/2026-05-06_document_codex_cli_native_sandbox_vs_commandops_container_sandbox_task.md
- codex/context_compass/artifacts/2026-05-06_codex_cli_native_sandbox_vs_commandops_container_sandbox_philosophy.md
- codex/context_compass/tickets/epics/2026-05-03_general_open_questions_epic.md
- codex/context_compass/artifact_board.md
- codex/context_compass/attention_board.md

## Validation
- Not run.
- Documentation-only lane. Source inspection and wiring updates only.

## Risks / Rollback Notes
- Risk: the artifact overstates the planned CommandOps design as implemented
  fact when it is still architectural intent.
  Rollback: keep the artifact explicitly split between observed Codex source
  facts and planned CommandOps direction.

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
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - artifacts/2026-05-06_codex_cli_native_sandbox_vs_commandops_container_sandbox_philosophy.md
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: none

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-05-06T10:27:13Z
  TYPE: PLAN
  CLAIM: The useful comparison is not product copy versus product copy. It is
    source-backed Codex local sandbox architecture versus the planned
    CommandOps container-first sandbox direction. The artifact should separate
    observed Codex facts from planned CommandOps intent so we do not blur
    implementation reality and future design.
  EVIDENCE:
  - <local-path>/Downloads/codex-main/codex-rs/README.md
  - <local-path>/Downloads/codex-main/codex-rs/linux-sandbox/README.md
  - <local-path>/Downloads/codex-main/codex-rs/shell-escalation/README.md
  - <local-path>/Downloads/codex-main/codex-rs/windows-sandbox-rs/src/lib.rs
  - <local-path>/Downloads/codex-main/codex-rs/windows-sandbox-rs/src/process.rs
  - <local-path>/Downloads/codex-main/codex-rs/windows-sandbox-rs/src/token.rs
  - <local-path>/Downloads/codex-main/codex-rs/windows-sandbox-rs/src/firewall.rs
  IMPACT: The resulting artifact can become a real design reference for later
    CommandOps sandbox work instead of leaving the distinction trapped in chat.
  NEXT: write the artifact, then wire it into the owning epic and artifact board.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-06T10:27:13Z
  TYPE: MEASURE
  CLAIM: The Codex local sandbox story is now source-backed. The maintained CLI
    is Rust, Linux local sandboxing is bubblewrap-first with seccomp and
    namespace isolation, Windows local sandboxing is a native Rust crate that
    uses restricted tokens, path ACL rewriting, sandbox users/credentials,
    `CreateProcessAsUserW`, firewall/WFP rules, and optional private desktop
    isolation, and shell escalation provides per-exec run/escalate/deny
    mediation. The new artifact records that model and contrasts it with the
    planned CommandOps direction: outer container/pod isolation via Docker
    Compose for general users and K3s/Kubernetes for business/enterprise,
    plus an inner process-policy layer inside the worker container.
  EVIDENCE:
  - <local-path>/Downloads/codex-main/codex-rs/README.md
  - <local-path>/Downloads/codex-main/codex-rs/linux-sandbox/README.md
  - <local-path>/Downloads/codex-main/codex-rs/shell-escalation/README.md
  - <local-path>/Downloads/codex-main/codex-rs/windows-sandbox-rs/Cargo.toml
  - <local-path>/Downloads/codex-main/codex-rs/windows-sandbox-rs/src/lib.rs
  - <local-path>/Downloads/codex-main/codex-rs/windows-sandbox-rs/src/process.rs
  - <local-path>/Downloads/codex-main/codex-rs/windows-sandbox-rs/src/identity.rs
  - <local-path>/Downloads/codex-main/codex-rs/windows-sandbox-rs/src/token.rs
  - <local-path>/Downloads/codex-main/codex-rs/windows-sandbox-rs/src/firewall.rs
  - codex/context_compass/artifacts/2026-05-06_codex_cli_native_sandbox_vs_commandops_container_sandbox_philosophy.md
  IMPACT: The open-questions lane now has one durable sandbox-design reference
    instead of a loose conversational explanation.
  NEXT: return the artifact lane for review and decide whether the next step is
    a concrete CommandOps sandbox interface/task or more architecture capture first.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-06T10:46:56Z
  TYPE: FACT
  CLAIM: The new sandbox-design artifact is now explicitly linked to the older
    AR/codegen capability-surface philosophy. The intended pairing is now
    durable in the files themselves instead of only implicit in chat:
    capability philosophy explains what AR/Rift/codegen are for, while the
    sandbox philosophy explains where lower-trust execution should sit so those
    capabilities stay protected.
  EVIDENCE:
  - codex/context_compass/artifacts/2026-05-06_codex_cli_native_sandbox_vs_commandops_container_sandbox_philosophy.md
  - codex/context_compass/artifacts/2026-04-26_ar_codegen_capability_surface_philosophy.md
  IMPACT: Future CommandOps sandbox work now has the correct paired philosophy
    reference instead of treating the sandbox artifact as a standalone design note.
  NEXT: return the artifact lane for review and decide whether the next step is
    concrete backend interface design or more surrounding architecture capture.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
This task owns the durable sandbox-design artifact comparing Codex local native
sandboxing with the planned CommandOps container/pod-first sandbox direction.
