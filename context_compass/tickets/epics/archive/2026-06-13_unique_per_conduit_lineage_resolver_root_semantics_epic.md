# Epic: Redefine `unique_per_conduit_lineage` as resolver-root-scoped (one instance per lineage, stored at the lineage root)

## Metadata
- Epic ID: EPIC-2026-06-13-unique-per-conduit-lineage-resolver-root-semantics
- Status: ready
- Owner: user
- Agent Name: compiler_strategy_0
- Priority: p1
- Created: 2026-06-13T23:18:00Z
- Updated: 2026-06-14T00:00:00Z
- Target Window: TBD (large, multi-story; sequence after current optimize-meld-hotpath lane work is parked or in parallel)
- Related Program/Initiative: DI existence-semantics correctness; prerequisite for any cluster/lineage PGO speculation (see EPIC tie-in below)

## Problem / Opportunity
`unique_per_conduit_lineage` (and `unique_per_conduit_cluster`) do not implement the scope their
names promise. In the live runtime they are implemented **identically to `unique`**: one instance
stored in the binding owner's creations, and that store is **baked at compile/hydration time**.

Evidence (current `src/melder`):
- The two runtime doors route `unique`, `unique_per_conduit_cluster`, and
  `unique_per_conduit_lineage` through the SAME branch reading `spell._owner_creations`:
  - `src/melder/aether/conduit/meld/conduit_meld.py:519-533` (`meld_existing_spell`) and `:707-725`
    (`describe_live_creation_status`).
  - `src/melder/aether/conduit/meld/spellspace_meld.py:525-545` and `:700-730`.
- `_owner_creations` is stamped to the **owning conduit's** creations:
  `src/melder/aether/spellbook/spell.py:1116` (`self._owner_creations = creations`) fed by
  `src/melder/aether/spellbook/spellbook.py:3141` (`new_spell._add_owned_conduit(conduit._id, ..., conduit._creations, ...)`).
- The emitted executors **bake** the owner store: the codegen door builder is called with
  `owner_creations=spell._owner_creations`
  (`src/melder/aether/spellbook/spell_compiler/codegen_creation_system/codegen_creation/spell_codegen_creation_cache.py:246,282,437`),
  and every strategy family's OWNER step reads `spell_N._owner_creations`
  (`.../strategies/generalized/compilers/generalized_manifest_no_overrides_compiler.py:524-566`).
- The existence->store routing itself:
  `.../codegen_planner/data/spell_generalized_codegen_lane_plan.py:2211-2223`
  (`_creation_target_for_existence`): `unique_per_conduit`->CALLER, `many`->CALLER,
  `unique_per_spell_space`->SPELLSPACE, **everything else (unique, cluster, lineage)->OWNER**.

Consequence (the bug): because the store is the single binding-owner store, **borrowing collapses**.
When a second root links/borrows a `unique_per_conduit_lineage` spell, it resolves through the
contract to the owner's `_owner_creations` and reads the **owner's** instance, instead of
instantiating its own in its own lineage. So "per lineage" is not realized: there is effectively one
instance, shared by anyone who can see the spell. The user identified this gap directly; this epic
fixes it.

## MRP Alignment (Most Reasonable Product)
Existence is a public, load-bearing DI contract. A core that ships an existence whose runtime
behavior contradicts its name is a trap, not an MRP: downstream systems (mutation, cluster sharing,
future PGO speculation) cannot build correct behavior on an undefined instance-identity model. This
epic makes the lineage scope mean what it says, with a uniform, evidence-grounded model that also
clarifies `unique` (frame) and prepares the same treatment for cluster. It is correctness-first and
additive in spirit (the `unique` and `unique_per_conduit` paths stay as-is).

## Ticket Contract
- ENTRY_GATE: this epic is routed on the board; the story set below is defined; the open transfer
  decision (Decision Log D1) is raised to the user before any transfer-touching story starts.
- EXECUTION_BOUNDARY: `unique_per_conduit_lineage` semantics only. The store-source mechanism
  (`root_creations`), the four door resolutions, borrow/dep-closure for lineage, transfer
  redefinition for lineage, and lineage cleanup/lifecycle. EXCLUDES cluster (separate epic; needs a
  membership rule), the PGO optimizer, and any change to `unique`/`unique_per_conduit`/`many`/
  `unique_per_spell_space` semantics.
- DEPENDENCIES: the meld doors (`conduit_meld`, `spellspace_meld`), the codegen-creation strategy
  families (generalized/solo/many_only x overrides/no-overrides), the door-compiler templates,
  hydration + finalize-context steps, `transfer_of_ownership`, `ConduitWard` link/contract path,
  `ConduitCreations`/`Creations`. Architecture anchors: `src_architecture.md`, `src_components.md`.
- EXIT_GATE: all required stories accepted; the differential + concurrency suite (Story H) green on
  the user's 3.14t target; the user confirms acceptance; board/closure sync complete.
- FAILURE_ESCALATION: raise DECISION_REQUEST for the transfer instance-fate question (D1) and the
  `_owner_creations`-narrowing confirmation (D2) before touching those surfaces; CONFLICT if any
  change would alter observable `unique`/`unique_per_conduit` behavior; BLOCKER if the codegen
  shape-cache cannot keep shape-sharing valid once `root_creations` is threaded.

## Goals (Outcomes)
- `unique_per_conduit_lineage` resolves to **one instance per lineage**, stored at the lineage
  **root**, shared by the root + all its lesser conduits + their spellspaces.
- A different root that borrows the spell **instantiates its own** instance in its own lineage-root
  store (borrow conveys the recipe/binding, not the owner's instance).
- A single, uniform store-selection rule across all four door types (root conduit, lesser conduit,
  spellspace, borrower-via-link) with **zero added meld-time cost** (per-door constant store).
- `transfer_of_ownership` redefined coherently against per-lineage instances.
- `unique` clarified as the only frame-global singleton; the model documented in the system docs.

## Non-Goals (Explicit Exclusions)
- `unique_per_conduit_cluster` redesign (separate epic; requires a conduit-cluster-membership rule
  because cluster scope is not unambiguous the way lineage is). This epic only ensures the mechanism
  it builds (`root_creations` store source + OWNER routing split) is shaped so cluster can reuse it.
- The adaptive PGO DI optimizer (separate; `unique`-only first). This epic is a prerequisite for any
  future lineage speculation but does not implement it.
- Any change to `unique`, `unique_per_conduit`, `many`, or `unique_per_spell_space` semantics.

## Scope Boundaries
- In scope: lineage store-source + routing; the four door resolutions; borrow/link dep-closure for
  lineage; transfer redefinition for lineage; lineage cleanup/lifecycle; docs + tests.
- Out of scope: cluster, optimizer, unrelated existences, unrelated refactors.

## State Transition Event
- from_state: draft
- to_state: ready
- transition_reason: current-state fully traced with evidence; design (one-store rule + four-door
  resolution + transfer question) converged with the user; story decomposition defined. The only
  blocker to `in_progress` is the user's call on Decision Log D1 (transfer) and D2 (`_owner_creations`
  narrowing) before the stories that touch those surfaces.

## Success Metrics
- Two independent roots each melding the same `unique_per_conduit_lineage` binding hold **two
  distinct instances** (was one).
- Root + lessers + spellspaces within one lineage share **one** instance.
- A borrower-via-link gets its **own** instance and its dep subtree built in its own scope.
- No regression in `unique`/`unique_per_conduit`/`many`/`unique_per_spell_space` behavior.
- No measurable meld-time regression on the warm path (per-door-constant store; verify with the
  contention harness).

## Requirements (Functional + Non-Functional)
THE ONE-STORE RULE (functional core):
- A `unique_per_conduit_lineage` step's store is **the resolving door's lineage-root creations**,
  keyed by `spell_id`. Resolved per door (not per meld), bound once at door construction.

FOUR-DOOR RESOLUTION (how each door obtains the lineage-root store):
- Root conduit door: root == self, so lineage-root store = its own `_creations` (== `caller_creations`).
- Lesser conduit door: a lesser carries the root id FLAT
  (`src/melder/aether/conduit/conduit.py:1576-1577`: `lesser._root_conduit_id = root id`,
  `lesser._meld._resolution_conduit_id = root id`); root conduits live in `frame._conduits`
  (lookup pattern at `conduit.py:308-309`). So lineage-root store =
  `frame._conduits[_root_conduit_id]._creations` (O(1), no parent walk). Preferred: the root hands
  its creations to the lesser's door at create/wire time (it already hands down the root id).
- Spellspace door (`SpellSpaceMeld`): already constructed with `_owner_conduit_creations` +
  `_owner_conduit_id` (`src/melder/aether/conduit/meld/spellspace_meld.py:34-80`). Add the owning
  conduit's lineage-root creations the same way (passed at spellspace construction; the owning
  conduit knows its root).
- Borrower-via-link door: resolves the spell (via the contract) but uses **its own** lineage-root
  store, so the borrower's lineage instantiates its own. Store chosen by the resolving door's root,
  NEVER by the spell's owner.

NON-FUNCTIONAL:
- Zero added warm-path cost: lineage-root store is a per-door constant (like `caller_creations`),
  bound once; rebind on `upgrade_to_normal` alongside `_resolution_conduit_id` (already rewired
  there). The fast-door inline cache must handle lineage without per-hit recomputation.
- Thread-safety (3.14t nogil): reuse the existing `ConduitCreations`/`Creations` lock discipline for
  per-lineage stores; do not invent new shared state. Concurrent first-meld of a lineage spell in a
  lineage must double-check under the creations lock (same pattern the emitted body already uses).
- Codegen shape-sharing must stay valid: `root_creations` must be threaded as a runtime PARAM, not
  baked identity, so the process-wide sha256 shape cache keeps sharing executors across same-shape
  spells.

UNIFYING MODEL (document this):
- All `unique_per_*` are "singleton keyed by a scope"; what differs is the store source:
  `unique`->frame (resolver-independent, bakeable), `unique_per_conduit`->caller (resolver conduit),
  `unique_per_conduit_lineage`->resolver's lineage root, `unique_per_spell_space`->resolver
  spellspace, `unique_per_conduit_cluster`->resolver's cluster (later). The bug was lineage/cluster
  being implemented as `unique` (owner-fixed) instead of resolver-relative.

## Constraints / Assumptions
- Additive to `unique`/`unique_per_conduit`; do not change their behavior.
- The control plane is ALREADY lineage-root-scoped for validation/gating: meld uses
  `_resolution_conduit_id` (= root id) for change-control + resolution-state gating
  (`src/melder/aether/conduit/meld/meld.py:172,613,708,776,946`). We are aligning STORAGE to the
  root-scoping the control plane already uses; no new identity system is needed.
- Borrow conveys the binding (recipe) + its dependency closure; the borrower's root constructs.
- Assumption (to confirm in Story A): `_owner_creations` for lineage becomes vestigial and narrows
  to `unique` only (frame store). See Decision Log D2.

## Dependencies / External References
- `src_architecture.md` (existence/scoping model; conduit lifecycle), `src_components.md` (Meld
  Resolution Runtime; Creations; Conduit Runtime; ConduitWard).
- Optimizer epic linkage: `codex/context_compass/artifacts/2026-06-13_adaptive_pgo_di_optimizer_design.md`
  and `tickets/tasks/2026-06-13_executor_construction_lane_trim_task.md` (lineage speculation is
  gated on this epic landing).

## Milestones (Track Progress)
- [ ] M1: `root_creations` store source threaded + ONE family end-to-end (generalized no-overrides)
      routing lineage to the resolver-root store; a two-root differential test passes. (Stories A, B, H-partial)
- [ ] M2: routing split propagated across ALL codegen families + both runtime non-codegen doors. (Stories C, D)
- [ ] M3: borrow/link dependency-closure correct for lineage. (Story E)
- [ ] M4: `transfer_of_ownership` redefined per the resolved D1 decision. (Story F)
- [ ] M5: cleanup/lifecycle verified + full differential & concurrency suite green; docs updated. (Stories G, H)

## Stories (Required to Complete)
- [ ] Story: STORY-lineage-A - Introduce the lineage-root store source + per-door binding. Bind
      `root_creations` on each door (root/lesser/spellspace) once at construction; lesser via flat
      root id (`frame._conduits[root_id]._creations` or root-passes-down); spellspace via owning
      conduit's root; rebind on `upgrade_to_normal`. Decide `_owner_creations` narrowing (D2).
- [ ] Story: STORY-lineage-B - Split OWNER routing into OWNER_FRAME (`unique`, keep baking
      `_owner_creations`) vs OWNER_ROOT (`lineage`, use passed `root_creations`) in the generalized
      no-overrides emitter + door-compiler template + hydration/finalize for that family; thread the
      `root_creations` param. Keep shape-cache sharing valid (param, not baked identity).
- [ ] Story: STORY-lineage-C - Propagate the OWNER_FRAME/OWNER_ROOT split across the remaining
      families: generalized overrides, solo (no/overrides), many_only (no/overrides), plus their
      finalize-context steps and the door-compiler templates. (~70 `_owner_creations` sites; mechanical
      but wide.)
- [ ] Story: STORY-lineage-D - Update the two runtime non-codegen doors
      (`conduit_meld`/`spellspace_meld` `meld_existing_spell` + `describe_live_creation_status`) to
      route `unique_per_conduit_lineage` to the resolver-root store and report the correct scope kind.
- [ ] Story: STORY-lineage-E - Borrow/link dependency-closure for lineage: a borrowed lineage spell
      must bring its lineage dep closure (via `link_dependencies`) so the borrower's root can build the
      whole subtree in its own scope; resolve deps in the borrower's scope.
- [ ] Story: STORY-lineage-F - Redefine `transfer_of_ownership` for per-lineage instances per the D1
      decision: move the recipe (binding) + owner-of-definition; per-lineage instances stay or
      invalidate per D1. Update `execute()`/`_move_creations`/`_teardown_creations`/preflight/rollback
      (`transfer_of_ownership.py:307-388,1400,1436`).
- [ ] Story: STORY-lineage-G - Cleanup/lifecycle: verify per-lineage instances dispose with their
      root's creations (cleanup follows location); no leaks across lineages; correct teardown ordering.
- [ ] Story: STORY-lineage-H - Differential + concurrency test suite: two-root isolation; lesser +
      spellspace share the root instance; borrower makes its own + builds its subtree; transfer
      behavior matches D1; nogil thread-safety (concurrent first-meld across a lineage). Update
      `src_architecture.md`/`src_components.md` existence model.
- [ ] Story: STORY-lineage-I (DEFERRED/parked) - Cluster redesign reusing this mechanism, gated on a
      conduit-cluster-membership rule. Out of this epic's scope; tracked for the follow-on cluster epic.

## Tasks (Cross-Cutting or Epic-Level)
- [ ] Task: Resolve Decision Log D1 (transfer instance fate) with the user before Story F.
- [ ] Task: Resolve Decision Log D2 (`_owner_creations` narrows to `unique`) with the user in Story A.
- [ ] Task: Patch-framework artifacts + owner signoff before any source edit (system-impacting:
      touches meld doors + codegen emit across families + transfer).
- [ ] Task: Verify Ticket Microcycle enforcement across active tickets/stories/tasks.

## Acceptance Criteria (Epic Done)
- Two roots melding one lineage binding hold two distinct instances; one lineage shares one.
- Borrow-via-link yields the borrower's own instance + subtree.
- `transfer_of_ownership` behaves per D1 with passing tests + rollback.
- No behavior change to `unique`/`unique_per_conduit`/`many`/`unique_per_spell_space`.
- No warm-path meld regression (contention harness).
- Differential + concurrency suite green on 3.14t; system docs updated; user accepts.

## Risks / Mitigations
- RISK (large blast radius, ~70 `_owner_creations` sites across all codegen families): mechanical but
  error-prone. MITIGATION: one family end-to-end first (M1) behind a differential test, then propagate;
  do families as a consistent codemod-like pattern, reviewed.
- RISK (warm-path regression): adding a store source could tax the hot path. MITIGATION: bind
  `root_creations` as a per-door constant (no per-meld recompute); verify with
  `profile_scope_cycle_contention.py` before/after.
- RISK (codegen shape-cache invalidation): if `root_creations` is baked as identity, shape-sharing
  breaks (one executor per spell, cache blowup). MITIGATION: thread it strictly as a runtime PARAM;
  the OWNER_FRAME vs OWNER_ROOT split is by existence (shape-stable), not by identity.
- RISK (thread-safety, nogil): concurrent first-meld of a lineage spell across a lineage. MITIGATION:
  reuse the existing double-checked creations-lock pattern in the emitted body; do not add new shared
  state.
- RISK (transfer correctness + rollback): redefining transfer is subtle. MITIGATION: resolve D1
  first; keep the minimal-critical-section + rollback structure already in `execute()`.

## Applicable Anti-Patterns
- [ ] No epic-state transition without story-level evidence.
- [ ] No closure while required stories are incomplete or unaccepted.
- [ ] No program claims without source evidence from story/task notes.
- [ ] No change to `unique`/`unique_per_conduit` observable behavior (CONFLICT if proposed).
- [ ] No baked identity in the shared executors (must stay shape-shareable).

## Validation / Test Approach
- Differential: per-lineage isolation, intra-lineage sharing, borrow-makes-own, dep-closure subtree,
  transfer per D1.
- Concurrency: nogil multi-thread first-meld across a lineage; two lineages in parallel.
- Performance: contention harness warm-path delta (no regression).
- Family coverage: each codegen family (generalized/solo/many_only x overrides/no-overrides) exercised
  with a lineage step.
- Truthful reporting: agents do not claim suite/coverage runs; the user runs on 3.14t.

## Rollout / Adoption Plan
- Internal correctness fix; no public API shape change (existence enum unchanged; behavior corrected).
- Land family-by-family behind tests; keep `unique`/`unique_per_conduit` untouched throughout.
- Update `src_architecture.md`/`src_components.md` existence/scoping model on completion.

## Open Questions
- D1 (transfer): on a lineage binding ownership transfer, do already-live per-lineage instances STAY
  (keyed by their roots; recipe-ownership is orthogonal) or INVALIDATE/dispose (recipe changed under
  them)? Lean: STAY. USER DECISION REQUIRED before Story F.
- D2: confirm `_owner_creations` narrows to `unique` (frame) only; lineage moves to `root_creations`;
  cluster to a cluster store later. Lean: yes. Confirm in Story A.
- Q3: does a lesser's door cache the root creations reference, or look it up via `frame._conduits`
  each rebind? (Perf/coupling tradeoff; resolve in Story A.)

## Decision Log
- 2026-06-13 DECISION (with user): `unique_per_conduit_lineage` becomes resolver-root-scoped (one
  instance per lineage, stored at the lineage root). Name stays `unique_per_conduit_lineage`
  ("unique_per_root" was shorthand for store location only).
- 2026-06-13 DECISION (with user): borrow conveys the recipe (binding), not the owner's instance; the
  borrower's root instantiates its own ("like `unique_per_conduit` but root creations").
- 2026-06-13 OPEN (D1): transfer instance fate — pending user.
- 2026-06-13 OPEN (D2): `_owner_creations` narrowing — pending confirm.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: false
- ARTIFACT_PATHS:
  - (none yet; design captured inline in this epic)
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: on epic closure, promote the existence model into `src_architecture.md`.

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: true
- CONTEXT_IDS:
  - CTX-2026-06-13-lineage-resolver-root
- CONTEXT_TOPICS:
  - unique_per_conduit_lineage resolver-root semantics
  - _owner_creations blast radius across codegen families
  - transfer_of_ownership per-lineage instance fate (D1)
- IF_UNKNOWN: ask user before implementation

## Notes
- DATETIME: 2026-06-13T23:18:00Z
  TYPE: FACT
  CLAIM: Today `unique_per_conduit_lineage` == `unique`: both doors route unique/cluster/lineage to
    `spell._owner_creations` (owner-fixed), and `_owner_creations` is the owning conduit's creations
    stamped at conjure. The store is baked into emitted executors at compile/hydration time, so
    borrowing collapses to the owner's instance. The lineage scope is not realized.
  EVIDENCE:
  - src/melder/aether/conduit/meld/conduit_meld.py:519-533
  - src/melder/aether/conduit/meld/conduit_meld.py:707-725
  - src/melder/aether/spellbook/spell.py:1116
  - src/melder/aether/spellbook/spellbook.py:3141
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/codegen_creation/spell_codegen_creation_cache.py:246-282
  IMPACT: this is the root cause the epic fixes; it is correctness, not optimization.
  NEXT: Story A introduces the resolver-root store source.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-06-13T23:18:00Z
  TYPE: DECISION
  CLAIM: The one-store rule: a lineage step's store = the resolving door's lineage-root creations,
    bound once per door (a per-door CONSTANT), uniform across root/lesser/spellspace/borrower doors.
    The control plane is already lineage-root-scoped (`_resolution_conduit_id`); we align storage to it.
  EVIDENCE:
  - src/melder/aether/conduit/conduit.py:1576-1577
  - src/melder/aether/conduit/conduit.py:308-309
  - src/melder/aether/conduit/meld/spellspace_meld.py:34-80
  - src/melder/aether/conduit/meld/meld.py:172
  IMPACT: makes a wide change tractable with zero added warm-path cost (constant store, not per-meld).
  NEXT: Story A binds `root_creations` per door; Story B threads it through one family.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-06-13T23:18:00Z
  TYPE: DECISION_REQUEST
  CLAIM: D1 — on lineage binding ownership transfer, do live per-lineage instances STAY or INVALIDATE?
    Lean STAY (keyed by root; recipe-ownership orthogonal). Blocks Story F.
  EVIDENCE:
  - src/melder/aether/conduit/conduit_ward/transfer/transfer_of_ownership.py:307-388
  - src/melder/aether/conduit/conduit_ward/transfer/transfer_of_ownership.py:1400
  IMPACT: defines transfer semantics under the new model; load-bearing.
  NEXT: get user decision before Story F.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-06-14T12:23:05Z
  TYPE: PLAN
  CLAIM: IN-PROGRESS implementation state (paused mid-build, NOT yet test-green).
    LANDED + VERIFIED GREEN (suite tests/unit/melder/aether: 3607 pass, only 3
    pre-existing nexus-frame-manager failures remain, not ours):
    - Sub-move 1 (additive `root_creations` threading, behavior-inert): ConduitMeld
      carries `_root_creations` (slot/param/binding/cleanup); conduit.py binds it
      at door construction (root->own creations, lesser->root's), propagates on
      lineage-controller rebind, resets on upgrade; CreationContext.execute /
      execute_no_hooks accept + forward `root_creations`; door-compiler outer-door
      signatures accept `root_creations=None`; 5 conduit_meld call sites pass it.
      Test doubles updated in 4 test files (the two _CreationContextStub classes +
      standalone executor stubs/lambdas).
    LANDED but NOT yet test-validated (the lineage flip; do not run suite expecting
    green until the families below are done):
    - Route resolver `_resolve_route_key_for_spell` (spell_codegen_creation_cache.py):
      `unique_per_conduit_lineage` -> NEW route key "lineage" (unique/cluster stay
      "shared").
    - Door-compiler (creation_runtime_door_compiler.py): added a "lineage" route to
      BOTH `_build_no_overrides_lines` AND `_build_with_overrides_lines` (each covers
      hooks + no-hooks via `return_created`); both read/write `root_creations` under
      `root_creations._lock` (mirror of the unique_per_conduit / shared shapes).
      Parameterized `_build_no_overrides_create_lines` with `owner_creations_expr`
      (passes "root_creations" for the lineage route).
    - Solo no-overrides inner (solo_no_overrides_codegen_creation_compiler.py):
      `has_prebound_owner_creations` forced False for lineage so the inner uses the
      `owner_creations` param (= root_creations) instead of the baked owner store.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/codegen_creation/spell_codegen_creation_cache.py (_resolve_route_key_for_spell)
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/shared_assets/creation_runtime_door_compiler.py (lineage routes)
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/solo/compilers/solo_no_overrides_codegen_creation_compiler.py:29-39
  IMPACT: solo / no-hooks / no-overrides lineage path is internally consistent
    (reads+writes root_creations end-to-end). NOT yet a green suite.
  NEXT (remaining for a coherent green lineage lane):
    (a) Generalized inners — BOTH generalized_manifest_no_overrides_compiler.py AND
        generalized_no_overrides_codegen_creation_compiler.py + the overrides twins:
        in the OWNER per-step routing, for a step whose existence is
        unique_per_conduit_lineage emit `creations_N = owner_creations` (the
        root_creations param) instead of `spell_N._owner_creations`.
    (b) many_only inners (same OWNER per-step change).
    (c) Solo + generalized + many OVERRIDES inners: force the param path for lineage
        (mirror the solo no-overrides has_prebound change); thread root_creations
        into `_execute_with_overrides` if/where the override runtime registers.
    (d) Hydrators (solo/generalized/many finalize-context steps) — confirm they do
        not pin the owner binding for lineage.
    (e) BORROW PATH (separate surface, required for the visible two-lineage behavior
        + the two-root differential test): contract conveys the recipe so a borrower
        root instantiates its own in its own root_creations (Story E). The store
        routing alone gives intra-lineage sharing (lesser->root instance); the
        cross-root case needs link/borrow.
    KNOWN EDGE (defer): a lineage DEP under a NON-lineage root currently resolves via
    the route's owner_creations param, which for a non-lineage root is the root
    spell's _owner_creations, not the dep's lineage-root store. Rare/murky (frame
    singleton depending on a per-lineage spell); revisit when threading root_creations
    as a separate inner param if needed.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- TYPE: FACT | AGENT: compiler_strategy_0 | 2026-06-14
  TITLE: KEYSTONE FOUND — the lineage lane was inert; route_family masked it. Now activated.
  BODY:
    Two corrections to the prior "solo lineage green" claim:
    (1) The single-root lineage test passes TRIVIALLY. For one root, the lineage
        spell's owner IS the root, so spell._owner_creations == root._creations ==
        root_creations. The old "shared" (owner) route and the new "lineage"
        (root_creations) route are PHYSICALLY THE SAME STORE for a single root, so
        the test cannot distinguish them. It only proves no-crash + intra-lineage
        sharing. The REAL differentiator (root vs owner) needs two roots where the
        owner != the resolving root — i.e. the BORROW path (Story E). Build borrow
        before claiming the semantic is validated.
    (2) The lane was INERT before today. `route_family` is set in
        `spell_artifact_processor.py` and bucketed lineage into the catch-all
        `else -> "shared"`. EVERY build path keys its route off route_family
        (solo_manifest, generalized_manifest, many_only_manifest, the three
        finalize/setup steps), EXCEPT the cache-package codec
        (`spell_codegen_creation_cache._resolve_route_key_for_spell`, which I'd
        already set to "lineage"). With caching OFF (the test config) the codec is
        unused, so lineage was STILL routed "shared" in the runtime door — the
        door-compiler "lineage" branch was dead code.
  ACTION (keystone activation landed 2026-06-14, no-overrides both build paths):
    (a) `spell_artifact_processor.py`: `elif existence is unique_per_conduit_lineage:
        route_family = "lineage"` (before the else). Lineage-only; unique/cluster
        stay "shared"; non-lineage paths untouched (gauntlet must stay green).
    (b) `creation_runtime_door_compiler.py`: added 4 lineage templates
        (overrides hooks/instance + no-overrides hooks/instance, all
        resolve_route_key="lineage", non-fast) and REGISTERED "lineage" in all 4
        dispatch maps (_OVERRIDES_ONLY_INSTANCE/_HOOKS_BY_ROUTE and
        _NO_OVERRIDES_ONLY_INSTANCE/_HOOKS_BY_ROUTE_AND_FAST, both fast False/True).
        Without this, route_family="lineage" would hard-raise "Unsupported route key".
    (c) Accept "lineage" in the 4 allow-list gates that would otherwise raise:
        generalized_manifest._resolve_route_key_from_model,
        generalized_finalize._resolve_route_key (REQUIRED — lineage-with-deps),
        many_only_manifest + many_only_finalize (defensive; a many root is never
        lineage). solo_manifest/solo_setup pass route_family through (no gate).
    (d) LIVE generalized inner (`generalized_no_overrides_codegen_creation_compiler
        ._append_step_creations_target_source`): added `is_lineage` param; OWNER step
        emits `creations_N = owner_creations` for lineage (the root_creations param)
        instead of preferring baked `spell_N._owner_creations`. Call site passes
        `is_lineage=plan_step.existence is unique_per_conduit_lineage`. Now matches the
        manifest compiler so live==manifest holds for no-overrides.
  REMAINING (unchanged from prior note + refined):
    - OVERRIDES inner store gap: door-compiler "lineage" override branch reuse-reads
      root_creations correctly, but its inner `_execute_with_overrides(...)` (and the
      live finalize `execute_with_overrides`, which bakes root_spell._owner_creations
      and has NO root_creations param) still constructs/stores against the owner. For
      a single root this coincides; under multiple roots the inner would double-store
      (owner + root). Thread root_creations through the overrides runtime — do this
      WITH the borrow work so it's testable.
    - BORROW PATH (Story E) — the only way to write a non-trivial differential test.
    - Transfer of ownership (Story F) LAST; depends on D1.
  VALIDATION ASKED OF USER: re-run the lineage test (now exercises the real "lineage"
    templates, not a trivial alias), the gauntlet (no lineage -> must stay green), and
    the full tests/unit/melder/aether suite (regression; lineage change is contained).
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- TYPE: MEASURE | AGENT: compiler_strategy_0 | 2026-06-14
  TITLE: Lineage migration functionally COMPLETE + PROVEN (borrow differential green). Perf regression to chase.
  BODY:
    Cross-root isolation now proven by a real differential, not the trivial
    single-root smoke. `tests/experimentation/test_lineage_borrow_isolation.py`
    (owner owns a lineage service, borrower borrows it over a link contract):
      - unique control: owner.meld(svc) IS borrower's borrowed svc (shared; same frame).
      - lineage: owner's instance IS NOT borrower's (each root its own). PASS.
      - contract-baked override on borrowed lineage svc: isolated + applied. PASS.
      - meld-time spell_override on borrowed lineage svc: cached in BORROWER root,
        owner store not polluted. PASS (this was the override-lane gap; now closed).
    Why borrow "just works": each conduit's meld threads its own root_creations into
    the door, so intra-lineage sharing AND cross-root isolation both fall out of the
    single routing rule (door reads root_creations, not _owner_creations).
  OVERRIDE LANE threaded this pass (meld-time spell_override now stores in
    root_creations for lineage; non-lineage unchanged, all additive root_creations=None):
      - door compiler lineage override branch -> passes root_creations as 4th arg to
        _execute_with_overrides (both call sites).
      - generalized finalize execute_with_overrides + generalized_manifest_overrides_runtime
        execute_with_overrides: accept root_creations, use it as owner_creations for lineage.
      - generalized override emitter `_append_overrides_shape_owner_creations_source`:
        is_lineage -> `creations_N = owner_creations` (the param).
      - solo override `unique_per_conduit_lineage` branch: accepts root_creations, stores there.
      - cache codec (`spell_codegen_creation_cache`): `_lazy_execute_with_overrides` +
        `_build_missing_overrides_executor` accept root_creations (conditional pass so
        non-lineage arity is exact). UNTESTED: caching is OFF in the suite; needs a
        caching-on run to validate the cache-load lineage+override path.
  GREEN: borrow file (4) + root-scoped (2) + gauntlet (1) + unit aether (3607; only the
    3 pre-existing _FakeFrame nexus doubles fail, unrelated).
  REGRESSION TO CHASE (raised by user, not yet diagnosed): melder gauntlet wall went
    ~670ms -> ~820ms (+~22%). Gauntlet uses NO lineage spells, so prime suspect is the
    UNIVERSAL Sub-move-1 threading (every meld now reads self._root_creations + passes
    one extra arg into the door; the override runtimes gained a None-check). Next: get
    the gauntlet's conjure-vs-meld breakdown + contention micro warm-door ns, then decide
    whether to make root_creations threading conditional/cheaper on the non-lineage fast
    door (must preserve borrow semantics: root_creations is resolver-relative, cannot be
    baked per-door). Do NOT guess — measure first.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- TYPE: DECISION | AGENT: compiler_strategy_0 | 2026-06-14
  TITLE: Perf redesign — move the lineage-root pointer ONTO Creations; drop the universal param thread.
  BODY:
    Sub-move-1 threaded `root_creations` as a second arg into EVERY warm meld
    (conduit_meld 264/356/dynamic, creation_context execute/execute_no_hooks, all
    door signatures). Gauntlet (no lineage) regressed ~+29% on the threaded-phase
    median (0.482ms -> ~0.62ms; construction + bootstrap unchanged) because every
    non-lineage door paid a 2-arg call for a value it ignores. User proposed the
    better design: the resolving conduit's `caller_creations` is already passed, so
    carry the lineage-root reference ON it and let only the lineage door read it.
  CHANGE (this pass):
    - `Creations` gains `_root_creations` (slot, defaults to `self`). Wired:
      lesser conduit -> root's `_root_creations`; spellspace -> owner conduit's
      `_root_creations`; `upgrade_to_normal` -> self; lineage-gate propagation ->
      self's root. Survives pooling (`reset_for_pool`/`clear_all` only clear the
      entries dict; conduit/spellspace pools are per-root so the pointer stays valid).
    - Door compiler: signatures reverted to 1-arg `(caller_creations)` /
      `(caller_creations, overrides)`; the lineage no-overrides + both overrides
      sub-branches now prepend `root_creations = caller_creations._root_creations`
      and use it exactly as before (still passes it to `_execute_with_overrides`).
    - Reverted ALL Sub-move-1 param threading: conduit_meld call sites + the
      `ConduitMeld._root_creations` slot/param/cleanup; creation_context
      execute/execute_no_hooks; the conduit.py/`upgrade_to_normal` meld bindings.
    - Override runtimes (finalize/manifest/solo/cache) KEEP their `root_creations`
      param unchanged — the door still passes it, now sourced from caller_creations.
  BONUS: spellspace-resolved lineage now works for free (SpellSpaceMeld was never
    threaded in Sub-move 1, so old design silently mis-stored; door self-sourcing
    fixes it). Non-lineage warm path is byte-for-byte the old 1-arg fast door.
  EXPECT: gauntlet threaded-phase median back to ~0.48ms; lineage tests stay green
    (root-scoped + borrow isolation, 6 tests); unit aether green (3 pre-existing
    nexus fails). Note: Sub-move-1 test doubles still carry an unused
    `root_creations=None` param — harmless (production now calls with fewer args).
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- TYPE: MEASURE | AGENT: compiler_strategy_0 | 2026-06-14
  TITLE: Perf FULLY recovered (at/slightly under baseline) after the Creations._root_creations redesign.
  BODY:
    Gauntlet medians (the reliable metric; cv ~177%):
      - threaded-phase median: baseline 0.482ms -> regressed 0.62ms -> NOW 0.472ms.
      - total median:          baseline 0.614ms -> regressed ~0.75ms -> NOW 0.591ms.
      - min total 0.480ms; hot_objects/s_min 1,000,930 (>1M/s, up from ~971k baseline).
    So moving the lineage-root pointer onto Creations (read only inside the lineage
    door) returned the non-lineage warm path to byte-for-byte the 1-arg baseline; the
    only added work is one attr-set at conduit/spellspace construction (construction
    timings unchanged: outer/request create still 0.001-0.002ms). Net cost of the whole
    lineage migration on the hot path: effectively zero (within noise).
    Validation: gauntlet green; 6 lineage tests green (root+lesser+borrow+overrides,
    no-overrides + meld-time + contract overrides); tests/unit/melder/aether 3607 passed
    (only the 3 pre-existing _FakeFrame nexus doubles fail, unrelated).
    upgrade_to_normal verified: line 1695 sets self._creations._root_creations=self
    BEFORE the lesser rebind at line 1701 (which re-points lessers to the new root) -
    correct order. Conduit pools are per-root and reset_for_pool/clear_all never touch
    _root_creations, so pooled lessers keep a valid root pointer across reuse.
  REMAINING (parked, unchanged): cluster (separate epic), transfer-of-ownership
    (Story F, gated on D1), and a belt-and-suspenders upgrade_to_normal+lineage test.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- TYPE: DECISION | AGENT: compiler_strategy_0 | 2026-06-14
  TITLE: D1 RESOLVED = STAY. Transfer of ownership for lineage: move the binding, ignore the creations.
  BODY:
    User confirmed: "if you can have one per root, we just transfer the spell and
    ignore the creations." For unique_per_conduit_lineage, ownership transfer flips
    ONLY the canonical binding (registry + spellbook); every per-root instance stays
    where it was resolved -- the source keeps its instance, the target builds its own
    on first resolve, borrowers keep theirs.
  WHY (from investigation of conduit_ward/transfer/transfer_of_ownership.py):
    - Only ONE step in execute() touches instances: the creations step
      (_move_creations / _teardown_creations), which operates on
      source_conduit._creations.extract_spell_creations(spell_id). For unique/cluster
      that's correct (owner-stored). For lineage the source's instance sits in
      source._creations only because the source is its own lineage root -- it's
      resolver-relative, not owner-bound -- so moving/tearing it would VIOLATE
      one-per-root (yank source's root instance to target, or destroy it).
    - The borrower step (_repoint_borrowers / _unshare_everywhere) and dirty-marking
      are contract/spell-state only; they never tear down instances. So borrowers'
      lineage instances are untouched regardless. No change needed there.
  CHANGE (landed): transfer_of_ownership.execute() now skips the creations
    move/teardown for `spell_obj.existence is Existence.unique_per_conduit_lineage`
    (added the Existence import). unique/cluster paths unchanged. Cluster keeps the
    owner-bound move until its own migration.
  TEST: test_execute_lineage_skips_creations_and_keeps_source_instance (unit, in
    test_transfer_of_ownership.py) -- even with move_creations=True, source keeps
    "obj-1", target gets none, ownership flips to TARGET. Mirrors/contrasts the
    existing test_execute_move_creations_transfers_creations (non-lineage moves).
  upgrade_to_normal + lineage test: GREEN (lesser shares root store pre-upgrade;
    after promotion its creations are their own lineage root).
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Closure Confirmation
- [ ] Work walkthrough shared with user
- [ ] Acceptance criteria confirmed by user
- [ ] Applicable anti-pattern checks are clear or escalated with evidence.

## Noting Behavior
- Note focus: program-level direction, cross-story tradeoffs, tranche order.
- Add notes when sequencing, scope, or the D1/D2 decisions change.
- Reference story/task evidence; keep notes append-only; UNKNOWN-first.

## Context / Handoff Summary
`unique_per_conduit_lineage` (and cluster) are currently implemented as `unique` — one owner-fixed
instance, store baked at compile time — so borrowing collapses and the lineage scope is not realized.
This epic redefines lineage as RESOLVER-ROOT-SCOPED: one instance per lineage, stored at the lineage
root, shared by root + lessers + spellspaces; a borrower instantiates its own in its own root. The
mechanism is one rule — the lineage step's store is the resolving door's lineage-root creations,
bound once per door as a constant (zero warm-path cost) — applied across four door types and threaded
as a runtime `root_creations` param through every codegen family (the ~70 `_owner_creations` sites).
Cleanup and dependency-resolution fall out of the resolver-relative shape; validation is already
root-scoped. The open decision is D1 (transfer: do live per-lineage instances stay or invalidate on
binding transfer; lean STAY). Cluster reuses this mechanism later behind a membership rule (separate
epic). This epic is also the prerequisite that makes any future lineage PGO speculation expressible
(the optimizer stays `unique`-only until this lands). Stories A->H decompose the work; M1 proves one
family end-to-end behind a two-root differential test before propagating.
