"""Consume M1-37 and record the owner's crystallizer call (melder_0, after its third re-onboarding of 2026-10-18).

The check-in row; M1-37 copied into EPIC-2026-10-18-spell_identity_is_the_code as a FACT note, deleted from the
mailbox and its alert cleared; the owner's mid-turn word as a DECISION note in the epic (the binding hash goes into
the SpellCrystal in this landing, the third-party reading accepted, keep moving, S9's refusal first) and in S2,
whose earlier record deferral it supersedes - S2's Requirements, Acceptance Criteria, EXIT_GATE, task list, decision
log and handoff follow. Ranges are computed from the files, never typed. All-or-nothing: nothing is written unless
every anchor matches exactly once; new prose stays within 120 characters; no CR is written.
"""
import datetime
import pathlib
import shutil
import sys


class Pass:
    """One staged read-modify-write pass over the Context Compass files this record touches."""

    ROOT = pathlib.Path.home() / "mnt/melder_private/context_compass"
    BACKUP = pathlib.Path("/tmp/m0_mq/bak_t6")
    EPIC = "tickets/epics/2026-10-18_spell_identity_is_the_code_epic.md"
    S2 = "tickets/stories/2026-10-18_binding_manifest_hash_story.md"
    S9 = "tickets/stories/2026-10-17_direct_cleanup_of_active_member_orphans_parked_versions_story.md"
    MAILBOX = "mailbox_board.md"
    BOARD = "attention_board.md"
    ARCH = "system_docs/patches/active/spell_identity_is_the_code_2026_10_18/architecture_patch.md"
    OWNER = ("\"ok cool make sure you land the binding hash going into crystallizer too please, those 3 things for "
             "library version are fine, and lets keep moving on this, to finish it off, M1 is working on refusal "
             "yeah\"")

    def __init__(self) -> None:
        self.now = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        self.staged: dict = {}

    def read(self, rel: str) -> str:
        if rel in self.staged:
            return self.staged[rel]
        return (self.ROOT / rel).read_text(encoding="utf-8")

    def stage(self, rel: str, text: str) -> None:
        self.staged[rel] = text

    @staticmethod
    def once(text: str, old: str, new: str, label: str) -> str:
        count = text.count(old)
        if count != 1:
            sys.exit(f"ANCHOR {label}: found {count}")
        for line in new.split("\n"):
            if len(line) > 120 and "context_compass/" not in line and not line.startswith("| "):
                sys.exit(f"WIDTH {label}: {len(line)}: {line}")
        return text.replace(old, new)

    def note_range(self, rel: str, marker: str, type_line: str) -> str:
        lines = self.read(rel).split("\n")
        hits = [i for i, line in enumerate(lines)
                if line == marker and i + 3 < len(lines) and lines[i + 3] == type_line]
        if len(hits) != 1:
            sys.exit(f"NOTE {rel} {marker} {type_line}: found {len(hits)}")
        end = hits[0] + 1
        while end < len(lines) and lines[end] != "":
            end += 1
        return f"context_compass/{rel}:{hits[0] + 1}-{end}"

    def doc_span(self, rel: str, first: str, last: str) -> str:
        lines = self.read(rel).split("\n")
        starts = [i for i, line in enumerate(lines) if line.startswith(first)]
        if len(starts) != 1:
            sys.exit(f"SPAN {first}: {len(starts)}")
        end = next((i for i in range(starts[0], len(lines)) if last in lines[i]), None)
        if end is None:
            sys.exit(f"SPAN END {last}")
        return f"context_compass/{rel}:{starts[0] + 1}-{end + 1}"

    @staticmethod
    def note(now: str, kind: str, claim: list, evidence: list, impact: list, nxt: list, reread: str,
             score: int) -> str:
        lines = [f"- DATETIME: {now}", "  AUTHOR: melder_0", "  AUTHOR_ROLE: synaptic_python_developer",
                 f"  TYPE: {kind}", "  CLAIM: " + claim[0]] + ["    " + c for c in claim[1:]]
        if len(evidence) == 1:
            lines.append("  EVIDENCE: " + evidence[0])
        else:
            lines += ["  EVIDENCE:"] + [f"  - {e}" for e in evidence]
        lines += ["  IMPACT: " + impact[0]] + ["    " + c for c in impact[1:]]
        lines += ["  NEXT: " + nxt[0]] + ["    " + c for c in nxt[1:]]
        lines += [f"  REREAD: {reread}", f"  SCORE_0_TO_10: {score}"]
        return "\n".join(lines)

    def mailbox(self) -> None:
        text = self.read(self.MAILBOX)
        text = self.once(text, "| melder_0 | claude | 2026-09-26T22:24:06Z | 2026-10-18T15:38:29Z | active |",
                         f"| melder_0 | claude | 2026-09-26T22:24:06Z | {self.now} | active |", "row")
        head = "- TO: melder_0\n  FROM: melder_1\n  DATETIME: 2026-10-18T15:41:09Z\n"
        if text.count(head) != 1:
            sys.exit("ANCHOR M1-37 head")
        start = text.index(head)
        end = text.index("<!-- END USER-DEFINED: messages -->", start)
        block = text[start:end]
        if "CLAIM: M1-37" not in block or not block.endswith("ACK_REQUESTED: false\n") or block.count("- TO:") != 1:
            sys.exit("M1-37 block shape")
        self.stage(self.MAILBOX, text[:start] + text[end:])
        board = self.read(self.BOARD)
        board = self.once(board, "- NEW MESSAGE for melder_0 (from melder_1, 2026-10-18T15:41:09Z)\n", "", "alert")
        self.stage(self.BOARD, board)

    def epic(self) -> None:
        now = self.now
        fact = self.note(now, "FACT", [
            "M1-37 from melder_1 (2026-10-18T15:41:09Z, NOTICE), consumed; it answers M0-196 (M1-36). The owner chose",
            "the refusal for S9 of EPIC-2026-10-17-correctness_defects: all three cleanup doors refuse the active",
            "member of an index that holds parked versions, the messages naming the remedies; Book teardown is",
            "unaffected. S9 lands first: its edits are `cleanup_and_remove_spell`'s check and docstring,",
            "`_dispose_spell`'s refusal text and `cleanup_spell`'s docstring in spellbook.py, and `Spell.cleanup`'s",
            "Raises entry in spell.py, nothing else. melder_1 hands both files back by message right after its",
            "landing, rebuild included, and S1 notches above it; spell_index.py and conduit.py are melder_0's again",
            "now. Since then the owner gave his word on those edits (E1-E7) and named the notch 0.2.8256 (melder_1's",
            "DECISION note of 2026-10-18T16:02:48Z).",
        ], [
            self.note_range(self.S9, "- DATETIME: 2026-10-18T15:41:09Z", "  TYPE: DECISION"),
            self.note_range(self.S9, "- DATETIME: 2026-10-18T16:02:48Z", "  TYPE: DECISION"),
        ], [
            "S1 and S2 edit spell.py and spellbook.py only after melder_1's hand-back; until then they are built",
            "and tested in a /tmp working mirror. The next notches are above 0.2.8256.",
        ], ["The owner's crystallizer call (DECISION note below)."], "REQUIRED", 8)
        decision = self.note(now, "DECISION", [
            "The owner (chat 2026-10-18, mid-turn): " + self.OWNER[:62],
            self.OWNER[62:168],
            self.OWNER[168:] + ". So: (1) the binding hash goes into the SpellCrystal record in",
            "this landing, with S2, not in S5: S2's DECISION note of 2026-10-18T15:45:30Z, point (1), is superseded,",
            "S2's Requirements, Acceptance Criteria and EXIT_GATE say so again, and a record patch (the field, its",
            "RecordVersion, what restore and graft do with a recorded hash) is written and linked before any",
            "crystallizer code. (2) The third-party reading stated for him in the architecture patch - an object of an",
            "installed package hashed as its type, its distribution version and its address-free repr, an installed",
            "class, metaclass or function named with its distribution version - is accepted as written. (3) S9 takes",
            "the refusal and lands first (M1-37). (4) Keep moving to finish: S1 and S2 are built and run in a /tmp",
            "working mirror while S9 lands, and copied into the repository once spellbook.py and spell.py are back.",
        ], [
            self.note_range(self.S2, "- DATETIME: 2026-10-18T15:45:30Z", "  TYPE: DECISION"),
            self.doc_span(self.ARCH, "- DECIDED (owner, 2026-10-18; S1): B", "the owner can narrow it to type"),
            self.doc_span(self.ARCH, "8. Installed third-party code (decision B)", "nothing else of the package"),
        ], [
            "S2 gains the crystal's record (spell_crystal.py, the record version, and the replays in restore_engine.py",
            "and graft_runner.py where they read it); the architecture patch's matrix and S2's mapping gain the",
            "record row; the third-party reading is final, not for him to narrow.",
        ], ["Record the blast-radius run; read the crystal, the record version and both replays whole; write the",
            "record patch."], "REQUIRED", 9)
        text = self.read(self.EPIC)
        text = self.once(text, "\n\n## Closure Confirmation\n",
                         "\n\n" + fact + "\n\n" + decision + "\n\n## Closure Confirmation\n", "epic notes")
        text = self.once(text, "- Updated: 2026-10-18T15:45:30Z\n", f"- Updated: {now}\n", "epic updated")
        text = self.once(
            text,
            "- 2026-10-18T15:45:30Z: Milestone 1 met - S1's patches updated, S2's written (FACT note).\n",
            "- 2026-10-18T15:45:30Z: Milestone 1 met - S1's patches updated, S2's written (FACT note).\n"
            f"- {now}: M1-37 consumed - S9 takes the refusal and lands first (FACT note); the owner's word - the\n"
            "  binding hash goes into the SpellCrystal in this landing, the third-party reading is accepted, keep\n"
            "  moving (DECISION note).\n", "epic log")
        old_state = text[text.index("- State: in_progress (melder_0), implementation. The owner's word (DECISION"):
                         text.index("\n## Project-Specific Additions")]
        new_state = "\n".join([
            "- State: in_progress (melder_0), implementation. The owner's word (DECISION note of 2026-10-18T15:01:53Z): land S1",
            "  with S2's cache keys now, duplicates strictly refused (S6 parked in the backlog), binding and caching",
            "  patterns later (EPIC-2026-10-18-identity_and_caching_configurables); and (DECISION note of",
            f"  {now}) the binding hash goes into the SpellCrystal in this landing and the third-party reading",
            "  is accepted as written. His earlier calls and decisions stand (DECISION notes of 2026-10-18T12:15:14Z,",
            "  13:06:51Z, 14:14:10Z). S1 and S2 in_progress; S3-S5 draft, each after its own patch; nothing in src/ yet.",
            "  S9 of EPIC-2026-10-17-correctness_defects takes the refusal and lands first as 0.2.8256 (M1-37;",
            "  melder_1's DECISION note of 2026-10-18T16:02:48Z); melder_1 hands spellbook.py and spell.py back by",
            "  message after its rebuild, and S1 and S2 notch above it; spell_index.py and conduit.py are melder_0's.",
            "- Done since: M1-37 consumed and the owner's crystallizer call recorded (FACT and DECISION notes of",
            f"  {now}).",
            "- Next: (1) record the blast-radius run (101 new failures, none a Melder defect); (2) the crystallizer",
            "  record patch for S2; (3) S1 and S2 built in a /tmp working mirror while S9 lands, then the landing pass -",
            "  red tests, src, green, the moved tests, the whole tree with the GIL off and on, docs, notches, the",
            "  rebuild last.",
            "",
        ])
        if "- Next: (1) the blast-radius run in a /tmp mirror; (2) M1-37 sets the order with S9;" not in old_state:
            sys.exit("epic handoff shape")
        text = self.once(text, old_state, new_state, "epic handoff")
        self.stage(self.EPIC, text)

    def s2(self) -> None:
        now = self.now
        text = self.read(self.S2)
        text = self.once(text, "- Updated: 2026-10-18T15:45:30Z\n", f"- Updated: {now}\n", "s2 updated")
        text = self.once(
            text,
            "- EXIT_GATE: a binding change without a code change misses both cache tiers; a restore rebuilds the same manifest\n"
            "  from the record (its binding hash joins the record in S5); byte-identical across processes; docs.\n",
            "- EXIT_GATE: a binding change without a code change misses both cache tiers; the SpellCrystal records the\n"
            "  binding hash and a restore or graft rebuilds the same manifest from the record; byte-identical across\n"
            "  processes; docs.\n", "s2 exit")
        text = self.once(
            text,
            "- The Spell carries the manifest and its hash; `Spell.describe` shows both. The record (the SpellCrystal) already\n"
            "  records every field and a restore rebuilds the manifest through bind; the hash joins the record in S5.\n",
            "- The Spell carries the manifest and its hash; `Spell.describe` shows both. The SpellCrystal records the binding\n"
            "  hash beside the fields it already records, and a restore or graft rebuilds the manifest through bind (the\n"
            "  owner, 2026-10-18: \"make sure you land the binding hash going into crystallizer too\"); the record patch\n"
            "  says what a rebuilt manifest whose hash differs from the recorded one does.\n", "s2 requirement")
        text = self.once(
            text,
            "- A restore rebuilds the same manifest and binding hash from the record (the SpellCrystal records every\n"
            "  field today).\n",
            "- The SpellCrystal records the binding hash, and a restore or graft rebuilds the same manifest and binding\n"
            "  hash from the record.\n", "s2 acceptance")
        text = self.once(
            text,
            "- [x] Task: the component patches - the manifest (Binding Pipeline, S2 section) and the creation cache's keys\n"
            "  (component_patch_creation_cache.md), written 2026-10-18; the record's field moves to S5 (DECISION note).\n",
            "- [x] Task: the component patches - the manifest (Binding Pipeline, S2 section) and the creation cache's keys\n"
            "  (component_patch_creation_cache.md), written 2026-10-18.\n"
            f"- [ ] Task: the record patch - the binding hash in the SpellCrystal (the owner's word, DECISION note of\n"
            f"  {now}), before its code.\n", "s2 tasks")
        text = self.once(
            text,
            "- 2026-10-18T15:45:30Z: the inventory (FACT note), the record field moved to S5 and the managed settings in the hash\n"
            "  (DECISION note), the component patches and the mapping (PLAN note).\n",
            "- 2026-10-18T15:45:30Z: the inventory (FACT note), the record field moved to S5 and the managed settings in the hash\n"
            "  (DECISION note), the component patches and the mapping (PLAN note).\n"
            f"- {now}: the binding hash goes into the SpellCrystal in this landing on the owner's word; point (1)\n"
            "  of the DECISION note of 15:45:30Z is superseded (DECISION note).\n", "s2 log")
        epic_decision = self.note_range(self.EPIC, f"- DATETIME: {now}", "  TYPE: DECISION")
        own = self.note_range(self.S2, "- DATETIME: 2026-10-18T15:45:30Z", "  TYPE: DECISION")
        decision = self.note(now, "DECISION", [
            "The owner (chat 2026-10-18): \"make sure you land the binding hash going into crystallizer too please\".",
            "Point (1) of the DECISION note of 2026-10-18T15:45:30Z is superseded: the binding hash joins the",
            "SpellCrystal record in this landing, not in S5; the Requirements, Acceptance Criteria and EXIT_GATE say so",
            "again. A record patch - the field on the crystal, its RecordVersion, and what restore and graft do with a",
            "recorded hash, including a rebuilt manifest whose hash differs because the receiving Book's policy",
            "changed (its disposal order, for one) - is written and linked before any crystallizer code. Points (2)",
            "and (3) stand.",
        ], [epic_decision, own], [
            "S2 adds spell_crystal.py and the record version, and restore_engine.py and graft_runner.py where they",
            "replay the crystal; the PLAN mapping gains the record's row.",
        ], ["Read the crystal, the record version and both replays whole; write the record patch."], "REQUIRED", 8)
        text = self.once(text, "\n\n## Closure Confirmation\n",
                         "\n\n" + decision + "\n\n## Closure Confirmation\n", "s2 notes")
        old_state = text[text.index("- State: in_progress (melder_0), implementation: lands with S1"):
                         text.index("\n## Project-Specific Additions")]
        new_state = "\n".join([
            "- State: in_progress (melder_0), implementation: lands with S1 on the owner's word (the epic's DECISION note of",
            "  2026-10-18T15:01:53Z), the binding hash in the SpellCrystal included (his word, DECISION note of",
            f"  {now}); spell.py comes back from melder_1 after S9 lands as 0.2.8256 (M1-37).",
            "- Done: the inventory (FACT note), the component patches (Binding Pipeline S2 section, creation cache), the",
            "  managed settings in the hash (DECISION note), the mapping (PLAN note); the record deferral superseded",
            "  (DECISION note).",
            "- Next: the blast-radius record; the record patch; S2 built with S1 in a /tmp working mirror; the landing",
            "  pass once spell.py is back.",
            "",
        ])
        text = self.once(text, old_state, new_state, "s2 handoff")
        self.stage(self.S2, text)

    def flush(self) -> None:
        for rel, text in self.staged.items():
            if "\r" in text:
                sys.exit(f"CR in {rel}")
        self.BACKUP.mkdir(parents=True, exist_ok=True)
        for rel, text in self.staged.items():
            shutil.copy2(self.ROOT / rel, self.BACKUP / (pathlib.Path(rel).name + ".pre_m1_37"))
            (self.ROOT / rel).write_text(text, encoding="utf-8", newline="\n")
            print("wrote", rel)


if __name__ == "__main__":
    run = Pass()
    run.mailbox()
    run.epic()
    run.s2()
    run.flush()
    print("now", run.now)
