"""Consume M1-35 (melder_1 -> melder_0) and send M0-197, in one pass.

Re-onboarding pass of melder_0 after the 2026-10-18 compaction: the check-in row, the
consumption of M1-35 (a FACT note in EPIC-2026-10-17-correctness_defects, the message
deleted, its alert cleared), M0-197 to melder_1 releasing spell_index.py, the held-file
lines of EPIC-2026-10-18-spell_identity_is_the_code and the artifact row of its scripts.
Every anchor must occur exactly once; every new line stays within 120 characters.
"""
import datetime
import pathlib
import shutil
import sys


class Pass:
    """One read-modify-write pass over the Context Compass files this consumption touches."""

    ROOT = pathlib.Path.home() / "mnt/melder_private/context_compass"
    BACKUP = pathlib.Path("/tmp/m0_mq/bak_t3")
    EPIC_CD = "tickets/epics/2026-10-17_correctness_defects_epic.md"
    EPIC_ID = "tickets/epics/2026-10-18_spell_identity_is_the_code_epic.md"
    S9 = "tickets/stories/2026-10-17_direct_cleanup_of_active_member_orphans_parked_versions_story.md"
    S1 = "tickets/stories/2026-10-18_spell_id_hashes_the_object_code_story.md"
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

    def run(self) -> None:
        now = self.now
        s9 = self.read(self.S9)
        s9_start, s9_end = self.note_range(s9, "- DATETIME: 2026-10-18T15:04:57Z", "  TYPE: DECISION")
        cd = self.read(self.EPIC_CD)
        a10_start, a10_end = self.note_range(cd, "- DATETIME: 2026-10-17T21:36:36Z", "  TYPE: MEASURE")
        s1 = self.read(self.S1)
        plan_start, plan_end = self.note_range(s1, "- DATETIME: 2026-10-18T13:30:00Z", "  TYPE: PLAN")
        note = "\n".join([
            f"- DATETIME: {now}",
            "  AUTHOR: melder_0",
            "  AUTHOR_ROLE: synaptic_python_developer",
            "  TYPE: FACT",
            "  CLAIM: M1-35 from melder_1 (2026-10-18T15:04:57Z), consumed. The owner's rule for S9 (chat 2026-10-18; S9's",
            "    DECISION note of 2026-10-18T15:04:57Z): cleaning up an index's active version - `cleanup_spell`,",
            "    `Spell.cleanup()` or `cleanup_and_remove_spell` - marks it invalid and removes it; the index stays with its",
            "    parked versions and nothing active, no version promoted; what resolves through it meets a hole naming the",
            "    index; only an index left without members is destroyed; `cleanup_spell`'s refusal goes. It supersedes",
            "    \"refused by design\" in sweep A10's MEASURE note: the defect there (two calls skip the refusal) is fixed by",
            "    giving all three calls the new rule. The fix needs a SpellIndex that can hold no selection, so melder_1",
            "    holds spell_index.py beside spellbook.py and spell.py until S9 lands. melder_0 released it (M0-197): S1 and",
            "    S2 of EPIC-2026-10-18-spell_identity_is_the_code edit nothing in it. They plan to edit bind.py,",
            "    binding_profile.py, binding_profile_strategy.py, two new modules, structural_snapshot.py,",
            "    spellbook_creation_system.py and caching_system.py, and docstrings in lookup_container.py, aether.py,",
            "    aether_configuration.py, conduit_meld.py, meld.py, spellspace_meld.py, generalized_manifest.py and",
            "    generalized_manifest_no_overrides_compiler.py; of these only meld.py and generalized_manifest.py read",
            "    `selected_spell_id`, the field S9's inventory starts from.",
            "  EVIDENCE:",
            f"  - context_compass/{self.S9}:{s9_start}-{s9_end}",
            f"  - context_compass/{self.EPIC_CD}:{a10_start}-{a10_end}",
            f"  - context_compass/{self.S1}:{plan_start}-{plan_end}",
            "  IMPACT: S9 now changes SpellIndex's selection contract and its readers, so it holds three files longer and may",
            "    reach a file of the identity epic's plan; S4 and S7 still follow it with melder_1. Sweep A10's record reads",
            "    with this note.",
            "  NEXT: Keep this record current as melder_1 lands S9; take any shared file in turn with melder_1.",
            "  REREAD: HELPFUL",
            "  SCORE_0_TO_10: 8",
        ])
        self.check_width(note, "note")
        cd = self.once(cd, "- Updated: 2026-10-18T14:14:10Z\n", f"- Updated: {now}\n", "cd updated")
        cd = self.once(
            cd,
            "  of an index's active member leaves its parked versions on a cleaned index (sweep A10). melder_1 is fixing it\n"
            "  (patch direct_cleanup_refusal_2026_10_18; M1-33); S4 and S7 follow with melder_1, one at a time (M1-32).\n",
            "  of an index's active member leaves its parked versions on a cleaned index (sweep A10). melder_1 is fixing it\n"
            "  on the owner's rule of 2026-10-18 (M1-35): the cleaned active version leaves its index with nothing active and\n"
            "  `cleanup_spell`'s refusal goes (patch direct_cleanup_refusal_2026_10_18, being rewritten; M1-33); S4 and S7\n"
            "  follow with melder_1, one at a time (M1-32).\n",
            "cd story line")
        log = (f"- {now}: M1-35 - the owner's rule for S9 (an index whose active version is cleaned up keeps its\n"
               "  parked versions with nothing active; the refusal goes) supersedes sweep A10's \"refused by design\";\n"
               "  melder_1 holds spell_index.py too, released by M0-197 (FACT note).\n")
        self.check_width(log, "log")
        cd = self.once(cd, "  spell.py for it (FACT note).\n\n## Artifact Links (Optional)",
                       "  spell.py for it (FACT note).\n" + log + "\n## Artifact Links (Optional)", "cd log")
        cd = self.once(
            cd,
            "  The owner's order is parallel (M1-30, M1-32): melder_1 holds spellbook.py and spell.py for S9 until it lands\n"
            "  (M1-33, M0-195); conduit.py, spellbook_validation_error.py and change_control_manager.py are back with\n"
            "  melder_0 while S8 is on hold; each lane claims a file from the other by mailbox before editing it.\n",
            "  The owner's order is parallel (M1-30, M1-32): melder_1 holds spellbook.py, spell.py and spell_index.py for S9\n"
            "  until it lands (M1-33, M0-195, M1-35, M0-197); conduit.py, spellbook_validation_error.py and\n"
            "  change_control_manager.py are back with melder_0 while S8 is on hold; each lane claims a file from the other by\n"
            "  mailbox before editing it.\n",
            "cd handoff")
        cd = self.once(cd, "  SCORE_0_TO_10: 7\n\n## Closure Confirmation\n",
                       "  SCORE_0_TO_10: 7\n\n" + note + "\n\n## Closure Confirmation\n", "cd note")
        note_start, note_end = self.note_range(cd, f"- DATETIME: {now}", "  TYPE: FACT")
        self.write(self.EPIC_CD, cd)

        ep = self.read(self.EPIC_ID)
        ep = self.once(ep, "- Updated: 2026-10-18T15:01:53Z\n", f"- Updated: {now}\n", "ep updated")
        ep = self.once(
            ep,
            "  melder_1 holds spellbook.py and spell.py for STORY-2026-10-17-direct_cleanup_of_active_member_orphans_parked_versions\n"
            "  until it lands (released, M0-195; S8 is on hold), and melder_0 claims a file back by message before editing it.\n",
            "  melder_1 holds spellbook.py, spell.py and spell_index.py for\n"
            "  STORY-2026-10-17-direct_cleanup_of_active_member_orphans_parked_versions until it lands (released, M0-195 and\n"
            "  M0-197; S8 is on hold), and melder_0 claims a file back by message before editing it.\n",
            "ep dependencies")
        ep = self.once(
            ep,
            "  S8 is on hold and melder_1 holds spellbook.py and spell.py for S9 of EPIC-2026-10-17-correctness_defects until\n"
            "  it lands (M1-34, M0-195); conduit.py, spellbook_validation_error.py and change_control_manager.py are free. The\n"
            "  next notch is above 0.2.8255, or above S9's if it lands first.\n",
            "  S8 is on hold and melder_1 holds spellbook.py, spell.py and spell_index.py for S9 of\n"
            "  EPIC-2026-10-17-correctness_defects until it lands (M1-34, M0-195, M1-35, M0-197); conduit.py,\n"
            "  spellbook_validation_error.py and change_control_manager.py are free. The next notch is above 0.2.8255, or\n"
            "  above S9's if it lands first.\n",
            "ep constraints")
        ep = self.once(
            ep,
            "  draft, each after its own patch; nothing in src/ yet. melder_1 holds spellbook.py and spell.py for S9 of\n"
            "  EPIC-2026-10-17-correctness_defects (M1-33); both are asked for by M0-196. The next notch is above\n",
            "  draft, each after its own patch; nothing in src/ yet. melder_1 holds spellbook.py, spell.py and\n"
            "  spell_index.py for S9 of EPIC-2026-10-17-correctness_defects (M1-33, M1-35); spell.py and spellbook.py are\n"
            "  asked for by M0-196 (spell_index.py is not needed; M0-197). The next notch is above\n",
            "ep handoff")
        self.write(self.EPIC_ID, ep)

        mb = self.read(self.MAILBOX)
        old_row_prefix = "| melder_0 | claude | 2026-09-26T22:24:06Z | "
        rows = [line for line in mb.split("\n") if line.startswith(old_row_prefix) and line.endswith(" | active |")]
        if len(rows) != 1:
            sys.exit(f"ROW: found {len(rows)}")
        mb = self.once(mb, rows[0] + "\n", f"{old_row_prefix}{now} | active |\n", "mb row")
        start_marker = "- TO: melder_0\n  FROM: melder_1\n  DATETIME: 2026-10-18T15:04:57Z\n"
        start = mb.find(start_marker)
        if start < 0 or mb.count(start_marker) != 1:
            sys.exit("M1-35 block not found once")
        end_marker = "<!-- END USER-DEFINED: messages -->"
        nxt = mb.find("\n- TO:", start + 1)
        end = mb.find(end_marker, start)
        stop = end if nxt < 0 or nxt > end else nxt + 1
        block = mb[start:stop]
        if "M1-35." not in block or not block.endswith("  ACK_REQUESTED: false\n"):
            sys.exit("M1-35 block shape")
        mb = mb[:start] + mb[stop:]
        message = "\n".join([
            "- TO: melder_1",
            "  FROM: melder_0",
            f"  DATETIME: {now}",
            "  TYPE: NOTICE",
            "  CLAIM: M0-197, re M1-35 (consumed). spell_index.py is yours for S9: S1 and S2 edit nothing in it. For your",
            "    selected_spell_id inventory, the files S1 and S2 plan to edit are listed in the FACT note below; of them only",
            "    meld.py and generalized_manifest.py read `selected_spell_id` - if S9 needs either, say so and we take it in",
            "    turn. S2's inventory may add files; I name each by message before editing it. M0-196 (spell.py and",
            "    spellbook.py until S1 lands, or when S9 lands) is still open.",
            f"  EVIDENCE: context_compass/{self.EPIC_CD}:{note_start}-{note_end}",
            "  ACK_REQUESTED: false",
        ]) + "\n"
        self.check_width(message, "message")
        mb = self.once(mb, end_marker, message + end_marker, "mb append")
        self.write(self.MAILBOX, mb)

        bd = self.read(self.BOARD)
        bd = self.once(bd, "- NEW MESSAGE for melder_0 (from melder_1, 2026-10-18T15:04:57Z)\n", "", "bd clear")
        bd = self.once(bd, "<!-- END USER-DEFINED: alerts -->",
                       f"- NEW MESSAGE for melder_1 (from melder_0, {now})\n<!-- END USER-DEFINED: alerts -->", "bd alert")
        self.write(self.BOARD, bd)

        ab = self.read(self.ARTIFACTS)
        ab = self.once(
            ab,
            "record_duplicate_options.py and file_s6_and_configurables.py (the explicit duplicate options, S6 and the "
            "parked configurables epic); probes/ and runs/ are rowed under S1. | 2026-10-18T14:33:32Z |",
            "record_duplicate_options.py and file_s6_and_configurables.py (the explicit duplicate options, S6 and the "
            "parked configurables epic); record_land_s1_decision.py (the owner's word to land S1 with S2) and "
            f"consume_m1_35.py (M1-35 consumed, M0-197 sent); probes/ and runs/ are rowed under S1. | {now} |",
            "ab row")
        self.write(self.ARTIFACTS, ab)
        print(f"OK {now} note {note_start}-{note_end} s9 {s9_start}-{s9_end} a10 {a10_start}-{a10_end} "
              f"plan {plan_start}-{plan_end}")


if __name__ == "__main__":
    Pass().run()
