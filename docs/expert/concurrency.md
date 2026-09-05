# Several rooms, explicit shared worlds

Prerequisites: [room setup](agent-rooms.md) and a free-threaded Python runtime.
The concurrency example opens a private room for each worker and points the rooms
at one shared target world. Each room owns its workstation and memory subscriptions.

## Check results across the boundary

Generated code places its answer in `result`; the execution payload carries that
answer alongside acceptance and error information. Expert 21 starts with a single
sum, then launches four coordinated workers and checks the exact results:
`5050`, `9`, `"0-1-4-9-16"`, and `5040`.

It also checks that the workstations have distinct identities. This demonstrates
private working spaces with a shared runtime target. It is not a timing benchmark
and does not establish a universal absence of contention.

## Match coordination to the operation

Computing an answer and changing topology have different coordination needs.
Continue to the [admission and gate guide](transactions.md) for structural changes
and shutdown. Use [multiple-world targeting](agent-rooms.md) when workers should
operate on different runtime worlds rather than a shared one.
