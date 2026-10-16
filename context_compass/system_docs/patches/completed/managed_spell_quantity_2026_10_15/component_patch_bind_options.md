# Component patch: managed bind options (managed_spell_quantity_2026_10_15, S2)

Components: ManagedSpellMode (new, spellbook/existence), Bind (`bind`, `_bind_logic`, `sha256_profile`,
`spell_id_inspector`, a new `_normalize_managed_options`), Spell (fields, properties, cleanup), Spellbook.bind /
bind_inactive, Conduit.bind / bind_inactive, SpellBinder, scan_bind / ScanBindMetadata / Scan.scan_module,
SpellCrystal, RestoreEngine and GraftRunner bind replay, RecordVersion. Story: STORY-2026-10-15-managed_bind_options.

## Before / after
- Keywords: `managed_spell_mode=None`, `managed_spell_limit=None`, `managed_spell_timeout_seconds=None` and
  `managed_spell_reset_methods=None`, keyword-only after `resolvable`, on Spellbook.bind, Spellbook.bind_inactive,
  Conduit.bind, Conduit.bind_inactive, Bind.bind, Bind._bind_logic, Bind.spell_id_inspector and scan_bind.
  SpellBinder gains `as_managed_spell_quantity(mode=None, *, limit=None, timeout_seconds=None, reset_methods=None)`
  and sends the options through its passthrough kwargs, as `SpellBinder.bind(..., managed_spell_mode=...)` already
  can. Before: these names landed in `Spell.metadata`.
- Normalization, once, in `Bind._normalize_managed_options`, after the profile is built and before the fingerprint:
  - any other existence: every option must be None -> (None, None, None, ()).
  - managed: class profiles only. Mode: None -> elastic; a member, or its name (lowercased). Limit: elastic defaults
    to 256 (the most idle objects kept); limited_quantity and queue require one; an int >= 1, bool refused.
    Timeout: queue requires a finite number > 0, stored as float; elastic and limited_quantity refuse one. Reset
    names: a list or tuple of non-empty strings, each naming a callable attribute of the class; kept in order, as a
    tuple.
- Fingerprint: `sha256_profile` appends `managed:<mode>:<limit>:<timeout or empty>:<names joined by ",">` after the
  disposal names when a mode is given - only managed bindings. Every other part and the schema prefix are unchanged.
- Spell: four private slots appended after the existing ones (the fast-door slot offsets stay put), read-only
  properties `managed_spell_mode`, `managed_spell_limit`, `managed_spell_timeout_seconds`,
  `managed_spell_reset_methods` (None / None / None / () when not managed) behind `check_cleaned()`, deleted at
  cleanup like `_resolvable`.
- scan: ScanBindMetadata stores the four as given (reset names checked at decoration like disposal names: a list or
  tuple of strings); `__repr__` shows them; `scan_module` replays them into Spellbook.bind;
  `RESERVED_SPELL_METADATA_KEYS` grows from 24 to 28 names.
- SpellCrystal: captures the options only when `existence_name == "managed_spell_quantity"` (mode by name, limit,
  timeout, reset names as a list); `describe()` adds the four keys only for such spells; a `managed_spell_options`
  property; a static `managed_bind_options(payload)` returning the bind keywords a payload carries ({} without them).
- Replay: RestoreEngine `_bind_one_active` / `_bind_one_staged` and GraftRunner `_bind_selected` / `_park_members` /
  `_merge_members` pass `**SpellCrystal.managed_bind_options(crystal)`.
- RecordVersion: 4.1.0 -> 4.2.0 (minor: added keys; 4.1 readers ignore them).

## Interface deltas
- Public: `ManagedSpellMode` (`melder.aether.spellbook.existence.managed_spell_mode`; the package-root export lands
  with S4's set), the four keywords, the four Spell properties, `SpellBinder.as_managed_spell_quantity`.
- Internal: `Bind._normalize_managed_options`, the `sha256_profile` keywords, `SpellCrystal.managed_spell_options`
  and `SpellCrystal.managed_bind_options`.
- Persisted: the four crystal keys, for managed spells only; RecordVersion 4.2.0.

## State / failure deltas
- Bind refuses, before any registry change:
  - an option on another existence - ValueError: "managed_spell_* options apply only to
    Existence.managed_spell_quantity; '<name>' is bound as <existence>. Remove <options> or bind it with
    existence=Existence.managed_spell_quantity."
  - a function, method, lambda or existing object - TypeError: "Existence.managed_spell_quantity binds classes
    only: its pool builds and reuses instances of a class, and '<name>' is <a function or method | an existing
    object>. ..."
  - mode - TypeError for a non-str non-member; ValueError for an unknown name (lists the three).
  - limit - TypeError (not an int, or a bool); ValueError (< 1; missing for limited_quantity or queue).
  - timeout - ValueError (given for elastic or limited_quantity; missing for queue; not finite or <= 0); TypeError
    (not an int or float, or a bool).
  - reset names - TypeError (not a list or tuple, a bare string, an element that is not a string); ValueError (an
    empty name, or a name that is not a callable attribute of the class).
- Non-managed bindings are unchanged: spell ids, Spell values, crystals, records and replays byte-identical. The
  0.2.8241 notch could bind a managed class without options (no option part in its id); from S2 its id carries the
  managed part. No release carries 0.2.8241, and a managed spell has no door before S5.

## Dependency / ordering
- S1 (the member). S3 composes pools from the Spell fields; S4 exports ManagedSpellMode at the package root.

## Validation expectations
- Unit: the normalization table (per-mode defaults, member and name, every refusal with its type and message);
  the fingerprint (one managed part per option, pinned literal ids for all six existing members and both
  `resolvable` values where legal); Spell properties and cleanup; Bind.bind and decorator forwarding;
  spell_id_inspector parity with bind; ScanBindMetadata storage, repr, replay and reserved keys;
  SpellBinder.as_managed_spell_quantity; the Conduit facades forwarding; SpellCrystal capture, describe, property
  and static helper (managed and not); RecordVersion 4.2.0; restore and graft replays passing the options.
- Integration: a real Spellbook binds a managed class (options on the Spell, ids differ per option); a crystallizer
  record and restore keeps the options, for an active and a staged member.
- Both GIL modes; the existing bind, scan, SpellBinder, spell, crystal, record-version, restore and graft suites.
