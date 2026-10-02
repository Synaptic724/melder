# code_description_patch_many_registration

## Metadata
- Patch ID: many_registration_trim_2026_10_01
- Component: Creations and SpellSpace
- Status: active
- Owner: user (agent fable_0)
- Created: 2026-10-01T01:08:13Z
- Updated: 2026-10-01T01:08:13Z

## Trigger Justification
- Why this artifact is required for this component: the change is concurrency-sensitive (a leaf lock, a
  refusal race with `cleanup()`) and touches a lifecycle state machine (registration -> purge/extract/restore
  -> disposal); the control flow of the record and its readers must be fixed before the edit.

## Control-Flow Description (Pseudocode Level)
1. `register_many(key, item, methods)`: `with self._lock:` if not cleaned: `bucket = self._creations.get(key)`;
   if None: `bucket = []`, `self._creations[key] = bucket`, `self._disposable_creations[key] =
   ManyDisposalBucket(bucket, methods)`; `bucket.append(item)`; return. Otherwise (cleaned):
   `_refuse_publish_into_cleaned_store(key, item, has_disposal_methods=True, disposal_methods=methods)`.
2. `add_many_creations(key, item, *, has_disposal_methods, disposal_methods)` -> `_append_many_locked` under
   `_lock`: `bucket = get(key)`; first use creates the list; a non-list raises ValueError; `record =
   self._disposable_creations.get(key)`; if has_disposal_methods: if record is None: if bucket is non-empty
   raise ValueError (mixed declaration) else create the record with `methods or []`; append. Else (no
   disposal): if record is not None raise ValueError (mixed declaration); append.
3. `_dispose_disposable_registry(detached)`: for value in reversed(detached.values()): tuple -> `_attempt_cleanup`;
   `ManyDisposalBucket` -> `_dispose_many_bucket(value)`: for item in reversed(value.entries):
   `_attempt_cleanup((item, value.methods))`.
4. `purge(spell, purge_all, creation)`: locks as today; `_detach_purge_entries` pops the live value and the
   record; dispatch: tuple -> `_attempt_cleanup`, `ManyDisposalBucket` -> `_dispose_many_bucket`.
5. `_detach_single_many_creation(spell_id, creation)`: identity search in the live list; pop; if the list is
   empty: delete both keys; `record = self._disposable_creations.get(spell_id)`; return
   `(1, retired, (creation, record.methods) if record is not None else None)`.
6. `extract_spell_creations(spell_id)`: many: pop the live list and the record (if a `ManyDisposalBucket`);
   one row per object with `disposal_methods = record.methods` when the record exists.
7. `restore_spell_creations(spell_id, rows)`: pops the key first (as today); per many row: create or reuse
   the live list; if `disposable`: record absent and list non-empty -> RuntimeError (mixed); record absent ->
   create `ManyDisposalBucket(list, methods or [])`; append. If not `disposable` and a record exists ->
   RuntimeError (mixed).
8. `cleanup`, `clear_all`, `reset_for_pool`, `reset_for_pool_unlocked`: unchanged.

## Edge/Error and Rollback Semantics
- Edge case 1: concurrent first registrations of one key: both take `_lock`; the second sees the bucket and
  appends (unchanged BUG-073 invariant: live and disposal truth land together - now by construction, since
  the record IS the live list).
- Edge case 2: a build that finishes after `cleanup()`: `_cleaned` is observed under the tombstone lock; the
  methods run outside the lock; RuntimeError chained from the disposal failure(s) (unchanged).
- Error behavior 1: a disposal method that raises contributes one RuntimeError (chained) and the other methods
  and objects still run (unchanged).
- Rollback behavior: revert store + emitters together; keep the generation bump.

## Invariants and Idempotency Expectations
- Invariant 1: `record.entries is self._creations[key]` for every disposal-bearing many key while live.
- Invariant 2: disposal order newest-first across the registry and inside a bucket, declared method order
  inside an object; one disposal per object.
- Idempotency condition 1: `cleanup` and `clear_all` stay idempotent; repeated purge of an absent key returns 0.

## Explicit Non-Goals
- Non-goal 1: lock-free append (trimmed B).
- Non-goal 2: per-thread buckets (S6), batched scope lists (S5).

## Validation Focus Points
- Validation item 1: the single-purge path (the one reader whose logic changes shape, not just type).
- Validation item 2: the mixed-declaration refusals on the public verb and restore.
- Validation item 3: the refusal race with `cleanup()` (existing test, must pass unchanged).

## Context / Handoff Summary
- What changed: nothing yet.
- Remaining unknowns: none.
- Next entrypoint: the task's mapping note, then the owner's confirmation of the exact edit.
