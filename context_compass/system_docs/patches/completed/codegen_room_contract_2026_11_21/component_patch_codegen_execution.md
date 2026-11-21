# component_patch_codegen_execution

## Metadata
- Patch ID: codegen_room_contract_2026_11_21
- Component: Codegen Internal Engine - namespace and execution (`CodegenNamespaceBuilder`, `CodegenBuiltinsStrategy`,
  `CodegenNamespace`, `CodegenExecutor`, `CodegenExecutionResult`), the room command surface
  (`CodegenCommandSystem.execute_codegen`) and the per-Rift configuration (`RiftConfiguration`)
- Status: implemented at 0.2.8311-0.2.8313; merged into src_components, src_architecture, tests_components and the
  source graph
- Owner: Mark (accountable); melder_0 (synaptic_python_developer)
- Created: 2026-11-21T22:40:00Z
- Updated: 2026-11-21T23:30:00Z

## Component Purpose and Boundary
- Current boundary: `execute_codegen` runs accepted code against a namespace whose `__builtins__` is the
  interpreter's builtins minus the denied names; `print` is the interpreter's, so its text reaches the host
  process's stdout. The payload carries `accepted`, `frame_name` and, when present, `reason`, `validation_issues`,
  `runtime_error` and `result` (the value room code assigned to `result`, when not None).
- Target boundary: a codegen room captures room code's `print` into the payload's `output` key, as the room's
  configuration sets: `RiftConfiguration.with_codegen_output_capture(enabled)` (default on) and
  `with_codegen_output_limit(characters)` (default 65,536), fixed when the room is created (owner, 2026-11-21).

## Before/After Behavior Summary
- Before: `print('rows:', 3)` in room code writes "rows: 3" to the host's stdout; the payload holds no trace of it.
- After (capture on): the payload holds `output: 'rows: 3\n'` and nothing reaches the host's stdout. Text beyond
  the limit is dropped; `output` then ends with one line "[output truncated: N more characters not kept]". A run
  that raises returns what it printed before the error beside `runtime_error`. With capture off, today's behaviour.
- Unchanged: `print(..., file=x)` with an explicit file writes to `x`; `validate_codegen`, `research_preview` and
  `materialize_codegen` print nothing into a payload, and a materialized module keeps the interpreter's `print`.

## Interface Deltas
- Inputs: `RiftConfiguration` gains the properties `codegen_output_capture` (bool) and `codegen_output_limit` (int,
  at least 1; a bool is refused), their `with_*` setters, read properties and defaults. `CodegenExecutionResult`
  takes `output` (str, default empty); `CodegenNamespace` takes the request's `CodegenOutputCapture`.
- Outputs: the execution payload gains `output` (str), present when the code printed anything to stdout.
- Error semantics: an invalid limit raises at configuration time (TypeError for a non-int or bool, ValueError
  below 1); `print` with a non-string `sep` or `end` raises TypeError as the builtin does.

## State and Lifecycle Deltas
- Owned state changes: a `CodegenOutputCapture` per request (kernel class), owned by the request's
  `CodegenNamespace` and cleaned with it.
- Lifecycle/cleanup changes: `CodegenNamespace.cleanup` cleans its capture.

## Failure Mode Deltas
- Removed failure mode: an agent cannot see what its code printed.
- New failure mode: a caller that read room code's prints from the host's stdout no longer finds them there unless
  the room turns capture off (release-note breaking change).

## Dependency and Ordering Constraints
1. The capture is created by the namespace builder from the owning Rift's configuration, installed by the builtins
   strategy only when `print` survives the denied builtins, and read by the executor after `exec` returns or raises.
2. The capture holds its own lock: room code that prints from several threads (where a profile allows threads)
   loses no text below the limit.

## Validation Expectations
- Test/validation item: a safe room returns printed text under `output` and the host's stdout stays empty.
- Test/validation item: the limit cuts the text exactly and adds the truncation line; a run that raises keeps its
  output; a room with capture off prints to stdout; no `output` key when nothing was printed.
- Test/validation item: configuration defaults, setters, refusals and freeze; the capture's `print` semantics
  (`sep`, `end`, `None`, explicit `file`), its limit boundary, concurrent prints and idempotent cleanup.
- Evidence target: tests/unit (capture, result, namespace, configuration) and the #337 integration file, GIL off.

## Unknowns and Open Decisions
- UNKNOWN: none.
- DECISION_REQUEST: none open (owner, 2026-11-21: room configuration, default on, 65,536 characters).

## Context / Handoff Summary
- What changed: specified.
- Remaining risks: tests or tools elsewhere that expect room `print` on stdout (the full suite decides).
- Next entrypoint: code_description_patch_codegen_output_capture.md.
