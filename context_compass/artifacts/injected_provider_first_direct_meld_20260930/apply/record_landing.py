"""
Record option B's landing (0.2.8215): implementation and validation note, steps, landing NOTICE M0-149..151.

Usage: python record_landing.py <melder_private context_compass root> <landing time>
"""
import datetime
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from apply_support import ApplySession

NOW = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
LANDED = sys.argv[2]
TASK = "tickets/tasks/2026-09-30_resolve_injected_provider_on_first_direct_meld_task.md"
BOARD = "attention_board.md"
MAILBOX = "mailbox_board.md"
RUNS = "context_compass/artifacts/injected_provider_first_direct_meld_20260930/runs"
PROBE = "context_compass/artifacts/injected_provider_direct_meld_20260930/runs_0_2_8215"

session = ApplySession(sys.argv[1])
task = session._load(TASK)
updated = next(line for line in task.split("\n") if line.startswith("- Updated: "))
session.replace(TASK, updated + "\n", f"- Updated: {NOW}\n")
session.replace(
    TASK,
    "- [ ] Implement B (target-pass tail flags; the deferred lane runs the full pass without a Phase 5 root).",
    "- [x] Implement B (target-pass tail flags; the deferred lane runs the full pass without a Phase 5 root).",
)
session.replace(
    TASK,
    "- [ ] Green: new tests, meld, spellbook, conduit and aether suites; the epic's probe.",
    "- [x] Green: new tests, meld, spellbook, conduit and aether suites; the epic's probe.",
)
session.replace(
    TASK,
    "  Fix, suites and probe: not run yet.\n",
    f"- Green ({NOW}, VM mirror at 0.2.8215): the 153 new and touched tests with GIL off and on; the full suite\n"
    "  13287 passed, 32 skipped, 12 xfailed, 2 xpassed (pre-existing), 1 failed (the build-asset stamp, refreshed\n"
    "  by the rebuild at the end); the epic's probe passes in every variant (runs_0_2_8215/).\n",
)
note = (
    f"- DATETIME: {NOW}\n"
    "  TYPE: MEASURE\n"
    f"  CLAIM: Option B landed on the device tree at {LANDED}, byte-identical to the VM mirror where it was\n"
    "    validated; __version__ 0.2.8214 -> 0.2.8215 (read at landing). flag_dependencies_without_own_plan runs on\n"
    "    the success path of run_resolution_phases_for_target_spell; _ensure_runtime_resolution_ready sends a\n"
    "    flagged spell that is neither an existing creation nor its Phase 5 root through the full target pass and\n"
    "    checks its verdict (_requires_own_target_pass, _raise_unless_resolution_valid); the comments in\n"
    "    spellbook.py and creation_context_rebuild.py no longer give the old lane as a reason. Green in the VM\n"
    "    (3.14.7t): the 153 new and touched tests with GIL off and on; the full suite in six runs, 13287 passed,\n"
    "    32 skipped, 12 xfailed, 2 xpassed (both pre-existing Fault B xpasses), 1 failed -\n"
    "    test_generated_build_assets_are_stamped_for_the_live_version, the stamp the final rebuild refreshes. The\n"
    "    epic's probe on 0.2.8215 passes every variant (diagnostic with cache off, cold and warm; resident; root;\n"
    "    unnamed lesser; unique; many; siblings isolated; both controls): after the consumer meld the provider\n"
    "    reads resolution_required True with no plan, and its direct meld returns the consumer's instance.\n"
    "  EVIDENCE:\n"
    "  - src/melder/aether/spellbook/spellbook_creation_system.py:1654-1765\n"
    "  - src/melder/aether/spellbook/spellbook_creation_system.py:1838-1908\n"
    "  - src/melder/aether/conduit/meld/meld.py:966-1086\n"
    "  - src/melder/aether/spellbook/spellbook.py:3804-3815\n"
    "  - src/melder/aether/spellbook/spellbook.py:5392-5399\n"
    "  - src/melder/aether/conduit/meld/creation_context/creation_context_rebuild.py:140-173\n"
    f"  - {RUNS}/green_new_tests_vm.log:1-4\n"
    f"  - {RUNS}/green_new_tests_vm_gil1.log:1-12\n"
    f"  - {RUNS}/suite_unit_rest_vm.log:1-41\n"
    f"  - {PROBE}/diagnostic_cacheoff.txt:1-1\n"
    "  IMPACT: The epic's diagnostic passes on source; what remains is the system docs, the graph, the release\n"
    "    note and the rebuild, which also clears the one stamp failure.\n"
    "  NEXT: Promote the patch docs into src_architecture, src_components and tests_components, update the graph\n"
    "    descriptors and the release note, then rebuild the assets and LLM bundles.\n"
    "  REREAD: REQUIRED\n"
    "  SCORE_0_TO_10: 9\n"
    "\n"
)
session.insert_before(TASK, "## Context / Handoff Summary\n", note)
task = session.texts[TASK]
start = task.index("## Context / Handoff Summary\n") + len("## Context / Handoff Summary\n")
end = task.index("\n## Project-Specific Additions", start)
session.texts[TASK] = task[:start] + (
    "Opened 2026-09-30T19:07:02Z on the owner's pick (option B, regression tests first). Regression and unit\n"
    f"tests went red, then green; option B landed at {LANDED} as 0.2.8215 (NOTICE M0-149..151), the full suite\n"
    "and the epic's probe green in the VM. Next: system docs, graph descriptors, release note, then the asset and\n"
    "LLM bundle rebuild last; then review for the owner's turn-in.\n"
) + task[end:]

board = session._load(BOARD)
row_start = board.index("| injected_dependency_direct_resolution | in_progress |")
row_end = board.index("\n", row_start)
row = board[row_start:row_end]
cells = row.split(" | ")
cells[6] = ("Promote the patch docs into the system docs, update the graph and the release note, then rebuild "
            "assets and LLM bundles.")
cells[10] = NOW
session.replace(BOARD, row, " | ".join(cells))
recipients = [("fable_0", "M0-149"), ("muse_0", "M0-150"), ("melder_2", "M0-151")]
alerts = "".join(f"- NEW MESSAGE for {name} (from melder_0, {NOW})\n" for name, _ in recipients)
session.insert_before(BOARD, "<!-- END USER-DEFINED: alerts -->", alerts)
messages = ""
for name, message_id in recipients:
    messages += (
        f"- TO: {name}\n"
        "  FROM: melder_0\n"
        f"  DATETIME: {NOW}\n"
        "  TYPE: NOTICE\n"
        f"  CLAIM: {message_id}. Option B is on the tree ({LANDED}) and __version__ 0.2.8214 -> 0.2.8215 (read at\n"
        "    landing): a target-local pass flags the owned dependencies it compiled without a plan of their own\n"
        "    (resolution_required), and the deferred lane runs the full target pass for a spell that is not its\n"
        "    Phase 5 root, so a provider bound after conjure melds directly after injection. Files: meld.py,\n"
        "    spellbook_creation_system.py, comments in spellbook.py and creation_context_rebuild.py. Docs, graph,\n"
        "    release note and assets follow; melder_0 stays sole writer of M0-146..148's files. Notch above 0.2.8215.\n"
        f"  EVIDENCE: context_compass/{TASK}\n"
        "  ACK_REQUESTED: false\n"
    )
session.insert_before(MAILBOX, "<!-- END USER-DEFINED: messages -->", messages)
mailbox = session._load(MAILBOX)
row = next(line for line in mailbox.split("\n") if line.startswith("| melder_0 | claude | 2026-09-26T22:24:06Z |"))
cells = row.split(" | ")
cells[3] = NOW
session.replace(MAILBOX, row, " | ".join(cells))
long_lines = [line for line in session.long_added_lines() if ": |" not in line]
if long_lines:
    raise SystemExit("long lines:\n" + "\n".join(long_lines))
print("written:", session.write(), NOW)
