# Task: Investigate Renaming Dynamic RiftSpace To Codegen
- Completed: 2026-04-26T11:39:24Z
- Summary: Closed after the bounded AR-layer rename feasibility and migration
  boundary were made explicit.

## Metadata
- Task ID: TASK-2026-04-13-investigate-renaming-dynamic-rift-space-to-codegen
- Epic: EPIC-2026-04-13-investigate-april-11-12-aethericrift-history-and-next-steps
- Status: done
- Owner: codex
- Priority: p0
- Created: 2026-04-13T23:54:10Z
- Updated: 2026-04-26T11:39:24Z

## Objective
Investigate whether the current `dynamic` room/mode can be cleanly renamed to
`codegen`, identify the exact blast radius, and determine whether the runtime
semantics are already narrow enough to make that rename honest.

## Ticket Contract
- ENTRY_GATE: the user explicitly asked to investigate renaming `dynamic` to
  `codegen` and to verify whether it can be done properly.
- EXECUTION_BOUNDARY: investigation, blast-radius mapping, and rename-risk
  assessment only.
- DEPENDENCIES:
  - src/melder/aether/nexus/configuration/rift_space_type.py
  - src/melder/aether/nexus/configuration/rift_configuration.py
  - src/melder/aether/nexus/nexus.py
  - src/melder/aether/nexus/rift/rift.py
  - src/melder/aether/nexus/rift/rift_space/dynamic_rift_space.py
  - src/melder/aether/nexus/rift/rift_space/command_system/dynamic_command_system.py
  - src/melder/utilities/interfaces/interfaces.py
  - codex/context_compass/system_docs/src_architecture.md
  - codex/context_compass/system_docs/src_components.md
  - codex/context_compass/tickets/artifacts/2026-04-08_rift_access_modes_static_capability_dynamic_model.md
  - codex/context_compass/tickets/artifacts/2026-04-12_capability_rift_space_runtime_model.md
- EXIT_GATE: the task records whether the rename is semantically honest now,
  what files/contracts/tests/docs would be touched, and what risks/blockers
  remain.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if the current `dynamic`
  semantics are still too broad/manual-runtime-oriented to justify a rename to
  `codegen` yet.

## Scope Boundaries
- In scope:
  - current `dynamic` semantics
  - rename blast radius across source/tests/docs/tickets
  - compatibility and migration risks
- Out of scope:
  - performing the rename
  - implementing new dynamic/codegen behavior
  - unrelated AR cleanup

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: the user explicitly requested a feasibility investigation
  for renaming `dynamic` to `codegen`.

## Steps / Checklist
- [ ] Read the current room-mode source/docs/tickets for `dynamic`.
- [ ] Map every meaningful `dynamic` symbol and contract surface.
- [ ] Determine whether `dynamic` already means "codegen room" strongly enough.
- [ ] Document rename blast radius and risks in `## Notes`.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- evidence-backed rename feasibility assessment
- concrete blast-radius inventory
- next-step recommendation

## Files / Paths Impacted
- codex/context_compass/tickets/tasks/2026-04-13_investigate_renaming_dynamic_rift_space_to_codegen_task.md
- codex/context_compass/attention_board.md

## Validation
- Not run.
- Recommended commands:
  - `git diff -- codex/context_compass`

## Risks / Rollback Notes
- Risk: renaming to `codegen` too early could lie about the current runtime if
  the room still materially includes broader non-codegen behavior.
  Rollback: keep `dynamic` until the runtime and docs narrow the meaning.

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
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: none

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-04-13T23:54:10Z
  TYPE: PLAN
  CLAIM: The rename question is no longer cosmetic. If `capability` is now the
    honest non-codegen room, then `dynamic` may be the wrong name for the final
    room. But we should not rename it blindly: we need to verify whether the
    current source, interfaces, tests, and docs already treat `dynamic` as the
    codegen room strongly enough for `codegen` to be honest.
  EVIDENCE:
  - user_instruction: "the final layer I do want to just call it codegen instead of dynamic"
  - src/melder/aether/nexus/rift/rift_space/dynamic_rift_space.py:17-29
  - src/melder/aether/nexus/configuration/rift_space_type.py:16-22
  IMPACT: We need a bounded rename-feasibility pass before we touch public
    names or ticket language.
  NEXT: map the current `dynamic` semantics and blast radius across source,
    tests, docs, and tickets.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-13T23:54:10Z
  TYPE: FACT
  CLAIM: The current `dynamic` blast radius is larger than one AR room class.
    It appears in:
    - AR room/type/configuration names (`RiftSpaceType.dynamic`,
      `DynamicRiftSpace`, `DynamicCommandSystem`)
    - target-frame eligibility rules in `Nexus`
    - interfaces and tests
    - older retained artifacts and many completed tickets
    - lower Melder runtime language, where "dynamic" still means something
      broader than codegen: conduit cloud, linking, clusters, ownership
      transfer, contract/link policy, and mutation-facing surfaces
    So a clean rename is possible only if we separate:
    1) AR room naming
    2) lower Melder `system_state == dynamic` and conduit dynamic-environment
       semantics
  EVIDENCE:
  - src/melder/aether/nexus/rift/rift_space/dynamic_rift_space.py:13-29
  - src/melder/aether/nexus/rift/rift_space/command_system/dynamic_command_system.py:6-20
  - src/melder/aether/nexus/configuration/rift_space_type.py:16-22
  - src/melder/aether/nexus/nexus.py:2370-2422
  - src/melder/utilities/interfaces/interfaces.py:7493-7495
  - tests/unit/melder/aether/test_nexus.py:786-818
  - tests/unit/melder/aether/test_nexus.py:3946-4033
  - src/melder/aether/conduit/conduit.py:2800-2815
  - src/melder/aether/conduit/conduit.py:2880-2903
  - src/melder/aether/conduit/conduit.py:3979-3998
  IMPACT: We should not treat this as a global "replace dynamic with codegen"
    sweep. The feasible rename boundary is probably the AR room/type layer
    first, with compatibility handling at that boundary.
  NEXT: inspect the AR interfaces/tests/config docs more closely to decide
    whether renaming the room layer alone is semantically honest now.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-13T23:54:10Z
  TYPE: FACT
  CLAIM: The AR room-layer rename looks feasible if it stays scoped to the
    AR room/type contract, but not if it tries to rewrite lower Melder
    `dynamic` semantics. Current AR evidence says:
    - `dynamic` room names appear in `RiftSpaceType`, `DynamicRiftSpace`,
      `DynamicCommandSystem`, `IDynamicRiftSpace`, docs, and AR-focused tests
    - that room is already described as "reserved for later codegen-oriented
      differentiation" and the target-frame rules for it are stricter than for
      capability (`ai_native_enabled=True`, `system_state=dynamic`)
    - but lower Melder/runtime code still uses "dynamic" to mean the substrate
      posture that enables conduit cloud, linking, cluster operations,
      ownership transfer, and mutation-adjacent behavior
    So the honest rename boundary is:
    1) AR room/type names and their tests/docs
    2) keep lower `SystemState.dynamic` and conduit dynamic-environment
       semantics unchanged for now
  EVIDENCE:
  - src/melder/aether/nexus/rift/rift_space/dynamic_rift_space.py:17-29
  - src/melder/aether/nexus/rift/rift_space/command_system/dynamic_command_system.py:12-20
  - src/melder/aether/nexus/configuration/rift_space_type.py:16-22
  - src/melder/aether/nexus/nexus.py:2414-2422
  - src/melder/utilities/interfaces/interfaces.py:7493-7495
  - tests/unit/melder/aether/test_nexus.py:786-818
  - tests/unit/melder/aether/test_nexus.py:3946-4033
  - codex/context_compass/system_docs/src_architecture.md:475-491
  - codex/context_compass/system_docs/src_components.md:519-584
  - src/melder/aether/conduit/conduit.py:2800-2815
  - src/melder/aether/conduit/conduit.py:2880-2903
  - src/melder/aether/conduit/conduit.py:3979-3998
  IMPACT: We can likely rename the AR room to `codegen`, but it should be a
    bounded AR compatibility migration, not a repo-wide semantic replacement
    of every `dynamic` term.
  NEXT: inventory the exact AR-layer rename surface and decide whether a
    compatibility alias (`dynamic` -> `codegen`) is required for configuration
    and tests.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-13T23:54:10Z
  TYPE: FACT
  CLAIM: The `system_state` responsibility is already layered the right way for
    an AR-room rename. `Nexus` validates AR target-frame eligibility from the
    target frame's bound configuration, not from any AR room object or from the
    conduit directly. Specifically, the stricter current `dynamic` room gate is:
    - `rift_enabled=True`
    - `ai_native_enabled=True`
    - `system_state == dynamic`
    at the target frame configuration layer. Separately, lower conduit runtime
    behavior derives its own `__dynamic_environment__` from the lower bound
    `Configuration.system_state`. So the rename can leave the lower frame and
    conduit convention alone:
    - frame/runtime posture stays `dynamic`
    - AR room can become `codegen`
  EVIDENCE:
  - src/melder/aether/nexus/nexus.py:2362-2425
  - src/melder/spellbook/configuration/configuration.py:303-316
  - src/melder/spellbook/configuration/configuration.py:968-990
  - src/melder/aether/conduit/conduit.py:161-178
  - src/melder/aether/conduit/conduit.py:966-967
  IMPACT: We do not need to rename lower `SystemState.dynamic` to make the AR
    room rename coherent. The frame is already the owner of the posture rule,
    and conduit inherits that lower posture.
  NEXT: stage the bounded AR-room rename implementation task and patch docs so
    the rename stays above the lower frame/conduit convention.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-13T23:54:10Z
  TYPE: DECISION
  CLAIM: A bounded AR-layer rename is justified. The room/type layer should
    move from `dynamic` to `codegen`, while lower Melder substrate semantics
    remain expressed through `SystemState.dynamic` and conduit
    `__dynamic_environment__`. The rename should therefore target AR-facing
    room names, config conversion, interfaces, docs, and tests, and it should
    preserve a compatibility path for legacy `dynamic` AR inputs during the
    transition.
  EVIDENCE:
  - src/melder/aether/nexus/rift/rift_space/dynamic_rift_space.py:17-29
  - src/melder/aether/nexus/configuration/rift_space_type.py:16-22
  - src/melder/aether/nexus/nexus.py:2362-2425
  - src/melder/spellbook/configuration/configuration.py:303-316
  IMPACT: We can move from investigation to implementation without lying about
    the lower runtime model.
  NEXT: create the implementation task and patch artifacts for the AR room
    rename.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
This task owns the feasibility investigation for renaming the `dynamic` room to
`codegen`.
