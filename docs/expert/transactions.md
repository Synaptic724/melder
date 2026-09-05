# Structural operations and admission

Prerequisites: [dynamic composition](../intermediate/dynamic-linking.md) and
[room boundaries](agent-rooms.md). Continue using public structural verbs such as
bind, link, sever, transfer, and staged binding. Each owns its admission and
bookkeeping; normal application code does not open an extra transaction around it.

## Read and write paths have different jobs

The internal DevOps plane coordinates structural changes through scopes and claim
modes. Resolution uses its own validity and creation gates. A failure at an
admission or posture gate should be diagnosed at the boundary named by the error.
The rewiring lesson demonstrates both a static world and a dynamic world whose
posture explicitly disables linking.

## A gate is more than a mutex

Stopping new entrants does not prove existing readers have left. The gate lesson
distinguishes reversible disable/enable from terminal shutdown. It selects the
`raise` entry policy for a single-threaded demonstration, disables admission,
checks refusal, reopens the gate, and checks that the same validation call works.

For shutdown, it performs a bounded `close_and_wait_rift(...)` and checks the
remaining active-thread count afterward. That count is a diagnostic, not a polling
loop to use as a substitute for synchronization.

The [concurrency guide](concurrency.md) demonstrates several rooms executing actual
jobs against a shared target. Use the architecture reference for the internal
coordination design behind these public operations.
