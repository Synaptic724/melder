# Component patch: Aether Singleton and AethericFrame Services (cross_object_lock_gaps_2026_10_11)

## Before / after
- `Aether._check_for_spell` and `_get_all_spell_ids` iterated `self._aetheric_frames.items()` live with no Aether
  lock and no plane claim; a frame born (plane FRAME_CREATE claim + Aether lock) or detached (Aether lock) mid-sweep
  made bind raise "dictionary changed size during iteration", and a frame cleaned but not yet detached made it raise
  "AethericFrame has already been cleaned." or AttributeError. After: Aether keeps `_aetheric_frame_view`, a tuple of
  `(name, frame)` pairs republished under the Aether lock by every registry write (`_ensure_frame_locked`,
  `_create_frame`, `_detach_cleaned_frame`; cleared and deleted at teardown). The sweeps read it in one attribute read -
  no per-call copy, the frame-count gate is `len(view)` - and ask each other frame through the cleanup-safe probes.
- New probes `AethericFrame._has_spell_unless_cleaned`, `_find_index_for_spell_unless_cleaned` and
  `_spells_in_index_unless_cleaned`: each takes the frame lock once and answers False / None / an empty set when the
  frame reads cleaned; otherwise has_spell's `in` per Book set, an O(1) `SpellIndex._has_spell_unless_cleaned` per
  index (where `find_index_for_spell` copies every index's member set), and one `set.update` per Book set.
- `AethericFrame.has_spell` and `spells_in_index` repeat their cleaned check under the frame lock, so a racing cleanup
  raises their documented RuntimeError, never AttributeError. `spells_in_index` takes each conjured Book's live
  `_spell_ids` with one `set.update` call instead of copying it element by element, which raised "Set changed size
  during iteration" while that Book bound (Note 10: about 2,000 of 150,000 public reads at -X gil=0, and 0-5 of ~250
  conjures through the conjure preflight); the one-call copy is also about 3x faster.
- `AethericFrame.cleanup` keeps `_lock` (a documented post-cleanup field, as Spell keeps its lock), so the probes and
  the re-checks can take it on a frame another thread has cleaned.

## Interface deltas
New internal probes and `Aether._aetheric_frame_view`; public signatures unchanged; the frame lock survives cleanup.

## State / failure deltas
Bind no longer fails while frames are born or collapse; a frame born after the view was read holds no spell yet, and
a dying frame counts as holding nothing. A conjure no longer fails its preflight while another Book of the frame binds.

## Dependency / ordering
Frame lock -> SpellIndex lock (as `find_index_for_spell`); the Book sets are read with single calls, never under a
Book lock. The view is written only under the Aether lock and read without it.

## Validation expectations
Bind parked in its sweep (as it releases frame-b's lock) while a frame is born and while a frame is cleaned binds
successfully; probes answer like the public reads on a live frame and as empty on a cleaned one; a Book adding to its
id set mid-read leaves both readers returning; the process-wide regime and frame suites stay green.
