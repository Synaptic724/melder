"""S8 to review: the story's and the epic's state, checklists and resume views, and the board row (before the rebuild).

Run from context_compass/: python <this file> <NOW>
Exact replacements, each asserted once; LF files; nothing is written for a file whose replacement misses.
"""
import pathlib
import sys

NOW = sys.argv[1]
STORY = pathlib.Path("tickets/stories/2026-10-16_parked_versions_wired_at_conjure_story.md")
EPIC = pathlib.Path("tickets/epics/2026-10-14_managed_spell_quantity_epic.md")
BOARD = pathlib.Path("attention_board.md")


def section(text: str, heading: str, next_heading: str) -> str:
    """Return the exact text from a heading line up to (not including) the next heading line."""
    start = text.index(heading + "\n")
    end = text.index("\n" + next_heading + "\n", start) + 1
    return text[start:end]


def edit(path: pathlib.Path, pairs: list) -> None:
    """Apply exact replacements, each expected once; write once."""
    text = path.read_bytes().decode("utf-8")
    assert "\r\n" not in text, path
    for old, new in pairs:
        if callable(old):
            old = old(text)
        assert text.count(old) == 1, (path.name, old[:90], text.count(old))
        text = text.replace(old, new)
    path.write_bytes(text.encode("utf-8"))
    print("edited", path)


STORY_STATE = """## State Transition Event
- from_state: in_progress
- to_state: blocked
- transition_reason: S8's work is done and notched 0.2.8248 - the conjure loop, generation 21, the message, the whole
  tree green in both GIL modes, `ManagedSpellLease` checked as built, the system docs and graph, the release note (its
  example run in both GIL modes) and the patch lane archived; the rebuild runs last, after these records. The
  EXIT_GATE's remaining item is the owner's acceptance, a reserved decision. Unblock: the owner accepts or redirects.
  The board row reads `review`.
- prior: blocked -> in_progress (2026-10-16T09:20:01Z): melder_1 landed 0.2.8247 (assets and bundles rebuilt, both
  checks OK) and handed back the four call-site lines and five test doubles, so the release note, the next notch, the
  rebuild and the system docs were free; the owner said "fix bind_inactive" (chat, 2026-10-16) and kept
  `ManagedSpellLease` as it is, asking that it be checked to work.
- prior: draft -> blocked: approved by the owner on 2026-10-16 ("bind_inactive should behave the same before and after
  conjure"; "you can bump the cache"); blocked until melder_1 reported its landing, because the release note, the
  next notch, the rebuild and the system docs were its for that landing.

"""

STORY_HANDOFF = """## Context / Handoff Summary
- Scope: S8 - conjure wires versions parked before it; cache generation 21; tests, docs, release note, notch, rebuild.
- State: blocked on the owner's acceptance (board: review), notched 0.2.8248. Done: U12 settled (FACT 09:37:24Z),
  the patch lane and the mapping (PLAN 09:43:47Z), the loop, generation 21 and the message, red then green (MEASURE
  09:50:18Z), the whole tree in both GIL modes and the `ManagedSpellLease` check (MEASURE 11:00:56Z), the system docs
  and graph (MEASURE 11:20:54Z), the notch and the release note with its example run in both GIL modes (MEASURE
  11:39:55Z), the patch lane archived under patches/completed/.
- Found: no public call returns a staged version's Spell for `notch_spell` - a backlog draft for the owner's design
  call (tickets/tasks/backlog/2026-10-16_public_notch_target_for_staged_versions_task.md).
- Next: the rebuild last (both checks), then the report; then the owner accepts S8 with the epic (S7 and S8 close with
  it) or redirects.
- Custody: once the rebuild passes, spellbook.py, spellbook_creation_system.py, transfer_of_ownership.py,
  site_plan_lowering.py, caching_system.py, the release note, the next notch, the system docs and the graph are free
  for melder_1's rule-2 landing; a change the owner asks of S8 lands after it.
- Limits: hosted CI and coverage are the owner's (Not run); codex_bridge cannot reach Codex desktop (2026-10-16, again
  at 11:33Z).

"""

EPIC_STATE = """## State Transition Event
- from_state: in_progress
- to_state: blocked
- transition_reason: S8 is done and notched 0.2.8248 (conjure wires the versions staged before it, cache generation
  21, `ManagedSpellLease` checked as built; the rebuild runs last, after these records), so every story's work has
  landed (S1-S6 and S8 notched, S7 documentation). The EXIT_GATE's remaining item is the owner's acceptance, a
  reserved decision. Unblock: the owner accepts S1-S8 or redirects. The board row reads `review`.
- prior: blocked -> in_progress (2026-10-16T09:30:00Z): the owner ruled on every open item (S8 builds the conjure
  wiring and cache generation 21; `ManagedSpellLease` stays as built and S8 checks that it works) and melder_1 landed
  0.2.8247 and handed back this lane's files, so S8 ran (DECISION note of that timestamp).
"""

EPIC_HANDOFF = """## Context / Handoff Summary
- Scope: build `Existence.managed_spell_quantity` end to end (Build Specification B1-B12) in eight stories, one notch
  per landed story, rebuild last; S8 carried the owner's follow-ups of 2026-10-16.
- Controlling decisions: the Decision Log (owner rulings 2026-10-12 to 2026-10-16; melder_0's build decisions of
  2026-10-15 - the S4 story's DECISION note: the lease on the root, the holding root; the S5 and S6 build decisions -
  which the owner kept on 2026-10-16, except the cache generation, which S8 moved to 21). The objects handed out are
  the agents'; Melder keeps the structure right.
- Source revision: 0.2.8248 (S8). S1 0.2.8241 (the member, the matrix, route family "managed", Phase 6 rank 0); S2
  0.2.8242 (the four bind options, Spell fields, the managed-only id part, record 4.2.0 and replay); S3 0.2.8243 (the
  pool, the exhaustion error, the Creations pool map, owner stamping, the probes, purge 0); S4 0.2.8244
  (`ReleaseManagedSpell`, the lease, the Creations register/unregister calls, the root exports); S5 0.2.8245 (leases
  through the emitted plans and doors, `Conduit.managed_spell_meld`); S6 0.2.8246 (the owner stamp follows a
  transfer's lineage both ways); melder_1's 0.2.8247 between them; S8 0.2.8248 (conjure wires the versions staged
  before it; cache generation 21).
- Done: Milestones 1-4 and 6; S1-S6 landed and closed (tickets/stories/completed/); S7's work (no notch) and S8's
  (0.2.8248), both in review; U1-U12 settled (B2-B8; U12 in the S8 story).
- Remaining: the rebuild for 0.2.8248 (last, both checks), then the owner's acceptance of the epic, which closes S7,
  S8 and the epic; Milestone 5 (the MelderOps prototype) after a release, with the owner.
- Found and parked: five backlog tasks - the scratch marker in `src/`, the architecture_and_design lifetimes, the
  graph's stale prose, the graph tools' census and indent (2026-10-16T00:53:23Z), and a public notch target for
  staged versions (S8, a draft waiting on the owner's choice of shape).
- Limits: codex_bridge cannot reach Codex desktop (every try; last at 2026-10-16T11:33Z), so the tickets and the board
  row are the coordination record; hosted CI runs and coverage are the owner's (Not run).
- Owners: melder_0 builds; the owner accepts. melder_1's rule-2 task waits on the owner's approval of D1-D5; this
  lane's files (spellbook.py among them) are free for it once the 0.2.8248 rebuild passes.
- Next 1-3 actions: rebuild last and check; report to the owner; on the owner's acceptance close S7, S8 and the epic
  (completion summaries, completed/, board anchors, artifact dispositions).

"""


def main() -> None:
    """Edit the story, the epic and the board."""
    edit(STORY, [
        ("- Status: in_progress\n", "- Status: blocked\n"),
        (lambda t: section(t, "## State Transition Event", "## Dependencies / Related Work"), STORY_STATE),
        ('- [ ] Docs (the failure mode "Stage versions after conjure" becomes a fixed defect), release note, notch, '
         'rebuild last.\n- [ ] Enforce Ticket Microcycle across all linked tasks.\n- [ ] Record meaningful attributed '
         'findings in supported Notes/comments or authorized linked evidence.\n',
         '- [x] Docs (the failure mode "Stage versions after conjure" is a fixed defect), the release note (its example '
         'run in\n      both GIL modes) and the notch 0.2.8248; the patch lane archived.\n- [ ] Rebuild last: the asset '
         'runner and the LLM bundles, each with `--check`.\n- [x] Enforce Ticket Microcycle across all linked tasks.\n'
         '- [x] Record meaningful attributed findings in supported Notes/comments or authorized linked evidence.\n'),
        ("- Restored worlds with staged members take the fixed path too -> run the restore suites.\n",
         "- Restored and grafted worlds stage their members after conjure, so they took the wired path already (U12 FACT\n"
         "  note) -> their suites run as regression checks.\n"),
        ("- [ ] No story-state transition without linked task-state evidence.\n- [ ] No closure while required tasks "
         "remain active or un-routed.\n- [ ] No cross-task synthesis claims without ticket-note evidence pointers.\n"
         "- [ ] No `src/` edit before the component patch and the mapping note exist.\n",
         "- [x] No story-state transition without linked task-state evidence.\n- [x] No closure while required tasks "
         "remain active or un-routed (S8 moves to review, not to done).\n- [x] No cross-task synthesis claims without "
         "ticket-note evidence pointers.\n- [x] No `src/` edit before the component patch and the mapping note exist "
         "(patch 09:42Z, mapping 09:43:47Z,\n      first `src/` edit after the red run).\n"),
        ("- [ ] Applicable anti-pattern checks are clear or escalated with evidence.\n\n## Noting Behavior\n",
         "- [x] Applicable anti-pattern checks are clear or escalated with evidence.\n\n## Noting Behavior\n"),
        (lambda t: section(t, "## Context / Handoff Summary", "## Project-Specific Additions"), STORY_HANDOFF),
        (lambda t: next(line for line in t.split("\n") if line.startswith("- Updated: ")) + "\n",
         "- Updated: " + NOW + "\n"),
    ])
    edit(EPIC, [
        ("- Status: in_progress\n", "- Status: blocked\n"),
        ("- Updated: 2026-10-16T09:30:00Z\n", "- Updated: " + NOW + "\n"),
        (lambda t: t[t.index("## State Transition Event\n"):t.index("- prior: in_progress (build) -> blocked "
                                                                     "(2026-10-15T23:43:36Z)")],
         EPIC_STATE),
        ("- [ ] Milestone 6: S8 - the owner's 2026-10-16 follow-ups (parked versions wired at conjure, cache generation "
         "21),\n      landed after melder_1's fix.\n",
         "- [x] Milestone 6: S8 - the owner's 2026-10-16 follow-ups (parked versions wired at conjure, cache generation "
         "21),\n      landed as 0.2.8248 after melder_1's 0.2.8247.\n"),
        ("      21 (the owner's follow-ups of 2026-10-16); also checks `ManagedSpellLease` works. In progress on "
         "0.2.8247.\n",
         "      21 (the owner's follow-ups of 2026-10-16); also checks `ManagedSpellLease` works. Landed 0.2.8248; "
         "waits on the\n      owner's acceptance of the epic.\n"),
        (lambda t: section(t, "## Context / Handoff Summary", "## Project-Specific Additions"), EPIC_HANDOFF),
    ])
    board = BOARD.read_bytes().decode("utf-8")
    old_row = next(line for line in board.split("\n") if line.startswith("| melder_object_pools | "))
    new_row = (
        "| melder_object_pools | review | handoff | claude | melder_0 | the owner's acceptance (reserved) | Rebuild the "
        "assets and LLM bundles last (both --check), then report to the owner. | Versions parked before conjure meld "
        "after a notch (every existence); cache generation 21; landed as 0.2.8248. | The owner accepts the epic "
        "(S1-S8), or redirects. | tickets/stories/2026-10-16_parked_versions_wired_at_conjure_story.md | " + NOW +
        " | REQUIRED |"
    )
    old_trigger = ("  SWITCH_TRIGGER: S8 lands with green tests and the owner accepts the epic (S1-S8), or the owner "
                   "redirects.\n")
    edit(BOARD, [
        (old_row, new_row),
        (old_trigger, "  SWITCH_TRIGGER: The owner accepts the epic (S1-S8), or redirects.\n"),
    ])


if __name__ == "__main__":
    main()
