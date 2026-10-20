# Component patch: Aether Singleton and AethericFrame Services (cross_object_lock_gaps_2026_10_11)

## Before / after
- Aether._check_for_spell and _get_all_spell_ids iterated self._aetheric_frames.items() live with no Aether lock and
  no plane claim; a frame born (plane FRAME_CREATE claim + Aether lock) or detached (Aether lock) mid-sweep made
  bind raise "dictionary changed size during iteration", and a frame cleaned but not yet detached made it raise
  "AethericFrame has already been cleaned." or AttributeError. After: both walk list(self._aetheric_frames.items())
  and probe each other frame with AethericFrame._has_spell_unless_cleaned / _find_index_for_spell_unless_cleaned /
  _spells_in_index_unless_cleaned, which answer False / None / an empty set for a cleaned frame.
- AethericFrame.has_spell and spells_in_index repeat their cleaned check under the frame lock.

## State / failure deltas
Bind no longer fails while frames are born or collapse. A frame born after the snapshot is not swept (it holds no
spell yet); a dying frame counts as holding nothing.

## Validation expectations
Forced interleavings (frame born mid-sweep, frame cleaned mid-sweep) bind successfully; probes on a cleaned frame;
the process-wide regime and frame suites green.
