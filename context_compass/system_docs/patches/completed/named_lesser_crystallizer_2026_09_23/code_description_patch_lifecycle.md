# Named emission and restoration ordering

## Creation
Within named attachment's existing parent/child window: link the child, publish Cloud under its short
leaf lock, then emit a detached structural twin after the Cloud lock releases. A record failure uses
the existing named-acquisition cleanup path; no successful return with silently missing publication.
Post-created hooks remain after attachment. Ancestor reads capture value state, never owned objects.

## Retirement
Keep the single _name conditional in _prepare_for_pool. Named return first completes descendant
cleanup, then removes the recorded conduit, unregisters Cloud, clears name and detaches itself.
Own Space/Creations disposal remains first; idle publication remains last. Record failure keeps the
named scope attached for retry. Child cleanup failures aggregate before ancestor detach/pool return,
including unnamed ancestry; the existing no-children Ward fast path stays unchanged. Hard lesser
teardown uses the same named-only record removal with established best-effort resource cleanup.
Normal teardown removes its recorded id before Book cleanup, after child/store teardown. This covers
failed promotion whose runtime attached a new Book but whose record still names the old Book.

## Promotion
Successful normal twin emission replaces the same id with its new Book/root role and drops supporting
ancestry. Pre-attachment rollback leaves the old lesser twin; post-attachment cleanup removes its id
regardless of which Book the last emitted twin named. Old Book removal cannot evict the new root twin.

## Fold and Replay
Fold named records/tombstones first. Expand supporting ancestry from only the surviving named rows,
validate against explicit named/root twins, and order parents first. No independently retained support
row can leak after its final named descendant is removed. Seal exports are recursively detached.
Build each Book/root once, then its lesser hierarchy with fresh ids. Record each scope immediately in
the existing rollback stack before building later children; report name-loss explicitly. Lesser policy
stays default by runtime contract; malformed nondefault child/support policies refuse at admission.

## Practical Scope
No new work on unnamed return or Meld; no blanket dynamic transactions for scope cycles. Live loads
require scope lifecycle quiescence. Hook callables and prior created objects are not serialized.
