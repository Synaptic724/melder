"""Consume M1-36 (melder_1 -> melder_0) after melder_0's second re-onboarding of 2026-10-18.

The check-in row, a FACT note in EPIC-2026-10-18-spell_identity_is_the_code recording M1-36, the held-file
lines of the epic and of S1 and S2, the message deleted, its alert cleared and the artifact row of the epic's
scripts. No reply: M1-36 asks for none. Every anchor must occur exactly once; new prose stays within 120 characters.
"""
import datetime
import pathlib
import shutil
import sys


class Pass:
    """One read-modify-write pass over the Context Compass files this consumption touches."""

    ROOT = pathlib.Path.home() / "mnt/melder_private/context_compass"
    BACKUP = pathlib.Path("/tmp/m0_mq/bak_t5")
    EPIC_ID = "tickets/epics/2026-10-18_spell_identity_is_the_code_epic.md"
    S9 = "tickets/stories/2026-10-17_direct_cleanup_of_active_member_orphans_parked_versions_story.md"
    S1 = "tickets/stories/2026-10-18_spell_id_hashes_the_object_code_story.md"
    S2 = "tickets/stories/2026-10-18_binding_manifest_hash_story.md"
    MAILBOX = "mailbox_board.md"
    BOARD = "attention_board.md"
    ARTIFACTS = "artifact_board.md"

    def __init__(self) -> None:
        self.now = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    def read(self, rel: str) -> str:
        return (self.ROOT / rel).read_text(encoding="utf-8")

    def write(self, rel: str, text: str) -> None:
        if "\r" in text:
            sys.exit(f"CR in {rel}")
        shutil.copy2(self.ROOT / rel, self.BACKUP / pathlib.Path(rel).name)
        (self.ROOT / rel).write_text(text, encoding="utf-8", newline="\n")

    @staticmethod
    def once(text: str, old: str, new: str, label: str) -> str:
        count = text.count(old)
        if count != 1:
            sys.exit(f"ANCHOR {label}: found {count}")
        return text.replace(old, new)

    @staticmethod
    def check_width(block: str, label: str) -> None:
        for line in block.split("\n"):
            if len(line) > 120 and "context_compass/" not in line:
                sys.exit(f"WIDTH {label}: {len(line)}: {line}")

    @staticmethod
    def note_range(text: str, marker: str, type_line: str) -> tuple:
        lines = text.split("\n")
        hits = [i for i, line in enumerate(lines)
                if line == marker and i + 3 < len(lines) and lines[i + 3] == type_line]
        if len(hits) != 1:
            sys.exit(f"NOTE {marker} {type_line}: found {len(hits)}")
        end = hits[0] + 1
        while end < len(lines) and lines[end] != "":
            end += 1
        return hits[0] + 1, end

    def epic(self) -> None:
        now = self.now
        s9 = self.read(self.S9)
        tr_start, tr_end = self.note_range(s9, "- DATETIME: 2026-10-18T15:27:07Z", "  TYPE: TRADEOFF")
        fa_start, fa_end = self.note_range(s9, "- DATETIME: 2026-10-18T15:27:07Z", "  TYPE: FACT")
        note = "\n".join([
            f"- DATETIME: {now}",
            "  AUTHOR: melder_0",
            "  AUTHOR_ROLE: synaptic_python_developer",
            "  TYPE: FACT",
            "  CLAIM: M1-36 from melder_1 (2026-10-18T15:27:07Z, ACK), consumed; it answers M0-196 and M0-197. The owner",
            "    reopened S9's rule - refusal on all three doors, or the hole rule (S9's TRADEOFF note) - and melder_1 sends",
            "    his pick as M1-37. Under the refusal S9 is a check in `cleanup_and_remove_spell` (spellbook.py) and a",
            "    Raises entry on `Spell.cleanup` (spell.py): it lands first, both files come back by message right after,",
            "    and S1 and S2 notch above it. Under the hole rule both files come here at once and S9 follows S1, then also",
            "    needing conduit.py and details.py, maybe meld.py, each claimed by message first. melder_1 edits neither",
            "    file before M1-37; spell_index.py stays with melder_1 (M0-197).",
            "  EVIDENCE:",
            f"  - context_compass/{self.S9}:{tr_start}-{tr_end}",
            f"  - context_compass/{self.S9}:{fa_start}-{fa_end}",
            "  IMPACT: S1 and S2's edits in spell.py and spellbook.py wait for M1-37 either way; the patch updates, S2's",
            "    component patch and the blast-radius run do not need them. Under the hole rule S9 would edit details.py",
            "    and maybe meld.py, which S1's statement sweep also touches (their \"fingerprint\" docstrings): those files",
            "    are taken in turn.",
            "  NEXT: Apply S1's patch updates and S2's component patch; the blast-radius run; read the mailbox for M1-37.",
            "  REREAD: REQUIRED",
            "  SCORE_0_TO_10: 8",
        ])
        self.check_width(note, "note")
        ep = self.read(self.EPIC_ID)
        ep = self.once(ep, "- Updated: 2026-10-18T15:15:34Z\n", f"- Updated: {now}\n", "ep updated")
        ep = self.once(
            ep,
            "  asked for by M0-196 (spell_index.py is not needed; M0-197). The next notch is above\n"
            "  0.2.8255, or above S9's.\n",
            "  asked for by M0-196 (spell_index.py is not needed; M0-197); M1-36: their order waits for the owner's pick\n"
            "  in S9 - under the refusal S9 lands first and hands both back, under the hole rule both come here at once\n"
            "  and S9 follows S1 (M1-37). The next notch is above 0.2.8255, or above S9's.\n",
            "ep handoff")
        ep = self.once(ep, "  SCORE_0_TO_10: 9\n\n## Closure Confirmation\n",
                       "  SCORE_0_TO_10: 9\n\n" + note + "\n\n## Closure Confirmation\n", "ep note")
        self.write(self.EPIC_ID, ep)
        self.note = self.note_range(ep, f"- DATETIME: {now}", "  TYPE: FACT")

    def stories(self) -> None:
        s1 = self.read(self.S1)
        s1 = self.once(
            s1,
            "  and spell.py are melder_1's for S9 and asked for (M0-196).\n",
            "  and spell.py are melder_1's for S9 and asked for (M0-196); their order waits for the owner's pick in S9\n"
            "  (M1-36, M1-37).\n",
            "s1 handoff")
        self.write(self.S1, s1)
        s2 = self.read(self.S2)
        s2 = self.once(
            s2,
            "  2026-10-18T15:01:53Z); spell.py is melder_1's for S9 and asked for (M0-196).\n",
            "  2026-10-18T15:01:53Z); spell.py is melder_1's for S9 and asked for (M0-196); its order waits for the\n"
            "  owner's pick in S9 (M1-36, M1-37).\n",
            "s2 handoff")
        self.write(self.S2, s2)

    def boards(self) -> None:
        now = self.now
        mb = self.read(self.MAILBOX)
        prefix = "| melder_0 | claude | 2026-09-26T22:24:06Z | "
        rows = [line for line in mb.split("\n") if line.startswith(prefix) and line.endswith(" | active |")]
        if len(rows) != 1:
            sys.exit(f"ROW: found {len(rows)}")
        mb = self.once(mb, rows[0] + "\n", f"{prefix}{now} | active |\n", "mb row")
        marker = "- TO: melder_0\n  FROM: melder_1\n  DATETIME: 2026-10-18T15:27:07Z\n"
        if mb.count(marker) != 1:
            sys.exit("M1-36 block not found once")
        start = mb.find(marker)
        end_marker = "<!-- END USER-DEFINED: messages -->"
        nxt = mb.find("\n- TO:", start + 1)
        end = mb.find(end_marker, start)
        stop = end if nxt < 0 or nxt > end else nxt + 1
        block = mb[start:stop]
        if "M1-36," not in block or not block.endswith("  ACK_REQUESTED: false\n"):
            sys.exit("M1-36 block shape")
        mb = mb[:start] + mb[stop:]
        self.write(self.MAILBOX, mb)
        bd = self.read(self.BOARD)
        bd = self.once(bd, "- NEW MESSAGE for melder_0 (from melder_1, 2026-10-18T15:27:07Z)\n", "", "bd clear")
        self.write(self.BOARD, bd)
        ab = self.read(self.ARTIFACTS)
        ab = self.once(
            ab,
            f"consume_m1_35.py (M1-35 consumed, M0-197 sent); probes/ and runs/ are rowed under S1. | 2026-10-18T15:15:34Z |",
            "consume_m1_35.py (M1-35 consumed, M0-197 sent); consume_m1_36.py (M1-36 consumed) and "
            "update_patches_b_strict.py (S1's patches for decision B and strict uniqueness, S2's binding manifest and "
            f"creation-cache patch); probes/ and runs/ are rowed under S1. | {now} |",
            "ab row")
        self.write(self.ARTIFACTS, ab)

    def run(self) -> None:
        self.epic()
        self.stories()
        self.boards()
        print(f"OK {self.now} note {self.note[0]}-{self.note[1]}")


if __name__ == "__main__":
    Pass().run()
