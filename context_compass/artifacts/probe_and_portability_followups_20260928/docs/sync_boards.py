"""Turn-in sync for the probe and portability follow-ups lane (melder_0, 2026-09-28).

Appends the closing NOTICEs, then applies the attention-board closure sync and alert lines, then the
artifact-board cleared row. Each shared file is re-read immediately before its write and read back after.
"""
import pathlib
import sys

now = sys.argv[1]
closed_at = sys.argv[2]
ticket = "tickets/tasks/completed/2026-09-28_finish_probe_and_doc_portability_followups_task.md"
base = ("The probe and portability follow-ups lane is turned in (owner direction, 2026-09-28): ConduitMeld\n"
        "    docstrings (0.2.8205) and src_architecture / src_components name no tooling path. melder_0 releases its\n"
        "    sole-writer claims on conduit_meld.py and those two documents. workflows_0's 0.2.8206 rebuild covers the\n"
        "    assets I waived (asset and LLM --check OK at 08:37Z). Notch above 0.2.8206 if you land a src change after.")
extra = {"fable_0": "\n    Your Meld and Spellbook graph nodes (meld.py, spellbook.py) are still SEMANTICS_STALE."}
recipients = [("fable_0", "M0-92"), ("muse_0", "M0-93"), ("melder_2", "M0-94")]


def rw(path: str, edit) -> None:
    p = pathlib.Path(path)
    raw = p.read_bytes().decode("utf-8")
    crlf = "\r\n" in raw
    text = edit(raw.replace("\r\n", "\n"))
    p.write_bytes((text.replace("\n", "\r\n") if crlf else text).encode("utf-8"))


def one(text: str, old: str, new: str) -> str:
    assert text.count(old) == 1, (text.count(old), old[:70])
    return text.replace(old, new, 1)


def mailbox(text: str) -> str:
    msgs = ""
    for who, mid in recipients:
        msgs += (f"- TO: {who}\n  FROM: melder_0\n  DATETIME: {now}\n  TYPE: NOTICE\n"
                 f"  CLAIM: {mid}. {base}{extra.get(who, '')}\n  EVIDENCE: context_compass/{ticket}\n"
                 f"  ACK_REQUESTED: false\n")
    return one(text, "<!-- END USER-DEFINED: messages -->", msgs + "<!-- END USER-DEFINED: messages -->")


def attention(text: str) -> str:
    lines = text.split("\n")
    row = [l for l in lines if l.startswith("| probe_portability_followups | in_progress |")]
    assert len(row) == 1, row
    text = one(text, row[0] + "\n", "")
    text = one(text, "- probe_portability_followups: SWITCH_TRIGGER is both follow-ups landed and turned in (owner"
               " direction, 2026-09-28).\n  RESUME_HIERARCHY: tickets/tasks/2026-09-28_finish_probe_and_doc_"
               "portability_followups_task.md.\n", "")
    oldest = [l for l in text.split("\n") if l.startswith("| comptime_ir_phase_pipeline | done | fable_0 |")]
    assert len(oldest) == 1, oldest
    text = one(text, oldest[0] + "\n", "")
    anchor = (f"| probe_portability_followups | done | melder_0 | {ticket} | ConduitMeld docstrings name each"
              " lifetime's store; src_architecture/src_components name no tooling path (both checks 0); ConduitMeld"
              " node accepted; notched 0.2.8205; waived rebuild covered by 0.2.8206 (asset/LLM checks OK)."
              f" Next: none. | {closed_at} |\n")
    text = one(text, "<!-- BEGIN USER-DEFINED: closed_anchors -->\n",
               "<!-- BEGIN USER-DEFINED: closed_anchors -->\n" + anchor)
    alerts = "".join(f"- NEW MESSAGE for {who} (from melder_0, {now})\n" for who, _ in recipients)
    return one(text, "<!-- END USER-DEFINED: alerts -->", alerts + "<!-- END USER-DEFINED: alerts -->")


def artifacts(text: str) -> str:
    row = (f"| {ticket} | artifacts/probe_and_portability_followups_20260928/ | retain_as_reference | Apply and edit"
           " scripts (docstrings, system docs, graph, closure), graph run logs and walker reports, the preservation"
           f" report, validation logs at 0.2.8205 and 0.2.8206. | {closed_at} |\n")
    return one(text, "<!-- BEGIN USER-DEFINED: cleared_artifacts -->\n",
               "<!-- BEGIN USER-DEFINED: cleared_artifacts -->\n" + row)


rw("mailbox_board.md", mailbox)
rw("attention_board.md", attention)
rw("artifact_board.md", artifacts)
print("synced", now)
