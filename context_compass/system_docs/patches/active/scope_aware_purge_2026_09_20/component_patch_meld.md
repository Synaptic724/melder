# Meld purge discovery contract

## Purpose and boundary
Meld owns Spell lookup and scope discovery. It already carries caller, root, cluster and space stores.

## Before and after
Add concrete ConduitMeld and SpellSpaceMeld purge paths using shared discovery; existing meld is untouched.

## Interface deltas
Meld.purge accepts the same internal selectors as meld plus purge_all=True, with no overrides.
It uses _resolve_spell unchanged; no runtime Spell import or internal-Spell public dispatch.
Instance-reference targets and purge_all=False raise NotImplementedError pending the later slice.
It returns the selected store's removal count. Missing selectors/targets retain existing lookup errors.

## State and lifecycle
The base declares the abstract purge contract and shared _resolve_purge_spell selector helper only.
Concrete doors own orchestration and policy. No new caches, wrappers or persistent state.
SpellSpaceMeld targets only its local store for many/space.
Conduit many/conduit target local storage; unique targets Spell owner; lineage targets root;
cluster targets elected leader. Shared stores require the actual caller to own that store.

## Failures
Refuse wrong scope before mutation/disposal. An inert cluster retains its existing leader-required
error. Do not bypass lookup visibility, compile a target or create an instance to delete it.

## Dependencies and ordering
Shared discovery -> concrete door selects/checks its store -> Creations.purge(spell).
Authorization lives on the concrete doors; removal synchronization belongs to Creations.

Owner review gate (2026-09-20): no further asset/index/graph generation until code approval.

## Validation
Positive/refusal authority matrix, lesser caller/root-id distinction, leader distinct from binder,
name/type/frame/id selectors, empty targets and unchanged warm execution.

## Unknowns
None. Existing supplied-object references and already-injected references are not rewritten.
