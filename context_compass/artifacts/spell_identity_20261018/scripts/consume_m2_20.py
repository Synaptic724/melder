"""Consume M2-20 (melder_2, 2026-10-18T23:59:55Z): melder_2 edits the managed-teardown text of the two source documents.

M2-20 says that, on the owner's ruling in melder_2's chat ("if the root cleans up it only cleans up whats held by the
root, update the system docs please"), TASK-2026-10-18-document_root_teardown_cleans_only_what_it_holds edits the
managed-teardown text of src_architecture and src_components and regenerates both indexes - no src, notch or
release-note change - and asks this lane's next rebuild to carry the packaged system documents. Deletes M2-20,
refreshes the roster row, clears its alert and records the fact on the identity epic: the epic's last-step rebuild
waits for melder_2's edits. One all-or-nothing pass; `--write` flushes.
"""
import re
import sys
from typing import List

from cc_record import Record


class ConsumeM220(Record):
    """The M2-20 consumption."""

    TASK = "tickets/tasks/2026-10-18_document_root_teardown_cleans_only_what_it_holds_task.md"

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

    def mailbox(self) -> None:
        """Delete M2-20 and refresh the roster row."""
        lines = self.read(self.MAILBOX).split("\n")
        lines = self._delete_message(lines, "2026-10-18T23:59:55Z", "M2-20.")
        text = "\n".join(lines)
        rows = re.findall(r"^\| melder_0 \| claude \| 2026-09-26T22:24:06Z \| \S+ \| active \|$", text, flags=re.M)
        if len(rows) != 1:
            sys.exit(f"roster row: {len(rows)}")
        text = text.replace(rows[0], f"| melder_0 | claude | 2026-09-26T22:24:06Z | {self.now} | active |")
        self.stage(self.MAILBOX, text)

    def alerts(self) -> None:
        """Clear M2-20's alert."""
        text = self.read(self.BOARD)
        text = self.once(text, "- NEW MESSAGE for melder_0 (from melder_2, 2026-10-18T23:59:55Z)\n", "", "alert M2-20")
        self.stage(self.BOARD, text)

    def epic(self) -> None:
        """The FACT note."""
        task_lines = len((self.ROOT / self.TASK).read_text(encoding="utf-8").rstrip("\n").split("\n"))
        note = self.note(self.now, "FACT", [
            "M2-20 consumed (melder_2, 2026-10-18T23:59:55Z): on the owner's ruling in melder_2's chat (\"if the root",
            "cleans up it only cleans up whats held by the root, update the system docs please\") melder_2's",
            "TASK-2026-10-18-document_root_teardown_cleans_only_what_it_holds edits the managed-teardown text of",
            "src_architecture and src_components and regenerates both indexes; this lane's corrected release failure",
            "modes stay as written; no src, notch or release-note change. The packaged system documents go stale",
            "until this lane's next rebuild, which melder_2 asks to carry them.",
        ], [
            f"context_compass/{self.TASK}:1-{task_lines}",
        ], [
            "The epic's last-step rebuild runs after melder_2's edits and index regeneration are on the tree, so it",
            "packages both lanes' documents; this lane edits neither source document in its leftovers.",
        ], [
            "The graph leftovers; before the rebuild, confirm melder_2's edits are done (its task or a NOTICE).",
        ], "REQUIRED", 8)
        self.append_notes(self.EPIC, [note], "epic m2-20")
        self.set_field(self.EPIC, "Updated")


def main() -> None:
    record = ConsumeM220("m2_20")
    record.mailbox()
    record.alerts()
    record.epic()
    if "--write" not in sys.argv:
        print("CHECK OK", record.now, sorted(record.staged))
        return
    record.flush()


if __name__ == "__main__":
    main()
