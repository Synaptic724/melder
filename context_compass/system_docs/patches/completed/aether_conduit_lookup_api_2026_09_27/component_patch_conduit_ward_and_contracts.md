# Component patch: ConduitWard and Contracts - lineage walk and ownership sweep (2026-09-27)

## Before
- `ConduitWard._get_lesser_conduit` iterated the live `_lesser_conduits` dict of every ward it visited. Links are
  written under the parent's lock and pool detaches under the child's, so the walk could meet "dictionary changed
  size during iteration" on the free-threaded build, or an AttributeError from a child whose ward hard teardown
  had deleted.
- TransferOfOwnership swept roots through Aether's generic `list_conduit_ids` / `get_conduit_by_id`.

## After
- The walk iterates `self._lesser_conduits.copy()` at each level (dict.copy is atomic on 3.14t, 0.2.72 probe) and
  skips a child whose `_conduit_ward` was deleted; the existing `None` leaf check stays.
- TransferOfOwnership calls `list_root_conduit_ids` / `get_root_conduit_by_id`; behaviour unchanged (root-only by
  design).

## Interface / state / failure deltas
- None for callers; the walk can no longer raise RuntimeError or AttributeError from concurrent lifecycle changes.

## Dependency and ordering
- Lands before Aether's LIVE lookup, which delegates to it.

## Validation expectations
- Unit: deterministic mutation-during-walk test (red on 0.2.78), deleted-ward child skipped, existing walk tests
  green. Transfer suites unchanged and green.
