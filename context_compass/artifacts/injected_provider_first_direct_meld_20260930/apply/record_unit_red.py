"""
Record the unit tests' red run on the task ticket (MEASURE note, third step checked).

Usage: python record_unit_red.py <melder_private context_compass root>
"""
import datetime
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from apply_support import ApplySession

NOW = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
TASK = "tickets/tasks/2026-09-30_resolve_injected_provider_on_first_direct_meld_task.md"
FLAGS = "tests/unit/melder/spellbook/test_spellbook_creation_system_dependency_flags.py"
MELD = "tests/unit/melder/aether/conduit/meld/test_meld.py"
FAST = "tests/unit/melder/spellbook/test_spellbook_creation_system_resolution_fastpath.py"
RUNS = "context_compass/artifacts/injected_provider_first_direct_meld_20260930/runs"

session = ApplySession(sys.argv[1])
task = session._load(TASK)
updated = next(line for line in task.split("\n") if line.startswith("- Updated: "))
session.replace(TASK, updated + "\n", f"- Updated: {NOW}\n")
session.replace(
    TASK,
    "- [ ] Unit tests for the flag and the deferred lane, run red.",
    "- [x] Unit tests for the flag and the deferred lane, run red.",
)
note = (
    f"- DATETIME: {NOW}\n"
    "  TYPE: MEASURE\n"
    "  CLAIM: Unit tests written and red on 0.2.8214 (VM mirror, GIL off): the new flag file, test_meld.py and the\n"
    "    fastpath file together give 14 failed, 126 passed. Red as intended: 11 flag tests (no\n"
    "    SpellbookCreationSystem.flag_dependencies_without_own_plan yet, and the target pass flags nothing on\n"
    "    success) and 3 lane tests (a spell without a Phase 5 root still gets the 8-11 pass; a full pass that\n"
    "    leaves an invalid verdict or raises is never reached). Green guards: the two failure-path flag tests, the\n"
    "    existing-creation lane test, the four deferred-lane tests now pinned to a Phase 5 root, the whole fastpath\n"
    "    file with its stub's new _spell_id_pool.\n"
    "  EVIDENCE:\n"
    f"  - {FLAGS}:120-283\n"
    f"  - {MELD}:2100-2113\n"
    f"  - {MELD}:2258-2389\n"
    f"  - {FAST}:90-107\n"
    f"  - {RUNS}/unit_red.log:1-48\n"
    "  IMPACT: Every behaviour option B adds is pinned before the source edit; the fix is done when these 14 and\n"
    "    the 11 component regressions pass with the rest of the suites.\n"
    "  NEXT: Apply the source edits to the VM mirror (meld.py, spellbook_creation_system.py, the comments in\n"
    "    spellbook.py and creation_context_rebuild.py, __version__ 0.2.8215) and run the new tests green.\n"
    "  REREAD: REQUIRED\n"
    "  SCORE_0_TO_10: 9\n"
    "\n"
)
session.insert_before(TASK, "## Context / Handoff Summary\n", note)
task = session.texts[TASK]
start = task.index("## Context / Handoff Summary\n") + len("## Context / Handoff Summary\n")
end = task.index("\n## Project-Specific Additions", start)
session.texts[TASK] = task[:start] + (
    "Opened 2026-09-30T19:07:02Z on the owner's pick (option B, regression tests first). The component regression\n"
    "tests are red (11 failed at the direct service meld, 2 controls pass); patch docs and NOTICE M0-146..148 are\n"
    f"out; the unit tests are red ({NOW}). Next: the source edits in the VM mirror, green, then the\n"
    "device tree, suites, the epic's probe, docs, notch 0.2.8215, release note, rebuild.\n"
) + task[end:]
long_lines = session.long_added_lines()
if long_lines:
    raise SystemExit("long lines:\n" + "\n".join(long_lines))
print("written:", session.write(), NOW)
