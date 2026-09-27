"""Closure of melder_2's five gauntlet tickets on the owner's turn-in (2026-09-26). --check writes nothing.

Tickets move by rename (the connected folder refuses deletes); the nested patch lane moves to patches/completed;
attention and artifact boards, the story and the measure task are synced in the same pass.
"""
import argparse
import os
import pathlib
import re
import sys
from typing import Dict, List, Tuple

CC = pathlib.Path.home() / "mnt/melder_private/context_compass"
T = CC / "tickets"
BASIS = ("owner turn-in in chat (~22:58Z): \"Turn in both (Recommended)\" for the nested slot-guard\n"
         "  implementation and the build-locks discovery, with P4, P1 and the tail attribution selected for turn-in in\n"
         "  the same answer; then \"then please remake the assets and I'll call it\".")
JOBS: Dict[str, Dict[str, object]] = {
    "2026-09-26_remove_nested_slot_guard_take_task.md": {
        "row": "gauntlet_nested_slot_guard",
        "summary": ("Door-called first builds of unique_per_conduit and spellspace roots take their build lock once\n"
                    "  (0.2.73): VM -3.3%/-3.6% per worker cycle, suites and soak green; docs, graph, assets and LLM bundles\n"
                    "  current at 0.2.74; the owner's 22:47Z Windows run is the best same-run result vs dishka (0.919x)."),
        "handoff": "Closed {now} on the owner's turn-in. Patch lane archived to\n"
                   "system_docs/patches/completed/nested_slot_guard_2026_09_26/.\n",
        "extra": [("  - system_docs/patches/active/nested_slot_guard_2026_09_26/\n",
                   "  - system_docs/patches/completed/nested_slot_guard_2026_09_26/\n")],
        "anchor": "Door-held first builds take their build lock once (0.2.73); VM -3.3%/-3.6% per worker cycle; docs, graph, "
                  "assets and LLM bundles at 0.2.74; owner run 0.919x dishka; owner turn-in.",
    },
    "2026-09-26_spellspace_build_locks_task.md": {
        "row": "gauntlet_spellspace_build_locks",
        "summary": ("Discovery answered: spellspace confinement does not cover melds from other threads, so the slot guard\n"
                    "  carries build-once. The safe win, the nested take, was implemented in its own task (0.2.73); a\n"
                    "  lock-free confined path would need a new thread rule and was not pursued."),
        "handoff": "Closed {now} on the owner's turn-in; the implementation is\n"
                   "tickets/tasks/completed/2026-09-26_remove_nested_slot_guard_take_task.md.\n",
        "extra": [("## Validation\n- Not run.\n",
                   "## Validation\n- Discovery only: no suites in this task. The implementation's validation is in\n"
                   "  tickets/tasks/completed/2026-09-26_remove_nested_slot_guard_take_task.md.\n")],
        "partial_step": ("- [x] VM prototype (no tree edit) of a lock-free confined path;",
                         "      path was not prototyped because it needs a new thread rule. Suites belong to an implementation task.\n",
                         "      Closed incomplete: the owner picked the nested-lock removal (21:37Z), done in its own task.\n"),
        "anchor": "Spellspace confinement does not cover foreign-thread melds; the nested take was the safe win (own task); "
                  "a lock-free path needs a thread rule; owner turn-in.",
    },
    "2026-09-26_spellspace_meld_warm_id_lane_task.md": {
        "row": "gauntlet_p4_spellspace_warm_lane",
        "summary": ("SpellSpace.meld serves warm id melds from the door's fast-door entry (0.2.68): about -17% per cached\n"
                    "  space meld on the VM; the owner's Windows runs show the SpellSpace window at parity with dishka on the\n"
                    "  request and worker_b lanes."),
        "handoff": "Closed {now} on the owner's turn-in.\n",
        "extra": [("- Owner machine: Not run.\n",
                   "- Owner machine: Windows runs from 19:31Z (0.2.68) to 22:47Z (0.2.74); same-run ratios in\n"
                   "  owner_run_20260926_ratios.txt, tail/owner_runs_1940_2005_ratios.txt and owner_run_20260926_2247_ratios.txt\n"
                   "  under artifacts/gauntlet_runtime_speed_20260926/.\n")],
        "anchor": "SpellSpace.meld warm id lane (0.2.68): about -17% per cached space meld; SpellSpace window at parity in "
                  "the owner's runs; owner turn-in.",
    },
    "2026-09-26_emit_positional_constructor_args_task.md": {
        "row": "gauntlet_p1_positional_args",
        "summary": ("Positional constructor arguments were validated and applied (16:16Z). The normal path then moved to\n"
                    "  melder_0's site-plan lowering (S2b-2) and the emitter was retired (R2); the positional rule lives on\n"
                    "  in the lowering (P5)."),
        "handoff": "Closed {now} on the owner's turn-in.\n",
        "extra": [("- Owner machine: Not run.\n",
                   "- Owner machine: every Windows run from 19:31Z on includes it, but it left the normal path with S2b-2,\n"
                   "  so no run isolates it.\n")],
        "anchor": "Positional constructor args applied (16:16Z); superseded on the normal path by the site-plan lowering "
                  "(P5 keeps the rule); owner turn-in.",
    },
    "2026-09-26_attribute_gauntlet_tail_spikes_task.md": {
        "row": "gauntlet_tail_spikes",
        "summary": ("Melder-only multi-millisecond cycle spikes attributed: turn-0 first-use hydration and compile, no GC\n"
                    "  in the loop; confirmed on Windows. Conjure-time hydration was withdrawn by owner direction; the\n"
                    "  optional 200k trend run was not done."),
        "handoff": "Closed {now} on the owner's turn-in.\n",
        "extra": [("## Validation\n- Not run yet.\n",
                   "## Validation\n- Owner Windows runs: 19:40Z (200k) and 20:05Z (30k GC probe) confirmed the attribution;\n"
                   "  22:47Z (0.2.74) shows the same turn-0 spike (max iteration 13.4 ms).\n")],
        "anchor": "Tail spikes attributed: turn-0 first use, no GC in the loop; confirmed on Windows; owner turn-in.",
    },
}


def section_append(t: str, heading: str, text: str) -> str:
    """Append `text` at the end of the section that starts at `heading`."""
    start = t.index(heading)
    nxt = t.find("\n## ", start + len(heading))
    return t[:start] + t[start:nxt].rstrip("\n") + "\n" + text + t[nxt:]


def close_ticket(name: str, job: Dict[str, object], now: str) -> str:
    """Return the closed text of one ticket in review."""
    t = (T / "tasks" / name).read_text(encoding="utf-8")
    assert t.count("\n- Status: review\n") == 1, (name, "status")
    t = t.replace("\n- Status: review\n", "\n- Status: done\n", 1)
    t = re.sub(r"\n- Updated: \S+\n", f"\n- Updated: {now}\n", t, count=1)
    t = t.replace("## Metadata\n", f"## Metadata\n- Completed: {now}\n- Closure Basis: {BASIS}\n"
                                   f"- Summary: {job['summary']}\n", 1)
    t = section_append(t, "## State Transition Event\n",
                       f"- from_state: review\n- to_state: done\n- transition_reason: Owner turn-in, {now}; see the Closure Basis.\n")
    for old, new in job.get("extra", []):
        assert t.count(old) == 1, (name, old[:50])
        t = t.replace(old, new)
    t = t.replace("- [ ] ", "- [x] ")
    if "partial_step" in job:
        step, tail_line, annotation = job["partial_step"]
        assert t.count(step) == 1 and t.count(tail_line) == 1, (name, "partial")
        t = t.replace(step, step.replace("- [x]", "- [ ]"))
        t = t.replace(tail_line, tail_line + annotation)
        t = t.replace("- [x] Steps complete and checked off\n",
                      "- [x] Steps complete and checked off (one step closed incomplete by the owner's pick; see Steps)\n")
    lines = t.split("\n")
    first = next(i for i, l in enumerate(lines) if l.startswith("- Completed: "))
    last = next(i for i in range(first, len(lines)) if lines[i].startswith("- Task ID: ")) - 1
    note = (f"- DATETIME: {now}\n  TYPE: DECISION\n  CLAIM: Closed on the owner's turn-in (see the Closure Basis); acceptance given.\n"
            f"  EVIDENCE: tickets/tasks/completed/{name}:{first + 1}-{last + 1}\n"
            "  IMPACT: The ticket moves to its completed folder; board and artifact rows are synced in the same pass.\n"
            "  NEXT: none.\n  REREAD: HELPFUL\n  SCORE_0_TO_10: 7\n")
    anchor = "\n## Context / Handoff Summary\n"
    assert t.count(anchor) == 1
    i = t.index(anchor)
    t = t[:i].rstrip("\n") + "\n\n" + note + t[i:]
    t = section_append(t, "## Context / Handoff Summary\n", str(job["handoff"]).format(now=now))
    for line in t.split("\n"):
        if len(line) > 120 and (line.startswith("- Summary:") or line.startswith("- Closure Basis:")):
            raise SystemExit(f"LONG {name}: {line[:70]}")
    return t


def sync_attention_board(now: str) -> str:
    """Remove the closed rows and details, add capped anchors, refresh the story row."""
    b = (CC / "attention_board.md").read_text(encoding="utf-8")
    anchors: List[str] = []
    for name, job in JOBS.items():
        row = str(job["row"])
        pat = re.compile(r"^\| " + re.escape(row) + r" \|.*\n", re.M)
        assert len(pat.findall(b)) == 1, row
        b = pat.sub("", b, count=1)
        lines = b.split("\n")
        start = next(i for i, l in enumerate(lines) if l.startswith(f"- {row}: SWITCH_TRIGGER"))
        end = start + 1
        while not (lines[end].startswith("- ") or lines[end].startswith("###")):
            end += 1
        b = "\n".join(lines[:start] + lines[end:])
        anchors.append(f"| {row} | done | melder_2 | tickets/tasks/completed/{name} | {job['anchor']} | {now} |")
    begin, end_marker = "<!-- BEGIN USER-DEFINED: closed_anchors -->\n", "<!-- END USER-DEFINED: closed_anchors -->"
    i, j = b.index(begin) + len(begin), b.index(end_marker)
    kept = [l for l in b[i:j].split("\n") if l.startswith("| ")]
    merged = anchors + kept
    b = b[:i] + "\n".join(merged[:12]) + "\n" + b[j:]
    pat = re.compile(r"^\| gauntlet_runtime_speed \|.*$", re.M)
    assert len(pat.findall(b)) == 1
    b = pat.sub(lambda m: ("| gauntlet_runtime_speed | in_progress | discovery | claude | melder_2 | none | Owner decides "
                           "whether an open lever (thread-affine pools, one-lock anonymous link, single-check fast door) is "
                           "worth a task. | Per-scope-cycle cost map vs dishka and dependency-injector, with ranked and "
                           "prototyped candidates. | Next lever validated and its task opened, or the owner redirects. | "
                           "tickets/tasks/2026-09-26_measure_gauntlet_scope_cycle_costs_task.md | " + now + " | REQUIRED |"),
                b, count=1)
    old = ("- gauntlet_runtime_speed: SWITCH_TRIGGER is the owner's Windows run on 0.2.74 (nested slot guard landed 22:41Z), or\n"
           "  the owner's answer on the SpellSpace scope RISK.")
    assert b.count(old) == 1
    b = b.replace(old, "- gauntlet_runtime_speed: SWITCH_TRIGGER is the owner's pick among the open levers, or the owner's\n"
                       "  answer on the SpellSpace scope RISK; P1, P4, the tail, build locks and nested slot guard are turned in.")
    return b


def sync_artifact_board(now: str) -> str:
    """Move the closed tickets' rows to the cleared list with their dispositions."""
    a = (CC / "artifact_board.md").read_text(encoding="utf-8")
    reasons = {
        "p1_positional_args/": "Apply script, diff and the two P1 test files; P1 superseded on the normal path by the lowering.",
        "p4_spellspace_warm_lane/": "Apply script, validated diff and the P4 component test; runs under vm_runs/p4_*.",
        "tail/": "VM probes and the owner's 19:40Z/20:05Z runs with same-run ratios; attribution accepted.",
        "spellspace_build_locks/": "Probes, prototype runs and the design sketch; the safe shape shipped as the nested task.",
        "nested_slot_guard/": "Edit/apply/close scripts, src.diff, tests, VM suites (0.2.73 and 0.2.74), A/B, soak, decomposition.",
    }
    cleared: List[str] = []
    for name in JOBS:
        pat = re.compile(r"^\| tickets/tasks/" + re.escape(name) + r" \| (\S+) \| [^|]+ \| [^|]+ \| (\S+) \|.*\n", re.M)
        rows = pat.findall(a)
        assert rows, name
        for path, disposition in rows:
            if path.startswith("system_docs/patches/active/"):
                done_path = path.replace("/active/", "/completed/")
                reason = ("Promoted to src_architecture and src_components (door-held first builds, 0.2.73), the graph "
                          "and the release note; three patch docs archived.")
                cleared.append(f"| tickets/tasks/completed/{name} | {done_path} | {disposition} | {reason} | {now} |")
            else:
                key = path.split("gauntlet_runtime_speed_20260926/")[1]
                cleared.append(f"| tickets/tasks/completed/{name} | {path} | {disposition} | {reasons[key]} | {now} |")
        a = pat.sub("", a)
    begin = "<!-- BEGIN USER-DEFINED: cleared_artifacts -->\n"
    i = a.index(begin) + len(begin)
    return a[:i] + "\n".join(cleared) + "\n" + a[i:]


def sync_story(now: str) -> str:
    """Tick the closed tasks, log the turn-in, add a note, refresh the handoff."""
    p = T / "stories" / "2026-09-26_gauntlet_runtime_speed_story.md"
    s = p.read_text(encoding="utf-8")
    for task_id in ("emit-positional-constructor-args", "spellspace-meld-warm-id-lane", "attribute-gauntlet-tail-spikes",
                    "spellspace-build-locks", "remove-nested-slot-guard-take"):
        old = f"- [ ] Task: TASK-2026-09-26-{task_id} "
        assert s.count(old) == 1, task_id
        s = s.replace(old, f"- [x] Task: TASK-2026-09-26-{task_id} ")
    old = ("- 2026-09-26T21:38:55Z: owner go-ahead to implement the nested slot-guard removal, safe shape only (\"just do it ... "
           "make it safe\"); melder_2 implements.\n")
    assert s.count(old) == 1
    s = s.replace(old, old + f"- {now}: owner turn-in of the nested slot-guard implementation, the build-locks discovery, P4, P1 "
                             "and the tail attribution after the 22:47Z Windows run.\n")
    s = re.sub(r"\n- Updated: \S+\n", f"\n- Updated: {now}\n", s, count=1)
    note = (f"- DATETIME: {now}\n  TYPE: DECISION\n"
            "  CLAIM: The owner turned in five child tasks after the 22:47Z Windows run: the nested slot-guard\n"
            "    implementation, the build-locks discovery, P4, P1 and the tail attribution. All moved to\n"
            "    tickets/tasks/completed/, and the nested patch lane moved to system_docs/patches/completed/. The story\n"
            "    stays open with the measure task, which holds the cost map and the open levers.\n"
            "  EVIDENCE:\n  - tickets/tasks/completed/2026-09-26_remove_nested_slot_guard_take_task.md:6-12\n"
            "  - attention_board.md:1-40\n"
            "  IMPACT: One active row remains in this story; the next step is the owner's pick among the open levers.\n"
            "  NEXT: Owner decides whether any open lever is worth a task.\n  REREAD: REQUIRED\n  SCORE_0_TO_10: 8\n")
    anchor = "\n## Context / Handoff Summary\n"
    i = s.index(anchor)
    s = s[:i].rstrip("\n") + "\n\n" + note + s[i:]
    i = s.index("## Context / Handoff Summary\n")
    j = s.index("\n## Project-Specific Additions")
    s = s[:i] + ("## Context / Handoff Summary\n"
                 "Attribution is done (measure task). Turned in: P1, P4, the tail attribution, the build-locks discovery and the\n"
                 "nested slot-guard removal (0.2.73; docs, graph, assets and LLM bundles at 0.2.74). The owner's 22:47Z Windows\n"
                 "run is the best same-run result vs dishka (hot_scopes/s 0.919x, per iteration 1.09x). Dropped: P3, interning,\n"
                 "conjure-time hydration; lever 1's lifecycle closed as measured. Open: the owner's pick among thread-affine pools\n"
                 "and the small redesigns, the SpellSpace active-scope RISK and the system_document_view race.\n") + s[j:]
    return s


def sync_measure_task(now: str) -> str:
    """Record the turn-ins in the attribution task and refresh its handoff."""
    p = T / "tasks" / "2026-09-26_measure_gauntlet_scope_cycle_costs_task.md"
    m = p.read_text(encoding="utf-8")
    note = (f"- DATETIME: {now}\n  TYPE: FACT\n"
            "  CLAIM: The owner turned in P1, P4, the tail attribution, the build-locks discovery and the nested slot-guard\n"
            "    removal after the 22:47Z Windows run (hot_scopes/s 0.919x dishka on 0.2.74). In that run most of the\n"
            "    per-iteration gap sits outside the measured cycles, and inside them in the outer scope's create and cleanup,\n"
            "    which lever 1 closed as measured.\n"
            "  EVIDENCE:\n  - artifacts/gauntlet_runtime_speed_20260926/owner_run_20260926_2247_ratios.txt:1-63\n"
            "  - tickets/tasks/2026-09-26_measure_gauntlet_scope_cycle_costs_task.md:1119-1149\n"
            "  IMPACT: This task keeps the cost map; the open levers wait for the owner's pick.\n"
            "  NEXT: Owner decides whether thread-affine pools or a small redesign is worth a task.\n"
            "  REREAD: REQUIRED\n  SCORE_0_TO_10: 8\n")
    anchor = "\n## Context / Handoff Summary\n"
    i = m.index(anchor)
    m = m[:i].rstrip("\n") + "\n\n" + note + m[i:]
    for old, new in (("- P1, positional constructor calls: in the tree since 16:16Z. melder_0's S2b-2 lowering took over the normal\n"
                      "  path, so P1 is in review until the owner decides with S2b-3.\n",
                      "- P1, positional constructor calls: turned in; the site-plan lowering carries the rule (P5).\n"),
                     ("- P4, SpellSpace.meld warm id lane: in the tree at 0.2.68, in review (its own task).\n",
                      "- P4, SpellSpace.meld warm id lane: in the tree at 0.2.68, turned in.\n"),
                     ("spellspace build locks moved to their own task, now in review.",
                      "spellspace build locks led to the nested slot-guard removal (0.2.73); both turned in.")):
        assert m.count(old) == 1, old[:40]
        m = m.replace(old, new)
    m = re.sub(r"\n- Updated: \S+\n", f"\n- Updated: {now}\n", m, count=1)
    return m


def main() -> int:
    """Build every closed or synced file; with --check stop there, otherwise write and move."""
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--now", required=True)
    args = ap.parse_args()
    now = args.now
    closed = {name: close_ticket(name, job, now) for name, job in JOBS.items()}
    board = sync_attention_board(now)
    artifacts = sync_artifact_board(now)
    story = sync_story(now)
    measure = sync_measure_task(now)
    print("built", len(closed), "tickets and 4 synced files")
    if args.check:
        return 0
    for name, text in closed.items():
        src, dst = T / "tasks" / name, T / "tasks" / "completed" / name
        assert not dst.exists(), dst
        src.write_text(text, encoding="utf-8")
        os.rename(src, dst)
        print("moved", dst.relative_to(CC))
    lane_src = CC / "system_docs/patches/active/nested_slot_guard_2026_09_26"
    lane_dst = CC / "system_docs/patches/completed/nested_slot_guard_2026_09_26"
    assert lane_src.is_dir() and not lane_dst.exists()
    os.rename(lane_src, lane_dst)
    print("moved", lane_dst.relative_to(CC))
    (CC / "attention_board.md").write_text(board, encoding="utf-8")
    (CC / "artifact_board.md").write_text(artifacts, encoding="utf-8")
    (T / "stories" / "2026-09-26_gauntlet_runtime_speed_story.md").write_text(story, encoding="utf-8")
    (T / "tasks" / "2026-09-26_measure_gauntlet_scope_cycle_costs_task.md").write_text(measure, encoding="utf-8")
    print("boards, story and measure task written")
    return 0


if __name__ == "__main__":
    sys.exit(main())
