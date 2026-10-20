"""Mark the four patch docs landed and promoted (the notch target and the owner's extension), before the archive move.

Run from context_compass/:  python archive_patch_lane_extension.py <NOW>
Each replacement must match exactly once; the files stay LF.
"""
import pathlib
import sys

NOW = sys.argv[1]
LANE = pathlib.Path("system_docs/patches/active/public_notch_target_2026_10_16")

EDITS = {
    "architecture_patch.md": [
        ("""- Status: reopened 2026-10-16 for the owner's extension (`add_to_spell_index` / `remove_from_spell_index` take
  `spell_id=`; the lane's text says spell_id); the notch part landed as patched and is promoted; the extension is
  written before its `src/` edit
""",
         """- Status: landed as 0.2.8249 - the notch target and, on the owner's extension, `add_to_spell_index` /
  `remove_from_spell_index` by `spell_id=` with the lane's text saying spell_id; built as patched, promoted into
  src_architecture, src_components, tests_components, tests_architecture and the graph; archived with the task
"""),
        ("- Updated: 2026-10-16T15:09:19Z\n", "- Updated: " + NOW + "\n"),
        ("""- Reopened for the extension (invariants 6-7; component_patch_conduit_index_move_target.md): nothing built for it
  yet.
- What remains: the extension's mapping, tests, code, wording, docs and release note; then the archive, the
  closure and the rebuild. Backlog: the seam's park-first ordering (Risks).
- Next entrypoint: component_patch_conduit_index_move_target.md, then the red tests.
""",
         """- The extension (invariants 6-7; component_patch_conduit_index_move_target.md) is built as patched: both verbs
  take `spell_id=` through `_resolve_spell_to_move` (the shared `_check_spell_argument`, `_owned_spell_by_id`);
  16 unit and 10 integration tests green with the GIL off and on, the index-move and notch callers' suites
  unchanged; the lane's text says spell_id; the system docs, the graph and the release note carry it. Still
  0.2.8249: one landing.
- What remains: nothing in this lane; the rebuild runs last, after the task's closure. Backlog: the seam's
  park-first ordering (Risks).
- Next entrypoint: the canonical documents (src_architecture, src_components, tests_components,
  tests_architecture) and the graph.
"""),
    ],
    "component_patch_conduit_notch_target.md": [
        ("""- Status: built as patched (0.2.8249); promoted into src_components (Conduit Runtime, SpellIndex Mutation Surface,
  the notch flow) and src_architecture; the lane is reopened for the index-move extension
""",
         """- Status: built as patched (0.2.8249); promoted into src_components (Conduit Runtime, SpellIndex Mutation Surface,
  the notch flow) and src_architecture; its refusals reworded to spell_id on the owner's extension; archived
"""),
    ],
    "code_description_patch_conduit_notch_target.md": [
        ("""- Status: built as described (0.2.8249); promoted into src_components (the notch flow) and src_architecture (the
  invariant and failure modes); the lane is reopened for the index-move extension
""",
         """- Status: built as described (0.2.8249); promoted into src_components (the notch flow) and src_architecture (the
  invariant and failure modes); the argument check now shared with the index moves (`_check_spell_argument`);
  archived
"""),
    ],
    "component_patch_conduit_index_move_target.md": [
        ("- Status: written before the extension's `src/` edit (the owner's extension, 2026-10-16)\n",
         """- Status: built as patched (0.2.8249, the owner's extension); promoted into src_components (Conduit Runtime,
  SpellIndex Mutation Surface, the index-move flow), src_architecture, tests_components and tests_architecture;
  archived
"""),
    ],
}


def main() -> None:
    """Apply each patch doc's edits; refuse unless each matches exactly once."""
    for name, edits in EDITS.items():
        doc = LANE / name
        text = doc.read_text(encoding="utf-8")
        for old, new in edits:
            assert text.count(old) == 1, (name, old[:70])
            text = text.replace(old, new, 1)
        doc.write_text(text, encoding="utf-8")
        print(name, "ok")


if __name__ == "__main__":
    main()
