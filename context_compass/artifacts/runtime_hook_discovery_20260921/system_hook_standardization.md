# System hook inventory and common management proposal

- Ticket: TASK-2026-09-21-investigate-runtime-hook-clearing
- Epic: EPIC-2026-09-21-runtime-hook-lifecycle-and-adjustment
- Investigator: updater_0
- Date: 2026-09-22 UTC
- Status: backlog reference; owner parked broad standardization on 2026-09-22
- Authorization: documentation only; no runtime/test edits or asset generation

Current work is limited to `tickets/tasks/2026-09-22_investigate_pooled_conduit_hook_reset_task.md`:
Conduit and SpellSpace Meld pool baseline/reset. The broader proposal below is not active scope.

## Owner objective

Melder is dynamic. Hook registrations must support clearing, re-adding and modification during live
operation. Their API style must also be consistent across subsystems. A collection of unrelated
subsystem-specific setters does not meet that requirement.

Preserve the accepted local/lineage model. Standardizing management does not itself authorize changes
to event timing, callback arguments, callback failure policy, scope inheritance or transaction recovery.

## What was investigated

The original `hook_trace.md` covers Bind, Spell, Meld, Conduit and SpellSpace lifecycle in depth.
This continuation follows the additional runtime families through registration, invocation, mutation
and teardown, with source-wide searches for hook/callback registration, callback fields and related
extension verbs. Generated build payloads were excluded because they duplicate source/documentation.

Search was used to locate code, not to prove behavior. The owners and relevant caller paths cited below
were read. This inventory distinguishes callback subscriptions from providers, strategies, scheduled
work and required owner-notification links. It does not claim every Callable in generated execution
machinery is an application hook, or that source findings have been runtime-tested.

## Existing management capabilities

| Surface | Current registration style | Remove / clear / replace today | Owner and applicability |
| --- | --- | --- | --- |
| Bind | `Book.add_bind_hooks(pre=..., activation=..., post=...)`; sequences, no returned IDs | `clear_bind_hooks()` clears all; no targeted replacement/removal | Book-owned; normal Conduit facade delegates to Book. Include. |
| Configuration seeds | `add_hook(book_id, name, hook)` and `add_hooks(book_id, **hooks)` | No public clear/replace; frozen configuration refuses changes | Initial Book-specific Conduit/Meld policy. Needs a live owner surface without unfreezing unrelated config. |
| Conduit lifecycle/link/contract | `register_conduit_hooks(mapping)` | Additive; no public clear/replace/remove | Local event lists shadow lineage lists. Include with scope preserved. |
| Conduit/Space Meld | Routed through Conduit registration; internal `set_meld_hooks(...)` | Internal reference/copy/overwrite modes; no common public controls | Local effective maps and lineage seeds are distinct. Include. |
| Per-Spell creation | Bind kwargs and SpellBinder `with_*_hook(s)` | Internal `_set_hooks`; selected list replacement and epoch bump | Version-owned, shared by callers. Public target facade still needs selection design. Include. |
| RiftSpace actions/categories | Four register methods return subscription IDs | `unregister_action_hook(id)`; no replace or group-clear | Room-owned, categories command/viewer/codegen; named-action and category-wide levels. Include. |
| Rift events | `register_event_callback(callback) -> id` | `unregister_event_callback(id)`; no replace/group-clear | One room event registry, no event-type filter in registration. Include. |
| Rift memory | `register_memory_callback(callback) -> id` | `unregister_memory_callback(id)`; no replace/group-clear | One room memory registry; presence enables normal memory production. Include. |
| ChangeControlManager | `set_commit_hook(fn)`, `set_abort_hook(fn)` | Replacement; `None` clears each single slot | Frame-owned optional hooks. Include; preserve separate internal validation/dirtying wiring. |
| DevOps transaction session | `register_commit_validator/hook`, `register_abort_hook` append to lists | No IDs, unregister, replace or clear | Per-request, owner-thread session; direct session access is through mediator. Include in mapping with session-state restrictions. |
| SyncWeakRef | `register_on_collect(callback)` | Replaces one callback; `None` clears | GC notification, wrapper lifetime; auxiliary family with specific dispatch constraints. |
| WeakRefNode | Constructor parent callback plus `add_callback(cb)` extras | Extras append only; firing consumes callbacks; cleanup retires all | Container-owned node; preserve internal pruning separately from optional observers. Auxiliary family. |

Common differences: add versus replace vocabulary, callback versus hook parameter names, positional
versus keyword arguments, IDs versus anonymous sequences, all-clear versus selected removal, and
inconsistent callability/lifecycle validation. These differences are concrete migration work.

## Where the most friction is concentrated

Priority below is an engineering recommendation, not an owner-approved implementation order.

| Priority | Boundary | Why it creates friction | Improvement |
| --- | --- | --- | --- |
| Highest lifecycle risk | Conduit -> Meld -> SpellSpace, including pooled reuse | Shared seed maps, copied local maps and retained Space references represent different states. Pool return resets only part of that state. | Define the owner/baseline for each registry, preserve local/lineage semantics, and refresh both Space acquisition paths. |
| Highest ownership risk | Lesser graduation -> Book/Bind | A normal-state facade can still reach the old Book; cleanup and retained child membership compound the problem. | Repair complete Book/reference adoption and parent isolation as its own story. |
| Largest management mismatch | Lists vs subscription IDs vs single callback slots | Adding may append or replace; None may mean clear or leave unchanged; targeted removal is often unavailable. | Agree common explicit register/replace/unregister/clear operations and registration addressing. |
| Largest behavioral mismatch | Changes during multi-stage dispatch | Bind captures all stages together; Meld rereads each stage; Rift captures post at exit. | Select and document one deliberate update-visibility contract, with migration tests. |
| Easier API migration | Rift event/memory subscriptions | IDs and individual removal already exist; replace and group-clear are missing. | Extend the existing ordered subscription model; preserve memory state and payload types. |
| Needs careful boundaries | Optional transaction/GC hooks beside required internal callbacks | Clear-all could otherwise erase rollback, validation, recording or container-pruning work. | Keep application registrations distinct from required owner plumbing and state-gate mutation. |

Rift action/category hooks fall between the last two groups: IDs already exist, but nesting/concurrency
and '*' addressing need qualification. Method naming should be standardized everywhere in scope;
fixing names alone will not repair the ownership and update-visibility mismatches above.

## RiftSpace dispatch and lifecycle

RiftSpace owns four registries and an ID-to-address map. Address is phase plus category plus optional
action. Registration validates phase/category/callability and stores callbacks in insertion order.
Unregister is an unknown-ID no-op and removes empty buckets. Cleanup clears registries without
disposing application callback objects; it also cleans the owned viewer, commands, event and memory
systems.

Action dispatch order is category pre, action pre, body, action post, category post. Pre lists are
captured at entry; post lists are captured at exit. Callbacks run outside the room registry lock.
A pre failure skips body/post. A body failure still executes post once pre completed. Callback errors
propagate raw, so a post error can replace a body error. New post registrations made during the body
can participate in that same action today.

Command and codegen hooks wrap the RiftGate ticket window. Pre runs before admission; post runs
after ticket release and memory emission. Viewer methods are wrapped through `view_action_hooks`,
with FrameViewer/ViewFrame/ViewConduit/ViewSpell/ViewMultiFrame delegating to the room's same scope.
These are dispatch adapters, not independent hook registries.

Two source-derived regression candidates require future runtime tests:
- Depth is one room-wide counter per category, not per thread/context. Overlapping same-category
  operations can be mistaken for nested calls; hook delivery can depend on their exit order.
- `action_name="*"` is accepted as an ordinary name, but unregister interprets `"*"` as the category
  marker. That can remove the reverse address while leaving the actual action registration behind.

Evidence:
- `src/melder/nexus/rift/rift_space/rift_space.py:155-322`
- `src/melder/nexus/rift/rift_space/rift_space.py:325-409`
- `src/melder/nexus/rift/rift_space/rift_space.py:596-990`
- `src/melder/nexus/rift/frame_viewer/view_action_hooks.py:11-67`
- `src/melder/nexus/rift/frame_viewer/frame_viewer.py:6651-6673`
- `src/melder/nexus/rift/frame_viewer/view_frame.py:160-177`
- `src/melder/nexus/rift/frame_viewer/view_conduit.py:118-134`
- `src/melder/nexus/rift/frame_viewer/view_spell.py:124-140`
- `src/melder/nexus/rift/frame_viewer/view_multiframe.py:138-152`
- `src/melder/nexus/rift/command_system/command_system.py:1009-1157`
- `src/melder/nexus/rift/command_system/command_system.py:1171-1200`
- `src/melder/nexus/rift/command_system/codegen_command_system.py:634-890`

## Event and memory subscriptions

Both systems snapshot the ID-ordered callback dictionary under their own RLock, then invoke outside
that registry lock. Each callback receives the emitted RiftEvent or RiftMemory. Removing a callback
during emission does not remove it from that emission's snapshot. The first raw exception stops the
remaining callbacks. Return values are ignored.

Memory callback presence is `memory_enabled`; ordinary command emission skips building a record
when there are no subscribers. Clearing callbacks must leave counters and shared context intact.
Each room owns and cleans its systems. Registry cleanup releases references and does not call user
callback disposal methods.

Caller context still matters: CodegenEventPublisher holds its producer lock across event publication.
Workstation's weak-collection publication suppresses failures. Command memory emission happens after
the gate ticket is released. A statement that these callbacks run outside every lock would be false.

Evidence:
- `src/melder/nexus/rift/rift_space/event_system/rift_event_system.py:78-290`
- `src/melder/nexus/rift/rift_space/memory_system/rift_memory_system.py:80-435`
- `src/melder/nexus/rift/codegen_system/observability/codegen_event_publisher.py:213-248`
- `src/melder/nexus/rift/rift_space/workstation.py:821-888`
- `src/melder/nexus/rift/command_system/command_system.py:1072-1157`

## Change control and transaction boundaries

Manager setters replace single slots, with None disabling them. Manager dispatch snapshots each
phase's references under its lock and invokes outside it. Order is structural validator, general
validator, dirty marker, general commit hook. The orchestrator holds manager dispatcher references;
its clear operation cannot be treated as equivalent to clearing optional application commit hooks.

Session callbacks are append-only lists. Commit captures validators and hooks together; abort
captures abort hooks and rollback actions, invoking rollback in reverse order. Registration currently
lacks callable/status/owner-thread checks even though join has explicit owner-thread checks.
Terminal-session mutation and mid-commit registration therefore require an explicit future contract.

The mediator runs session commit callbacks, strategy commit delta, then orchestrator commit. It
dispatches strategy on_end in finally. Session abort collects BaseException failures, but the shown
mediator finalizer ignores that returned list. Orchestrator abort failures are suppressed. Error-policy
standardization must account for these actual paths, not infer one policy from the word "hook".

Public Book/Conduit transaction context managers yield the Book/Conduit, not a TransactionSession.
Do not advertise session hook methods as if they already have those public facades.

The separate aetheric plane registers strategy classes, not hook subscriptions. on_start runs after
admission, commit delta runs while claims are held, and on_end participates in finalization. Its
described rollback actions have OPEN-state registration and terminal-discard rules. These recovery
obligations must retain their contract; generic observer clearing must not discard pending inverses.

Evidence:
- `src/melder/aether/aetheric_frame/dev_ops/change_control_manager/change_control_manager.py:222-334`
- `src/melder/aether/aetheric_frame/dev_ops/change_control_manager/change_control_manager.py:427-642`
- `src/melder/aether/aetheric_frame/dev_ops/change_control_manager/change_control_manager.py:783-878`
- `src/melder/aether/aetheric_frame/dev_ops/change_control_manager/transaction_manager/transaction_session.py:409-528`
- `src/melder/aether/aetheric_frame/dev_ops/change_control_manager/orchestrator/orchestrator.py:448-587`
- `src/melder/aether/aetheric_frame/dev_ops/change_control_manager/transaction_manager/transaction_mediator.py:971-995`
- `src/melder/aether/aetheric_frame/dev_ops/change_control_manager/transaction_manager/transaction_mediator.py:1043-1089`
- `src/melder/aether/conduit/conduit.py:3075-3096`
- `src/melder/aether/spellbook/spellbook.py:4513-4534`
- `src/melder/aether/aetheric_mediator/transaction_strategy.py:91-212`
- `src/melder/aether/aetheric_mediator/strategy_builder.py:197-226`
- `src/melder/aether/aetheric_mediator/transaction_session.py:641-681`
- `src/melder/aether/aetheric_mediator/transaction_session.py:896-1002`
- `src/melder/aether/aetheric_mediator/mediator.py:525-584`
- `src/melder/aether/aetheric_mediator/mediator.py:644-755`

## Other callback and extension seams: explicit classification

| Seam | Actual contract | Standardization implication |
| --- | --- | --- |
| ResearchSet on_mutation | Constructor callback; hosted root supplies composition emission. Hydration reconnects it after rebuilding; failures propagate. Standalone sets may receive caller callbacks. | No current live setter. Preserve the hosted recording link; decide whether to expose a separate observer family or standardize only standalone callback management. |
| ACL change_callback | Nexus callback passed through FrameACLManager into containers; refreshes Rift projections after changes | Internal notification wiring. User-hook clearing must preserve projection updates. |
| Validity notifications | SpellSystemStates attaches a RiskManager object and propagates it to child state; notifications call its concrete methods | Collaborator wiring, not an anonymous subscription registry. |
| Dirty-root revalidator | One function per conduit returning the validated root set; callers use its result | Execution service. Preserve return semantics; do not turn into fire-and-forget notification. |
| Weak-reference collection | SyncWeakRef has a replaceable single callback; WeakRefNode has parent plus extras, consumes on fire, suppresses errors | Auxiliary callback family; maintain GC/no-lock and container-pruning rules. Do not clear parent pruning with optional observers. |
| External persistence handlers | Frozen configuration of store/fetch/list/delete and legacy upload/download/list; whole-manager runtime replacement | Transport/provider lifecycle; fetch/list return data. Emission tap reuses store_unit, not a separate hook registry. |
| Channel logger resolver | Replaceable and clearable process-wide provider, emits root presence markers | Provider API, not an event hook chain. |
| SyntheticModule import hook | Install/remove one finder in sys.meta_path | Python import interceptor with process scope. Existing install/remove semantics remain a separate contract. |
| PhaseScheduler / UnitOfWork | Named factories and task functions; UnitOfWork inherits Future | Task scheduling and inherited Future callbacks, not another Melder subscription API. |
| Rift.on_nexus_frame_disposed | Logging-only method today | Placeholder event seam; no callback registration to standardize yet. |
| Strategy registries / virtual lifecycle methods | Typed strategy classes or implementations, including transaction/compiler/ACL/research strategies | Replacement of executable policy, not registration of observational callbacks. Do not erase typed extension contracts. |

Evidence:
- `src/melder/mutation_research/research_set/research_set.py:129-288`
- `src/melder/mutation_research/research_set/research_set.py:2634-2645`
- `src/melder/mutation_research/mutation_research.py:885-903`
- `src/melder/mutation_research/mutation_research.py:3930-3972`
- `src/melder/nexus/frame_acl_manager.py:276-289`
- `src/melder/nexus/acl/frame_acl_container.py:132-192`
- `src/melder/nexus/acl/frame_acl_container.py:1331-1340`
- `src/melder/nexus/nexus.py:2716-2728`
- `src/melder/aether/aetheric_frame/dev_ops/spell_system_states/spell_system_states.py:832-859`
- `src/melder/aether/aetheric_frame/dev_ops/spell_system_states/conduit_resolution_state.py:728-736`
- `src/melder/aether/aetheric_frame/dev_ops/change_control_manager/change_control_manager.py:1257-1291`
- `src/melder/aether/aetheric_frame/dev_ops/change_control_manager/change_control_manager.py:1522-1576`
- `src/melder/utilities/synchronization/sync_weak_ref.py:109-261`
- `src/melder/utilities/synchronization/sync_weak_ref.py:325-347`
- `src/melder/utilities/data_structures/weak_data_structures/weak_ref_node.py:109-212`
- `src/melder/utilities/data_structures/weak_data_structures/weak_ref_node.py:493-553`
- `src/melder/crystallizer/asset_management/external_persistence_manager_configuration.py:488-628`
- `src/melder/crystallizer/asset_management/external_persistence_manager_configuration.py:867-919`
- `src/melder/crystallizer/asset_management/asset_management_system.py:482-523`
- `src/melder/crystallizer/asset_management/asset_management_system.py:976-1043`
- `src/melder/crystallizer/asset_management/external_persistence_manager.py:83-154`
- `src/melder/crystallizer/asset_management/external_persistence_manager.py:479-559`
- `src/melder/aether/aether_utility_system.py:280-374`
- `src/melder/crystallizer/synthetic_module.py:1298-1340`
- `src/melder/utilities/synchronization/phase_scheduler.py:618-677`
- `src/melder/utilities/synchronization/unit_of_work.py:1-19`
- `src/melder/utilities/synchronization/unit_of_work.py:195-255`
- `src/melder/nexus/rift/rift.py:1124-1147`
- `src/melder/aether/spellbook/spell_compiler/validation/validation_system.py:193-243`
- `src/melder/mutation_research/diff/diff_engine.py:155-180`
- `src/melder/nexus/acl/configurations/profiles/view/frame_acl_view_profile_builder.py:132-151`

## Recommended common management contract — proposal, not implemented

Use one vocabulary and one registration-address model for application hook registries. Stable
registration IDs already work in RiftSpace/event/memory and allow replacing one callback without
guessing identity, losing its position, or clearing unrelated callbacks.

| Proposed operation | Meaning |
| --- | --- |
| `register_hook(hook_name=..., hook=...) -> str` | Append one validated callback and return its registration ID. |
| `register_hooks(hooks=...)` | Optional common batch form: mapping of hook names to callback sequences; validate the whole batch before publishing any change; return IDs grouped by name. |
| `replace_hook(hook_id=..., hook=...) -> None` | Replace the selected callback while preserving its ID and position; unknown ID raises KeyError. |
| `unregister_hook(hook_id=...) -> bool` | Remove one registration; False when the ID is absent. |
| `clear_hooks(hook_name=None) -> int` | Clear one event or all application hooks on this owner; return removed count. Does not clean the owner. |

These are proposed spellings. Keep the same parameter names, keyword style, input shapes and return
conventions on every included hook-management surface. Do not implement subsystem-specific variants
of the same operation. Event-specific callback payloads remain typed by their actual contracts.

Owner placement needs one explicit design decision: direct owner methods versus a consistently exposed
hook-management property. Either must preserve the existing Book-to-Conduit facade and the selected
Spell's ownership. A per-Spell mutation must use deliberate target selection; it must not require users
to reach into private maps. The proposal does not silently select a new public container abstraction.

Recommended common rules:
- Validate before mutation, including the complete batch. Repeated registrations are distinct and
  preserve order; replacement retains position. Clearing is idempotent and permits subsequent add.
- Use owner-scoped IDs; do not recover missing IDs through callback equality or global searches.
- Changes operate on the selected owner's application registrations. Clearing a local overlay must
  retain the accepted inheritance behavior; clearing and suppressing inherited callbacks are distinct.
- Release references to callbacks without disposing them. Reset pooled leases explicitly; never clear
  a borrowed parent dictionary in place.
- Publish coherent callback selections during mutation. Dispatch uses a stable selection rather than
  iterating a list being edited. Prefer the Bind-style whole-operation selection for multi-stage calls,
  but record that adopting it changes today's Meld/RiftSpace later-stage visibility and needs approval.
- Keep callback exception policy explicit at dispatch: advisory lifecycle, required validation and
  transaction recovery are different contracts. Registration errors can be uniform without erasing them.
- Session mutation requires a valid live session state and owner context. Clearing registrations is
  not permission to delete required rollback actions, dirty markers or parent notification plumbing.
- Keep inspection/readback consistent if exposed; return detached descriptions, not mutable registry maps.

## Internal structure and performance constraints

Recommend a small shared registration-storage implementation for IDs, ordered event lists, validation,
replace/remove/clear and coherent publication. Keep event dispatch and scope ownership in their current
subsystems. Standardize code shape and docstrings alongside the public APIs.

Updates are the infrequent path: build immutable callback selections there. Preserve existing cheap
hook-presence branches, direct callback dispatch and Spell epoch invalidation. Do not introduce an
owner-hierarchy walk, repeated identity search, new per-Meld allocation or registry lock just to
standardize naming. This is an implementation target, not a measured performance claim.

Single-slot setters can remain compatibility entrypoints that atomically replace their logical event's
registrations. Existing bind/Rift wrappers should delegate to the common mechanism. Final migration
policy for old names, event vocabulary and facade placement remains owner review work.

Recording remains values only. Book bind/config markers already exist; local Conduit/Meld and Spell
presence need explicit owners/update emissions. Additional families must not be declared persistent
merely because the new registry is shared. Callback bodies and runtime IDs are not restored as functions.

## Implementation sequence to propose after design approval

1. Agree the common verbs, addressing, placement, scope semantics and in-flight rule.
2. Repair lesser/Space pool baseline handling as a bounded lifecycle change.
3. Implement common registry mechanics and migrate one family with meaningful regression tests.
4. Apply the same public shape to Bind, Conduit/Meld/Spell, Rift action/event/memory and appropriate
   optional transaction hooks. Qualify auxiliary/internal seams before exposing new mutation doors.
5. Address graduation ownership independently; its Book/Space/parent references are broader than hooks.
6. Update recording markers, docs and examples, then run generators only after owner code approval.

Future tests must cover ordered replace, ID stability, clearing/re-add, invalid-batch no-change,
duplicates, callback mutation during dispatch, cross-thread publication, cleanup/reference release,
local/lineage isolation, both Space acquisition paths and idle-parent updates, warm Meld behavior,
Rift nested/overlapping actions, '*' addressing, session finalization and failure preservation.

No new tests ran. The earlier sixteen core characterization cases remain historical evidence; they
do not qualify this broader design. Performance, concurrency reproductions and the proposed APIs have
not been tested because this is a documentation-only investigation.
