Spell has __slots__: True  _owner_creations is slot: True
plain  (c0 = spells[0]._owner_creations; v = c0._creations.get(sid0))    37.1 ns
S9     (v = c0._creations.get(sid0), c0 global)                          28.9 ns
index  (s0 = spells[0]; c0 = s0._owner_creations ...)                    36.0 ns
attr only (c0 = s0._owner_creations, s0 global)                          32.6 ns
