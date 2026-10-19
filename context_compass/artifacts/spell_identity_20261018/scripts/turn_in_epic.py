"""Turn in EPIC-2026-10-18-spell_identity_is_the_code on the owner's word (melder_0, 2026-10-19).

The owner (chat): "sorry finish up those last things then turn in the epic and then we'll move on", then "ok cool
finish your shit and call it then" and "don't rebuild let the next agent in the runtime rebuild the assets you can
call it after your done". One all-or-nothing pass, revised after the re-onboarding for the messages that came in
meanwhile (M1-42: melder_1's 0.2.8259 rebuild already ran, after this lane's last edits; M2-26 and M2-27: melder_2
corrected its teardown wording after that rebuild and checked out):
- M2-24, M2-26, M2-27 and M1-42 consumed: deleted, their alerts cleared, the roster row refreshed;
- the identity epic: the consumption, DECISION and closure notes, Completed/Summary, Status done, the transition,
  milestones, stories, the risk, the artifact links, the decision log, the anti-pattern and closure checks, the
  handoff;
- S3, S4 and S5: parked as S6 was (the transition, a decision-log line, the handoff, a FACT note, Updated); S4
  takes M4b and M5b as acceptance cases (M1-42); S5's open question carries the owner's record policy;
- EPIC-2026-10-17-correctness_defects: M1-42's S4 recorded (a FACT note, the S4 box, the log, the handoff);
- the attention board: the identity row and detail out, one closed anchor in (capped at 12, oldest out), the
  correctness row's next, the alerts;
- the artifact board: the identity epic's five active rows cleared (retain_as_reference);
- the mailbox: M0-207 to melder_1 (melder_2 checked out after M2-27, so it gets none).
No rebuild (the owner's word). `--write` flushes; the moves (`mv -n`) follow in the shell.
"""
import re
import sys
from typing import List, Tuple

from cc_record import Record

EPIC_DONE = "tickets/epics/completed/2026-10-18_spell_identity_is_the_code_epic.md"
CORRECTNESS = "tickets/epics/2026-10-17_correctness_defects_epic.md"
S1_DONE = "tickets/stories/completed/2026-10-18_spell_id_hashes_the_object_code_story.md"
S2_DONE = "tickets/stories/completed/2026-10-18_binding_manifest_hash_story.md"
S3_BACKLOG = "tickets/stories/backlog/2026-10-18_revalidate_on_binding_change_story.md"
S4C_DONE = "tickets/stories/completed/2026-10-17_minted_index_missing_from_frame_registry_story.md"
TEARDOWN_DONE = "tickets/tasks/completed/2026-10-18_document_root_teardown_cleans_only_what_it_holds_task.md"
WORDING_DONE = "tickets/tasks/completed/2026-10-19_correct_root_teardown_docs_wording_task.md"
S6_BACKLOG = "tickets/stories/backlog/2026-10-18_explicit_duplicate_binding_story.md"
GUIDE = "special_instructions/agent_contribution_guide.md"
RUNS_S4C = "artifacts/minted_index_registry_20261018/runs"
TURN_IN_RUNS = "artifacts/spell_identity_20261018/runs/turn_in"
MTIMES = f"{TURN_IN_RUNS}/mtimes.txt"
NOTE_REL = "release_docs/next_version_release.md"


class TurnIn(Record):
    """The turn-in pass."""

    def __init__(self, label: str) -> None:
        super().__init__(label)
        self.decision_range = ""
        self.policy_range = ""

    #region evidence

    def completion(self, rel: str) -> str:
        """`context_compass/rel:a-b` from a completed ticket's `- Completed:` line through its Summary block."""
        lines = self.read(rel).split("\n")
        starts = [i for i, line in enumerate(lines) if line.startswith("- Completed: ")]
        if len(starts) != 1 or not lines[starts[0] + 1].startswith("- Summary: "):
            sys.exit(f"completion {rel}: {starts}")
        end = self.block_end(lines, starts[0] + 1)
        return f"context_compass/{rel}:{starts[0] + 1}-{end + 1}"

    def release_section(self, heading: str) -> str:
        """`release_docs/next_version_release.md:a-b` of one `## ` section of the running release note."""
        lines = (self.REPO / NOTE_REL).read_text(encoding="utf-8").split("\n")
        starts = [i for i, line in enumerate(lines) if line == heading]
        if len(starts) != 1:
            sys.exit(f"release section {heading}: {len(starts)}")
        end = starts[0] + 1
        while end < len(lines) and not lines[end].startswith("## "):
            end += 1
        while lines[end - 1].strip() == "":
            end -= 1
        return f"{NOTE_REL}:{starts[0] + 1}-{end}"

    #endregion

    #region mailbox

    @staticmethod
    def _delete_message(lines: List[str], sender: str, when: str, tag: str) -> List[str]:
        """Delete the message to melder_0 from `sender` sent at `when`; it must carry `tag`."""
        starts = [i for i in range(len(lines) - 2)
                  if lines[i] == "- TO: melder_0" and lines[i + 1] == f"  FROM: {sender}"
                  and lines[i + 2] == f"  DATETIME: {when}"]
        if len(starts) != 1:
            sys.exit(f"{tag} block: {len(starts)}")
        end = starts[0]
        while not lines[end].startswith("  ACK_REQUESTED: "):
            end += 1
        if tag not in "\n".join(lines[starts[0]:end + 1]):
            sys.exit(f"block does not carry {tag}")
        return lines[:starts[0]] + lines[end + 1:]

    def mailbox(self) -> None:
        """Consume M2-24, M2-26, M2-27 and M1-42, refresh the roster row, send M0-207 to melder_1."""
        lines = self.read(self.MAILBOX).split("\n")
        lines = self._delete_message(lines, "melder_2", "2026-10-19T00:12:26Z", "M2-24,")
        lines = self._delete_message(lines, "melder_1", "2026-10-19T00:25:06Z", "M1-42.")
        lines = self._delete_message(lines, "melder_2", "2026-10-19T00:35:22Z", "M2-26,")
        lines = self._delete_message(lines, "melder_2", "2026-10-19T00:43:26Z", "M2-27,")
        text = "\n".join(lines)
        rows = re.findall(r"^\| melder_0 \| claude \| 2026-09-26T22:24:06Z \| \S+ \| active \|$", text, flags=re.M)
        if len(rows) != 1:
            sys.exit(f"roster row: {len(rows)}")
        text = text.replace(rows[0], f"| melder_0 | claude | 2026-09-26T22:24:06Z | {self.now} | active |")
        to_melder_1 = "\n".join([
            "- TO: melder_1",
            "  FROM: melder_0",
            f"  DATETIME: {self.now}",
            "  TYPE: NOTICE",
            "  CLAIM: M0-207, re M1-42 (consumed). EPIC-2026-10-18-spell_identity_is_the_code is turned in on the owner's",
            "    word: S1 and S2 landed, S3-S5 parked in tickets/stories/backlog/ beside S6 (S4 takes your M4b and M5b).",
            "    Your 0.2.8259 rebuild carried my last edits, and the owner left the next rebuild to the next agent in the",
            "    runtime: melder_2's wording fix to src_architecture and src_components (M2-27, 00:43Z) came after it, so",
            "    `_system_documents` is stale until then. I edit neither spellbook.py nor spell.py; S7 is next with you.",
            f"  EVIDENCE: context_compass/{TURN_IN_RUNS}/asset_check_after_wording.txt",
            "  ACK_REQUESTED: false",
        ])
        end = "<!-- END USER-DEFINED: messages -->"
        text = self.once(text, "\n" + end, "\n" + to_melder_1 + "\n" + end, "messages end")
        self.stage(self.MAILBOX, text)

    #endregion

    #region identity epic

    def epic_notes(self) -> None:
        """The messages' FACT note, the DECISION note and the closure FACT note."""
        consumed = self.note(self.now, "FACT", [
            "M2-24, M2-26, M2-27 and M1-42 consumed. melder_2 (M2-24 at 2026-10-19T00:12:26Z, M2-26 at 00:35:22Z, M2-27",
            "at 00:43:26Z): its root-teardown wording in src_architecture and src_components, corrected again after the",
            "owner's review (TASK-2026-10-19-correct_root_teardown_docs_wording, closed), is on the tree with both indexes",
            "--check OK and touches no file of this lane; it asked this lane to hold its rebuild until M2-27, then said",
            "it may run, and checked out. M1-42 (melder_1, 00:25:06Z) reports S4 of EPIC-2026-10-17-correctness_defects",
            "landed at 0.2.8259 and turned in, which fixes the risk this epic carried (one object bound twice through a",
            "minted index, M4b and M5b) and drops the release note's known-limits clause on it; the graph's Spellbook",
            "and Spell accepted with S4 (the leftover of the FACT note of 2026-10-19T00:18:40Z); spellbook.py and",
            "spell.py are melder_0's again. Read here: melder_1's 0.2.8259 rebuild ran at 00:22-00:24Z, after this",
            "lane's last edits (descriptors 00:11-00:14Z, src_graph.md 00:14:36Z, governed-change.md 00:16:22Z), with",
            "asset --check OK x3 and LLM --check OK x3; melder_2's correction came after it, and the checks run now say",
            "`_system_documents` STALE, the other two assets and the three LLM bundles OK.",
        ], [
            self.completion(TEARDOWN_DONE),
            self.completion(WORDING_DONE),
            self.completion(S4C_DONE),
            self.whole(f"{RUNS_S4C}/rebuild_asset_check_after_llm_0_2_8259.txt"),
            self.whole(f"{RUNS_S4C}/rebuild_llm_check_0_2_8259.txt"),
            self.whole(MTIMES),
            self.whole(f"{TURN_IN_RUNS}/asset_check_after_wording.txt"),
            self.whole(f"{TURN_IN_RUNS}/llm_check_after_wording.txt"),
        ], [
            "No rebuild is owed for this lane's leftovers: melder_1's packaged them. The packaged system documents are",
            "stale for melder_2's correction until the next rebuild, which the owner left to the next agent in the",
            "runtime (DECISION note); M0-207 tells melder_1 and the turn-in report tells the owner. The turn-in edits",
            "only tickets, boards and the mailbox, which the contribution guide's rebuild rule does not cover.",
        ], [
            "The turn-in.",
        ], "REQUIRED", 8)
        decision = self.note(self.now, "DECISION", [
            "The owner's word (chat): \"sorry finish up those last things then turn in the epic and then we'll move",
            "on\", then \"ok cool finish your shit and call it then\" and \"don't rebuild let the next agent in the",
            "runtime rebuild the assets you can call it after your done\". So the leftovers finish (the staged copies,",
            "the graph, the expert guide, the release note), the epic is turned in with S1 and S2 landed, S3-S5 park in",
            "the backlog beside S6 for his later word, and this lane runs no rebuild: the next agent's rebuild in the",
            "runtime - melder_1's for 0.2.8259, which ran after the leftovers (M1-42) - packages them. The owner may",
            "close any ticket by directive (the contribution guide); this closes the epic with S3-S5 open, as he said.",
        ], [
            self.doc_block(GUIDE, "- The owner may close any ticket by directive"),
            self.doc_section(S6_BACKLOG, "## State Transition Event"),
        ], [
            "The epic's exit gate is met but for S3-S5 (parked, not dropped); their acceptance criteria stay open in",
            "those three stories for the owner to take up.",
        ], [
            "The closure: notes, the stories parked, the boards, the move to completed/.",
        ], "REQUIRED", 9)
        closure = self.note(self.now, "FACT", [
            "EPIC-2026-10-18-spell_identity_is_the_code turned in. Landed: S1, notched 0.2.8257 (release-note section",
            "\"A spell_id is the SHA256 of the object's code, and one object is one spell\"), and S2, notched 0.2.8258",
            "(\"A spell's binding is a manifest with its own hash\"), both completed 2026-10-18T23:31:15Z and rebuilt",
            "for 0.2.8258 (FACT note of 2026-10-18T23:43:33Z); the leftovers - no source, no notch - packaged by",
            "melder_1's 0.2.8259 rebuild (the FACT note above). Parked in tickets/stories/backlog/ beside S6 and",
            "EPIC-2026-10-18-identity_and_caching_configurables: S3 (a changed binding revalidates), S4 (the refusal",
            "names the existing registration; M4b and M5b its acceptance cases) and S5 (records holding one object",
            "twice). Whole tree: this lane's own run on the final source Not run (the owner called the turn-in first);",
            "melder_1's run of S4's source (S1, S2 and S4 in src; its MEASURE note of 2026-10-19T00:00:59Z), the GIL",
            "off and on, was green but for the 18 red tests held for S8 (7 unit, 11 integration), on the owner's hold.",
            "This lane's edits since S1 and S2 landed touch no src or tests.",
        ], [
            self.completion(S1_DONE),
            self.completion(S2_DONE),
            self.release_section("## A spell_id is the SHA256 of the object's code, and one object is one spell"),
            self.release_section("## A spell's binding is a manifest with its own hash"),
            self.note_range(S4C_DONE, "- DATETIME: 2026-10-19T00:00:59Z", "  TYPE: MEASURE"),
        ], [
            "Identity is the code and the binding a manifest, in src, docs, graph and record; one object is one spell.",
            "The rest of the identity work - revalidation on a binding change, the refusal's message, old records -",
            "waits in the backlog for the owner.",
        ], [
            "None in this epic; S3-S6 and the configurables epic on the owner's word.",
        ], "REQUIRED", 8)
        self.append_notes(self.EPIC, [consumed, decision, closure], "epic notes")

    def epic_head(self, text: str) -> str:
        """Completed/Summary, Status, the transition."""
        title = ("# Epic: spell_identity_is_the_code - a spell_id names the registered object's code; its binding is a "
                 "manifest\n")
        text = self.once(text, title + "\n## Metadata\n", title + "\n" + "\n".join([
            f"- Completed: {self.now}",
            "- Summary: turned in on the owner's word: S1 notched 0.2.8257 (a spell_id is the SHA256 of the object's",
            "  code; one object is one spell) and S2 notched 0.2.8258 (the binding manifest and its hash); rebuilt for",
            "  0.2.8258, the leftovers packaged by melder_1's 0.2.8259 rebuild; S3-S5 parked in the backlog with S6.",
        ]) + "\n\n## Metadata\n", "completed")
        text = self.once(text, "\n- Status: in_progress\n", "\n- Status: done\n", "status")
        transition = re.search(r"## State Transition Event\n.*?\n\n(?=## )", text, flags=re.S)
        if transition is None:
            sys.exit("transition block")
        return self.once(text, transition.group(0), "\n".join([
            "## State Transition Event",
            "- from_state: in_progress",
            "- to_state: done",
            "- transition_reason: turned in on the owner's word (chat; the DECISION note of the turn-in): S1 and S2",
            "  landed (0.2.8257, 0.2.8258), S3-S5 parked in the backlog with S6, the rebuild left to the next agent's.",
        ]) + "\n\n", "transition")

    def epic_plan(self, text: str) -> str:
        """Milestones, stories, the risk and the artifact links."""
        for old, new in (
                ("- [ ] Milestone 2: the code hash and the binding manifest landed (S1, S2).",
                 "- [x] Milestone 2: the code hash and the binding manifest landed (S1, S2)."),
                ("one registration per object landed (S3, S4).\n",
                 "one registration per object landed (S3, S4) - parked\n  with them in the backlog (2026-10-19).\n"),
                ("(S5); the owner's disposition.\n",
                 "(S5); the owner's disposition - S5 parked in the\n  backlog; the owner turned the epic in "
                 "(2026-10-19).\n"),
                ("- [ ] Story: STORY-2026-10-18-spell_id_hashes_the_object_code",
                 "- [x] Story: STORY-2026-10-18-spell_id_hashes_the_object_code"),
                ("and nothing from the bind call (S1).\n", "and nothing from the bind call (S1;\n"
                                                           "  done, notched 0.2.8257).\n"),
                ("- [ ] Story: STORY-2026-10-18-binding_manifest_hash", "- [x] Story: STORY-2026-10-18-binding_manifest_hash"),
                ("part of the caches' keys beside the spell_id (S2).\n",
                 "part of the caches' keys beside the spell_id (S2; done, notched 0.2.8258).\n"),
                ("a verb changes a spell's binding in place (S3).\n", "a verb changes a spell's binding in place (S3;\n"
                                                                      "  parked in the backlog, 2026-10-19).\n"),
                ("naming its registration (S4).\n", "naming its registration (S4; parked in the backlog, 2026-10-19).\n"),
                ("docs and the release note (S5).\n", "docs and the release note (S5; parked in the backlog, 2026-10-19).\n"),
                ("  edit A closes it, and this epic's S4 takes M4b and M5b as acceptance cases.\n",
                 "  edit A closes it, and this epic's S4 takes M4b and M5b as acceptance cases. Closed at 0.2.8259"
                 " (M1-42).\n"),
                ("  - system_docs/patches/active/spell_identity_is_the_code_2026_10_18/ (the epic's and S1's patch docs)\n",
                 "  - system_docs/patches/completed/spell_identity_is_the_code_2026_10_18/ (the epic's, S1's and S2's patch"
                 " docs,\n    archived at S1 and S2's turn-in)\n"),
        ):
            text = self.once(text, old, new, "plan " + old[:40])
        return text

    def epic_close(self, text: str) -> str:
        """The decision log, the anti-pattern and closure checks, the handoff."""
        text = self.once(text, "  (FACT note).\n\n## Artifact Links (Optional)", "\n".join([
            "  (FACT note).",
            "- 2026-10-18T23:31:15Z: S1 (0.2.8257) and S2 (0.2.8258) turned in; rebuilt for 0.2.8258 at 23:43:33Z (FACT",
            "  notes).",
            f"- {self.now}: the owner's word - turn the epic in, S3-S5 to the backlog, no rebuild by this lane",
            "  (DECISION note); M2-24, M2-26, M2-27 and M1-42 consumed and the epic turned in (FACT notes).",
        ]) + "\n\n## Artifact Links (Optional)", "decision log")
        text = self.once(text, "\n".join([
            "- [ ] No epic-state transition without story-level evidence.",
            "- [ ] No closure while required stories are incomplete or unaccepted.",
            "- [ ] No program claims without source evidence from story/task notes.",
        ]), "\n".join([
            "- [x] No epic-state transition without story-level evidence.",
            "- [x] No closure while required stories are incomplete or unaccepted - escalated and decided: the owner",
            "  turned the epic in with S3-S5 parked in the backlog (DECISION note of the turn-in).",
            "- [x] No program claims without source evidence from story/task notes.",
        ]), "anti-patterns")
        text = self.once(text, "\n".join([
            "- [ ] Work walkthrough shared with user",
            "- [ ] Criteria, required tests/reviews and delegated acceptance or reserved-owner disposition recorded",
            "- [ ] Applicable anti-pattern checks are clear or escalated with evidence.",
        ]), "\n".join([
            "- [x] Work walkthrough shared with user",
            "- [x] Criteria, required tests/reviews and delegated acceptance or reserved-owner disposition recorded",
            "- [x] Applicable anti-pattern checks are clear or escalated with evidence.",
        ]), "closure checks")
        state = re.search(r"- State: in_progress \(melder_0\), implementation\..*?\n(?=- Done since: M1-37 consumed)",
                          text, flags=re.S)
        if state is None:
            sys.exit("handoff state")
        text = self.once(text, state.group(0), "\n".join([
            "- State: done (melder_0), turned in on the owner's word (2026-10-19): S1 (0.2.8257) and S2 (0.2.8258)",
            "  landed and were rebuilt for 0.2.8258; S3-S5 parked in the backlog with S6 and the configurables epic;",
            "  the leftovers (graph, expert guide, release-note sentences) packaged by melder_1's 0.2.8259 rebuild;",
            "  this lane runs no rebuild (the owner's word).",
        ]) + "\n", "handoff state")
        return self.once(text, "\n".join([
            "- Next: S3 (a changed binding revalidates), S4 (the refusal names the existing",
            "  registration) and S5 (records holding one object twice), each after its own patch, on",
            "  the owner's word.",
        ]), "\n".join([
            "- Done since: the staged copies cleaned - the cited run logs restored, the two modules and six tests",
            "  deleted with the owner's permission; M2-20 consumed, M0-206 sent; the graph leftovers and the expert",
            "  guide (FACT notes of 2026-10-19T00:00:36Z, 00:08:45Z and 00:18:40Z).",
            "- Done since: M2-24, M2-26, M2-27 and M1-42 consumed; turned in on the owner's word (DECISION and FACT",
            "  notes of the turn-in); M0-207 sent to melder_1 (melder_2 checked out).",
            "- Next: none in this epic. S3-S6 and EPIC-2026-10-18-identity_and_caching_configurables wait in the",
            "  backlog for the owner's word.",
        ]), "handoff next")

    def epic_body(self) -> None:
        """Every edit above and below the notes, then Updated; then the ranges the stories cite."""
        text = self.read(self.EPIC)
        text = self.epic_head(text)
        text = self.epic_plan(text)
        text = self.epic_close(text)
        self.stage(self.EPIC, text)
        self.set_field(self.EPIC, "Updated")
        start = self.note_range(self.EPIC, f"- DATETIME: {self.now}", "  TYPE: DECISION")
        self.decision_range = start.replace(self.EPIC, EPIC_DONE)
        policy = self.note_range(self.EPIC, "- DATETIME: 2026-10-18T14:14:10Z", "  TYPE: DECISION")
        self.policy_range = policy.replace(self.EPIC, EPIC_DONE)

    #endregion

    #region stories

    def park(self, rel: str, label: str, state: str, nxt: str, extra: List[str],
             cite: List[Tuple[str, object]]) -> None:
        """Park one draft story: the transition, a decision-log line and the handoff; then its FACT note, whose
        citations into this story are computed after the edits above them; then Updated."""
        text = self.read(rel)
        transition = re.search(r"## State Transition Event\n.*?\n\n(?=## )", text, flags=re.S)
        if transition is None:
            sys.exit(f"transition {rel}")
        text = self.once(text, transition.group(0), "\n".join([
            "## State Transition Event",
            "- from_state: draft",
            "- to_state: draft",
            "- transition_reason: parked in the backlog by the owner (the epic's DECISION note of the turn-in,",
            f"  {self.now}): the epic turned in after S1 and S2 landed.",
        ]) + "\n\n", f"transition {rel}")
        text = self.once(text, "\n\n## Artifact Links (Optional)", "\n" + "\n".join([
            f"- {self.now}: parked in tickets/stories/backlog/ on the owner's word; the epic turned in after S1 and",
            "  S2 landed (the epic's DECISION note).",
        ]) + "\n\n## Artifact Links (Optional)", f"decision log {rel}")
        text = self.once(text, state, "\n".join([
            f"- State: draft, parked in the backlog (the owner, {self.now[:10]}): the identity epic turned in after",
            "  S1 (0.2.8257) and S2 (0.2.8258) landed.",
            f"- Next: {nxt}",
        ]) + "\n", f"handoff {rel}")
        self.stage(rel, text)
        evidence = [self.decision_range]
        for kind, value in cite:
            if kind == "own_note":
                marker, type_line, moved_to = value
                evidence.append(self.note_range(rel, marker, type_line).replace(rel, moved_to))
            else:
                evidence.append(str(value))
        note = self.note(self.now, "FACT", [
            f"Parked in tickets/stories/backlog/ on the owner's word ({label}): the identity epic turned in after S1",
            "(0.2.8257) and S2 (0.2.8258) landed; this story waits there, with S6 and the configurables epic, for the",
            "owner to take the identity work up again. Status stays draft.",
        ] + extra, evidence, [
            "Nothing in this story is started; its scope, requirements and acceptance stand as written.",
        ], [nxt], "HELPFUL", 7)
        self.append_notes(rel, [note], f"park {rel}")
        self.set_field(rel, "Updated")

    def stories(self) -> None:
        """S3, S4 and S5."""
        self.park(self.S3, "S3", "- State: draft (melder_0); after S1 and S2.\n"
                                 "- Next: the component patch once S1 and S2 land.\n",
                  "the owner's word; then the component patch (which binding fields revalidate and which only rebind).", [
                      "The risk of its FACT note of 2026-10-18T16:24:12Z stands: under S1 and S2 a rebind under another",
                      "slotted existence can meet the removed definition's object.",
                  ], [("own_note", ("- DATETIME: 2026-10-18T16:24:12Z", "  TYPE: FACT", S3_BACKLOG))])
        self.park(self.S4, "S4", "- State: draft (melder_0); after S1.\n- Next: the component patch once S1 lands.\n",
                  "the owner's word; then the component patch (the refusal naming the existing registration).", [
                      "M1-42: melder_1's 0.2.8259 fixed the minted-index gap, so a second registration of a version alone",
                      "in a minted index is refused (M4b, M5b); both join its acceptance criteria.",
                  ], [("path", self.completion(S4C_DONE))])
        text = self.read(self.S4)
        text = self.once(text, "accepted under per-frame ids.\n\n## Validation / Test Plan", "\n".join([
            "accepted under per-frame ids.",
            "- A second registration of an object whose version sits alone in an index `remove_from_spell_index`",
            "  minted is refused - in another Book of its frame (M4b) and in another frame under process-wide ids",
            "  (M5b) - as 0.2.8259 made it (STORY-2026-10-17-minted_index_missing_from_frame_registry; M1-42).",
        ]) + "\n\n## Validation / Test Plan", "S4 acceptance")
        self.stage(self.S4, text)
        text = self.read(self.S5)
        text = self.once(text, "## Open Questions\n- The record policy for one object registered twice (rebuild the first "
                               "and report, or refuse).\n", "\n".join([
                                   "## Open Questions",
                                   "- None open: the record policy for one object registered twice is the owner's call -"
                                   " restore the first",
                                   "  and file a shortfall per dropped duplicate (the epic's DECISION note of"
                                   " 2026-10-18T14:14:10Z).",
                               ]) + "\n", "S5 open question")
        self.stage(self.S5, text)
        self.park(self.S5, "S5", "- State: draft (melder_0); after S1-S4's patches.\n"
                                 "- Next: the component patch with the others'.\n",
                  "the owner's word; then the component patch (records holding one object twice restore the first).", [
                      "Its open question is answered (the owner, the epic's DECISION note of 2026-10-18T14:14:10Z: restore",
                      "the first, a shortfall per dropped duplicate), so Open Questions says so.",
                  ], [("path", self.policy_range)])

    #endregion

    #region correctness epic

    def correctness(self) -> None:
        """M1-42's S4: the FACT note, the S4 box, the log, the handoff, Updated."""
        note = self.note(self.now, "FACT", [
            "M1-42 consumed (melder_1, 2026-10-19T00:25:06Z): S4 (STORY-2026-10-17-minted_index_missing_from_frame_registry)",
            "landed at 0.2.8259 and is turned in - the index remove_from_spell_index mints is registered with the frame as",
            "bind registers its new index, the root's teardown unregisters it with the rest, and residency reads its",
            "version parked until a notch - with the system documents, the graph and the release note, rebuilt last with",
            "both checks OK; spellbook.py and spell.py are melder_0's again and mutation_research.py is released. The",
            "identity epic (EPIC-2026-10-18-spell_identity_is_the_code) is turned in with its S1 and S2 landed and S3-S5",
            "parked, so S1, S2 and S5 here, which waited for it (M1-32), wait for the owner's word.",
        ], [
            self.completion(S4C_DONE),
            self.whole(f"{RUNS_S4C}/rebuild_asset_check_after_llm_0_2_8259.txt"),
            self.whole(f"{RUNS_S4C}/rebuild_llm_check_0_2_8259.txt"),
        ], [
            "S4, S6 and S9 are done and S10 withdrawn; S7 is next with melder_1, S8 stays on hold (M1-33), S3 waits for",
            "its open question, and S1, S2 and S5 for the owner.",
        ], [
            "Keep this record current as melder_1 lands S7.",
        ], "HELPFUL", 8)
        self.append_notes(CORRECTNESS, [note], "correctness note")
        text = self.read(CORRECTNESS)
        text = self.once(text, "\n".join([
            "- [ ] Story: STORY-2026-10-17-minted_index_missing_from_frame_registry - the index remove_from_spell_index",
            "  mints is missing from the frame's spell registry, so its version is unknown by spell_id (sweep A3).",
        ]) + "\n", "\n".join([
            "- [x] Story: STORY-2026-10-17-minted_index_missing_from_frame_registry - the index remove_from_spell_index",
            "  mints is missing from the frame's spell registry, so its version is unknown by spell_id (sweep A3). Landed",
            "  by melder_1 at 0.2.8259: the minted index is registered with the frame as bind registers its new one and",
            "  leaves with its root, and residency reads its version parked; turned in 2026-10-19 (M1-42), in",
            "  tickets/stories/completed/.",
        ]) + "\n", "correctness S4 box")
        text = self.once(text, "\n\n## Artifact Links (Optional)", "\n" + "\n".join([
            f"- {self.now}: M1-42 - S4 landed at 0.2.8259 and is turned in; S7 is next with melder_1; the identity",
            "  epic is turned in, so S1, S2 and S5 wait for the owner's word (FACT note).",
        ]) + "\n\n## Artifact Links (Optional)", "correctness log")
        text = self.once(text, "\n".join([
            "- State: in_progress (melder_0), handoff. A1-A12 are done; ten stories filed - S9 done (0.2.8256, the",
            "  refusal; M1-38); S8 blocked, on hold by the owner (M1-33); S4 next with melder_1, then S7; S3 waiting for its open",
            "  question; S1, S2 and S5 waiting for EPIC-2026-10-18-spell_identity_is_the_code (M1-32); S6 done; S10",
            "  withdrawn:",
        ]), "\n".join([
            "- State: in_progress (melder_0), handoff. A1-A12 are done; ten stories filed - S9 done (0.2.8256, the",
            "  refusal; M1-38) and S4 done (0.2.8259; M1-42); S8 blocked, on hold by the owner (M1-33); S7 next with",
            "  melder_1; S3 waiting for its open question; S1, S2 and S5 waiting for the owner's word, the identity epic",
            "  they waited for (EPIC-2026-10-18-spell_identity_is_the_code) being turned in with its S3-S5 parked (M1-32);",
            "  S6 done; S10 withdrawn:",
        ]), "correctness state")
        text = self.once(text, "\n".join([
            "  STORY-2026-10-17-minted_index_missing_from_frame_registry (p2; MutationResearch residency",
            "  misses the version too, A8),",
        ]), "\n".join([
            "  STORY-2026-10-17-minted_index_missing_from_frame_registry (p2; done: landed at 0.2.8259 with",
            "  residency's parked verdict, turned in 2026-10-19),",
        ]), "correctness S4 entry")
        nxt = re.search(r"- Next: \(1\) melder_1 fixes S4, then S7.*?a fourth tranche on the owner's word\.\n", text,
                        flags=re.S)
        if nxt is None:
            sys.exit("correctness next")
        text = self.once(text, nxt.group(0), "\n".join([
            f"- Done since: M1-42 consumed - S4 landed at 0.2.8259 and is turned in (FACT note of {self.now}).",
            "- Next: (1) melder_1 fixes S7 (S4 and S9 landed, M1-38, M1-42), and S8 when the owner lifts its hold (M1-32,",
            "  M1-33); (2) S3 after the owner answers its open question; S1, S2 and S5 on the owner's word, the identity",
            "  epic they waited for being turned in; (3) each fix with the patch gate, its notch and the rebuild; (4) a",
            "  fourth tranche on the owner's word.",
        ]) + "\n", "correctness next")
        self.stage(CORRECTNESS, text)
        self.set_field(CORRECTNESS, "Updated")

    #endregion

    #region boards

    def attention(self) -> None:
        """The identity row and detail out, the closed anchor in (capped at 12), the correctness row, the alerts."""
        text = self.read(self.BOARD)
        rows = re.findall(r"^\| spell_identity_is_the_code \|.*\n", text, flags=re.M)
        if len(rows) != 1:
            sys.exit(f"active row: {len(rows)}")
        text = text.replace(rows[0], "")
        detail = re.search(r"^- WORK_ITEM: spell_identity_is_the_code\n(?:  .*\n)+", text, flags=re.M)
        if detail is None:
            sys.exit("detail entry")
        text = self.once(text, detail.group(0), "", "detail entry")
        text = self.once(text, "Keep the record current as melder_1 fixes S4, then S7; S8 waits for the owner (M1-33).",
                         "Keep the record current as melder_1 fixes S7; S8 waits for the owner (M1-33).",
                         "correctness next")
        text = self.once(text, "| tickets/epics/2026-10-17_correctness_defects_epic.md | 2026-10-18T17:23:22Z |",
                         f"| tickets/epics/2026-10-17_correctness_defects_epic.md | {self.now} |", "correctness row")
        anchor = (f"| spell_identity_is_the_code | done | melder_0 | {EPIC_DONE} | Turned in on the owner's word: S1 "
                  "(0.2.8257) and S2 (0.2.8258) landed; S3-S5 parked in the backlog with S6; the leftovers packaged by "
                  "melder_1's 0.2.8259 rebuild. Next: S3-S6 on the owner's word. "
                  f"| {self.now} |")
        begin = "<!-- BEGIN USER-DEFINED: closed_anchors -->\n"
        text = self.once(text, begin, begin + anchor + "\n", "anchor")
        region = re.search(r"<!-- BEGIN USER-DEFINED: closed_anchors -->\n(.*?)<!-- END USER-DEFINED: closed_anchors -->",
                           text, flags=re.S)
        anchors = [line for line in region.group(1).split("\n") if line.startswith("| ")]
        while len(anchors) > 12:
            oldest = min(anchors, key=lambda line: line.rstrip(" |").rsplit("| ", 1)[1])
            print("drop anchor:", oldest[:60])
            text = self.once(text, oldest + "\n", "", "drop " + oldest[:30])
            anchors.remove(oldest)
        alerts_end = "<!-- END USER-DEFINED: alerts -->"
        for when, sender, tag in (("2026-10-19T00:12:26Z", "melder_2", "M2-24"),
                                  ("2026-10-19T00:25:06Z", "melder_1", "M1-42"),
                                  ("2026-10-19T00:35:22Z", "melder_2", "M2-26"),
                                  ("2026-10-19T00:43:26Z", "melder_2", "M2-27")):
            text = self.once(text, f"- NEW MESSAGE for melder_0 (from {sender}, {when})\n", "", f"alert {tag}")
        text = self.once(text, "\n" + alerts_end, "\n".join([
            "",
            f"- NEW MESSAGE for melder_1 (from melder_0, {self.now})",
            alerts_end,
        ]), "alerts")
        self.stage(self.BOARD, text)

    def artifacts(self) -> None:
        """Clear the identity epic's five active rows."""
        text = self.read(self.ARTIFACTS)
        region = re.search(r"<!-- BEGIN USER-DEFINED: active_artifacts -->\n(.*?)<!-- END USER-DEFINED: active_artifacts",
                           text, flags=re.S)
        active = [line for line in region.group(1).split("\n")
                  if line.startswith("| tickets/epics/2026-10-18_spell_identity_is_the_code_epic.md |")]
        if len(active) != 5:
            sys.exit(f"active rows: {len(active)}")
        for line in active:
            text = self.once(text, line + "\n", "", "active " + line[60:110])
        reasons = {
            "artifacts/correctness_defects_20261017/probes/probe_fingerprint_reads_code.py":
                "Epic closed: cases F1-F5 (what the retired fingerprint read) and their runs stay in the sweep's "
                "folder as the identity design's evidence.",
            "artifacts/correctness_defects_20261017/probes/probe_code_hash_prototype.py":
                "Epic closed: the code-hash prototype (P1-P10) S1 ported, with its runs, stays as the design's "
                "evidence.",
            "artifacts/correctness_defects_20261017/probes/probe_code_hash_internals.py":
                "Epic closed: cases I1-I9 (changes inside a method body) and their runs stay as the design's evidence.",
            "artifacts/spell_identity_20261018/":
                "Epic closed: the epic's scripts (opening, owner calls, apply and test tranches, landing, docs, graph, "
                "notch, turn-ins, mailbox passes, the leftovers and this turn-in) stay as the record of how S1 and S2 "
                "landed.",
            "artifacts/spell_identity_20261018/runs/":
                "Epic closed: S1 and S2's runs (probes, bind cost, build parity, examples, docs sweep and checks, "
                "rebuild logs), the graph leftovers' runs and the turn-in's mtimes and checks (turn_in/).",
        }
        cleared = []
        for line in active:
            path = line.split(" | ")[1]
            if path not in reasons:
                sys.exit(f"no reason for {path}")
            cleared.append(f"| {EPIC_DONE} | {path} | retain_as_reference | {reasons[path]} | {self.now} |")
        begin = "<!-- BEGIN USER-DEFINED: cleared_artifacts -->\n"
        text = self.once(text, begin, begin + "\n".join(cleared) + "\n", "cleared")
        self.stage(self.ARTIFACTS, text)

    #endregion


def main() -> None:
    record = TurnIn("turn_in_epic")
    record.mailbox()
    record.epic_notes()
    record.epic_body()
    record.stories()
    record.correctness()
    record.attention()
    record.artifacts()
    if "--write" not in sys.argv:
        print("CHECK OK", record.now, sorted(record.staged), record.decision_range, record.policy_range)
        return
    record.flush()


if __name__ == "__main__":
    main()
