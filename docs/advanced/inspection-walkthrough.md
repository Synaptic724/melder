# Inspect an explicitly selected world

Prerequisites: [world boundaries](worlds.md), [Nexus setup](nexus.md), and
[viewer navigation](viewers.md).

Follow the complete linked examples in this order:

1. Build two isolated cache worlds with distinct binding identities. Compare the
   instances and verify each world's reuse.
2. Open a static Rift and inspect its initial state. No assigned frames is a valid
   starting state, not an instruction to substitute the default frame.
3. Use the target-attachment example to opt a frame into observation and attach
   the Rift explicitly. That example lives in the Expert collection; its source
   placement stays unchanged.
4. Enumerate the visible frames, choose one, and descend from conduit to spell.
   Ask for missing-section information before treating an omitted field as absent.

Keep the frame's eligibility, the Rift's assignment, and the selected view separate
while diagnosing visibility. Each answers a different question about the same read.
