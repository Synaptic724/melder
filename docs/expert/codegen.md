---
myst:
  html_meta:
    description: >-
      Build a Python application from generated source with Melder: validate,
      materialize, import, bind, and resolve objects with controlled lifetimes.
---

# Validate → materialize → import → bind → meld

Prerequisites: [an eligible agent room](agent-rooms.md),
[configuration](../advanced/posture.md), and [lifetimes](../beginner/lifetimes.md).
The complete application lesson starts with source strings and ends with working
Python objects: a tokenizer, counter, reporter, and a population of independent workers.

## Each verb answers a different question

| Step | Result to inspect |
| --- | --- |
| `validate_codegen` | `accepted`, the selected frame, and any validation issues |
| `execute_codegen` | The execution payload: `result`, `output` and error information (below) |
| `materialize_codegen` | `materialized` and the named module's publication result; `refusal` when the name is already loaded, under `melder`, a standard-library or installed name, or outside the frame's `materialize_modules` roots |
| Import | The generated module's real classes |
| Bind and meld | Objects managed through the normal registration and lifetime rules |

Validation checks the room's policy before execution; it does not prove arbitrary
Python safe. Malformed requests and policy refusals have different result/error
contracts. Inspect the returned payload before treating a call as completed work.

## What `execute_codegen` returns

The payload always carries `accepted` and `frame_name`. To return a value, assign it
to a variable named `result`; the payload carries it under `result` unless it is
`None`. What the code prints comes back under `output`, also when the code raises:

```python
payload = command.execute_codegen("print('rows:', 3)\nresult = {'answer': 42}\n", frame_name="ops")
# {'accepted': True, 'frame_name': 'ops', 'result': {'answer': 42}, 'output': 'rows: 3\n'}
```

A refusal adds `reason` and `validation_issues` (the code did not run); a run that
raised adds `reason` and `runtime_error` (`"ValueError: ..."`). Printed text is
captured per room: `RiftConfiguration.with_codegen_output_capture(False)` sends room
code's `print` to the host process's stdout instead, and
`with_codegen_output_limit(characters)` sets how much one execution keeps (65,536
characters by default, then a single "[output truncated: N more characters not kept]"
line). `print(..., file=x)` always writes to `x`.

## What a codegen profile limits

A frame's codegen profile (`safe`, `hybrid`, `permissive`, `full_access`, the
`precision` overlay) governs the Python room code may run: imports, the builtins it
may call, reflection, dunder access and nested codegen. Every profile exposes the
same room objects to room code - `viewer`, `workstation`, `target`, `command` and
`codegen` - and an object one of them returns, such as the live conduit from
`command.get_conduit_by_name`, accepts any of its methods. The profiles' frame,
conduit and spell rules (for `safe`: no linking, no lesser conduits, no transfers, no
spell creation, method calls or attribute writes) are published to agents as the
frame's `allowed_commands`; they are not yet enforced on room code (GitHub #338).

## The complete application

Run Expert 36. It validates and materializes the generated modules, imports and
binds the classes, then computes a word-frequency report. The assertions check
that `record` occurs four times, that each object has the expected state, that
`unique` reuses the tokenizer, and that five `many` workers have independent totals
`[1, 2, 3, 4, 5]`.

The core function below uses the source strings defined earlier in the saved file.
Open the complete linked lesson to copy or download that setup.

## Executing and keeping are separate

Materialization gives code a module address. A subsequent bind records its version
and custody. The iteration lesson compares room memory with research history:
running code does not itself declare a new research version. Subscribe to the
room's memory system before operations when you want to observe those command records.
