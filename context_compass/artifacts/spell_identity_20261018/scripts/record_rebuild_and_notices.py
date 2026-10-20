"""Record the 0.2.8258 rebuild and send M0-204 (melder_1) and M0-205 (melder_2) (melder_0, 2026-10-18).

The epic's FACT note and handoff, the board row, the two NOTICEs with their alerts and the roster row. One
all-or-nothing pass; `--write` flushes.
"""
import re
import sys

from docs_common import DocsRecord


class RebuildNotices(DocsRecord):
    """The rebuild record and the hand-backs."""

    R = "artifacts/spell_identity_20261018/runs/rebuild"

    def message(self, to: str, mid: str, claim: list, evidence: str) -> str:
        lines = [f"- TO: {to}", "  FROM: melder_0", f"  DATETIME: {self.now}", "  TYPE: NOTICE",
                 "  CLAIM: " + f"{mid}, " + claim[0]] + ["    " + c for c in claim[1:]] + \
                [f"  EVIDENCE: {evidence}", "  ACK_REQUESTED: false"]
        text = "\n".join(lines)
        self.check_width(text, mid)
        return text

    def run(self) -> None:
        note = self.note(self.now, "FACT", [
            "Rebuilt last for 0.2.8258, in a /tmp mirror and copied back byte for byte (writes in place; the mount",
            "refuses the builders' atomic replace, and a first in-repo asset run stopped there after writing three",
            "manifests identical to the mirror's): assets - agent documentation 470 entries, bind guard 630, system",
            "documents 4, all v0.2.8258; LLM bundles with --include-untracked - src 585 files, tests 1139, other 409",
            "(the mirror first missed the tracked `src/melder/__melder_cache__/__melder_cache__.py`; rebuilt with it).",
            "Repo-side --check: assets OK x3, bundles OK x3; no .git/index.lock. In the mirror after the rebuild:",
            "build_assets, llm_support, github_workflows and the identity tests - 731 passed, 1 skipped.",
        ], [self.whole(self.R + "/assets_check_repo.txt"), self.whole(self.R + "/llm_check_repo.txt"),
            self.whole(self.R + "/llm_build_mirror_2.txt")], [
            "S1 and S2's landing is complete; melder_1 and melder_2 are told."], [
            "Report to the owner; then S3-S5, each after its own patch."], "REQUIRED", 8)
        self.append_notes(self.EPIC, [note], "epic rebuild")
        text = self.read(self.EPIC)
        start = text.index("- Next: the rebuild for 0.2.8258 (assets and LLM bundles, last); then a NOTICE hands\n")
        end = text.index("\n\n## Project-Specific Additions")
        text = text[:start] + (f"- Done since: rebuilt for 0.2.8258 (FACT note of {self.now}); M0-204 hands spellbook.py\n"
                               "  and spell.py back to melder_1 and M0-205 tells melder_2 the rebuild carried its lane.\n"
                               "- Next: S3 (a changed binding revalidates), S4 (the refusal names the existing\n"
                               "  registration) and S5 (records holding one object twice), each after its own patch, on\n"
                               "  the owner's word.") + text[end:]
        self.stage(self.EPIC, text)
        self.set_field(self.EPIC, "Updated")
        board = self.read(self.BOARD).split("\n")
        k = [n for n, l in enumerate(board) if l.startswith("| spell_identity_is_the_code | ")]
        cells = board[k[0]].split(" | ")
        cells[1], cells[2] = "ready", "handoff"
        cells[6] = "S3-S5, each after its own patch, on the owner's word (S1 and S2 landed as 0.2.8257-0.2.8258)."
        cells[10] = self.now
        board[k[0]] = " | ".join(cells)
        text = "\n".join(board)
        text = self.once(text, "\n<!-- END USER-DEFINED: alerts -->",
                         f"\n- NEW MESSAGE for melder_1 (from melder_0, {self.now})\n- NEW MESSAGE for melder_2 (from "
                         f"melder_0, {self.now})\n<!-- END USER-DEFINED: alerts -->", "alerts")
        self.stage(self.BOARD, text)
        m1 = self.message("melder_1", "M0-204", [
            "re M1-40. S1 and S2 landed and turned in: 0.2.8257 and 0.2.8258 (`__version__` 0.2.8258), the release",
            "note's two sections, the system documents, the graph, the rebuild (both --check runs OK). Notch above",
            "0.2.8258 if you land after. spellbook.py and spell.py are yours again; I hold no src file. For S4's tests:",
            "one object is one spell, so a test that needs a second registration of a class binds a version of it",
            "(`version_of` in tests/_spell_identity_test_support.py) or a class of its own.",
        ], "context_compass/tickets/epics/2026-10-18_spell_identity_is_the_code_epic.md")
        m2 = self.message("melder_2", "M0-205", [
            "re M2-19. The 0.2.8258 rebuild (assets and LLM bundles, both --check runs OK) carries your docs,",
            "lessons 42-48 and your release-note bullet, which stays directly above the rebuild line; the docs checks passed",
            "over both lanes' docs (313 pages, check_site and check_seo clean of errors). Nothing is owed by your lane.",
        ], "context_compass/tickets/epics/2026-10-18_spell_identity_is_the_code_epic.md")
        mail = self.read(self.MAILBOX)
        rows = re.findall(r"^\| melder_0 \| claude \| 2026-09-26T22:24:06Z \| \S+ \| active \|$", mail, flags=re.M)
        if len(rows) != 1:
            sys.exit("roster")
        mail = mail.replace(rows[0], f"| melder_0 | claude | 2026-09-26T22:24:06Z | {self.now} | active |")
        mail = self.once(mail, "<!-- END USER-DEFINED: messages -->",
                         m1 + "\n" + m2 + "\n<!-- END USER-DEFINED: messages -->", "messages")
        self.stage(self.MAILBOX, mail)


def main() -> None:
    record = RebuildNotices("rebuild_notices")
    record.run()
    if "--write" not in sys.argv:
        print("CHECK OK", record.now, sorted(record.staged))
        return
    record.flush()


if __name__ == "__main__":
    main()
