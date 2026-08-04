# Task: Implement AethericRiftSystem Configuration Governance

## Metadata
- Task ID: TASK-2026-03-22-implement-aethericrift-system-configuration-governance
- Story: STORY-2026-03-16-aethericrift-system-bootstrap
- Status: in_progress
- Owner: codex
- Priority: p0
- Created: 2026-03-22T19:31:42Z
- Updated: 2026-03-28T21:54:26Z

## Objective
Implement the process-wide `AethericRiftSystemConfiguration` governance model so
`Aether` can host a disabled-by-default AR subsystem, install a validated
configuration into it, and enforce creation/access/frame/topology policy
through the hosted `AethericRiftSystem`.

## Ticket Contract
- ENTRY_GATE: the bootstrap story remains active, the ownership model is still
  `Aether hosts, AethericRiftSystem owns`, and the user has explicitly approved
  the new configuration/governance slice.
- EXECUTION_BOUNDARY: AR system configuration, enable/disable wiring, and the
  related `Aether` / `AethericRiftSystem` / `AethericRiftState` changes only.
- DEPENDENCIES:
  - STORY-2026-03-16-aethericrift-system-bootstrap
  - tickets/artifacts/aethericrift_v1_object_model_and_build_direction.md
  - tickets/artifacts/aethericrift_riftspace_interaction_architecture.md
  - system_docs/patches/active/aethericrift_v1_workspace_runtime/architecture_patch.md
  - system_docs/patches/active/aethericrift_v1_workspace_runtime/component_patch_aetheric_rift_core.md
- EXIT_GATE: AR system configuration governs process-wide enablement, creation,
  access, target-frame policy, and system-frame topology, and `Aether` facades
  config creation plus ARS enable/disable access into the hosted subsystem.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if implementing the system-wide
  governance schema forces per-Rift room/history semantics into the same
  tranche.

## Scope Boundaries
- In scope:
  - `AethericRiftSystemConfiguration`
  - `Aether` enable/disable + config-factory facade methods
  - `AethericRiftSystem` runtime enabled/disabled state and policy enforcement
  - target-frame allow/deny governance
  - system-frame shared/isolated topology settings
  - tests/documentation touched by that slice
- Out of scope:
  - `RiftAction` / `RiftMemory`
  - room history/checkpoint/disposition semantics
  - MutationResearch behavior
  - profile-stack implementation

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: the user approved implementation of the ARS
  configuration/governance slice and the board now routes to this task.

## Steps / Checklist
- [x] Repair story/board routing for this new implementation slice.
- [x] Finalize the `AethericRiftSystemConfiguration` property schema and
      defaults.
- [x] Make ARS disabled by default as runtime state rather than config-only
      metadata.
- [x] Add `Aether` facade methods for creating config objects and enabling or
      disabling ARS.
- [x] Enforce creation/access/token/frame-governance policy in
      `AethericRiftSystem`.
- [x] Add target-frame allow-list and deny-list behavior with explicit
      precedence.
- [x] Add system-frame topology settings, including
      `system_frame_mode = single|indexed|one_per_workspace`.
- [x] Update tests and run syntax validation.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further
      investigation.

## Deliverables
- Process-wide `AethericRiftSystemConfiguration` schema aligned to the current
  AR docs
- Disabled-by-default ARS runtime wiring
- `Aether` facade for config creation and ARS enable/disable
- Policy enforcement for creation/access/frame governance

## Files / Paths Impacted
- src/melder/aether/aether.py
- src/melder/aether/aetheric_rift_system/aetheric_rift_system.py
- src/melder/aether/aetheric_rift_system/configuration/aetheric_rift_system_configuration.py
- src/melder/aether/aetheric_rift_system/configuration/aetheric_rift_configuration.py
- src/melder/aether/aetheric_rift_system/aetheric_rift_state/aetheric_rift_state.py
- src/melder/utilities/interfaces/interfaces.py
- tests/unit/melder/aether/test_aether.py
- tests/unit/melder/aether/test_aetheric_rift_system.py
- codex/context_compass/attention_board.md
- codex/context_compass/tickets/stories/2026-03-16_aethericrift_system_bootstrap_story.md

## Validation
- Not run.
- Planned validation:
  - syntax compile of touched AR files
  - targeted pytest for ARS/Aether tests if `pytest` is available

## Risks / Rollback Notes
- Risk: system config expands into per-Rift or room-level behavior.
  Rollback: keep this slice limited to process-wide governance and defaults.
- Risk: frame topology and target-frame policy become conflated.
  Rollback: preserve the distinction between internal system-frame settings and
  external target-frame governance.

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
- [ ] Notes quality maintained (`SCORE_0_TO_10` >= `workflow.ticket_microcycle.minimum_note_score`)
- [ ] Applicable anti-pattern checks are clear or escalated with evidence.
- [ ] Acceptance criteria reviewed with user and confirmed
- [ ] Board sync completed for successor routing or closure anchor update.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: false
- ARTIFACT_PATHS:
  - none
- DISPOSITION: delete_on_close
- CLEANUP_TRIGGER: n/a

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-03-22T19:31:42Z
  TYPE: FACT
  CLAIM: The current AR docs support a process-wide ARS governance object that
    controls canonical state, token-gated creation/access, and frame-topology
    policy, while leaving room/workspace semantics to lower layers such as
    `AethericRiftState` and `RiftSpace`.
  EVIDENCE:
  - codex/context_compass/tickets/artifacts/aethericrift_v1_object_model_and_build_direction.md:25-41
  - codex/context_compass/system_docs/patches/active/aethericrift_v1_workspace_runtime/architecture_patch.md:33-45
  - codex/context_compass/tickets/artifacts/aethericrift_riftspace_interaction_architecture.md:17-45
  IMPACT: The new ARS configuration slice can stay process-wide and should not
    absorb room history, action, or memory semantics.
  NEXT: patch board/story routing, then inspect the current AR config/Aether/ARS
    implementation for the exact code changes needed.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-03-22T19:31:42Z
  TYPE: FACT
  CLAIM: The current code scaffold still reflects the older permissive,
    mode-based config model instead of the newly approved disabled-by-default
    governance model: `Aether` auto-installs `AethericRiftSystemConfiguration`
    with `with_defaults()` at startup, the system config still uses
    `creation_mode` / `state_access_mode` / `rift_access_mode`, and
    `AethericRiftSystem.create_rift_state(...)` already passes
    `configuration=...` into `AethericRiftState` even though the current state
    class signature does not expose that parameter.
  EVIDENCE:
  - src/melder/aether/aether.py:65-69
  - src/melder/aether/aetheric_rift_system/configuration/aetheric_rift_system_configuration.py:57-68
  - src/melder/aether/aetheric_rift_system/configuration/aetheric_rift_system_configuration.py:184-195
  - src/melder/aether/aetheric_rift_system/aetheric_rift_system.py:87-92
  - src/melder/aether/aetheric_rift_system/aetheric_rift_system.py:196-223
  - src/melder/aether/aetheric_rift_system/aetheric_rift_state/aetheric_rift_state.py:29-47
  IMPACT: The implementation needs a real config-schema rewrite plus lifecycle
    cleanup in `Aether`, `AethericRiftSystem`, and `AethericRiftState` rather
    than a narrow additive patch.
  NEXT: patch the interfaces and concrete config/system/state files together so
    the runtime model and signatures line up again.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-03-22T19:31:42Z
  TYPE: FACT
  CLAIM: The AR system governance slice is now implemented in code: the central
    system config has been rewritten to explicit creation/access/frame-policy
    flags, `AethericRiftSystem` now starts disabled and requires explicit
    enablement, target-frame allow/deny and shared-vs-isolated system-frame
    policy are enforced in the hosted system, `Aether` now facades ARS
    config-creation plus enable/disable/status, and canonical Rift state now
    stores both the owned per-Rift configuration and the resolved internal
    system-frame anchor.
  EVIDENCE:
  - src/melder/aether/aetheric_rift_system/configuration/aetheric_rift_system_configuration.py:60-86
  - src/melder/aether/aetheric_rift_system/configuration/aetheric_rift_system_configuration.py:204-226
  - src/melder/aether/aetheric_rift_system/configuration/aetheric_rift_system_configuration.py:323-492
  - src/melder/aether/aetheric_rift_system/aetheric_rift_system.py:52-89
  - src/melder/aether/aetheric_rift_system/aetheric_rift_system.py:159-206
  - src/melder/aether/aetheric_rift_system/aetheric_rift_system.py:516-672
  - src/melder/aether/aether.py:277-328
  - src/melder/aether/aether.py:379-610
  - src/melder/aether/aetheric_rift_system/aetheric_rift_state/aetheric_rift_state.py:35-88
  - tests/unit/melder/aether/test_aetheric_rift_system.py:25-209
  - tests/unit/melder/aether/test_aether.py:276-376
  IMPACT: The AR scaffold now matches the newly approved process-wide
    governance model instead of the older mode-based permissive placeholder.
  NEXT: run syntax validation, repair any contract drift, and then decide
    whether the next slice is ticket/status cleanup or more AR runtime work.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-03-22T19:31:42Z
  TYPE: MEASURE
  CLAIM: Syntax validation passed for the touched AR/config/test files via
    `py_compile`, but targeted pytest execution is still environment-blocked
    because the discovered virtualenv does not currently have `pytest`
    installed.
  EVIDENCE:
  - command:.venv\Scripts\python.exe -m py_compile src\melder\utilities\interfaces\interfaces.py src\melder\aether\aether.py src\melder\aether\aetheric_rift_system\configuration\aetheric_rift_system_configuration.py src\melder\aether\aetheric_rift_system\configuration\aetheric_rift_configuration.py src\melder\aether\aetheric_rift_system\aetheric_rift_system.py src\melder\aether\aetheric_rift_system\aetheric_rift_state\aetheric_rift_state.py src\melder\aether\aetheric_rift_system\aetheric_rift\aetheric_rift.py tests\unit\melder\aether\test_aether.py tests\unit\melder\aether\test_aetheric_rift_system.py
  - command:.venv\Scripts\python.exe -m pytest tests\unit\melder\aether\test_aetheric_rift_system.py tests\unit\melder\aether\test_aether.py -q -> No module named pytest
  IMPACT: The code is syntax-clean, but behavioral test execution still depends
    on the local Python environment being repaired or `pytest` being installed.
  NEXT: report the implementation outcome truthfully, including `Not run.` for
    pytest validation.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-03-28T00:00:00Z
  TYPE: FACT
  CLAIM: The current conduit link path does not appear to enforce a same-frame
    hard-stop. `Conduit.link(...)` validates dynamic mode, target type, and
    target id presence, then delegates to `ConduitWard._link(...)`. The ward
    link path checks lesser/self/dynamic/policy constraints and then creates a
    contract directly between the two wards/spellbooks. There is no explicit
    `_aetheric_frame` equality check in the public link path or the contract
    creation path.
  EVIDENCE:
  - src/melder/aether/conduit/conduit.py:2463-2500
  - src/melder/aether/conduit/conduit.py:2512-2541
  - src/melder/aether/conduit/conduit_ward/conduit_ward.py:573-652
  - src/melder/aether/conduit/conduit_ward/conduit_ward.py:652-698
  IMPACT: We should not assume cross-frame conduit linking is forbidden by the
    current runtime. ARS topology decisions should treat shared-root-conduit
    ideas as unsafe until we either enforce same-frame linking explicitly or
    deliberately support cross-frame contracts.
  NEXT: discuss whether cross-frame conduit linking should be forbidden as a
    runtime invariant and, if yes, create a dedicated enforcement task instead
    of burying that behavior inside ARS config.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-03-28T17:01:48Z
  TYPE: DECISION
  CLAIM: The next ARS lifecycle refactor should move from "eagerly hosted with
    default config attached" to "hosted but unconfigured until engaged." That
    means `Aether` still hosts an `AethericRiftSystem` object, but
    `_aetheric_rift_system_configuration` should start as `None`, ARS should
    track `_configured` separately from `_enabled`, and ARS-facing facade
    methods that require configured defaults or runtime state must fail fast
    until the user explicitly creates/installs a config and enables the
    subsystem.
  EVIDENCE:
  - src/melder/spellbook/spellbook.py:117-117
  - src/melder/aether/aether.py:54-69
  - src/melder/aether/aether.py:264-314
  - src/melder/aether/aetheric_rift_system/aetheric_rift_system.py:60-84
  - src/melder/aether/aetheric_rift_system/aetheric_rift_system.py:172-206
  IMPACT: This better matches ARS as an explicitly engaged master-user feature
    and prevents the runtime from looking preconfigured just because `Aether`
    or `Spellbook` was touched.
  NEXT: patch interfaces, system config schema, and `Aether` / ARS lifecycle
    guards to the new configured-vs-enabled model.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-03-28T17:01:48Z
  TYPE: FACT
  CLAIM: The ARS lifecycle now follows the intended host-side model more
    closely: `Aether` still hosts an `AethericRiftSystem` object at boot, but
    no ARS configuration is installed by default; ARS tracks both
    `_configured` and `_enabled`; system configuration now uses
    `system_frame_mode = single|indexed|one_per_workspace` plus the easier
    defaults we settled on (`default_system_frame_name = aetheric_frame_system`,
    default target frame limited to `default`); and the focused AR tests now
    require explicit config creation before ARS enablement or per-Rift config
    creation.
  EVIDENCE:
  - src/melder/aether/aether.py:54-69
  - src/melder/aether/aether.py:264-314
  - src/melder/aether/aetheric_rift_system/aetheric_rift_system.py:48-82
  - src/melder/aether/aetheric_rift_system/aetheric_rift_system.py:187-214
  - src/melder/aether/aetheric_rift_system/configuration/aetheric_rift_system_configuration.py:55-79
  - src/melder/aether/aetheric_rift_system/configuration/aetheric_rift_system_configuration.py:184-206
  - tests/unit/melder/aether/test_aether.py:282-380
  - tests/unit/melder/aether/test_aetheric_rift_system.py:6-135
  IMPACT: ARS now behaves like an explicitly engaged master-user subsystem
    instead of looking preconfigured just because `Aether` or `Spellbook`
    exists.
  NEXT: review the lifecycle and default posture with the user, then continue
    iterating on ARS/AR configuration boundaries.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-03-28T17:01:48Z
  TYPE: FACT
  CLAIM: The ARS/AR code paths we have been iterating on are still below the
    required docstring bar for the active `synaptic_python_developer` profile:
    many method docstrings state only a label/purpose and omit real parameter,
    return, raise, lifecycle, or contract detail. The next tranche should be a
    docstring-only pass across the ARS config/system/state/space objects and
    the `Aether` AR facade region.
  EVIDENCE:
  - src/melder/aether/aether.py:47-69
  - src/melder/aether/aetheric_rift_system/aetheric_rift_system.py:187-214
  - src/melder/aether/aetheric_rift_system/configuration/aetheric_rift_system_configuration.py:118-172
  - src/melder/aether/aetheric_rift_system/configuration/aetheric_rift_configuration.py:56-98
  - src/melder/aether/aetheric_rift_system/aetheric_rift_state/aetheric_rift_state.py:49-76
  - src/melder/aether/aetheric_rift_system/rift_space/rift_space.py:42-82
  IMPACT: The code contracts are harder to audit and do not currently meet the
    documentation-first standard required for touched AR files.
  NEXT: do a docstring-only pass on the AR files we have changed, without
    changing behavior.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-03-28T21:38:03Z
  TYPE: ALIGNMENT_CHECK
  CLAIM: The ARS system-level configuration surface is now stable enough to
    treat as the locked process-wide policy layer: it is grouped into
    creation/access governance, internal system-frame topology, target/userland
    frame governance, and per-Rift defaults. The multi-frame userland policy
    knobs (`allow_multiple_target_frames` and `max_target_frame_count`) remain
    on ARS and apply to target frames rather than ARS-owned internal system
    frames. The next design slice should move downward into
    `AethericRiftState`, ARS-managed frame responsibility tracking, and how AR
    state/workspace layers consume those frame assignments.
  EVIDENCE:
  - src/melder/aether/aetheric_rift_system/configuration/aetheric_rift_system_configuration.py:62-89
  - src/melder/aether/aetheric_rift_system/configuration/aetheric_rift_system_configuration.py:231-330
  - src/melder/aether/aether.py:47-88
  - src/melder/aether/aether.py:272-340
  - src/melder/aether/aetheric_rift_system/aetheric_rift_system.py:33-44
  - src/melder/aether/aetheric_rift_system/aetheric_rift_system.py:179-195
  IMPACT: Compaction and the next engineering pass can resume from the AR
    state-object / managed-frame-responsibility discussion instead of reopening
    the ARS governance schema again.
  NEXT: close the completed March 28 conduit/test tickets, sync the board, and
    continue the ARS -> AR/state design conversation from the locked config
    surface.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-03-28T21:54:26Z
  TYPE: DECISION
  CLAIM: The next AR refactor should stop forcing the public API through
    `Aether` and stop treating a separate public-facing `RiftState` as a core
    concept. The simpler direction is a second singleton root, `Nexus`,
    privately hosted by `Aether` but not facaded by it: `Nexus` owns only Rift
    registry/config/lifecycle state, creates `Rift` objects, and leaves real
    `Aether` targeting to the live `Rift` objects themselves.
  EVIDENCE:
  - src/melder/aether/aether.py:47-88
  - src/melder/aether/aether.py:272-423
  - src/melder/aether/aetheric_rift_system/aetheric_rift_system.py:22-57
  - src/melder/aether/aetheric_rift_system/aetheric_rift_system.py:179-394
  - src/melder/aether/aetheric_rift_system/aetheric_rift/aetheric_rift.py:13-63
  - src/melder/aether/aetheric_rift_system/aetheric_rift_state/aetheric_rift_state.py:8-41
  IMPACT: The current ARS governance implementation is not the right place to
    keep widening the old shell/state/facade model. The next slice should be a
    dedicated Nexus singleton/public-surface refactor with code and doc updates.
  NEXT: create a dedicated follow-up task and patch artifacts for the Nexus
    singleton/public-surface refactor, then route the board to that task before
    implementation.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
This task now carries the active AR lane after the governance implementation
landed. The process-wide ARS surface is locked around four groups:
creation/access governance, internal system-frame topology, target/userland
frame governance, and per-Rift defaults. The next refinement is below ARS:
define what `AethericRiftState` should store, how ARS tracks managed frame
responsibility, and how AR/workspace layers consume those assignments without
reopening the system-level config schema.
