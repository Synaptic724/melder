"""Link the patch folder from the S8 story (Artifact Links, handoff) and row it on artifact_board.md.

Every anchor must occur once; files are LF. Usage: link_patch.py --check | --apply
"""
import datetime
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
STORY_REL = "tickets/stories/2026-10-17_failed_notch_keeps_switch_without_borrowers_story.md"
PATCH = "system_docs/patches/active/failed_notch_refusal_2026_10_18/"
NOW = datetime.datetime.now(datetime.UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


def swap(text: str, old: str, new: str, label: str) -> str:
    """Replace one anchored block; the anchor must occur exactly once."""
    if text.count(old) != 1:
        raise SystemExit("anchor %s found %d times" % (label, text.count(old)))
    return text.replace(old, new)


def edit_story(text: str) -> str:
    """Add the patch folder to Artifact Links and refresh the handoff's State and Next."""
    text = swap(text,
                "  - artifacts/failed_notch_refusal_20261018/ (melder_1's lane: re-runs, scripts, notes)\n",
                "  - artifacts/failed_notch_refusal_20261018/ (melder_1's lane: re-runs, scripts, notes)\n"
                "  - " + PATCH + " (architecture, two component and one code-description patch)\n",
                "artifact_links")
    old_state = ("  EPIC-2026-10-18-spell_identity_is_the_code (DECISION note). The fix sits in conduit.py and"
                 " spellbook.py (free;\n  melder_1 claims each from melder_0 by message before any edit; M1-30).\n"
                 "- Next: (1) re-run probe N1-N3 on the current tree, GIL off and on, and re-read the notch commit"
                 " path whole;\n  (2) patch docs and the owner's approval; (3) the fix, its tests, docs, notch and"
                 " the rebuild last.\n")
    new_state = ("  EPIC-2026-10-18-spell_identity_is_the_code (DECISION note). Re-verified on 0.2.8255 (MEASURE"
                 " note); the\n  mechanism - an undo inside the window - follows from the commit path (FACT note);"
                 " patch docs drafted\n  (PLAN note). The fix sits in spellbook.py, conduit.py, the error and the CCM"
                 " docstring (free; melder_1\n  claims each from melder_0 by message before any edit; M1-30).\n"
                 "- Next: (1) the owner's approval of the patch docs; (2) claim the files from melder_0; (3) red tests,"
                 " the fix,\n  docs, notch and the rebuild last.\n")
    return swap(text, old_state, new_state, "handoff")


def edit_artifacts(text: str) -> str:
    """Row the patch folder at the end of the active_artifacts region."""
    row = ("| " + STORY_REL + " | " + PATCH + " | patch_doc | active | promote_to_documentation | Architecture, two"
           " component and one code-description patch for the notch refusal; the owner's approval before any src"
           " edit. | " + NOW + " | REQUIRED |\n")
    return swap(text, "<!-- END USER-DEFINED: active_artifacts -->\n",
                row + "<!-- END USER-DEFINED: active_artifacts -->\n", "active_artifacts_end")


def main() -> None:
    """Re-read, edit, and write only with --apply."""
    if sys.argv[1:] not in (["--check"], ["--apply"]):
        raise SystemExit(__doc__)
    apply = sys.argv[1:] == ["--apply"]
    for rel, editor in ((STORY_REL, edit_story), ("artifact_board.md", edit_artifacts)):
        path = ROOT / rel
        raw = path.read_bytes()
        if b"\r\n" in raw:
            raise SystemExit(rel + ": CRLF")
        text = raw.decode("utf-8")
        new = editor(text)
        for line in new.split("\n"):
            if len(line) > 120 and rel == STORY_REL and not line.lstrip().startswith(("- ", "|")):
                raise SystemExit("long line: " + line)
        print("%s: %d -> %d lines" % (rel, text.count("\n"), new.count("\n")))
        if apply:
            path.write_bytes(new.encode("utf-8"))
            if path.read_bytes().decode("utf-8") != new:
                raise SystemExit(rel + ": read-back mismatch")
    print("NOW", NOW, "applied" if apply else "checked")


main()
