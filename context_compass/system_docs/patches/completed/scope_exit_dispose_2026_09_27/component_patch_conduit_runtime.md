# Component patch: Conduit Runtime - dispose scope and finished pool return (2026-09-27)

## Before
- `__enter__` acquired the conduit lock and `__exit__` released it; nothing was disposed at block exit.
- `cleanup()` of a pooled lesser returned it to the pool again (no state check): two later acquisitions received the
  same object.
- `_prepare_for_pool` disposed the lesser's SpellSpaces, then its own store, then its descendants.
- SpellSpace failures during pool return were logged and the failing space was dropped; an own-store failure raised
  and left the lesser attached and unpooled for a retry.
- Permanent teardown (`_cleanup_lesser_conduit`, `_cleanup_normal_conduit`) logged every failure and raised none;
  ConduitWard logged its children's permanent-cleanup failures.
- Frame teardown swallowed a conduit's cleanup failure with a bare `pass`.

## After
- `__enter__` returns the conduit; `__exit__` calls `cleanup()` and never suppresses the block's exception.
  `enter_lesser_conduit(logger=None, *, name=None)` returns `create_lesser_conduit(logger, name=name)`, documented
  for `with conduit.enter_lesser_conduit() as lesser:`.
- `cleanup()` does nothing for a pooled lesser unless permanent cleanup was requested (`_prepare_for_pool` reads
  the state once and returns for `pooled_lesser`).
- `_prepare_for_pool`: descendants (`ConduitWard._cleanup_children_for_pool(collect_finished=True)`), then
  SpellSpaces, then the own store, then named retirement or detach, local hooks, Meld hooks and pool return; the
  collected disposal failures are raised last as one ExceptionGroup, after the lesser is back in its pool.
- `_cleanup_children_for_pool(collect_finished=False)`: a child that raised but finished (no longer in this ward's
  map) is returned when `collect_finished` (logged otherwise); a child still attached is retained and raised.
- Hot-path offsets (owner condition: scope use costs no more than before): `enter_spellspace` appends to the owned
  thread stack inline, and `_cleanup_spellspaces_for_pool` returns before the drain call when nothing is open or
  registered.
- `ConduitWard.cleanup()` raises its children's permanent-cleanup failures after finishing its own teardown.
- Permanent teardown collects disposal failures (ward, SpellSpaces, own store, cluster facade) and raises them after
  hooks, logger cleanup and field deletes; other failures are logged exactly as before.
- Frame teardown logs a conduit's cleanup failure through the Aether logger and continues.

## Interface deltas
- Public: `__enter__`/`__exit__` semantics (Breaking); new `enter_lesser_conduit`; `cleanup()` may raise an
  ExceptionGroup after finishing (lesser and root).
- Private: `_cleanup_spellspaces_for_pool() -> Optional[List[Exception]]`, `_cleanup_spellspaces() ->
  List[Exception]`, `_cleanup_lesser_conduit() -> List[Exception]`, `_cleanup_normal_conduit() -> List[Exception]`,
  `ConduitWard._cleanup_children_for_pool(collect_finished=False) -> Optional[List[Exception]]`,
  `ConduitWard._clean_up_lesser_conduits_links() -> List[Exception]`.

## State and failure deltas
- A lesser whose disposal failed is pooled (before: dropped Space, or unpooled lesser needing a retry).
- A lesser with an attached (unfinished) descendant or a failed named retirement still stays attached and unpooled.
- A root whose disposal failed is torn down completely and then raises (before: logged only).

## Dependency and ordering
- Descendants, SpellSpaces, own store: the same order permanent teardown already used.
- The pooled-lesser check folds into the state comparison `_prepare_for_pool` already made: no extra read.

## Validation expectations
- Component tests for every behaviour above; conduit, SpellSpace, named-lesser, graduation and creations suites and
  the whole tree green on 3.14t; per-step benchmarks show no regression on lesser create and cleanup.
