# Validate → materialize → import → bind → meld

Prerequisites: [an eligible agent room](agent-rooms.md),
[configuration](../advanced/posture.md), and [lifetimes](../beginner/lifetimes.md).
The complete application lesson starts with source strings and ends with working
Python objects: a tokenizer, counter, reporter, and a population of independent workers.

## Each verb answers a different question

| Step | Result to inspect |
| --- | --- |
| `validate_codegen` | `accepted`, the selected frame, and any validation issues |
| `execute_codegen` | The execution payload, including `result` and error information |
| `materialize_codegen` | `materialized` and the named module's publication result |
| Import | The generated module's real classes |
| Bind and meld | Objects managed through the normal registration and lifetime rules |

Validation checks the room's policy before execution; it does not prove arbitrary
Python safe. Malformed requests and policy refusals have different result/error
contracts. Inspect the returned payload before treating a call as completed work.

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
