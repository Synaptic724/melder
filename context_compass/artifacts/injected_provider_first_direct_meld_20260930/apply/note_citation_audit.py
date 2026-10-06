"""
Record the citation audit that precedes the docs pass (FACT note on the task).

Usage: python note_citation_audit.py <melder_private context_compass root>
"""
import datetime
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from apply_support import ApplySession

NOW = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
TASK = "tickets/tasks/2026-09-30_resolve_injected_provider_on_first_direct_meld_task.md"
session = ApplySession(sys.argv[1])
task = session._load(TASK)
updated = next(line for line in task.split("\n") if line.startswith("- Updated: "))
session.replace(TASK, updated + "\n", f"- Updated: {NOW}\n")
note = (
    f"- DATETIME: {NOW}\n"
    "  TYPE: FACT\n"
    "  CLAIM: Citation audit before the docs pass: the system docs cite line numbers in three files this lane\n"
    "    changed. The landing shifts spellbook.py by +2 after line 3811 and +6 after 5392, spellbook_creation_system.py\n"
    "    by +6/+11/+83 after 1667/1753/1825, and meld.py by up to +67 after 1019 - but most spellbook.py and meld.py\n"
    "    citations were already stale at 0.2.8214 (2 to 14 lines, and meld.py's \"every self._lock site\" ranges no\n"
    "    longer held its lock sites). Checked by symbol against the landed files: the notch, add and remove entries\n"
    "    and seams (3650/3701/3843/3876/4019/4051), the admits comment (3686), _conjured reads (667, 725),\n"
    "    _settle_or_inherit_conjure_mode (6516-6559), conjure's effective-mode line (6772), _run_structural_phases\n"
    "    (7135, precondition 7146), the cache-emit re-check (1055-1066), the configuration-mismatch log (5615-5621),\n"
    "    bind (5176-5188), the conduit property (6448); _run_scheduler_with_phases (2055, its lock 2083); meld.py lock\n"
    "    sites (276, 377, 1481-1679), the dirty-root raise (1167-1175), _gated_validation_required (1134).\n"
    "    Citations into untouched regions (spellbook_creation_system.py 242-260, 517-544, 616-723, 1253-1292) hold.\n"
    "  EVIDENCE:\n"
    "  - system_docs/src_architecture.md:428-442\n"
    "  - system_docs/src_architecture.md:1272-1332\n"
    "  - system_docs/src_components.md:458-468\n"
    "  - system_docs/src_components.md:528-548\n"
    "  - system_docs/src_components.md:3326-3331\n"
    "  - src/melder/aether/spellbook/spellbook.py:3650-4136\n"
    "  - src/melder/aether/spellbook/spellbook.py:6516-6559\n"
    "  - src/melder/aether/spellbook/spellbook_creation_system.py:2054-2096\n"
    "  - src/melder/aether/conduit/meld/meld.py:1134-1204\n"
    "  IMPACT: The docs pass remeasures every citation into the touched files, not only the ones this landing\n"
    "    moved; citations into other files stay out of scope.\n"
    "  NEXT: Apply the docs pass to src_architecture, src_components and tests_components and regenerate their\n"
    "    indexes.\n"
    "  REREAD: HELPFUL\n"
    "  SCORE_0_TO_10: 8\n"
    "\n"
)
session.insert_before(TASK, "## Context / Handoff Summary\n", note)
long_lines = [line for line in session.long_added_lines() if ": |" not in line]
if long_lines:
    raise SystemExit("long lines:\n" + "\n".join(long_lines))
print("written:", session.write(), NOW)
