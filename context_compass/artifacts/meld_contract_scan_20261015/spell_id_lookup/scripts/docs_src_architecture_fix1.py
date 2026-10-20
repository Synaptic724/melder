"""
src_architecture for fix #1 (find_spell_by_spell_id_2026_10_17): exact-once edits, all or nothing.

Usage: python docs_src_architecture_fix1.py <repo_root> [--check]

The boundary list, the operational invariants, the failure modes, the C1 code map (the 11 changed files, measured
from disk at run time) and the handoff summary. Numeric citations were remapped beforehand by
remap_citations.py; the index is regenerated after this script. Every old text is an anchor that must occur exactly
once; a code-map entry spans from its `- path:` line through the newline before the next one.
"""
import datetime
import pathlib
import sys

DOC = "context_compass/system_docs/src_architecture.md"

BOUNDARY_SENTENCE = (
    "  Book's spell or target index, a non-member or only member on removal). `get_spell_by_id` and `find_spell_by_id`\n"
    "  still answer a parked spell_id with the index's active member, so a parked spell is named by its spell_id.\n",
    "  Book's spell or target index, a non-member or only member on removal). Since 0.2.8253 the spell_id lookups\n"
    "  (`get_spell_by_spell_id`, `find_spell_by_spell_id`) answer a parked spell_id with that parked spell, so a\n"
    "  parked version can be named by its spell_id or by the Spell they return.\n",
)

BOUNDARY_BULLET = (
    "- `Spellbook.conjure(...)` for building a root Conduit.\n",
    "- `Spellbook.find_spell_by_spell_id(spell_id)` and `Conduit.get_spell_by_spell_id(spell_id,\n"
    "  aetheric_frame_name=\"default\")` (0.2.8253; renamed from `find_spell_by_id` and `get_spell_by_id`, with no\n"
    "  alias): the spell a spell_id names - the active version, else the parked one - or None from the Book, and\n"
    "  ValueError from the Conduit for a spell_id no conduit of the frame claims. A spell_id and a SpellIndex are\n"
    "  separate things (owner ruling, 2026-10-17): the spell an index has active is a lookup by the index's id\n"
    "  (`Conduit.get_spell_by_index_id`), never the answer to a spell_id. `Conduit.get_spell_permissions(spell_id)`\n"
    "  answers the permissions that version was bound with. The Rift rooms' `get_spell_by_spell_id(spell_id, *,\n"
    "  frame_name=None)` (renamed from `get_spell_by_id`, its command name and advertised name with it) and\n"
    "  `get_spell_by_source_id` answer the spell their argument names - a capability or codegen room the Spell, a\n"
    "  static room its live object - or raise.\n"
    "  EVIDENCE:\n"
    "  - `src/melder/aether/spellbook/spellbook.py:Spellbook.find_spell_by_spell_id`,\n"
    "    `Spellbook._get_spell_by_id_via_aether`\n"
    "  - `src/melder/aether/conduit/conduit.py:Conduit.get_spell_by_spell_id`, `Conduit.get_spell_permissions`\n"
    "  - `src/melder/nexus/rift/command_system/command_system.py:CommandSystem.get_spell_by_spell_id`,\n"
    "    `CommandSystem.get_spell_by_source_id`\n"
    "  - `src/melder/nexus/rift/command_system/static_command_system.py:StaticCommandSystem.get_spell_by_spell_id`,\n"
    "    `StaticCommandSystem.get_spell_by_source_id`\n"
    "- `Spellbook.conjure(...)` for building a root Conduit.\n",
)

INVARIANT = (
    "## Operational Invariants\n"
    "- One version, one copy (2026-10-16, 0.2.8251;",
    "## Operational Invariants\n"
    "- Lookup by spell_id is exact (2026-10-17, 0.2.8253; the owner's rule: a spell_id - the SHA256 `bind` and\n"
    "  `bind_inactive` return - and a SpellIndex - its ULID - are separate things; sharing an index follows whatever\n"
    "  spell it has active, sharing a spell by spell_id is exactly that spell, and a spell_id lookup never answers with\n"
    "  the spell its index has active): `Spellbook.find_spell_by_spell_id(spell_id)` returns the Spell bound under the\n"
    "  spell_id - one read of `_spells_by_id` (active versions), else one of `_inactive_spells` (parked) - or None, and\n"
    "  reads no index; its predecessor `find_spell_by_id` returned, for a parked spell_id, the spell the parked\n"
    "  version's index had active. `Conduit.get_spell_by_spell_id` returns what the owner Book's lookup returns (Aether\n"
    "  names the owner conduit; `Spellbook._get_spell_by_id_via_aether`), and `Conduit.get_spell_permissions` the\n"
    "  permissions that version was bound with. A caller that needs the spell an index has active takes an explicit\n"
    "  index step: it finds the member by spell_id, reads its index (`Spell._spell_index_unless_cleaned`) and asks for\n"
    "  the index's active spell - the owner Book's `_find_spell` in the contract dependency walk and its preflight\n"
    "  (`ConduitWard._link_spell_dependencies`, `_preflight_contract_dependency_collisions`), the conduit's\n"
    "  `get_spell_by_index_id` in `Conduit._resolve_transfer_spell` and `ConduitWard._transfer_spell_ownership`, the\n"
    "  source Book's `_spells` under its lock in `TransferOfOwnership._resolve_spell` and\n"
    "  `_transfer_owned_dependencies`, the member's own Book in `_deps_resolvable_on_target`. That is what the old\n"
    "  lookup returned for every spell_id of an owned spell, so a transfer, a dependency grant and their checks answer\n"
    "  as before, and a parked Spell object never reaches a transfer. The grant check\n"
    "  (`ConduitWard._check_spell_id_and_spell`) resolves exactly, so a grant or ungrant by a parked spell_id proceeds\n"
    "  (a grant parks the copy on the borrower), and the outbound half of a contract listing names each granted\n"
    "  version's own Spell. The Rift rooms follow: a lookup by spell_id or by a source id answers that spell - a\n"
    "  capability or codegen room through the owner Book's lookup (`CommandSystem._get_spell_by_record_locked` for a\n"
    "  source id), a static room by melding only the records published for that spell_id\n"
    "  (`StaticCommandSystem._meld_live_spell_from_records_locked`, which the index path shares) - and only a lookup by\n"
    "  spell index id answers what the index has active. Nexus publishes the version an index has active, so a room\n"
    "  refuses a parked version's spell_id or source id rather than answering another version. Locks: the lookup takes\n"
    "  none (two single-key dict reads; a disposal racing it returns the Spell it read, borrowed, or misses once the\n"
    "  spell_id has left the map); an explicit index step reads the member's index under the member's own spell lock,\n"
    "  releases it, then takes one Book lock alone, at a call site that holds no other lock, so no lock-order edge is\n"
    "  added. Nothing persisted, cached or emitted reads the lookups, so no cache generation or record version moves.\n"
    "  Not changed (the owner's to decide): `Spellbook._find_contracted_spell_by_id`, the contract row `Detail`,\n"
    "  `ConduitWard._get_spell_in_contracts`, `_get_all_spells_in_contracts` and `_validate_contracts_and_define`, and\n"
    "  `Meld._current_in_pool` still resolve a spell_id through its index, and three paths file a borrowed copy under\n"
    "  `spell_index.selected_spell_id`.\n"
    "  EVIDENCE: `src/melder/aether/spellbook/spellbook.py:Spellbook.find_spell_by_spell_id`,\n"
    "  `Spellbook._get_spell_by_id_via_aether`, `src/melder/aether/conduit/conduit.py:Conduit.get_spell_by_spell_id`,\n"
    "  `Conduit.get_spell_permissions`, `Conduit._resolve_transfer_spell`,\n"
    "  `src/melder/aether/conduit/conduit_ward/conduit_ward.py:ConduitWard._link_spell_dependencies`,\n"
    "  `ConduitWard._preflight_contract_dependency_collisions`, `ConduitWard._transfer_spell_ownership`,\n"
    "  `ConduitWard._check_spell_id_and_spell`, `ConduitWard._get_spells_in_contract_by_conduit`,\n"
    "  `src/melder/aether/conduit/conduit_ward/transfer/transfer_of_ownership.py:TransferOfOwnership._resolve_spell`,\n"
    "  `TransferOfOwnership._deps_resolvable_on_target`, `TransferOfOwnership._transfer_owned_dependencies`,\n"
    "  `src/melder/aether/spellbook/spell.py:Spell._spell_index_unless_cleaned`,\n"
    "  `src/melder/nexus/rift/command_system/command_system.py:CommandSystem._get_spell_by_record_locked`,\n"
    "  `CommandSystem.get_spell_by_spell_id` and\n"
    "  `src/melder/nexus/rift/command_system/static_command_system.py:StaticCommandSystem._meld_live_spell_from_records_locked`.\n"
    "- One version, one copy (2026-10-16, 0.2.8251;",
)

SMALL = [
    ("- Updated: 2026-10-16\n", "- Updated: 2026-10-17\n"),
    ("  and the contract listing resolves ids through the Book (`_find_contracted_spell_by_id`, `find_spell_by_id`), never\n",
     "  and the contract listing resolves ids through the Book (`_find_contracted_spell_by_id`, `find_spell_by_id` -\n"
     "  `find_spell_by_spell_id` since 0.2.8253), never\n"),
    ("  contracted-spell lookup and the transfer impact walk. `Conduit.get_spell_permissions` and\n"
     "  `CommandSystem.get_spell_by_id` resolve lineages through `Spellbook.find_spell_by_id` instead of walking.\n",
     "  contracted-spell lookup and the transfer impact walk. `Conduit.get_spell_permissions` and\n"
     "  `CommandSystem.get_spell_by_id` resolve through `Spellbook.find_spell_by_id` instead of walking (renamed\n"
     "  `get_spell_by_spell_id` and `find_spell_by_spell_id`, and exact, in 0.2.8253).\n"),
    ("- Lookup by version id (2026-10-11, 0.2.8229): `Spellbook.find_spell_by_id` answers from the Book's id maps and\n",
     "- Lookup by version id (2026-10-11, 0.2.8229; SUPERSEDED in part at 0.2.8253 by the exact lookup above: renamed\n"
     "  `find_spell_by_spell_id`, its parked branch returns the parked Spell and reads no index; the id maps, the\n"
     "  absence of a Book lock and the concurrency answers below survive, per spell_id rather than per lineage):\n"
     "  `Spellbook.find_spell_by_id` answers from the Book's id maps and\n"),
    ("  EVIDENCE: `src/melder/aether/spellbook/spellbook.py:Spellbook.find_spell_by_id`,\n"
     "  `src/melder/aether/spellbook/spell.py:Spell._spell_index_unless_cleaned`, `Spell.cleanup` and\n",
     "  EVIDENCE: `src/melder/aether/spellbook/spellbook.py:Spellbook.find_spell_by_spell_id` (`find_spell_by_id` until\n"
     "  0.2.8253), `src/melder/aether/spellbook/spell.py:Spell._spell_index_unless_cleaned`, `Spell.cleanup` and\n"),
    ("  `conduit.get_spell_by_id('<id>').spell_index`, or move it with add_to_spell_index first). A refusal before the\n"
     "  transaction changes nothing; one inside the window (another operation moved the target after the first check)\n"
     "  ends the transaction as failed, and the Spellbook is never called.\n",
     "  `conduit.get_spell_by_spell_id('<id>').spell_index` - `get_spell_by_id` until 0.2.8253 - or move it with\n"
     "  add_to_spell_index first). A refusal before the transaction changes nothing; one inside the window (another\n"
     "  operation moved the target after the first check) ends the transaction as failed, and the Spellbook is never\n"
     "  called.\n"),
    ("- A notch to the Spell `get_spell_by_id` or `find_spell_by_id` returns for a parked spell_id is a silent no-op, by\n"
     "  their contract: they answer a parked spell_id with the index's active member. Name a parked version by `spell_id=`.\n"
     "  EVIDENCE: `src/melder/aether/spellbook/spellbook.py:Spellbook.find_spell_by_id`.\n",
     "- A notch to the Spell the spell_id lookup returns for a parked spell_id moves the index to it (fixed in\n"
     "  0.2.8253): `get_spell_by_spell_id` and `find_spell_by_spell_id` return the parked version itself. Through\n"
     "  0.2.8252 `get_spell_by_id` and `find_spell_by_id` returned the index's active member, so that notch was a\n"
     "  silent no-op.\n"
     "  EVIDENCE: `src/melder/aether/spellbook/spellbook.py:Spellbook.find_spell_by_spell_id`.\n"),
    ("- `Conduit.get_spell_by_id` and `Conduit.get_conduit_by_spell_id` raise ValueError \"Spell version <id> not found in\n"
     "  any conduit.\" for an id no conduit in the frame claims - unknown or removed, bound in another frame, its owner\n",
     "- `Conduit.get_spell_by_spell_id` (`get_spell_by_id` until 0.2.8253) and `Conduit.get_conduit_by_spell_id` raise\n"
     "  ValueError \"Spell version <id> not found in any conduit.\" for an id no conduit in the frame claims - unknown or\n"
     "  removed, bound in another frame, its owner\n"),
    ("- `Spellbook.find_spell_by_id`, and `Conduit.get_spell_by_id` through it, no longer fail while other spells are\n",
     "- `Spellbook.find_spell_by_id`, and `Conduit.get_spell_by_id` through it (`find_spell_by_spell_id` and\n"
     "  `get_spell_by_spell_id` since 0.2.8253), no longer fail while other spells are\n"),
    ("  \"SpellIndex has already been cleaned.\", or returned None for a spell that was still registered. A parked\n"
     "  version disposed during a lookup now answers None instead of raising.\n"
     "  EVIDENCE: `src/melder/aether/spellbook/spellbook.py:Spellbook.find_spell_by_id`.\n",
     "  \"SpellIndex has already been cleaned.\", or returned None for a spell that was still registered. A parked\n"
     "  version disposed during a lookup answered None instead of raising (since 0.2.8253 it answers the Spell the\n"
     "  lookup read, borrowed, or None once its spell_id has left the map).\n"
     "  EVIDENCE: `src/melder/aether/spellbook/spellbook.py:Spellbook.find_spell_by_spell_id`.\n"),
]

FAILURES = (
    "## Failure Modes and Error Paths\n",
    "## Failure Modes and Error Paths\n"
    "- Breaking (0.2.8253): `Spellbook.find_spell_by_id` and `Conduit.get_spell_by_id` are gone, with no alias (a call\n"
    "  raises AttributeError); `find_spell_by_spell_id` and `get_spell_by_spell_id` take the same arguments. Their\n"
    "  answer for a parked spell_id changed: the parked spell itself, where the old pair answered the spell its index\n"
    "  had active (English for French's spell_id). `find_spell_by_spell_id` also answers a version split off by\n"
    "  `remove_from_spell_index` into an index with no active spell (it was None); the Conduit lookup still raises \"not\n"
    "  found in any conduit\" for such a version, because the index the move mints is missing from the frame registry\n"
    "  (pre-existing; STORY-2026-10-17-minted_index_missing_from_frame_registry). `Conduit.get_spell_permissions`\n"
    "  answers that version's own permissions (it was the active version's). The Rift rooms' command\n"
    "  `get_spell_by_id` is `get_spell_by_spell_id`, advertised under that name, and `get_spell_by_source_id` answers\n"
    "  the spell its source id names. To reach the version an index has active, ask the index:\n"
    "  `conduit.get_spell_by_index_id(conduit.get_spell_by_spell_id(spell_id).spell_index.id)`.\n"
    "  EVIDENCE: `src/melder/aether/spellbook/spellbook.py:Spellbook.find_spell_by_spell_id`,\n"
    "  `src/melder/aether/conduit/conduit.py:Conduit.get_spell_by_spell_id`, `Conduit.get_spell_permissions` and\n"
    "  `src/melder/nexus/rift/command_system/command_system.py:CommandSystem.get_spell_by_spell_id`.\n"
    "- A grant or ungrant by a parked spell_id no longer refuses (fixed in 0.2.8253): `add_spell_to_contract(spell_id=...)`\n"
    "  and `remove_spell_from_contract(spell_id=...)` raised RuntimeError \"Provided spell_id '<parked>' does not match\n"
    "  inspected ID '<active>'.\" because the lookup answered the active version; a grant now parks the copy on the\n"
    "  borrower, as a grant of the Spell object does. The inbound half of a contract listing still answers a parked\n"
    "  grant through its index (`Spellbook._find_contracted_spell_by_id`: the index's active copy, or nothing),\n"
    "  pending with the owner.\n"
    "  EVIDENCE: `src/melder/aether/conduit/conduit_ward/conduit_ward.py:ConduitWard._check_spell_id_and_spell` and\n"
    "  `ConduitWard._get_spells_in_contract_by_conduit`.\n"
    "- An ownership transfer handed a spell_id still moves the index the spell_id belongs to, resolved to the version\n"
    "  the index has active on the source (0.2.8253). A spell_id the source conduit cannot resolve to an active spell\n"
    "  of that index - another conduit's spell whose index the source neither owns nor borrows - now refuses at\n"
    "  resolution: RuntimeError \"[CONDUIT] Transfer-ownership could not resolve the source spell on this conduit.\"\n"
    "  (`Conduit`) or \"Could not resolve spell for ownership transfer.\" (`ConduitWard`), where the old lookup handed\n"
    "  the other conduit's spell on and the transfer refused it later with \"Source conduit does not own the spell.\".\n"
    "  `TransferOfOwnership` constructed with a spell_id it cannot resolve raises RuntimeError \"Unable to resolve spell\n"
    "  for transfer: the source conduit's Spellbook has no active spell in the index of spell_id '<id>'.\" from its\n"
    "  preflight; it failed with AttributeError on the None it handed to its ownership check.\n"
    "  EVIDENCE: `src/melder/aether/conduit/conduit.py:Conduit._resolve_transfer_spell`,\n"
    "  `src/melder/aether/conduit/conduit_ward/conduit_ward.py:ConduitWard._transfer_spell_ownership` and\n"
    "  `src/melder/aether/conduit/conduit_ward/transfer/transfer_of_ownership.py:TransferOfOwnership._resolve_spell`.\n"
    "- A static Rift room names what was asked when a spell_id or source-id lookup refuses (0.2.8253): ValueError\n"
    "  \"Spell id '<id>' uses unsupported static existence '<name>'.\" and \"Spell id '<id>' is not live in frame\n"
    "  '<frame>'.\", and \"Spell '<source_id>' ...\" for a source id (they said \"Spell index '<index id>' ...\"; the index\n"
    "  path keeps that wording). The base room's source-id lookup raises \"Spell '<source_id>' has no owner conduit in\n"
    "  frame '<frame>'.\" and \"Spell '<source_id>' was not found in the owner spellbook for frame '<frame>'.\" (it said\n"
    "  \"Spell index id '<id>' was not found in the owner spellbooks for frame '<frame>'.\").\n"
    "  EVIDENCE:\n"
    "  - `src/melder/nexus/rift/command_system/static_command_system.py:StaticCommandSystem._meld_live_spell_from_records_locked`\n"
    "  - `src/melder/nexus/rift/command_system/command_system.py:CommandSystem._get_spell_by_record_locked`\n",
)

CODE_MAP = {
    "src/melder/aether/spellbook/spellbook.py": (
        "    spell_id (0.2.8251).\n",
        "    spell_id (0.2.8251); `find_spell_by_id` renamed `find_spell_by_spell_id` and exact - a parked spell_id\n"
        "    answers its own spell, no index read (0.2.8253).\n"),
    "src/melder/aether/conduit/conduit.py": (
        "    linked peer's parked copy of the incoming version is made active again (`_activate_borrowed_spell`,\n"
        "    0.2.8250).\n",
        "    linked peer's parked copy of the incoming version is made active again (`_activate_borrowed_spell`,\n"
        "    0.2.8250); `get_spell_by_id` renamed `get_spell_by_spell_id` and exact, `get_spell_permissions` per version,\n"
        "    `_resolve_transfer_spell` takes the explicit index step (0.2.8253).\n"),
    "src/melder/aether/conduit/conduit_ward/conduit_ward.py": (
        "    to its copy (0.2.8250).\n",
        "    to its copy (0.2.8250); the dependency walks and the transfer's spell_id handle take the explicit index step,\n"
        "    the grant check and the outbound listing resolve exactly (0.2.8253).\n"),
    "src/melder/aether/conduit/conduit_ward/transfer/transfer_of_ownership.py": (
        "    (0.2.8248).\n",
        "    (0.2.8248); `_resolve_spell`, `_deps_resolvable_on_target` and `_transfer_owned_dependencies` take the\n"
        "    explicit index step from a spell_id (0.2.8253).\n"),
    "src/melder/aether/spellbook/bind/spell_index.py": (
        "    `_is_selected_unless_cleaned`, the release registry's selected-version probe (0.2.8244).\n",
        "    `_is_selected_unless_cleaned`, the release registry's selected-version probe (0.2.8244); `update` and\n"
        "    `has_spell` say a spell_id names its own spell, not the head (0.2.8253).\n"),
    "src/melder/aether/spellbook/spell.py": (
        "    managed version's pool (0.2.8242-0.2.8243).\n",
        "    managed version's pool (0.2.8242-0.2.8243); `_spell_index_unless_cleaned` names its readers, the explicit\n"
        "    index steps among them (0.2.8253).\n"),
    "src/melder/aether/spellbook/spell_compiler/validation/strategies/ambiguous_provider_strategy.py": (
        "  note: Phase-4 refusal of a single typed parameter with several providers; names every candidate's address (0.2.8224).\n",
        "  note: Phase-4 refusal of a single typed parameter with several providers; names every candidate's address\n"
        "    (0.2.8224); describes candidates through `find_spell_by_spell_id` (0.2.8253).\n"),
    "src/melder/crystallizer/crystal_loader_system/graft_runner.py": (
        "  note: spell-index graft driver; the same frame hydration as the restore engine (0.2.8222); replays the managed\n"
        "    options (0.2.8242).\n",
        "  note: spell-index graft driver; the same frame hydration as the restore engine (0.2.8222); replays the managed\n"
        "    options (0.2.8242); calls `find_spell_by_spell_id`, its adoption TRIAGE comment corrected (0.2.8253).\n"),
    "src/melder/crystallizer/crystal_loader_system/restore_engine.py": (
        "    replays the managed options through bind (0.2.8242).\n",
        "    replays the managed options through bind (0.2.8242); calls `find_spell_by_spell_id` (0.2.8253).\n"),
    "src/melder/nexus/rift/command_system/command_system.py": (
        "  note: shared room-local command surface.\n",
        "  note: shared room-local command surface; `get_spell_by_id` renamed `get_spell_by_spell_id` (command name,\n"
        "    raw-access label, advertised list), `get_spell_by_source_id` exact through `_get_spell_by_record_locked`\n"
        "    (0.2.8253).\n"),
    "src/melder/nexus/rift/command_system/static_command_system.py": (
        "  note: static command posture; treats a managed spell like `many` (0.2.8243).\n",
        "  note: static command posture; treats a managed spell like `many` (0.2.8243); `get_spell_by_spell_id` (renamed)\n"
        "    and `get_spell_by_source_id` meld only the named version through `_meld_live_spell_from_records_locked`,\n"
        "    which the index path shares (0.2.8253).\n"),
}

HANDOFF = (
    "## Context / Handoff Summary\n\n",
    "## Context / Handoff Summary\n\n"
    "2026-10-17 lookup by spell_id is exact (0.2.8253; the owner's rule: a spell_id and a SpellIndex are separate\n"
    "things, and a spell_id lookup never answers with the spell its index has active): `Spellbook.find_spell_by_id`\n"
    "and `Conduit.get_spell_by_id` are renamed `find_spell_by_spell_id` and `get_spell_by_spell_id` (Breaking, no\n"
    "alias) and answer the spell a spell_id names, active or parked; `get_spell_permissions` answers per version;\n"
    "callers that need an index's active spell (the transfer's spell_id handles, the contract dependency walks) take\n"
    "an explicit index step and answer as before; the Rift rooms' `get_spell_by_id` command is renamed\n"
    "`get_spell_by_spell_id` and both rooms' spell_id and source-id lookups answer the spell named. The boundary list,\n"
    "a new operational invariant (the 0.2.8229 lookup entry marked superseded in part), four failure modes (one\n"
    "Breaking), the corrected notch remedy and no-op entry, and the code map (eleven files remeasured) carry it; the\n"
    "component map carries the per-component contracts. Every numeric citation into the changed files was remapped\n"
    "line by line. Open with the owner: the five other places that resolve a spell_id through its index (the\n"
    "contracted-copy lookup, the contract row `Detail`, and three ConduitWard contract reads and checks),\n"
    "`Meld._current_in_pool`, and the three paths that file a borrowed copy under the selected id.\n\n",
)


def entry_span(text: str, rel: str) -> tuple:
    """Return (start, end) of a code-map entry: its `- path:` line through the newline before the next entry."""
    head = f"- path: `{rel}`\n  start_line: 1\n"
    if text.count(head) != 1:
        raise SystemExit(f"FAIL code map entry count {text.count(head)} for {rel}")
    start = text.index(head)
    nxt = text.find("\n- path:", start + 1)
    end = (nxt + 1) if nxt != -1 else len(text)
    return start, end


def main() -> None:
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    check = "--check" in sys.argv[1:]
    if len(args) != 1:
        raise SystemExit(__doc__)
    root = pathlib.Path(args[0]).resolve()
    doc = root / DOC
    raw = doc.read_bytes()
    if b"\r" in raw:
        raise SystemExit("FAIL: the document is expected to be LF")
    text = raw.decode("utf-8")
    edits = [BOUNDARY_SENTENCE, BOUNDARY_BULLET, INVARIANT, FAILURES, HANDOFF] + SMALL
    added = []
    for old, new in edits:
        n = text.count(old)
        if n != 1:
            raise SystemExit(f"FAIL anchor count {n}: {old[:90]!r}")
        text = text.replace(old, new)
        added.extend(new.split("\n"))
    now = datetime.datetime.now(datetime.UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
    for rel, (old_note, new_note) in CODE_MAP.items():
        loc = len((root / rel).read_bytes().splitlines())
        start, end = entry_span(text, rel)
        entry = text[start:end]
        lines = entry.split("\n")
        if not (lines[2].startswith("  end_line: ") and lines[3].startswith("  loc: ")
                and lines[4].startswith("  verified_at: ")):
            raise SystemExit(f"FAIL code map entry shape for {rel}: {lines[:5]!r}")
        lines[2] = f"  end_line: {loc}"
        lines[3] = f"  loc: {loc}"
        lines[4] = f"  verified_at: {now}"
        new_entry = "\n".join(lines)
        if new_entry.count(old_note) != 1:
            raise SystemExit(f"FAIL note anchor in {rel}: {old_note[:80]!r}")
        new_entry = new_entry.replace(old_note, new_note)
        text = text[:start] + new_entry + text[end:]
        added.extend(new_note.split("\n"))
        print(f"ok code map {rel} -> {loc}")
    long_lines = [ln for ln in added if len(ln) > 120]
    for ln in long_lines:
        print(f"NOTE over 120 ({len(ln)}): {ln[:100]}...")
    if check:
        print("check only: nothing written")
        return
    doc.write_bytes(text.encode("utf-8"))
    print("written", DOC, "verified_at", now)


if __name__ == "__main__":
    main()
