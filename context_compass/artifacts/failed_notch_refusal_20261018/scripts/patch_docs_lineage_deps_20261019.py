"""Add the lineage-dependency restore to the S8 patch docs (FACT note of 2026-10-19T11:41:48Z).

Each edit is an exact (old, new) pair that must occur once; every new line stays within 120 characters; the files
stay LF. Usage: patch_docs_lineage_deps_20261019.py --check|--apply
"""
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
PATCH = ROOT / "system_docs/patches/active/failed_notch_refusal_2026_10_18"

EDITS = {
    "architecture_patch.md": [
        (
            "  tracks the restored version, or no longer tracks an index it did not track before; Nexus publishes the\n",
            "  tracks the restored version with the dependencies and topology it had registered, or no longer tracks an\n"
            "  index it did not track before; Nexus publishes the\n",
        ),
        (
            "  Crystallizer's twins, which receive the switch and then its reversal, so the record ends on the restored version.\n",
            "  Crystallizer's twins, which receive the switch and then its reversal, so the record ends on the restored version.\n"
            "  The refused version's own topology stays under its spell_id: nothing reads it while it is parked, and its\n"
            "  next check replaces it.\n",
        ),
    ],
    "component_patch_spellbook_notch_refusal.md": [
        (
            "  `selected_spell_id`, the Book's address lookup and the frame claim for the incoming version's key, and whether\n"
            "  SpellSystemStates tracked the index.\n",
            "  `selected_spell_id`, the Book's address lookup and the frame claim for the incoming version's key, whether\n"
            "  SpellSystemStates tracked the index, the lineage's direct dependencies and the outgoing version's registered\n"
            "  topology.\n",
        ),
        (
            "  notch back does. When the refused version's key differs, that key's lookup and claim are then set back to\n",
            "  notch back does. The lineage's direct dependencies and the outgoing version's topology, with the collection\n"
            "  and contract indexes it feeds, are registered again: the check's Phase 3 put the refused version's there,\n"
            "  and another Book's resolution would read the restored version as depending on them. When the refused\n"
            "  version's key differs, that key's lookup and claim are then set back to\n",
        ),
    ],
    "code_description_patch_notch_refusal.md": [
        (
            "   (`get_lookup(spell._key)`) and whether SpellSystemStates tracks the index.\n",
            "   (`get_lookup(spell._key)`), whether SpellSystemStates tracks the index and its direct dependencies, and the\n"
            "   outgoing version's registered topology.\n",
        ),
    ],
}


def main() -> None:
    """Apply every pair in memory, check the caps, write only with --apply."""
    if sys.argv[1:] not in (["--check"], ["--apply"]):
        raise SystemExit(__doc__)
    results = {}
    for name, pairs in EDITS.items():
        path = PATCH / name
        raw = path.read_bytes()
        if b"\r\n" in raw:
            raise SystemExit("CRLF in " + name)
        text = raw.decode("utf-8")
        for old, new in pairs:
            if text.count(old) != 1:
                raise SystemExit("%s: anchor found %d times: %r" % (name, text.count(old), old[:80]))
            for line in new.split("\n"):
                if len(line) > 120:
                    raise SystemExit("%s: line over 120 chars (%d): %s" % (name, len(line), line))
            text = text.replace(old, new)
        results[path] = text
        print(name, "lines now:", text.count("\n"))
    if sys.argv[1] == "--apply":
        for path, text in results.items():
            path.write_bytes(text.encode("utf-8"))
            if path.read_bytes().decode("utf-8") != text:
                raise SystemExit("read-back mismatch: " + path.name)
        print("applied")


main()
