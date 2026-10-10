# Code description patch: scan_bind capture and scan_module replay (scan_bind_option_parity_2026_10_10)

## Control flow
1. `scan_bind(...)` (import time): refuse a None existence or permissions; normalize the three hook
   groups; normalize disposal names (None, or a list or tuple of str kept as a tuple); refuse reserved
   metadata keys; return the decorator.
2. `decorator(obj)`: build the ScanBindMetadata (its constructor copies the metadata into a private
   dict behind a read-only mapping), set it on obj under `__melder_scan_bind__`, return obj unchanged.
3. `Scan.scan_module(module)`, for each module attribute in dict order: read obj's own `__dict__` entry
   and skip obj when there is none; refuse a value that is not a ScanBindMetadata (TypeError); skip obj
   when this scan already bound it; refuse a re-export (ValueError); call Spellbook.bind with existence,
   permissions, spellframe, binding_name, resolvable, disposal_method_names and `to_bind_kwargs()`
   (hook lists, profile, metadata entries); record obj as bound.

## Edge and error semantics
- Identity, not equality: two distinct objects that compare equal are both bound, and collide when they
  share a binding key. The scan holds a strong reference to every object it bound until it returns, so
  an id() cannot be reused by a new object mid-scan.
- An object without a `__dict__`, or whose `__dict__` is not a dict or mappingproxy, is not a target.
- functools.wraps copies the wrapped `__dict__`, so a wraps-based wrapper carries its own declaration
  and is a target; a bare wrapper is not (unchanged).
- The first name in module dict order is the one used in error messages for an object with aliases.

## Invariants and idempotency
- Neither scan_bind nor the decorator touches a Spellbook; a rescan binds again and collides
  (unchanged).
- Spell cleanup clears `spell.metadata` in place. The decorator's mapping is never that dict, so a later
  scan of the same module, in another book, still forwards the complete metadata.

## Explicit non-goals
- No transactional rollback of a partly scanned module, no recursive discovery, and no decorator-time
  resolvable or Protocol checks (Bind owns them).
