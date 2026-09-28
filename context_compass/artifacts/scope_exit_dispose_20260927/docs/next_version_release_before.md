# Melder 0.2.8202

**Unreleased**

## Melds by name or class take the warm lane

`conduit.meld("Service")` and `conduit.meld(spell=Service)` now reach the compiled builder in one lookup once
the spell has been built once through that call - the warm lane that `meld(spell_id=...)` already had.
`SpellSpace.meld` does the same for scoped melds. The meld door keeps a second success-only registry keyed
by the name string or the class object a caller passes, validated per call by the same guards as the id
entry (door epoch, creation-context identity, live hook and validation flags), so a warm hit returns exactly
what the full lane would.

Nothing changes in what you call or what comes back: the same object for a stored lifetime, a fresh one per
call for `Existence.many`, the same errors, the same override and existing-object behaviour. Melds that pass
`spellframe` or `binding_name`, an instance or a callable as `spell`, dynamic worlds, hooks, and list, tuple
or empty override payloads keep their current path.

Directional numbers on a 2-core VM (Python 3.14t, free-threaded): a warm meld by name of a dependency-free
class 453 -> 269 ns, with one singleton dependency 537 -> 350 ns, at width 4 888 -> 687 ns, a stored singleton
melded directly 333 -> 177 ns; melds by name, by class and by id now cost the same.

## Packaging and documentation

- The packaged system documents (`melder.__components__`, `melder.__architecture__`) are regenerated: the Meld
  Resolution Runtime entry describes the name/class registry, its mint rule, its readers and its invalidation,
  and the meld sequence names both door registries.
- Agent documentation metadata and the whole-repository LLM bundles are rebuilt for 0.2.8202.
