"""
Turn in the owner-accepted lanes (owner, chat 2026-10-15: "ok cool turn it all in if your done"):
EPIC-2026-10-14-slotted_lifetime_ownership_fixes with its six tasks, EPIC-2026-10-14-many_child_follows_holder with
TASK-2026-10-14-fix_many_child_follows_holder, and TASK-2026-10-14-fix_pool_decay_fake_clock_rounding. For each
ticket: Status done, a completion block, a State Transition Event, the closing checks ticked, one closing Note, the
handoff summary, then `mv -n` into its completed folder. The board syncs follow in turn_in_boards_0_2_8240.py.
Run from the repository root: python turn_in_0_2_8240.py <UTC timestamp>
"""
import pathlib
import re
import subprocess
import sys

NOW = sys.argv[1]
ROOT = pathlib.Path("context_compass/tickets")
OWNER_QUOTE = '(owner, chat 2026-10-15: "ok cool turn it all in if your done")'
RUNS = "context_compass/artifacts/slotted_lifetime_fixes_20261014/runs"


def wrap(head: str, text: str, indent: str = "    ") -> list:
    out, line = [], head
    for word in text.split():
        if len(line) + 1 + len(word) > 118 and line.strip():
            out.append(line)
            line = indent + word
        else:
            line = line + word if line.endswith(" ") or line == head else line + " " + word
    out.append(line)
    return out


def note(kind: str, claim: str, evidence: list, impact: str, nxt: str, score: int) -> str:
    lines = [f"- DATETIME: {NOW}", "  AUTHOR: melder_1", "  AUTHOR_ROLE: synaptic_python_developer", f"  TYPE: {kind}"]
    lines += wrap("  CLAIM: ", claim)
    lines.append("  EVIDENCE:")
    lines += [f"  - {item}" for item in evidence]
    lines += wrap("  IMPACT: ", impact)
    lines += wrap("  NEXT: ", nxt)
    lines += ["  REREAD: HELPFUL", f"  SCORE_0_TO_10: {score}", ""]
    return "\n".join(lines) + "\n"


def tick_section(text: str, heading: str, only: tuple = ()) -> str:
    match = re.search(r"(^" + re.escape(heading) + r"\n)(.*?)(?=^## )", text, flags=re.S | re.M)
    if match is None:
        return text
    body = match.group(2)
    if only:
        for start in only:
            body = body.replace("- [ ] " + start, "- [x] " + start)
    else:
        body = body.replace("- [ ] ", "- [x] ")
    return text[:match.start(2)] + body + text[match.end(2):]


def close(rel: str, *, from_state: str, reason: str, summary: str, the_note: str, handoff: str,
          extra: list = ()) -> str:
    path = ROOT / rel
    text = path.read_bytes().decode("utf-8")
    assert "\r\n" not in text, rel
    status_line = f"\n- Status: {from_state}\n"
    assert text.count(status_line) == 1, (rel, "status")
    text = text.replace(status_line, "\n- Status: done\n")
    text, n = re.subn(r"\n- Updated: \S+\n", f"\n- Updated: {NOW}\n", text, count=1)
    assert n == 1, (rel, "updated")
    meta = text.index("## Metadata\n")
    nxt = text.index("\n## ", meta + 1) + 1
    block = f"- Completed: {NOW}\n" + "\n".join(wrap("- Summary: ", summary, "  ")) + "\n\n"
    text = text[:nxt] + block + text[nxt:]
    sec = re.search(r"(^## State Transition Event\n)(.*?)(\n+)(?=^## )", text, flags=re.S | re.M)
    assert sec is not None, (rel, "transition")
    event = (f"\n- from_state: {from_state}\n- to_state: done\n" + "\n".join(wrap("- transition_reason: ", reason, "  ")))
    text = text[:sec.end(2)] + event + text[sec.end(2):]
    for old, new in extra:
        assert text.count(old) == 1, (rel, old[:60])
        text = text.replace(old, new)
    text = tick_section(text, "## Steps / Checklist", only=("Run Ticket Microcycle", "Document each meaningful finding"))
    for heading in ("## Applicable Anti-Patterns", "## Done Checklist", "## Closure Confirmation",
                    "## Stories (Required to Complete)"):
        text = tick_section(text, heading)
    anchor = "## Context / Handoff Summary\n"
    assert text.count(anchor) == 1, (rel, "handoff anchor")
    text = text.replace(anchor, the_note + anchor)
    text, n = re.subn(r"(## Context / Handoff Summary\n).*?(\n## Project-Specific Additions)",
                      lambda m: m.group(1) + "\n".join(wrap("", handoff, "")) + "\n" + m.group(2), text, count=1,
                      flags=re.S)
    assert n == 1, (rel, "handoff")
    text.encode("ascii")
    path.write_bytes(text.encode("utf-8"))
    kind_dir = path.parent / "completed"
    subprocess.run(["mv", "-n", str(path), str(kind_dir / path.name)], check=True)
    assert (kind_dir / path.name).exists() and not path.exists(), (rel, "move")
    print("closed", kind_dir / path.name)
    return str(kind_dir / path.name)


EPIC_SLOTTED = "epics/2026-10-14_slotted_lifetime_ownership_fixes_epic.md"
REASON = f"the owner accepted the lane and directed the turn-in {OWNER_QUOTE}."
COMMON = [f"{RUNS}/full_tree_0_2_8240_gil0.txt:1-33", f"{RUNS}/full_tree_0_2_8240_gil1.txt:1-25",
          f"{RUNS}/rebuild_0_2_8240.txt:1-40"]

D_TASKS = [
    ("tasks/2026-10-14_investigate_cluster_member_teardown_without_leave_task.md", "D1",
     "notched 0.2.8236 (release note: \"A root that is torn down leaves its cluster, and leaving a cluster unshares its "
     "roots\"): a root's teardown leaves its cluster through the ordered exit, the cloud's leave unshares the leaver's "
     "roots and the cluster lookup reads the DevOps index."),
    ("tasks/2026-10-14_investigate_cluster_instance_not_rehomed_on_leader_change_task.md", "D2",
     "notched 0.2.8237 (release note: \"A cluster's shared object belongs to the cluster, not to its leader\"): the "
     "cluster owns its team store, so its object survives leader changes and is disposed once by the cluster's "
     "cleanup."),
    ("tasks/2026-10-14_investigate_stored_instances_dropped_without_disposal_task.md", "D3",
     "notched 0.2.8239 and 0.2.8240 (release note: \"An ownership transfer brings the spell's objects with it by "
     "default\"): `transfer_spell_ownership` defaults to `move_creations=True` and says a transfer hands over "
     "stewardship, not a working setup; contract invalidation unchanged by the owner's ruling."),
    ("tasks/2026-10-14_investigate_transfer_leaves_holder_children_behind_task.md", "D4",
     "notched 0.2.8238 (release note: \"A `many` dependency is disposed with the object that holds it\"): a moved "
     "holder's `many` children move with it in its record."),
    ("tasks/2026-10-14_investigate_purge_leaves_holder_children_registered_task.md", "D5",
     "notched 0.2.8238 (release note: \"A `many` dependency is disposed with the object that holds it\"): purging a "
     "holder disposes the `many` children recorded with it; kept as landed with the owner's acceptance."),
]

closed = []
for rel, tag, what in D_TASKS:
    closed.append(close(
        rel, from_state="review", reason=REASON,
        summary=f"{tag} of EPIC-2026-10-14-slotted_lifetime_ownership_fixes, {what} Turned in by owner directive.",
        the_note=note("DECISION",
                      f"Turned in. The owner accepted the lane and directed the turn-in {OWNER_QUOTE}; {tag} is "
                      f"{what} Status done, completion summary written, ticket moved to tasks/completed; the board "
                      "syncs run with the epic's closure.",
                      COMMON, "Closed; nothing of this task stays open.", "None.", 8),
        handoff=f"Done ({NOW}). {tag}: {what} Turned in by owner directive with EPIC-2026-10-14-slotted_lifetime_"
                "ownership_fixes; commit and push are the owner's.",
    ))

closed.append(close(
    "tasks/2026-10-14_investigate_upgrade_retained_holders_keep_old_dependencies_task.md", from_state="review",
    reason=REASON,
    summary="D6 of EPIC-2026-10-14-slotted_lifetime_ownership_fixes: no defect. Graduation keeps retained objects for "
            "eventual disposal; the `upgrade_to_normal` docstring paragraph landed with 0.2.8236; a retained object "
            "referencing a disposed dependency is pending agent work under the owner's runtime model. No notch of its "
            "own. Turned in by owner directive.",
    the_note=note("DECISION",
                  f"Turned in as no defect. The owner accepted the lane and directed the turn-in {OWNER_QUOTE}. The "
                  "red-test and options steps were superseded by the verdict (no defect); the docstring paragraph "
                  "landed with 0.2.8236.",
                  ["src/melder/aether/conduit/conduit.py:2476-2510", *COMMON],
                  "Closed; nothing of this task stays open.", "None.", 8),
    handoff=f"Done ({NOW}). Re-investigated at the owner's request: not a defect; the `upgrade_to_normal` docstring "
            "paragraph landed with 0.2.8236. Turned in by owner directive with the epic.",
    extra=[
        ("- [ ] Read `upgrade_to_normal`, `_conjure_existing_conduit` and the lineage repointing; record which retained\n",
         "- [x] Read `upgrade_to_normal`, `_conjure_existing_conduit` and the lineage repointing; record which retained\n"),
        ("- [ ] Write a red test from the probe's u6, and one for a `unique` dependency of the old root.\n",
         "- [x] Superseded by the verdict (no defect): no red test; existing tests pin both halves of the graduation\n"
         "      contract.\n"),
        ("- [ ] Lay out options (dispose retained holders at upgrade; carry their dependencies; refuse an upgrade that\n",
         "- [x] Superseded by the verdict (no defect): options not needed. Lay out options (dispose retained holders at\n"
         "      upgrade; carry their dependencies; refuse an upgrade that\n"),
    ],
))

closed.append(close(
    EPIC_SLOTTED, from_state="review", reason=REASON,
    summary="Six lifetime defect groups resolved as structure fixes, notched 0.2.8236-0.2.8240: a root's teardown "
            "leaves its cluster, the cluster owns its team store, a holder's `many` children are recorded with it "
            "(purge, move, disposal), a transfer moves by default and disposes nothing, and the transfer docs say it "
            "hands over stewardship, not a working setup; D6 no defect; contract invalidation unchanged by ruling. "
            "Release-note sections on the cluster exit, the cluster store, the many dependency and the transfer "
            "default; the owner's runtime model is in src_architecture. Turned in by owner directive.",
    the_note=note("DECISION",
                  f"Turned in. The owner accepted the lane and directed the turn-in {OWNER_QUOTE}; D5 stays as landed. "
                  "At his word the 13 stray .pyc files of 0.2.8239 (src/**/__pycache__, my unprefixed import) and the "
                  "stale landing/__pycache__ were deleted; the other __pycache__ folders belong to the owner's own "
                  "runs and were left. Status done, completion summary, six tasks and this epic moved to completed; "
                  "attention and artifact boards synced (turn_in_boards_0_2_8240.py).",
                  [f"{RUNS}/pyc_written_by_import_0_2_8239.txt:1-13", *COMMON,
                   "release_docs/next_version_release.md:202-307"],
                  "The lane is closed; commit and push are the owner's.",
                  "None in this lane; EPIC-2026-10-14-managed_spell_quantity waits on the owner's answers.", 9),
    handoff=f"Done ({NOW}). D1-D5 landed as structure fixes (0.2.8236-0.2.8240), D6 no defect, contract invalidation "
            "unchanged by the owner's ruling, and the owner's runtime model recorded in src_architecture. Full tree "
            "green GIL off and on, docs, graph, release note and the rebuild current. Turned in by owner directive; "
            "commit and push are the owner's.",
    extra=[
        ("- [ ] Milestone 4: D6 per its verdict; full tree, docs, graph, release note, notches, rebuild; owner acceptance.\n",
         "- [x] Milestone 4: D6 per its verdict; full tree, docs, graph, release note, notches, rebuild; owner acceptance.\n"),
        ("- [ ] D1 TASK", "- [x] D1 TASK"), ("- [ ] D2 TASK", "- [x] D2 TASK"), ("- [ ] D3 TASK", "- [x] D3 TASK"),
        ("- [ ] D4 TASK", "- [x] D4 TASK"), ("- [ ] D5 TASK", "- [x] D5 TASK"), ("- [ ] D6 TASK", "- [x] D6 TASK"),
    ],
))

MANY_RUNS = "context_compass/artifacts/many_child_registration_20261014/runs"
closed.append(close(
    "tasks/2026-10-14_fix_many_child_follows_holder_task.md", from_state="review", reason=REASON,
    summary="Notched 0.2.8235 (release note: \"A `many` dependency is disposed with the object that holds it\"): a "
            "slotted holder's disposal-bearing `many` children register in the holder's store, and the opt-in "
            "singleton specializer declines graphs that feed a `many` step into a non-`many` step. Purge and transfer "
            "of the children followed in 0.2.8238. Turned in by owner directive.",
    the_note=note("DECISION",
                  f"Turned in. The owner directed the turn-in of the finished work {OWNER_QUOTE}; 0.2.8235 stands and "
                  "the epic's open questions (purge, transfer) were resolved by "
                  "EPIC-2026-10-14-slotted_lifetime_ownership_fixes (0.2.8238). Left open, unticketed, for the owner: "
                  "the experimentation harness's S4 prologue rewrite no longer matches a miss "
                  "(tests/experimentation/codegen_strategy_certification.py).",
                  [f"{MANY_RUNS}/full_tree_summary_gil0.txt:1-32", f"{MANY_RUNS}/full_tree_summary_gil1.txt:1-23"],
                  "Closed; the follow-ups are recorded in the epic's closure.", "None.", 8),
    handoff=f"Done ({NOW}). Landed as 0.2.8235; children of a slotted holder register with its owner. Turned in by "
            "owner directive with EPIC-2026-10-14-many_child_follows_holder; commit and push are the owner's.",
))

closed.append(close(
    "epics/2026-10-14_many_child_follows_holder_epic.md", from_state="in_progress",
    reason=f"its fix task landed as 0.2.8235 and its open questions were resolved by "
           f"EPIC-2026-10-14-slotted_lifetime_ownership_fixes (0.2.8238); the owner directed the turn-in "
           f"{OWNER_QUOTE}.",
    summary="A slotted holder's `many` children belong to its owner: notched 0.2.8235 (registration with the holder's "
            "owner, the specializer guard); purge and transfer of the children landed in 0.2.8238 under "
            "EPIC-2026-10-14-slotted_lifetime_ownership_fixes. Left open, unticketed: the experimentation harness's "
            "S4 prologue rewrite. Turned in by owner directive.",
    the_note=note("DECISION",
                  f"Turned in. The owner directed the turn-in {OWNER_QUOTE}. Questions 1 and 2 (purge, transfer) were "
                  "answered by D5 and D4 of the slotted lane (0.2.8238); the flaky 0.2.8234 clock test was fixed by "
                  "TASK-2026-10-14-fix_pool_decay_fake_clock_rounding; the experimentation harness's S4 prologue "
                  "rewrite stays the owner's call, unticketed. EPIC-2026-10-14-managed_spell_quantity's F10 "
                  "prerequisite is met.",
                  [f"{MANY_RUNS}/full_tree_summary_gil0.txt:1-32", f"{RUNS}/probe_lifetime_owners_all_0_2_8240_gil0.txt:30-51"],
                  "Closed.", "None.", 8),
    handoff=f"Done ({NOW}). Landed as 0.2.8235 with its purge and transfer follow-ups in 0.2.8238 (slotted lane). "
            "Turned in by owner directive; commit and push are the owner's.",
    extra=[
        ("- [ ] Milestone 3: Owner acceptance.\n", "- [x] Milestone 3: Owner acceptance.\n"),
        ("- [ ] Task: TASK-2026-10-14-fix_many_child_follows_holder - implement the owner's rule and land it (landed\n"
         "      0.2.8235; in review).\n",
         "- [x] Task: TASK-2026-10-14-fix_many_child_follows_holder - implement the owner's rule and land it (landed\n"
         "      0.2.8235; done 2026-10-15).\n"),
    ],
))

POOL_RUNS = "context_compass/artifacts/pool_decay_clock_rounding_20261014/runs"
closed.append(close(
    "tasks/2026-10-14_fix_pool_decay_fake_clock_rounding_task.md", from_state="review", reason=REASON,
    summary="Test-only fix (no notch, no release note): the quiet-pool decay test's fake clock starts on a whole "
            "second, so its advances and deadlines are exact (0 failing origins of 100,000). Turned in by owner "
            "directive.",
    the_note=note("DECISION",
                  f"Turned in. The owner directed the turn-in of the finished work {OWNER_QUOTE}; the fix is "
                  "test-only and the pool suites pass GIL off and on.",
                  [f"{POOL_RUNS}/probe_decay_boundary_gil0.txt:1-4", f"{POOL_RUNS}/pool_suites_after_fix.txt:1-8"],
                  "Closed.", "None.", 8),
    handoff=f"Done ({NOW}). The quiet-pool decay test's clock starts on a whole second (test-only, no notch). Turned "
            "in by owner directive; the commit is the owner's.",
))
print("\n".join(closed))
