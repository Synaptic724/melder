"""Sync the artifact board and the ticket's Artifact Links after the patch lane public_notch_target_2026_10_16 moved
from system_docs/patches/active/ to completed/ (0.2.8249). Run from the context_compass root: python <this> <NOW>"""
import pathlib
import sys

NOW = sys.argv[1]
TICKET = "tickets/tasks/2026-10-16_public_notch_target_for_staged_versions_task.md"
BOARD = pathlib.Path("artifact_board.md")
ROW_PREFIX = f"| {TICKET} | system_docs/patches/active/public_notch_target_2026_10_16/"
CLEARED_MARK = "<!-- BEGIN USER-DEFINED: cleared_artifacts -->\n"
CLEARED_ROW = (
    f"| {TICKET} | system_docs/patches/completed/public_notch_target_2026_10_16/ | promote_to_documentation | "
    "Promoted at landing (0.2.8249) to src_architecture, src_components, tests_components and tests_architecture with "
    "their indexes, and to the graph; the three patch docs (architecture, component, code-description) archived. "
    f"| {NOW} |\n"
)

text = BOARD.read_text(encoding="utf-8")
lines = text.split("\n")
kept = [line for line in lines if not line.startswith(ROW_PREFIX)]
assert len(lines) - len(kept) == 3, len(lines) - len(kept)
text = "\n".join(kept)
assert text.count(CLEARED_MARK) == 1
text = text.replace(CLEARED_MARK, CLEARED_MARK + CLEARED_ROW, 1)
BOARD.write_text(text, encoding="utf-8")

ticket = pathlib.Path(TICKET)
body = ticket.read_text(encoding="utf-8")
old = (
    "  - system_docs/patches/active/public_notch_target_2026_10_16/architecture_patch.md\n"
    "  - system_docs/patches/active/public_notch_target_2026_10_16/component_patch_conduit_notch_target.md\n"
    "  - system_docs/patches/active/public_notch_target_2026_10_16/code_description_patch_conduit_notch_target.md\n"
)
new = (
    "  - system_docs/patches/completed/public_notch_target_2026_10_16/ (the architecture, component and\n"
    "    code-description patches; promoted at landing 0.2.8249 and archived)\n"
)
assert body.count(old) == 1
ticket.write_text(body.replace(old, new, 1), encoding="utf-8")
print("artifact board: 3 active patch rows removed, 1 cleared row added; ticket Artifact Links repointed")
