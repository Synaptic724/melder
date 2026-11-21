# Melder 0.2.8313

**Unreleased**

## Codegen validation accepts every way Python binds a name

Room code that binds a name through an exception handler, a match pattern or a type parameter was refused by codegen
validation, although it is valid Python: `except ValueError as e:` followed by `str(e)` was refused with "Name 'e' is
not available in the codegen namespace.", and so were `case n:`, `case [first, *rest]:`, `case {'a': v, **rest}:`,
`case int() as n:` and `def first[T](items: list[T]) -> T:` (GitHub issue #337). Name resolution counted only
assignment-style bindings, definitions, parameters and imports. It now counts every binding form - `except ... as` and
`except* ... as`, the match captures and PEP 695 type parameters included - so such code validates and runs. A name
that nothing in the code binds is still refused with the same message.

## `execute_codegen` returns what room code printed

What room code printed went to the stdout of the process running Melder, where the agent that sent the code never saw
it. A codegen room now captures it: `execute_codegen`'s payload carries it under a new `output` key, also when the code
raised (beside `runtime_error`), and nothing reaches the host's stdout.

```python
payload = command.execute_codegen("print('rows:', 3)\nresult = {'answer': 42}\n", frame_name="ops")
# {'accepted': True, 'frame_name': 'ops', 'result': {'answer': 42}, 'output': 'rows: 3\n'}
```

Two new room settings control it, fixed when the room is created:
`RiftConfiguration.with_codegen_output_capture(enabled)` (on by default) and `with_codegen_output_limit(characters)`
(65,536 by default). Text past the limit is dropped and `output` ends with one line, "[output truncated: N more
characters not kept]". A limit below 1 is refused with ValueError, a bool or a non-int with TypeError.
`print(..., file=x)` still writes to `x`, and a materialized module's `print` is unchanged. `execute_codegen`'s
docstring - the room's own help - now says that assigning `result` returns a value and names every payload key (GitHub
issue #337).

**Breaking change:** in a codegen room, room code's `print` no longer reaches the host process's stdout by default.
To keep the old behaviour, create the room from a configuration with `.with_codegen_output_capture(False)`.

## Packaging and documentation

The codegen profile docstrings and `docs/expert/codegen.md` now state what a profile enforces on room code: its
capability rules - imports, the denied builtins, reflection, dunder access and nested codegen. Its frame, conduit and
spell rules, among them `safe`'s denial of linking, lesser conduits, transfers, spell creation, method calls and
attribute writes, are published to agents as the frame's `allowed_commands` but are not yet enforced on room code,
which can call any method of a live object it holds, such as the conduit `command.get_conduit_by_name` returns (GitHub
issue #338). The same page now lists what `execute_codegen` returns and the room settings above.

The new kernel class `CodegenOutputCapture` (`melder.nexus.rift.codegen_system.namespace.codegen_output_capture`) is
room code's `print` in a capturing room. The internal-bind guard manifest holds 636 entries (635 at 0.2.8310):
`CodegenOutputCapture` cannot be bound. The docstrings of `RiftConfiguration`, `CodegenNameResolutionStrategy`,
`CodegenNamespaceBuilder`, `CodegenBuiltinsStrategy`, `CodegenNamespace`, `CodegenExecutor`, `CodegenExecutionResult`
and `CodegenCommandSystem.execute_codegen` describe the change; the source and test maps, their indexes and the source
graph describe it.

Agent documentation metadata and the whole-repository LLM bundles are rebuilt for 0.2.8313.
