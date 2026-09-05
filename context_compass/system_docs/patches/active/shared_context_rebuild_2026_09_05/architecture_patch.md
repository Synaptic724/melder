# Architecture patch: Shared context rebuild admission
<!-- BEGIN ENTRY: Shared context rebuild admission -->

## Scope and non-goals
Patch ID: shared_context_rebuild_2026_09_05. Repair the proven phase-5/phase-11 publication window
and active-context lifetime together. CounterSwitch, existence semantics, workflows and public
meld signatures remain unchanged. No global reader lock, generic primitive rewrite or hidden snapshot.

## Changed components
| Component | Boundary delta |
| --- | --- |
| Spell context lifecycle | Retain the stable index gate and explicit failed-build cause. |
| Meld resolution runtime | Move the existing dynamic ticket before context retrieval and hold through execution. |
| Compiler orchestration | Own a complete affected-scope freeze/drain/build/publication window. |

## Interface and boundary deltas
A private CreationContextRebuild context manager owns rare writer coordination. It borrows each
affected index gate, acquires existing gate transition locks in stable index order, freezes all
entrances, drains existing tickets and holds authority until final publication/abort. It adds no
mutex acquisition to normal readers and preserves pre-existing frozen/terminal posture on release.
Factory cold election remains CounterSwitch-based. Failed leadership records the cause and wakes
followers rather than leaving state 1. Forced and cached publication participate in the writer window.

## Cross-component invariants
- Readers hold exactly one index ticket from before the context read through executor return.
- Revalidation occurs before that index ticket; an admission-race recheck releases before rebuilding.
- No phase input/context is retired until the affected index readers/builders have drained.
- The gate, not a fabricated CounterSwitch state, represents phase-rebuild ownership. The idle latch
  behind a frozen gate is inaccessible to admitted readers; normal election starts after valid inputs.
- Overlapping writer scopes share ordered gate locks. Unrelated admitted execution remains independent.
- Phase 5 invalidates its actual dependency closure. Rebuilt contexts are published before reopening;
  dependencies lacking new plan inputs are explicitly marked for deferred planning, never left falsely ready.
- Cache-ready contexts may lack codegen artifacts. Warm reads must not require those artifacts.
- Failure is explicit, wakes waiters, and releases acquired coordination resources without suppressing cause.

## Migration and rollout
1. Install the controlled real-meld regression and demonstrate the original failure.
2. Add the rare writer scope and Spell gate/failure fields; wire producer and reader changes together.
3. Cover error, dependency, direct cache, deferred and reader-lifetime contracts before qualification.
4. Refresh canonical docs/descriptors and generated assets only after behavior passes.

## Rollback
Treat admission movement and producer fencing as one reverse-patch unit. Do not revert only one
half or restore the obsolete Spell cold-path mutex. Owner controls commit, push and rollout.

## Validation and ticket coverage
- S1-S3: TASK-2026-09-05-shared-context-protocol-repair under STORY-2026-09-05-shared-context-safety.
- S4: TASK-2026-09-05-shared-context-qualification under the same story and parent epic.
- Controlled original gap; acquired-reader retirement; failures/follower wakeup; overlapping dependencies;
  direct and cached publication; automatic/deferred/existing-instance cases; independent cluster progress.
- Local/full/platform and performance claims require measured results; hosted work remains explicit.

## Open verification gates
Nested public callbacks, lock-order interaction with structural revalidation/teardown and cached
hydration must be exercised before claiming the complete epic. A new semantic restriction or
unavoidable hot-path penalty is escalated rather than silently introduced.
<!-- END ENTRY: Shared context rebuild admission -->
