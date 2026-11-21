# code_description_patch_codegen_output_capture

## Metadata
- Patch ID: codegen_room_contract_2026_11_21
- Component: `CodegenOutputCapture` and its wiring through the namespace builder, builtins strategy and executor
- Status: implemented at 0.2.8311-0.2.8313; merged into src_components, src_architecture, tests_components and the
  source graph
- Owner: Mark (accountable); melder_0 (synaptic_python_developer)
- Created: 2026-11-21T22:40:00Z
- Updated: 2026-11-21T23:30:00Z
- Trigger: concurrency-sensitive state (a per-request buffer room code may write from several threads)

## Control Flow Commitments
- `CodegenNamespaceBuilder.build` reads the owning Rift's configuration: with `codegen_output_capture` on it builds
  one `CodegenOutputCapture(limit=codegen_output_limit)`, passes it to the builtins strategy and to the
  `CodegenNamespace` it returns; with it off it passes none. `build_builtins` (the materialize path) never captures.
- `CodegenBuiltinsStrategy.build_namespace_entries(configuration, output_capture)` replaces `print` in the request's
  builtins mapping with the capture's bound `capture_print` after the denied names are removed, and only when
  `print` is still there.
- `CodegenOutputCapture.capture_print(*values, sep=' ', end='\n', file=None, flush=False)`: a `file` that is not
  None goes to the interpreter's `print` with every argument; otherwise the text `sep.join(str(v)) + end` (None
  meaning the defaults) is appended under the capture's lock, up to the limit; characters past it are counted.
- `CodegenExecutor.execute` reads `namespace.get_output()` after `exec` returns or raises and passes it to
  `CodegenExecutionResult.executed` or `runtime_failed`; `to_payload` adds `output` when it is not empty.

## Edge and Error Semantics
- A text that reaches the limit part-way keeps its first characters; `output` adds "\n" when the kept text does not
  end with one, then "[output truncated: N more characters not kept]\n".
- `sep` or `end` that is neither None nor a str raises TypeError ("sep must be None or a string, not int"), as the
  builtin does; `flush` is accepted and has nothing to flush.
- `get_output()` on a namespace built without a capture returns "".

## Invariants and Idempotency
- The capture never holds more than `limit` characters of room text; `cleanup` is idempotent and drops the buffer.
- One capture per request; nothing about it outlives the request's namespace.

## Explicit Non-Goals
- No capture of stderr, logging, `sys.stdout.write` or a materialized module's prints; no change to room memory.
