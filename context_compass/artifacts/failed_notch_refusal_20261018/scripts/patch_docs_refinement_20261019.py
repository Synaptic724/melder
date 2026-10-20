"""Add the shared-key refinement and the preface's line-break refusal to the S8 patch docs (owner's go, 2026-10-19).

Each edit is an exact (old, new) pair that must occur once; every new line stays within 120 characters; the files
stay LF. Usage: patch_docs_refinement_20261019.py --check|--apply
"""
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
PATCH = ROOT / "system_docs/patches/active/failed_notch_refusal_2026_10_18"

EDITS = {
    "architecture_patch.md": [
        (
            "  and the lender cannot meld the index by address until a notch back (probe N2, on 0.2.8252 and on 0.2.8255).\n",
            "  and the lender cannot meld the index by address until a notch back (probe N2 on 0.2.8252, 0.2.8255 and\n"
            "  0.2.8260; any failing check does it, an ambiguous provider as well as a self-dependency).\n",
        ),
        (
            "  bind whose commit fails; the signature-claim stories S1 and S2, which wait for\n"
            "  EPIC-2026-10-18-spell_identity_is_the_code; the change-control machinery (validator, orchestrator, session\n"
            "  rollback actions), unchanged in code.\n",
            "  bind whose commit fails; the signature-claim stories S1 and S2, their own lanes after this one (the reversal\n"
            "  leaves a shared address's claim as a notch back leaves it); the change-control machinery (validator,\n"
            "  orchestrator, session rollback actions), unchanged in code.\n",
        ),
        (
            "  selected before; that version is active and the refused one parked; the Book's four active maps, its address\n"
            "  lookup and the frame claim of the refused version's key hold what they held; SpellSystemStates tracks the\n"
            "  restored version, or no longer tracks an index it did not track before; Nexus publishes the restored version's\n"
            "  record, or none; no research promotion is journaled; borrowers are untouched, because the fan-out never runs; the\n"
            "  refused version's Phase 1-4 artifacts are reset, so a later notch checks it again.\n",
            "  selected before; that version is active and the refused one parked; the Book's four active maps hold what they\n"
            "  held; the address lookup and the frame claim of the restored version's key name the restored version, as a\n"
            "  notch back leaves them, and those of a refused version keyed elsewhere hold what they held; SpellSystemStates\n"
            "  tracks the restored version, or no longer tracks an index it did not track before; Nexus publishes the\n"
            "  restored version's record, or none; no research promotion is journaled; borrowers are untouched, because the\n"
            "  fan-out never runs; the refused version's Phase 1-4 artifacts are reset, so a later notch checks it again.\n"
            "- A key the two versions share is left to the reversal's promotion. Setting it back to its before-value would\n"
            "  release the restored version's claim and Book lookup wherever staging the refused version had dropped them\n"
            "  (STORY-2026-10-17-staged_version_releases_active_signature), leaving the old version active but not meldable\n"
            "  by address.\n",
        ),
        (
            "1. These patch docs, linked from the story; the owner's approval. 2. Claim spellbook.py, conduit.py,\n"
            "spellbook_validation_error.py and change_control_manager.py from melder_0 by mailbox. 3. Red tests (the component\n"
            "patches' validation expectations). 4. The code and the docstrings. 5. The suites, GIL off and on; probe N1-N3\n"
            "re-run. 6. System documents with their indexes, the graph, the release note; the next free notch (0.2.8256 unless\n"
            "melder_0 lands first). 7. Closure; the rebuild last.\n",
            "1. These patch docs, linked from the story; the owner's approval (2026-10-18) and his go (2026-10-19). 2. Claim\n"
            "spellbook.py, conduit.py, spellbook_validation_error.py and change_control_manager.py from melder_0 by mailbox;\n"
            "while melder_0 holds them, build and test the change on a copy of the last landed tree and apply it by anchored\n"
            "edits onto melder_0's landing. 3. Red tests (the component patches' validation expectations). 4. The code and\n"
            "the docstrings. 5. The suites, GIL off and on; the probes re-run. 6. System documents with their indexes, the\n"
            "graph, the release note; the next free notch, read from `__version__` at landing. 7. Closure; the rebuild last.\n",
        ),
    ],
    "component_patch_spellbook_notch_refusal.md": [
        (
            "- Reversal when there was an active version: the seam run toward it (`_apply_notch(restored)`, change reason\n"
            "  `mutation_rolled_back`), then the incoming key's Book lookup and frame claim set back to their before-values\n"
            "  (released when they had none); the seam repoints only the key of the version it promotes.\n",
            "- Reversal when there was an active version: the seam run toward it (`_apply_notch(restored)`, change reason\n"
            "  `mutation_rolled_back`), which repoints the restored version's key - its Book lookup and frame claim - as a\n"
            "  notch back does. When the refused version's key differs, that key's lookup and claim are then set back to\n"
            "  their before-values (released when they had none), since the seam repoints only the key of the version it\n"
            "  promotes. A key the two share is left as the promotion set it: setting it back would release the restored\n"
            "  version's claim and lookup wherever staging the refused version had dropped them\n"
            "  (STORY-2026-10-17-staged_version_releases_active_signature), and the old version could not be melded by\n"
            "  address.\n",
        ),
        (
            "- Component: the same with an index-linked borrower: its copies are untouched (English active, SelfMade parked) and\n"
            "  its consumer melds English.\n",
            "- Component: the same with an index-linked borrower: its copies are untouched (English active, SelfMade parked) and\n"
            "  its consumer melds English.\n"
            "- Component: both refusals again with a version broken for an ordinary reason - TimedGreeter, whose `clock: Clock`\n"
            "  parameter has two registered providers ([AMBIGUOUS_PROVIDER]) - so the refusal does not depend on what the\n"
            "  check finds.\n",
        ),
    ],
    "code_description_patch_notch_refusal.md": [
        (
            "- A version that passes keeps its Phase 1-4 results, as at today's commit; the commit validator then skips it.\n",
            "- A version that passes keeps its Phase 1-4 results, as at today's commit; the commit validator then skips it.\n"
            "- The reversal's promotion repoints the restored version's key. The refused version's key is set back afterwards\n"
            "  only when it differs, or when there is no restored version; a shared address therefore ends claimed and\n"
            "  routed by the restored version, as after a notch back.\n",
        ),
    ],
    "component_patch_spellbook_validation_error_preface.md": [
        (
            "  that is not a str raises TypeError; an empty one is refused the same way (it would add a blank first line).\n",
            "  that is not a str raises TypeError; an empty one is refused the same way (it would add a blank first line), and\n"
            "  so is one with a line break (the refusal is one line; a second would sit between it and the report).\n",
        ),
        (
            "  line is the preface and the second the report's first line; a non-str or empty preface raises TypeError.\n",
            "  line is the preface and the second the report's first line; a non-str, empty or multi-line preface raises\n"
            "  TypeError.\n",
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
