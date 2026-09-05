# Understand errors and refusals

An error message is part of the public interaction. Start by identifying which
operation failed: registration, graph compilation, resolution, or cleanup.
Then compare its inputs and setup with the smallest relevant saved example.

## A useful debugging sequence

1. Keep the original exception type and message.
2. Identify the operation and the spell address involved.
3. Reduce the problem to the registrations and scope needed to reproduce it.
4. Check the source example's setup order and assertions.
5. Fix the invalid input or lifecycle assumption before adding a fallback.

The error-vocabulary lesson demonstrates a missing resolution target and the
public exception vocabulary. The double-bind lesson isolates registration
behavior. The reading-errors lesson focuses on interpreting a refusal.

These examples intentionally exercise failures. A caught refusal can be the
expected outcome of a lesson; it is different from silently ignoring an error
in application code.
