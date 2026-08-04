# Epic: Integrate First-Class Iris Logging Into Melder Runtime

## Metadata
- Epic ID: EPIC-2026-03-29-iris-first-class-logging-integration
- Status: in_progress
- Owner: codex
- Priority: p1
- Created: 2026-03-29T22:35:16Z
- Updated: 2026-03-29T23:26:03Z
- Target Window: 2026-Q2
- Related Program/Initiative: Rift runtime observability and codegen audit trail

## Problem / Opportunity
Melder already has a logger adapter pattern through `InitHelpers.resolve_safe_logger(...)`
and `SafeLogger`, but it currently uses that pattern mostly as a thin facade over
stdlib logging or channel-style logging. The richer Iris model in CommandOps already
defines a first-class structured logging pattern with:
- thread context fields
- group and system-group tagging
- arbitrary flat `properties`
- memory-backed channels and viewer/query surfaces

That creates a clear opportunity: Melder should not invent a separate structured
event/codegen logging stack for Rift/workspace/runtime changes. It should integrate
with the existing Iris pattern directly while still allowing general logger usage
when Iris is not present.

## MRP Alignment (Most Reasonable Product)
The smallest coherent long-term foundation is:
- keep the current `SafeLogger` adapter pattern
- define one Melder-side structured runtime event schema
- define one codegen event schema
- map those schemas onto Iris `groups`, `system_groups`, and `properties`
- preserve a simple message-first fallback path for plain stdlib or non-Iris
  environments

This is the right foundation because it gives Melder:
- immediate structured observability
- first-class compatibility with Iris
- no forced hard dependency on Iris-only runtime surfaces
- a lightweight fallback for plain loggers
- a path for later richer query/view tooling without rewriting the logging model

## Ticket Contract
- ENTRY_GATE: the current Melder logger adapter pattern and the external Iris field
  pattern are both read and evidenced.
- EXECUTION_BOUNDARY: epic-level planning only for runtime/codegen/event logging
  architecture, integration model, and rollout sequencing.
- DEPENDENCIES:
  - `src/melder/utilities/helpers/init_helpers.py`
  - `src/melder/utilities/logger/safe_logger.py`
  - `src/melder/aether/aether.py`
  - `src/melder/aether/conduit/conduit.py`
  - `<local-workspace>\src\command_ops\command_center\spectrum\iris\channel_logger.py`
  - `<local-workspace>\src\command_ops\command_center\spectrum\iris\iris.py`
  - `<local-workspace>\src\command_ops\command_center\spectrum\iris\iris_channel.py`
- EXIT_GATE: the integration model is decomposed into stories/tasks that cover
  schema, adapter work, runtime event sources, codegen logging, and adoption.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if first-class Iris support would
  require Melder to depend directly on CommandOps runtime objects in a way that
  breaks the current general-logger fallback model.

## Goals (Outcomes)
- Define how Melder logs structured runtime and codegen events using the existing
  `SafeLogger` pattern.
- Describe the Iris field model in durable project context:
  - `groups`
  - `system_groups`
  - `properties`
  - thread/agent context
- Preserve a simple general logger path for non-Iris usage.
- Create a plan for first-class Iris integration without forcing a premature hard
  runtime dependency.

## Non-Goals (Explicit Exclusions)
- Full implementation in this epic ticket itself.
- Retrofitting every existing Melder component with structured logging in one pass.
- Full eventstream/workspace deque implementation.
- Metrics/analytics/rate-limiting design.

## Scope Boundaries
- In scope:
  - logging architecture
  - Iris field mapping
  - runtime event schema planning
  - codegen event schema planning
  - adapter/fallback strategy
- Out of scope:
  - workstation/workspace implementation
  - MutationResearch transaction event modeling beyond logging hooks
  - external dashboard/viewer implementation work

## State Transition Event
- from_state: ready
- to_state: in_progress
- transition_reason: the user approved the `AetherUtilitySystem` direction and
  requested implementation of the first core-runtime migration slice now.

## Success Metrics
- One accepted epic exists that defines the Melder <-> Iris integration direction.
- The field-level Iris pattern is described in durable ticket context.
- Follow-up stories/tasks exist for schema, adapter, and event-source rollout.

## Requirements (Functional + Non-Functional)
- Melder must support first-class structured runtime logging for:
  - Rift events
  - frame lifecycle events
  - codegen requests/results
  - later workspace degradation/rebuild events
- Logging must support the Iris-native field shape:
  - `groups`
  - `system_groups`
  - `properties`
- Melder must still work with a general logger path when Iris is unavailable,
  but that fallback only needs to carry the message or a compact flattened
  summary rather than full Iris metadata fidelity.
- The adapter boundary must stay explicit and reviewable.
- No duplicate logging abstraction should be introduced.

## Constraints / Assumptions
- `SafeLogger` is already the adapter boundary in Melder.
- Iris supports richer per-record metadata than current Melder call sites use.
- First-class Iris support should not force Melder to become CommandOps-bound
  at import time.
- Event and codegen logs should be structurally queryable later, even if the
  first delivery surface is just logging.

## Dependencies / External References
- [init_helpers.py](<local-workspace>/src/melder/utilities/helpers/init_helpers.py)
- [safe_logger.py](<local-workspace>/src/melder/utilities/logger/safe_logger.py)
- [aether.py](<local-workspace>/src/melder/aether/aether.py)
- [conduit.py](<local-workspace>/src/melder/aether/conduit/conduit.py)
- [channel_logger.py](<local-workspace>/src/command_ops/command_center/spectrum/iris/channel_logger.py)
- [iris.py](<local-workspace>/src/command_ops/command_center/spectrum/iris/iris.py)
- [iris_channel.py](<local-workspace>/src/command_ops/command_center/spectrum/iris/iris_channel.py)
- [iris_policy.py](<local-workspace>/src/command_ops/command_center/spectrum/iris/iris_policy.py)

## Milestones (Track Progress)
- [ ] Milestone 1: Logging architecture locked
      Clear Melder-to-Iris integration model exists with adapter and fallback rules.
- [ ] Milestone 2: Event schemas locked
      Runtime event and codegen event schemas are defined with field mapping.
- [ ] Milestone 3: Rollout plan decomposed
      Concrete stories/tasks exist for implementation slices.

## Stories (Required to Complete)
- [ ] Story: STORY-2026-03-29-aether-utility-system-logging-provider - migrate
      Melder core runtime logging to an Aether-hosted utility/provider model
- [ ] Story: define Melder structured runtime event schema and Iris field mapping
- [ ] Story: define codegen logging schema and AST-enrichment boundary

## Tasks (Cross-Cutting or Epic-Level)
- [ ] Task: TASK-2026-03-29-migrate-core-logging-to-aether-utility-system -
      remove config-owned logger factories and migrate the core runtime path
- [ ] Task: define the base Melder event record contract (`event_type`, `epoch`, `step`, etc.)
- [ ] Task: define the codegen log contract and AST-summary enrichment boundary
- [ ] Task: verify Ticket Microcycle enforcement across active tickets/stories/tasks.

## Acceptance Criteria (Epic Done)
- The Iris field pattern is explicitly documented in project planning.
- The Melder integration model preserves both:
  - first-class Iris support
  - general logger fallback
- Follow-up stories/tasks exist for implementation slices.

## Risks / Mitigations
- Risk: Melder invents a second structured logging abstraction instead of reusing
  the existing adapter path.
  Mitigation: keep `SafeLogger` as the integration boundary and map structured
  event payloads onto Iris metadata fields.
- Risk: first-class Iris support becomes a hard coupling that breaks plain logger
  usage.
  Mitigation: keep the plain logger path as a message-first fallback instead of
  forcing full Iris semantics onto it.
- Risk: AST is overused as semantic truth.
  Mitigation: keep AST limited to superficial change-summary enrichment for codegen logs.

## Applicable Anti-Patterns
- [ ] No epic-state transition without story-level evidence.
- [ ] No closure while required stories are incomplete or unaccepted.
- [ ] No program claims without source evidence from story/task notes.

## Validation / Test Approach
- Planning validation only:
  - verify the current Melder adapter pattern is cited accurately
  - verify the current Iris field model is cited accurately
  - verify the epic preserves the general-logger fallback requirement

## Rollout / Adoption Plan
- First, lock the event and codegen schemas.
- Second, define the adapter behavior at the `SafeLogger` boundary.
- Third, add event/codegen emission to the highest-value runtime surfaces first:
  - `Nexus`
  - `Rift`
  - later `Workspace` / `Workstation`
- Fourth, add richer viewer/query surfaces later if needed.

## Open Questions
- Whether Melder should expose an explicit Iris-aware logger interface or continue
  to rely entirely on the `SafeLogger` adapter boundary.
- Whether codegen event persistence should live only in logger channels or also
  be mirrored into a later workspace event queue.
- Exactly how much structured payload should be flattened into the fallback
  message for plain logger usage.

## Decision Log
- 2026-03-29: first-class Iris support should be planned as an observability epic
  instead of ad hoc per-component logging changes.
- 2026-03-29: the general logger path remains a required fallback even if Iris
  becomes the richer preferred structured logger, but that fallback only needs
  message-level support rather than full first-class structured metadata.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: false
- ARTIFACT_PATHS:
  - none
- DISPOSITION: delete_on_close
- CLEANUP_TRIGGER: n/a

## Notes
- DATETIME: 2026-03-29T23:12:48Z
  TYPE: FACT
  CLAIM: Melder already has both factory implementations we need:
    `StdLoggerFactory` and `IrisLoggerFactory`. The real architectural gap is
    not missing factories, but missing the CommandOps-style system-wide
    acquisition path. Right now the Melder factories mostly live behind
    `Configuration.logger_factory` or ad hoc `resolve_safe_logger(...)` usage.
    CommandOps, by contrast, exposes a stable utility path that can request a
    channel logger or safe logger from a shared system-wide provider. That
    means the Melder refactor should focus on a hosted provider/dispenser plus
    a `resolve_channel_logger(...)`-style entrypoint, not on inventing yet
    another factory type.
  EVIDENCE:
  - src/melder/spellbook/configuration/configuration.py:164-224
  - src/melder/utilities/logger/std_logger_factory.py:10-287
  - src/melder/utilities/logger/iris_logger_factory.py:1-148
  - src/melder/utilities/helpers/init_helpers.py:1-29
  - <local-workspace>\src\command_ops\utilities\general_helpers\init_helpers.py:23-84
  IMPACT: The next planning slice should define a Melder-side provider singleton
    and utility entrypoint rather than treating `Configuration.logger_factory`
    as the long-term global logging story.
  NEXT: add the Aether-hosted/provider-dispenser ownership model and utility
    acquisition precedence to the epic/stories as the intended direction.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-03-29T22:35:16Z
  TYPE: FACT
  CLAIM: The Melder-side logger adapter pattern already exists and should be
    reused rather than replaced. `Aether` and `Conduit` both resolve a
    `SafeLogger` through `InitHelpers.resolve_safe_logger(...)`, which means the
    right path for richer Rift/workspace logging is to define better structured
    event payloads, not to create a second logging abstraction.
  EVIDENCE:
  - src/melder/utilities/helpers/init_helpers.py:1-29
  - src/melder/utilities/logger/safe_logger.py:82-205
  - src/melder/aether/aether.py:43-82
  - src/melder/aether/conduit/conduit.py:511-525
  IMPACT: The epic should build on the existing adapter seam instead of
    widening the runtime with a new logger stack.
  NEXT: preserve `SafeLogger` as the integration boundary in all follow-up stories.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-03-29T22:35:16Z
  TYPE: FACT
  CLAIM: The Iris field model is already rich enough to carry the structured
    runtime and codegen metadata Melder will need later. `ChannelLogger`
    snapshots `groups`, `system_groups`, and `properties` onto each record, and
    Iris viewer/query surfaces already support querying by exactly those fields.
    That means Melder can map event/codegen schemas onto existing Iris concepts
    instead of inventing a custom structured-record transport first.
  EVIDENCE:
  - <local-workspace>\src\command_ops\command_center\spectrum\iris\channel_logger.py:55-68
  - <local-workspace>\src\command_ops\command_center\spectrum\iris\channel_logger.py:102-160
  - <local-workspace>\src\command_ops\command_center\spectrum\iris\iris.py:306-357
  - <local-workspace>\src\command_ops\command_center\spectrum\iris\iris.py:1976-2018
  - <local-workspace>\src\command_ops\command_center\spectrum\iris\iris_channel.py:761-773
  IMPACT: The first implementation stories can focus on event schema and source
    emission instead of reinventing metadata transport or query semantics.
  NEXT: define the Melder-side event/codegen schema in follow-up planning.
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
This epic captures the plan for bringing first-class Iris-style structured
logging into Melder without losing the general-logger fallback path. Iris gets
the rich structured metadata model; plain general loggers only need the message
or a compact flattened summary. Melder already has stdlib and Iris factories;
the missing piece is a system-wide provider/dispenser plus a
`resolve_channel_logger(...)`-style utility path. The next step is to
decompose this into stories/tasks for event schema, codegen schema, provider
ownership, and adapter rollout.
