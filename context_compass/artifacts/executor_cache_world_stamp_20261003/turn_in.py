"""Turn in the S8 task + story, the matcher task and the cache world-stamp task on the owner's directive."""
import os
import re
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from cc_helpers import now_utc, read_text, write_text, replace_once, check_line_lengths  # noqa: E402

CC = os.path.abspath(os.path.join(HERE, "..", ".."))
TS = now_utc()
S8_TASK = "tickets/tasks/2026-10-03_implement_lazy_instance_results_task.md"
MATCHER_TASK = "tickets/tasks/2026-10-03_resolve_annotations_by_address_key_task.md"
CACHE_TASK = "tickets/tasks/2026-10-03_require_world_stamp_for_executor_cache_full_hit_task.md"
S8_STORY = "tickets/stories/2026-10-01_lazy_instance_results_story.md"
EPIC = "tickets/epics/2026-10-01_static_codegen_and_door_strategies_epic.md"


def completed_path(rel: str) -> str:
    head, name = rel.rsplit("/", 1)
    return f"{head}/completed/{name}"


def close_ticket(rel: str, summary: str, from_state: str, reason: str, updated_old: str) -> str:
    path = os.path.join(CC, rel)
    text, nl = read_text(path)
    lines = text.split("\n")
    assert lines[0].startswith("# "), lines[0]
    header = (
        f"\n- Completed: {TS}\n- Summary: {summary}\n"
    )
    assert "- Completed:" not in text
    text = lines[0] + "\n" + header + "\n".join(lines[1:])
    text = replace_once(text, f"- Status: {from_state}\n", "- Status: done\n", "status")
    text = replace_once(text, f"- Updated: {updated_old}\n", f"- Updated: {TS}\n", "updated")
    transition = (
        f"- from_state: {from_state}\n- to_state: done\n- transition_reason: {reason}\n"
    )
    # Append the transition at the end of the State Transition Event section (before the next heading).
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


summaries = {
    S8_TASK: (
        "S8 landed at 0.2.8217: a dict-mode site plan builds a dict literal per generic construction and nothing on\n"
        "  the warm path, same objects and errors; plan -26..-32% and meld -22..-23% on the VM's dict-mode shapes,\n"
        "  direct-mode byte-identical; generation 17; docs, graph, assets and bundles current; patch docs archived. The\n"
        "  cache-staleness RISK found here was fixed in its own lane (0.2.8220). Closed by the owner's directive;\n"
        "  owner-run suites and gauntlet: Not run."
    ),
    MATCHER_TASK: (
        "Landed at 0.2.8218: Phase 3 matches annotations by address key - an existing object resolves by its class,\n"
        "  a TYPE_CHECKING string and a class object agree, the eq-risky gate is gone; unit and component regressions,\n"
        "  the harness bound bare, generation 18; docs, graph, README, assets and bundles current; patch docs archived.\n"
        "  The Autofac-strict tightening is not wanted (owner). Closed by the owner's directive; owner-run suites:\n"
        "  Not run."
    ),
    CACHE_TASK: (
        "Landed at 0.2.8220: the creation-cache bundle records the world stamp at staging and an executor full hit\n"
        "  requires it, so a world that only added or removed an existing creation recompiles instead of replaying a\n"
        "  stale executor; unit, integration and component regressions; the surplus full hit retired (one recompile);\n"
        "  generation 19; docs, graph, assets and bundles current; every test directory passed sharded on the landed\n"
        "  copy. Closed by the owner's directive; owner-run suites and gauntlet: Not run."
    ),
}
reasons = {
    S8_TASK: f"Owner's turn-in directive ({TS}); notch 0.2.8217, note entry and rebuild\n  recorded at landing.",
    MATCHER_TASK: f"Owner's turn-in directive ({TS}); notch 0.2.8218, note entry and rebuild\n  recorded at landing.",
    CACHE_TASK: f"Owner's turn-in directive ({TS}); notch 0.2.8220, note entry and rebuild\n  recorded at landing.",
}
updated = {S8_TASK: "2026-10-03T19:36:16Z", MATCHER_TASK: "2026-10-03T19:36:16Z", CACHE_TASK: "2026-10-03T21:16:19Z"}

done_paths = {}
for rel in (S8_TASK, MATCHER_TASK, CACHE_TASK):
    done_paths[rel] = close_ticket(rel, summaries[rel], "review", reasons[rel], updated[rel])

# --- the S8 story ---
story_path = os.path.join(CC, S8_STORY)
text, nl = read_text(story_path)
text = replace_once(
    text,
    "- [ ] Task: read `_emit_context`, `_emit_miss`, `_is_direct` and the generic step emission whole; write the\n"
    "      patch docs; map patch sections to edits and tests.\n"
    "      tickets/tasks/2026-10-03_implement_lazy_instance_results_task.md (carries both tasks below as well)\n"
    "- [ ] Task: implement the lazy dict, differential tests, generation bump; re-run the harness.\n",
    "- [x] Task: read `_emit_context`, `_emit_miss`, `_is_direct` and the generic step emission whole; write the\n"
    "      patch docs; map patch sections to edits and tests.\n"
    f"      {done_paths[S8_TASK]} (carries both tasks below as well)\n"
    "- [x] Task: implement the lazy dict, differential tests, generation bump; re-run the harness.\n", "story tasks")
note = (
    f"- DATETIME: {TS}\n"
    "  TYPE: DECISION\n"
    "  CLAIM: Owner (2026-10-03): S8 turned in. The implementation task landed at 0.2.8217 (plan -26..-32% on the two\n"
    "    dict-mode shapes, direct-mode byte-identical, generation 17) and closes with this story; the open question\n"
    "    (a warm-path read of instance_results) was answered from source - only a generic step constructed on the\n"
    "    warm path reads the dict, and it now reads a literal of exactly its keys. Owner-run gauntlet: Not run.\n"
    "  EVIDENCE:\n"
    f"  - {done_paths[S8_TASK]}:1-12\n"
    "  IMPACT: Milestone 2 of the static epic is reached; S2a (with S9/S11) is the next lane on the owner's word.\n"
    "  NEXT: none for this story.\n"
    "  REREAD: HELPFUL\n"
    "  SCORE_0_TO_10: 7\n\n"
)
text = replace_once(text, "\n## Closure Confirmation\n", "\n" + note + "## Closure Confirmation\n", "story notes end")
text = replace_once(
    text,
    "- [ ] Work walkthrough shared with user\n- [ ] Acceptance criteria confirmed by user\n",
    "- [x] Work walkthrough shared with user\n- [x] Acceptance criteria confirmed by user (turn-in directive, 2026-10-03)\n",
    "story closure")
text = replace_once(
    text,
    "STATE 2026-10-03T18:46:54Z: IN_PROGRESS. The implementation task is the active lane. Resume from its latest STATE line.\n",
    "STATE 2026-10-03T18:46:54Z: IN_PROGRESS. The implementation task is the active lane. Resume from its latest STATE line.\n"
    f"\nSTATE {TS}: DONE. S8 shipped at 0.2.8217 and turned in by the owner's directive; gauntlet Not run.\n", "story state")
write_text(story_path, text, nl)
done_paths[S8_STORY] = close_ticket(
    S8_STORY,
    "S8 shipped at 0.2.8217 through its implementation task: no instance_results dict on the warm path of a\n"
    "  dict-mode root, each generic construction reads a literal of exactly its keys; plan -26..-32% on the VM;\n"
    "  closed by the owner's directive, gauntlet Not run.",
    "in_progress", f"Owner's turn-in directive ({TS}); the implementation task is closed.",
    "2026-10-03T18:46:54Z")

# --- the epic ---
epic_path = os.path.join(CC, EPIC)
text, nl = read_text(epic_path)
text = replace_once(text, "- [ ] Milestone 2: S8 shipped and turned in.\n",
                    "- [x] Milestone 2: S8 shipped and turned in at 0.2.8217 (VM-measured; owner-run gauntlet Not run at turn-in).\n",
                    "milestone 2")
text = replace_once(
    text,
    "- [ ] Story: STORY-2026-10-01-lazy-instance-results (S8) - no instance_results dict on the warm path of a\n"
    "      dict-mode root. tickets/stories/2026-10-01_lazy_instance_results_story.md\n",
    "- [x] Story: STORY-2026-10-01-lazy-instance-results (S8) - no instance_results dict on the warm path of a\n"
    f"      dict-mode root. {done_paths[S8_STORY]}\n", "epic story")
text = replace_once(text, "- Updated: 2026-10-02T19:09:13Z\n", f"- Updated: {TS}\n", "epic updated")
epic_note = (
    f"- DATETIME: {TS}\n"
    "  TYPE: DECISION\n"
    "  CLAIM: Owner (2026-10-03): S8 turned in (task and story moved to completed/, closed by directive, gauntlet Not\n"
    "    run) together with two standalone defect lanes found on the way - annotation matching by address key\n"
    "    (0.2.8218) and the executor-cache world stamp (0.2.8220). Milestone 2 is checked. Next lane per the\n"
    "    recommendation: S2a with S9/S11 (one emitter pass; the harness certifies S9/S11 first), patch docs first;\n"
    "    the epic keeps no board row until the owner names the next lane.\n"
    "  EVIDENCE:\n"
    f"  - {done_paths[S8_STORY]}:1-10\n"
    f"  - {done_paths[S8_TASK]}:1-12\n"
    "  IMPACT: No active lane in this epic; the tree is at 0.2.8220 with every landing's docs and assets current.\n"
    "  NEXT: owner names the next lane (S2a per the recommendation, or other work).\n"
    "  REREAD: HELPFUL\n"
    "  SCORE_0_TO_10: 7\n\n"
)
text = replace_once(text, "\n## Closure Confirmation\n", "\n" + epic_note + "## Closure Confirmation\n", "epic notes end")
text = text.rstrip("\n").replace(
    "\n## Project-Specific Additions",
    f"\nSTATE {TS}: IN_PROGRESS (idle). S1 and S8 turned in; no routed lane; S2a (with S9/S11) opens on the owner's word\n"
    "with its patch docs first.\n\n## Project-Specific Additions") + "\n"
write_text(epic_path, text, nl)
print("epic updated")

# --- attention board ---
board_path = os.path.join(CC, "attention_board.md")
board, nl = read_text(board_path)
for item in ("executor_cache_world_stamp", "annotation_address_matching", "static_codegen_strategies"):
    start = f"| {item} | review | handoff | claude | fable_0 | "
    assert board.count(start) == 1, item
    s = board.index(start)
    e = board.index("\n", s) + 1
    board = board[:s] + board[e:]
    pat = rf"^- {re.escape(item)}: SWITCH_TRIGGER.*\n(?:  .*\n)*"
    ms = list(re.finditer(pat, board, re.MULTILINE))
    assert len(ms) == 1, (item, len(ms))
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
    f"| executor_cache_world_stamp | done | fable_0 | {done_paths[CACHE_TASK]} | Executor full hit requires the recorded world stamp (generation 19, 0.2.8220); the stale-executor defect fixed with unit/integration/component regressions; the surplus full hit retired. Turned in by owner directive; suites and gauntlet Not run. Next: none. | {TS} |",
    f"| annotation_address_matching | done | fable_0 | {done_paths[MATCHER_TASK]} | Phase 3 matches annotations by address key at 0.2.8218 (existing objects by class; string/object parity; generation 18). Turned in by owner directive; suites Not run. Next: the Autofac-strict tightening is not wanted. | {TS} |",
    f"| static_codegen_strategies | done | fable_0 | {done_paths[S8_STORY]} | S8 lazy instance_results shipped at 0.2.8217 (plan -26..-32% on dict-mode roots, generation 17); story and task turned in by owner directive; gauntlet Not run. Next: S2a (with S9/S11) on the owner's word. | {TS} |",
]
drop = set(ordered[:len(new_rows)])
kept = [rows[i] for i in range(len(rows)) if i not in drop]
assert len(kept) + len(new_rows) == 12, (len(kept), len(new_rows))
board = board[:s] + "\n".join(kept + new_rows) + "\n" + board[e:]
write_text(board_path, board, nl)
print("board synced; dropped anchors:", [rows[i].split("|")[1].strip() for i in sorted(drop)])

# --- artifact board ---
art_path = os.path.join(CC, "artifact_board.md")
art, nl = read_text(art_path)
moves = {
    CACHE_TASK: ("artifacts/executor_cache_world_stamp_20261003/", "apply_world_stamp.py and land_docs.py (landed at 0.2.8220), the red run on the tree's rule, the green, shard, rebuild and check logs."),
    S8_TASK: ("artifacts/lazy_instance_results_20261003/", "apply_s8.py (landed at 0.2.8217), the interleaved A/B (ab_medians_s8_n3_a.md), the unit/component and shard logs."),
    MATCHER_TASK: ("artifacts/annotation_address_matching_20261003/", "apply_key_matching.py (landed at 0.2.8218) and the shard logs of the working copy."),
}
cleared_rows = ""
for rel, (folder, reason) in moves.items():
    start = f"| {rel} | {folder} | "
    assert art.count(start) == 1, rel
    s = art.index(start)
    e = art.index("\n", s) + 1
    art = art[:s] + art[e:]
    cleared_rows += f"| {done_paths[rel]} | {folder} | retain_as_reference | {reason} | {TS} |\n"
art = replace_once(art, "<!-- BEGIN USER-DEFINED: cleared_artifacts -->\n",
                   "<!-- BEGIN USER-DEFINED: cleared_artifacts -->\n" + cleared_rows, "cleared begin")
for rel in (CACHE_TASK, S8_TASK, MATCHER_TASK):
    old = f"| {rel} | system_docs/patches/completed/"
    assert art.count(old) == 1, rel
    art = art.replace(old, f"| {done_paths[rel]} | system_docs/patches/completed/")
assert art.count("| tickets/tasks/2026-10-03_implement_lazy_instance_results_task.md |") == 0
assert art.count("| tickets/tasks/2026-10-03_resolve_annotations_by_address_key_task.md |") == 0
assert art.count("| tickets/tasks/2026-10-03_require_world_stamp_for_executor_cache_full_hit_task.md |") == 0
write_text(art_path, art, nl)
print("artifact board synced", TS)
