# component_patch_codegen_execution

## Metadata
- Patch ID: nexus_cli_and_repl_2026_11_22
- Component: Codegen Internal Engine - `CodegenSystem`, `CodegenCompiler`, `CodegenExecutor`,
  `CodegenExecutionResult` - and the room command surface's `execute_codegen` and `research_heads` docstrings
- Status: implemented at 0.2.8314-0.2.8315; merged into src_components, src_architecture, tests_components and the
  source graph
- Owner: Mark (accountable); melder_0 (synaptic_python_developer)
- Created: 2026-11-22T14:40:00Z
- Updated: 2026-11-22T16:19:07Z

## Component Purpose and Boundary
- Current boundary: each run compiles under `<melder-codegen:{transaction_id}>`; a runtime failure answers
  `runtime_error: "<Type>: <message>"` and nothing else; the payload never names its run, and no run's source
  outlives the run.
- Target boundary: every execute payload names its run (`run_id`); a runtime failure also names the innermost
  room-code line, its run and that line's text; the room's `CodegenSystem` keeps each accepted run's source until
  the room is removed (owner, 2026-11-22).

## Before/After Behavior Summary
- Before: `assert 1 == 2` answers `runtime_error: "AssertionError: "`.
- After: the same run answers `run_id: <id>`, `runtime_error_line: 1`, `runtime_error_run_id: <id>`,
  `runtime_error_line_text: "assert 1 == 2"`. A run that calls a method an earlier run left on the workstation, and
  fails inside it, names the earlier run's id and the line of its code.
- Unchanged: `runtime_error`'s text, `output`, `result`, the validation-refused payload except `run_id`, and what
  the room memory records.

## Interface Deltas
- Inputs: `CodegenExecutor.execute(compiled_code, transaction_context, run_sources)` takes the room's kept sources;
  `CodegenCompiler` gains `run_filename(transaction_id)` and `run_id_from_filename(filename)` so one class owns the
  file-name form; `CodegenExecutionResult.runtime_failed` takes the three location values.
- Outputs: `run_id` (str) on every execute payload; on a runtime failure in room code, `runtime_error_line` (int),
  `runtime_error_run_id` (str) and, when the room kept that run's source, `runtime_error_line_text` (str, the line
  stripped).
- Error semantics: a failure with no room-code frame in its traceback (none expected) adds no location keys.

## State and Lifecycle Deltas
- Owned state changes: `CodegenSystem._run_sources` (run id -> source), filled for every run that passed validation,
  under the engine lock.
- Lifecycle/cleanup changes: `CodegenSystem.cleanup` clears and deletes it. Memory grows with the room's runs until
  the room is removed (owner-accepted).

## Failure Mode Deltas
- Removed failure mode: an agent cannot tell which line failed, or that it failed inside code an earlier run left.
- New failure mode: none; a run from another room (code shared across rooms) is located by line and run id only.

## Dependency and Ordering Constraints
1. The source is kept after validation accepts and before compile, so the run's own functions are quotable when a
   later run calls them.
2. The executor reads the kept sources under the engine lock it already runs under.

## Validation Expectations
- A failing bare `assert` names its line, run and text; a failure inside a method defined by an earlier run names
  that run; a failure inside melder code called from room code names the room line that made the call.
- Every execute payload, accepted or refused, carries `run_id`; a success has no location keys.
- The kept sources are gone after the room is removed.
- Docstrings: `execute_codegen` names the new keys, the `frame_name` default and keeping state between runs on the
  workstation; `research_heads` says its tip is the newest recorded version, with `research_residency` for the
  active one.
