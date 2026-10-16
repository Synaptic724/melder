"""Close EPIC-2026-10-14-managed_spell_quantity with S7 and S8 on the owner's acceptance (chat, 2026-10-16).

Run from context_compass/:
    python <this file> boards <NOW>    - attention board (row, detail, 3 anchors, 12 kept), artifact board (3 rows)
    python <this file> tickets <NOW>   - completion summaries, state, checklists, decision logs, resume views, notes
    then mv -n each ticket into its completed folder.
Exact replacements, each asserted; LF files; a file is written only when all its replacements hold.
"""
import pathlib
import sys
import textwrap

STEP, NOW = sys.argv[1], sys.argv[2]
QUOTE = '"I accept your managed spell stuff and continue onto the next stuff please"'
EPIC = "tickets/epics/2026-10-14_managed_spell_quantity_epic.md"
S7 = "tickets/stories/2026-10-15_managed_docs_release_story.md"
S8 = "tickets/stories/2026-10-16_parked_versions_wired_at_conjure_story.md"


def done_path(path: str) -> str:
    """Return the completed-folder path of an active ticket path."""
    folder, name = path.rsplit("/", 1)
    return f"{folder}/completed/{name}"


def write_lf(path: pathlib.Path, text: str) -> None:
    """Write text as UTF-8 bytes with LF line endings."""
    path.write_bytes(text.encode("utf-8"))


def boards() -> None:
    """Remove the review row and its detail, add three anchors, move the epic's three artifact rows to cleared."""
    board = pathlib.Path("attention_board.md")
    text = board.read_bytes().decode("utf-8")
    assert "\r\n" not in text
    lines = text.split("\n")
    row = [i for i, line in enumerate(lines) if line.startswith("| melder_object_pools | ")]
    assert len(row) == 1
    del lines[row[0]]
    detail_start = lines.index("- WORK_ITEM: melder_object_pools")
    assert lines[detail_start + 1].startswith("  SWITCH_TRIGGER: ")
    assert lines[detail_start + 2] == "  RESUME_HIERARCHY:"
    assert lines[detail_start + 3] == f"    - {EPIC}" and lines[detail_start + 4] == f"    - {S8}"
    del lines[detail_start:detail_start + 5]
    begin = lines.index("<!-- BEGIN USER-DEFINED: closed_anchors -->")
    end = lines.index("<!-- END USER-DEFINED: closed_anchors -->")
    anchors = lines[begin + 1:end]
    assert len(anchors) == 12, len(anchors)
    new_anchors = [
        f"| managed_docs_release | done | melder_0 | {done_path(S7)} | Documentation, no notch (S7 of "
        "EPIC-2026-10-14-managed_spell_quantity: system docs, graph, README, release note, benchmarks); owner "
        f"accepted. Next: none. | {NOW} |",
        f"| parked_versions_wired_at_conjure | done | melder_0 | {done_path(S8)} | Landed 0.2.8248 (S8: conjure wires "
        "the versions staged before it; cache generation 21); owner accepted. Next: none. | " + NOW + " |",
        f"| managed_spell_quantity | done | melder_0 | {done_path(EPIC)} | Epic accepted by the owner (S1-S8, "
        "0.2.8241-0.2.8248). Next: TASK-2026-10-16-public_notch_target_for_staged_versions. | " + NOW + " |",
    ]
    kept = anchors[3:] + new_anchors
    lines[begin + 1:end] = kept
    write_lf(board, "\n".join(lines))
    print("attention board: row and detail removed; anchors", len(kept), "(dropped the 3 oldest)")

    art = pathlib.Path("artifact_board.md")
    text = art.read_bytes().decode("utf-8")
    assert "\r\n" not in text
    lines = text.split("\n")
    folders = {
        "artifacts/melder_object_pools_20261011/": "Epic closed; the folder stays rowed under "
        "EPIC-2026-10-05-melder_services_and_pools as its evidence.",
        "artifacts/managed_shell_spike_20261014/": "The design spike behind the settled shape (probe_deque_holder.py) "
        "with its probes and logs; kept as the epic's design evidence.",
        "artifacts/managed_spell_quantity_20261015/": "Evidence of the 0.2.8241-0.2.8248 landings: the epic's text "
        "before the rewrite, probes, red/green and whole-tree runs, emission diffs, benchmarks, and the apply, docs, "
        "graph, release-note, rebuild and closure scripts.",
    }
    removed = []
    for folder in folders:
        hits = [i for i, line in enumerate(lines) if line.startswith(f"| {EPIC} | {folder} |")]
        assert len(hits) == 1, (folder, len(hits))
        removed.append(hits[0])
    begin_active = lines.index("<!-- BEGIN USER-DEFINED: active_artifacts -->")
    end_active = lines.index("<!-- END USER-DEFINED: active_artifacts -->")
    assert all(begin_active < i < end_active for i in removed)
    lines = [line for i, line in enumerate(lines) if i not in set(removed)]
    begin_cleared = lines.index("<!-- BEGIN USER-DEFINED: cleared_artifacts -->")
    cleared = [f"| {done_path(EPIC)} | {folder} | retain_as_reference | {reason} | {NOW} |"
               for folder, reason in folders.items()]
    lines[begin_cleared + 1:begin_cleared + 1] = cleared
    write_lf(art, "\n".join(lines))
    print("artifact board: 3 active rows moved to cleared")


def edit(path: str, pairs: list) -> None:
    """Apply exact replacements (each once) to one ticket; write once."""
    p = pathlib.Path(path)
    text = p.read_bytes().decode("utf-8")
    assert "\r\n" not in text, path
    for old, new in pairs:
        if callable(old):
            old = old(text)
        assert text.count(old) == 1, (path, old[:90], text.count(old))
        text = text.replace(old, new)
    write_lf(p, text)
    print("edited", path)


def state_block(text: str, when: str, reason: str) -> tuple:
    """Return (old, new) for the State Transition Event head: the current transition becomes a prior line."""
    start = text.index("## State Transition Event\n")
    first_prior = text.index("\n- prior:", start) + 1
    old = text[start:first_prior]
    head = old.split("\n")
    assert head[1].startswith("- from_state: ") and head[2].startswith("- to_state: ")
    old_from, old_to = head[1][len("- from_state: "):], head[2][len("- to_state: "):]
    old_reason = " ".join(line.strip() for line in head[3:] if line.strip())
    assert old_reason.startswith("- transition_reason: ")
    old_reason = old_reason[len("- transition_reason: "):]
    prior = textwrap.fill(f"- prior: {old_from} -> {old_to} ({when}): {old_reason}", width=118,
                          subsequent_indent="  ", break_on_hyphens=False, break_long_words=False)
    new_reason = textwrap.fill(f"- transition_reason: {reason}", width=118, subsequent_indent="  ",
                               break_on_hyphens=False, break_long_words=False)
    new = f"## State Transition Event\n- from_state: {old_to}\n- to_state: done\n{new_reason}\n{prior}\n"
    return old, new


def section(text: str, heading: str, next_heading: str) -> str:
    """Return the text from a heading line up to the next heading line."""
    start = text.index(heading + "\n")
    end = text.index("\n" + next_heading + "\n", start) + 1
    return text[start:end]


def completion(text: str, summary: str) -> tuple:
    """Return (old, new) inserting the completion lines between the title and Metadata."""
    old = "\n\n## Metadata\n"
    body = textwrap.fill(f"- Summary: {summary}", width=118, subsequent_indent="  ", break_on_hyphens=False,
                         break_long_words=False)
    return old, f"\n\n- Completed: {NOW}\n{body}\n\n## Metadata\n"


def note(kind: str, claim: str, evidence: list, impact: str, nxt: str) -> str:
    """Render one structured note."""
    wrap = lambda label, value: textwrap.fill(f"  {label}: {value}", width=118, subsequent_indent="    ",
                                              break_on_hyphens=False, break_long_words=False)
    lines = [f"- DATETIME: {NOW}", "  AUTHOR: melder_0", "  AUTHOR_ROLE: synaptic_python_developer", f"  TYPE: {kind}",
             wrap("CLAIM", claim), "  EVIDENCE:"] + [f"  - {e}" for e in evidence] + [
        wrap("IMPACT", impact), wrap("NEXT", nxt), "  REREAD: HELPFUL", "  SCORE_0_TO_10: 8", ""]
    return "\n".join(lines)


def tickets() -> None:
    """Close the three tickets in place (the moves follow)."""
    board = pathlib.Path("attention_board.md").read_text(encoding="utf-8").split("\n")
    anchors = [i + 1 for i, line in enumerate(board) if line.startswith(("| managed_docs_release | done",
                                                                        "| parked_versions_wired_at_conjure | done",
                                                                        "| managed_spell_quantity | done"))]
    art = pathlib.Path("artifact_board.md").read_text(encoding="utf-8").split("\n")
    cleared = [i + 1 for i, line in enumerate(art) if line.startswith(f"| {done_path(EPIC)} | artifacts/")]
    assert len(anchors) == 3 and len(cleared) == 3
    ev_board = f"context_compass/attention_board.md:{min(anchors)}-{max(anchors)}"
    ev_art = f"context_compass/artifact_board.md:{min(cleared)}-{max(cleared)}"
    accepted = f"the owner accepted the epic and its stories (chat, 2026-10-16: {QUOTE})"

    s7 = pathlib.Path(S7).read_text(encoding="utf-8")
    edit(S7, [
        completion(s7, "documentation, no notch - benchmarks (no regression on the existing meld shapes; a managed "
                       "warm cycle 306-385 ns), src_architecture, src_components and the tests docs with their indexes, "
                       "the graph, the README, docs site and glossary, the release note's managed section and "
                       "packaging lines, the patch lane archived, rubric scores (83, 83, 83, 77) and the rebuild with "
                       "both checks OK. Accepted by the owner with the epic (2026-10-16)."),
        ("- Status: blocked\n", "- Status: done\n"),
        (lambda t: next(l for l in t.split("\n") if l.startswith("- Updated: ")) + "\n", f"- Updated: {NOW}\n"),
        state_block(s7, "2026-10-15T23:43:36Z", accepted + "; every EXIT_GATE item is recorded in the Notes."),
        ("- [ ] Archive the patch docs (done); rebuild assets and bundles last (done, both checks OK); close the epic (the\n"
         "  owner's acceptance).\n",
         "- [x] Archive the patch docs (done); rebuild assets and bundles last (done, both checks OK); close the epic (the\n"
         "  owner accepted, 2026-10-16).\n"),
        ("## Decision Log\n- None yet.\n",
         f"## Decision Log\n- 2026-10-16 (owner, chat with melder_0): {QUOTE} - S7 accepted with the epic.\n"),
        ("- [ ] Criteria, required tests/reviews and delegated acceptance or reserved-owner disposition recorded\n"
         "- [ ] Applicable anti-pattern checks are clear or escalated with evidence.\n",
         "- [x] Criteria, required tests/reviews and delegated acceptance or reserved-owner disposition recorded\n"
         "- [x] Applicable anti-pattern checks are clear or escalated with evidence.\n"),
        (lambda t: section(t, "## Context / Handoff Summary", "## Project-Specific Additions"),
         "## Context / Handoff Summary\n- Scope: S7 - benchmarks, docs, graph, README, release note, patch promotion, "
         "rebuild; no `src/` change, no notch.\n- State: done - accepted by the owner with the epic (2026-10-16); the "
         "evidence is in the Notes above.\n- Next: none.\n- Limits: hosted CI and coverage are the owner's (Not run).\n\n"),
        ("\n## Closure Confirmation\n",
         "\n" + note("DECISION", "S7 closes: " + accepted + ". Reserved-owner disposition: accepted. The story moves "
                     "to completed/ with S8 and the epic; the board row is replaced by closed anchors.",
                     [ev_board], "The documentation lane is done; nothing remains open in it.", "none.")
         + "\n## Closure Confirmation\n"),
    ])

    s8 = pathlib.Path(S8).read_text(encoding="utf-8")
    edit(S8, [
        completion(s8, "landed 0.2.8248 - conjure stamps every version staged with `bind_inactive` before it, so the "
                       "version melds after a notch for every existence; creation cache generation 21; the "
                       "missing-pool message without the pre-conjure cause; `ManagedSpellLease` checked as built. "
                       "Whole tree green in both GIL modes; release-note section \"A version staged before `conjure` "
                       "melds after a notch\" (its example run); rebuild checks OK. Accepted by the owner with the "
                       "epic (2026-10-16)."),
        ("- Status: blocked\n", "- Status: done\n"),
        (lambda t: next(l for l in t.split("\n") if l.startswith("- Updated: ")) + "\n", f"- Updated: {NOW}\n"),
        state_block(s8, "2026-10-16T11:45:26Z", accepted + "; notched 0.2.8248, rebuilt and checked, every "
                    "EXIT_GATE item recorded in the Notes."),
        ("## Decision Log\n",
         f"## Decision Log\n- 2026-10-16 (owner, chat with melder_0): {QUOTE} - S8 accepted with the epic; on this "
         "story's finding: \"just use\n  the private version if its inside the public call thats reasonable\" "
         "(TASK-2026-10-16-public_notch_target_for_staged_versions).\n"),
        ("- [ ] Criteria, required tests/reviews and delegated acceptance or reserved-owner disposition recorded\n",
         "- [x] Criteria, required tests/reviews and delegated acceptance or reserved-owner disposition recorded\n"),
        (lambda t: section(t, "## Context / Handoff Summary", "## Project-Specific Additions"),
         "## Context / Handoff Summary\n- Scope: S8 - conjure wires versions parked before it; cache generation 21; "
         "tests, docs, release note, notch, rebuild.\n- State: done - landed 0.2.8248 and accepted by the owner with "
         "the epic (2026-10-16); the evidence is in the\n  Notes above.\n- Follow-up: the public notch target for "
         "staged versions (TASK-2026-10-16-public_notch_target_for_staged_versions),\n  ruled on by the owner and "
         "next in line.\n- Limits: hosted CI and coverage are the owner's (Not run).\n\n"),
        ("\n## Closure Confirmation\n",
         "\n" + note("DECISION", "S8 closes: " + accepted + ". Reserved-owner disposition: accepted. The owner also "
                     "ruled on this story's finding (\"just use the private version if its inside the public call "
                     "thats reasonable\"): `notch_spell` resolves a staged version by its id through the Book's "
                     "internal lookup, built next in TASK-2026-10-16-public_notch_target_for_staged_versions.",
                     [ev_board], "The lane is closed and its files are free.", "none for this story.")
         + "\n## Closure Confirmation\n"),
    ])

    epic = pathlib.Path(EPIC).read_text(encoding="utf-8")
    edit(EPIC, [
        completion(epic, "`Existence.managed_spell_quantity` built end to end in eight stories - the member "
                         "(0.2.8241), the bind options and record (0.2.8242), the root-owned pool (0.2.8243), "
                         "`ReleaseManagedSpell` and the lease (0.2.8244), leases through the emitted plans and "
                         "`Conduit.managed_spell_meld` (0.2.8245), pools through an ownership transfer (0.2.8246), the "
                         "documentation (S7) and versions staged before conjure with cache generation 21 (0.2.8248). "
                         "Accepted by the owner on 2026-10-16; Milestone 5 (a MelderOps prototype after a release) "
                         "stays with the owner."),
        ("- Status: blocked\n", "- Status: done\n"),
        (lambda t: next(l for l in t.split("\n") if l.startswith("- Updated: ")) + "\n", f"- Updated: {NOW}\n"),
        state_block(epic, "2026-10-16T11:45:26Z", accepted + "; all eight stories closed with their evidence, every "
                    "EXIT_GATE check recorded."),
        ("- [ ] S7 STORY-2026-10-15-managed_docs_release - system docs, graph, tests docs, README, release note, "
         "benchmarks.\n      Work done 2026-10-15, no notch; waits on the owner's acceptance of the epic.\n"
         f"      {S7}\n",
         "- [x] S7 STORY-2026-10-15-managed_docs_release - system docs, graph, tests docs, README, release note, "
         "benchmarks.\n      Documentation, no notch; accepted with the epic (2026-10-16).\n"
         f"      {done_path(S7)}\n"),
        ("- [ ] S8 STORY-2026-10-16-parked_versions_wired_at_conjure - conjure wires versions parked before it; cache "
         "generation\n      21 (the owner's follow-ups of 2026-10-16); also checks `ManagedSpellLease` works. Landed "
         "0.2.8248; waits on the\n      owner's acceptance of the epic.\n"
         f"      {S8}\n",
         "- [x] S8 STORY-2026-10-16-parked_versions_wired_at_conjure - conjure wires versions parked before it; cache "
         "generation\n      21 (the owner's follow-ups of 2026-10-16); also checks `ManagedSpellLease` works.\n"
         "      Landed 0.2.8248; accepted with the epic (2026-10-16).\n"
         f"      {done_path(S8)}\n"),
        ("- [ ] No epic-state transition without story-level evidence.\n- [ ] No closure while required stories are "
         "incomplete or unaccepted.\n- [ ] No program claims without source evidence from story notes.\n- [ ] No "
         "`src/` edit before the story's component patch and mapping note exist.\n",
         "- [x] No epic-state transition without story-level evidence.\n- [x] No closure while required stories are "
         "incomplete or unaccepted.\n- [x] No program claims without source evidence from story notes.\n- [x] No "
         "`src/` edit before the story's component patch and mapping note exist.\n"),
        ("## Decision Log\n",
         f"## Decision Log\n- 2026-10-16 (owner, chat with melder_0, after the S8 report): {QUOTE} - S1-S8 and the "
         "epic accepted\n  and closed.\n"),
        ("- [ ] Criteria, required tests/reviews and delegated acceptance or reserved-owner disposition recorded\n"
         "- [ ] Applicable anti-pattern checks are clear or escalated with evidence.\n",
         "- [x] Criteria, required tests/reviews and delegated acceptance or reserved-owner disposition recorded\n"
         "- [x] Applicable anti-pattern checks are clear or escalated with evidence.\n"),
        (lambda t: section(t, "## Context / Handoff Summary", "## Project-Specific Additions"),
         "## Context / Handoff Summary\n- Scope: `Existence.managed_spell_quantity` end to end (Build Specification "
         "B1-B12), eight stories, one notch per\n  landed story, rebuild last.\n- State: done - accepted by the owner "
         "on 2026-10-16 (Decision Log); S1-S8 closed (tickets/stories/completed/).\n- Source revision: 0.2.8248: "
         "S1-S6 0.2.8241-0.2.8246, S7 documentation, S8 0.2.8248 (melder_1's 0.2.8247 between).\n- Left with the "
         "owner: Milestone 5 (a MelderOps prototype after a release); the backlog tasks found on the way (the\n  "
         "scratch marker, the architecture_and_design lifetimes, the graph's stale prose, the graph tools' census "
         "and\n  indent); the public notch target, which the owner ruled on, runs next.\n- Custody: this lane's files "
         "are free; melder_1's rule-2 task may take spellbook.py once the owner approves D1-D5.\n- Limits: hosted CI "
         "and coverage are the owner's (Not run); codex_bridge could not reach Codex desktop.\n\n"),
        ("\n## Closure Confirmation\n",
         "\n" + note("DECISION", "The epic closes: " + accepted + ". Reserved-owner disposition: accepted. Closed "
                     "together: S7, S8 and this epic (completion summaries; completed/ folders); the board row and its "
                     "detail entry are replaced by three closed anchors (the three oldest dropped to keep twelve); the "
                     "epic's three evidence folders move to the cleared artifact rows, retained as reference. "
                     "Milestone 5 (a MelderOps prototype after a release) stays with the owner. In the same message "
                     "the owner ruled on S8's finding; TASK-2026-10-16-public_notch_target_for_staged_versions builds "
                     "it next.", [ev_board, ev_art], "The managed lane is closed; its files and the release note, notch "
                     "and rebuild are free for the next lane.", "TASK-2026-10-16-public_notch_target_for_staged_versions "
                     "- record the owner's ruling and route it.")
         + "\n## Closure Confirmation\n"),
    ])


if __name__ == "__main__":
    {"boards": boards, "tickets": tickets}[STEP]()
