"""S6 turn-in: close the story (summary, Status, State Transition, checklists, handoff), move it to completed/ with
`mv -n` semantics, tick S6 in the epic with its MEASURE note and handoff, and sync the attention and artifact boards
(route to S7, closed anchor capped at 12, notch notice, the S6 patch rows).

Run from the repository root: python s6_close.py <NOW>
"""
import pathlib
import re
import sys

now = sys.argv[1]
CC = pathlib.Path("context_compass")
STORY = CC / "tickets/stories/2026-10-15_managed_ownership_transfer_story.md"
DONE = CC / "tickets/stories/completed/2026-10-15_managed_ownership_transfer_story.md"
EPIC = CC / "tickets/epics/2026-10-14_managed_spell_quantity_epic.md"
BOARD = CC / "attention_board.md"
ARTIFACTS = CC / "artifact_board.md"
NOTE = pathlib.Path("release_docs/next_version_release.md")


def replace_once(text: str, old: str, new: str) -> str:
    assert text.count(old) == 1, old[:90]
    return text.replace(old, new)


def check_width(before: str, after: str, name: str) -> None:
    old = set(before.splitlines())
    long = [l for l in after.splitlines() if l not in old and len(l) > 120 and not l.startswith("|")]
    assert not long, (name, long)


# ---- the story -------------------------------------------------------------------------------------------------
assert STORY.exists() and not DONE.exists()
story = STORY.read_text(encoding="utf-8")
before = story
title = "# Story: managed_ownership_transfer - pools travel with an ownership transfer, back on rollback\n"
story = replace_once(story, title + "\n## Metadata\n", title + f"""
- Completed: {now}
- Summary: landed 0.2.8246 - the owner stamp follows an ownership transfer's lineage both ways: the flip and the
  parked-member migration stamp through `_restamp` (the stamp-back registered first, a composed pool's discard in a
  `finally`), and `Creations.discard_managed_quantity` takes back an empty pool a stamp composed; pools move as the
  rows S3 and S4 built. U9 settled (a notch never re-stamps). Whole tree green in both GIL modes. Release-note
  sections "An ownership transfer brings the spell's objects with it by default" and
  "`Existence.managed_spell_quantity`: objects leased from a root-owned pool and released back" extended.

## Metadata
""")
story = replace_once(story, "- Status: in_progress\n", "- Status: done\n")
story = replace_once(story, "- Updated: 2026-10-15T20:48:33Z\n", f"- Updated: {now}\n")
story = replace_once(story, """## State Transition Event
- from_state: ready
- to_state: in_progress
- transition_reason: S5 landed and closed (0.2.8245, 2026-10-15T18:15:07Z); S6 starts with the transfer path and U9.
- prior: draft -> ready (2026-10-15T09:29:51Z): ready once S5 lands.
""", """## State Transition Event
- from_state: in_progress
- to_state: done
- transition_reason: acceptance criteria met with red-then-green tests in both GIL modes, the probe's B, D, E, F and G
  fixed, the transfer suites and the whole tree green in both modes; notched 0.2.8246 (delegated routine closure
  under the owner's go-ahead).
- prior: ready -> in_progress (2026-10-15T18:18:41Z): S5 landed and closed (0.2.8245, 2026-10-15T18:15:07Z); S6
  started with the transfer path and U9.
- prior: draft -> ready (2026-10-15T09:29:51Z): ready once S5 lands.
""")
for line in (
    "Red tests: move, no move, rollback, parked members, releases.",
    "Implement; green in both GIL modes; the transfer suites.",
    "Notch, release note, epic spec update, close, board sync.",
    "Enforce Ticket Microcycle across all linked tasks.",
    "Record meaningful attributed findings in supported Notes/comments or authorized linked evidence.",
    "No story-state transition without linked task-state evidence.",
    "No closure while required tasks remain active or un-routed.",
    "No cross-task synthesis claims without ticket-note evidence pointers.",
    "No `src/` edit before the component patch and the mapping note exist.",
    "Criteria, required tests/reviews and delegated acceptance or reserved-owner disposition recorded",
    "Applicable anti-pattern checks are clear or escalated with evidence.",
):
    story = replace_once(story, f"- [ ] {line}\n", f"- [x] {line}\n")
story = replace_once(
    story,
    "- For the owner: stamping versions staged before conjure (DECISION note, point 6).\n",
    "- For the owner: stamping versions staged before conjure (DECISION note, point 6); carried to the epic's Open\n"
    "  Questions.\n",
)
story = replace_once(story, """## Context / Handoff Summary
- Scope: S6 - managed pools through ownership transfer (move, no move, rollback, parked members) and the notch (U9).
- State: in_progress on 0.2.8245; U9 answered and the probe read (FACT), the fix designed (DECISION).
- Next: red tests (unit beside test_transfer_of_ownership.py, the discard tests, the integration file).
""", """## Context / Handoff Summary
- Scope: S6 - managed pools through ownership transfer (move, no move, rollback, parked members) and the notch (U9).
- State: done; landed 0.2.8246 (the FACT, DECISION, PLAN and MEASURE notes; runs/s6_validation_index.md; the probe
  before and after).
- Open for the owner: stamping versions staged with `bind_inactive` before conjure (DECISION note, point 6; the
  epic's Open Questions). Documented: after a no-move transfer a parked managed version notched in on the target
  needs `conduit=` for a release by class.
- Next: S7 (STORY-2026-10-15-managed_docs_release) - system docs, graph, tests docs, README, release note,
  benchmarks, patch promotion.
""")
check_width(before, story, "story")
STORY.write_text(story, encoding="utf-8")
STORY.rename(DONE)  # mv -n: DONE was checked absent above
story_lines = len(DONE.read_text(encoding="utf-8").splitlines())

# ---- the release-note ranges the epic note cites -------------------------------------------------------------
note_lines = NOTE.read_text(encoding="utf-8").splitlines()
def find(prefix: str) -> int:
    hits = [i + 1 for i, l in enumerate(note_lines) if l.startswith(prefix)]
    assert len(hits) == 1, (prefix, hits)
    return hits[0]
t_start = find("A transfer now moves each version's owner record both ways (0.2.8246).")
t_end = find("- A version staged with `bind_inactive` before `conjure` carries no owner record")
m_start = find("Pools follow an ownership transfer (0.2.8246).")
m_end = find("  not-managed `ValueError`; release again once the transfer has returned.")

# ---- the epic ----------------------------------------------------------------------------------------------------
epic = EPIC.read_text(encoding="utf-8")
before = epic
epic = re.sub(r"^- Updated: \S+\n", f"- Updated: {now}\n", epic, count=1, flags=re.M)
epic = replace_once(epic, """- [ ] S6 STORY-2026-10-15-managed_ownership_transfer - pools through move, no move, rollback and notch.
      tickets/stories/2026-10-15_managed_ownership_transfer_story.md
""", """- [x] S6 STORY-2026-10-15-managed_ownership_transfer - pools through move, no move, rollback and notch; the owner
      stamp follows the lineage.
      Landed 0.2.8246. tickets/stories/completed/2026-10-15_managed_ownership_transfer_story.md
""")
epic = replace_once(epic, "\n## Closure Confirmation\n", f"""
- DATETIME: {now}
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: MEASURE
  CLAIM: S6 landed as 0.2.8246: the owner stamp follows an ownership transfer's lineage both ways. The flip and
    `_migrate_inactive_members` stamp through `_restamp` (the stamp-back registered first, a composed pool's discard
    in a `finally`); `Creations.discard_managed_quantity` takes back an empty pool a stamp composed; rows are
    unchanged (S3, S4). U9 is settled: a notch never re-stamps, so the stamp has to follow the transfer - for every
    existence, `unique` included. Red then green in both GIL modes (42 tests: 19 stamp, 11 discard, 12 integration),
    the probe's B, D, E, F and G fixed and A, C unchanged, the whole tree green in both modes. Stamping versions
    staged before conjure stays with the owner (Open Questions).
  EVIDENCE:
  - context_compass/tickets/stories/completed/2026-10-15_managed_ownership_transfer_story.md:1-{story_lines}
  - context_compass/artifacts/managed_spell_quantity_20261015/runs/s6_validation_index.md:1-81
  - release_docs/next_version_release.md:{t_start}-{t_end}
  - release_docs/next_version_release.md:{m_start}-{m_end}
  IMPACT: Every mechanic of the build has landed (S1-S6, Milestone 3); S7 documents it, promotes the patches and
    records the benchmarks.
  NEXT: Rebuild and check for 0.2.8246, then S7 - read its story and the patch lane, then the system docs.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

## Closure Confirmation
""")
handoff_start = epic.index("## Context / Handoff Summary\n")
handoff_end = epic.index("## Project-Specific Additions\n")
assert epic.count("## Context / Handoff Summary\n") == 1 and handoff_start < handoff_end
epic = epic[:handoff_start] + """## Context / Handoff Summary
- Scope: build `Existence.managed_spell_quantity` end to end (Build Specification B1-B12) in seven stories, one notch
  per landed story, rebuild last.
- Controlling decisions: the Decision Log (owner rulings 2026-10-12 to 2026-10-15; melder_0's build decisions of
  2026-10-15 - the S4 story's DECISION note: the lease on the root, the holding root; the S5 and S6 build decisions).
  The objects handed out are the agents'; Melder keeps the structure right.
- Source revision: 0.2.8246 - S1 landed 0.2.8241 (the member, the matrix, route family "managed", Phase 6 rank 0);
  S2 0.2.8242 (the four bind options, Spell fields, the managed-only id part, record 4.2.0 and replay); S3 0.2.8243
  (the pool, the exhaustion error, the Creations pool map, owner stamping, the probes, purge 0); S4 0.2.8244
  (`ReleaseManagedSpell`, the lease, the Creations register/unregister calls, the root exports); S5 0.2.8245 (leases
  through the emitted plans and doors, `Conduit.managed_spell_meld`); S6 0.2.8246 (the owner stamp follows a
  transfer's lineage both ways, `Creations.discard_managed_quantity`).
- Done: Milestones 1-3; the epic rewritten and archived; the architecture patch doc; the seven stories; S1-S6 landed
  and closed (tickets/stories/completed/); U1-U11 settled (B2-B8).
- Remaining: S7 (tickets/stories/2026-10-15_managed_docs_release_story.md: system docs, graph, tests docs, README,
  release note, benchmarks before/after against baseline_0_2_8244/, patch promotion); the owner's call on stamping
  versions staged before conjure (Open Questions); the owner's acceptance.
- Limits: the codex_bridge listing fails ("Codex app tool request failed" on every try on 2026-10-15, last at
  20:55Z), so the tickets and the board row are the coordination record; hosted CI runs and coverage are the
  owner's (Not run).
- Owners: melder_0 builds; the owner accepts. melder_1's open task (meld_contract_scan) plans its build on a scratch
  tree; whoever lands after 0.2.8246 notches above it.
- Next 1-3 actions: rebuild the assets and bundles for 0.2.8246 and check them; S7 - read its story, the patch lane
  and the system-doc sections the managed member touches.

""" + epic[handoff_end:]
check_width(before, epic, "epic")
EPIC.write_text(epic, encoding="utf-8")

# ---- the attention board --------------------------------------------------------------------------------------
board = BOARD.read_text(encoding="utf-8")
before = board
row = re.compile(r"^\| melder_object_pools \|.*\|$", re.M)
assert len(row.findall(board)) == 1
board = row.sub(
    "| melder_object_pools | in_progress | implementation | claude | melder_0 | none | S7: rebuild for 0.2.8246, then read"
    " the S7 story and the patch lane and start the system docs. | `managed_spell_quantity` built in seven stories (epic"
    " Build Specification), one notch per story, rebuild last. | Every story landed with green tests and the owner"
    " accepts, or the owner redirects. | tickets/stories/2026-10-15_managed_docs_release_story.md | " + now + " | REQUIRED |",
    board,
)
board = replace_once(
    board,
    "    - tickets/stories/2026-10-15_managed_ownership_transfer_story.md\n",
    "    - tickets/stories/2026-10-15_managed_docs_release_story.md\n",
)
begin = "<!-- BEGIN USER-DEFINED: closed_anchors -->\n"
end = "<!-- END USER-DEFINED: closed_anchors -->"
a = board.index(begin) + len(begin)
b = board.index(end)
anchors = [l for l in board[a:b].splitlines() if l.startswith("| ")]
while len(anchors) >= 12:
    anchors.pop(0)
anchors.append(
    "| managed_ownership_transfer | done | melder_0 | tickets/stories/completed/2026-10-15_managed_ownership_transfer_story.md"
    " | Landed 0.2.8246 (S6 of EPIC-2026-10-14-managed_spell_quantity: the owner stamp follows a transfer's lineage both"
    " ways, `discard_managed_quantity`). Next: S7 docs. | " + now + " |"
)
assert len(anchors) == 12
board = board[:a] + "\n".join(anchors) + "\n" + board[b:]
board = replace_once(
    board,
    "  injections - and `Conduit.managed_spell_meld`; S5). Notch above it if you land after.\n",
    "  injections - and `Conduit.managed_spell_meld`; S5). Notch above it if you land after.\n"
    "- melder_0 landed 0.2.8246 (an ownership transfer stamps every version onto the new owner and a failed one stamps\n"
    "  them back, discarding the empty pools its stamps composed; `Creations.discard_managed_quantity`; S6). Notch above\n"
    "  it if you land after.\n",
)
check_width(before, board, "attention board")
BOARD.write_text(board, encoding="utf-8")

# ---- the artifact board ----------------------------------------------------------------------------------------
art = ARTIFACTS.read_text(encoding="utf-8")
lines = art.split("\n")
changed = 0
for i, l in enumerate(lines):
    if "managed_ownership_transfer.md" in l and "S6 (in progress): " in l:
        l = l.replace("S6 (in progress): ", "S6 (landed 0.2.8246, story closed): ")
        l = l.replace("| 2026-10-15T18:45:39Z | REQUIRED |", "| " + now + " | REQUIRED |")
        lines[i] = l
        changed += 1
assert changed == 2, changed
ARTIFACTS.write_text("\n".join(lines), encoding="utf-8")

print("story closed ->", DONE, story_lines, "lines")
print("release note ranges", t_start, t_end, m_start, m_end)
print("epic, attention board and artifact board synced")
