"""
src_components for fix #1 (find_spell_by_spell_id_2026_10_17): exact-once edits, all or nothing.

Usage: python docs_src_components_fix1.py <repo_root> [--check]

Spellbook Core, the Binding Pipeline, the RiftSpace Workstation And Command Surface, the Conduit Runtime, ConduitWard
and Contracts, the Ownership Transfer and RiftSpace Command System subcomponents, the transfer flow, a new lookup
flow, the C1 code map (ten changed files remeasured from disk at run time) and the handoff. Numeric citations were
remapped beforehand by remap_citations.py; the index is regenerated after this script.
"""
import datetime
import pathlib
import sys

DOC = "context_compass/system_docs/src_components.md"

EDITS = [
    ("- Updated: 2026-10-16\n", "- Updated: 2026-10-17\n"),
    # Spellbook Core: the dated paragraph.
    ("### Component: Spellbook Core (Binding and Conjure)\n",
     "### Component: Spellbook Core (Binding and Conjure)\n"
     "Exact lookup by spell_id (2026-10-17, 0.2.8253; find_spell_by_spell_id_2026_10_17): `find_spell_by_id` is renamed\n"
     "`find_spell_by_spell_id(spell_id)` - the owner's name, with no alias - and answers the Spell bound under the\n"
     "spell_id: a read of `_spells_by_id` (the active versions), else of `_inactive_spells` (the parked ones), or None.\n"
     "Its parked branch no longer reads the parked spell's index (`Spell._spell_index_unless_cleaned`) to return\n"
     "`_spells[index]`, the spell the index has active: a spell_id and a SpellIndex are separate things (owner ruling,\n"
     "2026-10-17), and the spell an index has active is a lookup by the index's id (`get_spell_by_index_id`,\n"
     "`_find_spell`). A parked version therefore answers itself, also one split off by `remove_from_spell_index` into an\n"
     "index with no active spell (it was None), and a parked version disposed while the lookup runs is returned as read,\n"
     "borrowed, or missed once its spell_id has left the map. `_get_spell_by_id_via_aether` (its name kept) returns the\n"
     "owner Book's `find_spell_by_spell_id` answer. Still lock-free and O(1), with `check_cleaned()` first; the callers\n"
     "that wanted the index's active spell take an explicit index step (Conduit Runtime, ConduitWard and Contracts,\n"
     "Subcomponent: Ownership Transfer).\n"
     "EVIDENCE: `src/melder/aether/spellbook/spellbook.py:Spellbook.find_spell_by_spell_id` and\n"
     "`Spellbook._get_spell_by_id_via_aether`.\n"
     "\n"),
    # Spellbook Core: concurrency.
    ("- `find_spell_by_id` is lock-free on purpose (0.2.8229): it reads `_spells_by_id`, then `_inactive_spells` and\n"
     "  `Spell._spell_index_unless_cleaned`, then `_spells.get(index)` - single-key reads, never an iteration - so a\n",
     "- `find_spell_by_spell_id` (`find_spell_by_id` until 0.2.8253) is lock-free on purpose (0.2.8229): it reads\n"
     "  `_spells_by_id`, then `_inactive_spells` (until 0.2.8253 a parked hit also read\n"
     "  `Spell._spell_index_unless_cleaned`, then `_spells.get(index)`) - single-key reads, never an iteration - so a\n"),
    ("  `_flip_registry_and_spellbooks` and `_migrate_inactive_members`, are the only windows in which a lineage id\n"
     "  briefly answers None.\n",
     "  `_flip_registry_and_spellbooks` and `_migrate_inactive_members`, are the only windows in which a spell_id\n"
     "  briefly answers None (a lineage id until 0.2.8253).\n"),
    # Spellbook Core: failure modes.
    ("- `find_spell_by_id` returns None for an id no local index claims - unknown, another Book's, a contracted\n"
     "  spell's, a parked version split into a fresh index, a parked version disposed during the lookup - and raises\n"
     "  only RuntimeError for a cleaned Book (0.2.8229; before, concurrent binds and removals made it raise the\n"
     "  size-change RuntimeError or the SpellIndex AttributeError/RuntimeError, or miss a registered spell).\n",
     "- `find_spell_by_spell_id` (`find_spell_by_id` until 0.2.8253) returns None for a spell_id this Book holds no spell\n"
     "  under - unknown, another Book's, a contracted spell's, a parked version once its disposal has popped it - and\n"
     "  raises only RuntimeError for a cleaned Book (0.2.8229; before, concurrent binds and removals made it raise the\n"
     "  size-change RuntimeError or the SpellIndex AttributeError/RuntimeError, or miss a registered spell). Until\n"
     "  0.2.8253 a parked version split into a fresh index, and one disposed during the lookup, answered None too.\n"),
    ("  never fire. `_get_spell_by_id_via_aether` returns None only when the owner's `find_spell_by_id` misses.\n",
     "  never fire. `_get_spell_by_id_via_aether` returns None only when the owner's `find_spell_by_spell_id` misses.\n"),
    # Binding Pipeline: the index read's readers and the SpellIndex docstrings.
    ("  `_lock` itself, so the read never raises on a cleaned Spell; it holds no other lock, and an index move (which\n"
     "  repoints `spell_index` under the Spellbook lock) is seen as the old or the new index.\n",
     "  `_lock` itself, so the read never raises on a cleaned Spell; it holds no other lock, and an index move (which\n"
     "  repoints `spell_index` under the Spellbook lock) is seen as the old or the new index. Its readers since\n"
     "  0.2.8253: the parked branch of `Spellbook._find_contracted_spell_by_id` and the explicit index steps that turn a\n"
     "  spell found by spell_id into the spell its index has active (the ownership transfer's spell_id handles, the\n"
     "  contract dependency walks); until then its first reader was the parked branch of `find_spell_by_id`.\n"),
    ("  over indexes the caller neither owns nor locks (`Spellbook._find_contracted_spell_by_id`, `Detail.has_spell`,\n"
     "  `IndexDetail.has_spell`).\n",
     "  over indexes the caller neither owns nor locks (`Spellbook._find_contracted_spell_by_id`, `Detail.has_spell`,\n"
     "  `IndexDetail.has_spell`). Since 0.2.8253 the docstrings of `has_spell` and `SpellIndex.update` say a spell_id\n"
     "  names its own spell (`Spellbook.find_spell_by_spell_id`), not the lineage's selected head; membership answers\n"
     "  are unchanged.\n"),
    # RiftSpace Workstation And Command Surface.
    ("- `get_spell_by_id` resolves the spell in the owner's Book through `Spellbook.find_spell_by_id` (0.2.8230); it used\n"
     "  to walk that Book's live index map, which a bind or removal on another thread could resize mid-walk.\n",
     "- `get_spell_by_spell_id` (`get_spell_by_id` until 0.2.8253) resolves the spell in the owner's Book through\n"
     "  `Spellbook.find_spell_by_spell_id` (0.2.8230; `find_spell_by_id` until 0.2.8253); it used to walk that Book's live\n"
     "  index map, which a bind or removal on another thread could resize mid-walk. `get_spell_by_source_id` reads the\n"
     "  owner Book the same way (`_get_spell_by_record_locked`, 0.2.8253). The static room's lookups hold the command\n"
     "  lock across `meld_existing_spell`, as its index path does; no lock is added.\n"),
    ("- `StaticCommandSystem` denies topology mutation and direct `meld(...)`.\n",
     "- `StaticCommandSystem` denies topology mutation and direct `meld(...)`.\n"
     "- A spell lookup by spell_id or by source id answers exactly the spell named (0.2.8253; owner, 2026-10-17: a\n"
     "  spell_id and a SpellIndex are separate things): the base room returns the owner Book's `find_spell_by_spell_id`\n"
     "  answer (`get_spell_by_spell_id`; `get_spell_by_source_id` through `_get_spell_by_record_locked`, which applies the\n"
     "  frame gate and the record's spell-index ACL and, resolving the owner conduit through `_get_conduit_by_id_locked`,\n"
     "  the conduit ACL), and the static room melds only the records published for that spell_id, or the one record the\n"
     "  source id names (`StaticCommandSystem._meld_live_spell_from_records_locked`, reuse-only `meld_existing_spell`).\n"
     "  Only `get_spell_by_index_id` answers what an index has active. The command is renamed `get_spell_by_spell_id`\n"
     "  from `get_spell_by_id` - the action name the command gate admits and the room memory records, the raw-access\n"
     "  label and the advertised base command list - with no alias. Nexus publishes the version an index has active, so\n"
     "  a parked version's spell_id or source id is refused (ValueError), never answered with the active version.\n"
     "  EVIDENCE: `src/melder/nexus/rift/command_system/command_system.py:CommandSystem.get_spell_by_spell_id`,\n"
     "  `CommandSystem.get_spell_by_source_id`, `CommandSystem._get_spell_by_record_locked` and\n"
     "  `src/melder/nexus/rift/command_system/static_command_system.py:StaticCommandSystem.get_spell_by_spell_id`,\n"
     "  `StaticCommandSystem.get_spell_by_source_id`, `StaticCommandSystem._meld_live_spell_from_records_locked`.\n"),
    ("- Strong/weak binding misuse raises instead of silently degrading storage mode.\n"
     "- Denied runtime actions fail fast.\n",
     "- Strong/weak binding misuse raises instead of silently degrading storage mode.\n"
     "- Denied runtime actions fail fast.\n"
     "- ValueError from the spell lookups name what was asked (0.2.8253): the static room says \"Spell id '<id>' uses\n"
     "  unsupported static existence '<name>'.\" and \"Spell id '<id>' is not live in frame '<frame>'.\", and \"Spell\n"
     "  '<source_id>' ...\" for a source id (they said \"Spell index '<index id>' ...\"; the index path keeps that\n"
     "  wording); the base room's source-id lookup says \"Spell '<source_id>' has no owner conduit in frame '<frame>'.\"\n"
     "  and \"Spell '<source_id>' was not found in the owner spellbook for frame '<frame>'.\" (it said \"Spell index id\n"
     "  '<id>' was not found in the owner spellbooks for frame '<frame>'.\"). The old command name `get_spell_by_id` is\n"
     "  gone (AttributeError).\n"),
    # Conduit Runtime.
    ("### Component: Conduit Runtime (Normal and Lesser)\nPurpose:\n"
     "- Execution scope for resolving spells and managing object lifecycles.\n\n",
     "### Component: Conduit Runtime (Normal and Lesser)\nPurpose:\n"
     "- Execution scope for resolving spells and managing object lifecycles.\n\n"
     "Exact lookups by spell_id (2026-10-17, 0.2.8253; find_spell_by_spell_id_2026_10_17): `get_spell_by_id` is renamed\n"
     "`get_spell_by_spell_id(spell_id, aetheric_frame_name=\"default\")` - the owner's name, no alias - and returns the\n"
     "spell that owns the spell_id, active or parked: Aether names the owner conduit, whose Book answers\n"
     "(`Spellbook._get_spell_by_id_via_aether` -> `find_spell_by_spell_id`); a spell_id no conduit of the frame claims\n"
     "still raises ValueError. For a parked spell_id it returned the spell its index had active. `get_spell_permissions`\n"
     "answers the permissions that exact version was bound with (it answered the active version's). The transfer\n"
     "footprint's `_resolve_transfer_spell` keeps its answer through an explicit index step: a SpellIndex id resolves\n"
     "through `get_spell_by_index_id`; a spell_id through `get_spell_by_spell_id`, then `get_spell_by_index_id` of that\n"
     "member's index (`_spell_index_unless_cleaned` under the member's own lock, then this conduit's Book lock alone) -\n"
     "the same spell for a spell this conduit owns, and a RuntimeError when the index has no active spell this conduit\n"
     "reaches. The notch target's refusal for another index names the renamed lookup in its remedy, and the notch and\n"
     "index-move docstrings say a spell_id resolves to that exact spell.\n"
     "EVIDENCE: `src/melder/aether/conduit/conduit.py:Conduit.get_spell_by_spell_id`, `Conduit.get_spell_permissions`,\n"
     "`Conduit._resolve_transfer_spell` and `Conduit._owned_notch_target`.\n"
     "\n"),
    ("did). `get_spell_by_id` keeps answering a parked spell_id with the index's active member.\n",
     "did). Since 0.2.8253 `get_spell_by_spell_id` answers a parked spell_id with that spell (until then\n"
     "`get_spell_by_id` answered with the index's active member).\n"),
    ("- `get_spell_permissions` takes no conduit lock and resolves through `Spellbook.find_spell_by_id` (0.2.8230); it used\n",
     "- `get_spell_permissions` takes no conduit lock and resolves through `Spellbook.find_spell_by_spell_id` (0.2.8230;\n"
     "  `find_spell_by_id` until 0.2.8253, exact since then); it used\n"),
    ("- ValueError from `get_spell_by_id` and `get_conduit_by_spell_id` for an id no conduit in the frame claims, or for\n",
     "- ValueError from `get_spell_by_spell_id` (`get_spell_by_id` until 0.2.8253) and `get_conduit_by_spell_id` for an id\n"
     "  no conduit in the frame claims, or for\n"),
    ("  as `get_*` lookups do; they always raised, and their docstrings say so since 0.2.8230 (owner decision\n"
     "  2026-10-11; they promised None).\n",
     "  as `get_*` lookups do; they always raised, and their docstrings say so since 0.2.8230 (owner decision\n"
     "  2026-10-11; they promised None).\n"
     "- RuntimeError \"[CONDUIT] Transfer-ownership could not resolve the source spell on this conduit.\" from\n"
     "  `transfer_spell_ownership(spell=<spell_id>)` when the spell_id's index has no active spell this conduit reaches\n"
     "  (0.2.8253: also for another conduit's spell whose index this conduit neither owns nor borrows, which used to\n"
     "  reach the transfer and be refused there with \"Source conduit does not own the spell.\").\n"),
    # ConduitWard and Contracts.
    ("### Component: ConduitWard and Contracts\nPurpose:\n"
     "- Control-plane manager for conduit contracts and lineage links.\n\n",
     "### Component: ConduitWard and Contracts\nPurpose:\n"
     "- Control-plane manager for conduit contracts and lineage links.\n\n"
     "Spell_id lookups in the ward (2026-10-17, 0.2.8253; find_spell_by_spell_id_2026_10_17): the grant and ungrant check\n"
     "(`_check_spell_id_and_spell`) calls the renamed `Conduit.get_spell_by_spell_id`, which answers a parked spell_id\n"
     "with that spell, so `add_spell_to_contract(spell_id=<parked>)` and `remove_spell_from_contract(spell_id=<parked>)`\n"
     "proceed - a grant parks the copy on the borrower (`_add_inactive_contracted_spell`), as a grant of the Spell object\n"
     "does - where they raised RuntimeError \"Provided spell_id '<parked>' does not match inspected ID '<active>'.\". The\n"
     "dependency walks of `_link_spell_dependencies` and `_preflight_contract_dependency_collisions` grant a dependency at\n"
     "the version its index has active now, in two explicit steps: the spell that owns the dependency's spell_id\n"
     "(`get_spell_by_spell_id`), then the owner Book's `_find_spell` of its index; `_transfer_spell_ownership` resolves a\n"
     "spell_id handle the same way through this conduit's `get_spell_by_index_id`. Both keep the old answers for a spell\n"
     "the owner holds, and the walks keep their errors. The outbound half of `_get_spells_in_contract_by_conduit` lists\n"
     "each granted version's own Spell (`find_spell_by_spell_id`); the inbound half still reads through\n"
     "`Spellbook._find_contracted_spell_by_id`, and `_get_spell_in_contracts`, `_get_all_spells_in_contracts` and\n"
     "`_validate_contracts_and_define` still resolve a granted row by its index (the owner's to decide).\n"
     "EVIDENCE: `src/melder/aether/conduit/conduit_ward/conduit_ward.py:ConduitWard._check_spell_id_and_spell`,\n"
     "`ConduitWard._link_spell_dependencies`, `ConduitWard._preflight_contract_dependency_collisions`,\n"
     "`ConduitWard._transfer_spell_ownership` and `ConduitWard._get_spells_in_contract_by_conduit`.\n"
     "\n"),
    ("  maps under it and resolves every id by key through this conduit's Book (inbound\n"
     "  `Spellbook._find_contracted_spell_by_id`, outbound `Spellbook.find_spell_by_id`). It no longer calls\n",
     "  maps under it and resolves every id by key through this conduit's Book (inbound\n"
     "  `Spellbook._find_contracted_spell_by_id`, outbound `Spellbook.find_spell_by_spell_id` - `find_spell_by_id` until\n"
     "  0.2.8253). It no longer calls\n"),
    ("- RuntimeError if `_sever_link` finds no contract to remove.\n",
     "- RuntimeError if `_sever_link` finds no contract to remove.\n"
     "- RuntimeError \"Could not resolve spell for ownership transfer.\" from `_transfer_spell_ownership` when a spell_id\n"
     "  handle's index has no active spell this conduit reaches (0.2.8253: also for another conduit's spell whose index\n"
     "  this conduit neither owns nor borrows, which the transfer used to refuse later as not owned by the source).\n"),
    # Subcomponent: Ownership Transfer.
    ("  it creates (owner ruling, 2026-09-27).\nData Structures:\n",
     "  it creates (owner ruling, 2026-09-27).\n"
     "- A spell_id names one member and a transfer moves its whole index, so every spell_id handle resolves in two\n"
     "  explicit steps (0.2.8253): the spell that owns it (`get_spell_by_spell_id`, active or parked), then the spell its\n"
     "  index has active - `Conduit._resolve_transfer_spell` and `ConduitWard._transfer_spell_ownership` through the\n"
     "  conduit's `get_spell_by_index_id`, `TransferOfOwnership._resolve_spell` and `_transfer_owned_dependencies` from\n"
     "  the source Book's `_spells` under its lock, `_deps_resolvable_on_target` from the member's own Book. That is the\n"
     "  old lookup's answer for every spell the source owns; a parked Spell object never reaches a transfer or a\n"
     "  dependency sub-transfer, and `_resolve_spell` raises \"Unable to resolve spell for transfer: the source conduit's\n"
     "  Spellbook has no active spell in the index of spell_id '<id>'.\" where it handed None to the ownership check.\n"
     "  `_dirty_dependencies` only renames its call: it marks the spell's index, which the exact spell shares.\n"
     "Data Structures:\n"),
    # Subcomponent: RiftSpace Command System.
    ("Static spell owners resolve through `Aether.get_root_conduit_by_id` (0.2.79).\n",
     "Static spell owners resolve through `Aether.get_root_conduit_by_id` (0.2.79).\n"
     "- Spell lookups (0.2.8253): `get_spell_by_spell_id` (renamed from `get_spell_by_id`) and `get_spell_by_source_id`\n"
     "  answer the spell named - the base room the owner Book's `find_spell_by_spell_id` answer (the source id through\n"
     "  `_get_spell_by_record_locked`), the static room the live object of only that spell_id's published records\n"
     "  (`_meld_live_spell_from_records_locked`, shared with the index path) - and `get_spell_by_index_id` the spell an\n"
     "  index has active (Component: RiftSpace Workstation And Command Surface).\n"),
    # Flows.
    ("### Flow: Transfer Spell Ownership (Dynamic)\n1. `Conduit.transfer_spell_ownership(...)` validates dynamic mode.\n",
     "### Flow: Transfer Spell Ownership (Dynamic)\n"
     "1. `Conduit.transfer_spell_ownership(...)` validates dynamic mode; a spell_id handle resolves to the spell its\n"
     "   index has active here - `Conduit._resolve_transfer_spell`: `get_spell_by_spell_id`, then\n"
     "   `get_spell_by_index_id` of that member's index (0.2.8253).\n"),
    ("### Flow: Conduit.notch_spell -> Target Check -> Spellbook._apply_notch\n",
     "### Flow: Conduit.get_spell_by_spell_id -> Owner Book (Exact)\n"
     "1. `Conduit.get_spell_by_spell_id(spell_id, aetheric_frame_name=\"default\")`: `check_cleaned`, then\n"
     "   `Spellbook._get_spell_by_id_via_aether(spell_id, aetheric_frame_name)` on this conduit's Book (0.2.8253; renamed\n"
     "   from `get_spell_by_id`).\n"
     "2. `Spellbook._get_conduit_by_spell_id(spell_id, aetheric_frame_name)` (\"default\" names the Book's frame) ->\n"
     "   `Aether._get_conduit_by_spell_id` -> the owner conduit, else ValueError \"Spell version <id> not found in any\n"
     "   conduit.\" (or the missing frame's error); an owner with no Spellbook raises RuntimeError.\n"
     "3. `owner._spellbook.find_spell_by_spell_id(spell_id)`: `check_cleaned`, `_spells_by_id.get(spell_id)`, else\n"
     "   `_inactive_spells.get(spell_id)` - no lock, no index read; the Spell returned is borrowed (None when the\n"
     "   spell_id left the owner's Book between the two steps).\n"
     "4. Where the spell an index has active is wanted (the transfers, the contract dependency walks), the caller then\n"
     "   reads `member._spell_index_unless_cleaned()` (the member's lock) and asks the index's Book for its active\n"
     "   spell - `Spellbook._find_spell(index)` or `Conduit.get_spell_by_index_id(index.id)` (one Book lock).\n"
     "\n"
     "### Flow: Conduit.notch_spell -> Target Check -> Spellbook._apply_notch\n"),
    # Handoff.
    ("## Context / Handoff Summary\n\n",
     "## Context / Handoff Summary\n\n"
     "2026-10-17 lookup by spell_id is exact (0.2.8253; the owner's rule: a spell_id and a SpellIndex are separate\n"
     "things): Spellbook Core carries `find_spell_by_spell_id` (renamed from `find_spell_by_id`, no alias) - the active\n"
     "version, else the parked one, no index read - with its threading and failure notes; Conduit Runtime carries\n"
     "`get_spell_by_spell_id` (renamed from `get_spell_by_id`), the per-version `get_spell_permissions` and the transfer\n"
     "footprint's explicit index step; ConduitWard and Contracts carries the exact grant check (a parked spell_id grant\n"
     "proceeds), the dependency walks' and the transfer handle's explicit step and the exact outbound listing;\n"
     "Ownership Transfer carries the transfer's spell_id resolution; the RiftSpace Workstation And Command Surface and\n"
     "the RiftSpace Command System carry the renamed room command and the exact spell_id and source-id lookups with\n"
     "their messages; the Binding Pipeline names `_spell_index_unless_cleaned`'s readers and the SpellIndex docstrings;\n"
     "a new call flow follows the lookup to the owner Book; the transfer flow and the code map (ten files remeasured)\n"
     "follow. Every numeric citation into the eleven changed files was remapped line by line. Open with the owner: the\n"
     "contract-side lookups that still resolve a spell_id through its index (`_find_contracted_spell_by_id`, `Detail`,\n"
     "three ConduitWard contract reads and checks), `Meld._current_in_pool`, and the copies filed under the selected\n"
     "id.\n\n"),
]

CODE_MAP = [
    "src/melder/aether/spellbook/spellbook.py",
    "src/melder/aether/conduit/conduit.py",
    "src/melder/aether/conduit/conduit_ward/conduit_ward.py",
    "src/melder/aether/conduit/conduit_ward/transfer/transfer_of_ownership.py",
    "src/melder/aether/spellbook/bind/spell_index.py",
    "src/melder/aether/spellbook/spell.py",
    "src/melder/crystallizer/crystal_loader_system/graft_runner.py",
    "src/melder/crystallizer/crystal_loader_system/restore_engine.py",
    "src/melder/nexus/rift/command_system/command_system.py",
    "src/melder/nexus/rift/command_system/static_command_system.py",
]


def entry_span(text: str, rel: str) -> tuple:
    """Return (start, end) of a code-map entry's five contract lines: `- path:` through `verified_at`."""
    head = f"- path: `{rel}`\n  start_line: 1\n"
    if text.count(head) != 1:
        raise SystemExit(f"FAIL code map entry count {text.count(head)} for {rel}")
    start = text.index(head)
    end = start
    for _ in range(5):
        end = text.index("\n", end) + 1
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
    added = []
    for old, new in EDITS:
        n = text.count(old)
        if n != 1:
            raise SystemExit(f"FAIL anchor count {n}: {old[:90]!r}")
        text = text.replace(old, new)
        added.extend(new.split("\n"))
    now = datetime.datetime.now(datetime.UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
    for rel in CODE_MAP:
        loc = len((root / rel).read_bytes().splitlines())
        start, end = entry_span(text, rel)
        lines = text[start:end].split("\n")
        if not (lines[2].startswith("  end_line: ") and lines[3].startswith("  loc: ")
                and lines[4].startswith("  verified_at: ")):
            raise SystemExit(f"FAIL code map entry shape for {rel}: {lines[:5]!r}")
        lines[2] = f"  end_line: {loc}"
        lines[3] = f"  loc: {loc}"
        lines[4] = f"  verified_at: {now}"
        text = text[:start] + "\n".join(lines) + text[end:]
        print(f"ok code map {rel} -> {loc}")
    for ln in added:
        if len(ln) > 120:
            print(f"NOTE over 120 ({len(ln)}): {ln[:100]}...")
    if check:
        print("check only: nothing written")
        return
    doc.write_bytes(text.encode("utf-8"))
    print("written", DOC, "verified_at", now)


if __name__ == "__main__":
    main()
