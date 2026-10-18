"""
S6 part A's board and ticket-link sync after the docs and graph pass (melder_0, 2026-10-18).

Run from context_compass/:  python3 artifacts/correctness_defects_20261017/scripts/s6_part_a_boards.py <NOW>
- artifact_board.md: the S6 probe rows name their re-runs at the fix, the patch-doc row says part A is promoted,
  two rows for the probes added since (the release-note example, the cross-frame refusal).
- attention_board.md: the managed_settings_spell_id row's next action and updated_at.
- the S6 story's Artifact Links: the re-runs and the two probes with their runs.
Each file is re-read right before its write; every edit is checked to apply exactly once.
"""
import pathlib
import sys

NOW = sys.argv[1]
STORY = "tickets/stories/2026-10-17_release_routes_parked_version_objects_to_active_pool_story.md"
A = "artifacts/correctness_defects_20261017/"

ROW_NEXT = {
    A + "probes/probe_managed_release_routing.py":
        "Cases Q1-Q6 with their runs (runs/probe_managed_release_routing_gil0.txt, _gil1.txt) and their re-run at the "
        "fix (_after_gil0.txt, _after_gil1.txt: Q2-Q4 stop at staging; Q1, Q5 and Q6 unchanged).",
    A + "probes/probe_same_id_staging.py":
        "Cases S1 (re-staging one spell_id is refused) and S2 (a settings change minted a new id) with their runs "
        "(runs/probe_same_id_staging_gil0.txt, _gil1.txt) and their re-run at the fix (_after_gil0.txt, "
        "_after_gil1.txt: S2's rebind keeps the spell_id).",
    A + "probes/probe_settings_rebind.py":
        "Cases R1-R3 (a settings change by cleanup_spell and bind, a settings-only staging, a mode change) with their "
        "runs on the tree and on the prototype (runs/probe_settings_rebind_tree_gil0.txt, _gil1.txt, _proto_gil0.txt, "
        "_proto_gil1.txt) and their re-run at the fix (_after_gil0.txt, _after_gil1.txt).",
    "system_docs/patches/active/managed_settings_spell_id_2026_10_17/":
        "Entry-gate docs of S6's fix; part A's (architecture, three component patches, the pool's code description) "
        "landed at 0.2.8254 and are promoted to the system documents and the graph; part B's component patch waits "
        "for the owner's talk; archive at the story's closure.",
}
NEW_ROWS = [
    f"| {STORY} | {A}probes/probe_release_note_s6.py | investigation_evidence | in_progress | retain_as_reference | "
    "Cases E1-E2: the release note's example run as written on 0.2.8254 (runs/probe_release_note_s6_gil0.txt, "
    f"_gil1.txt). | {NOW} | HELPFUL |",
    f"| {STORY} | {A}probes/probe_cross_frame_same_id.py | investigation_evidence | in_progress | "
    "retain_as_reference | Cases C1-C4: one managed class bound at one address in two frames under process-wide ids "
    "is refused at the second bind once the first Book is conjured, else at the second conjure "
    f"(runs/probe_cross_frame_same_id_gil0.txt, _gil1.txt). | {NOW} | HELPFUL |",
]


def artifact_board() -> None:
    """Rewrite the four S6 rows' next and updated_at cells and insert the two probe rows."""
    path = pathlib.Path("artifact_board.md")
    lines = path.read_text(encoding="utf-8").split("\n")
    done = set()
    anchor = None
    for i, line in enumerate(lines):
        cells = line.split(" | ")
        if len(cells) != 8 or cells[0] != "| " + STORY:
            continue
        if cells[1] in ROW_NEXT:
            assert cells[1] not in done, cells[1]
            cells[5] = ROW_NEXT[cells[1]]
            cells[6] = NOW
            lines[i] = " | ".join(cells)
            done.add(cells[1])
            if cells[1].startswith("system_docs/patches/"):
                anchor = i
    assert done == set(ROW_NEXT), set(ROW_NEXT) - done
    assert anchor is not None
    text = "\n".join(lines)
    for row in NEW_ROWS:
        assert row.split(" | ")[1] not in text, "row already present"
    lines[anchor + 1:anchor + 1] = NEW_ROWS
    path.write_text("\n".join(lines), encoding="utf-8", newline="\n")
    print("artifact_board: 4 rows updated, 2 added")


def attention_board() -> None:
    """Set the managed_settings_spell_id row's next action and updated_at."""
    path = pathlib.Path("attention_board.md")
    lines = path.read_text(encoding="utf-8").split("\n")
    hits = [i for i, line in enumerate(lines) if line.startswith("| managed_settings_spell_id | ")]
    assert len(hits) == 1, hits
    cells = lines[hits[0]].split(" | ")
    assert len(cells) == 12 and cells[9] == STORY, cells
    cells[6] = ("Part A is in at 0.2.8254 with tests, docs and graph: rebuild last, release the held files to "
                "melder_1, then report to the owner and talk through part B and the legacy record.")
    cells[10] = NOW
    lines[hits[0]] = " | ".join(cells)
    path.write_text("\n".join(lines), encoding="utf-8", newline="\n")
    print("attention_board: managed_settings_spell_id row updated")


def story_links() -> None:
    """Add the re-runs and the two probes with their runs to the story's ARTIFACT_PATHS."""
    path = pathlib.Path(STORY)
    text = path.read_text(encoding="utf-8")
    anchor = "  - " + A + "runs/probe_settings_rebind_proto_gil1.txt\n"
    assert text.count(anchor) == 1
    added = [
        A + "runs/probe_managed_release_routing_after_gil0.txt (Q1-Q6 re-run at the fix)",
        A + "runs/probe_managed_release_routing_after_gil1.txt",
        A + "runs/probe_same_id_staging_after_gil0.txt (S1-S2 re-run at the fix)",
        A + "runs/probe_same_id_staging_after_gil1.txt",
        A + "runs/probe_settings_rebind_after_gil0.txt (R1-R3 re-run at the fix)",
        A + "runs/probe_settings_rebind_after_gil1.txt",
        A + "probes/probe_release_note_s6.py (cases E1, E2: the release note's example)",
        A + "runs/probe_release_note_s6_gil0.txt",
        A + "runs/probe_release_note_s6_gil1.txt",
        A + "probes/probe_cross_frame_same_id.py (cases C1-C4: one managed class in two frames)",
        A + "runs/probe_cross_frame_same_id_gil0.txt",
        A + "runs/probe_cross_frame_same_id_gil1.txt",
    ]
    links = text[text.index("## Artifact Links"):text.index("## Context Management")]
    for item in added:
        # Only the Artifact Links block counts: the Notes already cite some of these runs as evidence.
        assert item.split(" ")[0] not in links, item
    text = text.replace(anchor, anchor + "".join("  - " + item + "\n" for item in added))
    path.write_text(text, encoding="utf-8", newline="\n")
    print("story: 12 artifact links added")


# The first run (02:06Z) applied the two boards and stopped at story_links on a check that read the whole ticket;
# the check now reads only the Artifact Links block, and a step can be run alone: `... <NOW> story`.
STEPS = {"artifact": artifact_board, "attention": attention_board, "story": story_links}
for step in (sys.argv[2:] or list(STEPS)):
    STEPS[step]()
