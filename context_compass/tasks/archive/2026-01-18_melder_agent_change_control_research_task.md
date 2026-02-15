# Task: Compile agent stories and change-control impacts

## Metadata
- Task ID: TASK-2026-01-18-melder-agent-change-control-research
- Story: STORY-2026-01-18-melder-post-conjure-binding
- Status: completed
- Owner:
- Priority: p1
- Created: 2026-01-18
- Updated: 2026-01-20

## Objective
Compile a detailed research writeup on **agent usage flows** (human or AI) for
Melder’s conduit + spell graph system, with emphasis on change-control,
post-conjure binding, contracted linking, and revalidation behavior.

## Scope Boundaries
- In scope:
  - Agent-facing surfaces: Spellbook, Conduit, ConduitWard, contract/link flows.
  - Change-control gating and SpellSystemStates behavior.
  - Post-conjure binding/scan effects on structural phases and collections.
  - Multi-conduit interaction patterns **within a single AethericFrame**.
- Out of scope:
  - Cross-aetheric-frame coordination (explicitly not allowed).
  - ACL/permission redesigns beyond describing current behavior.
  - Implementing new features; this is research only.

## Steps / Checklist
- [x] Inventory agent surfaces and how they mutate graph state.
- [x] Map those actions to change-control + validation gates.
- [x] Identify risks and open questions for agent-driven concurrency.
- [x] Draft MRP-aligned scope for coordination improvements.
- [x] Propose follow-up tasks and decision checkpoints.

## Deliverables
- Detailed research writeup in Context / Handoff Summary (usage flows + impacts).
- Draft MRP scope for coordination improvements.
- Follow-up task list for refinement.

## Files / Paths Impacted
- `src/melder/aether/aetheric_frame.py`
- `src/melder/aether/dev_ops/dev_ops_manager.py`
- `src/melder/aether/dev_ops/change_control_manager/change_control_manager.py`
- `src/melder/aether/dev_ops/spell_system_states/spell_system_states.py`
- `src/melder/aether/conduit/conduit.py`
- `src/melder/aether/conduit/conduit_ward/conduit_ward.py`
- `src/melder/aether/conduit/meld/meld.py`
- `src/melder/aether/conduit/meld/meld_runtime/meld_runtime.py`
- `src/melder/spellbook/spellbook.py`
- `src/melder/spellbook/spell_crafter/spell_crafter.py`

## Validation
- Not run (analysis-only).

## Risks / Rollback Notes
- Risk: Agent coordination assumptions diverge from actual runtime behavior.
  Mitigation: document uncertainties and list code-level verification steps.

## Done Checklist
- [x] Steps complete and checked off
- [x] Deliverables produced and linked
- [x] Documentation updated (if needed)
- [x] Validation status recorded
- [x] User walkthrough complete and acceptance criteria confirmed

## Context / Handoff Summary
### Agent surfaces (what agents can do today)
Evidence is limited to a single AethericFrame (no cross-frame coordination).

1) **Spellbook-centric actions (graph mutation + registration)**
   - Bind new spells (`Spellbook.bind`, `SpellBinder.finalize`):
     - Registers a lineage in `SpellSystemStates` and marks it gated.
     - Requires an active binding transaction (post-change).
     - Post-conjure binds run structural phases 1-4 at transaction end.
   - Scan modules (`Spellbook.scan`):
     - Binds all `scan_bind` targets; also transaction-gated.
   - Conjure (`Spellbook.conjure`):
     - Builds a Conduit; later meld calls can trigger Phase 5-7 per conduit.

2) **Conduit-centric actions (resolution + sharing)**
   - Meld (`Conduit.meld`):
     - Runs structural revalidation when state is UNKNOWN/GATED.
     - Blocks when `ChangeControlManager` marks root dirty.
   - Link/contract (`ConduitWard._link`, `_add_spell_to_contract`):
     - Contracts spells into the borrower’s Spellbook contracted maps.
     - Enforces binding-key uniqueness across **contracted** maps only.
     - Optionally links dependencies with preflight collision checks.
   - Transfer ownership (`TransferOfOwnership`):
     - Registers pending change entries and can mark lineages gated/dirty.
     - Uses change-control hooks during transfer.
   - Policy/permissions:
     - Contracts require spell permissions (create/read) and policy gates.

3) **DevOps/control-plane actions**
   - `DevOpsManager`:
     - Exposes `ChangeControlManager` + `SpellSystemStates` for tooling.
   - `ChangeControlManager`:
     - Tracks pending changes, `component_of` index, and dirty roots.
     - Blocks meld when a root is dirty.
   - `SpellSystemStates`:
     - Tracks lineages, dependencies, and **collection dependents per Spellbook**.
     - Manages per-conduit resolution validity (Phases 5-7).

### Agent usage flows (how agents operate the system)
These are intended usage scenarios derived from current APIs and code behavior.

1) **Solo agent builds a toolset in one conduit (pre-conjure)**
   - Agent binds or scans all spells in a transaction, then conjures.
   - Structural phases run during conjure; per-conduit phases (5-7) run on meld.
   - No change-control friction unless spell lineages are dirty.

2) **Solo agent adds tools post-conjure**
   - Must open a binding transaction, bind/scan, then close transaction.
   - Structural phases 1-4 run for new spells at transaction end.
   - list[Frame] consumers in *this Spellbook* are marked dirty.
   - Meld will re-run phases 5-7 as needed (per conduit).
   - If the agent forgets the transaction, bind/scan raises.

3) **Multi-agent collaboration inside one frame (isolated spellbooks)**
   - Each agent owns a conduit/spellbook; no cross-frame effects.
   - Sharing occurs only via explicit links/contracts.
   - Contracted spells appear in borrower’s contracted maps only; owners are not
     auto-updated unless linked and explicitly revalidated.

4) **Agent shares tools via contract links**
   - Agent A links to Agent B and contracts a spell.
   - Borrower’s Spellbook enforces binding-key uniqueness across **contracted peers**.
   - Contract fails when a contracted key collides with another contracted key.
   - Local key overlap is allowed; local bindings win lookup resolution.
   - list[Frame] consumers in borrower’s Spellbook can include contracted spells,
     but only after local gating and resolution phases allow it.

5) **Agent updates a spell that is currently contracted**
   - Owner updates binding (new version) -> change-control marks lineage gated.
   - Borrowers relying on contracted spell may be blocked until revalidation
     (depending on how gating is surfaced in their conduit).
   - Current code does not describe an explicit contract-scoped change-control
     barrier; this is a coordination gap to resolve.

6) **Agents trading tools frequently (dynamic mode)**
   - Frequent bind/scan/contract operations imply many transient states.
   - Without a higher-level coordination model, meld can observe partially
     updated graphs. Current mitigation is transaction gating + dirty-root checks.

7) **Agent binds a spell with a frame overlap (local collision)**
   - Agent attempts to bind a spell with a lookup key already used locally.
   - `Spellbook._assert_lookup_key_available(...)` raises a collision error.
   - Agent must use a distinct binding_name or spellframe to disambiguate.
   - This avoids silent override in the local graph.

8) **Agent contracts a spell that overlaps a local binding key**
   - Agent links to peer and attempts to contract a spell with a key already
     bound locally (or already contracted).
   - Preflight collision checks raise only when a contracted key collides with
     another contracted key (or within dependency batches).
   - Local overlap is allowed; the contracted spell is shadowed by the local key.

9) **Agent unlinks or removes a contracted spell**
   - Agent removes a contracted spell or clears a contract.
   - Borrower spellbook removes contracted maps and invalidates contract
     consumers via `_invalidate_contract_consumers(...)`.
   - list[Frame] consumers in the borrower are now potentially stale and must
     re-resolve on next meld.

10) **Agent transfers ownership with active contracts**
   - Transfer registers pending changes and may mark lineages gated/dirty.
   - If `force_unshare` is set, contracts/shares are stripped as part of the move.
   - Borrowers can lose access; subsequent melds will fail or revalidate.

11) **Agent changes policy or permissions while links exist**
   - Policy changes can block contracting or inbound links.
   - If policy forbids new links, existing contracts remain but future changes
     cannot propagate through new contracts.
   - Agent must reconcile policy state with contract expectations.

12) **Agent links with dependency auto-linking enabled**
   - Agent contracts a root spell with `link_dependencies=True`.
   - Preflight walks dependency graph for collisions; any conflict aborts.
   - If dependency owners differ, the system auto-links to those owners.
   - This expands the contract graph and increases coordination needs.

13) **Agent uses lesser conduits (child nodes)**
   - Lesser conduits cannot bind directly; they must be upgraded to normal.
   - After upgrade, resolution state is seeded from root conduit.
   - Agents should expect resolution validity to follow the upgraded lineage.

14) **Agent attempts meld during a binding transaction**
   - Binding transaction is a deliberate mutation boundary.
   - The system can be in a transient state; if roots are dirty, meld blocks.
   - If no dirty gate is active, meld may still observe partial availability,
     so transaction semantics should be documented for agents.

15) **Agent revalidates dirty roots via DevOps**
   - Agent explicitly calls `DevOpsManager.revalidate_dirty_roots(...)`.
   - This re-runs phases for dirty roots using the registered revalidator hook.
   - On failure, dirty flags remain and meld is blocked for those roots.

16) **Agent declares cross-conduit dependencies via SpellContract**
   - Agent uses `SpellContract` defaults in constructor parameters.
   - Contract sockets are captured during Phase 1-3 and tracked as special
     sockets in the symbolic graph (not normal DI).
   - In automatic mode, validation warns that contracts are unresolved.

### Coordination direction (MRP guardrails)
- Single admission gate: all change requests funnel through the orchestrator
  (lock-based admission) to avoid race conditions.
- Embargoes are transaction-driven internal state (implicit via bind/link/
  transfer/mutation) and released on commit/abort.
- Provider changes embargo inbound link/contract requests targeting that
  provider while the change is active.
- Advisory hints (soft locks) are exposed so agents can coordinate without
  hard-blocking reads.
- Minimal audit logging: conduit_id, request_type, created_at (log only if a
  logger is configured).
   - In dynamic mode, agents must link provider conduits to satisfy contracts.
   - On meld, `MeldEngine` resolves contracts by checking contracted maps first,
     then local spellbook maps; ambiguous/missing providers raise errors.

17) **Agent uses MutationContract for late-bound overrides**
   - MutationContract sockets are tracked similarly to SpellContract sockets.
   - Validation can warn when providers are missing or ambiguous.
   - Late binding can defer provider availability, but meld still fails if
     nothing resolves at execution time.

### Graph system changes and agent impact
- **Post-conjure structural phases** ensure new spells are structurally validated
  before any Phase 5-7 resolution can occur.
- **Collection dependency tracking** is spellbook-scoped:
  list[Frame] consumers are marked dirty only in the owning Spellbook.
- **Change-control gating** blocks meld execution for dirty roots, but the
  component-of index is frame-wide and can be overwritten by whichever spellbook
  last ran Phase 5/7.
- **Contract socket validation** (Phase 4) surfaces missing/ambiguous providers,
  especially for SpellContract/MutationContract in automatic mode.

### Ways an agent can impact system state (explicit actions)
- Bind or scan new spells (creates lineage; marks gated; dirties collections).
- Conjure conduits (establishes per-conduit resolution state).
- Meld (triggers structural + resolution phases; blocked by change-control).
- Link and contract spells (adds contracted spell into borrower spellbook).
- Unlink or sever contracts (removes contracted spells; invalidates consumers).
- Transfer spell ownership (marks pending changes; potentially gates lineages).
- Declare SpellContract / MutationContract sockets in spell signatures.
- Add contract dependencies (auto-linking dependencies expands contract graph).
- Modify policies/permissions (affects contract eligibility).
- Trigger DevOps revalidation (`DevOpsManager.revalidate_dirty_roots`).
- Clear pending changes (`ChangeControlManager.clear_pending_change`).
- Change binding strategy (binding_name/spellframe) to resolve collisions.

### Open risks / questions
- How to prevent frame-wide `component_of` overwrite when multiple spellbooks
  run Phase 5/7 inside the same frame.
- Whether contracted spells should register dependency changes in the borrower’s
  change-control view (contract-scoped gating).
- Whether a contract-level transaction is needed to prevent meld during rapid
  agent-driven graph edits.
- How to expose transaction state to agents so they can decide when to read or
  defer meld during high-churn periods.
- Whether contract-provider ambiguity should be resolved by policy (e.g. reject
  early vs allow manual disambiguation via binding_name).

### Research notes (contract sockets)
- `SpellContract` is explicitly **dynamic-mode only** and declares a late-bound
  contract socket intended to be satisfied via conduit linking.
  (`src/melder/aether/conduit/meld/contracts/spell_contract.py`)
- `MeldEngine` resolves SpellContract sockets by scanning contracted maps first,
  then local maps, and raises `MeldExecutionError` for ambiguous/missing providers.
  (`src/melder/aether/conduit/meld/meld_engine/meld_engine.py`)
- Phase 4 validation includes `ContractProviderPresenceStrategy`, which warns
  in automatic mode and raises issues for ambiguous/malformed contracts.
  (`src/melder/spellbook/spell_crafter/validation/strategies/contract_provider_presence_strategy.py`)

### Draft MRP scope (coordination improvements)
- Keep all coordination **within one AethericFrame** (no cross-frame coupling).
- Use a single admission gate with conflict/embargo checks; no request queues.
- Treat bind, link, transfer ownership, mutation, and cluster_link as the only
  transaction types; no standalone scan/embargo transactions.
- Keep binding/scan as the explicit mutation boundary; spellbooks retain local
  dirty propagation (list[Frame] consumers) without global redundancy.
- Require explicit link participants (borrower + peers) for deterministic
  contract admission and embargo scope.
- Scope keys and hashes stay internal; only minimal audit metadata is logged
  when a logger exists.

### Follow-up tasks (draft)
- Confirm whether `component_of` can be safely scoped by spellbook/conduit id.
- Define contract-scoped dirty propagation rules for contracted spells.
- Finalize change-orchestrator staging semantics (metadata-only vs map staging).
- Add agent-focused tests (bind/scan post-conjure + contract changes).
