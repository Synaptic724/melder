# DevOps Control Plane & Transaction Mediator — System Map

- Author: mediator_builder_0 (cowork)
- Created: 2026-06-13
- Ticket: tickets/tasks/2026-06-13_understand_devops_and_mediator_system_task.md
- Scope: `src/melder/aether/aetheric_frame/dev_ops/**` (37 files, ~15.5k LOC).
  Mediator/transaction admission core read line-by-line; the validity,
  risk, incident, and information subsystems mapped from the C4/C3 docs +
  object graph + source spot-checks.
- Evidence basis: source reads listed in the final section; cross-checked
  against `system_docs/src_architecture.md`, `src_components.md`, and
  `readable_src_graph.json` (graph tail is truncated/invalid JSON — verified
  against source).

---

## 1. Orientation

The DevOps system is the **frame-local control plane**. Every `AethericFrame`
owns one `DevOpsManager`, which is the ownership root for the operational
managers. It is *not* on the meld hot path; it is the governance/health layer
that the hot path consults through narrow gates.

It splits into **two planes plus a shared registry**:

1. **Transaction / admission plane** (the "mediator system"): serializes
   structural mutations — bind, link, cluster_link, transfer_ownership,
   mutation — so non-overlapping work runs in parallel and only true scope
   overlap waits. Lives under `change_control_manager/`.
2. **Validity / dirty-root plane**: tracks per-lineage and per-conduit
   validity, marks dependent roots dirty after change, and gates meld
   execution until revalidation. Lives in `spell_system_states/` +
   `risk_manager/` + the dirty-root half of `change_control_manager.py`.
3. **DevopsInformationRegistry** (shared mirror): frame-local mirror of
   identities, topology relations (spellbook→conduits, provider→borrowers,
   cluster→conduits), live transactions, and "fact-record" freshness
   baselines. Caller-paid information strategies read it; transactions write
   it at commit.

Ownership tree:

```
AethericFrame
├── SpellSystemStates                         (validity registry; hot path reads it)
├── DevopsInformationRegistry                 (shared topology/transaction mirror)
└── DevOpsManager                             (ownership root / facade)
    ├── IncidentManager                       (descriptive incident records)
    ├── RiskManager                           (per-conduit risk -> spellbook gating)
    ├── CreationGateController                (conduit/lineage admission gates)
    └── ChangeControlManager                  (the change-control owner)
        ├── ChangeControlTransactionManager   (request build + in-flight registry)
        ├── ChangeControlEmbargoManager       (THE moded scope-key lock table)
        ├── ChangeControlOrchestrator         (serialized admit/stage/commit/abort)
        ├── ChangeControlConflictManager      (legacy; retired at admission)
        └── TransactionMediator               (live session facade callers use)
            ├── TransactionSession (per admitted root request)
            └── TransactionStrategyBuilder -> {Bind,Link,ClusterLink,TransferOwnership}Strategy
```

---

## 2. Object catalog (all objects)

### 2.1 Hub
- **DevOpsManager** (`dev_ops_manager.py`): frame ownership root. Owns
  IncidentManager, ChangeControlManager, RiskManager, CreationGateController;
  holds SpellSystemStates; borrows DevopsInformationRegistry. Wires
  `SpellSystemStates.set_risk_manager(risk)`. Facade methods:
  `revalidate_dirty_roots`, conduit/lineage gate enable/disable/close-and-wait.

### 2.2 Transaction vocabulary (immutable payloads)
- **ChangeTransactionType** (StrEnum): `bind`, `link`, `transfer_ownership`,
  `mutation`, `cluster_link`.
- **ChangeControlTransactionRequest** (frozen): pre-admission record —
  `request_id`, `request_type`, `created_at`, `initiator_conduit_id`,
  `spellbook_id`, `conduit_ids`, `scope_keys`, `scope_claims` ((key,mode)),
  `scope_hashes`, `binding_keys`, `contract_keys`, `metadata`.
- **ChangeControlAdmissionResult** (frozen): `admitted`, `reasons`,
  `conflicts` (holder ids), `embargoes` (blocking scope keys).
- **ChangeControlStagedMutation** (frozen): post-admission record shared
  across commit/abort hooks; `from_request` + `with_updates`.

### 2.3 The lock table (concurrency primitive)
- **ClaimMode** (StrEnum): `EXCLUSIVE` "x", `SHARED` "s", `INTENT` "ix".
  Static compatibility matrix: x blocks everything; s only coexists with s;
  ix only with ix. An owner never blocks itself.
- **ChangeControlEmbargoRecord** (frozen): one claimed `scope_key` +
  `reason_tag` + `owner_request_id` + `created_at` + `mode`.
- **AcquisitionDecision** (frozen): `acquired` + `blocking`
  ((scope_key, holder_request_id, holder_mode) tuples).
- **ChangeControlEmbargoManager**: the single admission gate. `try_acquire`
  (atomic all-or-nothing), `wait_for_release` (scope-local pending on a
  Condition), `release_owner` (free a request's claims + wake all waiters).
  Derives scope keys: `scope:spellbook:<id>`, `scope:conduit:<id>`,
  `binding:<frame>:<binding>`, `contract:<frame>:<binding>:<peer>`. Legacy
  binary surfaces (`open_embargo`, `find_embargoes`, `extend_embargoes`,
  `apply/release_implicit_embargoes`) remain in EXCLUSIVE mode for compat.

### 2.4 Admission sequencing
- **ChangeControlOrchestrator**: serializes admit/stage/commit/abort under one
  lock. `admit_request` = one `embargo.try_acquire` of the request's merged
  claim set; on success registers in-flight + stages; on failure returns
  blocking evidence. `commit_request` runs validator→hook then releases;
  `abort_request` runs abort hook then releases. Hooks
  (`commit_validator`/`commit_hook`/`abort_hook`) run **outside** the lock.
  The legacy in-flight conflict scan is retired.
- **ChangeControlTransactionManager**: request bookkeeping. `build_request`
  mints `tx-<uuid>`, normalizes claim modes, derives SHA256 scope hashes;
  owns the in-flight registry, a provider→borrowers link mirror, an optional
  audit callback, and the scope-key builders.
- **ChangeControlConflictManager**: scope-overlap detector (`find_conflicts`).
  Still present, but **retired at admission** — kept only for signature
  compatibility.

### 2.5 Live session layer (the mediator)
- **TransactionMediator**: the front door callers use. Owns root sessions
  keyed by `request_id`, thread-local request-id stacks, the strategy builder,
  and the scope-wait admission loop. Key methods: `begin_transaction`
  (identity check → build → `_admit_with_scope_wait` → session), `begin_frame`
  (raw root/join), `start_transaction`/`end_transaction*` (strategy-driven),
  `end_frame`/`_finalize_root_session` (commit/abort at outermost frame).
- **TransactionSession**: per-root-request state machine. Status
  `open → committing → committed` or `open → abort_only → aborted`;
  depth-counted same-thread recursion (`join`/`leave`); owner-thread enforced;
  capabilities; commit validators/hooks, abort hooks, rollback actions
  (reverse order); `run_commit_pipeline`/`run_abort_pipeline`.

### 2.6 Strategy plug-in (per transaction family)
- **TransactionStrategy** (ABC, static/class methods): `build_start_plan`
  (identity+metadata → normalized request inputs), `on_start`, `on_end`,
  `apply_commit_delta` (registry delta while scopes held; default stamps
  `report_fact` baselines per `spellbook:`/`conduit:` region; families
  override for relational truth).
- **TransactionStrategyBuilder**: registry of strategy *classes* by normalized
  name; `resolve`, `build_start_plan`, `on_start`, `on_end`,
  `apply_commit_delta` dispatch.
- **BindTransactionStrategy / LinkTransactionStrategy /
  ClusterLinkTransactionStrategy / TransferOwnershipTransactionStrategy**:
  per-family scope/claim derivation from live topology (resolve participants,
  build spellbook/conduit/ward/cluster/borrower scopes). TransferOwnership
  reuses `TransferOfOwnership.preflight` to discover borrower/dependency
  participants without mutating runtime state.

### 2.7 Change-control owner (wiring + dirty roots)
- **ChangeControlManager**: constructs and owns the five managers above +
  the mediator (handing it `admit_request_fn=self.admit_request` so
  disablement policy applies). Second job: the **dirty-root system** —
  `_component_of_by_conduit` (node_id→{root_id}), `_dirty_roots_by_conduit`,
  `_dirty_spells_by_conduit`, `_monitor_active_by_conduit`,
  `_revalidate_fn_by_conduit`. Public API: `admit/commit/abort_request`,
  `register_pending_change`, `set_revalidator`, `rebuild/upsert_component_of`,
  `notify_spell_changed`, `revalidate_dirty_roots`, `is_root_dirty`.
  Commit pipeline hooks: structural validator (re-run Phase 1–4 on bind
  commit) then commit validator; dirty marker (mark dependents dirty in
  SpellSystemStates) then commit hook.

### 2.8 Validity plane
- **SpellSystemStates**: frame-local registry of `SpellSystemState`
  (per lineage) + `ConduitResolutionState` (per conduit). Dirty lineages,
  local topologies, `mark_collection_dependents_dirty`,
  `mark_contract_dependents_dirty`, `unregister_lineage` (notifies RiskManager).
- **SpellSystemState**: per-lineage structural validity, flags, change reason,
  direct deps/dependents.
- **ConduitResolutionState**: per-conduit spell/root validity + diagnostics +
  dirty markers.
- **SpellValidity** (enum): unknown/valid/gated/invalid/disabled/cleaned.
- **SpellState** (enum): topology/contract/mutation/ops flags.
- **SpellStateChangeReason** (enum): coarse latest-transition reason.
- **RiskManager**: per-conduit risk; reacts to validity changes and toggles
  spellbook validation-required gating.

### 2.9 Incident + information
- **IncidentManager / Incident / IncidentSeverity / IncidentStatus**:
  descriptive incident records (open/ack/resolved/suppressed).
- **DevopsIdentity**: per-runtime-object identity (owner_kind/id, frame,
  metadata, available transactions); attaches to the registry; `update_metadata`
  is local-only (eager registry refresh was removed from the hot path).
- **DevopsInformationRegistry**: frame mirror of identities, topology maps,
  live transactions, and `report_fact` freshness baselines.
- **DevopsInformationStrategy(+Builder)** and `information_strategies/*`:
  caller-paid, registry-only views — `transaction_activity_view`,
  `cluster_fanout`, `transfer_blast_radius`, `frame_operational_view`,
  `registry_consistency_audit`; `InformationFreshnessInspector` centralizes
  the staleness/baseline vocabulary.

---

## 3. The mediator system (deep dive)

### 3.1 Layering
Bottom-up, each layer adds one concern:
1. **Immutable payloads** (request / staged / admission-result): no behavior.
2. **EmbargoManager**: the only thing that decides concurrency, via moded
   scope-key claims. This is the real "lock."
3. **Orchestrator**: serializes the admit/stage/commit/abort sequence and runs
   commit/abort hooks; it *delegates* the actual concurrency decision to one
   `embargo.try_acquire`.
4. **TransactionManager**: builds requests, tracks in-flight, owns scope-key
   builders + link mirror.
5. **TransactionMediator + TransactionSession**: the live, thread-aware
   session facade that callers actually use — recursion, scope-wait, commit
   finalization, strategy dispatch.

The design intent (from the prior mediator lane,
`tickets/tasks/2026-05-30_investigate_mediator_policy_and_lazy_devops_reporting_task.md`):
a **thin mediator** (front-door/session facade) + **strategy-owned policy**
(each family owns its own scope/blast-radius) + a **top-down orchestrator**
over pending→admitted→active→released, with information strategies feeding
mirrored truth. The current code largely realizes this.

### 3.2 Scope keys & claim modes — the concurrency primitive
A request declares **scope keys** (derived: `scope:spellbook:<id>`,
`scope:conduit:<id>`, `binding:…`, `contract:…`) and optional **claim modes**
per key (`scope_claims`). At admission the embargo manager merges derived keys
(default EXCLUSIVE) with explicit modes and does one atomic `try_acquire`:
- Disjoint claim sets admit in parallel.
- `s`/`s` and `ix`/`ix` coexist on one key; `x` excludes everything.
- All-or-nothing: a partial conflict acquires nothing and returns
  `(scope_key, holder_id, holder_mode)` blocking evidence.

Scope **keys** are the admission vocabulary; scope **hashes** are advisory
identity only (the conflict manager that used them is retired).

### 3.3 End-to-end lifecycle
```
caller (e.g. Spellbook bind / Conduit link) holds a DevopsIdentity
  -> mediator.start_transaction(identity, type) / begin_transaction(...)
       -> identity.supports_transaction(name) check
       -> strategy.build_start_plan(...) shapes the request inputs
       -> transaction_manager.build_request(...) -> immutable request
       -> _admit_with_scope_wait(request):
            loop: admit_request_fn (CCM facade) -> orchestrator.admit_request
                    -> embargo.try_acquire(merged claims)
                  admitted? return : if blocking-scopes -> wait_for_release
                    (<=1s slices) and retry until deadline (else RuntimeError)
       -> TransactionSession created, registered (mediator + info registry)
       -> strategy.on_start(...)
  ... caller performs the actual mutation; same-thread nested work JOINs
      (depth++); failures call session.mark_abort_only(...)
  -> mediator.end_transaction*/end_frame(success):
       depth-- ; only the OUTERMOST frame finalizes:
         commit path: session.run_commit_pipeline()
                      -> _apply_strategy_commit_delta (registry truth, scopes held)
                      -> orchestrator.commit_request (release claims, wake waiters)
         abort path:  run_abort_pipeline -> orchestrator.abort_request (release)
       -> strategy.on_end(...)
```
Commit hooks inside the orchestrator/CCM: **structural validator** (bind →
re-run Phase 1–4 via `spellbook._run_post_conjure_structural_phases`) then
**commit validator**; **dirty marker** (mark collection/contract dependents
dirty in SpellSystemStates) then **commit hook**.

### 3.4 Concurrency & threading
- One `RLock` per manager; the embargo manager pairs it with a `Condition`.
- Blocked acquirers wait on the embargo Condition, **never** holding the
  mediator lock; every release/cleanup `notify_all`s and waiters re-attempt
  their full claim set (spurious-wake-safe).
- Same-thread recursion is depth-counted in one session (owner-thread
  enforced); cross-thread re-begin of the same request id fails fast.
- Cross-thread different roots always start; overlap is resolved purely by
  scope-claim acquisition, not by thread arbitration. This is the NOGIL-era
  posture: parallel by default, serialize only on real overlap.
- `apply_commit_delta` runs while scopes are still held, so registry-mirror
  writes are race-free against overlapping writers by construction.

### 3.5 Strategy plug-in model
`start_transaction` resolves a family strategy class via the builder;
`build_start_plan` produces the request shape (initiator, spellbook, conduits,
scope_keys/claims/hashes, binding/contract keys, metadata, capabilities).
`on_start`/`on_end` run family side effects; `apply_commit_delta` is where a
family writes its mirrored-registry truth. New transaction families plug in by
implementing `TransactionStrategy` and registering with the builder — the
mediator carries no per-family branches.

### 3.6 Config / disablement
- `max_transaction_wait_time_in_seconds` (from `AethericFrameConfiguration`)
  is the **only** root-arbitration knob; `queue_competing_root_transactions`
  and `warn` were removed.
- `ChangeControlManager.enable/disable_change_control` toggles bypass: when
  disabled, `admit_request` just records in-flight and returns admitted (no
  embargo gating), and commit/abort just drop in-flight state.

---

## 4. Validity / dirty-root plane

This is how a committed change forces later revalidation:
1. A commit's **dirty marker** marks collection/contract dependents dirty in
   `SpellSystemStates`, and/or `ChangeControlManager.notify_spell_changed`
   marks a changed spell dirty.
2. `notify_spell_changed` walks `_component_of_by_conduit` (built from Phase 5
   root blueprints via `rebuild/upsert_component_of`) to find dependent roots,
   adds them to `_dirty_roots_by_conduit`, sets `monitor_active`, and mirrors
   into `SpellSystemStates` (`state.mark_dependency_change()`).
3. `RiskManager` reacts to validity changes and toggles spellbook
   validation-required gating per conduit.

---

## 5. How it ties into everything else

- **AethericFrame** owns SpellSystemStates + DevopsInformationRegistry +
  DevOpsManager; constructs them in dependency order.
- **Conduit / ConduitWard** are the callers: bind/link/cluster/transfer flows
  carry a `DevopsIdentity` and drive the mediator; they also register
  per-conduit revalidators (`set_revalidator`).
- **Spellbook / SpellCompiler**: Phase 5 builds root blueprints →
  `rebuild_component_of`; commit-time structural validator re-runs Phase 1–4;
  the registered revalidator reruns Phase 5–11 for dirty roots.
- **Meld (the hot path)**: at resolution, `Meld._ensure_lineage_resolvable`
  checks `SpellSystemStates` validity, and `Meld._gated_validation_required`
  calls `ChangeControlManager.is_root_dirty(conduit_id, root_id)` →
  `MeldExecutionError` if dirty. This is the single narrow seam between the
  control plane and the hot path. `revalidate_dirty_roots` clears it.
- **DevopsInformationRegistry**: transactions write fact-record baselines at
  commit (`apply_commit_delta` → `report_fact`); caller-paid information
  strategies read mirrored truth + freshness without re-deriving.
- **IncidentManager**: transfer/abort failures report incidents.

The end-to-end loop: **structural mutation → mediator admission (scope claims)
→ execute → commit (structural revalidation + dirty marking + registry delta)
→ dirty roots per conduit → Meld gate (`is_root_dirty`) → revalidation**.

---

## 6. Observations / open items

- `ChangeControlConflictManager` is dead weight at admission (retired; kept
  only for the orchestrator signature). Candidate for removal once the
  signature is cleaned.
- `system_docs/readable_src_graph.json` is **truncated/invalid JSON** at EOF
  (ends mid-edge). The graph's devops nodes/edges I used were in the valid
  prefix and cross-checked against source, but the file itself needs
  regeneration.
- Legacy binary-embargo surfaces (`open_embargo`, `find_embargoes`,
  `apply/release_implicit_embargoes`, `extend_embargoes`) coexist with the
  moded `try_acquire` path; `extend_embargoes` is still EXCLUSIVE-only, which
  is a real semantic edge for post-admission scope discovery on shared claims.
- "rest mapped" subsystems (spell_system_states family, risk_manager,
  incident_manager, devops_information_registry + information_strategies) were
  understood from docs + graph + spot-checks, not full line-by-line reads.
  Flag if you want any of them read in full.
