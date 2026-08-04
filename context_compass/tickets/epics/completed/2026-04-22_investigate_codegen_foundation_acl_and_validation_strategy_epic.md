# Epic: Investigate Codegen Foundation ACL And Validation Strategy
- Completed: 2026-04-26T11:39:24Z
- Summary: Closed after the codegen foundation direction was established and
  handed off to the dedicated implementation epic and landed runtime slices.

## Metadata
- Epic ID: EPIC-2026-04-22-investigate-codegen-foundation-acl-and-validation-strategy
- Status: done
- Owner: codex
- Priority: p0
- Created: 2026-04-23T00:07:30Z
- Updated: 2026-04-26T11:39:24Z
- Target Window: 2026-Q2
- Related Program/Initiative: Codegen room foundation over the completed capability substrate

## Problem / Opportunity
Capability is now in a strong enough place that the next real layer is codegen.

Capability proves the room/workstation/frame substrate:
- explicit frame linking
- explicit Nexus-created rooted conduits
- runtime object access through the mediated command surface
- workstation binding and target execution
- multi-frame handoff inside one room
- cleanup behavior

But codegen is not "capability plus a giant command family."

Current source makes that boundary clearer than it was when this epic was first
opened:
- `CodegenCommandSystem` now owns a deliberately slim helper surface plus the
  placeholder `validate_codegen(...)` and `execute_codegen(...)` seams.
- `CodegenProjection` already gives codegen a detached ACL configuration plus a
  detached compiled access surface for one target frame.
- `Rift` already exposes `_get_required_codegen_projection(...)`.
- `src/melder/aether/nexus/rift/codegen_system/` exists but is still empty,
  which means the real codegen runtime engine has an obvious home instead of
  having to expand `CodegenCommandSystem` into another god object.

Codegen introduces different system requirements:
- generated Python that is compiled/validated and then executed
- AST validation before execution
- accepted/rejected execution results
- codegen execution history and normal logs so agents/users can inspect what ran
- hook points for overwatch and sentinel monitoring
- ACL semantics around whether codegen can execute and what workspace objects
  enter the execution namespace

The opportunity is to define the foundational codegen system clearly before
implementation starts, using the now-proven capability substrate as the lower
execution layer instead of mixing the two concepts.

## MRP Alignment (Most Reasonable Product)
The MRP is not "make `CodegenRiftSpace` different somehow."
The MRP is "define the smallest trustworthy codegen system foundation that can
compile, validate, execute, monitor, and report generated Python on top of the
already-proven capability mechanics."

That means:
- keep the public room surface small: selected runtime helpers plus
  `validate_codegen(...)` and `execute_codegen(...)`
- keep `CodegenCommandSystem` thin and move the real codegen engine into
  `src/melder/aether/nexus/rift/codegen_system/`
- define the codegen execution namespace and AST validation model explicitly
- define what ACLs mean for codegen namespace exposure and execution authority
- define the accepted/rejected result and history/log contract
- define overwatch/sentinel hooks around execution

If codegen starts as either a vague capability alias or a bloated artifact
workflow, the system will miss the real foundation: generated Python executing
against live workspace objects under validation and monitoring.

## Ticket Contract
- ENTRY_GATE: capability mechanics are now strong enough to act as the
  substrate beneath codegen.
- EXECUTION_BOUNDARY: investigation and strategy only for codegen room
  foundations, ACL semantics, AST validation, execution namespace,
  overwatch/sentinel monitoring, and codegen history/log boundaries.
- DEPENDENCIES:
  - src/melder/aether/nexus/rift/rift_space/codegen_rift_space.py
  - src/melder/aether/nexus/rift/command_system/codegen_command_system.py
  - src/melder/aether/nexus/rift/codegen_system/
  - src/melder/aether/nexus/rift/projection/codegen_projection.py
  - src/melder/aether/nexus/rift/rift.py
  - src/melder/aether/nexus/acl/configurations/frame_acl_codegen_configuration.py
  - src/melder/aether/nexus/acl/configurations/profiles/codegen/
  - src/melder/aether/nexus/acl/validator/profiles/codegen/
  - codex/context_compass/tickets/artifacts/codegen_validation_pipeline_design.md
  - codex/context_compass/system_docs/src_architecture.md
  - codex/context_compass/system_docs/src_components.md
  - tickets/tasks/2026-04-22_expand_capability_space_frame_and_workstation_integration_tests_task.md
  - tickets/tasks/2026-04-22_expand_capability_json_failure_and_cleanup_integration_tests_task.md
- EXIT_GATE: the current codegen baseline, missing foundation pieces, ACL
  strategy, validation strategy, and implementation order are explicit enough
  to stage follow-on stories/tasks without guessing.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if the codegen foundation
  implies a broader AR/runtime redesign instead of a bounded layer on top of
  capability.

## Goals (Outcomes)
- Reconstruct the actual current codegen baseline from source.
- Make the capability-to-codegen handoff explicit:
  capability remains the prepared-runtime execution substrate, while codegen
  becomes the governed generated-Python execution layer above it.
- Define the thin-facade split:
  `CodegenCommandSystem` owns the public room surface while
  `codegen_system/` owns AST validation, namespace construction, compile/exec,
  hooks, and result shaping.
- Define how codegen should differ from capability at the room, command,
  projection, monitoring, and memory levels.
- Define the intended codegen ACL model for execution authority and namespace
  exposure, and how it composes with existing view/command/codegen family chains.
- Define the AST validation, compile/exec, accepted/rejected result, and
  history/log model for codegen work.
- Produce an implementation strategy and milestone order, not code.

## Non-Goals (Explicit Exclusions)
- Implementing the codegen system.
- Expanding capability further unless the investigation proves a prerequisite gap.
- Rewriting the existing ACL subsystem without evidence.
- Building prompts, model adapters, or product UX in this epic.

## Scope Boundaries
- In scope:
  - `CodegenRiftSpace`
  - `CodegenCommandSystem`
  - `codegen_system/`
  - `CodegenProjection`
  - codegen ACL configuration/profile/validator surfaces
  - codegen AST validation, namespace, execution, monitoring, and history/log strategy
  - capability-to-codegen layering strategy
- Out of scope:
  - actual codegen runtime implementation
  - model integration details
  - product-layer UX
  - public codegen artifact/session/workflow APIs
  - object-level creator/provenance fields

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: the user explicitly requested an investigation epic for
  codegen foundation strategy and asked that no code be built in this lane yet.

## Success Metrics
- One explicit epic owns the codegen-foundation investigation.
- The current codegen baseline is evidenced from source rather than assumed.
- The ACL, validation, monitoring, and implementation-order strategy is
  explicit enough to decompose into follow-on work.

## Requirements (Functional + Non-Functional)
- Functional:
  - explain what codegen inherits from the shared room/runtime substrate versus
    what it adds itself
  - define the public `CodegenCommandSystem` helper + execution surface
  - define what belongs in `codegen_system/` instead of the command facade
  - define the codegen ACL semantics
  - define AST validation and compile/exec behavior
  - define monitoring/event/memory expectations for codegen execution history
  - define the minimal codegen method surface, not a workflow command family
  - define implementation order
- Non-functional:
  - no handwaving
  - no implementation in this epic
  - keep strategy aligned to the existing proven runtime substrate

## Constraints / Assumptions
- Capability is intentionally a strong core, not an everything-surface.
- Command ownership refactor is already complete, so codegen no longer starts
  from capability parity by accident; it starts from the slimmer shared base
  plus its explicitly selected helpers.
- Codegen should use the shared room/runtime substrate where that substrate is
  already proven instead of rebuilding mechanics.
- Separate ACL family chains for view/command/codegen already exist, so the
  strategy should respect that current architecture unless source evidence says
  it is insufficient.
- Existing room-local event and memory systems should be considered as likely
  integration points for codegen telemetry before inventing a second unrelated
  monitoring stack.
- CommandOps/logger history is the provenance/accountability layer for who ran
  codegen. Melder runtime objects should not grow new creator/provenance fields
  just to duplicate that signal.
- `src/melder/aether/nexus/rift/codegen_system/` is currently empty, so this
  epic can define its object model cleanly instead of working around an
  existing implementation.

## Dependencies / External References
- `src/melder/aether/nexus/rift/rift_space/capability_rift_space.py`
- `src/melder/aether/nexus/rift/rift_space/codegen_rift_space.py`
- `src/melder/aether/nexus/rift/command_system/capability_command_system.py`
- `src/melder/aether/nexus/rift/command_system/codegen_command_system.py`
- `src/melder/aether/nexus/rift/codegen_system/`
- `src/melder/aether/nexus/rift/projection/codegen_projection.py`
- `src/melder/aether/nexus/rift/rift.py`
- `src/melder/aether/nexus/acl/configurations/frame_acl_codegen_configuration.py`
- `src/melder/aether/nexus/acl/configurations/profiles/codegen/`
- `src/melder/aether/nexus/acl/validator/profiles/codegen/`
- `codex/context_compass/tickets/artifacts/codegen_validation_pipeline_design.md`
- `codex/context_compass/system_docs/src_architecture.md`
- `codex/context_compass/system_docs/src_components.md`

## Milestones (Track Progress)
- [ ] Milestone 1: Reconstruct the current codegen baseline from source and docs.
      Success means the room, command, projection, ACL, and validator state is
      described precisely enough that no one has to guess what codegen
      currently is.
- [ ] Milestone 2: Define the codegen ACL, validation, and monitoring strategy.
      Success means the thin command-facade split, minimal method surface,
      ACL/namespace layering, AST validation, execution hooks, history, and
      event/memory posture are explicit.
- [ ] Milestone 3: Define the implementation order and follow-on story/task decomposition.
      Success means the first implementation slices can be staged without
      re-litigating the architecture.

## Stories (Required to Complete)
- [ ] Story: reconstruct current codegen room, command, projection, and ACL baseline
- [ ] Story: design `codegen_system/` object ownership and thin command-facade split
- [ ] Story: design codegen exec namespace, AST validation, and minimal command surface
- [ ] Story: design codegen ACL/namespace exposure strategy over the current capability substrate
- [ ] Story: design codegen history, event, overwatch, and sentinel monitoring strategy
- [ ] Story: stage implementation-order and follow-on work for codegen foundation

## Tasks (Cross-Cutting or Epic-Level)
- [ ] Task: read the existing codegen runtime and ACL/validator surfaces
- [ ] Task: map the selected public helper surface already owned by `CodegenCommandSystem`
- [ ] Task: define the first `codegen_system/` object set and ownership split
- [ ] Task: compare capability and codegen postures explicitly
- [ ] Task: define codegen exec namespace and accepted/rejected result contract
- [ ] Task: define codegen monitoring/event/memory expectations
- [ ] Task: Verify Ticket Microcycle enforcement across active tickets/stories/tasks.

## Acceptance Criteria (Epic Done)
- The current codegen baseline is documented with source-backed evidence.
- The capability-to-codegen layering strategy is explicit.
- The codegen ACL, AST validation, namespace, execution, and monitoring model is explicit enough to implement.
- The implementation order is explicit enough to decompose into stories/tasks.

## Risks / Mitigations
- Risk: codegen strategy turns into vague aspiration instead of a buildable
  foundation.
  Mitigation: tie every major strategy claim to current source or mark it UNKNOWN.
- Risk: codegen inherits too much from capability and loses the governance
  distinction that makes codegen different.
  Mitigation: make AST validation, namespace exposure, execution history, and
  sentinel/overwatch hooks first-class parts of the strategy.
- Risk: codegen strategy drifts back into a bloated public API.
  Mitigation: keep the public surface minimal: execute generated Python plus
  the smallest compile/history support needed, not a command workflow.
- Risk: `CodegenCommandSystem` becomes another god object once AST/namespace
  logic is added.
  Mitigation: keep the public command facade thin and move the actual engine
  into `src/melder/aether/nexus/rift/codegen_system/`.

## Applicable Anti-Patterns
- [ ] No epic-state transition without story-level evidence.
- [ ] No closure while required stories are incomplete or unaccepted.
- [ ] No program claims without source evidence from story/task notes.

## Validation / Test Approach
- Investigation only in this epic.
- Validation is evidence quality:
  - current codegen baseline traced from source
  - strategy tied to actual ACL/validator/runtime surfaces
  - no unevidenced implementation claims

## Rollout / Adoption Plan
- Read the current codegen and capability/codegen-adjacent surfaces.
- Capture the real current baseline and gaps.
- Define the strategy in this order:
  1. freeze the public codegen surface around the already-selected runtime
     helpers plus `validate_codegen(...)` and `execute_codegen(...)`
  2. define `codegen_system/` as the runtime engine package rather than
     expanding `CodegenCommandSystem`
  3. define the first object set inside `codegen_system/`:
     `CodegenSystem`, AST validator, namespace builder, execution result, and
     hook dispatcher only if it earns its keep
  4. define the execution namespace:
     workstation, command, rift/space/viewer, target, frame name, and any
     exposed direct runtime objects
  5. define AST validation and compile gates before `exec`
  6. define how `CodegenProjection.compiled_access_surface` and codegen ACLs
     gate execution authority and namespace exposure
  7. define codegen history/log records and hook points for overwatch/sentinel
     monitoring
  8. define accepted/rejected result shape without creating public artifact or
     session APIs
- Stage follow-on stories/tasks for implementation after the user reviews the epic.

## Open Questions
- Should `validate_codegen(...)` remain the only public preflight surface
  beside `execute_codegen(...)`, or does codegen need another public helper
  beyond the already-selected runtime helper set?
- What is the minimum AST validation stack before generated Python can be
  compiled/executed?
- Which stable names belong in the initial execution namespace:
  `rift`, `space`, `viewer`, `workstation`, `command`, `target`, `frame_name`,
  or additionally direct bound objects as locals?
- How should codegen monitoring relate to the room-local event system and
  memory system?
- What should codegen ACLs actually gate: execution authority, namespace object
  exposure, direct runtime object exposure, imports/builtins, or all of those?
- Should codegen history store full generated source, source hash, or both?
- What hook points are required for overwatch and sentinel monitoring:
  pre-validate, post-validate, pre-exec, post-exec, exception, or all of them?

## Decision Log
- 2026-04-22: User requested an investigation-only epic for codegen
  foundation, ACLs, and validation, with no code implementation yet.
- 2026-04-23: Direction corrected: codegen is generated Python compiled and
  executed against live workspace objects. Public surface should stay minimal,
  centered on `execute_codegen(...)`, with AST validation, codegen history/logs,
  overwatch/sentinel hooks, and ACL-gated namespace exposure. Do not design a
  public artifact/session/workflow API or object-level provenance fields.
- 2026-04-24: Direction tightened again: `CodegenCommandSystem` now owns a
  selected helper subset plus placeholder `validate_codegen(...)` and
  `execute_codegen(...)`, while the real runtime engine should live under the
  currently empty `src/melder/aether/nexus/rift/codegen_system/` package
  instead of bloating the command facade.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: false
- ARTIFACT_PATHS:
  - none
- DISPOSITION: delete_on_close
- CLEANUP_TRIGGER: n/a

## Notes
- DATETIME: 2026-04-23T00:07:30Z
  TYPE: PLAN
  CLAIM: This epic exists to make the next major layer explicit. Capability is
    now strong enough to act as the substrate beneath codegen, so the next move
    is to reconstruct the real codegen baseline and define the codegen
    foundation strategy before implementation starts.
  EVIDENCE:
  - user_instruction: "investigate capability and the codegen stuff we have built and make a strategy for how we can start implementing the foundation for codegen system, and how the acls will work and validation"
  - user_instruction: "don't build anything but make an epic to investigate"
  IMPACT: The next step is source-backed investigation and strategy, not coding.
  NEXT: read the current codegen room, command, projection, and ACL/validator surfaces.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-23T00:07:30Z
  TYPE: FACT
  CLAIM: The room/runtime side of codegen is still mostly a placeholder. `CodegenRiftSpace`
    only fixes `space_kind='codegen'` and composes `CodegenCommandSystem`, while
    `CodegenCommandSystem` itself currently just inherits the shared broad
    runtime command posture from `CommandSystem` without adding a real codegen
    execution model.
  EVIDENCE:
  - src/melder/aether/nexus/rift/rift_space/codegen_rift_space.py:12-78
  - src/melder/aether/nexus/rift/command_system/codegen_command_system.py:6-16
  IMPACT: Codegen implementation should not start by pretending the room/runtime
    layer is already defined; that layer still needs a real generated-Python
    compile/validate/exec contract.
  NEXT: trace the projection and ACL side to see what is already richer than
    the room/runtime placeholder.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-23T00:07:30Z
  TYPE: FACT
  CLAIM: The projection and ACL side of codegen is much more developed than the
    room/runtime side. `Nexus` already builds a detached `CodegenProjection`
    inside each `FrameProjectionSet`, the frame ACL container already owns a
    separate named codegen family chain, the builder can draft and commit
    codegen configs, the validator has codegen-specific generic/safe/precision
    strategy dispatch, and the compiler already derives `allowed_commands` from
    codegen frame/conduit/spell/capability rulesets.
  EVIDENCE:
  - src/melder/aether/nexus/nexus.py:1643-1664
  - src/melder/aether/nexus/rift/projection/frame_projection_set.py:10-98
  - src/melder/aether/nexus/rift/projection/codegen_projection.py:6-80
  - src/melder/aether/nexus/acl/frame_acl_container.py:750-895
  - src/melder/aether/nexus/acl/builder/frame_acl_builder.py:140-181
  - src/melder/aether/nexus/acl/builder/frame_acl_builder.py:235-245
  - src/melder/aether/nexus/acl/builder/frame_acl_builder.py:290-362
  - src/melder/aether/nexus/acl/validator/frame_acl_validator.py:117-140
  - src/melder/aether/nexus/acl/validator/frame_acl_validator.py:198-201
  - src/melder/aether/nexus/acl/validator/frame_acl_validator.py:786-842
  - src/melder/aether/nexus/acl/frame_acl_compiler.py:123-173
  - src/melder/aether/nexus/acl/frame_acl_compiler.py:425-473
  IMPACT: The first real codegen implementation should probably start by making
    `CodegenCommandSystem` consume the existing codegen projection/ACL contract
    for namespace exposure and execution authority instead of redesigning ACL
    storage from scratch.
  NEXT: map the minimal compile/execute/history method surface and validator
    constraints into a first-cut implementation order.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-23T00:07:30Z
  TYPE: FACT
  CLAIM: Current codegen ACL semantics are already quite specific. The codegen
    family distinguishes frame, conduit, spell, and capability rulesets;
    standard profiles (`safe`, `hybrid`, `permissive`, `precision`) differ on
    operations like `local_create`, `invoke_method`, `read_attribute`,
    `write_attribute`, `dynamic_access`, `mutation`, `contract_override`,
    `unsafe_reflection`, and `dunder_access`; and the validator currently
    enforces profile-version consistency plus extra `safe` and `precision`
    constraints rather than a full generated-artifact validation stack.
  EVIDENCE:
  - src/melder/aether/nexus/acl/configurations/profiles/codegen/safe_profile.py:9-58
  - src/melder/aether/nexus/acl/configurations/profiles/codegen/hybrid_profile.py:9-57
  - src/melder/aether/nexus/acl/configurations/profiles/codegen/permissive_profile.py:9-56
  - src/melder/aether/nexus/acl/configurations/profiles/codegen/precision.py:9-53
  - src/melder/aether/nexus/acl/validator/profiles/codegen/safe_strategy.py:1-63
  - src/melder/aether/nexus/acl/validator/profiles/codegen/precision_strategy.py:1-23
  - src/melder/aether/nexus/acl/configurations/frame_acl_codegen_configuration.py:15-546
  IMPACT: Codegen validation should be split conceptually:
    1. current ACL/profile validation already governs what codegen is allowed to
       attempt
    2. future generated-Python AST validation still needs to be designed above
       that layer
  NEXT: write the strategy so ACL validation stays a lower policy gate while
    AST validation becomes a separate upper execution gate before compile/exec.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-23T00:07:30Z
  TYPE: DECISION
  CLAIM: Recommended foundation order:
    1. formalize the minimal codegen method surface around generated-Python
       execution, centered on `execute_codegen(...)`
    2. define the exec namespace and how codegen ACLs gate which workspace
       objects are exposed
    3. define the AST validation/compile gate before `exec`
    4. define codegen execution history plus overwatch/sentinel hook points
       using existing logs/history rather than object-level provenance fields
    5. implement `CodegenCommandSystem` as `CapabilityCommandSystem` plus the
       governed codegen execution method instead of another capability-like
       pass-through
  EVIDENCE:
  - src/melder/aether/nexus/rift/command_system/codegen_command_system.py:6-16
  - src/melder/aether/nexus/rift/projection/codegen_projection.py:6-80
  - src/melder/aether/nexus/acl/frame_acl_compiler.py:425-473
  - tests/unit/melder/aether/test_nexus_orchestration_and_lifecycle.py:449-468
  IMPACT: This keeps codegen implementation aligned to the already-proven
    capability substrate while giving codegen its own validated Python
    execution model instead of turning it into either a renamed capability room
    or a bloated artifact/session API.
  NEXT: present the epic as the current strategy baseline and stage follow-on
    stories/tasks only after user review.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-23T11:26:30Z
  TYPE: DECISION
  CLAIM: Codegen direction is corrected to the permanent model:
    codegen is generated Python compiled/validated/executed against a prepared
    workspace namespace. The public codegen surface should remain minimal,
    centered on `execute_codegen(...)` with only the smallest compile/history
    helpers if they are truly needed. There should be no public artifact
    manager, no transaction/session workflow API, and no object-level creator
    provenance fields. Accountability comes from codegen history/data plus the
    existing CommandOps/logger trail.
  EVIDENCE:
  - user_instruction: "codegen is simple not sophisticated"
  - user_instruction: "execute_codegen"
  - user_instruction: "theres an AST validation cycle inside it"
  - user_instruction: "we still have a history of whats executed"
  - user_instruction: "we do not need a shit load of methods for this"
  IMPACT: Follow-on implementation must prioritize namespace construction,
    AST validation, compile/exec behavior, execution history/logging, and
    hookable overwatch/sentinel monitoring, not a multi-command workflow.
  NEXT: decompose follow-on work around `execute_codegen(...)`, AST validation,
    codegen history, namespace ACL exposure, and monitoring hooks.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-24T11:30:39Z
  TYPE: FACT
  CLAIM: The live codegen room surface is now explicitly slim instead of
    capability-parity-by-default. `CodegenCommandSystem` inherits only the
    slimmer shared base, owns a selected runtime-helper subset itself, and
    still exposes `validate_codegen(...)` and `execute_codegen(...)` only as
    rejected placeholders.
  EVIDENCE:
  - src/melder/aether/nexus/rift/command_system/codegen_command_system.py:8-25
  - src/melder/aether/nexus/rift/command_system/codegen_command_system.py:28-52
  - src/melder/aether/nexus/rift/command_system/codegen_command_system.py:438-547
  IMPACT: The codegen investigation no longer needs to argue for a slim public
    surface in the abstract; the source already has that shape, so the next
    design step is the internal engine behind those seams.
  NEXT: define what belongs in `codegen_system/` versus what stays in
    `CodegenCommandSystem`.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-24T11:30:39Z
  TYPE: FACT
  CLAIM: The runtime already has the right lower seams for a separate internal
    codegen engine. `CodegenProjection` owns a live frame descriptor reference
    plus detached ACL/configuration state and a detached compiled access
    surface, and `Rift` already exposes `_get_required_codegen_projection(...)`
    for frame-targeted consumers.
  EVIDENCE:
  - src/melder/aether/nexus/rift/projection/codegen_projection.py:6-20
  - src/melder/aether/nexus/rift/projection/codegen_projection.py:31-47
  - src/melder/aether/nexus/rift/projection/codegen_projection.py:65-93
  - src/melder/aether/nexus/rift/rift.py:691-702
  IMPACT: Namespace construction and execution authority do not need a new
    projection type; the codegen runtime can consume the existing projection
    contract directly.
  NEXT: define how `compiled_access_surface` gates namespace exposure and
    execution authority inside the future engine.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-24T11:30:39Z
  TYPE: DECISION
  CLAIM: The clean implementation split is now explicit: keep
    `CodegenCommandSystem` as the public room facade and put the real engine in
    `src/melder/aether/nexus/rift/codegen_system/`. The first object set should
    stay small: `CodegenSystem`, AST validator, namespace builder, execution
    result, and hooks only if needed for overwatch/sentinel integration.
  EVIDENCE:
  - shell_command: Get-ChildItem -Force src\\melder\\aether\\nexus\\rift\\codegen_system | Select-Object Name,PSIsContainer,Length -> only `__init__.py` exists and its length is 0
  - src/melder/aether/nexus/rift/command_system/codegen_command_system.py:14-25
  - codex/context_compass/tickets/artifacts/codegen_validation_pipeline_design.md:15-28
  - codex/context_compass/tickets/artifacts/codegen_validation_pipeline_design.md:75-113
  - user_instruction: "we have a directory where we can put all this so thats fine"
  IMPACT: The next codegen implementation slice should create the internal
    engine package rather than pouring AST/compile/exec logic directly into the
    command surface.
  NEXT: update the board and follow-on implementation staging around the thin
    facade plus internal engine model.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-24T11:30:39Z
  TYPE: DECISION
  CLAIM: The older recommendation to treat codegen as
    `CapabilityCommandSystem` plus governed execution is now superseded by the
    completed command-ownership refactor. Codegen starts from the slimmer
    shared base plus its explicitly selected helper surface, not from
    capability inheritance.
  EVIDENCE:
  - src/melder/aether/nexus/rift/command_system/codegen_command_system.py:18-25
  - src/melder/aether/nexus/rift/command_system/codegen_command_system.py:28-52
  - user_instruction: "we don't just want to extend the capability system"
  IMPACT: Follow-on codegen work should not be staged as a capability extension
    layer; it should be staged as a thin room facade over a separate internal
    codegen engine.
  NEXT: keep the first codegen implementation slice centered on the
    `codegen_system/` package and the two public codegen seams.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-25T00:01:28Z
  TYPE: DECISION
  CLAIM: The implementation decomposition is now staged. The next codegen lane
    is no longer abstract investigation; it is the ready implementation epic
    that breaks `codegen_system/` into root, validation, validation-strategies,
    namespace, namespace-strategies, execution, and observability stories with
    one task per planned non-init Python file.
  EVIDENCE:
  - codex/context_compass/tickets/epics/2026-04-25_implement_codegen_system_runtime_epic.md:1-127
  IMPACT: This investigation epic can remain the strategy anchor while the new
    implementation epic becomes the execution handoff point.
  NEXT: start implementation from the root directory story when the user says go.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Closure Confirmation
- [ ] Work walkthrough shared with user
- [ ] Acceptance criteria confirmed by user
- [ ] Applicable anti-pattern checks are clear or escalated with evidence.

## Noting Behavior
- Note focus: program-level direction, cross-story tradeoffs, and tranche order.
- Add notes when priorities, sequencing, or scope boundaries change.
- Reference story/task evidence instead of duplicating tactical execution logs.
- Keep notes append-only and preserve UNKNOWN-first promotion discipline.

## Context / Handoff Summary
This epic owns the investigation and strategy lane for the codegen foundation
over the now-proven capability substrate. Current baseline: codegen room/runtime
is still placeholder-level, but the public room surface is now intentionally
slim and the projection/ACL family beneath it is already fairly explicit.
Strategy baseline: `CodegenCommandSystem` should stay a thin public facade with
selected helpers plus `validate_codegen(...)` / `execute_codegen(...)`, while
the real AST validation, namespace, compile/exec, result, and monitoring engine
lives under `src/melder/aether/nexus/rift/codegen_system/`. ACLs should gate
execution authority and namespace exposure; AST validation/compile happens
before `exec`; codegen history/logs and overwatch/sentinel hooks provide
accountability without object-level provenance fields or public
artifact/session APIs.
