# Component patch: Rift room lookups by spell_id (find_spell_by_spell_id_2026_10_17)

## Before / after behavior
- `CommandSystem.get_spell_by_id(spell_id)` is renamed `get_spell_by_spell_id(spell_id)` (owner, 2026-10-17:
  "update it all"). The action name the command gate admits and the room memory records, the raw-access label and
  the advertised command list carry the new name. Its steps are unchanged - the published index of the spell_id
  (for the spell ACL), the owner conduit through the frame, the owner Book's lookup - and the Book lookup is exact
  (`find_spell_by_spell_id`, the Spellbook patch), so a spell_id answers its own spell.
- `CommandSystem.get_spell_by_source_id(source_id)`: before, it took the record the source id names and resolved
  the record's index (`_get_spell_by_index_id_locked`), answering the spell the index has active, not the spell
  the record names. Nexus publishes the version an index has active (the room's projection reads the live
  descriptor: a notch swaps the record at once), so in a settled frame the two agree; the exact read no longer
  depends on that. After, the new `_get_spell_by_record_locked(record, frame_name=...)` checks the frame
  and the record's spell-index ACL, resolves the record's owner conduit (`_get_conduit_by_id_locked`, so the
  conduit ACL still applies) and returns the owner Book's `find_spell_by_spell_id(record.spell_id)` - the spell the
  record names, active or parked.
- `StaticCommandSystem.get_spell_by_id(spell_id)` is renamed `get_spell_by_spell_id(spell_id)`. Before, it turned
  the spell_id into its published index and returned the live object of the first published record of that index
  that melds (`owner.meld_existing_spell(spell=record.spell_id)` over every record of the index). After, it tries
  only the records published for that spell_id (one per Book that publishes it), through the shared helper
  `_meld_live_spell_from_records_locked(records, subject=..., frame_name=...)`.
- `StaticCommandSystem.get_spell_by_source_id(source_id)`: before, the record's index, then any record of it;
  after, the record the source id names only, through the same helper.
- `StaticCommandSystem._get_spell_by_index_id_locked` (the index path; same answers) loops through the helper. Its
  messages do not change.
- Exact already, unchanged: `CommandSystem.get_spell_permissions` (delegates to `Conduit.get_spell_permissions`,
  exact through the Conduit patch), `StaticCommandSystem.describe_spell_status_by_id` and
  `describe_spell_status_by_source_id` (records with that spell_id). `describe_spell_status_by_id` keeps its name
  (not asked).

## Interface deltas
- Removed: `CommandSystem.get_spell_by_id`, `StaticCommandSystem.get_spell_by_id`, and the command name
  "get_spell_by_id" in `list_supported_command_methods` of the capability and static rooms (codegen rooms never
  advertised it). Added: `get_spell_by_spell_id(spell_id, *, frame_name=None)` on both, the same signature; no
  alias. Breaking.
- Static room messages on the spell_id and source-id paths name what was asked: "Spell id '<id>' uses unsupported
  static existence '<name>'.", "Spell id '<id>' is not live in frame '<frame>'.", and "Spell '<source_id>' ..."
  (they said "Spell index '<index id>' ..."). The index path keeps "Spell index '<id>' ...".
- Base room `get_spell_by_source_id`: "Spell '<source_id>' has no owner conduit in frame '<frame>'." for an
  ownerless record and "Spell '<source_id>' was not found in the owner spellbook for frame '<frame>'." when the
  owner Book no longer holds that spell_id (before, "Spell index id '<id>' was not found in the owner spellbooks
  for frame '<frame>'."). "Owner conduit for spell '<id>' has no spellbook." as `get_spell_by_spell_id` says it.

## State and failure deltas
- No state. Each path holds the command lock as before; the Book lookup is lock-free; the static melds take what
  `meld_existing_spell` takes. No lock or lock-order edge is added.
- `_DENIED_RAW_RUNTIME_OBJECT_ACCESS_METHOD_NAMES` is empty in every room, so the renamed raw-access label refuses
  nothing; `get_spell_by_source_id` keeps its label.

## Dependency and ordering
- In the same change as the Spellbook patch, so the base room's Book lookups are exact when the rename lands.

## Validation expectations
- Unit (command-system doubles): the base room's `get_spell_by_source_id` returns the Book's spell for the record's
  spell_id, not the spell the record's index has active, and refuses an ownerless record and a spell_id its owner
  Book no longer holds; the static room's `get_spell_by_spell_id` and `get_spell_by_source_id` meld only the named
  spell_id (another record of the same index is never melded) and name what was asked in their refusals; the index
  path's messages are unchanged; both rooms advertise `get_spell_by_spell_id` and not `get_spell_by_id`.
- Integration (a capability room over a dynamic frame, before and after a notch): the room answers the active
  version by its spell_id, its source id and its index; the parked version is not published, so its spell_id and
  source id are refused, never answered with the active version.
- The Rift suites - unit nexus and command-system tests, the static and capability JSON testbenches - GIL off and
  on.
