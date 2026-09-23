# Creations purge locking and disposal

## Trigger
Selective disposal changes a concurrent lifecycle boundary and must preserve paired-map mutation.

## Control flow
1. Check live store state.
2. If Spell.existence is unique, acquire Spell._lock.
3. Acquire the selected store's lock and recheck live state.
4. Test key membership, not value truthiness. An absent key returns zero.
5. True pops both entries and counts by Existence. False removes the supplied instance only: compare
   the singleton reference or search the selected many bucket, then retire its disposal metadata.
   Empty many buckets are removed. Absent instances return zero; equality methods are never invoked.
6. Release store lock and, for unique, Spell lock. Retain the detached live object until this point.
7. Dispose only the detached metadata through existing disposal helpers.
8. Release detached references; return count or raise the aggregated disposal failures.

## Errors and rollback
No rollback after disposal begins. Subsequent creations live in new entries and are not touched by
this operation. A callback may register a replacement after locks are released. Nothing extracts
transfer payloads or restores removed state.

## Invariants and idempotence
Meld authorized the caller and chose the store before entry. Creations knows no caller scope.
Unique serializes with Spell-locked creation; other modes serialize with the actual root/local store.
Repeated purge of an absent key returns zero. Unrelated objects and configured method lists survive.

## Non-goals
No global drain, dependency rewrite, scope ownership move, compiler/cache change or new creation lock.

## Validation
Instrument lock order; block actual constructors with events; race two purges; verify disposal can
acquire both locks from another thread; verify callbacks cannot erase a replacement registration.
