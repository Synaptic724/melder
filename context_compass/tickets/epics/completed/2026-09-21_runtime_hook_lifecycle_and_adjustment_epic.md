# Epic: Standardize runtime hook APIs and preserve scope lifecycle

- Completed: 2026-09-22T19:50:34Z
- Summary: Completed the owner-approved Conduit/Meld/SpellSpace pool reset and shared-root update
  slice, its regressions, measured costs and canonical documentation. Broader standardization remains deferred.
- Deferred scope: tickets/tasks/backlog/2026-09-21_investigate_runtime_hook_clearing_task.md.

## Metadata
- Epic ID: EPIC-2026-09-21-runtime-hook-lifecycle-and-adjustment
- Status: done
- Owner: user
- Agent Name: updater_0
- Priority: p1
- Created: 2026-09-21T22:28:07Z
- Updated: 2026-09-22T19:50:34Z
- Target Window: completed approved pool/root slice; broader research and package generation deferred
- Related Initiative: Consistent hook management across subsystems, pooling and graduation ownership

## Reopened Scope: Pool Reset and Root Hook Propagation
The owner accepted this completed slice for turn-in on 2026-09-22. Implementation and discovery
tasks are archived with this epic; original pool patch contracts are promoted and archived. The
historical wider proposals below are preserved as deferred research, not claimed as implemented.

Owner approved the focused implementation on 2026-09-22. The active task is
`tickets/tasks/completed/2026-09-22_add_local_hook_setters_and_tracking_task.md` and its patch contracts are
`system_docs/patches/completed/pool_hook_baselines_2026_09_22/`. Those current contracts supersede the
historical discovery-only restrictions below. Broader standardization remains deferred.

The owner reopens this epic for Conduit/Meld/SpellSpace pool behavior and explicitly asks to examine
root hook changes that propagate without localizing. Cover existing hooks being changed and initially
empty hooks receiving additions. The approved source implementation is now qualified and in review.

Graduation ownership is FIXED and turned in under the completed graduation epic. Do not repeat that
repair or treat the historical failure descriptions below as current source behavior. Bind, per-Spell,
Rift and general cross-subsystem hook standardization remain outside this active slice.

Active discovery: tickets/tasks/completed/2026-09-22_investigate_pooled_conduit_hook_reset_task.md.
The accepted model uses root-owned stable dictionaries, existing local semantics and bool-gated
pool restoration. Source review and measurements live under the active implementation task.
All generated/build assets remain held; package version is 0.2.45.

## Historical Authorization and Owner Direction
2026-09-22 follow-up: the owner requested a fresh focused read of pooled Meld/SpellSpace hooks and
bind hooks during lesser graduation. That investigation is recorded in the task below; this broad
standardization epic remains backlogged. Current source still discards the new Book on upgrade,
so bind-hook facades after graduation affect the parent Book. No repair or generation in this pass.

**BACKLOG: the owner parked this broad epic on 2026-09-22.** Its proposal is reference material,
not the current work scope. Active discovery is limited to pooled Conduit/Meld and SpellSpaceMeld hooks:
`tickets/tasks/completed/2026-09-22_investigate_pooled_conduit_hook_reset_task.md`.
Investigate a modified flag and a pool-owned safe baseline, restore root hooks on reuse and release
the pool's saved references during cleanup. Broad hook APIs, global root-update propagation,
graduation ownership and other subsystems are deferred. No implementation is authorized.

**Documentation only. Do not implement repairs, change more tests or generate assets in this pass.**
The owner explicitly considers the current local/lineage model acceptable. Preserve that model and
investigate its lifecycle gaps; do not silently replace it with a new inheritance or propagation model.

The immediate concerns are restoring hook state when pooled objects are reused, understanding
SpellSpace Meld hooks, and establishing what happens to bind hooks when a lesser graduates to normal.
The owner now requires runtime modification as the minimum and explicitly requires a consistent
style across subsystems. This is an API standardization effort as well as a lifecycle repair.

## Owner Requirement: One Consistent Hook Management Style
Applications must be able to add, clear, re-add and modify hook registrations while the system is
live. Providing similar capabilities through unrelated subsystem-specific conventions is insufficient.

The common contract must define these together before implementations diverge further:
- One naming vocabulary and signature style for add/register, remove, replace/update and clear.
  Exact method names remain a design decision; this list describes operations, not approved signatures.
- One accepted callback/sequence registration format and consistent argument order/keyword usage.
- One addressing convention for selecting the event, stage or individual registration being changed.
  Existing subscription IDs and ordered-list APIs must be considered in that common design.
- Consistent clear and replacement meanings, including registering again after clear without
  rebuilding the subsystem or accidentally duplicating callbacks.
- Consistent validation and documented ordering/update-visibility rules. Specify what an in-flight
  invocation sees when another call or one of its own callbacks modifies registrations.
- Consistent return conventions, error presentation, public facades, typing and rich docstrings.
- Corresponding internal ownership/cleanup conventions; use shared registry mechanics where they
  remove duplication without changing scope semantics or adding unnecessary work to dispatch.

Events still supply their actual context and retain their owning scope. Preserve the accepted
local/lineage model. Existing callback failure policies and invocation timing must be mapped into
the proposed standard explicitly; a method-name cleanup must not silently change those behaviors.

Design coverage now includes the additional identified families: RiftSpace action/category hooks,
room event/memory subscriptions and change-control hooks, alongside Bind, Spell, Meld and Conduit.
Their relevant registration, dispatch, update and cleanup paths are now traced in the broader inventory
below. The original core trace alone remains narrower than that system inventory.
Classify infrastructure mechanisms such as SyntheticModule's import hook explicitly when mapping
coverage: a Python import interceptor is a different extension contract from a callback registry.

Implementation, further test changes and generated assets remain held. The common API proposal and
current-to-proposed mapping below are ready for owner discussion.

## Broader Investigation and Common API Proposal
Read `artifacts/runtime_hook_discovery_20260921/system_hook_standardization.md` for the operation
matrix, source evidence, design recommendation and migration sequence. It complements hook_trace.md.

The broader audit confirms three incompatible management styles currently coexist: anonymous callback
sequences, ID-based subscriptions, and replaceable single callback slots. Optional transaction hooks
also coexist with required validation/dirtying/rollback work. Additional callback seams implement
research recording, ACL refresh, weak-container pruning, service providers and Python import behavior.
These are all mapped; callback-shaped internal wiring is not silently classified as user registration.

Recommended management vocabulary, pending owner review:
- register_hook: add one callback and return its stable registration ID.
- replace_hook: replace a selected callback while preserving ID and order.
- unregister_hook: remove one registration by ID and report whether it existed.
- clear_hooks: remove one event's registrations or all application registrations on that owner.
- An optional batch register operation uses the same vocabulary and validates before publishing.

Use the same parameter names, shapes, return conventions and docstring structure on every included
surface. A small shared storage mechanism can provide IDs, ordering, validation and update publication,
while dispatch and ownership remain with each subsystem. Callback context stays truthful to the event.
Exact facade/property placement, event vocabulary and compatibility treatment remain design decisions.

The preferred in-flight rule is stable callback selection for one operation, with updates affecting
later operations. This extends the current Bind precedent but would change Meld/RiftSpace's per-stage
visibility, so it is a proposed semantic decision rather than a change already authorized.

Source-derived additions to future qualification:
- RiftSpace depth suppression is room-wide per category; overlapping threads can suppress each
  other's hooks. The new standard must distinguish concurrent actions from recursive nesting.
- Literal action_name="*" collides with the category marker in unregister routing.
- Event/memory subscriptions snapshot safely at their registry boundary, but producer locks and
  exception handling differ. Clearing memory hooks must retain memory counters/context.
- DevOps session callback additions currently lack callable/status/thread validation at registration.
  Preserve finalization and recovery obligations while defining which updates a live session permits.
- Hosted ResearchSet on_mutation and ACL change callbacks are owner notification links. Their role
  must remain explicit if optional application hook controls are added to those owners.

No runtime reproductions or repairs were made for these newly found cases. Source evidence is in the
inventory; new tests and performance qualification belong to later approved implementation stories.

## Problem / Opportunity
The existing systems have different owners and update semantics. Public runtime registration is
additive; clearing/replacement exists only on some internal surfaces. Pool reuse currently preserves
local Meld state in places where other local state is reset. Graduation also contains a Book adoption
gap, so a fresh Book's empty bind-hook registry cannot be assumed to become the graduated conduit's
registry merely because the factory was called.

Discovery task: `tickets/tasks/backlog/2026-09-21_investigate_runtime_hook_clearing_task.md`.
The bind-hook implementation remains in a separate review task with generated assets held.

Detailed trace: `artifacts/runtime_hook_discovery_20260921/hook_trace.md`. It maps every event in
this scope to its registry, arguments, dispatcher, failure policy and lifecycle boundary. Continued
source reading is authorized; the implementation/test/generation hold remains in force.

## MRP Alignment
Keep the existing local/lineage behavior and make lifecycle transitions trustworthy. A reused scope
must not accidentally retain the previous lease's local callbacks. Graduated ownership must point at
the intended Book. Future hook controls should use these existing owners and preserve the common
no-hooks execution path.

## Historical Model: Source and Probe Findings

Graduation and configuration observations here predate the completed graduation repair. The reopened
pool task and its latest proposal hold current root-update/pooling findings; wider families stay deferred.

| Hook family | Where it lives | Current behavior |
| --- | --- | --- |
| Configuration seeds | SpellbookConfiguration maps keyed by Book ID | Registration is additive before freeze; normal mutation is refused afterward. Separate getters return live maps; the merged getter returns a detached copy. |
| Conduit lifecycle/link/contract hooks | Shared seed table plus a local Conduit table | A nonempty local list overrides the inherited list for that event. Removing the local list reveals inheritance. |
| Meld hooks | Each Meld component's effective map | Shared mode retains a supplied map reference. Local mode copies the effective map and appends callbacks. Conduit retains the original lineage seed separately. |
| Per-Spell creation hooks | The canonical Spell version | Pre/post surround direct Meld requests; activation runs only for newly created results. Scope callers share the same version's hook lists. |
| Bind hooks | The owning Book's Bind component | Independent of these runtime hooks. A newly constructed Book has empty bind-hook storage; Book and normal-Conduit add/clear APIs access the attached Book's registry. |

Preserve the differences above unless the owner explicitly requests a change. In particular, this
epic does not redefine Conduit shadowing as a merge or require live propagation to already-active
scopes simply because another scope's local setup changed.

### Pooled lesser conduits
- Conduit._prepare_for_pool clears its local lifecycle table, resets creations and detaches the ward.
- It does not restore ConduitMeld's effective hook map to the lineage baseline.
- A probe registered a local Meld callback, returned the lesser, reacquired the same shell and
  observed that callback execute in the next lease. Its local lifecycle callback had been cleared.
- This is the immediate reset discrepancy to address while keeping the local/lineage model intact.
- Cleanup-start/complete lifecycle events currently run for permanent teardown, not ordinary lesser
  pool return. Do not silently change that separate event-timing contract as part of resetting maps.

### SpellSpaces
- A SpellSpace owns a SpellSpaceMeld front door and borrows the owning ConduitMeld's effective hook
  map when constructed. It has no separate SpellSpace-specific lifecycle-hook registry today.
- SpellSpace pool return/acquisition retains the old Meld map reference. A fresh space constructed
  after an owner-local map replacement sees the new map; older/recycled spaces retain the old one.
- Define the correct baseline for the next lease and restore it through the pool lifecycle. Check
  both manual create/cleanup and managed enter/exit paths.
- Reset-at-return alone may be insufficient if the owner changes after the space is returned but
  before it is acquired again. Re-entry must meet the selected baseline contract.
- Release previous-lease callback references without calling disposal on user callback objects.
- Adding a separate SpellSpace lifecycle-hook system is not requested by this epic.

### Lesser graduation and bind hooks
**Do not assume the current upgrade actually adopts the newly created Spellbook.**

Source currently does this inside Conduit.upgrade_to_normal:

```python
self._spellbook.create_new_preset_spellbook()
```

The factory returns a new Book; the upgrade does not assign the result to the Conduit or its Meld
component. Existing Book/Meld hook references remain attached. Therefore calling the factory does
not itself reset the graduated conduit's bind hooks.

The intended direction discussed with the owner is:
- Graduation adopts its intended fresh Book and its fresh Bind, whose bind hooks start empty.
- The user can register new bind hooks through the graduated Conduit facade.
- Parent Book hooks stay intact; clearing the parent's registry is not a substitute for ownership.
- Review the complete adoption path before coding: Conduit and Meld Book references, cached registry
  aliases, Book-to-Conduit attachment, transaction identity, visibility of existing definitions,
  existing creations, descendants and cleanup ownership must remain coherent.
- Do not treat this as a one-line assignment fix. A fresh Book is empty and unconjured; preserving
  resolution and creations requires the existing lifecycle machinery to be understood first.
- Upgrade-specific handling of inherited/local Conduit and Meld hooks must be explicit. Current
  code retains those references; do not assume new ownership automatically isolates their maps.

The continued source trace exposes additional graduation obligations:
- Once normal-state guards pass, current bind-hook facades still add/clear on the old attached Book.
  Normal cleanup also calls cleanup on that Book. Parent isolation is therefore a correctness issue,
  not just a decision about whether to copy hook lists.
- Ward conversion currently permits only a childless lesser. The Conduit docstring's statement that
  it retains children is inaccurate. The outer method has already flipped state when this refusal runs.
- Ward conversion drops its parent pointer but does not remove the parent's child-map entry. Parent
  ward teardown still permanently cleans the conduits in that map.
- Existing and idle SpellSpaces captured Book, resolution ID, root/cluster stores and hook references
  at construction. Conduit-only rewiring does not refresh those references.
- Qualify both teardown orders, reciprocal detachment, refusal before mutation and Space reuse.
  Supporting graduation with descendants would be an additional decision; do not assume it works.

This is source-confirmed. A new graduation runtime probe was not run after the owner restricted work
to documentation. It is required before implementation. Earlier bind discovery statements implying
automatic adoption of a fresh hook-empty Book are superseded by this finding.

### Per-Spell adjustment
- Spell._set_hooks already replaces supplied lists, leaves None stages unchanged, updates the hook
  gate and increments _door_epoch. Empty lists clear the selected stages.
- Probes verified late set/clear on warm Conduit and SpellSpace requests without replacing the
  compiled CreationContext. Activation was not retroactively run on an existing unique object.
- The same Spell version's callbacks apply to direct requests from root, lesser and SpellSpace.
- There is no matching general public set/clear surface today. Future wrappers need ownership and
  callback validation and must use this established invalidation path.
- Current callbacks are reread per stage: a pre callback clearing Spell hooks suppresses that same
  call's later post stage. Record the chosen in-flight semantics before exposing adjustment.
- In the tested graph, a dependency's activation callback did not run for inline construction while
  melding its consumer; direct melding of the dependency did run it. Expanding hook execution across
  dependency nodes is a separate behavior decision, not an automatic consequence of adding setters.

### Other findings to retain without expanding the approved model
- Mixed Conduit/Meld registration can partially apply a valid lifecycle update before rejecting an
  invalid Meld callback. Future batch controls need validate-before-mutate behavior.
- Meld dispatch includes on_meld_activation, but current public name validation admits only Meld
  pre/post names. Decide whether to expose that existing branch; do not enable it silently.
- Lifecycle callback errors are logged/suppressed and later callbacks continue. Meld/Spell callback
  errors become HookExecutionError and stop the chain. Clearing APIs must not accidentally unify them.
- Removing the last callbacks should remove empty map entries where appropriate; a nonempty Meld
  map containing empty lists still sends execution through the hooks path.
- Configuration batch additions also apply sequentially and can retain earlier additions after a bad
  later entry. Runtime Conduit registration does not hold one lock over the mixed-map update.
- Root conjure and lesser construction use different signatures: root pre has no arguments and root
  post receives the new Conduit; lesser pre receives the parent and lesser post receives parent/child.
  Root activation occurs before spell-owner wiring/cache hydration; lesser activation precedes attachment.
- Runtime lifecycle dispatch snapshots one chosen event list. Root conjure and Meld iterate live lists;
  Meld rereads maps per stage. Bind alone captures all stages for the whole operation today.
- Ordinary meld reuse runs pre/post, but explicit meld_existing_spell skips all hooks. Supplied
  existing objects never produce created=True, so ordinary meld does not run activation for them.
- Link/unlink callbacks run on the initiating Conduit after its transaction closes. Contract callbacks
  run inside the mutation window and identify only caller/peer, once per successful operation/batch.
  Index add/remove and root-contract removal have no direct hook dispatch. These are not a complete
  graph-change feed; adding event symmetry is a separate behavior decision.
- Per-bind creation-hook kwargs are installed after Bind activation, so explicit kwargs can replace
  stages that the activation callback set. SpellBinder's with_*_hook(s) configures creation hooks.
- Pool overflow permanently destroys an idle lesser after local lifecycle callbacks were cleared.
  Cleanup-complete callbacks receive a Conduit whose core collaborators have already been removed.
- Space hard teardown deletes its Meld reference without invoking Meld.cleanup. Record a focused
  future teardown probe before deciding whether to repair that subordinate lifecycle.

### Crystallizer impact
- Book twins currently report configuration hook names and the new bind-hook markers.
- Current local Conduit/Meld callbacks and per-Spell creation hooks are not represented as equivalent
  presence markers. A recording probe confirmed that preflight reported the configuration seed only.
- Future runtime controls must define where durable hook presence/scope belongs and refresh the
  appropriate twin when changed. Keep callback bodies outside serialization and report required
  application code honestly during restore.
- Preserve current persistence scope: ordinary lesser conduits and SpellSpaces are transient.
  This epic does not enable named lesser persistence or introduce new durable scope types.

## Ticket Contract
- ENTRY_GATE: Owner approves the selected story, desired lifecycle behavior and required patch
  contracts before implementation. Current authorization is documentation only.
- EXECUTION_BOUNDARY: Hook reset/reuse, graduation Book ownership, existing runtime adjustment
  surfaces, cross-subsystem management-style design, recording markers and focused regressions.
  Preserve existing local/lineage semantics. Broader lifecycle coverage is incomplete, not assumed.
- DEPENDENCIES: Conduit/SpellSpace pools; Book/Bind ownership; Meld dispatch; Spell door epochs;
  existing transaction/cleanup and Crystallizer producer/restore contracts.
- EXIT_GATE: Accepted stories demonstrate isolation, next-lease baseline, correct graduation
  ownership and documented adjustment behavior without changing ordinary resolution semantics.
- FAILURE_ESCALATION: Raise a source-backed conflict if ownership repair requires wider registration
  or visibility changes. Keep that work explicit instead of patching maps opportunistically.

## Goals and Scope
- Establish one consistent hook-management API style across applicable subsystems, with runtime
  add/remove/replace/clear/re-add as the minimum capability.
- Restore the intended hook baseline on reused lesser/SpellSpace leases.
- Establish real new-Book adoption on graduation and empty bind-hook initialization for that Book.
- Allow explicit runtime adjustment through existing owners after the lifecycle prerequisites are met.
- Keep parent/sibling hooks, existing creations, ownership and caller permissions correct.
- Keep the ordinary no-hooks path cheap; measure any performance claim before making it.

## Non-Goals
- Implementation, further test changes or generated assets in this documentation pass.
- Replacing the local/lineage model or forcing a new propagation rule on active scopes.
- Adding SpellSpace lifecycle events, named lesser persistence or an unrelated scope model.
- Serializing executable callback code or automatically rebuilding callback functions on restore.
- Changing dependency-node hook execution, lifecycle error policy or cleanup event timing without
  a separate owner decision.

## State Transition Event
- from_state: review
- to_state: done
- transition_reason: Owner accepts the completed pool/root-hook slice; broader standardization stays backlogged.

## Proposed Stories (Not Yet Created or Authorized for Implementation)
0. Shared API contract: use the completed applicable-family inventory to agree one operation vocabulary,
   signature/input shape, addressing/return model, mutation behavior and documentation pattern.
   Map existing APIs to that standard before implementing subsystem controls; retain scope ownership.
1. Pool lifecycle: restore lesser Meld baseline and reset/refresh SpellSpace Meld state at lease
   boundaries, covering owner changes while a space is idle and release of old callback references.
2. Graduation ownership: prove the current references, establish complete new-Book adoption, and
   verify empty new bind hooks, facade re-registration, parent isolation, reciprocal detachment,
   leaf-only refusal ordering and existing/idle Space references.
3. Runtime hook controls: apply the accepted common API to each family in bounded slices, including
   gaps in add/remove/replace/clear/re-add. Mirror Book APIs through Conduit. Map current callback
   failure policies explicitly and avoid accidental behavior changes during standardization.
4. Recording and qualification: record appropriate presence/scope metadata, preserve restore honesty,
   update source documentation and run targeted compatibility/performance checks.

## Milestones
- [x] Source investigation and current-behavior characterization recorded.
- [x] Owner model-preservation and documentation-only directions captured.
- [x] Broader hook families traced and common API/operation mapping proposed.
- [x] Owner selected and approved the bounded pool/root-hook contract.
- [x] Implement and qualify that selected slice; preserve broader proposals as deferred.
- [x] Owner accepts turn-in and canonical documentation; package assets remain separately held.

## Acceptance Criteria and Future Regression Matrix
- Equivalent hook-management operations use the same approved naming, signature and input conventions
  across the included subsystems; differences require a documented scope/event reason.
- Every included family supports runtime clearing, re-registration and modification through its
  owning API. The same operation must not require learning a different subsystem-specific idiom.
- A recycled lesser cannot execute callbacks installed only for its previous lease.
- A recycled SpellSpace starts with the chosen owner baseline; changes while it is idle cannot leave
  an unintended stale map. Active-scope behavior follows the accepted model, not an invented rule.
- Local resets do not clear parent/sibling/shared callbacks or dispose borrowed callback objects.
- After correct graduation, Conduit/Meld use the intended Book and its own Bind registry; old parent
  hooks do not fire for the new Book unless explicitly registered there.
- New normal Conduit add/clear facades affect only its intended Book. Parent binding and Meld still
  work after new-root hook changes and teardown.
- Existing creations, definition visibility, descendants and cleanup remain correct through upgrade.
- Unsupported graduation shapes fail before state mutation. The prior parent no longer owns the
  graduated conduit in its child map, and neither teardown order retires the other root's Book/hooks.
- Existing/pooled Spaces follow the accepted graduation policy without silently retaining stale owners.
- Mixed valid/invalid registrations leave no partial changes under the approved new controls.
- Per-Spell set/clear uses existing epoch invalidation and respects version-wide ownership.
- Warm/no-hook behavior, created-versus-reused activation and in-flight updates are tested explicitly.
- Persistence reports durable hook requirements at the correct owner without serializing functions.

## Required Reading Before Each Story
Start from src_architecture and the verified src_components index. Read the Conduit Runtime, Conduit
Hook Wiring, Meld Resolution, Creations/SpellSpace, Spellbook Configuration and Crystallizer sections.
Use source rather than stale prose where the two disagree; then follow these exact owners:

- Pool story: `src/melder/aether/conduit/conduit.py` — constructor, create_lesser_conduit,
  _prepare_for_pool, _cleanup_spellspaces_for_pool and hard cleanup.
- `src/melder/aether/conduit/conduit_pool.py` — create_object and return_lesser_conduit.
- `src/melder/aether/conduit/spell_space/spell_space.py` — constructor, cleanup, managed recycle
  and _cleanup_for_pool_reuse.
- `src/melder/aether/conduit/spell_space/spell_space_pool.py` — create, prepare, both acquire paths,
  release and destruction.
- Graduation story: `src/melder/aether/conduit/conduit.py` — upgrade_to_normal and normal cleanup.
- `src/melder/aether/spellbook/spellbook.py` — create_new_preset_spellbook, initialization,
  Book/Conduit attachment, bind, transaction metadata, cleanup and new bind-hook APIs.
- `src/melder/aether/conduit/conduit_ward/conduit_ward.py` — _convert_to_normal_conduit and lineage wiring.
- `src/melder/aether/conduit/meld/meld.py` — Book/map aliases captured by construction and cleanup.
- Adjustment story: `src/melder/aether/conduit/conduit.py` — register_conduit_hooks,
  _validate_conduit_hooks_payload, _merge_conduit_hooks, _collect_conduit_hook_chain and dispatch.
- `src/melder/aether/spellbook/configuration/spellbook_configuration.py` — names, add/get/freeze and emission.
- `src/melder/aether/conduit/meld/meld.py` — set_meld_hooks and callback execution/error helpers.
- `src/melder/aether/conduit/meld/conduit_meld.py` — direct resolution, warm-door guards and hook order.
- `src/melder/aether/conduit/meld/spellspace_meld.py` — equivalent Space behavior and guards.
- `src/melder/aether/spellbook/spell.py` — _set_hooks, _door_epoch and cleanup.
- `src/melder/aether/conduit/meld/creation_context/creation_context.py` — created-flag execution contract.
- `src/melder/aether/spellbook/spell_compiler/codegen_creation_system/shared_assets/creation_runtime_door_compiler.py`
  — hook-aware doors return instance/created; changing graph-level callback execution is separate work.
- Recording story: `src/melder/crystallizer/crystals/conduit_crystal.py`,
  `src/melder/crystallizer/crystals/spellbook_crystal.py`,
  `src/melder/crystallizer/crystals/spell_crystal.py`, configuration producers, preflight
  ConfigurationLossStrategy and RestoreEngine reporting.
- Tests: `tests/experimentation/test_runtime_hook_discovery_experiment.py` and the bind-hook tests
  from TASK-2026-09-21-implement-bind-lifecycle-hooks.
- Full event/read map: `artifacts/runtime_hook_discovery_20260921/hook_trace.md`; read the registry,
  dispatch, invocation-consistency, pool/graduation and recording sections before designing controls.

## Evidence Anchors
- `src/melder/aether/conduit/conduit.py:334-363` — seed versus effective map wiring.
- `src/melder/aether/conduit/conduit.py:563-587` — lesser pool return.
- `src/melder/aether/conduit/conduit.py:1657-1711` — current runtime registration.
- `src/melder/aether/conduit/conduit.py:1779-1841` — local shadow/fallback.
- `src/melder/aether/conduit/conduit.py:1960-2140` — graduation.
- `src/melder/aether/spellbook/spellbook.py:6386-6423` — factory returns a separate Book.
- `src/melder/aether/conduit/conduit.py:696-866` — lesser versus normal cleanup ownership.
- `src/melder/aether/conduit/spell_space/spell_space.py:166-208` — initial Meld reference.
- `src/melder/aether/conduit/spell_space/spell_space_pool.py:148-279` — pool reuse and release.
- `src/melder/aether/conduit/meld/meld.py:1264-1329` — reference/copy modes and dispatch errors.
- `src/melder/aether/spellbook/spell.py:638-682` — list replacement and epoch.
- `src/melder/aether/conduit/meld/conduit_meld.py:369-576` — warm guards and selected-target callbacks.
- `src/melder/aether/conduit/conduit.py:422-466` — current Conduit twin producer.
- `src/melder/crystallizer/crystals/spell_crystal.py:1071-1170` — current per-Spell capture boundary.

## Validation / Test Approach
Before the owner's documentation-only instruction, 16 current-behavior probes passed in 4.83 seconds.
Scoped Ruff passed with the repository's Optional/Union policy exceptions. These probes characterize
current behavior, including undesirable cases; they do not turn those cases into desired requirements.
Convert the affected assertions into corrective regressions when the corresponding story is approved.
No runtime repair, further code/test edits or asset generation is authorized by this epic's creation.

## Open Decisions
- Exact common API names/signatures, callback input shape, individual-registration addressing and
  return conventions; shared implementation strategy and migration of current public entrypoints.
- Exact next-lease baseline and reset timing, including owner updates while a SpellSpace is idle.
- Complete Book/definition/creation ownership during graduation; the factory call alone is inadequate.
- Public adjustment names and whether clearing local state restores inheritance or explicitly mutes
  an inherited event. Preserve current behavior until the owner chooses any extension.
- In-flight callback semantics for runtime updates; the new bind hooks' snapshot rule is a precedent,
  not permission to change these systems silently.
- Scope of additional fixes: public Meld activation registration and dependency-node callback execution.
- Whether contract/index event symmetry, Space subordinate hard teardown or graduation with children
  belongs in a later separately approved story. Do not fold those into the small pool-reset repair.

## Risks / Mitigations
- Clearing a shared dictionary can affect other scopes: identify the owner and all aliases first.
- Resetting only the visible Conduit map can leave old callbacks in pooled SpellSpace Meld objects.
- Assigning a new Book without rebinding cached aliases can split resolution, binding and cleanup.
- Hook controls must preserve normal no-hooks execution; avoid unmeasured hot-path hierarchy scans.
- Correct stale docstrings during an approved implementation; do not treat them as runtime evidence.

## Artifact Links
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - artifacts/runtime_hook_discovery_20260921/
  - artifacts/runtime_hook_discovery_20260921/hook_trace.md
  - artifacts/runtime_hook_discovery_20260921/system_hook_standardization.md
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: accepted completion of this epic or an explicit owner disposition.

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS: none
- IF_UNKNOWN: source-backed ownership and baseline decisions before implementation.

## Notes
- DATETIME: 2026-09-21T22:28:07Z
  TYPE: DECISION
  CLAIM: Owner preserves the current local/lineage model and requests documentation in a new epic
    only. Prioritize pool reset correctness, SpellSpace Meld baseline and graduation's new-Book/bind-hook
    ownership. Record the wider adjustment findings without treating them as implementation approval.
  EVIDENCE:
  - Owner's explicit model-preservation, graduation and documentation-only instructions.
  - tickets/tasks/backlog/2026-09-21_investigate_runtime_hook_clearing_task.md
  - artifacts/runtime_hook_discovery_20260921/characterization_final.log:1-2
  IMPACT: This is the new durable program record. Runtime and test work stop at the documentation boundary.
  NEXT: Owner reviews this epic and selects a bounded discovery/repair story.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-21T22:50:14Z
  TYPE: DECISION
  CLAIM: Continued source investigation is complete for the scoped hook families. Preserve the
    accepted model and keep the pool-reset repair independent of graduation ownership. The latter
    now explicitly includes old-Book facade/cleanup targets, reciprocal parent detachment, current
    leaf-only admission and existing/pooled Space references. Dispatch differences and missing event
    symmetry remain documented decisions rather than silently expanded implementation scope.
  EVIDENCE:
  - artifacts/runtime_hook_discovery_20260921/hook_trace.md
  - tickets/tasks/backlog/2026-09-21_investigate_runtime_hook_clearing_task.md
  IMPACT: Future work can resume from the event/read map without rediscovering owners after compaction.
    No implementation approval, test changes or generated assets are implied by discovery completion.
  NEXT: Owner selects the first repair story; recommended starting point is pooled Meld hook reset.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-21T23:28:14Z
  TYPE: DECISION
  CLAIM: Owner sets runtime add/clear/re-add/modification as the minimum and then clarifies that
    style must be standardized across subsystems as well. Elevate the common API contract ahead of
    separate setter implementations. Broaden design coverage to the identified callback families;
    preserve the local/lineage model and keep implementation, test changes and assets held.
  EVIDENCE:
  - Owner's consecutive runtime-modification and cross-subsystem-style instructions.
  - artifacts/runtime_hook_discovery_20260921/hook_trace.md
  IMPACT: Independent subsystem APIs that merely offer the same operations do not satisfy this epic.
    The additional families need lifecycle qualification before any implementation is considered complete.
  NEXT: Develop one concrete management API proposal and map each family's current surface onto it.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-22T00:16:28Z
  TYPE: DECISION
  CLAIM: Broader investigation now covers Rift action/event/memory, manager/session transaction hooks,
    auxiliary GC callbacks and related provider/strategy/internal notification seams. A concrete common
    registration-ID API and migration map are recorded for review. Keep scope ownership, obligatory
    control wiring, callback failure policy and performance boundaries explicit. No code is implemented.
  EVIDENCE:
  - artifacts/runtime_hook_discovery_20260921/system_hook_standardization.md
  - tickets/tasks/backlog/2026-09-21_investigate_runtime_hook_clearing_task.md
  IMPACT: The next decision is one common contract, not independently named setters for each subsystem.
    Existing pool/graduation defects remain separate implementation work with their recorded boundaries.
  NEXT: Review API placement/names, individual addressing and the proposed in-flight selection rule.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-22T09:11:27Z
  TYPE: DECISION
  CLAIM: Owner backlogs this epic and narrows active work to a modified flag plus pool-owned hook
    baseline/reset investigation for Conduit/Meld. Universal registry APIs and dynamic root-hook
    propagation are not approved. Preserve this broader research without continuing its workstreams.
  EVIDENCE:
  - Owner's explicit narrowing and backlog request.
  - tickets/tasks/completed/2026-09-22_investigate_pooled_conduit_hook_reset_task.md
  IMPACT: This epic and its broad discovery task are parked; the new standalone task owns active work.
  NEXT: Resume only if the owner explicitly reopens broad standardization.
  REREAD: HELPFUL
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-22T10:13:25Z
  TYPE: FACT
  CLAIM: Focused source reinspection confirms the existing pool-retention and graduation findings.
    Graduation creates but does not adopt the new Book; normal-only bind-hook facades consequently
    mutate the original Book's Bind. Keep this ownership repair separate from pool hook restoration.
  EVIDENCE:
  - src/melder/aether/conduit/conduit.py:1961-2140
  - src/melder/aether/conduit/conduit.py:3098-3179
  - src/melder/aether/spellbook/spellbook.py:6387-6423
  - tickets/tasks/completed/2026-09-22_investigate_pooled_conduit_hook_reset_task.md
  IMPACT: This does not reopen the broader standardization proposal or authorize graduation repair.
  NEXT: Continue discussion from the narrow task's pool baseline and ownership findings.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Closure Confirmation
- [x] Owner selected and accepted the implemented pool/root-hook slice.
- [x] Completed behavior, qualification and canonical documentation are delivered.

## Noting Behavior
Keep model, ownership and story-order decisions here. Child tasks retain detailed traces and probes.

- DATETIME: 2026-09-22T15:35:19Z
  TYPE: MEASURE
  CLAIM: Four artifact-owned root-update probes confirm public root registration localizes, and
    internal reference installation with create_local_hooks=False does not propagate replacements.
    Fresh Spaces see the new effective map while existing/recycled Spaces and lessers keep the old
    seed. With no seed, root/lesser Meld maps are distinct empties. Six existing characterizations
    reproduce local shadowing, lesser/Space lease retention and partial mixed registration.
  EVIDENCE:
  - artifacts/pool_hook_propagation_20260922/root_update_results.json
  - artifacts/pool_hook_propagation_20260922/existing_probes.log:1-2
  - artifacts/pool_hook_propagation_20260922/proposal.md
  IMPACT: A flag or fixed pool copy cannot deliver the requested root update semantics by itself.
    Recommend root-owned stable live baseline containers, explicit shared/local mutation and lease
    re-adoption; copy containers away from shared frozen configuration, never callback objects.
    Keep internal reference installation distinct so pool reset/graduation cannot edit old owners.
  NEXT: Review shared update visibility and set/clear semantics before implementation.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-09-22T16:07:05Z
  TYPE: DECISION
  CLAIM: Owner emphasizes that hook edits are rare and pooled operations are hot; modification
    tracking should remain a simple bool with minimal locking. Recommend existing mutation locks,
    a bool check at lease boundaries and reference restoration only when necessary. Ordinary Meld
    execution gets no new lock, copy, revision polling or hierarchy scan.
  EVIDENCE:
  - Owner's current bool/lock and rare-event performance direction.
  - artifacts/local_hook_tracking_20260922/read_cost.json:1-29
  - artifacts/pool_hook_propagation_20260922/proposal.md
  IMPACT: Pay normalization/copy/publication costs on rare registration paths. A Space that inherits
    an owner-local map must be marked for restoration at acquisition even if it never changes hooks
    itself. Stable shared baseline identity supports root updates without dirtying every descendant.
    This remains a design recommendation; end-to-end overhead has not been measured or implemented.
  NEXT: Finalize the small shared/local publication and lease-reset contract before coding.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-09-22T16:52:18Z
  TYPE: MEASURE
  CLAIM: The approved pool/root slice is implemented and qualified: 2102 tests pass, with two existing
    owner-deferred shared-context skips. Seventy-three new cases cover pool reset, root publication,
    local isolation, disposal, concurrency, graduation compatibility and warm-door clear recovery.
  EVIDENCE:
  - tickets/tasks/completed/2026-09-22_add_local_hook_setters_and_tracking_task.md
  - artifacts/pool_hook_implementation_20260922/source_review.md
  IMPACT: The historical pool defects above are repaired. Broader standardization remains deferred.
    Empty-cycle pool overhead is about 19-42 ns (1.4-10.3% by scope); ordinary Meld doors are unchanged.
    Generated assets and version remain held for the owner's review.
  NEXT: Review the bounded implementation before canonical promotion and generation.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
Completed by owner instruction. The narrow pool/root-update behavior and 2102-test qualification
are accepted; canonical maps/descriptors and indexes are refreshed. Three original patch contracts
are archived. Broad hook standardization remains in its existing backlog task; packaged/LLM assets
remain on the separate generation hold. No additional runtime changes were made during closure.

Historical review context:
The approved Conduit/Meld/SpellSpace pool slice is implemented and in source review, tracked by
TASK-2026-09-22-add-local-hook-setters-and-tracking. Its source_review.md holds semantics, evidence
and measured costs. The historical discovery findings remain here for context; they are superseded
for this bounded slice. Broader hook standardization stays deferred. Graduation ownership was already
completed separately and its compatibility tests remain green. Generated/build assets are still held.
