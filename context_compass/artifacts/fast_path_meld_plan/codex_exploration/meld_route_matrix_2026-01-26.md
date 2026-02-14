# Meld Route Matrix (Fast Path vs Fallback)

## Scope
Enumerate possible meld routes and the gating conditions that select them.
Aligned to fast-path tickets and existing runtime/engine behavior.

## Sources
- `context_compass/artifacts/fast_path_meld_plan/ticket_fast_path_github.md`
- `context_compass/artifacts/fast_path_meld_plan/ticket2_fast_path_github.md`
- `context_compass/artifacts/fast_path_meld_plan/ticket3_fast_path_github.md`
- `context_compass/artifacts/fast_path_meld_plan/research_fast_path_gates.md`
- `context_compass/artifacts/fast_path_meld_plan/research_plan_compilation.md`
- `context_compass/artifacts/fast_path_meld_plan/research_override_mutation.md`
- `src/melder/aether/conduit/meld/meld.py`
- `src/melder/aether/conduit/meld/meld_runtime/meld_runtime.py`
- `src/melder/aether/conduit/meld/meld_engine/meld_engine.py`

## Definitions (ticket-aligned)
- Fast path: execute precompiled plan (ExecutionProgram / RootExecutionPlan).
- Slow path: current MeldRuntime + MeldEngine graph execution.
- Best case: no overrides, no mutation overrides, validity already valid, not dirty, hooks off.
- Shared existence: any existence except `Existence.many`.
- Per-path existence: `Existence.many`.
- Tight creation path: precompiled creation steps with minimal branching (no locks policy here).

## Route Matrix (High-Level)
| Route | Conditions (all must hold) | Execution path | Notes |
| --- | --- | --- | --- |
| R1 Best-case fast plan | Plan exists and signature matches; no overrides; no mutation overrides; validity VALID; not dirty; hooks off | Fast plan executor | Target: tight loop, reuse/construct/register |
| R2 Fast plan + root cache hit | R1 + root instance already cached and reuse allowed | Return cached root | Optional optimistic no-lock read (ticket2) |
| R3 Fast plan ineligible: overrides | Any overrides present (root/socket/contract) | Slow path | Until override patch maps (phase 10) are added |
| R4 Fast plan ineligible: mutation | Mutation override present | Slow path | Until mutation patch map exists |
| R5 Fast plan ineligible: validation gate | Lineage or resolution validity UNKNOWN/GATED/INVALID | Slow path | Runs phases 1-7 as needed |
| R6 Fast plan ineligible: dirty root | Change-control dirty root | Slow path | Revalidate and rebuild plan |
| R7 Hooked path | Hooks enabled (global or spell) | Slow path | Plan variant optional per tickets |

## Detailed Routes (Execution Lanes)

### R1: Best-case (Singleton, self creations, no override, no validation, no hooks)
Conditions:
- Root spell is shared existence (unique / per-cluster / per-lineage).
- Owner creations present and valid.
- No overrides or mutations.
- Validity already VALID and root not dirty.
- Hooks disabled.

Execution:
1) Fast path gate passes.
2) Check root cache (optional early return).
3) Execute precompiled plan:
   - reuse instances where allowed
   - construct missing
   - register by existence
4) Return root instance.

### R2: Per-conduit shared route (unique_per_conduit)
Conditions:
- Same as R1 but existence is per-conduit.
- Caller creations required (per meld.py).

Execution:
1) Fast gate passes.
2) Use caller creations for reuse and registration.
3) Execute plan as above.

### R3: Per-path route (Existence.many)
Conditions:
- No overrides, no mutation, validity VALID, not dirty.
- Existence.many nodes in plan.

Execution:
- Plan expands occurrences into per-path instance keys.
- Per-path instances are always constructed (no reuse).
- Registration only when disposal methods exist.

### R4: Overrides present (root or socket)
Conditions:
- Any override payload in `spell_override` or socket-level overrides present.

Execution:
- Current behavior: slow path (GraphMutator + SpellOverrider + MeldEngine).
- Ticket direction: introduce override patch map (phase 10) so limited overrides can remain fast.

### R5: Mutation overrides present
Conditions:
- `spell.mutation_override` non-empty.

Execution:
- Current: GraphMutator clones/rewires DAG at runtime, then engine run.
- Ticket direction: mutation patch map at conjure time, else fallback.

### R6: Contract sockets (late-bound)
Conditions:
- Contract providers require dynamic selection or overrides.

Execution:
- Current: engine resolves per occurrence using contracted spells or local fallback.
- Ticket direction: compile contracts when wiring is stable; otherwise mark plan ineligible.

### R7: Validity gated or dirty root
Conditions:
- Structural or resolution validity UNKNOWN/GATED/INVALID, or dirty root.

Execution:
- Meld gate runs phases 1-7 as needed (under locks).
- Plan invalidated and rebuilt before retrying fast path.

### R8: Hooks enabled
Conditions:
- Meld hooks or spell hooks enabled.

Execution:
- Current: hook-aware meld path (pre, activation, post).
- Ticket direction: optionally compile hook-aware plan variant, or force slow path.

### R9: Spellspace scope
Conditions:
- Existence.unique_per_spell_space in any nodes.

Execution:
- Requires active spellspace in caller conduit.
- Slow path semantics must be preserved; fast path may precompute spellspace selection but still requires active spellspace validation.

### R10: Existing-creation spells
Conditions:
- Spell is existing-creation type.

Execution:
- Runtime returns user_created_object; registration depends on existence.
- Fast path can treat as zero-construction op (skip callable, optional register).

## Tight Creation Plan (what the fast executor should do)
Goal: minimize dynamic decisions in meld by baking creation steps into the plan.

### Creation actions (per node)
| Existence | Reuse check | Construct | Register | Notes |
| --- | --- | --- | --- | --- |
| unique | yes (shared store) | if miss | yes | Root and shared nodes; cache hit returns |
| unique_per_conduit | yes (caller store) | if miss | yes | Caller creations required |
| unique_per_spell_space | yes (active spellspace) | if miss | yes | Requires active spellspace |
| unique_per_conduit_cluster | yes (shared store) | if miss | yes | Shared existence |
| unique_per_conduit_lineage | yes (shared store) | if miss | yes | Shared existence |
| many | no | always | only if disposal methods | Treat as per-path node |

### Tight creation sequence (fast path)
1) Resolve creations target (owner vs caller vs spellspace) from plan metadata.
2) Optional reuse check (only for non-many).
3) Construct missing nodes (class/method/lambda) or return existing object.
4) Register by existence (skip for many without disposal methods).

Notes:
- This section intentionally avoids lock policy; locking strategy is a rebuild concern.
- The plan should encode the creations target and existence actions so meld does not branch.

## Notes / Alignment to Tickets
- R1/R2/R3 are the primary fast-path targets (tickets 1-3).
- R4/R5/R6 are explicit slow-path fallback triggers unless patch maps exist.
- R7 preserves change-control and validation semantics.
- R8 acknowledges hook behavior as an eligibility gate (research_fast_path_gates).
- R9/R10 ensure existence and spellspace semantics are retained.

## Strategy: Route Tiers and Cost Expectations
### Tier 0: Best-case fast plan
Conditions:
- Validity already VALID (structural + per-conduit resolution).
- Not dirty under change-control.
- No overrides/mutations/contracts requiring dynamic work.
- Hooks disabled.
- Compiled plan exists and signature matches.

Cost profile:
- O(steps) execution of precompiled plan.
- Optional early return for cached root.

### Tier 1: Fast plan but cache miss
Conditions:
- Same as Tier 0, but root (or some shared nodes) not cached.

Cost profile:
- Tight loop constructs missing nodes and registers; still no graph/override work.

### Tier 2: Partial revalidation (dirty root or gated validity)
Conditions:
- Structural or resolution validity UNKNOWN/GATED, or root is dirty.

Behavior (per tickets):
- Re-run phases 1-4 and/or 5-7 as needed for the affected root.
- Rebuild compiled plan (phases 8-10) after validation completes.

Cost profile:
- Users pay the revalidation cost; subsequent melds return to Tier 0/1.

### Tier 3: New binding or wiring change
Conditions:
- New spell bound, contract wiring changed, or conduit link/unlink.

Behavior (per tickets):
- Full conjure pipeline for affected roots:
  - Phases 1-7 to rebuild validity and root blueprints.
  - Phases 8-10 to compile new execution plan.

Cost profile:
- Heavy, expected, acceptable (one-time compilation cost).

### Tier 4: Override/mutation heavy
Conditions:
- Overrides, mutation overrides, or late-bound contract resolution required.

Behavior:
- Current slow path: GraphMutator + SpellOverrider + MeldEngine.
- Future: patch maps from Phase 10 for targeted overrides; else fallback.

Cost profile:
- Worst-case, but correctness preserved.

## Strategy: Revalidation Ladder (What Users Pay For)
1) **Dirty root**: re-run required validation phases for that root (1-4 and/or 5-7), then recompile plan (8-10).
2) **New binding / wiring change**: full 1-7 + 8-10 for affected roots (intended heavy path).
3) **Overrides/mutations**: either patch fast plan (if supported) or go slow path.

## Strategy: "Unwind from Tier 0" Execution Process
Goal: attempt the most optimistic path first, then unwind in ordered steps
that preserve correctness while maximizing speed.

### Step 0: Ultra-fast gate + cache return
- Check: plan exists, signature matches, validity VALID, not dirty, hooks off.
- If root cached and reuse allowed: return immediately.
- Else continue to Step 1.

### Step 1: Execute compiled plan (no overrides)
- Preconditions: no overrides, no mutation overrides, no late-bound contracts.
- Execute tight loop plan: reuse where allowed, construct missing, register.
- Return root instance.

### Step 2: Patchable overrides (if Phase 10 exists)
- If overrides present and patch map exists:
  - Apply override slot patches to plan.
  - Execute patched plan.
- If override cannot be patched: go to Step 3.

### Step 3: Mutation patches (if Phase 10 exists)
- If mutation overrides present and patch map supports it:
  - Apply mutation patches.
  - Execute patched plan.
- If mutation cannot be patched: go to Step 4.

### Step 4: Slow path execution (current engine)
- Run MeldRuntime + MeldEngine with GraphMutator / SpellOverrider.
- Preserve all existing semantics (contracts, spellspace, hooks, locks).

### Step 5: Revalidation / recompilation (when needed)
- If validity gated/unknown or dirty root:
  - Re-run phases 1-7 as needed.
  - Rebuild compiled plan (phases 8-10).
  - Retry from Step 0.

## Phase Coverage Matrix
This maps the routes back to the conjure/runtime phases described in the
fast-path tickets (1-7 existing, 8-10/11 proposed).

### Phase Catalog (ticket-aligned)
| Phase | Scope | Purpose (short) | Primary artifact | Ticket source |
| --- | --- | --- | --- | --- |
| 1 | Conjure | Requirements extraction | SpellRequirements | ticket_fast_path_github.md |
| 2 | Conjure | Symbolic graph | SpellSymbolicGraph | ticket_fast_path_github.md |
| 3 | Conjure | Local resolution frame / DAG | SpellResolutionFrame, SpellLocalTopology | ticket_fast_path_github.md |
| 4 | Conjure | Structural validation | SpellValidationResult, validity flags | ticket_fast_path_github.md |
| 5 | Conjure | Root blueprints (deep DAG) | RootResolutionBlueprint, SpellSystemIndex | ticket_fast_path_github.md |
| 6 | Conjure | System validation (per-conduit) | SpellSystemStates resolution validity | ticket_fast_path_github.md |
| 7 | Conjure | Change-control wiring | Dirty tracking + revalidator | ticket_fast_path_github.md |
| 8 | Conjure (proposed) | Occurrence plan compilation | OccurrencePlan / execution order | ticket_fast_path_github.md, ticket2_fast_path_github.md |
| 9 | Conjure (proposed) | Injection plan compilation | Arg/Factory plan | ticket_fast_path_github.md, ticket2_fast_path_github.md |
| 10 | Conjure (proposed) | Override/mutation patch maps | Patch maps / slot maps | ticket_fast_path_github.md, ticket3_fast_path_github.md |
| 11 | Conjure (optional) | Codegen executor | Compiled fast executor | ticket_fast_path_github.md, ticket2_fast_path_github.md, ticket3_fast_path_github.md |

### Route-to-Phase Coverage
| Route / Tier | Phases required at meld time | Phases required at conjure time |
| --- | --- | --- |
| Tier 0 (best-case fast plan) | None (just gates) | 1-7 + 8-10 (11 optional) |
| Tier 1 (fast plan, cache miss) | None (just gates) | 1-7 + 8-10 (11 optional) |
| Tier 2 (dirty/gated revalidation) | 1-4 and/or 5-7, then 8-10 | 1-7 + 8-10 (refresh) |
| Tier 3 (new bind / wiring change) | None (after conjure completes) | Full 1-7 + 8-10 (11 optional) |
| Tier 4 (override/mutation heavy) | Slow path engine (graph/override) | 1-7 only (until patch maps ready) |

### Notes
- Phases 1-7 are already implemented and can be re-run at meld time if gated.
- Phases 8-10 remove per-call graph planning from meld.
- Phase 11 is optional and only needed if the tight loop still misses targets.

## Open Questions (from research docs)
- Where compiled plans live (blueprint vs spell vs conduit) without cleanup issues.
- What plan signature and epochs are needed for invalidation.
- How to patch overrides for shared vs per-path instances without breaking semantics.
