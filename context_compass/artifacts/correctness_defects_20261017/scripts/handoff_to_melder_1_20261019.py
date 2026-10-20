"""melder_0 hands every ticket it holds to melder_1, on the owner's word (chat 2026-10-19: "After you finish your
change hand all your tickets to melder1 your competing for the same resources and document them").

The epic and S3 change hands with a DECISION note each, their Agent Name, Decision Log and resume view; the six
parked backlog tickets melder_0 held change hands with a DECISION note stating where each stands. The board rows move
to melder_1, the release-note probe is rowed under S3, M0-211 (HANDOFF) goes to melder_1 with its alert, and
melder_0's roster row reads departed. All-or-nothing; `--write` flushes.
"""
import ast
import pathlib
import re
import sys
from typing import List

sys.path.insert(0, str(pathlib.Path.home() / "mnt/melder_private/context_compass/artifacts/spell_identity_20261018/scripts"))
from cc_record import Record


class Handoff(Record):
    """Every ticket melder_0 holds, the boards and the mailbox."""

    EPIC_C = "tickets/epics/2026-10-17_correctness_defects_epic.md"
    S3 = "tickets/stories/2026-10-17_parked_cleanup_leaves_borrower_copies_story.md"
    ATOMIC = "tickets/stories/backlog/2026-09-29_atomic_frame_retirement_and_creation_attribution_story.md"
    DUPLICATE = "tickets/stories/backlog/2026-10-18_explicit_duplicate_binding_story.md"
    ONE_REG = "tickets/stories/backlog/2026-10-18_one_registration_per_object_story.md"
    REVALIDATE = "tickets/stories/backlog/2026-10-18_revalidate_on_binding_change_story.md"
    MIGRATION = "tickets/stories/backlog/2026-10-18_spell_id_migration_story.md"
    WORDING = "tickets/tasks/backlog/2026-10-17_spell_id_wording_in_held_files_task.md"
    ID_EPIC = "tickets/epics/completed/2026-10-18_spell_identity_is_the_code_epic.md"
    HOST_EPIC = "tickets/epics/completed/2026-09-29_host_integration_read_surface_epic.md"
    RECHECK = "tickets/tasks/completed/2026-10-16_recheck_contract_consumers_when_provider_changes_task.md"
    PATCH = "system_docs/patches/active/cleanup_releases_contracts_2026_10_19/architecture_patch.md"

    # ---- helpers -------------------------------------------------------------------------------------------
    def def_range(self, rel: str, cls: str, meth: str) -> str:
        src = (self.REPO / rel).read_text(encoding="utf-8")
        for node in ast.parse(src).body:
            if isinstance(node, ast.ClassDef) and node.name == cls:
                for item in node.body:
                    if isinstance(item, ast.FunctionDef) and item.name == meth:
                        return f"{rel}:{item.lineno}-{item.end_lineno}"
        sys.exit(f"DEF {rel} {cls}.{meth}")

    def agent(self, rel: str) -> None:
        self.stage(rel, self.once(self.read(rel), "\n- Agent Name: melder_0\n", "\n- Agent Name: melder_1\n",
                                  f"agent {rel}"))
        self.set_field(rel, "Updated")

    def replace_bullet(self, rel: str, first: str, new: List[str], label: str) -> None:
        """Replace the bullet starting with `first` (with its indented continuation lines) by `new`."""
        lines = self.read(rel).split("\n")
        hits = [i for i, line in enumerate(lines) if line.startswith(first)]
        if len(hits) != 1:
            sys.exit(f"BULLET {label}: {len(hits)}")
        end = hits[0]
        while end + 1 < len(lines) and lines[end + 1].startswith("  "):
            end += 1
        self.check_width("\n".join(new), label)
        self.stage(rel, "\n".join(lines[:hits[0]] + new + lines[end + 1:]))

    def summary_line(self, rel: str, line: str, label: str) -> None:
        """Add one bullet at the end of the ticket's Context / Handoff Summary."""
        text = self.read(rel)
        self.stage(rel, self.once(text, "\n\n## Project-Specific Additions\n",
                                  "\n" + line + "\n\n## Project-Specific Additions\n", label))

    def handoff_note(self, state: List[str], evidence: List[str], nxt: List[str]) -> str:
        claim = ["The owner (chat 2026-10-19): \"After you finish your change hand all your tickets to melder1 your",
                 "competing for the same resources and document them\". melder_0 hands this ticket to melder_1 as it "
                 "stands:"] + state
        return self.note(self.now, "DECISION", claim, evidence,
                         ["Its holder is melder_1; nothing else in it changes."], nxt, "REQUIRED", 8)

    # ---- S3 ------------------------------------------------------------------------------------------------
    def s3(self) -> None:
        book = "src/melder/aether/spellbook/spellbook.py"
        ward = "src/melder/aether/conduit/conduit_ward/conduit_ward.py"
        conduit = "src/melder/aether/conduit/conduit.py"
        note = self.note(self.now, "DECISION", [
            "The owner (chat 2026-10-19), after S3's change: \"After you finish your change hand all your tickets to",
            "melder1 your competing for the same resources and document them\". melder_0 hands S3 to melder_1, landed",
            "but for the rebuild and the turn-in: src, 13 tests, docs, indexes, graph, the release-note section and the",
            "notch 0.2.8261 (FACT notes of 2026-10-19T11:48:58Z and 12:30:04Z; MEASURE note of 12:00:59Z). conduit.py,",
            "spellbook.py and conduit_ward.py are melder_1's (M0-211); S3's hunks sit in `Conduit.cleanup_spell`,",
            "`Spellbook.cleanup_spell`, `Spellbook._dispose_spell` and `ConduitWard._emit_spell_disposed`, not in the",
            "notch path S8 edits. Left for melder_1: S8 applied on S3's tree and the whole tree run there (the S8",
            "mirror lacked S3's 13 tests); the rebuild for both, which sets the release note's rebuild line (it reads",
            "0.2.8260); the turn-in on the owner's word - the completion summary names 0.2.8261 and the section",
            "\"Cleaning up a spell takes it out of every contract first\", the patch docs go to",
            "system_docs/patches/completed/cleanup_releases_contracts_2026_10_19/, the story to completed/, and both",
            "boards sync. Seen and not S3's, for the owner: the direct doors (`cleanup_and_remove_spell`, a direct",
            "`Spell.cleanup()`) release no contract (K6); a grant of a parked version adds every member id of its",
            "index to the borrower's borrowed ids and its removal drops only its own (`_add_inactive_contracted_spell`,",
            "K2); `test_concurrent_adds_of_same_conduit_admit_exactly_one` is timing-dependent (1 of 10 reruns fail",
            "on 0.2.8260); the graph nodes Conduit and ConduitWard stay SEMANTICS_STALE."],
            [self.note_range(self.S3, "- DATETIME: 2026-10-19T11:48:58Z", "  TYPE: FACT"),
             self.note_range(self.S3, "- DATETIME: 2026-10-19T12:00:59Z", "  TYPE: MEASURE"),
             self.note_range(self.S3, "- DATETIME: 2026-10-19T12:30:04Z", "  TYPE: FACT"),
             self.def_range(conduit, "Conduit", "cleanup_spell"),
             self.def_range(book, "Spellbook", "cleanup_spell"),
             self.def_range(book, "Spellbook", "_dispose_spell"),
             self.def_range(ward, "ConduitWard", "_emit_spell_disposed"),
             self.whole(self.PATCH)],
            ["S3's holder is melder_1; melder_0 holds no file and no ticket."],
            ["melder_1 applies S8 on S3's tree (M0-211)."], "REQUIRED", 9)
        self.append_notes(self.S3, [note], "s3 note")
        self.agent(self.S3)
        text = self.read(self.S3)
        text = self.once(
            text,
            "  - artifacts/correctness_defects_20261017/scripts/s3_fix/ (the src apply script and the record passes)\n",
            "  - artifacts/correctness_defects_20261017/scripts/s3_fix/ (the src apply script and the record passes)\n"
            "  - artifacts/correctness_defects_20261017/probes/probe_release_note_s3.py (the note's example, as written)\n",
            "s3 artifact link")
        text = self.once(
            text,
            "  melder_1's S8 landing, notched above 0.2.8261, rebuilds for both (the owner; DECISION note).\n"
            "- 2026-10-19T12:30:04Z: docs, indexes, graph, the release-note section and the notch 0.2.8261 (FACT note).\n",
            "  melder_1's S8 landing, notched above 0.2.8261, rebuilds for both (the owner; DECISION note).\n"
            "- 2026-10-19T12:30:04Z: docs, indexes, graph, the release-note section and the notch 0.2.8261 (FACT note).\n"
            f"- {self.now}: handed to melder_1 with every ticket melder_0 held, on the owner's word (DECISION note).\n",
            "s3 decision log")
        self.stage(self.S3, text)
        lines = self.read(self.S3).split("\n")
        start = [i for i, line in enumerate(lines) if line.startswith("- State: in_progress, melder_0 (the owner's go")]
        stop = [i for i, line in enumerate(lines) if line.startswith("- Next: (1) M0-211 hands")]
        if len(start) != 1 or len(stop) != 1 or stop[0] <= start[0]:
            sys.exit(f"S3 SUMMARY {start} {stop}")
        end = stop[0]
        while lines[end + 1].startswith("  "):
            end += 1
        new = [
            "- State: in_progress with melder_1 since 2026-10-19, handed over by melder_0 on the owner's word (DECISION",
            f"  note of {self.now}). Confirmed by the owner and re-tested on 0.2.8260, GIL off and on: the records",
            "  stayed, and a later notch to the same class staged again raised AttributeError in the borrower fan-out",
            "  and left the borrower with no active version (MEASURE note). The fix uses the removal code that exists",
            "  (DECISION note of 2026-10-19T10:41:53Z): src in conduit.py, spellbook.py and conduit_ward.py with 13",
            "  tests, red on 0.2.8260 and green with the GIL off and on (FACT note of 2026-10-19T11:48:58Z); validated",
            "  with the GIL off and on - the probes at the fix and the whole tree against 0.2.8260 (MEASURE note of",
            "  2026-10-19T12:00:59Z); docs, indexes, graph, the release-note section and the notch 0.2.8261 (FACT note of",
            "  2026-10-19T12:30:04Z). The three files are melder_1's (M0-211). Not rebuilt: the rebuild rides melder_1's",
            "  S8 landing (the owner).",
            "- Next: (1) melder_1 applies S8 on S3's tree and runs the whole tree there, S3's 13 tests included; (2) its",
            "  landing rebuilds for both and sets the release note's rebuild line to its version; (3) S3's turn-in on",
            "  the owner's word - the completion summary names 0.2.8261 and the release-note section, the patch docs",
            "  move to system_docs/patches/completed/, the story to completed/, and both boards sync."]
        self.check_width("\n".join(new), "s3 summary")
        self.stage(self.S3, "\n".join(lines[:start[0]] + new + lines[end + 1:]))

    # ---- the epic ------------------------------------------------------------------------------------------
    def epic(self) -> None:
        note = self.note(self.now, "DECISION", [
            "The owner (chat 2026-10-19), after S3's change: \"After you finish your change hand all your tickets to",
            "melder1 your competing for the same resources and document them\". melder_0 hands the epic to melder_1 with",
            "every ticket it held, each documented in its Notes and resume view:",
            "STORY-2026-10-17-parked_cleanup_leaves_borrower_copies (S3; landed at 0.2.8261 but for the rebuild, which",
            "rides S8's landing, and the turn-in on the owner's word) and six parked backlog tickets -",
            "STORY-2026-09-29-atomic-frame-retirement-and-creation-attribution, STORY-2026-10-18-explicit_duplicate_binding,",
            "STORY-2026-10-18-one_registration_per_object,",
            "STORY-2026-10-18-revalidate_on_binding_change, STORY-2026-10-18-spell_id_migration and",
            "TASK-2026-10-17-spell_id_wording_in_held_files. conduit.py, spellbook.py and conduit_ward.py are",
            "melder_1's (M0-211). The epic stands at: A1-A12 swept; eleven stories - S4, S6, S7 and S9 done, S10",
            "withdrawn, S3 landed, S8 in progress with melder_1, S1, S2 and S5 to follow it (M1-45), S11 waiting for",
            "the owner's scheduling. The parked identity-and-caching configurables epic stays unassigned (filed by",
            "melder_0). melder_0 holds no ticket and no file and checks out of the roster."],
            [self.note_range(self.S3, f"- DATETIME: {self.now}", "  TYPE: DECISION"),
             self.note_range(self.S3, "- DATETIME: 2026-10-19T12:30:04Z", "  TYPE: FACT"),
             self.note_range(self.EPIC_C, "- DATETIME: 2026-10-19T12:24:16Z", "  TYPE: FACT")],
            ["melder_1 is the epic's writer and the only agent on these tickets and files."],
            ["melder_1 applies S8 on S3's tree and rebuilds for both, then S1, S2 and S5 (M1-45)."], "REQUIRED", 9)
        self.append_notes(self.EPIC_C, [note], "epic note")
        self.agent(self.EPIC_C)
        text = self.read(self.EPIC_C)
        text = self.once(
            text,
            "  its copy and id with index-link borrowers, past their own unlink (sweep A2). In progress with melder_0 on\n"
            "  the owner's go (2026-10-19).\n",
            "  its copy and id with index-link borrowers, past their own unlink (sweep A2). Landed at 0.2.8261 by\n"
            "  melder_0 (every cleanup_spell door releases the version's contracts first), then handed to melder_1 with\n"
            "  the epic on the owner's word (2026-10-19); the rebuild rides S8's landing, the turn-in waits for the owner.\n",
            "epic s3 line")
        text = self.once(
            text,
            "  STORY-2026-10-19-notch_back_keeps_outgoing_dependencies (S11; ready, unassigned, p2) under this epic (FACT\n"
            "  note).\n\n## Artifact Links",
            "  STORY-2026-10-19-notch_back_keeps_outgoing_dependencies (S11; ready, unassigned, p2) under this epic (FACT\n"
            "  note).\n"
            f"- {self.now}: the owner's direction - melder_0 hands the epic and every ticket it held to melder_1\n"
            "  (DECISION note; M0-211).\n\n## Artifact Links",
            "epic decision log")
        text = self.once(
            text,
            "- State: in_progress (melder_0), handoff. A1-A12 are done; ten stories filed from the sweep and an eleventh\n",
            "- State: in_progress (melder_1 since 2026-10-19, handed over by melder_0 on the owner's word), handoff.\n"
            "  A1-A12 are done; ten stories filed from the sweep and an eleventh\n",
            "epic state")
        text = self.once(
            text,
            "  M1-44); melder_0 holds conduit.py, spellbook.py and conduit_ward.py for S3, and melder_1's S8 claim on\n"
            "  conduit.py, spellbook.py, spellbook_validation_error.py and change_control_manager.py takes effect when S3\n"
            "  lands (M1-45, M1-46, M0-210); each lane claims a file from the other by mailbox before editing it.\n",
            "  M1-44); S3 landed at 0.2.8261 and melder_0 released conduit.py, spellbook.py and conduit_ward.py to\n"
            "  melder_1 (M0-211), whose S8 claim on conduit.py, spellbook.py, spellbook_validation_error.py and\n"
            "  change_control_manager.py is in effect; melder_0 holds no file and no ticket.\n",
            "epic holders")
        self.stage(self.EPIC_C, text)
        self.replace_bullet(self.EPIC_C, "- Next: (1) melder_0 lands S3", [
            "- Done since: S3 landed at 0.2.8261 (S3's FACT note of 2026-10-19T12:30:04Z); on the owner's word melder_0",
            f"  handed the epic and every ticket it held to melder_1 (DECISION note of {self.now}; M0-211).",
            "- Next: (1) melder_1 applies S8 on S3's tree, rebuilding for both, and turns S3 in on the owner's word;",
            "  (2) S1, S2 and S5 with melder_1, one at a time (M1-45); S4, S7 and S9 landed (M1-38, M1-42, M1-44);",
            "  (3) S11 on the owner's scheduling; (4) each fix with the patch gate, its notch and its rebuild; (5) a",
            "  fourth tranche on the owner's word."], "epic next")

    # ---- the six parked tickets ----------------------------------------------------------------------------
    def parked(self) -> None:
        holder = f"- Holder: melder_1 since 2026-10-19, from melder_0 on the owner's word (DECISION note of {self.now})."
        # STORY-2026-09-29-atomic-frame-retirement-and-creation-attribution: no Notes section yet.
        note = self.handoff_note([
            "draft since 2026-09-29, parked for the owner's decision on whether MelderOps shares its frames with code",
            "outside its operation guard; no design and no source; its epic,",
            "EPIC-2026-09-29-host-integration-read-surface, is completed."],
            [self.doc_section(self.ATOMIC, "## Context / Handoff Summary"),
             self.doc_section(self.HOST_EPIC, "## Metadata")],
            ["The owner's word on sharing MelderOps frames; then the design (patch docs and a DECISION_REQUEST)."])
        text = self.read(self.ATOMIC)
        text = self.once(text, "\n## Context / Handoff Summary\n",
                         "\n## Notes\n" + note + "\n\n## Context / Handoff Summary\n", "atomic notes")
        self.stage(self.ATOMIC, text)
        self.summary_line(self.ATOMIC, holder, "atomic holder")
        self.agent(self.ATOMIC)
        # STORY-2026-10-18-explicit_duplicate_binding.
        note = self.handoff_note([
            "draft, parked (the owner, 2026-10-18): one object is strictly one spell since 0.2.8257. The four forms of",
            "an explicit duplicate bind and the recommendation are in the identity epic's STRATEGY_DISCUSSION note,",
            "now in tickets/epics/completed/ (this story's PLAN note cites the epic's old path); it waits for the",
            "owner's choice of the form and the name."],
            [self.note_range(self.ID_EPIC, "- DATETIME: 2026-10-18T14:33:32Z", "  TYPE: STRATEGY_DISCUSSION"),
             self.note_range(self.DUPLICATE, "- DATETIME: 2026-10-18T14:33:32Z", "  TYPE: PLAN")],
            ["The owner's choice of the form and the name; then its design (patch docs)."])
        self.append_notes(self.DUPLICATE, [note], "duplicate note")
        self.summary_line(self.DUPLICATE, holder, "duplicate holder")
        self.agent(self.DUPLICATE)
        # STORY-2026-10-18-one_registration_per_object (S4 of the identity epic).
        note = self.handoff_note([
            "draft, parked since the identity epic's turn-in after 0.2.8257 and 0.2.8258; nothing started; its",
            "acceptance carries M4b and M5b, which hold since 0.2.8259."],
            [self.note_range(self.ONE_REG, "- DATETIME: 2026-10-19T00:49:20Z", "  TYPE: FACT")],
            ["The owner's word; then the component patch (the refusal naming the existing registration)."])
        self.append_notes(self.ONE_REG, [note], "one registration note")
        self.summary_line(self.ONE_REG, holder, "one registration holder")
        self.agent(self.ONE_REG)
        # STORY-2026-10-18-revalidate_on_binding_change (S3 of the identity epic).
        note = self.handoff_note([
            "draft, parked since the identity epic's turn-in; nothing started; the risk in its FACT note of",
            "2026-10-18T16:24:12Z stands - a rebind under another slotted existence can meet the removed",
            "definition's object at its first meld."],
            [self.note_range(self.REVALIDATE, "- DATETIME: 2026-10-18T16:24:12Z", "  TYPE: FACT"),
             self.note_range(self.REVALIDATE, "- DATETIME: 2026-10-19T00:49:20Z", "  TYPE: FACT")],
            ["The owner's word; then the component patch (which binding fields revalidate and which only rebind)."])
        self.append_notes(self.REVALIDATE, [note], "revalidate note")
        self.summary_line(self.REVALIDATE, holder, "revalidate holder")
        self.agent(self.REVALIDATE)
        # STORY-2026-10-18-spell_id_migration (S5 of the identity epic).
        note = self.handoff_note([
            "draft, parked since the identity epic's turn-in; nothing started; its open question is answered",
            "(restore the first registration, a shortfall per dropped duplicate)."],
            [self.note_range(self.MIGRATION, "- DATETIME: 2026-10-19T00:49:20Z", "  TYPE: FACT")],
            ["The owner's word; then the component patch (records holding one object twice restore the first)."])
        self.append_notes(self.MIGRATION, [note], "migration note")
        self.summary_line(self.MIGRATION, holder, "migration holder")
        self.agent(self.MIGRATION)
        # TASK-2026-10-17-spell_id_wording_in_held_files: Notes end at its Context / Handoff Summary.
        note = self.handoff_note([
            "blocked in the backlog since 2026-10-17. The release its ENTRY_GATE waited for came -",
            "TASK-2026-10-16-recheck_contract_consumers_when_provider_changes is done and its files went back (M1-28,",
            "2026-10-18) - but 0.2.8253 to 0.2.8261 rewrote many lines its 132 decisions point at, so the inventory is",
            "re-run against the current text before any decision is applied; it waits for the owner's scheduling, and",
            "its status is the new holder's to set."],
            [self.doc_section(self.RECHECK, "## Metadata"),
             self.note_range(self.EPIC_C, "- DATETIME: 2026-10-18T12:06:53Z", "  TYPE: DECISION"),
             self.note_range(self.WORDING, "- DATETIME: 2026-10-17T20:49:39Z", "  TYPE: FACT")],
            ["The owner's scheduling; then re-run the inventory over the held files."])
        text = self.read(self.WORDING)
        text = self.once(text, "\n\n## Context / Handoff Summary\n", "\n\n" + note + "\n\n## Context / Handoff Summary\n",
                         "wording note")
        text = self.once(
            text,
            "- State: blocked (backlog) - waits for melder_1's release NOTICE (rule 2's closure and its rebuild).\n",
            "- State: blocked (backlog) - the release it waited for came (M1-28, 2026-10-18); it waits for the owner's\n"
            f"  scheduling and a fresh inventory (DECISION note of {self.now}).\n",
            "wording state")
        self.stage(self.WORDING, text)
        self.summary_line(self.WORDING, holder, "wording holder")
        self.agent(self.WORDING)

    # ---- boards and mailbox --------------------------------------------------------------------------------
    def boards(self) -> None:
        text = self.read(self.BOARD)
        for work_item, mode, nxt in (
                ("correctness_defects", None,
                 "melder_1 holds the epic (handed over by melder_0, the owner's word): S8 on S3's tree, then S1, S2 "
                 "and S5; S11 waits for the owner."),
                ("parked_cleanup_contracts", "handoff",
                 "melder_1: apply S8 on S3's tree and rebuild for both; turn S3 in on the owner's word.")):
            rows = re.findall(rf"^\| {work_item} \|.*$", text, flags=re.M)
            if len(rows) != 1:
                sys.exit(f"ROW {work_item}: {len(rows)}")
            cells = rows[0].split(" | ")
            if cells[4] != "melder_0":
                sys.exit(f"AGENT {work_item}: {cells[4]}")
            cells[4] = "melder_1"
            if mode is not None:
                cells[2] = mode
            cells[6] = nxt
            cells[10] = self.now
            text = text.replace(rows[0], " | ".join(cells))
        text = self.once(text, "\n<!-- END USER-DEFINED: alerts -->",
                         f"\n- NEW MESSAGE for melder_1 (from melder_0, {self.now})\n<!-- END USER-DEFINED: alerts -->",
                         "alert m0-211")
        self.stage(self.BOARD, text)
        text = self.read(self.ARTIFACTS)
        rows = re.findall(r"^\| tickets/stories/2026-10-17_parked_cleanup_leaves_borrower_copies_story\.md \| "
                          r"artifacts/correctness_defects_20261017/scripts/s3_fix/ \|.*$", text, flags=re.M)
        if len(rows) != 1:
            sys.exit(f"ARTIFACT ROW scripts: {len(rows)}")
        row = ("| tickets/stories/2026-10-17_parked_cleanup_leaves_borrower_copies_story.md | "
               "artifacts/correctness_defects_20261017/probes/probe_release_note_s3.py | release_note_probe | active | "
               "retain_as_reference | The 0.2.8261 release note's example, run as written: OK on the fix with the GIL "
               "off and on, AttributeError on 0.2.8260 (runs/s3_fix/release_note_probe_*). | "
               f"{self.now} | HELPFUL |")
        self.stage(self.ARTIFACTS, text.replace(rows[0], rows[0] + "\n" + row))

    def mailbox(self) -> None:
        text = self.read(self.MAILBOX)
        rows = re.findall(r"^\| melder_0 \| claude \| 2026-09-26T22:24:06Z \| \S+ \| active \|$", text, flags=re.M)
        if len(rows) != 1:
            sys.exit(f"ROW melder_0: {len(rows)}")
        text = text.replace(rows[0], f"| melder_0 | claude | 2026-09-26T22:24:06Z | {self.now} | departed |")
        decision = self.note_range(self.EPIC_C, f"- DATETIME: {self.now}", "  TYPE: DECISION")
        message = (
            "- TO: melder_1\n"
            "  FROM: melder_0\n"
            f"  DATETIME: {self.now}\n"
            "  TYPE: HANDOFF\n"
            "  CLAIM: M0-211, on the owner's word (chat 2026-10-19: \"After you finish your change hand all your tickets\n"
            "    to melder1 your competing for the same resources and document them\"). S3 landed at 0.2.8261 - src, 13\n"
            "    tests, docs, indexes, graph, the release-note section, the notch - with no rebuild. conduit.py,\n"
            "    spellbook.py and conduit_ward.py are yours; notch above 0.2.8261; your S8 landing rebuilds for both and\n"
            "    sets the release note's rebuild line (it reads 0.2.8260). Every ticket melder_0 held is yours, its state\n"
            "    in its Notes and resume view: EPIC-2026-10-17-correctness_defects,\n"
            "    STORY-2026-10-17-parked_cleanup_leaves_borrower_copies (turn-in on the owner's word) and, parked,\n"
            "    STORY-2026-09-29-atomic-frame-retirement-and-creation-attribution,\n"
            "    STORY-2026-10-18-explicit_duplicate_binding, STORY-2026-10-18-one_registration_per_object,\n"
            "    STORY-2026-10-18-revalidate_on_binding_change, STORY-2026-10-18-spell_id_migration and\n"
            "    TASK-2026-10-17-spell_id_wording_in_held_files. melder_0 holds nothing and has checked out.\n"
            f"  EVIDENCE: {decision}\n"
            "  ACK_REQUESTED: false")
        text = self.once(text, "\n<!-- END USER-DEFINED: messages -->",
                         "\n" + message + "\n<!-- END USER-DEFINED: messages -->", "message")
        self.stage(self.MAILBOX, text)

    def run(self) -> None:
        self.s3()
        self.epic()
        self.parked()
        self.boards()
        self.mailbox()
        for rel in (self.S3, self.EPIC_C, self.ATOMIC, self.DUPLICATE, self.ONE_REG, self.REVALIDATE,
                    self.MIGRATION, self.WORDING):
            print("DECISION", self.note_range(rel, f"- DATETIME: {self.now}", "  TYPE: DECISION"))


def main() -> None:
    record = Handoff("handoff_to_melder_1")
    record.run()
    if "--write" not in sys.argv:
        print("CHECK OK", record.now, sorted(record.staged))
        return
    record.flush()


if __name__ == "__main__":
    main()
