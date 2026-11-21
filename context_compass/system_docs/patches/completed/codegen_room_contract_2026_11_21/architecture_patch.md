# architecture_patch

## Metadata
- Patch ID: codegen_room_contract_2026_11_21
- Status: implemented at 0.2.8311-0.2.8313; merged into src_components, src_architecture, tests_components and the
  source graph
- Owner: Mark (accountable); melder_0 (synaptic_python_developer) authors and implements
- Ticket: https://github.com/Synaptic724/melder/issues/337
- Created: 2026-11-21T22:16:54Z
- Updated: 2026-11-21T23:30:00Z

## Patch Scope and Non-Goals
- Objective: room code that binds a name the way Python allows is not refused by codegen validation (task 1), and
  an agent can see what its code returned and printed (task 2); the codegen profiles' scope is documented (task 3).
  Decided by the owner on 2026-11-21 (#337 Decision Log).
- Non-goals: no change to what a codegen profile allows or what room objects room code can reach (task 3 stays as
  designed); no logging work (#313, #314); no caching option for Nexus-managed frames (task 5 is traced first); no
  change to materialized modules, `validate_codegen` or `research_preview`.

## Changed-Components Matrix
| component | change_type | rationale | depends_on |
|---|---|---|---|
| Codegen validation (`CodegenNameResolutionStrategy`) | modify | collect every name-binding form, not only `ast.Name` stores | none |
| Codegen namespace and execution (`CodegenNamespaceBuilder`, `CodegenBuiltinsStrategy`, `CodegenNamespace`, `CodegenExecutor`, `CodegenExecutionResult`, new `CodegenOutputCapture`) | modify | a room-owned `print` captures output into the payload's `output` key | the room configuration |
| Per-Rift configuration (`RiftConfiguration`) | modify | the capture switch and limit, set per room | none |
| Room command surface (`CodegenCommandSystem.execute_codegen`) | docstring | name the `result` convention and every payload key | the payload change |
| Codegen profiles (`SafeCodegenProfileStrategy`, `HybridCodegenProfileStrategy`, `docs/expert/codegen.md`) | docstring | state what a profile enforces on room code: its capability rules only; the operation rules are published, not enforced (GitHub #338) | none |

## Interface and Boundary Deltas
- Task 1: `CodegenNameResolutionStrategy` accepts a load of a name the code binds through `except ... as`,
  `except* ... as`, a match capture (`MatchAs`, `MatchStar`, `MatchMapping.rest`) or a PEP 695 type parameter
  (`TypeVar`, `ParamSpec`, `TypeVarTuple`). No signature changes.
- Task 2: `execute_codegen`'s payload gains `output` (str), present when the code printed anything: the text that
  `print` would have written to stdout, at most the room's limit, then one truncation line. Present on a runtime
  failure too. `RiftConfiguration` gains `with_codegen_output_capture(enabled)` (default on) and
  `with_codegen_output_limit(characters)` (default 65,536), fixed when the room is created (owner, 2026-11-21).
- Task 3: documentation only: the codegen profiles state what they enforce. Enforcing their operation denials on
  room code that holds a live object is its own story (owner, 2026-11-21).

## Cross-Component Invariants
- Validation still precedes the namespace; a name that nothing in the code binds is still refused.
- Binding a name never adds a value to the namespace: the runtime builtins and room objects are unchanged, so a
  denied builtin stays absent whatever the code binds.
- The capture is per request: built with the namespace, read by the executor, cleaned with the namespace; nothing
  outlives the request. Materialized modules keep the interpreter's `print`.
- `print(..., file=x)` with an explicit file writes to `x` as before; only `print` to stdout is captured.

## Migration and Rollout Order
1. Failing-first pins: each binding form refused today; `print` output absent from the payload today.
2. Task 1: the name collectors and their docstrings.
3. Task 2: the capture, the builtins swap on the execute path, the result field and payload key, the docstrings.
4. Task 3: the profile docstrings and `docs/expert/codegen.md`.
5. System docs, graph descriptors, release note, notches; the rebuild last.

## Rollback Strategy
- Rollback trigger: a binding form admitted that should not be, or a caller depending on room `print` reaching stdout.
- Rollback steps: revert the collector change; restore the interpreter `print` in the execute-path builtins.
- Post-rollback verification: the failing-first pins return to their 0.2.8310 expectations.

## Validation Expectations and Evidence Plan
- Unit: each binding form accepted by the strategy; never-bound names still refused.
- Integration, in a safe-profile room: the #337 task 1 snippets validate and execute; `print` output arrives under
  `output`, is cut at the limit with a truncation line, comes back with a runtime error, and leaves stdout empty.
- Suites: the codegen unit, component and integration suites, then the full suite, the GIL off.

## Ticket Coverage Map
- Epic: https://github.com/Synaptic724/melder/issues/337 (tasks 1-3)
- Story: none (the owner keeps this work as tasks in the epic)
- Tasks: tasks 1, 2 and 3 of the epic

## Unknowns and Decision Requests
- UNKNOWN: none.
- DECISION_REQUEST: none open; task 2's settings decided 2026-11-21 (room configuration, default on, 65,536
  characters).

## Context / Handoff Summary
- What changed: implemented as specified at 0.2.8311 (task 1), 0.2.8312 (task 2) and 0.2.8313 (task 3, docs); the
  deltas are merged into the canonical system docs and the graph.
- What remains: the agent loop re-runs on a wheel of this landing; enforcement of the profiles is GitHub #338.
- Next entrypoints: component_patch_codegen_validation.md, component_patch_codegen_execution.md.
