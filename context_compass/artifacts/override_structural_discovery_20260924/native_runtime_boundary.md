# Native runtime boundary for compact construction plans

Date: 2026-09-24. Lead: updater_0. Compiler partner: updater_1.
Task: tickets/tasks/2026-09-24_discover_override_execution_semantics_task.md.
Status: native observations and experimental integration; no production patch or speed claim.

Latest variant: native_compact_direct_adapter.py/probe.py retains the first integration artifacts,
binds constructors cold and emits publication only after shared-miss calls. Its eight cases include
the seven native integration controls plus a 511-site pruned call with catalog iteration forbidden.
Read joint_alpha_proposal.md for the combined compiler/native implementation sequence.

## What the current runtime establishes

Store selection belongs to Meld and compiled lifetime operations. Creations holds objects and
disposal metadata; it does not decide which scope may resolve or purge a target.

| Existence | Native root construction lock | Native target store / purge lock |
| --- | --- | --- |
| many | No root singleton lock | Caller Space when present, otherwise Conduit; retained disposal entries use store lock |
| unique | Target Spell lock across the inner plan | Spell owner store; purge takes Spell then store |
| unique_per_conduit | Caller store lock across the inner plan | Caller Conduit store |
| unique_per_spell_space | Space store lock across the inner plan | Explicit Space store |
| unique_per_conduit_lineage | Lineage-root store lock across the inner plan | Lineage root's store |
| unique_per_conduit_cluster | Elected-leader store lock across the inner plan | Elected leader's store |

Singleton reads generally have an unlocked first lookup, followed by a writer-lock recheck on a miss.
Generalized unique dependency steps take Spell then store, release the store while constructing,
and reacquire it to publish. `add_creation` relies on its caller's writer discipline. Many registration
owns its store lock. These are current source facts, not guarantees to infer from the class names.

Sources:
- src/melder/aether/spellbook/spell_compiler/codegen_creation_system/shared_assets/creation_runtime_door_compiler.py:497-871
- src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/generalized/compilers/generalized_no_overrides_codegen_creation_compiler.py:871-1145
- src/melder/aether/conduit/creations/creations.py:320-579

## Existing lock-order inversion

Native per-conduit and lineage roots can hold the same store needed by a unique dependency's purge:

```text
creation thread: root store held -> waits for unique child's Spell lock
purge thread:    child Spell held -> waits for that same store
```

The bounded probe uses actual public Meld and purge calls with wrappers over the real RLocks.
It refuses the final contended store acquisition instead of leaving a deadlocked process, then
releases the child lock and verifies that the native creation thread finishes normally.

Both ordinary and override calls reproduce this order for the normal-root per-conduit and lineage
cases. Many/unique root controls do not produce this cycle. Explicit Space and lesser-Conduit controls
hold a different caller store from the unique child's owner store, so this particular cycle does not
form there. Cluster and other cross-store combinations are not qualified by these controls.

This exists before the structural rewrite. Pre-acquiring arbitrary container locks is therefore
not a valid integration strategy. The fix must address shared writer coordination across routes.

Evidence: native_lock_probe.py and native_lock_results.json, twelve lock-order cases.

## A reuse miss is not a settled decision

Two additional native controls pause immediately before the root's writer-lock acquisition. Another
thread publishes the same parent through public Meld. After resuming, the ordinary root reuses that
object; the override root retains its existing override-on-existing-instance refusal.

An early boolean dictionary cannot replace that recheck. The compact prelude must receive a settled
decision and retain the authority behind it until the attempt completes or is abandoned.

Root override-on-reuse policy remains a separate native rule. The integrated compact fixtures use
many roots and do not qualify replacing that policy for shared roots.

## Proposed writer protocol

The experiment retains native Creations as the only live-object/disposal registry. It adds stable
claim identity for one selected store and Spell version. Unique can use the existing Spell lock;
other shared lifetimes need per-entry coordination if this design is selected.

1. Resolve current store ownership through the caller's native scope machinery.
2. In consumer-before-provider order, ask only for shared sites currently demanded by the program.
3. Try to acquire that entry's writer claim without holding a container lock.
4. After acquisition, read the actual stored value under the short store mutex.
5. If another writer blocks the attempt, release every earlier claim before waiting. Retry selection
   only; no constructors, input equality callbacks or registrations have run yet.
6. Once all demanded decisions settle, select active operands and execute generated constructors.
   Publish through native Creations with the existing identity and disposal metadata.
7. Release claims on success and on error. Never retry after application construction begins.

Purge must use the same claim identity. Its detachment happens under the writer and store locks;
native disposal helpers run after both are released. Wrapping the entire old purge call in an extra
lock would incorrectly keep that lock held during user cleanup.

Claims must survive value purge while waiters can still exist. Deleting/replacing an entry lock at
purge would let old and new waiters synchronize on different locks. The experiment keeps records
until its coordinator is quiescent; production retirement belongs to the scope lifecycle contract.

Merely adding per-entry locks is insufficient: opposite acquisition orders can still deadlock.
The experimental nonblocking-acquire/release-before-wait protocol avoids that cycle and retries
before user effects. Fairness, starvation bounds and reentrant construction remain unqualified.

All writers must participate: normal creation, override creation and purge. Keeping the old root
container-lock wrapper around the new program would preserve the inversion and defeat this design.

Evidence: entry_claim_probe.py and entry_claim_results.json, four protocol controls over real stores.

## Compiler/native interface now demonstrated

The peer's separate `CompactClaimPrelude(plan).prepare(select)` emits a consumer-first selection
program. It calls `select(site_index)` only for demanded shared sites, receiving `(found, value)`.
Found values form a fresh reuse mapping; absent descendants under reused parents are never queried.
All incoming consumers settle before a shared provider's operand conditions are decided.

The lead's `NativeCompactAdapter` joins that prelude to native stores and the compact generated body.
Each attempt owns its claims and observations. A contested claim propagates out of the prelude;
the adapter releases the attempt before waiting and trying again. The generated body is compiled once,
with constructor operands supplied per call so concurrent calls do not share mutable call state.

Shared constructor wrappers publish the actual created object to its existing native Creations
store. Many fixtures without disposal remain unregistered, as in the native runtime. This bounded
adapter does not implement the production many-disposal branch or all callable/signature forms.

| Integrated control | Observed result |
| --- | --- |
| Five many dependencies, three supplied | Two providers plus consumer; zero shared-claim callbacks |
| Unique child removed while parent remains live | Only consumer constructs; absent child is not claimed |
| Parent then purged | Child and parent construct again using the same prepared plan |
| Earlier conflicting alias beneath a reused parent | Live service receives 91 and is publicly retrievable from its native store |
| Competing publication during claim wait | Prelude retries, reuses one parent and omits its unused child claim |
| Root constructor fails | No constructor replay; claims release and another thread can proceed |
| Dynamic Conduit and explicit Space | Native ticket counts match their respective doors; terminal refusal constructs nothing |

Evidence: native_compact_adapter.py, native_compact_probe.py and native_compact_results.json,
seven integrated cases. Native public reuse-only lookups verify the published instance identities.

## Admission and invalidation

Native dynamic Conduit calls hold a Conduit ticket before reaching their root-index gate. Explicit
SpellSpace calls reach that root-index gate without a Conduit ticket. Parked index-gate callers hold
no index ticket; the Conduit caller still holds its outer ticket. During the observed root constructor,
both doors hold an index ticket. Refusal and completion return the ticket counts to zero.

The claim prelude belongs inside admitted execution. Claims do not replace CreationGate, baseline
validation, capability checks or scope authority. Conversely, CreationGate does not serialize purge,
which deliberately does not drain in-flight resolution.

A request parked at admission can outlive the context it captured. The experimental dynamic adapter
checks the existing epoch/context identity after admission and refuses stale capture; full native
revalidation and retry-to-new-plan integration are not implemented. Reverse-impact gate coverage for
every structural mutation is also not established by these probes.

Sources and evidence:
- src/melder/aether/conduit/meld/creation_context/creation_context.py:237-309
- src/melder/aether/conduit/meld/creation_context/creation_context_factory.py:183-248
- src/melder/utilities/synchronization/creation_gate.py:349-415
- native_admission_probe.py and native_admission_results.json, five admission/disposal controls

## Production changes still required

- Make the native writer contract coherent across ordinary/override root wrappers, dependency
  emitters and Creations purge. Define claim-record ownership, retirement and reentrancy explicitly.
- Build compact physical/socket/provider data upstream, including incoming contract payload sources,
  positional cases and retained-provider readiness. The fixture adapter does not supply those facts.
- Keep request-specific readiness separate from baseline validity; preserve hard root/capability
  and ownership guards. A supplied call must not mark an incomplete baseline globally valid.
- Integrate existing context epochs, gate admission and family-cache hydration without a new global
  cache authority. Experimental byte payloads are not the shipped cache format.
- Preserve root override refusal, hook ordering, disposal and current error translation deliberately.
- Measure native public cold/warm/hydrated paths, contention and ordinary execution. These probes
  establish correctness mechanisms and constructor reductions, not a production throughput gain.

The current claim prototype takes locks for demanded shared sites and allocates diagnostic per-call
state. That is intentionally not presented as the final fast path. Pure many code should retain direct
lowering; shared-hit and uncontended-miss costs require measurement and native specialization.

Peer review identified an O(base sites) wrapper-tuple rebuild in the first native adapter. That version
is retained unchanged. The separate direct-publication variant removes the loop: constructor references
are bound during setup and a call-local publisher is emitted only for a shared constructor that runs.
The deep-all control executes one constructor from 511 base sites with runtime catalog iteration
forbidden, zero shared claims and a 348-byte generated body. The variant duplicates cold compilation
while reusing the first adapter's setup; production should consolidate that cold builder.

No production source, release version or build assets were changed by this investigation.
