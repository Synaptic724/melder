# Component patch: Scan-Bind Module Scanner (scan_bind_option_parity_2026_10_10)

## Before / after behavior
- Before: scan_bind accepted existence, permissions, spellframe, binding_name, profile and three hook
  lists; resolvable, disposal_method_names and metadata keywords raised TypeError ("unexpected keyword
  argument"). A frozen dataclass, ScanBindMetadata, held the declaration. scan_module found it with
  getattr, so an undecorated subclass, a module-level instance of a decorated class, a metaclass
  attribute or a `__getattr__` fallback looked decorated - it was bound, collided, or aborted the scan
  as "corrupted" - and a second name for the same object was bound twice ("Spell ID collision").
- After: scan_bind takes resolvable, disposal_method_names and `**spell_metadata`, and the scanner
  forwards them to Spellbook.bind beside the existing arguments. ScanBindMetadata is an immutable
  slotted class. The scanner reads the object's own `__dict__` and binds each object once per scan.

## Interface deltas
- As in the architecture patch: three new scan_bind parameters, two new decoration-time TypeErrors,
  three new ScanBindMetadata attributes, metadata entries in `to_bind_kwargs()`.

## State and failure deltas
- New decoration-time TypeErrors: disposal_method_names that is not a list or tuple of str; reserved
  metadata keys, named in the message. Unchanged: None existence or permissions -> ValueError; hook
  shape TypeErrors; re-export ValueError; corrupted metadata TypeError; collisions RuntimeError.
- New scan-time TypeErrors come from Bind (non-bool resolvable; a Protocol target left resolvable).
- A failed scan keeps the registrations it made before the failure, pre-conjure and post-conjure,
  with or without an outer bind window (unchanged; now documented and pinned by tests).

## Dependency and ordering
- The reserved key set is the parameter names of Spellbook.bind, Bind.bind, Bind._bind_logic and
  Spell.__init__ plus the three hook keys; a unit test derives it from those signatures so a new
  native parameter cannot slip through as metadata.

## Validation expectations
- Unit: decoration contract (defaults, storage, snapshot isolation, immutability, validation, reserved
  keys), discovery (own metadata, subclasses, instances, proxies, aliases, wraps, re-exports, corrupted
  metadata, collisions, rescans) and direct-versus-scan parity (existence, permissions, frame, binding
  name, profile, resolvable, disposal order, metadata, spell_id).
- Component: Book registration callbacks once per actual registration (new options, aliases);
  post-conjure scan in a dynamic world with the new options; failure boundaries pre-conjure and
  post-conjure (scan's own window and an outer window).
- The existing scan, bind, hook and resolvable tiers stay green with the GIL disabled.
