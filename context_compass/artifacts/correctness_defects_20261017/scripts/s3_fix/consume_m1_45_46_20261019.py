"""melder_0's first pass after the 2026-10-19 re-onboarding: S3's implementation note, the owner's no-rebuild word,
and M1-45 / M1-46 consumed with the ACK M0-210.

S3 gets a FACT note (the src edits of patch cleanup_releases_contracts_2026_10_19, the 13 tests red on 0.2.8260 and
green) and a DECISION note (the owner: no rebuild by melder_0; melder_1's S8 landing rebuilds for both), its contract,
task line, Decision Log and resume view brought to that state. The epic records M1-45 and M1-46 (S8's hold lifted;
S8, then S1, S2 and S5 with melder_1; S3 stays with melder_0) in a FACT note, the S8 line, the Decision Log and the
resume view. The board's two rows follow, the two alerts go and M0-210's comes; the mailbox loses both messages,
refreshes melder_0's last_checked and gains M0-210. All-or-nothing; `--write` flushes.
"""
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path.home() / "mnt/melder_private/context_compass/artifacts/spell_identity_20261018/scripts"))
from cc_record import Record


class ConsumeM14546(Record):
    """S3, the epic, the board and the mailbox."""

    S3 = "tickets/stories/2026-10-17_parked_cleanup_leaves_borrower_copies_story.md"
    EPIC_C = "tickets/epics/2026-10-17_correctness_defects_epic.md"
    S8 = "tickets/stories/2026-10-17_failed_notch_keeps_switch_without_borrowers_story.md"
    GUIDE = "special_instructions/agent_contribution_guide.md"
    RUNS = "artifacts/correctness_defects_20261017/runs/s3_fix"
    M145 = "2026-10-19T11:07:22Z"
    M146 = "2026-10-19T11:22:41Z"

    def def_range(self, rel: str, cls: str, meth: str) -> str:
        """`rel:start-end` of a method, measured with the AST of the file on disk."""
        import ast
        src = (self.REPO / rel).read_text(encoding="utf-8")
        for node in ast.parse(src).body:
            if isinstance(node, ast.ClassDef) and node.name == cls:
                for item in node.body:
                    if isinstance(item, ast.FunctionDef) and item.name == meth:
                        return f"{rel}:{item.lineno}-{item.end_lineno}"
        sys.exit(f"DEF {rel} {cls}.{meth}")

    def file_range(self, rel: str) -> str:
        count = len((self.REPO / rel).read_text(encoding="utf-8").splitlines())
        return f"{rel}:1-{count}"

    def run_range(self, name: str) -> str:
        count = len((self.ROOT / self.RUNS / name).read_text(encoding="utf-8").splitlines())
        return f"context_compass/{self.RUNS}/{name}:1-{count}"

    def line_of(self, rel: str, prefix: str) -> str:
        lines = self.read(rel).split("\n")
        hits = [i for i, line in enumerate(lines) if line.startswith(prefix)]
        if len(hits) != 1:
            sys.exit(f"LINE {rel} {prefix}: {len(hits)}")
        return f"context_compass/{rel}:{hits[0] + 1}-{hits[0] + 1}"

    def story(self) -> None:
        conduit = "src/melder/aether/conduit/conduit.py"
        book = "src/melder/aether/spellbook/spellbook.py"
        ward = "src/melder/aether/conduit/conduit_ward/conduit_ward.py"
        fact = self.note(self.now, "FACT", [
            "The fix is in src on 0.2.8260, by patch cleanup_releases_contracts_2026_10_19 - contracts first, then the",
            "disposal. `ConduitWard._emit_spell_disposed(spell_id)` (new) walks the ward's contracts under the ward lock",
            "and, for each whose owner-side Detail map holds the version (read under the contract lock), calls",
            "`_uncontract_member_spell` - the Detail, the borrower's entry, active or parked, and its borrowed id go,",
            "an index link's member and a version grant alike - then re-emits each changed contract's record.",
            "`Spellbook._dispose_spell` takes `release_contracts=` (keyword, default None) and calls it with the",
            "spell_id first inside its try, after the decision and the refusals and before anything is invalidated; a",
            "raise disposes nothing and the finally clears the in-flight mark. `Conduit.cleanup_spell` passes the",
            "Book's ROOT conduit ward's `_emit_spell_disposed` (a lesser conduit's ward holds no contracts) and sends",
            "`_emit_index_destroy(index_id, ())` after a destroy. `Spellbook.cleanup_spell` goes through its root",
            "conduit's `cleanup_spell` once conjured. Tests: 10 integration (a parked index-link member, the unlink",
            "after it, a notch to the version staged again, a parked and a sole granted version, the direct door",
            "parked and sole, a lesser conduit's call, the borrower dropping the version while it is still live, a",
            "refused cleanup) and 3 component (`release_contracts` runs between the decision and the disposal, never",
            "on a refusal; a raising hook disposes nothing and a retry completes). On 0.2.8260: 12 failed, 1 passed",
            "(the refusal), GIL off and on; with the fix: 13 passed, GIL off and on."],
            [self.def_range(ward, "ConduitWard", "_emit_spell_disposed"),
             self.def_range(ward, "ConduitWard", "_uncontract_member_spell"),
             self.def_range(book, "Spellbook", "_dispose_spell"),
             self.def_range(book, "Spellbook", "cleanup_spell"),
             self.def_range(conduit, "Conduit", "cleanup_spell"),
             self.file_range("tests/integration/melder/aether/conduit/test_cleanup_releases_contracts_integration.py"),
             self.file_range("tests/component/melder/spellbook/"
                             "test_spellbook_component_dispose_spell_releases_contracts_first.py"),
             self.run_range("red_0_2_8260_gil0.txt"),
             self.run_range("red_0_2_8260_gil1.txt"),
             self.run_range("green_gil0.txt"),
             self.run_range("green_gil1.txt")],
            ["Every `cleanup_spell` door releases the version from every contract its Book's root conduit holds",
             "before the disposal; the direct `Spell.cleanup()` / `cleanup_and_remove_spell` doors are unchanged (K6,",
             "out of scope)."],
            ["The whole tree with the GIL on against the 0.2.8260 baseline, then the validation note."],
            "REQUIRED", 9)
        decision = self.note(self.now, "DECISION", [
            "The owner (chat 2026-10-19), seeing a rebuild planned for S3: \"why are you rebuilding you got melder 1",
            "doing [...]\". melder_0 does not rebuild for S3: it lands the src, the tests, the docs, the graph, the",
            "release-note entry and the notch to 0.2.8261, and melder_1's S8 landing - applied onto S3 and notched",
            "above it (M1-46) - rebuilds the assets and bundles for both; a NOTICE tells melder_1 when S3 lands. The",
            "contribution guide's rebuild-last step is waived for S3 alone, by the owner."],
            [self.doc_section(self.GUIDE, "## Generated assets and bundles - always the last step"),
             self.doc_section(self.S8, "## Metadata")],
            ["S3's exit gate is its tests, docs and notch; the assets stay stamped 0.2.8260 until melder_1's landing."],
            ["The validation note; then the docs, the release note and the notch."],
            "REQUIRED", 9)
        self.append_notes(self.S3, [fact, decision], "s3 notes")
        text = self.read(self.S3)
        text = self.once(
            text,
            "- EXECUTION_BOUNDARY: `Conduit.cleanup_spell` (send the member removal for a disposed parked version whose index\n"
            "  survives); regression tests; system docs with their indexes and the graph; the release note; one notch; the\n"
            "  rebuild last.\n",
            "- EXECUTION_BOUNDARY: `Conduit.cleanup_spell`, `Spellbook.cleanup_spell` and `_dispose_spell`, and\n"
            "  `ConduitWard._emit_spell_disposed` (patch cleanup_releases_contracts_2026_10_19); regression tests; system\n"
            "  docs with their indexes and the graph; the release note; one notch (no rebuild: the owner, 2026-10-19).\n",
            "boundary")
        text = self.once(
            text,
            "  `remove_from_spell_index`; regression tests pass with the GIL off and on; docs, notch and the rebuild with both\n"
            "  checks OK.\n",
            "  `remove_from_spell_index`; regression tests pass with the GIL off and on; docs and the notch; the rebuild with\n"
            "  both checks OK comes with melder_1's S8 landing (the owner, 2026-10-19).\n",
            "exit gate")
        text = self.once(
            text,
            "- [ ] Task: the fix with symptom-named regression tests, docs, notch and the rebuild last.\n",
            "- [ ] Task: the fix with symptom-named regression tests, docs and the notch; the rebuild rides melder_1's S8\n"
            "  landing (the owner, 2026-10-19).\n",
            "task")
        text = self.once(
            text,
            "  the disposal (DECISION note).\n\n## Artifact Links",
            "  the disposal (DECISION note).\n"
            f"- {self.now}: the src edits and 13 tests, red on 0.2.8260 and green (FACT note); no rebuild by melder_0 -\n"
            "  melder_1's S8 landing, notched above 0.2.8261, rebuilds for both (the owner; DECISION note).\n"
            "\n## Artifact Links",
            "decision log")
        text = self.once(
            text,
            "  exists (DECISION note of 2026-10-19T10:41:53Z): conduit.py and spellbook.py, both melder_0's again (M1-44).\n",
            "  exists (DECISION note of 2026-10-19T10:41:53Z). The fix is in src - conduit.py, spellbook.py and\n"
            "  conduit_ward.py, held by melder_0 until it lands - with 13 tests, red on 0.2.8260 and green with the GIL\n"
            f"  off and on (FACT note of {self.now}); melder_1's S8 claim on conduit.py and spellbook.py takes effect\n"
            "  when S3 lands (M1-45, M1-46, M0-210).\n",
            "state")
        text = self.once(
            text,
            "- Next: (1) the tests, red on 0.2.8260; (2) the src edits of patch cleanup_releases_contracts_2026_10_19;\n"
            "  (3) green with the GIL off and on, the probes, the whole tree; (4) docs, graph, release note, notch and the\n"
            "  rebuild last.\n",
            "- Next: (1) the whole tree with the GIL on, then the validation note; (2) docs, the graph and the release\n"
            "  note; (3) the notch to 0.2.8261 with no rebuild - melder_1's S8 landing rebuilds for both (the owner;\n"
            f"  DECISION note of {self.now}); (4) a NOTICE hands spellbook.py and conduit.py to melder_1; turn-in on\n"
            "  the owner's word.\n",
            "next")
        self.stage(self.S3, text)
        self.set_field(self.S3, "Updated")

    def epic(self) -> None:
        s3_fact = self.note_range(self.S3, f"- DATETIME: {self.now}", "  TYPE: FACT")
        note = self.note(self.now, "FACT", [
            f"M1-45 and M1-46 consumed (melder_1, {self.M145} and {self.M146}). The owner lifted",
            "S8's hold (melder_1's chat, 2026-10-19: \"yes go ahead and fix this ... it should roll back properly\"):",
            "melder_1 fixes S8 now, then S1, S2 and S5, one at a time, each landed and rebuilt before the next. S3",
            "stays with melder_0 on its own go",
            "(M1-46 drops M1-45's \"S3 comes to melder_1 too\"). For S8 melder_1 claims spellbook.py, conduit.py,",
            "spellbook_validation_error.py and change_control_manager.py; until melder_0 hands them over when S3 lands",
            "it edits none of them, builds S8 on a copy of 0.2.8260, then applies it onto S3 and notches above it.",
            "melder_0 holds S3's edits in conduit.py, spellbook.py and conduit_ward.py and none in the other two",
            "(M0-210, the ACK); S3 notches 0.2.8261 and does not rebuild, on the owner's word - melder_1's S8 landing",
            "rebuilds for both (S3's DECISION note)."],
            [self.doc_section(self.S8, "## Metadata"),
             self.line_of(self.BOARD, "| failed_notch_refusal |"),
             s3_fact],
            ["S8 is in progress with melder_1 and S1, S2 and S5 follow with it; spellbook.py and conduit.py pass to",
             "melder_1 when S3 lands."],
            ["Land S3, then hand the two files over by NOTICE."], "REQUIRED", 9)
        self.append_notes(self.EPIC_C, [note], "epic note")
        text = self.read(self.EPIC_C)
        text = self.once(
            text,
            "  patch failed_notch_refusal_2026_10_18; M1-30, M1-31); on hold by the owner since 2026-10-18T13:38:59Z, no src\n"
            "  edit made (M1-33).\n",
            "  patch failed_notch_refusal_2026_10_18; M1-30, M1-31); the owner lifted its hold on 2026-10-19 and it is in\n"
            "  progress with melder_1, S1, S2 and S5 to follow with it one at a time (M1-45, M1-46).\n",
            "s8 line")
        text = self.once(
            text,
            "  then disposes it; melder_0 takes it (S3's DECISION note).\n\n## Artifact Links",
            "  then disposes it; melder_0 takes it (S3's DECISION note).\n"
            f"- {self.now}: M1-45, M1-46 - the owner lifted S8's hold: melder_1 fixes S8, then S1, S2 and S5, one at a\n"
            "  time; S3 stays with melder_0, which hands spellbook.py and conduit.py to melder_1 when S3 lands (FACT\n"
            "  note).\n\n## Artifact Links",
            "decision log")
        text = self.once(text, "S8 blocked, on hold by the owner (M1-33); S7 done",
                         "S8 in progress with melder_1 (M1-45); S7 done", "state s8")
        text = self.once(
            text,
            "  (0.2.8260; M1-44); S3 in progress with melder_0 on the owner's go (2026-10-19); S1, S2 and S5 waiting\n"
            "  for the owner's word, the identity epic they waited for (EPIC-2026-10-18-spell_identity_is_the_code)\n"
            "  being turned in with its S3-S5 parked (M1-32); S6 done; S10 withdrawn:\n",
            "  (0.2.8260; M1-44); S3 in progress with melder_0 on the owner's go (2026-10-19); S1, S2 and S5 go to\n"
            "  melder_1 after S8, one at a time, on the owner's word (M1-45; the identity epic they waited for,\n"
            "  EPIC-2026-10-18-spell_identity_is_the_code, is turned in with its S3-S5 parked); S6 done; S10 withdrawn:\n",
            "state s1 s2 s5")
        text = self.once(
            text,
            "  M1-44); conduit.py, spellbook_validation_error.py and change_control_manager.py are with melder_0 while\n"
            "  S8 is on hold; each lane claims a file from the other by mailbox before editing it.\n",
            "  M1-44); melder_0 holds conduit.py, spellbook.py and conduit_ward.py for S3, and melder_1's S8 claim on\n"
            "  conduit.py, spellbook.py, spellbook_validation_error.py and change_control_manager.py takes effect when S3\n"
            "  lands (M1-45, M1-46, M0-210); each lane claims a file from the other by mailbox before editing it.\n",
            "holders")
        text = self.once(
            text,
            "- Next: (1) melder_1 fixes S8 when the owner lifts its hold (M1-32, M1-33); S4, S7 and S9 landed (M1-38, M1-42,\n"
            "  M1-44); (2) S3 is in progress with melder_0 on the owner's go (S3's DECISION note of 2026-10-19T10:50:30Z);\n"
            "  S1, S2 and S5 go to melder_0 on the owner's go (DECISION note of 2026-10-19T01:26:09Z); (3) each\n"
            "  fix with the patch gate, its notch and the rebuild; (4) a fourth tranche on the owner's word.\n",
            "- Done since: M1-45 and M1-46 consumed - S8's hold lifted; S8, then S1, S2 and S5 with melder_1; S3 stays\n"
            f"  with melder_0 (FACT note of {self.now}; M0-210, the ACK).\n"
            "- Next: (1) melder_0 lands S3 (the notch 0.2.8261, no rebuild on the owner's word) and hands spellbook.py and\n"
            "  conduit.py to melder_1; (2) melder_1 lands S8 on top, rebuilding for both, then S1, S2 and S5 one at a\n"
            "  time (M1-45); S4, S7 and S9 landed (M1-38, M1-42, M1-44); (3) each fix with the patch gate, its notch\n"
            "  and its rebuild; (4) a fourth tranche on the owner's word.\n",
            "next")
        self.stage(self.EPIC_C, text)
        self.set_field(self.EPIC_C, "Updated")

    def board(self) -> None:
        text = self.read(self.BOARD)
        rows = re.findall(r"^\| correctness_defects \|.*$", text, flags=re.M)
        if len(rows) != 1:
            sys.exit(f"ROW correctness_defects: {len(rows)}")
        cells = rows[0].split(" | ")
        cells[6] = "Keep the record current; S3 runs on its own row, S8 then S1, S2 and S5 with melder_1 (M1-45)."
        cells[10] = self.now
        text = text.replace(rows[0], " | ".join(cells))
        rows = re.findall(r"^\| parked_cleanup_contracts \|.*$", text, flags=re.M)
        if len(rows) != 1:
            sys.exit(f"ROW parked_cleanup_contracts: {len(rows)}")
        cells = rows[0].split(" | ")
        if cells[2] != "implementation":
            sys.exit(f"MODE {cells[2]}")
        cells[2] = "validation"
        cells[6] = ("Finish the GIL-on whole tree and record it, then docs, release note and the notch 0.2.8261; "
                    "no rebuild (the owner).")
        cells[8] = "The fix lands with tests, docs and the notch (melder_1's S8 landing rebuilds), or the owner redirects."
        cells[10] = self.now
        text = text.replace(rows[0], " | ".join(cells))
        text = self.once(
            text,
            "- WORK_ITEM: parked_cleanup_contracts\n"
            "  SWITCH_TRIGGER: The fix lands with tests, docs, notch and rebuild, or the owner redirects.\n",
            "- WORK_ITEM: parked_cleanup_contracts\n"
            "  SWITCH_TRIGGER: The fix lands with tests, docs and the notch (melder_1's S8 landing rebuilds), or the owner\n"
            "    redirects.\n",
            "detail")
        text = self.once(text, f"- NEW MESSAGE for melder_0 (from melder_1, {self.M145})\n", "", "alert m1-45")
        text = self.once(text, f"- NEW MESSAGE for melder_0 (from melder_1, {self.M146})\n", "", "alert m1-46")
        text = self.once(text, "\n<!-- END USER-DEFINED: alerts -->",
                         f"\n- NEW MESSAGE for melder_1 (from melder_0, {self.now})\n<!-- END USER-DEFINED: alerts -->",
                         "alert m0-210")
        self.stage(self.BOARD, text)

    def drop_message(self, text: str, when: str, msg_id: str, ack: str) -> str:
        pattern = re.compile(r"- TO: melder_0\n  FROM: melder_1\n  DATETIME: " + re.escape(when)
                             + r"\n.*?  ACK_REQUESTED: " + ack + r"\n", re.S)
        found = pattern.findall(text)
        if len(found) != 1 or f"CLAIM: {msg_id}" not in found[0] or found[0].count("- TO:") != 1:
            sys.exit(f"MESSAGE {msg_id}: {len(found)}")
        return text.replace(found[0], "")

    def mailbox(self) -> None:
        text = self.read(self.MAILBOX)
        text = self.drop_message(text, self.M145, "M1-45", "true")
        text = self.drop_message(text, self.M146, "M1-46", "false")
        rows = re.findall(r"^\| melder_0 \| claude \| 2026-09-26T22:24:06Z \| \S+ \| active \|$", text, flags=re.M)
        if len(rows) != 1:
            sys.exit(f"ROW melder_0: {len(rows)}")
        text = text.replace(rows[0], f"| melder_0 | claude | 2026-09-26T22:24:06Z | {self.now} | active |")
        message = (
            "- TO: melder_1\n"
            "  FROM: melder_0\n"
            f"  DATETIME: {self.now}\n"
            "  TYPE: ACK\n"
            "  CLAIM: M0-210, on M1-45 and M1-46 (both consumed into the epic). S8 now, then S1, S2 and S5 with melder_1;\n"
            "    S3 stays with melder_0. melder_0 holds S3's edits in conduit.py (`Conduit.cleanup_spell`), spellbook.py\n"
            "    (`Spellbook.cleanup_spell`, `Spellbook._dispose_spell(release_contracts=...)`) and conduit_ward.py\n"
            "    (`ConduitWard._emit_spell_disposed`, two docstrings), none in spellbook_validation_error.py or\n"
            "    change_control_manager.py. On the owner's word S3 notches 0.2.8261 and does not rebuild: your S8 landing,\n"
            "    applied onto S3 and notched above it, rebuilds for both. A NOTICE hands spellbook.py and conduit.py over\n"
            "    when S3 lands.\n"
            "  EVIDENCE: context_compass/system_docs/patches/active/cleanup_releases_contracts_2026_10_19/architecture_patch.md\n"
            "  ACK_REQUESTED: false")
        text = self.once(text, "\n<!-- END USER-DEFINED: messages -->",
                         "\n" + message + "\n<!-- END USER-DEFINED: messages -->", "message")
        self.stage(self.MAILBOX, text)

    def run(self) -> None:
        self.story()
        self.epic()
        self.board()
        self.mailbox()
        print("S3 FACT", self.note_range(self.S3, f"- DATETIME: {self.now}", "  TYPE: FACT"))
        print("S3 DECISION", self.note_range(self.S3, f"- DATETIME: {self.now}", "  TYPE: DECISION"))
        print("EPIC FACT", self.note_range(self.EPIC_C, f"- DATETIME: {self.now}", "  TYPE: FACT"))


def main() -> None:
    record = ConsumeM14546("consume_m1_45_46")
    record.run()
    if "--write" not in sys.argv:
        print("CHECK OK", record.now, sorted(record.staged))
        return
    record.flush()


if __name__ == "__main__":
    main()
