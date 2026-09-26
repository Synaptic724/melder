"""Closure edits for melder_0's override lane tickets (owner turn-in 2026-09-26T20:55:47Z). --check writes nothing."""
import argparse
import datetime
import pathlib
import sys
from typing import Dict, List, Tuple

ROOT = pathlib.Path.home() / "mnt/melder_private/context_compass/tickets"
BASIS = ("owner turn-in (DECISION 2026-09-26T20:55:47Z in the lane task):\n"
         "  \"I trust your work its fine ... close your tickets\"; walkthrough waived by the owner.")


def section_insert(t: str, heading: str, text: str) -> str:
    """Append `text` at the end of the section that starts at `heading`."""
    start = t.index(heading)
    nxt = t.find("\n## ", start + len(heading))
    if nxt < 0:
        return t.rstrip("\n") + "\n" + text
    return t[:start] + t[start:nxt].rstrip("\n") + "\n" + text + t[nxt:]


def close(path: str, from_state: str, summary: str, note: str, handoff: str, ticks: List[Tuple[str, str]],
          now: str) -> str:
    """Return the closed text of one ticket."""
    p = ROOT / path
    t = p.read_text(encoding="utf-8")
    meta = t.index("## Metadata\n")
    head, body = t[:meta], t[meta:]
    status_old = f"\n- Status: {from_state}\n"
    assert body.count(status_old) >= 1, (path, "status")
    body = body.replace(status_old, "\n- Status: done\n", 1)
    i = body.index("\n- Updated: ")
    j = body.index("\n", i + 1)
    body = body[:i] + f"\n- Updated: {now}" + body[j:]
    body = body.replace("## Metadata\n", f"## Metadata\n- Completed: {now}\n- Closure Basis: {BASIS}\n- Summary: {summary}\n", 1)
    t = head + body
    t = section_insert(t, "## State Transition Event\n",
                       f"- from_state: {from_state}\n- to_state: done\n- transition_reason: Owner turn-in, {now}; see the Closure Basis.\n")
    t = section_insert(t, "## Notes\n", "\n" + note)
    t = section_insert(t, "## Context / Handoff Summary\n", handoff)
    for old, new in ticks:
        assert t.count(old) >= 1, (path, old)
        t = t.replace(old, new)
    for line in t.split("\n"):
        if len(line) > 120 and not line.lstrip().startswith(("- context_compass/", "- src/", "- tickets/", "| ")):
            if line.startswith("- Summary:") or line.startswith("- Closure Basis:"):
                raise SystemExit(f"LONG {path}: {line[:60]}")
    return t


def main() -> int:
    """Build every closed ticket, then write unless --check."""
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--now", required=True)
    a = ap.parse_args()
    now = a.now
    note = (f"- DATETIME: {now}\n  TYPE: DECISION\n  CLAIM: Closed on the owner's turn-in (see the Closure Basis): acceptance "
            "given, walkthrough waived.\n  EVIDENCE: tickets/tasks/2026-09-26_build_site_plan_lowering_task.md\n"
            "  IMPACT: The ticket moves to its completed folder; board and artifact rows are synced in the same pass.\n"
            "  NEXT: none.\n  REREAD: HELPFUL\n  SCORE_0_TO_10: 7\n")
    tick_done = [("- [ ] Acceptance criteria reviewed with user and confirmed", "- [x] Acceptance criteria reviewed with user and confirmed"),
                 ("- [ ] Board sync completed for successor routing or closure anchor update.",
                  "- [x] Board sync completed for successor routing or closure anchor update.")]
    jobs: Dict[str, Tuple[str, str, str, List[Tuple[str, str]]]] = {
        "tasks/2026-09-26_build_site_plan_lowering_task.md": (
            "in_progress",
            "S2-S6 delivered (0.2.59-0.2.71). Override melds run one plan per key set and never build a supplied\n"
            "  dependency; normal melds of the many_only and generalized families run the same runtime's normal plan;\n"
            "  every family raises UnresolvedInputError before construction; the Phase-5 per-path overlay, the\n"
            "  override-targeting surface and the old normal emitters are retired; docs, graph, build assets, LLM bundles\n"
            "  and release note are current at 0.2.71. Validation: per-step suites on 3.14t and GIL in Notes, not rerun\n"
            "  at closure. Owner follow-ups: the Phase-5 live-pool iteration RISK (19:32:26Z note) and the two unroll\n"
            "  benchmarks deleted in R2.",
            f"Closed {now} on the owner's turn-in. Patch lane archived to\n"
            "system_docs/patches/completed/override_site_plan_2026_09_26/ (retired_graph_descriptors/ inside).\n",
            [("- [ ] Validate on 3.14t and GIL; measure.", "- [x] Validate on 3.14t and GIL; measure (per step, in Notes)."),
             ("- [ ] Run Ticket Microcycle during execution:", "- [x] Run Ticket Microcycle during execution:"),
             ("- [ ] Document each meaningful finding immediately", "- [x] Document each meaningful finding immediately"),
             ("## Validation\n- Not run.\n", "## Validation\n- Per-step suites on 3.14t and GIL are in Notes; asset and document tests "
              "2026-09-26T20:58:58Z and\n  21:04:25Z; nothing was rerun at closure.\n"),
             ("  - system_docs/patches/active/override_site_plan_2026_09_26/\n", "  - system_docs/patches/completed/override_site_plan_2026_09_26/\n"),
             ("- [ ] Steps complete and checked off", "- [x] Steps complete and checked off"),
             ("- [ ] Deliverables produced and linked", "- [x] Deliverables produced and linked"),
             ("- [ ] Documentation updated (if needed)", "- [x] Documentation updated (if needed)"),
             ("- [ ] Validation status recorded", "- [x] Validation status recorded")] + tick_done),
        "tasks/2026-09-26_fix_collection_member_many_sharing_task.md": (
            "review",
            "Collection members get member-specific compiler paths in Phases 5 and 8, so each member builds its own\n"
            "  many dependencies (shared existences unchanged); cache generation 13; the site-plan lowering keeps member\n"
            "  sites apart. Patch doc archived with the story's lane.",
            f"Closed {now} on the owner's turn-in.\n",
            [("  - system_docs/patches/active/override_site_plan_2026_09_26/component_patch_collection_member_paths.md",
              "  - system_docs/patches/completed/override_site_plan_2026_09_26/component_patch_collection_member_paths.md")] + tick_done),
        "tasks/2026-09-26_design_override_and_caller_input_execution_task.md": (
            "review",
            "design_v2.md with the E1-E4 prototype results was approved 2026-09-26T11:26Z with Q1-Q5 as recommended\n"
            "  and built as STORY-2026-09-26-implement-override-site-plan-lowering (done). Artifacts retained as reference.",
            f"Closed {now} on the owner's turn-in; the design shipped as the site-plan lowering story.\n",
            []),
        "tasks/2026-09-26_trace_caller_input_conjure_strictness_regression_task.md": (
            "review",
            "Cause timeline recorded: the Phase-3 no-candidate failure predates 2026-06-15 and the internal-registration\n"
            "  guard (2026-07-15..08-01) blocked registering Package. Fixed by the unresolved-input sockets story (0.2.54)\n"
            "  and S4 of the site-plan lowering story. Artifacts retained as reference.",
            f"Closed {now} on the owner's turn-in; the fix shipped in 0.2.54 and 0.2.66-0.2.71.\n",
            []),
        "stories/2026-09-26_implement_override_site_plan_lowering_story.md": (
            "in_progress",
            "S1-S6 done (0.2.59-0.2.71): supplied overrides and their subtrees are never built; normal melds share the\n"
            "  lowering; unresolved inputs are decided before construction; conjure is linear in sites; the old emitters\n"
            "  and the targeting surface are retired; docs, graph, assets, LLM bundles and release note are current.",
            f"Closed {now} on the owner's turn-in. S2-S6 ran inside TASK-2026-09-26-build-site-plan-lowering; the patch\n"
            "lane is archived to system_docs/patches/completed/override_site_plan_2026_09_26/.\n",
            [("- [ ] Task: TASK-2026-09-26-fix-collection-member-many-sharing", "- [x] Task: TASK-2026-09-26-fix-collection-member-many-sharing"),
             ("- [ ] Task: S2 shared lowering", "- [x] Task: S2 shared lowering"),
             ("- [ ] Task: S3 key-set plans", "- [x] Task: S3 key-set plans"),
             ("- [ ] Task: S4 unresolved inputs", "- [x] Task: S4 unresolved inputs"),
             ("- [ ] Task: S5 retire the Phase-5", "- [x] Task: S5 retire the Phase-5"),
             ("- [ ] Task: S6 qualification", "- [x] Task: S6 qualification"),
             ("- [ ] Enforce Ticket Microcycle across all linked tasks.", "- [x] Enforce Ticket Microcycle across all linked tasks."),
             ("- [ ] Require meaningful-finding note updates", "- [x] Require meaningful-finding note updates"),
             ("- [ ] Work walkthrough shared with user", "- [x] Work walkthrough shared with user (waived by the owner at turn-in)"),
             ("- [ ] Acceptance criteria confirmed by user", "- [x] Acceptance criteria confirmed by user"),
             ("  - system_docs/patches/active/override_site_plan_2026_09_26/\n", "  - system_docs/patches/completed/override_site_plan_2026_09_26/\n")]),
        "epics/2026-09-24_override_execution_performance_epic.md": (
            "in_progress",
            "Diagnosis, design v2 and the site-plan lowering are delivered: override melds build only what the call does\n"
            "  not supply (3-of-5 supplied builds the other two plus the consumer, a component test) and ran 22-44% faster\n"
            "  on three benchmark graphs and 4.6x on the deep 511-site graph; normal melds share the lowering. All stories\n"
            "  and tasks done.",
            f"Closed {now} on the owner's turn-in; every story and task of the epic is in a completed folder.\n",
            [("- [ ] Implement and qualify the chosen optimization.", "- [x] Implement and qualify the chosen optimization."),
             ("(melder_0; in progress, S1 ready):\n  tickets/stories/2026-09-26_implement_override_site_plan_lowering_story.md",
              "(melder_0; done 2026-09-26):\n  tickets/stories/completed/2026-09-26_implement_override_site_plan_lowering_story.md")]
            + [(f"- [ ] TASK-2026-09-24-{s}:\n  tickets/tasks/2026-09-24_{s.replace('-', '_')}_task.md",
                f"- [x] TASK-2026-09-24-{s}:\n  tickets/tasks/completed/2026-09-24_{s.replace('-', '_')}_task.md")
               for s in ("discover-override-execution-semantics", "discover-override-occurrence-slicing",
                         "experiment-static-many-override-execution", "coordinate-override-execution-investigation",
                         "investigate-override-compiler-planning", "measure-melder-creation-and-overrides")]),
    }
    out: Dict[pathlib.Path, str] = {}
    for path, (frm, summary, handoff, ticks) in jobs.items():
        out[ROOT / path] = close(path, frm, summary, note, handoff, ticks, now)
        print("ok", path)
    if a.check:
        return 0
    for p, t in out.items():
        p.write_text(t, encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
