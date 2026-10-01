# Where the warm-meld cost sits (VM 3.14.7t, GIL disabled; ns per call, loop floor 13-14 ns included)

## The three door frames, measured by calling each level directly

| shape | conduit.meld | lane -> executor | executor alone | Conduit.meld frame + prologue | lane frame |
| --- | ---: | ---: | ---: | ---: | ---: |
| solo (bare Root() = 90) | 288 | 133 | 113 | 155 | 20 |
| w1_singleton | 368 | 204 | 184 | 163 | 21 |
| w2_mixed | 508 | 333 | 316 | 175 | 17 |
| wide8_singleton | 755 | 560 | 533 | 195 | 27 |

`Conduit.meld`'s fast path (conduit.py:4527-4576) runs: `_cleaned` check, `type(spell_id) is str`, three None
checks (spell, spellframe, binding_name), `__dynamic_environment__`, `_fast_meld_doors.get(spell_id)`, a 4-tuple
unpack, `_meld_hooks`, `_door_epoch == captured_epoch`, `_creation_context is captured_context`,
`_spellbook_validation_required`, `override is None`, `_no_overrides_instance_executor` load, the existing-object
branch, then the call. The lane (`<creation_context_no_overrides_only_template>`) is 9 instructions: load the
executor from a cell and call it.

## One singleton site, in isolation (above a 13 ns call floor; the executor's real `spells`/`sid0` globals)

| read pattern | ns |
| --- | ---: |
| emitted: `c0 = spells[0]._owner_creations; v0 = c0._creations.get(sid0); if v0 is None: ...` | 23 |
| bound `dict.get` constant + None check | 15 |
| closed-over instance + one epoch int-compare (PGO proper) | 7 |
| closed-over instance, no guard | 1 |

So a singleton site costs 23 ns as emitted; a bound get recovers ~8 ns, a guarded constant ~16 ns. The
"~45 ns per singleton read" figure quoted from the composite runs was an over-attribution: the composite
delta also carried the executor's local stores and argument shuffling.
