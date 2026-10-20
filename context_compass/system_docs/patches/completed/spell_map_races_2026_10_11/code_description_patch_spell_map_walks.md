# Code description patch: spell-map walks (spell_map_races_2026_10_11)

## Control flow
1. bind: claim_lookup (unchanged, outside) -> `with self._lock:` publish _lookup_spells[key], _spells[index],
   _register_owned_spell_id (re-enters the RLock) -> the rest of bind unchanged.
2. Unlocked walkers: `for x in list(m.values())` / `list(m.items())` / `list(m)`; lead spell = first element of a
   list(values()) snapshot, or [] when empty.
3. has_spell: check_cleaned(); with lock: check_cleaned(); membership. Probe: with lock: False if cleaned else
   membership.
4. Id lookups: Spellbook.find_spell_by_id for lineage resolution; the Aether owner lookup behind the Conduit
   spell lookups is unchanged and raises for a miss.

## Edge semantics
A snapshot walk sees the map at one instant: a spell bound after the snapshot is not visited, one removed after it
may be visited (its probes answer False once cleaned). Answers equal today's on a quiet Book.

## Non-goals
No reader locks; no change to frame-registry walks or to the Aether frame sweep; no cache format change.
