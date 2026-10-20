"""S7 D7: hand the lane to the owner - S7 and the epic wait on the owner's acceptance (a reserved decision).

Story: Status blocked (the template's word for an unmet gate; the board row says review), the transition event, the
checklists, the handoff. Epic: Status blocked, the transition event, the S7 line, the two cross-cutting tasks, the
handoff and the synthesis note (an ALIGNMENT_CHECK read from a file). Board: the row to review / handoff with the
owner's acceptance as its blocker. Every replacement is asserted to occur exactly once; nothing is written on a miss.
The rebuild follows this script; its result is recorded afterwards.
Run from context_compass/: python <this file> <NOW> <epic note file>
"""
import pathlib
import re
import sys

NOW = sys.argv[1]
EPIC_NOTE = pathlib.Path(sys.argv[2]).read_text(encoding="utf-8").replace("<NOW>", NOW).rstrip("\n") + "\n"
STORY = pathlib.Path("tickets/stories/2026-10-15_managed_docs_release_story.md")
EPIC = pathlib.Path("tickets/epics/2026-10-14_managed_spell_quantity_epic.md")
BOARD = pathlib.Path("attention_board.md")


def swap(text: str, old: str, new: str, where: str) -> str:
    """Replace one exact block or stop."""
    if text.count(old) != 1:
        raise SystemExit(f"{where}: block occurs {text.count(old)} times (expected 1): {old[:70]!r}")
    return text.replace(old, new)


story = STORY.read_text(encoding="utf-8")
story = swap(story, "- Status: in_progress\n", "- Status: blocked\n", "story status")
story = re.sub(r"^- Updated: \S+$", "- Updated: " + NOW, story, count=1, flags=re.M)
story = swap(story,
             "- from_state: ready\n- to_state: in_progress\n"
             "- transition_reason: S6 landed and closed (0.2.8246, rebuilt and checked); S7 starts with the benchmarks.\n"
             "- prior: draft -> ready (2026-10-15T09:29:51Z): ready once S6 lands.\n",
             "- from_state: in_progress\n- to_state: blocked\n"
             "- transition_reason: S7's work is done - benchmarks, the four system docs and the graph, the README and docs\n"
             "  site, the release note, the archived patch lane, rubric scores - and the rebuild runs last; the EXIT_GATE's\n"
             "  remaining item is the owner's acceptance of the epic, a reserved decision. Unblock: the owner accepts or\n"
             "  redirects. The board row reads `review`.\n"
             "- prior: ready -> in_progress (2026-10-15T21:07:15Z): S6 landed and closed (0.2.8246, rebuilt and checked).\n"
             "- prior: draft -> ready (2026-10-15T09:29:51Z): ready once S6 lands.\n", "story transition")
story = swap(story,
             "- [ ] Benchmarks: the spike probes and the existing meld shapes, before and after.\n"
             "- [ ] Edit the system docs and regenerate indexes; descriptors and graph reassembly.\n"
             "- [ ] README and the release note.\n"
             "- [ ] Archive the patch docs; rebuild assets and bundles last; close the epic.\n"
             "- [ ] Enforce Ticket Microcycle across all linked tasks.\n"
             "- [ ] Record meaningful attributed findings in supported Notes/comments or authorized linked evidence.\n",
             "- [x] Benchmarks: the spike probes and the existing meld shapes, before and after.\n"
             "- [x] Edit the system docs and regenerate indexes; descriptors and graph reassembly.\n"
             "- [x] README and the release note.\n"
             "- [ ] Archive the patch docs (done); rebuild assets and bundles last (next); close the epic (the owner).\n"
             "- [x] Enforce Ticket Microcycle across all linked tasks.\n"
             "- [x] Record meaningful attributed findings in supported Notes/comments or authorized linked evidence.\n",
             "story tasks")
story = swap(story,
             "- [ ] No story-state transition without linked task-state evidence.\n"
             "- [ ] No closure while required tasks remain active or un-routed.\n"
             "- [ ] No cross-task synthesis claims without ticket-note evidence pointers.\n"
             "- [ ] No `src/` edit before the component patch and the mapping note exist.\n",
             "- [x] No story-state transition without linked task-state evidence.\n"
             "- [x] No closure while required tasks remain active or un-routed.\n"
             "- [x] No cross-task synthesis claims without ticket-note evidence pointers.\n"
             "- [x] No `src/` edit before the component patch and the mapping note exist (S7 changed no `src/` file).\n",
             "story anti-patterns")
story = swap(story,
             "- State: in_progress on 0.2.8246. Done: the benchmarks",
             "- State: blocked on the owner's acceptance (board: review), 0.2.8246. Done: the benchmarks", "story state")
story = swap(story,
             "- Next: archive the patch lane and sync the artifact board; rubric scores; S7 to review for the owner's acceptance\n"
             "  of the epic; rebuild last. For the owner: architecture_and_design (verified against 0.1.2) still lists six\n"
             "  members.\n",
             "  Then: the patch lane archived and both boards synced (FACT), the rubric scores (MEASURE: 83, 83, 83, 77; two\n"
             "  stale claims fixed while scoring).\n"
             "- Next: rebuild the assets and bundles and check them (last); then the owner accepts the epic (S1-S7) or\n"
             "  redirects, and rules on stamping parked versions. For the owner: architecture_and_design (verified against\n"
             "  0.1.2) still lists six members.\n", "story next")
STORY.write_text(story, encoding="utf-8")
print("story updated")

epic = EPIC.read_text(encoding="utf-8")
epic = swap(epic, "- Status: in_progress\n", "- Status: blocked\n", "epic status")
epic = re.sub(r"^- Updated: \S+$", "- Updated: " + NOW, epic, count=1, flags=re.M)
epic = swap(epic,
            "- from_state: in_progress (design iteration)\n- to_state: in_progress (build)\n"
            "- transition_reason: the owner authorized implementation on 2026-10-15 (\"implement it\") and asked for one story per\n"
            "  mechanic and an epic detailed enough to survive several compactions (Decision Log, 2026-10-15).\n",
            "- from_state: in_progress (build)\n- to_state: blocked\n"
            "- transition_reason: every story's work has landed (S1-S6 as 0.2.8241-0.2.8246; S7 documentation, no notch) and the\n"
            "  rebuild runs last; what remains is the owner's acceptance and the parked-stamp question, both reserved to the\n"
            "  owner (synthesis note of this timestamp). Unblock: the owner accepts or redirects.\n"
            "- prior: in_progress (design iteration) -> in_progress (build) (2026-10-15): the owner authorized implementation\n"
            "  (\"implement it\") and asked for one story per mechanic and an epic detailed enough to survive several\n"
            "  compactions (Decision Log, 2026-10-15).\n", "epic transition")
epic = swap(epic,
            "- [ ] S7 STORY-2026-10-15-managed_docs_release - system docs, graph, tests docs, README, release note, benchmarks.\n"
            "      tickets/stories/2026-10-15_managed_docs_release_story.md\n",
            "- [ ] S7 STORY-2026-10-15-managed_docs_release - system docs, graph, tests docs, README, release note, benchmarks.\n"
            "      Work done 2026-10-15, no notch; waits on the owner's acceptance of the epic.\n"
            "      tickets/stories/2026-10-15_managed_docs_release_story.md\n", "epic S7 line")
epic = swap(epic,
            "- [ ] Task: benchmark lease, release and the existing meld shapes before S5 and after S7 (probes in the spike folder).\n"
            "- [ ] Task: keep the running release note's managed section current at every landing (one section, extended).\n",
            "- [x] Task: benchmark lease, release and the existing meld shapes before S5 and after S7 (probes in the spike folder).\n"
            "      Done: S5's and S7's MEASURE notes (existing shapes within noise; the managed cycle 306-385 ns).\n"
            "- [x] Task: keep the running release note's managed section current at every landing (one section, extended).\n"
            "      Done: release_docs/next_version_release.md, the managed section and the packaging lines.\n", "epic tasks")
epic = swap(epic,
            "- Done: Milestones 1-3; the epic rewritten and archived; the architecture patch doc; the seven stories; S1-S6 landed\n"
            "  and closed (tickets/stories/completed/); U1-U11 settled (B2-B8).\n"
            "- Remaining: S7 (tickets/stories/2026-10-15_managed_docs_release_story.md: system docs, graph, tests docs, README,\n"
            "  release note, benchmarks before/after against baseline_0_2_8244/, patch promotion); the owner's call on stamping\n"
            "  versions staged before conjure (Open Questions); the owner's acceptance.\n",
            "- Done: Milestones 1-3; the epic rewritten and archived; the architecture patch doc; the seven stories; S1-S6 landed\n"
            "  and closed (tickets/stories/completed/); U1-U11 settled (B2-B8); S7's work (benchmarks, system docs and graph,\n"
            "  README and docs site, release note, patch lane archived, rubric scores; its story's Notes).\n"
            "- Remaining: the rebuild and its checks (last); the owner's acceptance of S1-S7 and the build decisions; the\n"
            "  owner's call on stamping versions staged before conjure (Open Questions). Status blocked on those; board review.\n",
            "epic done/remaining")
epic = swap(epic,
            "- Next 1-3 actions: rebuild the assets and bundles for 0.2.8246 and check them; S7 - read its story, the patch lane\n"
            "  and the system-doc sections the managed member touches.\n",
            "- Next 1-3 actions: rebuild the assets and bundles and check them; the owner accepts or redirects (synthesis note,\n"
            "  ALIGNMENT_CHECK of " + NOW + "); on acceptance close S7 and the epic and sync both boards.\n", "epic next")
marker = "\n## Closure Confirmation"
if epic.count(marker) != 1:
    raise SystemExit("epic: closure marker not unique")
epic = epic.replace(marker, "\n" + EPIC_NOTE + marker, 1)
EPIC.write_text(epic, encoding="utf-8")
print("epic updated")

board = BOARD.read_bytes().decode("utf-8")
old_row = re.compile(
    r"^\| melder_object_pools \| in_progress \| implementation \| claude \| melder_0 \| none \| [^|]+ \|"
    r"( [^|]+ \| [^|]+ \| tickets/stories/2026-10-15_managed_docs_release_story\.md \| )\S+( \| REQUIRED \|)$", re.M)
new_next = ("Owner: accept the epic (S1-S7) and its build decisions, rule on stamping parked versions, or redirect; "
            "rebuild checks recorded in S7.")
board, n = old_row.subn(lambda m: "| melder_object_pools | review | handoff | claude | melder_0 | owner acceptance "
                        "(reserved) | " + new_next + " |" + m.group(1) + NOW + m.group(2), board)
if n != 1:
    raise SystemExit(f"board row matched {n} times")
BOARD.write_bytes(board.encode("utf-8"))
print("board row updated")
