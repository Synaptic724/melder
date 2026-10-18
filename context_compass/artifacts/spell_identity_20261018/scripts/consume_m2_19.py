"""Consume M2-19 (melder_2, 2026-10-18T23:04:33Z): melder_2's release-note bullet is on the tree now (melder_0).

M2-19 says that, on the owner's directive in melder_2's chat (finish now, no rebuild in that lane), melder_2 added
its one release-note bullet - the one naming docs/intermediate/managed-spells.md, directly above the closing rebuild
line of `## Packaging and documentation` - runs no rebuild, and closes S3 and its epic; this landing's release-note
edit must re-read the file and keep that bullet above the rebuild line, and this landing's rebuild carries melder_2's
docs and release-note changes. Deletes M2-19, refreshes the roster row, clears its alert and records the fact on the
identity epic. One all-or-nothing pass; `--write` flushes.
"""
import re
import sys
from typing import List, Tuple

from cc_record import Record


class ConsumeM219(Record):
    """The M2-19 consumption."""

    NOTE_REL = "release_docs/next_version_release.md"

    @staticmethod
    def _delete_message(lines: List[str], when: str, tag: str) -> List[str]:
        """Delete the message to melder_0 from melder_2 sent at `when`; it must carry `tag`."""
        starts = [i for i in range(len(lines) - 2)
                  if lines[i] == "- TO: melder_0" and lines[i + 1] == "  FROM: melder_2"
                  and lines[i + 2] == f"  DATETIME: {when}"]
        if len(starts) != 1:
            sys.exit(f"{tag} block: {len(starts)}")
        end = starts[0]
        while not lines[end].startswith("  ACK_REQUESTED: "):
            end += 1
        if tag not in "\n".join(lines[starts[0]:end + 1]):
            sys.exit(f"{tag} block does not carry {tag}")
        return lines[:starts[0]] + lines[end + 1:]

    def bullet_range(self) -> Tuple[int, int]:
        """The 1-based line range of melder_2's bullet in the running release note, checked to sit above the rebuild
        line."""
        lines = (self.REPO / self.NOTE_REL).read_text(encoding="utf-8").split("\n")
        hits = [i for i, line in enumerate(lines) if "docs/intermediate/managed-spells.md" in line]
        if not hits:
            sys.exit("no managed-spells bullet in the release note")
        start = hits[0]
        while not lines[start].startswith("- "):
            start -= 1
        end = self.block_end(lines, start)
        rebuild = [i for i, line in enumerate(lines) if line.startswith("- Agent documentation metadata and the")]
        if len(rebuild) != 1 or rebuild[0] <= end:
            sys.exit(f"rebuild line {rebuild} not below the bullet ending {end + 1}")
        return start + 1, end + 1

    def mailbox(self) -> None:
        """Delete M2-19 and refresh the roster row."""
        lines = self.read(self.MAILBOX).split("\n")
        lines = self._delete_message(lines, "2026-10-18T23:04:33Z", "M2-19,")
        text = "\n".join(lines)
        rows = re.findall(r"^\| melder_0 \| claude \| 2026-09-26T22:24:06Z \| \S+ \| active \|$", text, flags=re.M)
        if len(rows) != 1:
            sys.exit(f"roster row: {len(rows)}")
        text = text.replace(rows[0], f"| melder_0 | claude | 2026-09-26T22:24:06Z | {self.now} | active |")
        self.stage(self.MAILBOX, text)

    def alerts(self) -> None:
        """Clear M2-19's alert."""
        text = self.read(self.BOARD)
        text = self.once(text, "- NEW MESSAGE for melder_0 (from melder_2, 2026-10-18T23:04:33Z)\n", "", "alert M2-19")
        self.stage(self.BOARD, text)

    def epic(self) -> None:
        """The FACT note and the handoff lines."""
        first, last = self.bullet_range()
        note = self.note(self.now, "FACT", [
            "M2-19 consumed (melder_2, 2026-10-18T23:04:33Z): on the owner's directive in melder_2's chat (23:01Z: finish",
            "now, no rebuild in that lane) melder_2 added its one release-note bullet - the managed spells chapter,",
            "docs/intermediate/managed-spells.md - directly above the closing rebuild line of `## Packaging and",
            "documentation`, runs no rebuild and closes S3 and its epic; its writes to docs/ and release_docs/ end there.",
            "So this landing's release-note pass re-reads the file and keeps that bullet above the rebuild line, and this",
            "landing's rebuild is the one that carries melder_2's docs and release-note changes.",
        ], [
            f"{self.NOTE_REL}:{first}-{last}",
            "context_compass/tickets/stories/2026-10-18_managed_spell_sphinx_docs_story.md",
        ], [
            "No ordering wait remains on melder_2's side; the docs checks before the rebuild still cover both lanes'",
            "docs, and the rebuild line names this landing's version.",
        ], [
            "The tests system documents and the source follow-ups.",
        ], "HELPFUL", 7)
        self.append_notes(self.EPIC, [note], "epic m2-19")
        text = self.read(self.EPIC)
        old = ("- Next: the tests system documents and the source follow-ups, the graph, the notches, the release\n"
               "  note, the docs checks, the closure, the rebuild last; then a NOTICE hands\n"
               "  spellbook.py and spell.py back to melder_1 (M1-40) and another tells melder_2 the rebuild\n"
               "  is done.\n")
        new = (f"- Done since: M2-19 consumed - melder_2's release-note bullet is on the tree, above the rebuild line,\n"
               f"  and its lane runs no rebuild (FACT note of {self.now}).\n"
               "- Next: the tests system documents and the source follow-ups, the graph, the notches, the release\n"
               "  note (melder_2's bullet kept above the rebuild line), the docs checks, the closure, the rebuild last;\n"
               "  then a NOTICE hands spellbook.py and spell.py back to melder_1 (M1-40) and another tells melder_2\n"
               "  the rebuild carried its docs and its bullet.\n")
        text = self.once(text, old, new, "epic handoff")
        self.stage(self.EPIC, text)
        self.set_field(self.EPIC, "Updated")


def main() -> None:
    record = ConsumeM219("m2_19")
    record.mailbox()
    record.alerts()
    record.epic()
    if "--write" not in sys.argv:
        print("CHECK OK", record.now, sorted(record.staged))
        return
    record.flush()


if __name__ == "__main__":
    main()
