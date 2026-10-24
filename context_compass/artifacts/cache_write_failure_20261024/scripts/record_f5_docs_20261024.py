"""Record F5's system-document pass in the task's Notes (melder_0, 2026-10-24).

All-or-nothing: anchors match once, lines fit 120 characters, no CR, and a file that changed since it was read
refuses the pass.
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path.home() / "mnt/melder_private/context_compass/artifacts/spell_identity_20261018/scripts"))
from cc_record import Record

TICKET = "tickets/tasks/2026-10-24_cache_file_write_failure_fails_meld_task.md"
ARCH = "system_docs/src_architecture.md"
COMP = "system_docs/src_components.md"
SCRIPT = "artifacts/cache_write_failure_20261024/scripts/apply_system_docs_20261024.py"


class Pass(Record):
    """The note pass."""

    def checked_flush(self) -> None:
        for rel, before in self.original.items():
            if (self.ROOT / rel).read_text(encoding="utf-8") != before:
                sys.exit(f"RACE {rel}: changed since it was read; nothing written")
        self.flush()


def main() -> None:
    r = Pass("record_f5_docs")
    fact = r.note(r.now, "FACT", [
        "F5, the system documents: src_architecture carries a new first operational invariant (best-effort cache saves:",
        "the bool, the per-writer temp file, the Windows-only rename retry, one WARNING per bundle, the flag left",
        "cleared, the locks), two failure modes (fixed in 0.2.8266; Breaking for `Spell.emit_cache_file()`), the code",
        "map (caching_system.py 1122, spellbook.py 8398, spell.py 2035 lines) and a summary entry; src_components a",
        "best-effort-saves bullet in the Spellbook Core cache list, a failure-mode bullet, step 6 of the cold-cache flow,",
        "the three extents and a summary entry. Every numeric citation into spellbook.py past the edit moved 20 lines;",
        "the script proves all 24 pairs on a line map of HEAD's and today's spellbook.py, and repoints the stale",
        "settle-then-inherit (:6971-6983, :6984) and `_run_structural_phases` (:7423) citations, checked by content.",
        "Checks: both indexes regenerated, --check OK (5700 and 12544 lines); the content-preservation multiset diff",
        "lists only the remapped citations and the remeasured code-map fields; the portability and absolute-path greps",
        "find nothing; the citation-bounds recipe flags only two bare file names in a 2026-10-16 summary entry",
        "(src_components 12053-12054, pre-existing). Rubric not run: a targeted edit. The first try of the script",
        "stopped on three seam citations that carry a description and wrote nothing."],
        [r.doc_block(ARCH, "- Cache saves are best-effort (2026-10-24"),
         r.doc_block(ARCH, "- Fixed in 0.2.8266: a creation-cache save"),
         r.doc_block(ARCH, "- Breaking (0.2.8266): `Spell.emit_cache_file()`"),
         r.doc_block(COMP, "- Best-effort saves (2026-10-24, 0.2.8266)"),
         r.doc_block(COMP, "- A creation-cache save the operating system refuses raises nothing"),
         r.whole(SCRIPT)],
        ["The two documents describe what landed, with citations that point at their code; the packaged copies",
         "follow at the rebuild."],
        ["The graph: extract with --strict on Python 3.14, read the drift report, re-accept the changed nodes after",
         "reading them, reassemble and check."], "REQUIRED", 8)
    text = r.once(r.read(TICKET), "\n\n## Context / Handoff Summary\n",
                  "\n\n" + fact + "\n\n## Context / Handoff Summary\n", "note")
    r.check_width(text, "ticket")
    r.stage(TICKET, text)
    r.set_field(TICKET, "Updated")
    r.checked_flush()


if __name__ == "__main__":
    main()
