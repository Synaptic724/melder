"""
Turn in the per-frame spell worlds task and its investigation ticket on the owner's word (2026-09-30).

Usage: python turn_in.py <context_compass root>
Writes the closure fields, notes and state transitions, then syncs the attention, artifact and mailbox boards.
The ticket moves (mv -n into tickets/tasks/completed/) are done by the caller after this script succeeds.
"""
import datetime
import pathlib
import sys

CC = pathlib.Path(sys.argv[1])
NOW = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
BASIS = ('- Closure Basis: owner turn-in in chat (2026-09-30): "turn in the [work] you did then work on the next\n'
         '  thing".\n')
PER_FRAME = "tickets/tasks/2026-09-30_record_and_restore_per_frame_spell_worlds_task.md"
INVESTIGATION = "tickets/tasks/2026-09-30_investigate_aether_record_spell_id_regime_task.md"


def load(relative: str) -> str:
    """Read one LF board or ticket."""
    text = (CC / relative).read_bytes().decode("utf-8")
    if "\r\n" in text:
        raise SystemExit(f"{relative}: unexpected CRLF")
    return text


def swap(text: str, old: str, new: str, relative: str) -> str:
    """Replace one exact block."""
    if text.count(old) != 1:
        raise SystemExit(f"{relative}: anchor count {text.count(old)}: {old[:90]!r}")
    return text.replace(old, new)


def close(relative: str, summary: str, from_state: str, note: str) -> None:
    """Write the closure metadata, the state transition and the closing note of one ticket."""
    text = load(relative)
    text = swap(text, "- Status: review\n", "- Status: done\n", relative)
    updated = next(line for line in text.split("\n") if line.startswith("- Updated: "))
    text = swap(text, updated + "\n", f"- Updated: {NOW}\n- Completed: {NOW}\n" + BASIS + summary, relative)
    start = text.index("## State Transition Event\n")
    end = text.index("\n## ", start + 5)
    earlier = text[start:end].split("- transition_reason: ", 1)[1].strip()
    text = (text[:start] + "## State Transition Event\n- from_state: review\n- to_state: done\n"
            f"- transition_reason: ({NOW}) owner turn-in in chat. Earlier: {from_state} -> review: " + earlier + "\n"
            + text[end:])
    for box in ("- [ ] Acceptance criteria reviewed with user and confirmed",
                "- [ ] Board sync completed for successor routing or closure anchor update.",
                "- [ ] No closure without acceptance confirmation and board-sync completion.",
                "- [ ] Applicable anti-pattern checks are clear or escalated with evidence.",
                "- [ ] Steps complete and checked off", "- [ ] Deliverables produced and linked",
                "- [ ] Documentation updated (if needed)", "- [ ] Validation status recorded",
                "- [ ] Unknown-first discipline followed (`UNKNOWN` promoted to `FACT` only with evidence)",
                "- [ ] Notes quality maintained (`SCORE_0_TO_10` >=",
                "- [ ] No status transition without evidence-backed transition reason.",
                "- [ ] No implementation/validation from `UNKNOWN` or `HYPOTHESIS`.",
                "- [ ] No behaviour claim from a document or a search hit; read the code."):
        if box in text:
            text = text.replace(box, "- [x]" + box[5:])
    anchor = "\n## Context / Handoff Summary\n"
    text = swap(text, anchor, note + anchor, relative)
    (CC / relative).write_bytes(text.encode("utf-8"))
    print("closed", relative)


close(
    PER_FRAME,
    '- Summary: Per-frame spell-id worlds record and restore intact. The Aether record carries the spell-id regime\n'
    '  and restore stage 1 installs, reports or refuses it (notched 0.2.8213); spell custody is keyed per frame under\n'
    '  per-frame ids and replayed per Book, RecordVersion 4.0.0 (notched 0.2.8214). Release note sections "A restore\n'
    '  brings back the spell-id regime it recorded" and "Fixed: a class bound in several frames keeps every frame\'s\n'
    '  binding when recorded"; system docs, graph, assets and LLM bundles current (--check OK).\n',
    "in_progress",
    f"""
- DATETIME: {NOW}
  TYPE: DECISION
  CLAIM: The owner turned this lane in (chat): "turn in the [work] you did then work on the next thing". Closed with
    the investigation ticket; both move to tickets/tasks/completed/, the board rows become closed anchors, the
    artifact rows clear (implementation evidence retained, patch docs promoted and archived), and melder_0 releases
    its sole-writer claim (M0-132..134) through a NOTICE.
  EVIDENCE: tickets/tasks/2026-09-30_record_and_restore_per_frame_spell_worlds_task.md:1-20
  IMPACT: The lane is closed; the injected-provider epic (work package C) is next.
  NEXT: none for this ticket.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8
""",
)
close(
    INVESTIGATION,
    '- Summary: Measured in fresh processes: a per-frame spell-id world restored under process-wide ids (the Aether\n'
    '  record lacked the regime) and lost one frame\'s copy of a class bound in two frames (custody keyed by spell id)\n'
    '  while the restore reported complete. The owner picked A + B, landed in\n'
    '  tickets/tasks/completed/2026-09-30_record_and_restore_per_frame_spell_worlds_task.md (0.2.8213, 0.2.8214). No\n'
    '  source changed here.\n',
    "in_progress",
    f"""
- DATETIME: {NOW}
  TYPE: DECISION
  CLAIM: Turned in on the owner's word (chat), together with the implementation task that fixed both findings.
  EVIDENCE: tickets/tasks/2026-09-30_investigate_aether_record_spell_id_regime_task.md:1-20
  IMPACT: Closed; the probes and runs stay retained as reference.
  NEXT: none for this ticket.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8
""",
)

# Attention board: rows out, detail out, two anchors in (cap 12, oldest out).
board = load("attention_board.md")
for work_item in ("| per_frame_spell_worlds |", "| aether_record_spell_id_regime |"):
    row = next(line for line in board.split("\n") if line.startswith(work_item))
    board = swap(board, row + "\n", "", "attention_board.md")
board = swap(
    board,
    "- per_frame_spell_worlds: SWITCH_TRIGGER is the owner's turn-in (landed, docs, notches and rebuild done;\n"
    "  in review). RESUME_HIERARCHY:\n"
    "  tickets/tasks/2026-09-30_investigate_aether_record_spell_id_regime_task.md ->\n"
    "  tickets/tasks/2026-09-30_record_and_restore_per_frame_spell_worlds_task.md.\n",
    "",
    "attention_board.md",
)
anchors = (
    f"| per_frame_spell_worlds | done | melder_0 | tickets/tasks/completed/2026-09-30_record_and_restore_per_frame_spell_worlds_task.md "
    "| A: the Aether record carries the spell-id regime, restore stage 1 installs, reports or refuses it (0.2.8213); "
    "B: custody keyed per frame under per-frame ids, per-Book replay, RecordVersion 4.0.0 (0.2.8214); release note, "
    f"docs, graph, assets and LLM bundles; patch docs archived. Next: none. | {NOW} |\n"
    f"| aether_record_spell_id_regime | done | melder_0 | tickets/tasks/completed/2026-09-30_investigate_aether_record_spell_id_regime_task.md "
    "| Two measured defects in recording per-frame worlds (regime missing from the Aether record; one frame's copy "
    f"lost at record time); the owner picked A + B, landed with the per-frame task. Next: none. | {NOW} |\n"
)
board = swap(board, "<!-- BEGIN USER-DEFINED: closed_anchors -->\n",
             "<!-- BEGIN USER-DEFINED: closed_anchors -->\n" + anchors, "attention_board.md")
region_start = board.index("<!-- BEGIN USER-DEFINED: closed_anchors -->\n") + len("<!-- BEGIN USER-DEFINED: closed_anchors -->\n")
region_end = board.index("<!-- END USER-DEFINED: closed_anchors -->")
rows = [line for line in board[region_start:region_end].split("\n") if line.startswith("|")]
rows.sort(key=lambda line: line.rstrip(" |").rsplit("| ", 1)[1], reverse=True)
rows = rows[:12]
board = board[:region_start] + "\n".join(rows) + "\n" + board[region_end:]
(CC / "attention_board.md").write_bytes(board.encode("utf-8"))
print("attention board synced:", len(rows), "anchors")

# Artifact board: three active rows clear.
artifacts = load("artifact_board.md")
for prefix in (
        "| tickets/tasks/2026-09-30_investigate_aether_record_spell_id_regime_task.md | artifacts/aether_record_spell_id_regime_20260930/ |",
        "| tickets/tasks/2026-09-30_record_and_restore_per_frame_spell_worlds_task.md | artifacts/per_frame_spell_worlds_20260930/ |",
        "| tickets/tasks/2026-09-30_record_and_restore_per_frame_spell_worlds_task.md | system_docs/patches/completed/per_frame_spell_worlds_2026_09_30/ |",
):
    row = next(line for line in artifacts.split("\n") if line.startswith(prefix))
    artifacts = swap(artifacts, row + "\n", "", "artifact_board.md")
cleared = (
    "| tickets/tasks/completed/2026-09-30_record_and_restore_per_frame_spell_worlds_task.md | "
    "system_docs/patches/completed/per_frame_spell_worlds_2026_09_30/ | promote_to_documentation | Promoted to "
    "src_architecture, src_components and tests_components at landing (0.2.8213-0.2.8214); five patch docs archived. | "
    f"{NOW} |\n"
    "| tickets/tasks/completed/2026-09-30_record_and_restore_per_frame_spell_worlds_task.md | "
    "artifacts/per_frame_spell_worlds_20260930/ | retain_as_reference | Survey, red/green and suite logs, probe reruns, "
    f"src/test/doc/graph/release apply scripts and the 0.2.8214 rebuild and check logs. | {NOW} |\n"
    "| tickets/tasks/completed/2026-09-30_investigate_aether_record_spell_id_regime_task.md | "
    "artifacts/aether_record_spell_id_regime_20260930/ | retain_as_reference | Probe script and the S1-S3 record and "
    f"restore runs behind the two defects (0.2.8212). | {NOW} |\n"
)
artifacts = swap(artifacts, "<!-- BEGIN USER-DEFINED: cleared_artifacts -->\n",
                 "<!-- BEGIN USER-DEFINED: cleared_artifacts -->\n" + cleared, "artifact_board.md")
(CC / "artifact_board.md").write_bytes(artifacts.encode("utf-8"))
print("artifact board synced")

# Mailbox: release the sole-writer claim.
mailbox = load("mailbox_board.md")
claim = ("    lane (0.2.8213-0.2.8214) is turned in on the owner's word; melder_0 releases M0-132..134 on aether.py,\n"
         "    aether_configuration.py, aether_utility_system.py, spellbook.py (emit sites) and the crystallizer files.\n"
         "    Assets and LLM bundles stay current at 0.2.8214 (--check OK). Notch above 0.2.8214 if you land src after.\n")
messages = ""
for number, to in ((142, "fable_0"), (143, "muse_0"), (144, "melder_2")):
    messages += (f"- TO: {to}\n  FROM: melder_0\n  DATETIME: {NOW}\n  TYPE: NOTICE\n"
                 f"  CLAIM: M0-{number}. The per-frame spell worlds\n" + claim +
                 "  EVIDENCE: context_compass/tickets/tasks/completed/2026-09-30_record_and_restore_per_frame_spell_worlds_task.md\n"
                 "  ACK_REQUESTED: false\n")
mailbox = swap(mailbox, "<!-- END USER-DEFINED: messages -->", messages + "<!-- END USER-DEFINED: messages -->",
               "mailbox_board.md")
own = next(line for line in mailbox.split("\n") if line.startswith("| melder_0 | claude |"))
mailbox = swap(mailbox, own, f"| melder_0 | claude | 2026-09-26T22:24:06Z | {NOW} | active |", "mailbox_board.md")
(CC / "mailbox_board.md").write_bytes(mailbox.encode("utf-8"))
board = load("attention_board.md")
alerts = "".join(f"- NEW MESSAGE for {to} (from melder_0, {NOW})\n" for to in ("fable_0", "muse_0", "melder_2"))
board = swap(board, "<!-- END USER-DEFINED: alerts -->", alerts + "<!-- END USER-DEFINED: alerts -->", "attention_board.md")
(CC / "attention_board.md").write_bytes(board.encode("utf-8"))
print("mailbox NOTICE M0-142..144 sent", NOW)
