"""Record F5's graph, notch and release-note pass in the task's Notes (melder_0, 2026-10-24).

All-or-nothing: anchors match once, lines fit 120 characters, no CR, and a file that changed since it was read
refuses the pass.
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path.home() / "mnt/melder_private/context_compass/artifacts/spell_identity_20261018/scripts"))
from cc_record import Record

TICKET = "tickets/tasks/2026-10-24_cache_file_write_failure_fails_meld_task.md"
SCRIPTS = "artifacts/cache_write_failure_20261024/scripts/"


class Pass(Record):
    """The note pass."""

    def checked_flush(self) -> None:
        for rel, before in self.original.items():
            if (self.ROOT / rel).read_text(encoding="utf-8") != before:
                sys.exit(f"RACE {rel}: changed since it was read; nothing written")
        self.flush()


def release_section() -> str:
    lines = (Record.REPO / "release_docs/next_version_release.md").read_text(encoding="utf-8").split("\n")
    start = lines.index("## A cache file that cannot be saved no longer fails a meld")
    end = lines.index("## Packaging and documentation")
    last = len(lines) - 1 if lines[-1] == "" else len(lines)
    return f"release_docs/next_version_release.md:{start + 1}-{end - 1}", \
        f"release_docs/next_version_release.md:{last - 4}-{last}"


def main() -> None:
    r = Pass("record_f5_graph_notch")
    section, packaging = release_section()
    version_lines = (Record.REPO / "src/melder/__version__.py").read_text(encoding="utf-8").split("\n")
    vline = version_lines.index('__version__ = "0.2.8266"') + 1
    fact = r.note(r.now, "FACT", [
        "F5 continued. The graph: the extractor walks the whole tree, and melder_1's descriptors are its own, so it",
        "ran into a mirror and only this lane's descriptors came back - caching_system.json, spellbook.json, spell.json",
        "and, after the notch, __version__.json (its source hash only) - each checked for unchanged authored fields.",
        "The three class nodes gained one responsibility each (CachingSystem's best-effort save and its owned slot",
        "`_refused_save_logged`; Spellbook's save seam; Spell's explicit save), read against the source and accepted",
        "with graph_walker - their stamps matched the pre-edit spans, so this lane's edit is the only delta - then",
        "normalized back to the extractor's format; reassembled, --check OK (593 sections, 28208 lines). The notch:",
        "__version__ read 0.2.8265 at this moment and now reads 0.2.8266. The release note: header 0.2.8266, the",
        "section \"A cache file that cannot be saved no longer fails a meld\" (Breaking for `Spell.emit_cache_file()`),",
        "a packaging bullet and the rebuild line for 0.2.8266."],
        [r.whole(SCRIPTS + "graph_descriptors_20261024.py"), r.whole(SCRIPTS + "notch_and_release_note_20261024.py"),
         section, packaging, f"src/melder/__version__.py:{vline}-{vline}"],
        ["Left as found, outside this lane: 220 stale nodes graph-wide, the build-asset and conduit_cloud.json",
         "descriptors one extraction behind, and melder_1's six descriptors (HolderDisposalEntry retired there) for",
         "melder_1's landing, which notches above 0.2.8266."],
        ["Send the NOTICEs (M0-216 to melder_1, M0-217 to melder_2), then close the task."], "REQUIRED", 8)
    text = r.once(r.read(TICKET), "\n\n## Context / Handoff Summary\n",
                  "\n\n" + fact + "\n\n## Context / Handoff Summary\n", "note")
    r.check_width(text, "ticket")
    r.stage(TICKET, text)
    r.set_field(TICKET, "Updated")
    r.checked_flush()


if __name__ == "__main__":
    main()
