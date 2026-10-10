# Architecture patch: scan_bind_option_parity_2026_10_10

## Objective and non-goals
- Objective: `scan_bind` declares everything `Spellbook.bind` accepts for a target - the native
  `resolvable` capability, per-target `disposal_method_names` and application metadata keywords - and
  replays them through the one bind pipeline, so a scanned registration matches a direct bind of the
  same target. A scan registers only objects that carry their own declaration, once per object.
- Non-goals: no change to Spellbook.bind, Bind, Spell or bind validation; permissions stay required on
  scan_bind (direct bind defaults to create); no package traversal; no change to transaction or
  atomicity semantics (a failed scan keeps the registrations it made, as before - now documented); no
  change to the internal-bind guard.

## Changed components
- Scan-Bind Module Scanner (`src/melder/aether/spellbook/bind/scan.py`): `scan_bind`,
  `ScanBindMetadata`, `Scan.scan_module`.
- Documentation only: the `Spellbook.scan` docstring (scans are not atomic) and the README
  "Declarative Binding by Module" example (it omitted the required permissions).

## Invariants
- One pipeline: a scanned target reaches Spellbook.bind with the same native arguments a direct bind
  takes; the scanner adds no binding rule of its own, only decorator-time argument shape checks.
- Own declaration only: a module attribute is a scan target only when its own `__dict__` holds the
  ScanBindMetadata. Inheritance, instances of decorated classes, metaclass attributes and
  `__getattr__` fallbacks never make a target.
- One registration per object per scan: other names for an object this scan already bound are
  skipped; distinct objects with colliding binding keys, and later rescans, still raise.
- Metadata storage is shallow and immutable at the outer level: the decorated object carries a
  read-only mapping, values are borrowed by identity, and each bind receives a fresh dict.
- Metadata keys that Spellbook.bind, Bind or Spell take natively are refused at decoration, so
  application metadata can never collide with or shadow a native argument.

## Interface deltas
- `scan_bind(..., resolvable: bool = True, disposal_method_names: Optional[Sequence[str]] = None,
  **spell_metadata: Any)`. New decoration-time TypeErrors: a disposal-name group that is not a list or
  tuple of str; a reserved metadata key. A non-bool resolvable fails at scan time from Bind, exactly as
  a direct bind fails.
- `ScanBindMetadata` (internal, not exported) is an immutable slotted class instead of a frozen
  dataclass, with new attributes `resolvable`, `disposal_method_names` and `spell_metadata`;
  `to_bind_kwargs()` also returns the metadata entries.
- Behaviour (Breaking): an undecorated subclass of a decorated class, and a module-level instance of
  one, are no longer registered by a scan; a second name for an object already bound in the same scan
  no longer raises "Spell ID collision".

## Migration order
1. Patch docs. 2. Failing tests (unit and component). 3. scan.py. 4. Spellbook.scan docstring, README,
src_components and src_architecture, graph descriptors. 5. Notch 0.2.8228 and the release note.
6. Generated assets and llm_support bundles, last.

## Rollback
- Restore scan.py from 66939dfe8 and drop the two new test files; the documentation reverts with them.
  No recorded artifact, spell-id rule or cache format changes, so no data migration either way.

## Ticket coverage matrix
| patch section | ticket |
| --- | --- |
| all | tickets/tasks/2026-10-08_restore_scan_bind_option_parity_task.md |
