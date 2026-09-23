# Named lesser Nexus integration

## Contract
Named scope discovery must describe the live named lifecycle without changing root ownership,
permissions, instance lifetimes or ordinary anonymous pool cycles. Existing records carry all needed
name/state/parent/root fields. No new record family or live-object registry is introduced.

## Boundaries and Order
- Conduit owns named publication timing inside existing named attachment/cleanup locking.
- Nexus/FrameDescriptorManager own record construction and replacement; no projection refresh occurs.
- CommandSystem owns ACL-checked identity resolution, used by capability and codegen named getters.
- Capability's create_lesser_conduit forwards an optional keyword-only name.
- Fresh IDs enter compiled projections only through the existing explicit Rift refresh. Permanent
  removal retains the existing stale-projection failure until refresh; this is not an ACL redesign.

## Invariants
- Named pool return clears published name/parent before idle publication; the same recorded ID remains.
- A private pooled publication builds detached pooled values while the runtime is still owned so
  sink failure can be retried. It must not create a record for an unpublished candidate.
- Only named branches add Nexus work. Anonymous pool return keeps one name conditional and no sink call.
- Root names/counts remain root-only; Cloud names/counts include active named lessers.
- Published-id authorization cannot be redirected to a different ID by name reuse.
- Views return value metadata; raw runtime access remains forbidden for static rooms.

## Rollback and Failure
Acquisition uses existing named cleanup on failure. Soft retirement publishes cleared record values,
unregisters Cloud, refreshes the frame overview, clears the name and detaches in that order. Until
the final steps succeed, the retained name/parent route retries cleanup and no shell is idle.
There is no all-or-nothing snapshot across Cloud and Nexus. Discovery remains a borrowed-reference
contract; cleanup/reuse may follow a successful fetch.

## Coverage
TASK-2026-09-23-implement-named-lesser-nexus covers publication, command selection and qualification.
Final canonical documentation/examples belong to the epic's qualification story. Build assets stay held.
