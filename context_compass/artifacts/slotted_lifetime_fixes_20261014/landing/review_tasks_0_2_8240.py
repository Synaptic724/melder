"""
Move the lane's D1-D5 tasks to review and record the end-of-pass state (EPIC-2026-10-14-slotted_lifetime_ownership_fixes):
Status and Updated, a State Transition Event, answered Open Questions, one Note each and a current handoff summary; D6
(already in review) gets its alignment note and summary. Notes are appended, never rewritten. Run from the
repository root: python review_tasks_0_2_8240.py <UTC timestamp>
"""
import pathlib
import re
import sys

NOW = sys.argv[1]
TASKS = pathlib.Path("context_compass/tickets/tasks")
RUNS = "context_compass/artifacts/slotted_lifetime_fixes_20261014/runs"
ARCH = "context_compass/system_docs/src_architecture.md"
COMP = "context_compass/system_docs/src_components.md"
TESTS = "context_compass/system_docs/tests_components.md"
COMMON_EVIDENCE = [
    f"{RUNS}/full_tree_0_2_8240_gil0.txt:1-28",
    f"{RUNS}/full_tree_0_2_8240_gil1.txt:1-20",
]


def note(kind: str, claim: str, evidence: list, impact: str, nxt: str, score: int) -> str:
    lines = [f"- DATETIME: {NOW}", "  AUTHOR: melder_1", "  AUTHOR_ROLE: synaptic_python_developer", f"  TYPE: {kind}"]
    lines += wrap("  CLAIM: ", claim)
    lines.append("  EVIDENCE:")
    lines += [f"  - {item}" for item in evidence]
    lines += wrap("  IMPACT: ", impact)
    lines += wrap("  NEXT: ", nxt)
    lines += ["  REREAD: REQUIRED", f"  SCORE_0_TO_10: {score}", ""]
    return "\n".join(lines) + "\n"


def wrap(head: str, text: str) -> list:
    out, line = [], head
    for word in text.split():
        if len(line) + 1 + len(word) > 118 and line.strip():
            out.append(line)
            line = "    " + word
        else:
            line = line + word if line.endswith(" ") or line == head else line + " " + word
    out.append(line)
    return out


def update(name: str, *, to_review: bool, reason: str, open_questions: str, handoff: str, the_note: str,
           extra: list = ()) -> None:
    path = TASKS / name
    text = path.read_bytes().decode("utf-8")
    assert "\r\n" not in text, name
    if to_review:
        assert text.count("\n- Status: in_progress\n") == 1, name
        text = text.replace("\n- Status: in_progress\n", "\n- Status: review\n")
        anchor = "\n\n\n## Steps / Checklist"
        assert text.count(anchor) == 1, (name, "steps anchor")
        event = "\n- from_state: in_progress\n- to_state: review\n" + "\n".join(wrap("- transition_reason: ", reason))
        text = text.replace(anchor, event + anchor)
    text, n = re.subn(r"\n- Updated: \S+\n", f"\n- Updated: {NOW}\n", text, count=1)
    assert n == 1, (name, "updated")
    text, n = re.subn(r"(## Open Questions\n).*?(\n## Artifact Links)", lambda m: m.group(1) + open_questions + m.group(2),
                      text, count=1, flags=re.S)
    assert n == 1, (name, "open questions")
    for old, new in extra:
        assert text.count(old) == 1, (name, old[:60])
        text = text.replace(old, new)
    anchor = "## Context / Handoff Summary\n"
    assert text.count(anchor) == 1, (name, "handoff anchor")
    text = text.replace(anchor, the_note + anchor)
    text, n = re.subn(r"(## Context / Handoff Summary\n).*?(\n## Project-Specific Additions)",
                      lambda m: m.group(1) + handoff + m.group(2), text, count=1, flags=re.S)
    assert n == 1, (name, "handoff")
    text.encode("ascii")
    path.write_bytes(text.encode("utf-8"))
    print("updated", name)


def para(text: str) -> str:
    return "\n".join(wrap("", text)) + "\n"


REVIEW_REASON = ("the fix landed with its red tests green GIL off and on; the lane's full tree is green GIL off and on "
                 "at 0.2.8240 and the change is promoted into the system docs (epic Notes 2026-10-14T23:39:45Z and "
                 "2026-10-15T00:00:12Z); the owner accepts.")

update(
    "2026-10-14_investigate_cluster_member_teardown_without_leave_task.md",
    to_review=True, reason=REVIEW_REASON,
    open_questions=("- Answered (owner, 2026-10-14: \"a torn down root shouldn't live in a cluster\"): a root's teardown\n"
                    "  leaves its cluster, and a leader's teardown leaves it inert and electable (0.2.8236).\n"
                    "- Answered by D2 (0.2.8237): the cluster's instances live in its team store and survive leader changes.\n"),
    handoff=para("In review (2026-10-15). Landed as 0.2.8236: root teardown leaves its cluster first "
                 "(`Conduit._leave_cluster_for_teardown`: `ConduitCluster.release_member` while the frame lives, "
                 "`drop_member` in frame teardown or after a failed exit), the cloud's leave runs the ordered exit and "
                 "unshares the leaver's roots, and the cloud's cluster lookup reads the DevOps index and names clusters "
                 "through `_cluster_names_by_id`. Red tests green GIL off and on; the lane's full tree green at 0.2.8240 "
                 "GIL off and on; promoted into src_architecture, src_components and tests_components. Remaining: the "
                 "owner's acceptance; commit and push are the owner's."),
    the_note=note("FACT",
                  "Status to review. D1 (0.2.8236) holds at the end of the lane's pass: the audit probe's c1 and c3 "
                  "show a torn-down member or leader no longer recorded in its cluster (unelect and elect work, the "
                  "member's meld serves the same leaf), the full tree is green GIL off and on at 0.2.8240, and the "
                  "system docs carry the cluster-exit invariant, its failure mode and the ConduitCluster and "
                  "ConduitCloud rules.",
                  [f"{RUNS}/probe_lifetime_owners_all_0_2_8240_gil0.txt:1-22", *COMMON_EVIDENCE,
                   f"{ARCH}:1000-1014", f"{ARCH}:1785-1790", f"{COMP}:6191-6243", f"{TESTS}:1407-1415"],
                  "The task waits only for the owner's acceptance; closure goes with the epic.",
                  "The owner accepts or redirects; then close with the epic.", 8),
)

update(
    "2026-10-14_investigate_cluster_instance_not_rehomed_on_leader_change_task.md",
    to_review=True, reason=REVIEW_REASON,
    open_questions=("- Answered by the owner's directive to fix all of the audit's findings (2026-10-14) and landed as\n"
                    "  0.2.8237: the instance survives a leader change in a store the cluster owns and is disposed by the\n"
                    "  cluster's cleanup.\n"
                    "- Yes: `resolved_store()` still raises while no leader is elected, and the elected leader's id is the\n"
                    "  purge authority.\n"),
    handoff=para("In review (2026-10-15). Landed as 0.2.8237: the cluster owns a `Creations` team store; election "
                 "binds every member facade to it with the leader's id (the purge authority), and a root joining "
                 "while a leader is elected is bound too; unelection, a leader's leave or teardown keep it; the "
                 "cluster's cleanup disposes it once (`delete_cluster` raises failures after deleting, frame teardown "
                 "logs them). Red tests green GIL off and on; the lane's full tree green at 0.2.8240; promoted into "
                 "the system docs. Remaining: the owner's acceptance; commit and push are the owner's."),
    the_note=note("FACT",
                  "Status to review. D2 (0.2.8237) holds at the end of the lane's pass: the audit probe's c2 shows a "
                  "re-election serving the original instance (no second one) and the departed leader's teardown no "
                  "longer disposing it; r9 shows a cluster holder's child kept in the cluster's store; the full tree is "
                  "green GIL off and on at 0.2.8240; the system docs carry the team-store invariant, the failure mode, "
                  "the ConduitCluster rules and the Meld store selection.",
                  [f"{RUNS}/probe_lifetime_owners_all_0_2_8240_gil0.txt:10-18",
                   f"{RUNS}/probe_lifetime_owners_all_0_2_8240_gil0.txt:74-79", *COMMON_EVIDENCE,
                   f"{ARCH}:987-999", f"{ARCH}:1779-1784", f"{COMP}:6191-6220"],
                  "The task waits only for the owner's acceptance; closure goes with the epic.",
                  "The owner accepts or redirects; then close with the epic.", 8),
)

update(
    "2026-10-14_investigate_transfer_leaves_holder_children_behind_task.md",
    to_review=True, reason=REVIEW_REASON,
    open_questions=("- Answered (owner, 2026-10-14: \"moving the many is fine\"): a moved holder's adopted children move with\n"
                    "  it (0.2.8238); since 0.2.8239 the move is the transfer default unless the caller passes\n"
                    "  `move_creations=False`.\n"),
    handoff=para("In review (2026-10-15). Fixed as 0.2.8238 and accepted in substance by the owner (\"moving the many "
                 "is fine\"): a holder's extract row carries its adopted children and the restore rebuilds its record, "
                 "so a moved holder's `many` children move with it and a rollback brings them back; since 0.2.8239 the "
                 "move is the transfer default. Red tests green GIL off and on; the lane's full tree green at 0.2.8240; "
                 "promoted into the system docs. Remaining: closure with the epic; commit and push are the owner's."),
    the_note=note("FACT",
                  "Status to review. D4 (0.2.8238) holds at the end of the lane's pass: the audit probe's t4 and t4b "
                  "show the holder's child moved with it (in neither the source store nor a bucket of its own), the "
                  "source's teardown closing nothing and the child closed once with the holder at the target; the full "
                  "tree is green GIL off and on at 0.2.8240; the system docs carry the holder-record invariant and the "
                  "transfer contract.",
                  [f"{RUNS}/probe_lifetime_owners_all_0_2_8240_gil0.txt:30-47", *COMMON_EVIDENCE,
                   f"{ARCH}:974-986", f"{COMP}:6163-6190"],
                  "The task waits for closure with the epic.",
                  "Close with the epic once the owner accepts it.", 8),
)

update(
    "2026-10-14_investigate_purge_leaves_holder_children_registered_task.md",
    to_review=True, reason=REVIEW_REASON,
    open_questions=("- Landed as yes (0.2.8238): purging a holder disposes the `many` children recorded with it, after it.\n"
                    "  Offered to the owner (2026-10-14) to revert purge to leaving them registered; kept as landed\n"
                    "  unless he says otherwise.\n"),
    handoff=para("In review (2026-10-15). Fixed as 0.2.8238: a holder's disposal-bearing `many` children are recorded "
                 "in its `HolderDisposalEntry`, so purging the holder disposes it and then its children (failures "
                 "raised with its own) and nothing accumulates; a `many` purge or probe of the child spell counts only "
                 "children no holder adopted (in the release note). Red tests green GIL off and on; the lane's full "
                 "tree green at 0.2.8240; promoted into the system docs. Open: the owner may still ask for purge to "
                 "leave the children registered (offered 2026-10-14). Commit and push are the owner's."),
    the_note=note("FACT",
                  "Status to review. D5 (0.2.8238) holds at the end of the lane's pass: the audit probe's p5 shows five "
                  "purged holders and their five children closed and none left registered; the full tree is green GIL "
                  "off and on at 0.2.8240; the system docs carry the holder-record invariant, the purge failure mode "
                  "and the Creations Disposal Pipeline rule. The owner has not yet answered the offer to revert purge "
                  "to leaving the children registered; D5 stays as landed meanwhile.",
                  [f"{RUNS}/probe_lifetime_owners_all_0_2_8240_gil0.txt:48-51", *COMMON_EVIDENCE,
                   f"{ARCH}:974-986", f"{ARCH}:1775-1778", f"{COMP}:6634-6657"],
                  "The task waits for the owner's acceptance of purge disposing the children.",
                  "The owner accepts D5 as landed or asks for the revert.", 8),
)

update(
    "2026-10-14_investigate_upgrade_retained_holders_keep_old_dependencies_task.md",
    to_review=False, reason="",
    open_questions=("- Answered by the re-investigation and the owner's runtime model (2026-10-14): an upgrade keeps the\n"
                    "  retained creations for eventual disposal; a retained object referencing an instance the old lineage\n"
                    "  disposed is pending agent work, not a defect.\n"),
    handoff=para("In review. Re-investigated at the owner's request: not a defect. Graduation keeps retained objects "
                 "in their stores only for eventual disposal; old spell ids no longer resolve, so no meld serves a "
                 "retained holder again. The `upgrade_to_normal` docstring paragraph landed with 0.2.8236 (a retained "
                 "object may hold references to instances the former lineage owns, disposed on that owner's schedule). "
                 "By the owner's runtime model such an object is pending agent work. Next: the owner confirms; D6 "
                 "closes as no defect with the epic."),
    the_note=note("ALIGNMENT_CHECK",
                  "D6 aligned with the owner's runtime model (2026-10-14, promoted to src_architecture): the docstring "
                  "paragraph landed with 0.2.8236, and the audit probe's u6 at 0.2.8240 is unchanged by design (the old "
                  "root's teardown closes the lineage instance once; the retained holder is closed once, at the "
                  "upgraded conduit's teardown). The 'one owner's lifetime' rule in the Objective was my framing; the "
                  "owner's model makes a retained reference to a disposed dependency pending agent work, not a defect.",
                  ["src/melder/aether/conduit/conduit.py:2476-2510",
                   f"{RUNS}/probe_lifetime_owners_all_0_2_8240_gil0.txt:52-58", f"{ARCH}:522-548"],
                  "D6 closes as no defect when the owner confirms.",
                  "The owner confirms; close with the epic.", 8),
)

update(
    "2026-10-14_investigate_stored_instances_dropped_without_disposal_task.md",
    to_review=True, reason=("the transfer half landed as 0.2.8239 (default) and 0.2.8240 (handover docstring) with "
                            "regression tests green GIL off and on; the invalidation half was ruled out by the owner "
                            "(no change); the lane's full tree is green at 0.2.8240 and the change is promoted into the "
                            "system docs; the owner accepts."),
    open_questions=("- Answered (owner, 2026-10-14): the default transfer moves the source's instances\n"
                    "  (`move_creations=True`); a transfer disposes nothing.\n"
                    "- Answered (owner, 2026-10-14): contract invalidation stays as it is; the objects it lets go of stay\n"
                    "  pending for agents (Notes 23:00:25Z).\n"),
    extra=[
        ("- [ ] Invalidation half: the owner rules on what contract invalidation does with the consumers it retires (b7,\n"
         "      l1, l2); red tests and a fix only if he wants one.\n",
         "- [x] Invalidation half: ruled by the owner (Notes 23:00:25Z): left as it is - b7, l1 and l2 are intended\n"
         "      behaviour; no red tests, no fix.\n"),
        ("- Not run: the full tree, the audit probe's other cases and the benchmarks (end of the epic's pass).\n",
         "- End of the epic's pass (0.2.8240): the full tree green GIL off and on, the audit probe's eleven cases, the\n"
         "  emission diff and the warm-meld benchmarks (epic Notes 2026-10-14T23:39:45Z).\n"),
    ],
    handoff=para("In review (2026-10-15). D3 is the transfer default: `transfer_spell_ownership` defaults to "
                 "`move_creations=True` (0.2.8239), so a transferred `unique` stays one object and the source's "
                 "objects follow the spell; a transfer disposes nothing; `move_creations=False` and a move into a "
                 "filled slot (m1) are documented, not changed; the docstring, the ownership guide and the release "
                 "note say a transfer hands over stewardship, not a working setup (0.2.8240; probe h1 and h2). Contract "
                 "invalidation stays as it is by the owner's ruling (b7, l1, l2 intended). Validated with the epic's "
                 "pass; promoted into the system docs. Remaining: the owner's acceptance; commit and push are the "
                 "owner's."),
    the_note=note("FACT",
                  "Status to review. The audit probe at 0.2.8240 shows t3 moved by default (the holder in the target "
                  "store, the target melding the same holder, closed once at the end) and b7 as the owner ruled it (the "
                  "retired consumer is not disposed); the full tree is green GIL off and on; the system docs carry the "
                  "transfer invariant, the handover sequence step, the two transfer failure modes and the runtime "
                  "model that states the invalidation ruling.",
                  [f"{RUNS}/probe_lifetime_owners_all_0_2_8240_gil0.txt:23-29",
                   f"{RUNS}/probe_lifetime_owners_all_0_2_8240_gil0.txt:59-67", *COMMON_EVIDENCE,
                   f"{ARCH}:522-548", f"{ARCH}:826-842", f"{ARCH}:959-973", f"{ARCH}:1764-1774"],
                  "D3 waits only for the owner's acceptance; closure goes with the epic.",
                  "The owner accepts or redirects; then close with the epic.", 9),
)
