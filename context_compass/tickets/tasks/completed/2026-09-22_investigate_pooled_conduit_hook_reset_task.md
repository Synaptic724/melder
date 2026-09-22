# Task: Investigate pooled Conduit and SpellSpace Meld hook baseline reset

- Completed: 2026-09-22T19:50:34Z
- Summary: Pool/Space ownership, root propagation and reset findings led to the accepted implemented
  repair. Original characterization and proposal are retained as discovery evidence.

## Metadata
- Task ID: TASK-2026-09-22-investigate-pooled-conduit-hook-reset
- Status: done
- Owner: codex
- Agent Name: updater_0
- Priority: p1
- Created: 2026-09-22T09:11:27Z
- Updated: 2026-09-22T19:50:34Z
- Related epic: EPIC-2026-09-21-runtime-hook-lifecycle-and-adjustment (reopened for this slice)

## Current Reopened Scope
Completed discovery: use the implementation task for delivered behavior. The original investigation
boundaries and symptoms below are historical; the qualified repair now addresses the selected defects.

The owner requests pool fixes next and asks how non-local root updates should propagate, including
empty-to-populated maps. Investigate current behavior and record a bounded proposal first. Graduation
is complete; broad standardization remains deferred. No runtime source or test-suite edits and no
generators in this discovery pass. Small artifact-owned characterization runs may verify the trace.

## Objective
Investigate only restoration of Conduit/Meld and SpellSpaceMeld hooks across pool leases. Evaluate the owner's
suggested modified flag and pool-owned safe copy of root hooks, including deterministic release of
saved callback references during pool cleanup. Establish the minimum correct change before coding.

## Ticket Contract
- ENTRY_GATE: Owner explicitly requested this narrowed investigation and parked the broad epic.
- EXECUTION_BOUNDARY: Source reads and documentation for Conduit, ConduitPool, Meld and their hook
  initialization/mutation/reset/cleanup paths, including both manual and managed SpellSpace pool paths.
  Owner explicitly confirmed SpellSpace inclusion. Current follow-up also includes source tracing of
  bind hooks when a lesser graduates to normal. No new independent Space lifecycle-hook feature.
- DEPENDENCIES: Existing root/local hook behavior and pool lifecycle. Prior core trace is reference.
- EXIT_GATE: Source-backed ownership/copy/flag/reset/cleanup proposal; root-update assumptions and
  any necessary nested-pool handling are explicit. Future regression cases are identified.
- FAILURE_ESCALATION: Record a concrete boundary if the fix would require global root propagation,
  a shared mutable hook-holder object or unrelated lifecycle repair; do not implement that expansion.

## Scope Boundaries
- In scope: modified-state tracking, saved baseline ownership, fresh/reused lesser and SpellSpace
  consistency, cleanup ordering, aliased callback lists and retained nested Meld hook references.
- Out of scope: universal hook APIs/IDs, root-wide live propagation implementation, other callback systems,
  per-Spell/Bind changes, graduation repair, new persistence behavior, runtime/test edits and generators.
  Graduation source investigation is explicitly included by the latest owner request; repair remains separate.
- Root dynamic-update behavior is now explicitly in discovery scope; implementation still requires its contract.
- Owner explicitly accepts method-only mutation tracking. Direct edits to hook lists/dictionaries
  are outside the supported contract; do not add proxies, integrity scans or defensive mutation detection.

## State Transition Event
- from_state: in_progress
- to_state: done
- transition_reason: Owner accepts the implemented repair and turns in its completed discovery work.

## Steps / Checklist
- [x] Trace root seeds, effective local maps and pool initialization/ownership order.
- [x] Trace mutation flag placement, partial-failure behavior and fresh/reused lease restoration.
- [x] Trace saved-copy and nested-reference cleanup, including pool eviction.
- [x] Record the focused plan, baseline alternatives and future regression matrix.

## Deliverables
- Findings and focused proposal in this task's Notes and handoff summary.
- Prior broad epic and discovery task moved to backlog with evidence retained.

## Files / Paths Impacted
Documentation only in ContextCompass. Source investigation targets:
- src/melder/aether/conduit/conduit.py
- src/melder/aether/conduit/conduit_pool.py
- src/melder/aether/conduit/meld/meld.py
- src/melder/utilities/general_base/abstract_elastic_pool.py
- src/melder/aether/conduit/spell_space/spell_space.py
- src/melder/aether/conduit/spell_space/spell_space_pool.py

## Required Reading
Use src_components index slices for Conduit Runtime, Conduit Hook Wiring and Creations/SpellSpace.
Read the exact initialization, registration, acquisition, return, eviction and cleanup methods above.
Use source to settle behavior; the prior trace records known retained-map symptoms, not this design.

## Validation
- Runtime tests: Not run. This task is investigation/documentation only.
- Future tests must distinguish safe shallow copies of containers from shared callback objects,
  no-change versus modified leases, failed registration, root/local semantics and nested pool reuse.

## Risks / Rollback Notes
- A dict copy alone still aliases mutable inner lists; copying callable objects is not intended.
- A modified flag must cover every supported mutation that can leave state behind, including failure.
- Resetting one Meld pointer may leave another pooled object holding its old local map.
- A saved baseline is not an automatic live view of root changes; define that boundary explicitly.

## Applicable Anti-Patterns
- [ ] No broader hook framework or unrelated lifecycle fixes introduced.
- [ ] No clearing borrowed root lists or disposing user callback objects.
- [ ] No claims of runtime reproduction without an actual authorized run.

## Artifact Links
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - artifacts/pool_hook_propagation_20260922/
- DISPOSITION: retain_as_reference
- Reference: artifacts/runtime_hook_discovery_20260921/hook_trace.md
- Broad reference: tickets/epics/completed/2026-09-21_runtime_hook_lifecycle_and_adjustment_epic.md

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS: none

## Noting Behavior
Record each completed source trace with evidence and one next step. Keep the scope narrow.

## Notes
- DATETIME: 2026-09-22T09:11:27Z
  TYPE: PLAN
  CLAIM: Owner narrowed work to pooled Conduit/Meld hook reset and requested the broad epic be
    backlogged. Investigate a modified flag and a pool-owned safe baseline; do not assume support for
    changing root hooks everywhere without a shared holder. No code/test changes or asset generation.
  EVIDENCE:
  - Owner's current modified-flag, root-reset, pool-copy and backlog instruction.
  IMPACT: This standalone task is the only active hook investigation.
  NEXT: Trace construction order and which root map currently supplies fresh lesser hook state.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-22T09:11:27Z
  TYPE: DECISION
  CLAIM: Owner explicitly confirmed SpellSpace belongs in the narrowed pool/Meld hook investigation.
    Trace its separate Meld hook reference and both pool paths alongside Conduit reset.
  EVIDENCE:
  - Owner's follow-up: "its also spellspace remember? maybe thats impacted too with meld".
  IMPACT: Space reset is core scope here; this does not reopen other callback families or new APIs.
  NEXT: Trace the root/Conduit/Space reference chain and the pool baseline capture points.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-22T09:18:15Z
  TYPE: FACT
  CLAIM: Root Conduit establishes its lineage seed maps and ConduitMeld before constructing either
    pool, so both have a valid hook source at pool initialization. ConduitPool currently stores no
    baseline and never constructs on a miss; Conduit.create_lesser_conduit owns the fresh path.
    SpellSpacePool stores its owner ConduitMeld and creates new Spaces from its current fields.
    Both concrete pools inherit cleanup that destroys idle objects but does not release subclass
    fields. A new baseline therefore needs explicit subclass-owned cleanup after idle destruction.
  EVIDENCE:
  - src/melder/aether/conduit/conduit.py:334-395
  - src/melder/aether/conduit/conduit_pool.py:57-161
  - src/melder/aether/conduit/spell_space/spell_space_pool.py:65-279
  - src/melder/utilities/general_base/abstract_elastic_pool.py:196-217
  IMPACT: A safe copy can be captured without a new hook-holder type. Copy dict and inner callback
    sequences, not callback objects. Passing None to fresh Conduit construction means reread config,
    so a deliberate empty baseline must not accidentally use the fallback path.
  NEXT: Trace mutation and release/acquire behavior to locate flag/reset operations and nested aliases.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-22T09:18:15Z
  TYPE: DECISION_REQUEST
  CLAIM: Asked whether the pool baseline is fixed at pool creation or refreshed from the current
    owner on each new lease. These differ when root hooks change. No answer has been received yet.
  EVIDENCE:
  - Owner's saved-copy proposal and concern about dynamically changing root hooks.
  - src/melder/aether/conduit/conduit.py:334-395
  - src/melder/aether/conduit/spell_space/spell_space_pool.py:119-145
  IMPACT: A modified flag only records local edits; it cannot by itself detect that a borrowed owner
    hook map was replaced. Keep both baseline choices explicit until the owner answers.
  NEXT: Continue independent mutation/reset/cleanup tracing while the baseline question is pending.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-22T09:21:47Z
  TYPE: FACT
  CLAIM: Public Conduit registration changes local lifecycle state first and may later fail while
    processing Meld callbacks. A reset flag set only at successful return would miss that partial
    mutation. Meld local mode creates copied effective lists; resetting by reference to a pool-owned
    baseline can therefore avoid reconstructing callbacks on each ordinary lease. Root lineage seed
    tables are distinct from the root ConduitMeld's effective local map: fresh lessers use seeds,
    whereas fresh Spaces use their immediate owning ConduitMeld's effective map.
  EVIDENCE:
  - src/melder/aether/conduit/conduit.py:1657-1711
  - src/melder/aether/conduit/conduit.py:1779-1840
  - src/melder/aether/conduit/conduit.py:2296-2388
  - src/melder/aether/conduit/meld/meld.py:1264-1307
  - src/melder/aether/conduit/spell_space/spell_space.py:166-208
  IMPACT: The flag should describe divergence from the relevant baseline and must cover failure
    residue. Do not silently replace lesser seed inheritance with root-local effective hooks.
  NEXT: Map Space inherited divergence and the complete release/cleanup path into the narrow proposal.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-22T09:21:47Z
  TYPE: FACT
  CLAIM: A Space can inherit a modified owner-Meld map at construction without any local mutation.
    Manual Space cleanup and managed recycle both preserve the SpaceMeld map. Managed acquisition
    bypasses prepare_object, so a fix there alone misses enter_spellspace. Lesser cleanup returns its
    active/manual Spaces to its retained SpacePool before clearing local lifecycle hooks, leaving
    their old effective Meld references alive. Prewarming also uses acquire_untracked for Spaces
    and normal create/cleanup for lessers. Pool cleanup destroys idle objects before clearing idle
    storage; saved baseline ownership needs its own terminal release after these callbacks finish.
  EVIDENCE:
  - src/melder/aether/conduit/spell_space/spell_space.py:166-208
  - src/melder/aether/conduit/spell_space/spell_space.py:266-398
  - src/melder/aether/conduit/spell_space/spell_space_pool.py:119-279
  - src/melder/aether/conduit/conduit.py:564-621
  - src/melder/aether/conduit/conduit.py:954-1000
  - src/melder/aether/conduit/conduit.py:1116-1210
  - src/melder/utilities/general_base/abstract_elastic_pool.py:196-217
  IMPACT: A local-modification bit on Space alone is insufficient for inherited changes. Fresh,
    prewarmed and reused objects must meet the same chosen baseline contract. Hook restoration
    belongs after current-lease disposal and before pool publication; do not alter disposal behavior.
  NEXT: Record fixed versus current-owner baseline alternatives while awaiting the owner's answer.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-22T09:23:54Z
  TYPE: MEASURE
  CLAIM: The broad epic and discovery task were moved to their backlog directories without
    overwriting destinations. Active routing now points only to this narrow task, and the retained
    artifact association follows the backlogged task. All 21 source ranges in this task resolve
    within file bounds. No runtime/test changes, test runs or generated assets occurred.
  EVIDENCE:
  - tickets/epics/completed/2026-09-21_runtime_hook_lifecycle_and_adjustment_epic.md
  - tickets/tasks/backlog/2026-09-21_investigate_runtime_hook_clearing_task.md
  - attention_board.md:86-86
  - artifact_board.md:67-67
  IMPACT: Scope and re-entry routing match the owner's narrowing. Baseline selection remains an
    unanswered design question, not an authorization to implement either alternative.
  NEXT: Discuss fixed baseline versus adoption of current owner hooks for new leases.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-22T09:36:10Z
  TYPE: DECISION
  CLAIM: Owner explicitly rejects strict detection of direct list edits and requires hook changes
    through methods. Existing public Conduit.register_conduit_hooks adds lifecycle/Meld callbacks;
    the internal Meld.set_meld_hooks supports reference replacement, local merge and overwrite.
    SpellSpace has its own Meld but no direct public hook setter. Track supported method calls only.
  EVIDENCE:
  - Owner's method-only mutation instruction.
  - src/melder/aether/conduit/conduit.py:1657-1711
  - src/melder/aether/conduit/meld/meld.py:1264-1307
  - src/melder/aether/conduit/spell_space/spell_space.py:166-208
  IMPACT: The modified flag can be maintained at explicit mutation seams. Arbitrary raw-container
    mutation requires no detection or support; public add and internal replacement remain distinct.
  NEXT: Map flag updates to these existing methods and pool restoration after the baseline choice is settled.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-22T10:09:11Z
  TYPE: DECISION
  CLAIM: Owner requests reonboarding and a focused source investigation of pooled Meld/SpellSpace
    hooks plus bind-hook behavior on lesser graduation. Broad standardization stays backlogged.
    The earlier API/flag implementation slice is held during this investigation; no runtime or
    test edits, asset generation or broader ownership repair in this pass.
  EVIDENCE:
  - Owner's current reonboard, pool/SpellSpace and bind-graduation instruction.
  - tickets/tasks/completed/2026-09-22_add_local_hook_setters_and_tracking_task.md:11-30
  IMPACT: Reverify prior discoveries against live source and record a bounded recommendation.
  NEXT: Read the relevant component slices, then trace the actual pool and graduation call paths.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-22T10:13:25Z
  TYPE: FACT
  CLAIM: Re-read current source after reonboarding. Lesser return clears only its local Conduit
    lifecycle map; it preserves ConduitMeld._meld_hooks and the retained SpacePool. Reacquisition
    changes state and reattaches the ward without rebasing Meld hooks. Each fresh Space borrows
    its immediate ConduitMeld's current map, but both Space return paths and both acquire paths
    retain that map. Managed acquire_untracked bypasses prepare_object entirely.
  EVIDENCE:
  - src/melder/aether/conduit/conduit.py:334-395
  - src/melder/aether/conduit/conduit.py:565-621
  - src/melder/aether/conduit/conduit.py:2228-2388
  - src/melder/aether/conduit/conduit_pool.py:99-161
  - src/melder/aether/conduit/spell_space/spell_space.py:166-208
  - src/melder/aether/conduit/spell_space/spell_space.py:266-398
  - src/melder/aether/conduit/spell_space/spell_space_pool.py:119-279
  - src/melder/aether/conduit/meld/meld.py:1264-1329
  IMPACT: The previous reset finding remains current. A Space can carry a local owner's old map
    without ever being locally modified itself; a Space-local dirty flag alone misses that case.
    Baseline adoption must cover fresh/reused lessers and manual/managed Spaces together.
  NEXT: Trace graduation's Book factory, live aliases and Bind facade owner before recommending a change.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-22T10:13:25Z
  TYPE: FACT
  CLAIM: Graduation does not reset bind hooks. upgrade_to_normal discards the new Book returned
    by create_new_preset_spellbook; Conduit and Meld retain the parent Book and its lookup aliases.
    A new Book really does construct an empty Bind registry, but that unused registry does not
    become the upgraded conduit's registry. After the normal-state guard admits the hook facades,
    add_bind_hooks and clear_bind_hooks still mutate the old parent Book. Normal teardown also
    calls cleanup on that same Book, whose component cleanup retires Bind and its callback tuples.
  EVIDENCE:
  - src/melder/aether/conduit/conduit.py:1961-2140
  - src/melder/aether/conduit/conduit.py:3098-3179
  - src/melder/aether/conduit/conduit.py:757-866
  - src/melder/aether/spellbook/spellbook.py:219-357
  - src/melder/aether/spellbook/spellbook.py:360-415
  - src/melder/aether/spellbook/spellbook.py:4758-4831
  - src/melder/aether/spellbook/spellbook.py:6387-6423
  - src/melder/aether/spellbook/bind/bind.py:190-349
  - src/melder/aether/conduit/meld/meld.py:228-264
  IMPACT: Clearing hooks on graduation would clear the parent's policy. Repair must adopt the
    correct Book and refresh its dependent references; it cannot be reduced to clearing a hook map.
  NEXT: Keep graduation ownership repair separate from the bounded pool-hook reset.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-22T10:13:25Z
  TYPE: FACT
  CLAIM: Space managed recycling is intentionally thread-confined and lock-free; manual cleanup
    uses the Space lock and Conduit cleanup uses its existing lock. Neither concrete pool owns a
    saved hook baseline today, and inherited pool cleanup only destroys idle objects and clears
    the deque. Upgrade retains the existing SpacePool and SpaceMeld aliases. Ward conversion is
    childless-only and drops its parent pointer without removing the parent's child-map entry.
  EVIDENCE:
  - src/melder/aether/conduit/spell_space/spell_space.py:266-374
  - src/melder/aether/conduit/conduit_pool.py:57-77
  - src/melder/aether/conduit/spell_space/spell_space_pool.py:65-117
  - src/melder/utilities/general_base/abstract_elastic_pool.py:196-217
  - src/melder/aether/conduit/conduit.py:1961-2140
  - src/melder/aether/conduit/conduit_ward/conduit_ward.py:305-329
  - src/melder/aether/conduit/conduit_ward/conduit_ward.py:526-579
  - src/melder/aether/conduit/conduit_ward/conduit_ward.py:1141-1185
  IMPACT: No additional lock is required inside ordinary Meld to implement pool reset. The chosen
    hook baseline needs explicit container ownership and teardown. Graduation needs reciprocal
    detachment, early admission and Space reference handling in its separate repair.
  NEXT: Present the focused findings and baseline recommendation without source changes.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Current Recommendation (Discussion, Not Implemented)
Keep the pool repair small: track supported hook-method changes, restore lease-local hooks after
creation disposal and before idle publication, and cover both manual and managed Space lanes.
Keep all new tracking/restoration off ordinary meld execution.

Preserve the existing distinction between lesser lineage seeds and Space immediate-owner hooks.
For Spaces, recommend adopting the current owner's effective hook map when a new lease begins;
that preserves today's fresh-construction behavior and makes reuse agree with it. Active Spaces
need no broadcast updates. A return-time release is still needed so idle shells do not retain
prior-lease callback references. Nested Space pools must participate when their lesser is returned.
This recommendation is not an answer to the pending fixed-versus-current-owner policy question.

The proposed configuration-has-hooks bit describes whether a baseline is empty; it does not describe
local modification or inherited owner replacement. A same-size hook replacement defeats count-based
change detection. Method-maintained modification state handles local edits, while Space lease adoption
handles the inherited-map case without a hierarchy walk during meld.

Graduation remains a separate ownership repair. A correctly adopted fresh Book should retain its
fresh empty Bind, allow new hook registration through the normal Conduit facade, and leave the
parent Book's Bind unchanged. Tests must first reproduce adoption, alias and teardown failures.

## Narrow Proposal and Pending Baseline Decision
The proposed modified flag is useful for skipping restoration when a scope still has its expected
hook state. It is not a replacement for defining that state or tracking changes made by an owner.

| Concern | Smallest responsibility |
| --- | --- |
| Saved copy | Pool owns copies of the hook dictionary and its inner lists/tuples; callback objects remain borrowed. |
| Conduit local mutation | Record divergence before any supported mutation can leave residue, including a partially failing registration. |
| Meld local mutation | Preserve existing copied-local behavior; restore the saved baseline reference instead of clearing borrowed root maps. |
| Return | Dispose/reset current-lease creations first, restore hooks before the object enters idle storage, then clear its modified state. |
| Fresh construction | Supply the same selected baseline as reused objects; otherwise fresh and pooled behavior diverge. |
| Space | Cover cleanup and managed recycle, acquire and acquire_untracked, plus Spaces inside a recycled lesser. No separate Space lifecycle events. |
| Pool teardown | Destroy idle children while their baseline is still usable, then release pool-owned saved containers and borrowed references deterministically. |
| Runtime cost | Keep tracking on registration and pool boundaries; no new work inside meld execution. Scalar read-cost evidence is in the related API/flag task; end-to-end performance is unmeasured. |

For a lesser, current inherited root state means the lineage seed maps, not root-local overlays.
For a Space, current inheritance means its immediate owner's ConduitMeld effective map, even when
that owner is a lesser. Those sources must not be collapsed merely because both are called a root.

The owner was asked to choose between:
- Fixed pool baseline: capture once, initialize fresh/reused scopes consistently from it, and treat
  later local edits as lease-local. This is the smallest model without root-change propagation.
  However, fixed Space baselines would not automatically pick up owner-local changes that today's
  fresh Space constructor observes. That is a behavioral choice, not an incidental implementation.
- Current-owner baseline: new leases adopt the owner's current hooks. A local modified flag alone
  cannot detect owner replacement; require deliberate re-adoption or a baseline revision scheme.
  Active scopes need not be broadcast-updated, but this is more than resetting local modifications.

Pending: no answer received yet. Do not treat elapsed time as approval of either behavior.
Capture timing also matters: pools are created inside Conduit.__init__, before the root's conjure
activation hooks run. A fixed pool-construction snapshot excludes later activation-installed hooks.

Source anchors for capture timing and existing hot-path behavior:
- src/melder/aether/conduit/conduit.py:334-395
- src/melder/aether/spellbook/spellbook_creation_system.py:978-997
- src/melder/aether/conduit/meld/conduit_meld.py:368-403

## Future Regression Matrix
- Unmodified leases retain baseline hooks without reconstructing callback lists every cycle.
- Modified lifecycle hooks and modified Meld hooks both reset, including failed mixed registration.
- Root/sibling callback containers remain unchanged; callbacks themselves are never deep-copied/disposed.
- Fresh, prewarmed and reused lessers/Spaces agree on the selected baseline.
- Manual Space cleanup and managed exit both release lease-local callback references.
- A lesser with a modified Meld and a previously used Space cannot leak that map into the next lease.
- Empty baselines do not trigger Conduit constructor fallback to live configuration.
- Pool overflow and terminal cleanup release saved copies in the correct order.
- Root edits and activation-installed hooks follow the chosen baseline policy explicitly.
- Existing Meld hook-aware/no-hooks execution and compiled-context behavior remain unchanged.

- DATETIME: 2026-09-22T15:25:41Z
  TYPE: DECISION
  CLAIM: Owner reopens pool-hook work and adds investigation of root changes that propagate without
    localizing. Trace hook-present updates and no-hook additions across root, lesser, idle/fresh/reused
    and active SpellSpace runtimes. Graduation is complete and remains a separate closed lane.
  EVIDENCE:
  - Owner's current pool/root-hook propagation instruction.
  - tickets/epics/completed/2026-09-22_graduated_conduit_spellbook_ownership_and_configuration_epic.md
  IMPACT: Earlier exclusions of root-propagation discovery are superseded for this focused pass.
    Do not reopen unrelated hook families, make runtime changes, or regenerate build assets.
  NEXT: Trace current root seed/effective map identity and both pool lease paths in source.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-09-22T15:30:39Z
  TYPE: FACT
  CLAIM: Root baseline and effective Meld references are distinct. Conduit registration always
    localizes; fresh lessers use root._conduit_hooks/root._meld_hooks, while fresh Spaces capture
    the immediate ConduitMeld's effective map. Meld.set_meld_hooks(create_local_hooks=False) only
    assigns this Meld's pointer. Return/acquire paths still retain old Meld maps, including managed
    Space acquire_untracked, which bypasses prepare_object. A local dirty flag cannot detect owner
    pointer replacement or a previously empty baseline becoming populated.
  EVIDENCE:
  - src/melder/aether/conduit/conduit.py:334-395
  - src/melder/aether/conduit/conduit.py:1657-1711
  - src/melder/aether/conduit/conduit.py:2269-2428
  - src/melder/aether/conduit/meld/meld.py:1264-1307
  - src/melder/aether/conduit/spell_space/spell_space.py:166-208
  - src/melder/aether/conduit/spell_space/spell_space.py:266-398
  - src/melder/aether/conduit/spell_space/spell_space_pool.py:119-279
  IMPACT: Root propagation needs an explicit shared publication seam, distinct from local mutation
    and private reference installation. A root-owned baseline must not mutate the frozen frame-wide
    configuration's shared dictionaries. Ordinary fast doors already read the effective hook map.
  NEXT: Characterize empty/seeded root updates and recycled scope behavior without source changes.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
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
## Context / Handoff Summary
Reopened pool/root-propagation investigation complete. Read artifacts/pool_hook_propagation_20260922/proposal.md.
Four current-source root-update cases and six existing characterization tests establish the exact
visibility gaps for initially empty versus seeded hooks. These characterize current behavior, not a fix.
No runtime source, permanent test-suite or generated asset changes were made in this pass.

Recommend root-owned stable shared baselines, explicit shared/local mutation, release of lease-local
maps after disposal, and current-owner adoption in both Space acquisition paths. Do not mutate the
canonical shared frame configuration. No ordinary-meld hierarchy scan or additional lock is proposed.
Set/clear and already-active source-switching details need an explicit contract before implementation.

Graduation is complete and closed; historical bug descriptions above are superseded. Any future hook
baseline initialization must preserve its independent empty Book and root ownership. The requested
Conduit setter/Meld register/flags slice is still unimplemented; broad hook standardization remains parked.
