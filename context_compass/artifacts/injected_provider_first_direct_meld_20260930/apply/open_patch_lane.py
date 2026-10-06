"""
Write the lane's patch docs, claim its files by NOTICE (M0-146..148) and record the mapping on the task.

Usage: python open_patch_lane.py <melder_private context_compass root>
Creates system_docs/patches/active/injected_provider_first_direct_meld_2026_09_30/ from ./patch_docs, appends a PLAN
note (patch section -> implementation -> validation), syncs the task, attention, artifact and mailbox boards.
"""
import datetime
import difflib
import pathlib
import sys
from typing import List

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from apply_support import ApplySession

HERE = pathlib.Path(__file__).parent
NOW = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
PATCH_ID = "injected_provider_first_direct_meld_2026_09_30"
PATCH_DIR = f"system_docs/patches/active/{PATCH_ID}"
TASK = "tickets/tasks/2026-09-30_resolve_injected_provider_on_first_direct_meld_task.md"
BOARD = "attention_board.md"
ARTIFACTS = "artifact_board.md"
MAILBOX = "mailbox_board.md"
DOCS = [
    "architecture_patch.md",
    "component_patch_spellcompiler_target_pass.md",
    "component_patch_meld_resolution_runtime.md",
    "code_description_patch_first_direct_meld.md",
]

session = ApplySession(sys.argv[1])
line_counts = {}
for name in DOCS:
    text = (HERE / "patch_docs" / name).read_text(encoding="utf-8").replace("@NOW@", NOW)
    session.create(f"{PATCH_DIR}/{name}", text)
    line_counts[name] = text.count("\n")

task = session._load(TASK)
updated = next(line for line in task.split("\n") if line.startswith("- Updated: "))
session.replace(TASK, updated + "\n", f"- Updated: {NOW}\n")
session.replace(TASK, "- [ ] Patch docs and the mailbox NOTICE.", "- [x] Patch docs and the mailbox NOTICE.")
session.replace(
    TASK,
    "- src/melder/aether/spellbook/spellbook_creation_system.py, src/melder/aether/conduit/meld/meld.py,\n"
    "  src/melder/__version__.py; tests (new component regressions, unit tests); system docs, graph descriptors,\n"
    "  release note.\n",
    "- src/melder/aether/spellbook/spellbook_creation_system.py and src/melder/aether/conduit/meld/meld.py (logic);\n"
    "  src/melder/aether/spellbook/spellbook.py and\n"
    "  src/melder/aether/conduit/meld/creation_context/creation_context_rebuild.py (comments that state the old lane\n"
    "  rule); src/melder/__version__.py.\n"
    "- tests/component/melder/aether/conduit/test_conduit_component_injected_provider_direct_meld.py (new),\n"
    "  tests/unit/melder/spellbook/test_spellbook_creation_system_dependency_flags.py (new),\n"
    "  tests/unit/melder/aether/conduit/meld/test_meld.py and\n"
    "  tests/unit/melder/spellbook/test_spellbook_creation_system_resolution_fastpath.py (updated).\n"
    "- System docs, graph descriptors, release note.\n",
)
session.replace(
    TASK,
    "  - artifacts/injected_provider_direct_meld_20260930/\n- DISPOSITION: retain_as_reference\n",
    "  - artifacts/injected_provider_direct_meld_20260930/\n"
    f"  - {PATCH_DIR}/\n"
    "- DISPOSITION: retain_as_reference (the two artifact folders); promote_to_documentation (the patch docs, at\n"
    "  landing).\n",
)
evidence = "\n".join(f"  - {PATCH_DIR}/{name}:1-{line_counts[name]}" for name in DOCS)
note = (
    f"- DATETIME: {NOW}\n"
    "  TYPE: PLAN\n"
    "  CLAIM: Patch docs written (patch id below) and read in order (architecture, the two component patches, the\n"
    "    code description); NOTICE M0-146..148 claims the lane's files. Mapping, patch section -> implementation ->\n"
    "    validation: (1) target pass tail -> new static SpellbookCreationSystem.flag_dependencies_without_own_plan,\n"
    "    called on the success path of run_resolution_phases_for_target_spell after the scoped cleanup -> a new unit\n"
    "    file (flag and skip matrix, the write under the dependency's lock, called on success only), and the fastpath\n"
    "    stub gains the _spell_id_pool the success path now reads; (2) deferred lane routing and the code description\n"
    "    -> Meld._ensure_runtime_resolution_ready sends a spell that is neither an existing creation nor its Phase 5\n"
    "    root through the full pass and checks its verdict -> four new lane tests in test_meld.py, and its two\n"
    "    deferred-lane tests make their spell a Phase 5 root; (3) the invariants -> the component regression file\n"
    "    (red) turns green, then the epic's probe. Comment-only edits where a comment gives \"the deferred lane cannot\n"
    "    compile it\" as a reason: spellbook.py (notch and bind) and creation_context_rebuild.py.\n"
    "  EVIDENCE:\n"
    f"{evidence}\n"
    "  - src/melder/aether/spellbook/spellbook.py:3804-3813\n"
    "  - src/melder/aether/spellbook/spellbook.py:5390-5393\n"
    "  - src/melder/aether/conduit/meld/creation_context/creation_context_rebuild.py:140-169\n"
    "  IMPACT: Four src files - two with logic, two with comments only - each change mapped to a patch section and a\n"
    "    test; nothing outside the declared boundary (no verdict, RiskManager or public API change).\n"
    "  NEXT: Write the unit tests for the flag helper and the deferred lane, and run them red in the VM mirror.\n"
    "  REREAD: REQUIRED\n"
    "  SCORE_0_TO_10: 9\n"
    "\n"
)
session.insert_before(TASK, "## Context / Handoff Summary\n", note)
session.replace(
    TASK,
    "pass). Next: patch docs, NOTICE M0-146..148, unit tests red, the fix, green, docs, notch 0.2.8215, release\n"
    "note, rebuild.\n",
    f"pass). Patch docs and NOTICE M0-146..148 at {NOW}. Next: unit tests red, the fix, green, docs, notch\n"
    "0.2.8215, release note, rebuild.\n",
)

board = session._load(BOARD)
row_start = board.index("| injected_dependency_direct_resolution | in_progress |")
row_end = board.index("\n", row_start)
row = board[row_start:row_end]
cells = row.split(" | ")
cells[6] = ("Write the unit tests for the flag helper and the deferred lane and run them red, then implement "
            "option B.")
cells[10] = NOW
session.replace(BOARD, row, " | ".join(cells))
recipients = [("fable_0", "M0-146"), ("muse_0", "M0-147"), ("melder_2", "M0-148")]
alerts = "".join(f"- NEW MESSAGE for {name} (from melder_0, {NOW})\n" for name, _ in recipients)
session.insert_before(BOARD, "<!-- END USER-DEFINED: alerts -->", alerts)

session.insert_after(
    ARTIFACTS,
    "<!-- BEGIN USER-DEFINED: active_artifacts -->\n",
    f"| {TASK} | {PATCH_DIR}/ | patch_doc | active | promote_to_documentation | Architecture, target-pass and "
    "meld-runtime component patches and the first-direct-meld code description; promote at landing. "
    f"| {NOW} | REQUIRED |\n",
)

messages = ""
for name, message_id in recipients:
    messages += (
        f"- TO: {name}\n"
        "  FROM: melder_0\n"
        f"  DATETIME: {NOW}\n"
        "  TYPE: NOTICE\n"
        f"  CLAIM: {message_id}. Owner-directed lane (option B of the injected-provider epic, 2026-09-30): a spell\n"
        "    bound after conjure and first built as a consumer's dependency must meld directly afterwards. melder_0 is\n"
        "    the only writer until the lane closes of src/melder/aether/conduit/meld/meld.py (the deferred lane),\n"
        "    spellbook/spellbook_creation_system.py (the target pass tail), the comments stating the old lane rule in\n"
        "    spellbook.py and creation_context_rebuild.py, and the lane's tests. __version__ 0.2.8214 -> 0.2.8215 at\n"
        "    landing; notch above it if you land src after. Tell melder_0 before editing those files.\n"
        f"  EVIDENCE: context_compass/{TASK}\n"
        "  ACK_REQUESTED: false\n"
    )
session.insert_before(MAILBOX, "<!-- END USER-DEFINED: messages -->", messages)
mailbox = session._load(MAILBOX)
row = next(line for line in mailbox.split("\n") if line.startswith("| melder_0 | claude | 2026-09-26T22:24:06Z |"))
cells = row.split(" | ")
cells[3] = NOW
session.replace(MAILBOX, row, " | ".join(cells))

long_lines: List[str] = [
    line for line in session.long_added_lines()
    if ": |" not in line and not line.split(": ", 2)[2].lstrip().startswith("- system_docs/")
]
for relative in session.created:
    for number, line in enumerate(session.texts[relative].split("\n"), 1):
        if len(line) > 120 and len(line.split()) > 1 and not line.startswith("|"):
            long_lines.append(f"{relative}:{number}: {len(line)}")
if long_lines:
    raise SystemExit("long lines:\n" + "\n".join(long_lines))
print("written:", session.write(), NOW)
