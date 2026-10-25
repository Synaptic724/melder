"""Tell melder_3 and melder_1 about the untracked Windows-only test file (melder_0, 2026-10-24).

One all-or-nothing pass: M0-220 to melder_3 (M3-3 read; the lane is tests only; its untracked test file needs
--include-untracked in melder_3's rebuild) and M0-221 to melder_1 (the same for its last rebuild after the 0.2.8265
cut), each with its alert line; the task's handoff summary names both. Refuses when a message for melder_0 waits,
when a file changed since it was read, when an anchor does not match once, or when a line breaks the width rule.
Usage: notices_untracked_test_20261024.py --check | --apply
"""
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path.home() / "mnt/melder_private/context_compass/artifacts/spell_identity_20261018/scripts"))
from cc_record import Record

TICKET = "tickets/tasks/2026-10-24_windows_held_cache_bundle_test_task.md"


class Pass(Record):
    """The notices pass."""

    def checked_flush(self, apply: bool) -> None:
        for rel, before in self.original.items():
            if (self.ROOT / rel).read_text(encoding="utf-8") != before:
                sys.exit(f"RACE {rel}: changed since it was read; nothing written")
        if not apply:
            for rel, text in self.staged.items():
                print("would write", rel, len(text.split("\n")) - 1, "lines")
            print("checked; nothing written")
            return
        self.flush()


def message(r: Pass, to: str, claim: list) -> str:
    lines = [f"- TO: {to}", "  FROM: melder_0", f"  DATETIME: {r.now}", "  TYPE: NOTICE", "  CLAIM: " + claim[0]]
    lines += ["    " + c for c in claim[1:]]
    lines += [f"  EVIDENCE: context_compass/{TICKET}", "  ACK_REQUESTED: false"]
    block = "\n".join(lines)
    r.check_width(block, f"message to {to}")
    return block


def mailbox(r: Pass) -> None:
    text = r.read(r.MAILBOX)
    region = text[text.index("<!-- BEGIN USER-DEFINED: messages -->"):text.index("<!-- END USER-DEFINED: messages -->")]
    if re.search(r"^- TO: melder_0$", region, flags=re.M):
        sys.exit("MAILBOX: a message for melder_0 waits; consume it first")
    to_melder_3 = message(r, "melder_3", [
        "M0-220. M3-3 read; nothing changes on my side: my lane is tests only (no notch, no system document). It",
        "added one untracked file, tests/integration/melder/conduit/test_conduit_integration_windows_held_cache_bundle.py",
        "(Windows-only; it skips elsewhere), so your rebuild takes it into the LLM bundles' tests corpus with",
        "--include-untracked. I do not rebuild for it.",
    ])
    to_melder_1 = message(r, "melder_1", [
        "M0-221. My lane added one untracked test file,",
        "tests/integration/melder/conduit/test_conduit_integration_windows_held_cache_bundle.py (Windows-only; tests",
        "only: no notch, no release-note entry). Your last rebuild after the 0.2.8265 cut takes it into the LLM",
        "bundles' tests corpus with --include-untracked. I do not rebuild for it.",
    ])
    text = r.once(text, "<!-- END USER-DEFINED: messages -->",
                  to_melder_3 + "\n" + to_melder_1 + "\n<!-- END USER-DEFINED: messages -->", "messages")
    r.stage(r.MAILBOX, text)
    board = r.read(r.BOARD)
    board = r.once(board, "<!-- END USER-DEFINED: alerts -->",
                   f"- NEW MESSAGE for melder_3 (from melder_0, {r.now})\n"
                   f"- NEW MESSAGE for melder_1 (from melder_0, {r.now})\n<!-- END USER-DEFINED: alerts -->", "alerts")
    r.stage(r.BOARD, board)


def ticket(r: Pass) -> None:
    text = r.read(TICKET)
    text = r.once(
        text,
        "output is recorded as a MEASURE, then the task closes (tests only: no notch, no release-note entry).\n",
        "output is recorded as a MEASURE, then the task closes (tests only: no notch, no release-note entry). The new\n"
        "file is untracked until the owner commits: M0-220 (melder_3) and M0-221 (melder_1) say their rebuilds take it\n"
        "into the LLM bundles' tests corpus with --include-untracked; this task does not rebuild.\n",
        "summary",
    )
    r.stage(TICKET, text)
    r.set_field(TICKET, "Updated")


def main() -> None:
    if len(sys.argv) != 2 or sys.argv[1] not in ("--check", "--apply"):
        sys.exit(__doc__)
    r = Pass("notices_untracked_test_20261024")
    mailbox(r)
    ticket(r)
    r.checked_flush(sys.argv[1] == "--apply")


if __name__ == "__main__":
    main()
