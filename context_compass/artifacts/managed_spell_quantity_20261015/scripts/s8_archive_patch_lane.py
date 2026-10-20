"""S8: record the parked-versions patch lane's promotion and archive (patch status, artifact board, story links).

Run from context_compass/, in two steps around the folder move:
    python <this file> status <NOW>   - mark the four patch docs promoted (Status/Updated/handoff), before the move
    mv -n system_docs/patches/active/parked_versions_wired_at_conjure_2026_10_16 system_docs/patches/completed/
    python <this file> boards <NOW>   - replace the lane's 4 active artifact-board rows with one cleared row at the
                                        top of the cleared region; repoint the story's Artifact Links (historical Notes
                                        keep the paths they were written with)
Every replacement is asserted exactly; nothing is written on a miss.
"""
import pathlib
import sys

STEP, NOW = sys.argv[1], sys.argv[2]
LANE = "parked_versions_wired_at_conjure_2026_10_16"
ACTIVE = f"system_docs/patches/active/{LANE}/"
DONE = f"system_docs/patches/completed/{LANE}/"
STORY = "tickets/stories/2026-10-16_parked_versions_wired_at_conjure_story.md"
CLEARED_ROW = (
    f"| {STORY} | {DONE} | promote_to_documentation | Promoted at landing (0.2.8248) to src_architecture, "
    "src_components, tests_components and tests_architecture with their indexes, and to the graph; the four patch "
    "docs (architecture, three component) archived. | " + NOW + " |"
)


def replace_once(path: pathlib.Path, pairs: tuple) -> None:
    """Apply exact replacements, each expected exactly once (LF files)."""
    text = path.read_bytes().decode("utf-8")
    assert "\r\n" not in text, path
    for old, new in pairs:
        assert text.count(old) == 1, (path, old[:80], text.count(old))
        text = text.replace(old, new)
    path.write_bytes(text.encode("utf-8"))
    print("edited", path)


def mark_status() -> None:
    """The patch docs say they were built as written, promoted and archived at landing."""
    lane = pathlib.Path(ACTIVE)
    replace_once(lane / "architecture_patch.md", (
        ("- Status: active; written before any `src/` edit (2026-10-16)\n",
         "- Status: promoted at landing (0.2.8248) and archived; written before any `src/` edit (2026-10-16)\n"),
        ("- Updated: 2026-10-16T09:42:16Z\n", f"- Updated: {NOW}\n"),
        ("- What changed: the patch is written; nothing in `src/` yet.\n"
         "- What remains: the mapping note, red tests, the change, validation, docs, the notch and the rebuild.\n"
         "- Next entrypoint: component_patch_spellbook_creation_system.md.\n",
         "- What changed: built as written and landed as 0.2.8248 - the parked loop in `define_conduit_into_spells`,\n"
         "  generation 21, the missing-pool message and the comments; red then green in both GIL modes, the whole tree\n"
         "  green; promoted into src_architecture, src_components, the tests docs and the graph, then archived.\n"
         "- What remains: nothing in this lane; the owner accepts the story with the epic.\n"
         "- Next entrypoint: none (archived).\n"),
    ))
    for name in ("component_patch_spellbook_creation_system.md", "component_patch_caching_system.md",
                 "component_patch_site_plan_runtime_helpers.md"):
        replace_once(lane / name, (
            ("- Created: 2026-10-16T09:42:54Z\n",
             f"- Created: 2026-10-16T09:42:54Z\n- Status: built as written; promoted at landing (0.2.8248) and "
             f"archived {NOW}\n"),
        ))


def sync_boards() -> None:
    """Artifact board and the story's Artifact Links follow the archived folder."""
    assert pathlib.Path(DONE).is_dir() and not pathlib.Path(ACTIVE).exists(), "move the folder first"
    board = pathlib.Path("artifact_board.md")
    text = board.read_bytes().decode("utf-8")
    assert "\r\n" not in text
    lines = text.split("\n")
    begin_active = lines.index("<!-- BEGIN USER-DEFINED: active_artifacts -->")
    end_active = lines.index("<!-- END USER-DEFINED: active_artifacts -->")
    rows = [i for i in range(begin_active + 1, end_active) if f"| {ACTIVE}" in lines[i]]
    assert len(rows) == 4, len(rows)
    assert all(lines[i].startswith(f"| {STORY} | {ACTIVE}") for i in rows)
    assert sum(ACTIVE in line for line in lines) == 4
    kept = [line for i, line in enumerate(lines) if i not in set(rows)]
    begin_cleared = kept.index("<!-- BEGIN USER-DEFINED: cleared_artifacts -->")
    kept.insert(begin_cleared + 1, CLEARED_ROW)
    board.write_bytes("\n".join(kept).encode("utf-8"))
    print("artifact board: removed", len(rows), "active rows; added the cleared row")
    story = pathlib.Path(STORY)
    story_text = story.read_bytes().decode("utf-8")
    old = f"  - {ACTIVE}"
    assert story_text.count(old) == 4, story_text.count(old)
    story.write_bytes(story_text.replace(old, f"  - {DONE}").encode("utf-8"))
    print("repointed the story's four Artifact Links")


if __name__ == "__main__":
    {"status": mark_status, "boards": sync_boards}[STEP]()
