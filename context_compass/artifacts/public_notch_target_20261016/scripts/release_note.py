"""Add the 0.2.8249 entry to the running release note (TASK-2026-10-16-public_notch_target_for_staged_versions).

Run from the repository root:  python <this file>
Exact, asserted replacements on an LF file: the header, S8's example notch (a comment until now, by id since
0.2.8249), S8's "What stays the same" (notch_spell changes in the next section), the new section (read from
notes/release_note_section.md, inserted before "## Packaging and documentation"), two packaging bullets and the
rebuild line. Prints lines over 117 characters.
"""
import pathlib

NOTE = pathlib.Path("release_docs/next_version_release.md")
SECTION = pathlib.Path(
    "context_compass/artifacts/public_notch_target_20261016/notes/release_note_section.md"
).read_text(encoding="utf-8")

EDITS = [
    ("# Melder 0.2.8248\n", "# Melder 0.2.8249\n"),
    (
        "# after reports.notch_spell(spell_index=index, spell=<v2's Spell>):\n"
        "service = reports.meld(spell_id=v2)         # a ReportServiceV2; RuntimeError before 0.2.8248\n",
        "reports.notch_spell(spell_index=index, spell_id=v2)   # by id since 0.2.8249 (next section)\n"
        "service = reports.meld(spell_id=v2)         # a ReportServiceV2; RuntimeError before 0.2.8248\n",
    ),
    (
        "What stays the same: active versions, a `bind_inactive` after `conjure()`, `notch_spell`, ownership transfers,\n"
        "spell ids and records. Restore and the spell-index graft stage versions after `conjure()`, so they worked before and\n"
        "behave as before.\n",
        "What stays the same: active versions, a `bind_inactive` after `conjure()`, ownership transfers, spell ids and\n"
        "records. Restore and the spell-index graft stage versions after `conjure()`, so they worked before and behave as\n"
        "before.\n",
    ),
    ("\n## Packaging and documentation\n", "\n" + SECTION + "## Packaging and documentation\n"),
    (
        "- Agent documentation metadata and the whole-repository LLM bundles are rebuilt for 0.2.8248.\n",
        "- The README's swap sketch (stage a version, notch to it, meld it, notch back) names the versions by id and runs\n"
        "  as written; the expert guide on governed change (`docs/expert/governed-change.md`) shows promotion as\n"
        "  `notch_spell(spell_index=..., spell_id=...)` and says a wrong target is refused, and the expert walkthrough on\n"
        "  notch-swapping a live object (lesson 17) swaps by id.\n"
        "- The packaged system documents (`melder.__architecture__`, `melder.__components__`) and the packaged graph\n"
        "  describe the notch target - its two forms, the checks before and inside the transaction, the refusals - and\n"
        "  the corrected index-mutation sequence: the conduit starts the transaction, and the notch claims the Spellbook\n"
        "  exclusively. The `conduit.py` code-map extent is remeasured, and line citations that had drifted point at\n"
        "  their code again.\n"
        "- Agent documentation metadata and the whole-repository LLM bundles are rebuilt for 0.2.8249.\n",
    ),
]


def main() -> None:
    """Apply every edit once, asserting each old text occurs exactly once."""
    text = NOTE.read_bytes().decode("utf-8")
    assert "\r\n" not in text, "the release note is LF"
    assert text.startswith("# Melder 0.2.8248\n"), text[:40]
    for old, new in EDITS:
        found = text.count(old)
        if found != 1:
            raise SystemExit(f"expected one occurrence, found {found}: {old[:70]!r}")
        text = text.replace(old, new, 1)
    NOTE.write_bytes(text.encode("utf-8"))
    long_lines = [(n, len(line)) for n, line in enumerate(text.split("\n"), 1) if len(line) > 117]
    print("release note written;", len(text.split("\n")) - 1, "lines; lines over 117:", long_lines or "none")


if __name__ == "__main__":
    main()
