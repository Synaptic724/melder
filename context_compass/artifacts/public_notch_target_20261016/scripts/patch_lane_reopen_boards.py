"""Reopened lane: fix the two notch patch Status lines, the artifact board rows and the ticket's Artifact Links.
Run from the context_compass root:  python <this file> <NOW>"""
import pathlib
import sys

NOW = sys.argv[1]
TICKET = "tickets/tasks/2026-10-16_public_notch_target_for_staged_versions_task.md"
LANE = "system_docs/patches/active/public_notch_target_2026_10_16/"


def replace_once(path: pathlib.Path, old: str, new: str) -> None:
    """One exact replacement in an LF file."""
    text = path.read_text(encoding="utf-8")
    if text.count(old) != 1:
        raise SystemExit(f"{path}: {text.count(old)} occurrences of {old[:70]!r}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


replace_once(pathlib.Path(LANE + "component_patch_conduit_notch_target.md"),
             "- Status: built as patched and landed 0.2.8249 (2026-10-16); promoted into src_components (Conduit Runtime, SpellIndex\n"
             "  Mutation Surface, the notch flow) and src_architecture; archived\n",
             "- Status: built as patched (0.2.8249); promoted into src_components (Conduit Runtime, SpellIndex Mutation Surface,\n"
             "  the notch flow) and src_architecture; the lane is reopened for the index-move extension\n")
replace_once(pathlib.Path(LANE + "code_description_patch_conduit_notch_target.md"),
             "- Status: built as described and landed 0.2.8249 (2026-10-16); promoted into src_components (the notch flow) and\n"
             "  src_architecture (the invariant and failure modes); archived\n",
             "- Status: built as described (0.2.8249); promoted into src_components (the notch flow) and src_architecture (the\n"
             "  invariant and failure modes); the lane is reopened for the index-move extension\n")

board = pathlib.Path("artifact_board.md")
text = board.read_text(encoding="utf-8")
cleared = [line for line in text.split("\n")
           if line.startswith(f"| {TICKET} | system_docs/patches/completed/public_notch_target_2026_10_16/ |")]
assert len(cleared) == 1, len(cleared)
text = text.replace(cleared[0] + "\n", "", 1)
anchor = [line for line in text.split("\n") if line.startswith(f"| {TICKET} | artifacts/public_notch_target_20261016/ |")]
assert len(anchor) == 1, len(anchor)
rows = [
    (LANE + "architecture_patch.md", "Objective (option A), non-goals, the changed components with file owners, seven "
     "invariants (one target, owned and member, checked before admission and under the seal, valid calls unchanged, "
     "no new lock; the index moves by spell_id; spell_id wording), interface deltas, migration order, rollback, "
     "coverage matrix, risks; reopened for the owner's extension."),
    (LANE + "component_patch_conduit_notch_target.md", "`Conduit.notch_spell` before/after: `spell_id=`, "
     "`_resolve_notch_target`, `_owned_notch_target`, the refusals and their messages (spell_id wording); validation "
     "expectations."),
    (LANE + "code_description_patch_conduit_notch_target.md", "Control flow, the edge and error table, idempotency, "
     "why the check repeats inside the window, the residual cleanup_spell race, non-goals."),
    (LANE + "component_patch_conduit_index_move_target.md", "`add_to_spell_index` / `remove_from_spell_index` "
     "before/after: `spell_id=`, the shared argument check, `_owned_spell_by_id`, the docstrings, the seams' refusals "
     "kept; validation expectations (the owner's extension)."),
]
new_rows = "".join(f"| {TICKET} | {path} | patch_doc | active | promote_to_documentation | {note} | {NOW} | REQUIRED |\n"
                   for path, note in rows)
text = text.replace(anchor[0] + "\n", anchor[0] + "\n" + new_rows, 1)
board.write_text(text, encoding="utf-8")

replace_once(pathlib.Path(TICKET),
             "  - system_docs/patches/completed/public_notch_target_2026_10_16/ (the architecture, component and\n"
             "    code-description patches; promoted at landing 0.2.8249 and archived)\n",
             "  - system_docs/patches/active/public_notch_target_2026_10_16/architecture_patch.md\n"
             "  - system_docs/patches/active/public_notch_target_2026_10_16/component_patch_conduit_notch_target.md\n"
             "  - system_docs/patches/active/public_notch_target_2026_10_16/code_description_patch_conduit_notch_target.md\n"
             "  - system_docs/patches/active/public_notch_target_2026_10_16/component_patch_conduit_index_move_target.md\n")
print("statuses fixed; board: cleared row removed, 4 active rows added; ticket Artifact Links repointed")
