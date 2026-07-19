# Mutation Lifecycle

## Purpose
Standardize mutation progression so every campaign follows predictable states.

## Lifecycle States
1. `proposed`
2. `authorized`
3. `locked`
4. `applied`
5. `validated`
6. `promoted` or `rolled_back` or `discarded`
7. `closed`

## State Semantics

### `proposed`
- Candidate mutation is defined (codeblock, patch, or structural intent).

### `authorized`
- ACL/profile/domain checks passed for mutation operations.

### `locked`
- Mutation lock acquired for target scope/spell/object set.

### `applied`
- Candidate is materialized in a mutation scope.

### `validated`
- Revalidation and diagnostics completed with result artifacts.

### `promoted`
- Candidate accepted into curated lineage.

### `rolled_back`
- Candidate rejected and prior stable node restored.

### `discarded`
- Candidate dropped without promotion.

### `closed`
- Lock released, scope closed, records finalized.

## Required Artifacts
- candidate identity (`candidate_id`, source hash)
- lock identity (`lock_id`, owner, scope)
- validation report
- lineage decision record
- incident links

