"""Closure pass for EPIC-2026-09-27-aether-conduit-lookup-api and melder_0's other open tickets (owner turn-in).

Computes every ticket edit in memory, asserts each anchor, then writes. Moves happen in bash afterwards.
Run from context_compass/: python ~/apply/close_lane.py <CLOSE_TS>
"""
import pathlib
import re
import sys

CLOSE = sys.argv[1]
QUOTE_1 = ('- Closure Basis: owner acceptance and turn-in in chat (2026-09-27): "yeah accepted turn in everything call it all\n'
           '  and stay signed in but finish off your work".\n')
TASK_DONE = "tickets/tasks/completed/2026-09-27_implement_aether_conduit_lookup_api_task.md"
RECOUNT = "context_compass/artifacts/aether_lookup_api_survey_20260927/usage_survey_recount_0279.txt:55-96"
FINAL = "context_compass/artifacts/aether_conduit_lookup_api_impl_20260927/suites_final_0279_vm.txt:1-38"
out = {}


def load(path):
    return pathlib.Path(path).read_bytes().decode("utf-8")


def rep(text, old, new, path, count=1):
    found = text.count(old)
    assert found == count, f"{path}: expected {count} of {old[:70]!r}, found {found}"
    return text.replace(old, new)


def metadata(text, path, status_old, summary):
    text = rep(text, f"- Status: {status_old}\n", "- Status: done\n", path)
    m = re.search(r"- Updated: \S+\n", text)
    assert m, path
    block = f"- Updated: {CLOSE}\n- Completed: {CLOSE}\n" + QUOTE_1 + summary
    return text[:m.start()] + block + text[m.end():]


def add_note(text, path, note):
    anchor = "\n## Closure Confirmation\n" if "\n## Closure Confirmation\n" in text else "\n## Context / Handoff Summary\n"
    return rep(text, anchor, note + anchor, path)


def check_width(text, path):
    orig = set(load(path).splitlines())
    for i, line in enumerate(text.splitlines(), 1):
        if line in orig:
            continue
        if len(line) > 120 and not line.startswith("|"):
            raise SystemExit(f"{path}:{i} is {len(line)} chars: {line[:60]!r}")


# ---------------------------------------------------------------- stories
STORY = {
    "list_conduit_ids_root_rename": ("`list_conduit_ids` is now `list_root_conduit_ids` (hard rename, same root-only answers); "
                                     "TransferOfOwnership sweeps impacted lineages with it.",
                                     ["src/melder/aether/aether.py:1687-1718",
                                      "src/melder/aether/conduit/conduit_ward/transfer/transfer_of_ownership.py:752-816"]),
    "list_conduit_names_root_rename": ("`list_conduit_names` is now `list_root_conduit_names` (hard rename, same "
                                       "root-only answers).", ["src/melder/aether/aether.py:1720-1750"]),
    "count_conduits_root_rename": ("`count_conduits` is now `count_root_conduits`; it reads the root registry "
                                   "directly (same answers, no id tuple built).", ["src/melder/aether/aether.py:1752-1778"]),
    "has_conduit_id_root_rename": ("`has_conduit_id` is now `has_root_conduit_id` (hard rename, same root-only "
                                   "answers).", ["src/melder/aether/aether.py:1780-1813"]),
    "has_conduit_name_root_rename": ("`has_conduit_name` is now `has_root_conduit_name` (hard rename, same root-only "
                                     "answers).", ["src/melder/aether/aether.py:1815-1848"]),
    "find_conduit_id_by_name_root_rename": ("`find_conduit_id_by_name` is now `find_root_conduit_id_by_name` and returns "
                                            "Optional[str] (same root-only answers).",
                                            ["src/melder/aether/aether.py:1850-1883"]),
    "get_conduit_by_name_root_rename": ("The root-only lookup is `get_root_conduit_by_name` (private helper "
                                        "`_get_root_conduit_by_name`); the generic name now answers named scopes.",
                                        ["src/melder/aether/aether.py:1885-1919",
                                         "src/melder/aether/aether.py:2135-2175"]),
    "get_conduit_by_id_root_rename": ("The root-only lookup is `get_root_conduit_by_id` (private helper "
                                      "`_get_root_conduit_by_id`, which spell-owner resolution and StaticCommandSystem "
                                      "use); the generic name now answers any live conduit.",
                                      ["src/melder/aether/aether.py:1921-1954",
                                       "src/melder/aether/aether.py:2177-2256"]),
    "find_any_conduit_by_name": ("`Aether.get_conduit_by_name` answers over the frame Cloud's named directory: named "
                                 "roots and active named lessers at any depth; returned scopes do not resolve.",
                                 ["src/melder/aether/aether.py:1956-2011"]),
    "find_any_conduit_by_id": ("`Aether.get_conduit_by_id` answers over every live conduit: the root map, then each root "
                               "ward's snapshot walk; CommandSystem and StaticFrameViewer now delegate to it.",
                               ["src/melder/aether/aether.py:2013-2107",
                                "src/melder/aether/conduit/conduit_ward/conduit_ward.py:1220-1268",
                                "src/melder/nexus/rift/command_system/command_system.py:194-248",
                                "src/melder/nexus/rift/frame_viewer/static_frame_viewer.py:306-333"]),
}
CLOUD = ("`ConduitCloud.list_conduits()` returns a snapshot tuple of the frame's named conduits (named roots and "
         "active named lessers) under the Cloud lock.", ["src/melder/aether/aetheric_frame/conduit_cloud.py:578-609"])


def wrap(prefix, text, indent="    ", width=116):
    words, lines, cur = text.split(), [], prefix
    for w in words:
        if len(cur) + 1 + len(w) > width and cur.strip():
            lines.append(cur)
            cur = indent + w
        else:
            cur = (cur + " " + w) if cur.strip() else (cur + w)
    lines.append(cur)
    return "\n".join(lines) + "\n"


def story(path, claim, evidence):
    text = load(path)
    summ = wrap("- Summary:", "Delivered at 0.2.79 by TASK-2026-09-27-implement-aether-conduit-lookup-api and accepted "
                "by the owner: " + claim, indent="  ")
    text = metadata(text, path, "in_progress", summ)
    text = rep(text, "\n## Dependencies / Related Work\n",
               "- from_state: in_progress\n- to_state: done\n"
               f"- transition_reason: Delivered at 0.2.79 and accepted with the epic (owner turn-in, chat, {CLOSE}).\n"
               "\n## Dependencies / Related Work\n", path)
    text = re.sub(r"- \[ \] (Usage survey|Design facts)", r"- [x] \1", text, count=1)
    text = rep(text, "- [ ] Task: TASK-2026-09-27-implement-aether-conduit-lookup-api",
               "- [x] Task: TASK-2026-09-27-implement-aether-conduit-lookup-api", path)
    text = rep(text, "## Validation / Test Plan\n- Not run.\n",
               "## Validation / Test Plan\n- Run: see the task's Validation (3.14t whole tree green; GIL subsets green).\n", path)
    text = rep(text, "## Open Questions\n",
               "## Open Questions\n- None open at closure: the owner's 2026-09-27 decisions (Decision Log) answer them.\n", path)
    for box in ("Work walkthrough shared with user", "Acceptance criteria confirmed by user"):
        text = rep(text, f"- [ ] {box}", f"- [x] {box}", path)
    ev = "".join(f"  - {e}\n" for e in evidence + [TASK_DONE, RECOUNT])
    note = (f"- DATETIME: {CLOSE}\n  TYPE: FACT\n"
            + wrap("  CLAIM:", "Delivered at 0.2.79 and accepted (owner turn-in, chat 2026-09-27): " + claim
                   + " Every surveyed usage is migrated (recount); suites green on 3.14t and GIL.")
            + "  EVIDENCE:\n" + ev
            + "  IMPACT: Acceptance criteria met; the story closes with the epic.\n"
            + "  NEXT: none (closed).\n  REREAD: HELPFUL\n  SCORE_0_TO_10: 7\n")
    note = "\n" + note
    notes_anchor = "\n## Closure Confirmation\n"
    text = rep(text, notes_anchor, note + notes_anchor, path)
    text = rep(text, "## Context / Handoff Summary\n",
               f"## Context / Handoff Summary\nClosed {CLOSE}: delivered at 0.2.79 by the epic's implementation task and "
               "accepted by the owner.\n", path)
    check_width(text, path)
    out[path] = text


for key, (claim, ev) in STORY.items():
    story(f"tickets/stories/2026-09-27_aether_{key}_story.md", claim, ev)
story("tickets/stories/2026-09-27_conduit_cloud_list_all_conduits_story.md", *CLOUD)

# ---------------------------------------------------------------- implementation task
p = "tickets/tasks/2026-09-27_implement_aether_conduit_lookup_api_task.md"
t = load(p)
t = metadata(t, p, "review", wrap("- Summary:", "Aether's eight root-only lookups renamed `*_root_*`; `get_conduit_by_name` "
             "answers named scopes and `get_conduit_by_id` any live conduit; one frame resolver; "
             "`ConduitCloud.list_conduits()`; callers, 17 test files, docs, graph, release note, 0.2.79 notch, build "
             "assets and LLM bundles; whole tree green on 3.14t, affected subsets on GIL.", indent="  "))
t = rep(t, "  owner acceptance.\n\n## Steps / Checklist", "  owner acceptance.\n- from_state: review\n- to_state: done\n"
        f"- transition_reason: Owner acceptance and turn-in (chat, {CLOSE}).\n\n## Steps / Checklist", p)
t = rep(t, "- [ ] Run Ticket Microcycle during execution:", "- [x] Run Ticket Microcycle during execution:", p)
t = rep(t, "- [ ] Document each meaningful finding immediately", "- [x] Document each meaningful finding immediately", p)
for box in ("No status transition without evidence-backed transition reason.",
            "No implementation/validation from `UNKNOWN` or `HYPOTHESIS`.",
            "No closure without acceptance confirmation and board-sync completion.",
            "No behaviour claim cited to a search hit; every range covers the logic that was read.",
            "No drive-by refactors outside the listed methods.",
            "Steps complete and checked off", "Deliverables produced and linked", "Documentation updated (if needed)",
            "Validation status recorded", "Unknown-first discipline followed", "Acceptance criteria reviewed with user and confirmed",
            "Board sync completed for successor routing or closure anchor update.", "Applicable anti-pattern checks are clear or escalated with evidence."):
    t = rep(t, f"- [ ] {box}", f"- [x] {box}", p)
t = rep(t, "- [ ] Notes quality maintained", "- [x] Notes quality maintained", p)
t = rep(t, "  - system_docs/patches/active/aether_conduit_lookup_api_2026_09_27/\n",
        "  - system_docs/patches/completed/aether_conduit_lookup_api_2026_09_27/ (archived at closure)\n", p)
t = rep(t, "the rebuilt assets and bundles and two release-note lines (12:22Z) are not committed yet.",
        "the rebuilt assets and bundles and two release-note lines (12:22Z) stay uncommitted.", p)
t = rep(t, "Open: owner acceptance.\nAfter acceptance: archive the patch lane to system_docs/patches/completed/, close this task, the eleven stories and\nthe epic, turn in the trace task, and sync the attention and artifact boards.\n",
        f"Accepted by the owner.\nClosed {CLOSE}: patch lane archived to system_docs/patches/completed/; this task, the eleven\n"
        "stories, the epic, the trace task and the 2026-08-07 disposal-methods task turned in; boards synced.\n", p)
note = (f"\n- DATETIME: {CLOSE}\n  TYPE: DECISION\n"
        "  CLAIM: Owner accepted the lane and turned in everything (chat: \"yeah accepted turn in everything call it all\n"
        "    and stay signed in but finish off your work\"). Closure set = every open melder_0 ticket: this task, the trace\n"
        "    task, the eleven stories, the epic, and tasks/2026-08-07_creations_disposal_all_methods_task.md (its file\n"
        "    passes today). Other agents' rows (melder_2, fable_0) are theirs and stay open. \"Stay signed in\": the\n"
        "    mailbox row stays active. The patch lane moves to system_docs/patches/completed/; artifacts are retained.\n"
        f"  EVIDENCE:\n  - {FINAL}\n  - {RECOUNT}\n"
        "  IMPACT: The lane closes with every EXIT_GATE item met; the uncommitted assets, bundles and release-note lines are\n"
        "    the owner's to commit.\n  NEXT: none (closed).\n  REREAD: HELPFUL\n  SCORE_0_TO_10: 8\n")
t = rep(t, "\n## Context / Handoff Summary\n", note + "\n## Context / Handoff Summary\n", p)
check_width(t, p)
out[p] = t

# ---------------------------------------------------------------- trace task
p = "tickets/tasks/2026-09-27_trace_get_conduit_by_name_named_lesser_lookup_task.md"
t = load(p)
t = metadata(t, p, "review", wrap("- Summary:", "Cause found and reproduced: Aether's name lookups read only the frame's "
             "root maps while named lessers live only in the ConduitCloud directory; the fix shipped under "
             "EPIC-2026-09-27-aether-conduit-lookup-api at 0.2.79.", indent="  "))
t = rep(t, "  recorded in Notes (2026-09-27T09:58:06Z).\n", "  recorded in Notes (2026-09-27T09:58:06Z).\n"
        "- from_state: review\n- to_state: done\n"
        f"- transition_reason: Owner turn-in (chat, {CLOSE}); the fix landed under the epic at 0.2.79.\n", p)
for box in ("Acceptance criteria reviewed with user and confirmed",
            "Board sync completed for successor routing or closure anchor update", "Validation status recorded",
            "Deliverables produced and linked"):
    t = rep(t, f"- [ ] {box}", f"- [x] {box}", p)
note = (f"\n- DATETIME: {CLOSE}\n  TYPE: FACT\n"
        "  CLAIM: Turned in by the owner with the epic. The cause recorded here was fixed at 0.2.79: Aether.get_conduit_by_name\n"
        "    now answers over the frame Cloud's named directory, so a live named lesser resolves by name.\n"
        "  EVIDENCE:\n  - src/melder/aether/aether.py:1956-2011\n"
        "  - tests/integration/melder/aether/test_aether_named_lesser_lookup.py:1-145\n"
        "  IMPACT: MF7 is resolved; this task closes.\n  NEXT: none (closed).\n  REREAD: HELPFUL\n  SCORE_0_TO_10: 7\n")
t = rep(t, "\n## Context / Handoff Summary\n", note + "\n## Context / Handoff Summary\n", p)
t = rep(t, "## Context / Handoff Summary\n", f"## Context / Handoff Summary\nClosed {CLOSE} by owner turn-in; the fix "
        "shipped under EPIC-2026-09-27-aether-conduit-lookup-api (0.2.79).\n", p)
check_width(t, p)
out[p] = t

# ---------------------------------------------------------------- 2026-08-07 disposal-methods task
p = "tickets/tasks/2026-08-07_creations_disposal_all_methods_task.md"
t = load(p)
t = metadata(t, p, "in_progress", wrap("- Summary:", "The disposal-methods regression file (all declared methods invoked "
             "in order, `many` lane, pinned stop-at-first-failure posture) passes on 3.14t (GIL 0 and 1) and the GIL "
             "build, agent-run; per-method error aggregation stays an open owner decision, not taken at turn-in.",
             indent="  "))
t = rep(t, "  source fix already applied upstream, so the test is the remaining deliverable.\n",
        "  source fix already applied upstream, so the test is the remaining deliverable.\n"
        "- from_state: in_progress\n- to_state: done\n"
        f"- transition_reason: Owner turn-in of every melder_0 ticket (chat, {CLOSE}); the file is green today.\n", p)
t = rep(t, "- [ ] Owner runs the file on 3.14t\n", "- [x] Owner runs the file on 3.14t (agent-run instead on 2026-09-27; "
        "owner turned the task in)\n", p)
t = rep(t, "- [ ] Record the result in `## Notes`", "- [x] Record the result in `## Notes`", p)
t = rep(t, "- [ ] Ask owner to confirm acceptance criteria before closure",
        "- [x] Ask owner to confirm acceptance criteria before closure", p)
t = rep(t, "## Validation\n- Not run.\n", "## Validation\n- Run 2026-09-27 (agent, VM worktree byte-equal to the device "
        "file): 4 passed on 3.14.7t\n  PYTHON_GIL=0 and =1 and on the 3.14.7 GIL build; also inside the whole-tree run.\n", p)
for box in ("No closure without acceptance confirmation and board-sync completion.", "Validation status recorded",
            "Applicable anti-pattern checks are clear or escalated with evidence",
            "Acceptance criteria reviewed with user and confirmed",
            "Board sync completed for successor routing or closure anchor update"):
    t = rep(t, f"- [ ] {box}", f"- [x] {box}", p)
note = (f"\n- DATETIME: {CLOSE}\n  TYPE: MEASURE\n"
        "  CLAIM: The regression file runs green today: 4 passed on 3.14.7t PYTHON_GIL=0 and =1 and on the 3.14.7 GIL\n"
        "    build (VM worktree copy, byte-equal to the device file), and it sits inside today's whole-tree run. The\n"
        "    per-method error-aggregation question (DECISION note above) was not ruled; the owner turned the task in.\n"
        f"  EVIDENCE:\n  - tests/unit/melder/aether/conduit/creations/test_creations_disposal_all_methods_regression.py:1-211\n"
        f"  - {FINAL}\n"
        "  IMPACT: The exit gate's green run exists (agent-run); the task closes on the owner's turn-in.\n"
        "  NEXT: none (closed).\n  REREAD: HELPFUL\n  SCORE_0_TO_10: 7\n")
t = rep(t, "\n## Context / Handoff Summary\n", note + "\n## Context / Handoff Summary\n", p)
t = rep(t, "## Context / Handoff Summary\n", f"## Context / Handoff Summary\nClosed {CLOSE} by owner turn-in; the file "
        "is green on 3.14t and GIL (agent-run).\n", p)
check_width(t, p)
out[p] = t

# ---------------------------------------------------------------- epic
p = "tickets/epics/2026-09-27_aether_conduit_lookup_api_epic.md"
t = load(p)
t = metadata(t, p, "in_progress", wrap("- Summary:", "Delivered in one change set at 0.2.79 "
             "(TASK-2026-09-27-implement-aether-conduit-lookup-api): root-only lookups carry `*_root_*` names, Aether "
             "finds any named scope by name and any live conduit by id, ConduitCloud lists its named conduits; all "
             "eleven stories accepted; the survey recount shows no retired name on Aether.", indent="  "))
t = rep(t, "  investigate before we migrate\").\n", "  investigate before we migrate\").\n"
        "- from_state: in_progress\n- to_state: done\n"
        f"- transition_reason: Owner acceptance and turn-in (chat, {CLOSE}).\n", p)
for box in ("Milestone 3: Patch docs written and linked.", "Milestone 4: Stories implemented and accepted.",
            "Milestone 5: Docs, system docs, bundles, release note and version moved.",
            "Task: Usage survey across src, tests, docs, examples, system docs and generated bundles (this investigation).",
            "Task: Version step and release note after the change lands.",
            "Work walkthrough shared with user", "Acceptance criteria confirmed by user"):
    t = rep(t, f"- [ ] {box}", f"- [x] {box}", p)
t, n = re.subn(r"- \[ \] Story: STORY-2026-09-27-", "- [x] Story: STORY-2026-09-27-", t)
assert n == 11, n
t = rep(t, "- Frame-string enforcement scope (DECISION_REQUEST note); everything else decided 2026-09-27.\n",
        "- None open: the frame-string scope was decided 2026-09-27T10:41:49Z (shared resolver, TypeError).\n", p)
t = rep(t, "## Decision Log\n", f"## Decision Log\n- {CLOSE}: owner accepted the landed change and turned in the epic, "
        "its eleven stories and tasks (chat).\n", p)
note = (f"- DATETIME: {CLOSE}\n  TYPE: DECISION\n"
        "  CLAIM: Epic closed on owner acceptance. All eleven stories shipped in one change set at 0.2.79 under the\n"
        "    implementation task: survey -> owner API decision -> patch docs -> red regression test -> src and 17 test\n"
        "    files -> suites on 3.14t and GIL -> system docs, graph, release note, notch -> build assets and LLM bundles.\n"
        "    The recount shows only the approved NAMED/LIVE lookups on Aether under generic names. Open outside this epic:\n"
        "    whether spell ids should collide across frames (UNKNOWN, trace task note 09:51:28Z) - not investigated here.\n"
        f"  EVIDENCE:\n  - {TASK_DONE}\n  - {RECOUNT}\n  - {FINAL}\n"
        "  IMPACT: MF7 is resolved and the lookup surface states its coverage.\n  NEXT: none (closed).\n"
        "  REREAD: HELPFUL\n  SCORE_0_TO_10: 8\n")
t = rep(t, "\n## Closure Confirmation\n", note + "\n## Closure Confirmation\n", p)
t = rep(t, "## Context / Handoff Summary\n", f"## Context / Handoff Summary\nClosed {CLOSE} on owner acceptance: "
        "delivered at 0.2.79 (see Summary);\npatch lane archived; artifacts retained.\n", p)
check_width(t, p)
out[p] = t

for path, text in out.items():
    pathlib.Path(path).write_bytes(text.encode("utf-8"))
print(f"wrote {len(out)} tickets at {CLOSE}")
