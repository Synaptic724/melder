"""Turn in the S9 task, its story and the static epic on the owner's directive; park the door story."""
import os
import re
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "executor_cache_world_stamp_20261003"))
from cc_helpers import now_utc, read_text, write_text, replace_once, check_line_lengths  # noqa: E402

CC = os.path.abspath(os.path.join(HERE, "..", ".."))
TS = now_utc()
TASK = "tickets/tasks/2026-10-03_certify_and_implement_site_store_constants_task.md"
STORY = "tickets/stories/2026-10-03_flat_warm_body_constants_story.md"
EPIC = "tickets/epics/2026-10-01_static_codegen_and_door_strategies_epic.md"
DOOR = "tickets/stories/2026-10-01_meld_door_strategies_story.md"
DOOR_PARKED = "tickets/stories/backlog/2026-10-01_meld_door_strategies_story.md"
S2A_PARKED = "tickets/stories/backlog/2026-10-01_existing_object_constants_story.md"


def completed_path(rel: str) -> str:
    head, name = rel.rsplit("/", 1)
    return f"{head}/completed/{name}"


def close_ticket(rel: str, summary: str, from_state: str, reason: str, updated_old: str) -> str:
    path = os.path.join(CC, rel)
    text, nl = read_text(path)
    lines = text.split("\n")
    assert lines[0].startswith("# "), lines[0]
    header = f"\n- Completed: {TS}\n- Summary: {summary}\n"
    assert "- Completed:" not in text
    text = lines[0] + "\n" + header + "\n".join(lines[1:])
    text = replace_once(text, f"- Status: {from_state}\n", "- Status: done\n", "status")
    text = replace_once(text, f"- Updated: {updated_old}\n", f"- Updated: {TS}\n", "updated")
    transition = f"- from_state: {from_state}\n- to_state: done\n- transition_reason: {reason}\n"
    m = re.search(r"## State Transition Event\n(?:.*\n)*?(?=\n## )", text)
    assert m, "transition section"
    text = text[:m.end()] + transition + text[m.end():]
    bad = check_line_lengths(header + transition)
    if bad:
        raise SystemExit(f"{rel}: lines over cap {bad}")
    write_text(path, text, nl)
    target = os.path.join(CC, completed_path(rel))
    assert not os.path.exists(target), target
    shutil.move(path, target)
    print("closed", rel, "->", completed_path(rel))
    return completed_path(rel)


done = {}

# ---- task ----
done[TASK] = close_ticket(
    TASK,
    "S9 landed at 0.2.8221: a unique site owned by an automatic conduit reads its owner store as a plan\n"
    "  constant (no alias line; dynamic, unowned and meld.<store> sites unchanged; misses byte-identical;\n"
    "  no generation bump); red on the tree's lowering, green with 4 unit + 3 component tests, every shard\n"
    "  green on the landed copy; plan -7..-17% on roots with unique providers on the VM; S11 retired as\n"
    "  already true; docs, graph, assets and bundles current; patch docs archived. Closed by the owner's\n"
    "  directive; full-tree suites and gauntlet Not run.",
    "review",
    f"Owner's turn-in directive ({TS}); notch 0.2.8221, note entry and rebuild\n  recorded at landing.",
    "2026-10-04T00:02:11Z",
)

# ---- story ----
path = os.path.join(CC, STORY)
text, nl = read_text(path)
text = replace_once(
    text,
    "- [ ] Task: TASK-2026-10-03-certify-and-implement-site-store-constants - harness S9/S11 columns, then the\n"
    "      emitter and hydrator edits with tests. tickets/tasks/2026-10-03_certify_and_implement_site_store_constants_task.md\n",
    "- [x] Task: TASK-2026-10-03-certify-and-implement-site-store-constants - harness S9/S11 columns, then the\n"
    f"      emitter and hydrator edits with tests. {done[TASK]}\n",
    "story task line")
note = (
    f"- DATETIME: {TS}\n"
    "  TYPE: DECISION\n"
    "  CLAIM: Owner (2026-10-04): the lane is turned in. S9 shipped at 0.2.8221 through the task (plan -7..-17% on the\n"
    "    VM's shapes with unique providers, dynamic plans byte-identical, no generation bump); S11 retired as already\n"
    "    true; S2a stays parked. The hydrator edits the narrative anticipated were not needed: the emitter binds the\n"
    "    constant itself because plans are emitted at hydration from rows. Owner-run suites and gauntlet: Not run.\n"
    "  EVIDENCE:\n"
    f"  - {done[TASK]}:1-12\n"
    "  IMPACT: Milestone 3 of the static epic is reached; the epic closes on the same directive.\n"
    "  NEXT: none for this story.\n"
    "  REREAD: HELPFUL\n"
    "  SCORE_0_TO_10: 7\n\n"
)
text = replace_once(text, "\n## Closure Confirmation\n", "\n" + note + "## Closure Confirmation\n", "story notes end")
text = replace_once(
    text,
    "- [ ] Work walkthrough shared with user\n- [ ] Acceptance criteria confirmed by user\n"
    "- [ ] Applicable anti-pattern checks are clear or escalated with evidence.\n",
    "- [x] Work walkthrough shared with user\n"
    "- [x] Acceptance criteria confirmed by user (turn-in directive, 2026-10-04; owner-run numbers Not run)\n"
    "- [x] Applicable anti-pattern checks are clear or escalated with evidence.\n",
    "story closure")
text = text.rstrip("\n").replace(
    "\n## Project-Specific Additions",
    f"\nSTATE {TS}: DONE. S9 shipped at 0.2.8221 and turned in by the owner's directive; suites and gauntlet Not run.\n"
    "\n## Project-Specific Additions") + "\n"
write_text(path, text, nl)
done[STORY] = close_ticket(
    STORY,
    "S9 shipped at 0.2.8221 through its task: an automatic world's unique sites read their owner store as\n"
    "  a plan constant; -7..-17% of the plan on the VM's shapes with unique providers; S11 already true;\n"
    "  S2a parked. Closed by the owner's directive; owner-run suites and gauntlet Not run.",
    "in_progress", f"Owner's turn-in directive ({TS}); the task is closed.",
    "2026-10-04T00:02:11Z",
)

# ---- door story: parked with the epic's closure ----
path = os.path.join(CC, DOOR)
text, nl = read_text(path)
text = replace_once(text, "- Status: ready\n", "- Status: ready (parked)\n", "door status")
text = replace_once(text, "- Updated: 2026-10-01T00:55:51Z\n", f"- Updated: {TS}\n", "door updated")
m = re.search(r"## State Transition Event\n(?:.*\n)*?(?=\n## )", text)
assert m, "door transition section"
transition = (
    "- from_state: ready\n- to_state: ready (parked)\n"
    f"- transition_reason: Parked in the backlog when the owner turned the static epic in ({TS}); the door\n"
    "  lane (epoch audit, door harness in dynamic posture, D5, D1-D3) reopens under a new epic on the owner's word.\n"
)
text = text[:m.end()] + transition + text[m.end():]
write_text(path, text, nl)
target = os.path.join(CC, DOOR_PARKED)
assert not os.path.exists(target), target
shutil.move(path, target)
print("parked", DOOR, "->", DOOR_PARKED)

# ---- epic ----
path = os.path.join(CC, EPIC)
text, nl = read_text(path)
text = replace_once(
    text,
    "- [ ] Milestone 3: the flat warm body (S9 + S11) shipped and turned in; S2a parked (owner, 2026-10-03).\n"
    "- [ ] Milestone 4: the door harness table landed; the certified door set named.\n"
    "- [ ] Milestone 5: the certified door strategies shipped or dropped with numbers.\n",
    "- [x] Milestone 3: the flat warm body (S9) shipped and turned in at 0.2.8221; S11 already true; S2a parked\n"
    "      (owner, 2026-10-03).\n"
    "- [ ] Milestone 4: the door harness table landed; the certified door set named. NOT REACHED - the epic was\n"
    "      closed by the owner's directive (2026-10-04); the door story is parked in the backlog.\n"
    "- [ ] Milestone 5: the certified door strategies shipped or dropped with numbers. NOT REACHED (same).\n",
    "milestones")
text = replace_once(
    text,
    "- [ ] Story: STORY-2026-10-03-flat-warm-body-constants (S9 + S11) - site and store constants and live key\n"
    "      objects on every shared site. tickets/stories/2026-10-03_flat_warm_body_constants_story.md\n",
    "- [x] Story: STORY-2026-10-03-flat-warm-body-constants (S9 + S11) - site and store constants and live key\n"
    f"      objects on every shared site. {done[STORY]}\n",
    "epic s9 story")
text = replace_once(
    text,
    "- [ ] Story: STORY-2026-10-01-meld-door-strategies (D1-D4) - a door harness, then the certified door\n"
    "      strategies. tickets/stories/2026-10-01_meld_door_strategies_story.md\n",
    "- [ ] Story: STORY-2026-10-01-meld-door-strategies (D1-D5) - a door harness, then the certified door\n"
    f"      strategies. PARKED at the epic's closure (owner, 2026-10-04). {DOOR_PARKED}\n",
    "epic door story")
epic_note = (
    f"- DATETIME: {TS}\n"
    "  TYPE: DECISION\n"
    "  CLAIM: Owner (2026-10-04): the lane and the epic are turned in. Shipped under this epic: S1 (0.2.8216), S8\n"
    "    (0.2.8217) and S9 (0.2.8221), each with tests, docs, graph, assets and a release-note section; S11 was found\n"
    "    already true; S4 dropped (noise); S2a parked (existing objects are rare). Not reached: the door lane\n"
    "    (Milestones 4-5: epoch audit, door harness in dynamic posture, D5, D1-D3) - its story is parked in the\n"
    "    backlog with the catalogue above as its brief, and reopens under a new epic on the owner's word. Owner-run\n"
    "    gauntlet numbers for the ranking: Not run at closure.\n"
    "  EVIDENCE:\n"
    f"  - {done[STORY]}:1-10\n"
    f"  - {done[TASK]}:1-12\n"
    f"  - {DOOR_PARKED}:1-12\n"
    "  IMPACT: No active lane in this epic; the tree is at 0.2.8221 with every landing's docs and assets current.\n"
    "  NEXT: none for this epic; the door lane and the PGO epic wait on the owner.\n"
    "  REREAD: HELPFUL\n"
    "  SCORE_0_TO_10: 8\n\n"
)
bad = check_line_lengths(epic_note, exempt=r"^  - tickets/")
if bad:
    raise SystemExit(f"epic note lines over cap: {bad}")
text = replace_once(text, "\n## Closure Confirmation\n", "\n" + epic_note + "## Closure Confirmation\n", "epic notes end")
text = replace_once(
    text,
    "- [ ] Work walkthrough shared with user\n- [ ] Acceptance criteria confirmed by user\n"
    "- [ ] Applicable anti-pattern checks are clear or escalated with evidence.\n",
    "- [x] Work walkthrough shared with user\n"
    "- [x] Acceptance criteria confirmed by user (closed by directive, 2026-10-04; the door strategies not reached)\n"
    "- [x] Applicable anti-pattern checks are clear or escalated with evidence.\n",
    "epic closure")
text = text.rstrip("\n").replace(
    "\n## Project-Specific Additions",
    f"\nSTATE {TS}: DONE. S1, S8 and S9 shipped (0.2.8216, 0.2.8217, 0.2.8221); the door lane not reached and parked;\n"
    "closed by the owner's directive.\n\n## Project-Specific Additions") + "\n"
write_text(path, text, nl)
done[EPIC] = close_ticket(
    EPIC,
    "Three static strategies shipped and turned in - S1 registration trim (0.2.8216), S8 lazy\n"
    "  instance_results (0.2.8217), S9 owner-store constants (0.2.8221) - with tests, docs, graph, assets and\n"
    "  release-note sections; S11 already true, S4 dropped, S2a parked; the door lane (D1-D5) not reached,\n"
    "  its story parked in the backlog. Closed by the owner's directive; owner-run gauntlet ranking Not run.",
    "in_progress", f"Owner's turn-in directive ({TS}); S9's story and task are closed, the door story\n  parked.",
    "2026-10-04T00:02:11Z",
)

# ---- attention board ----
board_path = os.path.join(CC, "attention_board.md")
board, nl = read_text(board_path)
start = "| flat_warm_body | review | handoff | claude | fable_0 | "
assert board.count(start) == 1
s = board.index(start)
e = board.index("\n", s) + 1
board = board[:s] + board[e:]
pat = r"^- flat_warm_body: SWITCH_TRIGGER.*\n(?:  .*\n)*"
ms = list(re.finditer(pat, board, re.MULTILINE))
assert len(ms) == 1, len(ms)
board = board[:ms[0].start()] + board[ms[0].end():]
begin = "<!-- BEGIN USER-DEFINED: closed_anchors -->\n"
end = "<!-- END USER-DEFINED: closed_anchors -->\n"
s = board.index(begin) + len(begin)
e = board.index(end)
rows = [r for r in board[s:e].split("\n") if r.strip()]
assert all(r.startswith("| ") for r in rows), rows[:2]


def closed_at(row: str) -> str:
    return row.rstrip("|").rstrip().rsplit("|", 1)[-1].strip()


ordered = sorted(range(len(rows)), key=lambda i: (closed_at(rows[i]), i))
new_rows = [
    f"| flat_warm_body | done | fable_0 | {done[TASK]} | S9 owner-store constants landed at 0.2.8221 (plan -7..-17% on roots with unique providers; dynamic plans byte-identical; no generation bump); S11 already true. Turned in by owner directive; suites and gauntlet Not run. Next: none. | {TS} |",
    f"| flat_warm_body_story | done | fable_0 | {done[STORY]} | The S9/S11 story behind the task; S2a parked. Turned in by owner directive. Next: none. | {TS} |",
    f"| static_codegen_and_door_strategies | done | fable_0 | {done[EPIC]} | S1, S8 and S9 shipped (0.2.8216/0.2.8217/0.2.8221); S4 dropped, S2a parked; the door lane (D1-D5) not reached, its story parked in the backlog. Closed by owner directive; gauntlet ranking Not run. Next: the door lane under a new epic on the owner's word. | {TS} |",
]
drop = set(ordered[:len(new_rows)])
kept = [rows[i] for i in range(len(rows)) if i not in drop]
assert len(kept) + len(new_rows) == 12, (len(kept), len(new_rows))
board = board[:s] + "\n".join(kept + new_rows) + "\n" + board[e:]
write_text(board_path, board, nl)
print("board synced; dropped anchors:", [rows[i].split("|")[1].strip() for i in sorted(drop)])

# ---- artifact board ----
art_path = os.path.join(CC, "artifact_board.md")
art, nl = read_text(art_path)
start = f"| {TASK} | artifacts/flat_warm_body_20261003/ | "
assert art.count(start) == 1
s = art.index(start)
e = art.index("\n", s) + 1
art = art[:s] + art[e:]
cleared = (
    f"| {done[TASK]} | artifacts/flat_warm_body_20261003/ | retain_as_reference | The S9 harness extension, the "
    "interleaved A/B runs and medians, the micro-benchmark, apply_s9.py and land_docs_s9.py (landed at 0.2.8221), "
    f"the red/green, shard, graph, rebuild and check logs. | {TS} |\n"
)
art = replace_once(art, "<!-- BEGIN USER-DEFINED: cleared_artifacts -->\n",
                   "<!-- BEGIN USER-DEFINED: cleared_artifacts -->\n" + cleared, "cleared begin")
old = f"| {TASK} | system_docs/patches/completed/flat_warm_body_2026_10_03/ |"
assert art.count(old) == 1
art = art.replace(old, f"| {done[TASK]} | system_docs/patches/completed/flat_warm_body_2026_10_03/ |")
assert art.count(f"| {TASK} |") == 0
write_text(art_path, art, nl)
print("artifact board synced", TS)
