"""
tests_components for fix #1 (find_spell_by_spell_id_2026_10_17): exact-once edits, all or nothing.

Usage: python docs_tests_components_fix1.py <repo_root> [--check]

The four new test modules (a unit, a component and two integration modules) as key files of their C2 clusters with
Protects bullets, the three suites' Protects and recounted module counts, the core section's counts, four new C1
code-map records and the two records fix #1's codemod lengthened (measured from disk at run time), the information
sources, Metadata and the handoff. The managed stamp test's stale record is left to its own lane. The index is
regenerated after this script.
"""
import datetime
import pathlib
import sys

DOC = "context_compass/system_docs/tests_components.md"

NEW_FILES = [
    ("tests/unit/melder/aether/test_command_system_spell_id_lookups.py",
     "the Rift rooms' lookups by spell_id and source id answer the version named, the static room melds only it,\n"
     "    and the command is renamed with no alias (0.2.8253)."),
    ("tests/component/melder/spellbook/test_spellbook_component_find_spell_by_spell_id.py",
     "`find_spell_by_spell_id` answers each spell_id with its own Spell through notch, index moves, transfer and\n"
     "    disposal, by single-key reads (0.2.8253)."),
    ("tests/integration/melder/aether/conduit/test_spell_id_lookup_returns_that_spell_integration.py",
     "a spell_id answers that spell on a lender and its borrower: permissions, grants by a parked spell_id, and the\n"
     "    transfer and dependency guards (0.2.8253)."),
    ("tests/integration/melder/aether/rift/test_rift_spell_id_lookups_return_that_spell_integration.py",
     "a capability room answers the active version by spell_id, source id and index and refuses a parked one\n"
     "    (0.2.8253)."),
]

REMEASURE = [
    "tests/integration/melder/conduit/test_conduit_integration_release_managed_spell.py",
    "tests/integration/melder/conduit/test_conduit_integration_notch_revalidation.py",
]

EDITS = [
    ("- Updated: 2026-10-16\n", "- Updated: 2026-10-17\n"),
    # Unit Test Suite: Protects, counts, the aether tree.
    ("  reason (see `### Subcomponent: Utilities Unit Cluster`)\n\nInputs:\n- local runtime classes",
     "  reason (see `### Subcomponent: Utilities Unit Cluster`)\n"
     "- the Rift rooms' lookups by spell_id (0.2.8253): a spell_id or a source id answers the version it names, never\n"
     "  the one its index has active - the capability room through the owner Book, the static room by melding only\n"
     "  that version - the refusals name what was asked, and the index path and the spell-index ACL hold (see\n"
     "  `### Subcomponent: Aether/Nexus/Rift Unit Cluster`)\n"
     "\nInputs:\n- local runtime classes"),
    ("- the densest tier: 508 `test_*.py` modules among 511 `.py` files (recounted 2026-10-16)\n",
     "- the densest tier: 509 `test_*.py` modules among 512 `.py` files (recounted 2026-10-17)\n"),
    ("- The aether tree carries 207 `test_*.py` modules beneath these; they are the\n",
     "- The aether tree carries 208 `test_*.py` modules beneath these; they are the\n"),
    # Component Test Suite: Protects, counts.
    ("  (0.2.8245; see `### Subcomponent: Aether Component Cluster`)\n\nInputs:\n",
     "  (0.2.8245; see `### Subcomponent: Aether Component Cluster`)\n"
     "- the exact lookup by spell_id on a real Book (0.2.8253): every spell_id answers its own Spell through each\n"
     "  move between the Book's maps, by single-key reads (see\n"
     "  `### Subcomponent: Spellbook Runtime And Binding Component Cluster`)\n"
     "\nInputs:\n"),
    ("- 166 `test_*.py` modules among 168 `.py` files (recounted 2026-10-16)\n",
     "- 166 `test_*.py` modules among 168 `.py` files (recounted 2026-10-17)\n"),
    # Integration Runtime Suite: Protects, counts, the aether and rift trees.
    ("  `### Subcomponent: Conduit Integration Cluster`)\n\nInputs:\n- real runtime objects\n",
     "  `### Subcomponent: Conduit Integration Cluster`)\n"
     "- the exact lookup by spell_id (0.2.8253): a parked version's spell_id answers that version on its lender and\n"
     "  on a linked borrower, each version answers its own permissions and is granted and ungranted by its spell_id,\n"
     "  and a transfer and a dependency grant keep resolving through the index (see\n"
     "  `### Subcomponent: Spellbook Integration Cluster`); a capability room answers the active version by spell_id,\n"
     "  source id and index and refuses a parked one (see `### Subcomponent: Aether Integration Cluster`)\n"
     "\nInputs:\n- real runtime objects\n"),
    ("- 170 `test_*.py` modules among 177 `.py` files (recounted 2026-10-16); the others are benches and the\n",
     "- 172 `test_*.py` modules among 179 `.py` files (recounted 2026-10-17); the others are benches and the\n"),
    ("- The aether tree carries 46 `test_*.py` modules beneath these; they are the\n",
     "- The aether tree carries 48 `test_*.py` modules beneath these; they are the\n"),
    ("- The rift tree (inside the aether tree) carries 3 `test_*.py` modules over the\n"
     "  same three benches; they are counted here rather than cited.\n",
     "- The rift tree (inside the aether tree) carries 4 `test_*.py` modules, three of them\n"
     "  over the same three benches; they are counted here rather than cited.\n"),
    # C2: Aether/Nexus/Rift Unit Cluster.
    ("  of probing a store, the status payload says why, and a live pool never makes it a live static spell\n"
     "Key Files (C1):\n",
     "  of probing a store, the status payload says why, and a live pool never makes it a live static spell\n"
     "- the Rift rooms' lookups by spell_id (0.2.8253; `test_command_system_spell_id_lookups.py`, 12 tests): over\n"
     "  doubles that publish an index's active version and a parked one, the capability room's\n"
     "  `get_spell_by_source_id` and `get_spell_by_spell_id` answer the version named through the owner Book's\n"
     "  lookup, never the index's active one, refuse an ownerless record and a spell_id the owner Book no longer\n"
     "  holds with messages naming the source id, and still check the spell-index ACL first; the static room melds\n"
     "  only the named version for a spell_id or a source id and names what was asked when it refuses (not live,\n"
     "  unsupported existence), while its index path still answers the first record of the index with a live\n"
     "  object; both rooms advertise `get_spell_by_spell_id` and keep no `get_spell_by_id`\n"
     "Key Files (C1):\n"),
    ("- `tests/unit/melder/aether/test_static_rooms_managed_spell_quantity.py` (static rooms, 2026-10-15)\n",
     "- `tests/unit/melder/aether/test_static_rooms_managed_spell_quantity.py` (static rooms, 2026-10-15)\n"
     "- `tests/unit/melder/aether/test_command_system_spell_id_lookups.py` (room lookups by spell_id, 2026-10-17)\n"),
    # C2: Spellbook Runtime And Binding Component Cluster.
    ("  name a member with no copy and rely on the membership match the fix removed\nKey Files (C1):\n",
     "  name a member with no copy and rely on the membership match the fix removed\n"
     "- the exact lookup by spell_id (0.2.8253; `test_spellbook_component_find_spell_by_spell_id.py`, 10 tests;\n"
     "  renamed from `test_spellbook_component_find_spell_by_id.py`, never catalogued): `find_spell_by_spell_id`\n"
     "  answers an active and a parked spell_id with its own Spell, and still does after a notch, an add-to-index\n"
     "  move and a split to a fresh index; a transfer moves both spell_ids to the target Book; a disposed parked\n"
     "  version, an unknown spell_id and another Book's spell_id answer None; the lookup never iterates the live\n"
     "  active-index map, and a parked version disposed mid-lookup returns the Spell it read, borrowed, with the\n"
     "  next lookup missing\n"
     "Key Files (C1):\n"),
    ("- `tests/component/melder/spellbook/test_scan_bind_parity_component.py` (scan parity over real wiring, "
     "2026-10-10)\n",
     "- `tests/component/melder/spellbook/test_scan_bind_parity_component.py` (scan parity over real wiring, "
     "2026-10-10)\n"
     "- `tests/component/melder/spellbook/test_spellbook_component_find_spell_by_spell_id.py` (exact lookup, "
     "2026-10-17)\n"),
    # C2: Aether Integration Cluster.
    ("  loading roots the hybrid profile and the precision overlay deny\nKey Files (C1):\n",
     "  loading roots the hybrid profile and the precision overlay deny\n"
     "- a capability room's lookups by spell_id (0.2.8253;\n"
     "  `test_rift_spell_id_lookups_return_that_spell_integration.py`, 4 tests): in a dynamic frame open to Rift\n"
     "  rooms, with PricingV1 active and PricingV2 parked on one index, the room answers PricingV1 by its spell_id,\n"
     "  its source id and its index with the same Spell; after a notch it answers PricingV2 by all three; and before\n"
     "  and after the notch it refuses the parked version's spell_id and source id (\"was not found in frame\n"
     "  'default'\") rather than answering the active one\n"
     "Key Files (C1):\n"),
    ("- `tests/integration/melder/aether/test_codegen_core_boundary_integration.py` (characterization, 2026-10-10)\n",
     "- `tests/integration/melder/aether/test_codegen_core_boundary_integration.py` (characterization, 2026-10-10)\n"
     "- `tests/integration/melder/aether/rift/test_rift_spell_id_lookups_return_that_spell_integration.py` "
     "(2026-10-17)\n"),
    # C2: Spellbook Integration Cluster.
    ("  when the old version's grant is removed by its Spell\nKey Files (C1):\n",
     "  when the old version's grant is removed by its Spell\n"
     "- a lookup by spell_id answers that spell (0.2.8253; `test_spell_id_lookup_returns_that_spell_integration.py`,\n"
     "  10 tests): in a dynamic world of a lender (English active and French parked on Greeter's index, the\n"
     "  consumer Polite) linked to a borrower, `get_spell_by_spell_id` answers French's spell_id with French on both\n"
     "  conduits and each spell_id with its own spell after a notch; `get_spell_permissions` answers each version's\n"
     "  own permissions; an unknown spell_id raises ValueError and the old names raise AttributeError; a grant and\n"
     "  an ungrant by French's spell_id proceed, the grant parking the copy on the borrower and the lender's\n"
     "  outbound listing naming French; three guards keep the index-step answers - a transfer by the parked\n"
     "  spell_id moves the whole index with English still active, a dependency grant after a notch contracts\n"
     "  French, and a transfer with dependencies after a notch moves Greeter's index with French active\n"
     "Key Files (C1):\n"),
    ("- `tests/integration/melder/aether/conduit/test_spell_index_meld_and_contract_lifecycle.py` (2026-10-16)\n",
     "- `tests/integration/melder/aether/conduit/test_spell_index_meld_and_contract_lifecycle.py` (2026-10-16)\n"
     "- `tests/integration/melder/aether/conduit/test_spell_id_lookup_returns_that_spell_integration.py` "
     "(2026-10-17)\n"),
    # C1 code map header.
    ("above - 258 paths (recounted 2026-10-16) - and nothing else.",
     "above - 263 paths (recounted 2026-10-17) - and nothing else."),
    ("builders - not every `test_*.py` module beneath it. The 844 test modules of the\n",
     "builders - not every `test_*.py` module beneath it. The 847 test modules of the\n"),
    # Information sources.
    ("- direct filesystem inventory of `tests/`\n\n## Open Questions\n",
     "- `tests/unit/melder/aether/test_command_system_spell_id_lookups.py`\n"
     "- `tests/component/melder/spellbook/test_spellbook_component_find_spell_by_spell_id.py`\n"
     "- `tests/integration/melder/aether/conduit/test_spell_id_lookup_returns_that_spell_integration.py`\n"
     "- `tests/integration/melder/aether/rift/test_rift_spell_id_lookups_return_that_spell_integration.py`\n"
     "- direct filesystem inventory of `tests/`\n\n## Open Questions\n"),
    # Handoff.
    ("## Context / Handoff Summary\n\n2026-10-16 one version, one copy (0.2.8251)",
     "## Context / Handoff Summary\n\n"
     "2026-10-17 lookup by spell_id is exact (0.2.8253): the Aether/Nexus/Rift Unit Cluster gains\n"
     "`test_command_system_spell_id_lookups.py` (the Rift rooms' spell_id and source-id lookups over doubles, 12\n"
     "tests), the Spellbook Runtime And Binding Component Cluster\n"
     "`test_spellbook_component_find_spell_by_spell_id.py` (the exact Book lookup, 10 tests; renamed from the\n"
     "uncatalogued `test_spellbook_component_find_spell_by_id.py`), the Spellbook Integration Cluster\n"
     "`test_spell_id_lookup_returns_that_spell_integration.py` (a lender and borrower world, 10 tests) and the Aether\n"
     "Integration Cluster `test_rift_spell_id_lookups_return_that_spell_integration.py` (a capability room, 4\n"
     "tests), each a key file with a code-map record; the Unit, Component and Integration suites name the\n"
     "protection. Fix #1's codemod renamed the lookups in 82 test files; two of them grew a line where a comment\n"
     "about the old answer became history, and their records (`test_conduit_integration_release_managed_spell.py`,\n"
     "`test_conduit_integration_notch_revalidation.py`) are remeasured. Counts are recounted from disk (unit 509 of\n"
     "512 `.py`, aether tree 208; component 166 of 168; integration 172 of 179, aether tree 48, rift tree 4; 847\n"
     "test modules in the three tiers). The core set is 263 paths, equal to the code map; the 0.2.8251 entry had\n"
     "added a key file without moving the count from 258. Left stale on purpose: the record of\n"
     "`test_spell_managed_quantity_stamp.py` (152 lines; 185 on disk), which changed with\n"
     "TASK-2026-10-16-stamp_test_boots_its_own_aether and is that task's successor's to update.\n\n"
     "2026-10-16 one version, one copy (0.2.8251)"),
]

LAST_RECORD_END = ("    either member order and the removal of a parked version's grant (0.2.8251).\n"
                   "\n## Diagrams\n")


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


def new_records(root: pathlib.Path, now: str) -> str:
    """Return the four new code-map records, measured from disk."""
    out = []
    for rel, note in NEW_FILES:
        loc = len((root / rel).read_bytes().splitlines())
        out.append(f"- path: `{rel}`\n  start_line: 1\n  end_line: {loc}\n  loc: {loc}\n"
                   f"  verified_at: {now}\n  note: {note}\n")
        print(f"ok new record {rel} -> {loc}")
    return "".join(out)


def main() -> None:
    """Apply every edit exactly once to a copy in memory; write it unless --check."""
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
    if text.count(LAST_RECORD_END) != 1:
        raise SystemExit("FAIL: the code map's last record anchor is not unique")
    records = new_records(root, now)
    text = text.replace(LAST_RECORD_END, LAST_RECORD_END.split("\n\n## Diagrams")[0] + "\n" + records
                        + "\n## Diagrams\n")
    added.extend(records.split("\n"))
    for rel in REMEASURE:
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
        print(f"ok remeasured {rel} -> {loc}")
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
