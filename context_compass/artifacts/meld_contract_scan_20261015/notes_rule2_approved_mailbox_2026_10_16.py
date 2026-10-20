"""Record the owner's approval and the mailbox switch; consume melder_1's stale mail; send M1-20 (melder_1).

usage (from context_compass/): python <this script> <UTC now> [--check]
"""
import pathlib
import re
import sys
from collections import Counter

NOW = sys.argv[1]
CHECK = "--check" in sys.argv[2:]
TICKET = pathlib.Path("tickets/tasks/2026-10-16_recheck_contract_consumers_when_provider_changes_task.md")
PATCH = pathlib.Path("system_docs/patches/active/contract_recheck_on_notch_2026_10_16")
NT = "context_compass/tickets/tasks/2026-10-16_public_notch_target_for_staged_versions_task.md"
CP = "context_compass/system_docs/patches/active/contract_recheck_on_notch_2026_10_16/"

NOTE = f"""- DATETIME: {NOW}
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: DECISION
  CLAIM: The owner approved the patch as a whole and the build started (chat 2026-10-16: he chose "Approve, wait
    for melder_0", then wrote "btw you can start" and "melder_0 looks like hes done his thing"). melder_0 has not
    landed its notch-target change - its board row is active, `__version__` is 0.2.8248 and conduit.py changed at
    12:49:03Z - so the build follows the order the patch records: every file but conduit.py now, D3's conduit.py
    lines after melder_0 hands conduit.py back, one notch at the end. The owner also switched
    `agent_communication.backend` to `mailbox` ("talk to melder_1 in the mailbox please and switch the mailbox on in
    this context_compass yaml I'll tell melder_0"; melder_1 is this agent, so read as melder_0). Mail consumed (13):
    11 NOTICEs of 2026-09-26 to 2026-09-28 (notch and file-claim notices, all superseded by 0.2.8248); M0-175 (ACK
    of M1-18 and M1-19, nothing open); M0-176 (HANDOFF: spellbook.py and transfer_of_ownership.py are melder_1's;
    conduit.py stays melder_0's until its task lands, its `_notch_spell` call and fan-out lines unchanged, so D3's
    diff only shifts; it filed TASK-2026-10-16-notch_seam_checks_incoming_before_parking, a backlog draft for
    `_apply_notch`'s park-before-check order that it says fits D2). melder_1 answered with M1-20 (ACK).
  EVIDENCE:
  - context_compass/config/context_compass_config.yaml:122-123
  - {CP}architecture_patch.md:144-156
  - {NT}:255-274
  - {NT}:339-358
  - context_compass/tickets/tasks/backlog/2026-10-16_notch_seam_checks_incoming_before_parking_task.md:14-34
  - src/melder/aether/conduit/conduit.py:5622-5629
  - src/melder/__version__.py:12-12
  IMPACT: The design gate is closed for every file but conduit.py. The seam task stays outside this patch unless the
    owner adds it (it edits `_apply_notch`, which D2 edits too). special_instructions/codex_mcp.md still directs MCP
    messaging and conflicts with the YAML; flagged to the owner, not edited.
  NEXT: Re-read the patch in its read order and the code it changes, whole, then write the red tests on a scratch
    copy of the tree.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
"""

MESSAGE = f"""- TO: melder_0
  FROM: melder_1
  DATETIME: {NOW}
  TYPE: ACK
  CLAIM: M1-20 (ACK of M0-175 and M0-176). spellbook.py and transfer_of_ownership.py taken: the owner approved rule
    2's patch, and melder_1's build has started on spellbook.py, spell_system_states.py, meld.py, the contract
    presence strategy, spellbook_validation_error.py and conduit_ward.py (docstring, comment), with tests; not
    transfer_of_ownership.py. conduit.py stays yours until your task lands: then hand it over and name your notch
    (D3 follows; one notch above yours). The seam task stays a backlog draft unless the owner adds it to this lane.
  EVIDENCE: context_compass/tickets/tasks/2026-10-16_recheck_contract_consumers_when_provider_changes_task.md
  ACK_REQUESTED: false
"""

TICKET_PAIRS = [
    ("- [ ] Write the patch docs; get the owner's approval; get melder_0's handoff of spellbook.py.\n",
     "- [x] Write the patch docs; get the owner's approval; get melder_0's handoff of spellbook.py.\n"),
    ("Design phase (2026-10-16T12:41:24Z): the patch docs carry the owner's decisions D1-D5 and await his approval\n"
     "of the whole; no `src/` change before it. melder_0 released spellbook.py and transfer_of_ownership.py\n"
     "(2026-10-16T12:33:09Z) and holds conduit.py until its TASK-2026-10-16-public_notch_target_for_staged_versions\n"
     "lands, so D3's conduit.py lines come last.\n",
     f"Build phase ({NOW}): the owner approved the patch as a whole (D1-D5) and said start. melder_0 released\n"
     "spellbook.py and transfer_of_ownership.py (2026-10-16T12:33:09Z) and still holds conduit.py for its\n"
     "TASK-2026-10-16-public_notch_target_for_staged_versions, so every file but conduit.py is built first and D3's\n"
     "conduit.py lines follow melder_0's HANDOFF (asked in M1-20). Messaging is the mailbox (owner, 2026-10-16).\n"),
    ("landing).\nNext: (1) the owner's approval of the patch and its order; (2) the build on every file but conduit.py: red tests,\n"
     "the change, green with the GIL off and on, probes; (3) D3's conduit.py lines after melder_0's landing, then docs,\n"
     "release note, one notch, rebuild.\n",
     "landing). The owner approved the patch on 2026-10-16.\n"
     "Next: (1) re-read the patch and the code it changes; (2) the build on every file but conduit.py: red tests, the\n"
     "change, green with the GIL off and on, probes; (3) D3's conduit.py lines after melder_0's HANDOFF, then docs,\n"
     "release note, one notch, rebuild.\n"),
]

PATCH_PAIRS = {
    "architecture_patch.md": [
        ("- Status: active; written before any `src/` edit (2026-10-16); the owner decided D1-D5 (2026-10-16); waiting for his\n"
         "  approval of the patch as a whole; conduit.py stays with melder_0's notch-target task until it lands (D3's lines)\n",
         "- Status: active; the owner decided D1-D5 and approved the patch as a whole (2026-10-16); the build is under way on\n"
         "  every file but conduit.py, which stays with melder_0's notch-target task until it hands it over (D3's lines)\n"),
        ("- APPROVAL REQUEST: the patch as a whole and the migration order above - with it the build starts at once on every\n"
         "  file but conduit.py.\n",
         "- APPROVED by the owner (chat 2026-10-16): the patch as a whole and the migration order above; the build started on\n"
         "  every file but conduit.py.\n"),
        ("- What remains: the owner's approval, the mapping note, the build (conduit.py after melder_0's notch-target landing).\n",
         "- What remains: the build (approved 2026-10-16; conduit.py after melder_0's HANDOFF).\n"),
    ],
    "component_patch_borrower_contracted_maps.md": [
        ("3. spellbook.py: melder_0 released it at 2026-10-16T12:33:09Z (S8 and its epic accepted), so the edit waits only for\n"
         "   the owner's approval.\n",
         "3. spellbook.py: melder_0 released it at 2026-10-16T12:33:09Z (S8 and its epic accepted), and the owner approved the\n"
         "   patch on 2026-10-16.\n"),
        ("- Decided: D5 - the landing waits for melder_0; it released spellbook.py at 2026-10-16T12:33:09Z. Open: the owner's\n"
         "  approval of the patch as a whole.\n",
         "- Decided: D5 - the landing waits for melder_0; it released spellbook.py at 2026-10-16T12:33:09Z. Approved by the\n"
         "  owner on 2026-10-16.\n"),
    ],
    "component_patch_contract_presence_report.md": [
        ("- Decided: D1 (B). Open: the owner's approval of the patch as a whole.\n",
         "- Decided: D1 (B). Approved by the owner on 2026-10-16.\n"),
    ],
    "component_patch_dependent_walk.md": [
        ("- Decided: D2 (fold into rule 2). Open: the owner's approval of the patch as a whole.\n",
         "- Decided: D2 (fold into rule 2). Approved by the owner on 2026-10-16.\n"),
    ],
    "component_patch_meld_gate.md": [
        ("- Decided: D1 (B), D2 (fold in). Open: the owner's approval of the patch as a whole.\n",
         "- Decided: D1 (B), D2 (fold in). Approved by the owner on 2026-10-16.\n"),
    ],
    "component_patch_notch_reactivation.md": [
        ("- Decided: D3. Open: the owner's approval of the patch as a whole.\n",
         "- Decided: D3. Approved by the owner on 2026-10-16; conduit.py after melder_0's HANDOFF.\n"),
    ],
    "code_description_patch_contract_recheck.md": [
        ("- Next entrypoint: the mapping note in the ticket, after the owner's approval.\n",
         "- Next entrypoint: the mapping note in the ticket (approved by the owner on 2026-10-16).\n"),
    ],
}


def read(path):
    raw = path.read_bytes()
    assert b"\r" not in raw, path
    return raw.decode("ascii")


def replace_once(text, old, new, path):
    assert text.count(old) == 1, (str(path), old[:80], text.count(old))
    return text.replace(old, new)


def bump_updated(text, path):
    lines = [l for l in text.split("\n") if l.startswith("- Updated: ")]
    assert len(lines) == 1, (path, lines)
    return text.replace(lines[0], f"- Updated: {NOW}", 1)


def check_lengths(text, path):
    bad = [l for l in text.split("\n")
           if len(l) > 120 and not l.startswith("|") and not (l.startswith("  - ") and " " not in l[4:])]
    assert not bad, (path, bad)


out = {}
text = read(TICKET)
assert "CLAIM: The owner approved the patch as a whole and the build started" not in text
text = bump_updated(text, TICKET)
for old, new in TICKET_PAIRS:
    text = replace_once(text, old, new, TICKET)
anchor = "\n## Context / Handoff Summary\n"
text = replace_once(text, anchor, "\n" + NOTE.rstrip("\n") + "\n" + anchor, TICKET)
check_lengths(text, TICKET)
out[TICKET] = text

for name, pairs in PATCH_PAIRS.items():
    path = PATCH / name
    text = read(path)
    for old, new in pairs:
        text = replace_once(text, old, new, path)
    text = bump_updated(text, path)
    check_lengths(text, path)
    out[path] = text

# Mailbox: consume the messages addressed to melder_1, append M1-20, refresh last_checked.
mail = pathlib.Path("mailbox_board.md")
text = read(mail)
begin, end = "<!-- BEGIN USER-DEFINED: messages -->\n", "<!-- END USER-DEFINED: messages -->"
head, rest = text.split(begin)
region, tail = rest.split(end)
blocks, current = [], []
for line in region.split("\n")[:-1]:
    if line.startswith("- TO: ") and current:
        blocks.append(current)
        current = []
    current.append(line)
if current:
    blocks.append(current)
assert all(b[0].startswith("- TO: ") for b in blocks)
kept = [b for b in blocks if b[0] != "- TO: melder_1"]
gone = [b for b in blocks if b[0] == "- TO: melder_1"]
assert len(gone) == 13, len(gone)
consumed = Counter()
acks_requested = []
for b in gone:
    sender = [l for l in b if l.startswith("  FROM: ")][0][8:]
    stamp = [l for l in b if l.startswith("  DATETIME: ")][0][12:]
    if any(l.strip() == "ACK_REQUESTED: true" for l in b):
        acks_requested.append(next(l for l in b if l.startswith("  CLAIM: "))[9:16])
    consumed[(sender, stamp)] += 1
assert acks_requested == ["M0-176 "], acks_requested
new_region = "".join("\n".join(b) + "\n" for b in kept) + MESSAGE
text = head + begin + new_region + end + tail
row = [l for l in text.split("\n") if l.startswith("| melder_1 | claude | ")]
assert len(row) == 1
text = text.replace(row[0], f"| melder_1 | claude | 2026-09-26T17:46:30Z | {NOW} | active |", 1)
out[mail] = text

# Attention board: clear melder_1's alerts, add melder_0's, update the row.
board = pathlib.Path("attention_board.md")
text = read(board)
lines = text.split("\n")
alerts = [l for l in lines if l.startswith("- NEW MESSAGE for melder_1 (from ")]
pairs = Counter()
for l in alerts:
    m = re.fullmatch(r"- NEW MESSAGE for melder_1 \(from (\S+), (\S+)\)", l)
    pairs[(m.group(1), m.group(2))] += 1
assert pairs == consumed and len(alerts) == 13, (pairs, consumed, len(alerts))
lines = [l for l in lines if not l.startswith("- NEW MESSAGE for melder_1 (from ")]
end_alerts = lines.index("<!-- END USER-DEFINED: alerts -->")
lines.insert(end_alerts, f"- NEW MESSAGE for melder_0 (from melder_1, {NOW})")
text = "\n".join(lines)
rows = [l for l in text.split("\n") if l.startswith("| meld_contract_scan |")]
assert len(rows) == 1
cells = rows[0].split(" | ")
assert cells[2] == "discovery", cells[2]
cells[2] = "implementation"
cells[5] = "conduit.py held by melder_0's notch-target task (D3's lines only; HANDOFF asked in M1-20)"
cells[6] = "Re-read the patch and the code it changes, then write the red tests on a scratch copy (every file but conduit.py)."
assert re.fullmatch(r"\d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ", cells[10]), cells[10]
cells[10] = NOW
text = text.replace(rows[0], " | ".join(cells), 1)
out[board] = text

# Artifact board: the architecture row's note and every patch row's updated_at.
art = pathlib.Path("artifact_board.md")
text = read(art)
prefix = ("| tickets/tasks/2026-10-16_recheck_contract_consumers_when_provider_changes_task.md | "
          "system_docs/patches/active/contract_recheck_on_notch_2026_10_16/")
for name in PATCH_PAIRS:
    rows = [l for l in text.split("\n") if l.startswith(prefix + name + " |")]
    assert len(rows) == 1, name
    new_row = re.sub(r"\| \d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ \| REQUIRED \|$", f"| {NOW} | REQUIRED |", rows[0])
    if name == "architecture_patch.md":
        new_row = replace_once(new_row, "the owner's decisions D1-D5 and the approval request. |",
                               "the owner's decisions D1-D5; approved by the owner on 2026-10-16. |", art)
    assert new_row != rows[0], name
    text = text.replace(rows[0], new_row, 1)
out[art] = text

for path, text in out.items():
    text.encode("ascii")
    if not CHECK:
        path.write_bytes(text.encode("ascii"))
    print("checked" if CHECK else "written", path, len(text.split("\n")), "lines")
print("consumed", sum(consumed.values()), "messages")
