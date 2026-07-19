# Patch: Unify the meld creation-store surface (meld layer only)

## Metadata
- Patch ID: PATCH-2026-06-23-meld-store-surface
- Program: "scope authoritative" (lane 1 — step 0: align the meld store surface)
- Status: COMPLETE — meld layer renamed AND all callers rewired. Build restored.
- Owner: cowork / optimizer_0
- Risk: high (threadsafe meld core + breaks construction until callers rewired)
- Sandbox: py_compile OK (3.10); full run requires 3.14t AND the caller fixups.

## What changed (3 files)
Canonical store surface, now owned by the base `Meld`:
- `_conduit_creations` — owning-conduit store (unique_per_conduit / many). Was
  ConduitMeld `_creations` and SpellSpaceMeld `_owner_conduit_creations`.
- `_root_creations` — lineage-root store.
- `_cluster_creations` — ClusterCreations facade (resolved at the front door via
  `resolved_store()`; assigned post-construction by the conduit).
- `_spellspace_creations` — active spellspace scope store; `None` on the conduit
  path. LEFT UNTOUCHED in SpellSpaceMeld's logic (the load-bearing scope-vs-
  conduit distinction; spellspace work must never fall back to `_conduit_creations`).

- meld.py (base `Meld`): added the four to `__slots__` + `__init__`
  (`conduit_creations`, `root_creations=None`→defaults to conduit_creations,
  `cluster_creations=None`, `spellspace_creations=None`); the four `del`s moved
  into `Meld.cleanup()`; docstrings updated to say the base owns the surface.
- conduit_meld.py (`ConduitMeld`): `__slots__ = []`; thin `__init__` that renames
  the param `creations` → `conduit_creations` and forwards to base; thin
  `cleanup` delegating to base; `self._creations` → `self._conduit_creations` at
  its 3 use sites.
- spellspace_meld.py (`SpellSpaceMeld`): slots keep only `_spellspace` /
  `_spellspace_id` / `_owner_conduit_id`; thin `__init__` renames param
  `owner_conduit_creations` → `conduit_creations` and forwards all four stores to
  base; cleanup drops only its own ids; `_owner_conduit_creations` →
  `_conduit_creations` at its 4 use sites; `_spellspace_creations` unchanged.

## Verification
- py_compile: all three parse.
- grep: zero `_owner_conduit_creations`, zero bare `self._creations`, zero old
  param names remain; the new surface is present in all three files.

## Callers rewired (build restored) — exactly 3 sites
Full src grep showed the rename touched only three call sites:
- conduit.py:294 `creations=` -> `conduit_creations=` (ConduitMeld construction).
- conduit.py:1731 `self._meld._creations = ...` -> `self._meld._conduit_creations`
  (post-upgrade field write).
- spell_space.py:142 SpellSpaceMeld kwarg `owner_conduit_creations=` ->
  `conduit_creations=` (final hand-off to the meld).
NOT changed (correctly): the SpellSpace / SpellSpacePool own `_owner_conduit_creations`
fields and their `owner_conduit_creations=` params (conduit.py:304 -> Pool,
spell_space_pool.py:90 -> SpellSpace) are NOT meld fields; they keep that name and
only the final kwarg into the meld was renamed. Codegen and cluster untouched.

## Verification
- py_compile OK across all 5 files (3 meld + conduit.py + spell_space.py).
- grep: zero residual `_meld._creations` / `_meld._owner_conduit_creations` /
  `conduit_meld._creations` reads.
- Behavior-preserving (pure rename/relocation): the scope suites should return to
  the SAME pass/fail set as before the meld work (lineage/cluster/spellspace
  dependency reds STILL red -- those are the real bugs, not yet fixed; unique/upc/
  many/direct greens still green). User runs on 3.14t to confirm no regression.

## Next
With the surface unified and honest, resume lane 1 proper: pass the meld into the
codegen so each step pulls its own store (`meld._conduit_creations` /
`_root_creations` / `_cluster_creations` resolved / `_spellspace_creations`),
solo -> many_only -> generalized.
