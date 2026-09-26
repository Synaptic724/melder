# component_patch_spellcompiler_pool_reads

## Metadata
- Patch ID: compiler_pool_snapshot_2026_09_26
- Component: SpellCompiler and Validation Pipeline
- Status: draft
- Owner: user (implementation: melder_0)
- Created: 2026-09-26T21:20:00Z

## Before/After Behavior
- Before: Phase 3 `_iter_all_spells`, the binding-resolution-cycle, circular-dependency and
  duplicate-name strategies, Phase 5 `run_frame_wide`/`run_local`, Phase 6 `run_frame_wide` (and the two
  Phase-6 system strategies it hands the pool to) and the Phase-8 `_build_spell_walk_rows` iterate
  `spellbook._spell_id_pool` live. A concurrent write raises "dictionary changed size during iteration";
  Phase 8 catches it and returns None, dropping the existence-occurrence analysis for that pass. A Phase-5
  pass that sees a pool entry before its state is registered raises "requires a live SpellSystemState".
- After: each of these iterates a copy of the pool taken in one call; Phase 5 and Phase 6 frame-wide take
  one copy per pass and use it throughout; Phase 5 admits only ids in its adjacency snapshot.

## Interface Deltas
- None.

## State / Failure Deltas
- Removed failures: the two RuntimeErrors above on these passes, and the silent Phase-8 None.
- Unchanged: lookups (`get`, `[]`, `in`) stay on the live pool where they are not part of an iteration;
  a spell removed after a pass copied the pool is still seen by that pass, as it would be if the removal
  landed a moment later.

## Dependency / Ordering
- Independent of other lanes. fable_0's Phase-8 walk file gets a NOTICE before the edit.

## Validation Expectations
- Unit: a pool whose iteration mutates it (a stand-in for a concurrent writer) makes each pass raise on
  the current tree and pass after; a pool entry without a state makes Phase 5 raise before and be excluded
  after; the Phase-8 walk returns a bundle, not None.
- Suites: spellbook unit/component/integration, multithreading, compiler phases on 3.14t and GIL.
