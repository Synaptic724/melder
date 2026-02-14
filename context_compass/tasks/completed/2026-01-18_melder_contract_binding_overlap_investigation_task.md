# Task: Investigate binding-key overlap when contracting linked spells

## Metadata
- Task ID: TASK-2026-01-18-melder-contract-binding-overlap-investigation
- Story: STORY-2026-01-18-melder-post-conjure-binding
- Status: completed
- Owner:
- Priority: p1
- Created: 2026-01-18
- Updated: 2026-01-20

## Objective
Define and validate the contract-linking behavior when a spell contracted from
another conduit overlaps with an existing local or contracted binding key.

This is an analysis ticket: produce a clear, deterministic contract for
collision behavior (error vs namespace vs aliasing) and identify the exact
integration points that would need enforcement.

## Scope Boundaries
- In scope:
  - Conduit link/contract flows (`ConduitWard`).
  - Spellbook contracted spell registries + lookup collision guards.
  - Binding key normalization (`SpellInputUtils` / `_make_spell_key`).
  - Contract dependency linking and preflight collision checks.
- Out of scope:
  - Implementing new namespace/alias features.
  - Any cross-aetheric-frame coordination.
  - ACL or permissions model changes.

## Steps / Checklist
- [x] Inventory contract/link code paths and where binding collisions are checked.
- [x] Identify current behavior for collisions (local vs contracted vs dependency links).
- [x] Define desired collision contract (error vs explicit disambiguation).
- [x] Identify follow-up tasks and test cases needed to enforce the contract.

## Deliverables
- Written analysis + recommendation in Context / Handoff Summary.
- Proposed tests to cover link collisions and dependency-link collisions.

## Files / Paths Impacted
- `src/melder/aether/conduit/conduit_ward/conduit_ward.py`
- `src/melder/aether/conduit/conduit_ward/contract/`
- `src/melder/spellbook/spellbook.py`
- `src/melder/spellbook/spell_input_utils.py`

## Validation
- Not run (analysis-only).

## Risks / Rollback Notes
- Risk: Overly strict collision policy could block legitimate contract use cases.
  Mitigation: define explicit disambiguation rules (binding_name or spellframe).

## Done Checklist
- [x] Steps complete and checked off
- [x] Deliverables produced and linked
- [x] Documentation updated (if needed)
- [x] Validation status recorded
- [x] User walkthrough complete and acceptance criteria confirmed

## Context / Handoff Summary
- Evidence: contract/link collision checks are **contracted-only** today.
  - `ConduitWard._add_spell_to_contract(...)` and
    `_preflight_contract_dependency_collisions(...)` call
    `Spellbook._assert_lookup_key_available(..., check_local=False,
    check_contracted=True)`, so they reject collisions across **contracted**
    maps but do not check local bindings.
  - `Spellbook._add_contracted_spell(...)` repeats the same contracted-only check.
  - `Spellbook.bind(...)` uses `check_contracted=False`, so **local** bindings
    are allowed even when a contracted binding key already exists.
  - `Meld._resolve_spell_by_lookup_key(...)` resolves **local first**, then
    contracted, so local bindings shadow contracted bindings on key overlap.
  - Dependency preflight tracks a `batch_keys` map to prevent duplicate keys
    within a dependency tree, then checks against contracted maps only.

- Current behavior summary:
  - Local ↔ contracted key overlap is **allowed**; local wins resolution.
  - Contracted ↔ contracted overlap across peers is **rejected**.
  - Dependency-link collisions are rejected within the dependency batch and
    against existing contracted bindings (but not local bindings).

- Recommended contract (MRP):
  1) **Keep local precedence**: allow local/contracted key overlap and document
     that local bindings shadow contracted ones during lookup. If callers need
     the remote spell, they must use a distinct `binding_name`/`spellframe` or
     resolve by `spell_id`.
  2) **Reject contracted/contracted overlaps** across peer conduits (already
     enforced). This avoids nondeterministic resolution across peers.
  3) **Keep dependency preflight strict** for contracted maps + batch collisions
     to ensure deterministic dependency linking.

- Follow-up tests to codify the contract:
  - Local binding vs contracted binding with same key resolves to local.
  - Contracting from two peers with the same key raises a collision error.
  - Dependency-link collisions (batch or existing contracted) raise before
    linking, while local key overlap does not block.
