# code_description_patch_failure_location

## Metadata
- Patch ID: nexus_cli_and_repl_2026_11_22
- Component: `CodegenExecutor.execute` and its collaborators (`CodegenCompiler`, `CodegenSystem`,
  `CodegenExecutionResult`)
- Status: implemented at 0.2.8314-0.2.8315; merged into src_components, src_architecture, tests_components and the
  source graph
- Owner: Mark (accountable); melder_0 (synaptic_python_developer)
- Created: 2026-11-22T14:40:00Z
- Updated: 2026-11-22T16:19:07Z

## Control Flow Commitments
- `CodegenSystem.execute_codegen_request`: after validation accepts, record `code` under the run's transaction id in
  `_run_sources`, then build the namespace, compile and execute as today, passing `_run_sources` to the executor.
- `CodegenExecutor.execute`, when `exec` raises: walk `exc.__traceback__` to its end and keep the last entry whose
  frame's `f_code.co_filename` is a run file name (`CodegenCompiler.run_id_from_filename` returns its id). Its
  `tb_lineno` is the line; its run id is the run; the line's text is that run's kept source's line, stripped, when
  the source is kept and the line exists. Then `CodegenExecutionResult.runtime_failed(...)` with those values.
- `CodegenExecutionResult.to_payload` adds `run_id` always, and the three location keys when set.

## Edge and Error Semantics
- The innermost room-code frame wins: a failure inside melder code that room code called is located at the room
  line that made the call; a failure inside a method an earlier run defined is located in that run's code.
- No room-code frame in the traceback adds no location keys; a run id whose source is not kept (another room's
  run) adds the line and run id without text.
- `runtime_error`'s text is built exactly as today.

## Invariants and Idempotency
- The walk reads the traceback only; it neither clears nor re-raises anything, and a failure while locating would be
  a defect, not a fallback path (no broad `except`).
- `_run_sources` entries are written once per accepted run and never changed.

## Explicit Non-Goals
- No location for validation refusals (they carry their own issues), for materialized modules' frames, or for
  failures outside `exec`.
