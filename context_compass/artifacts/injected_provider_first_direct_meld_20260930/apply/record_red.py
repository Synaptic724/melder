"""
Record the regression tests' red run on the task ticket (MEASURE note, first step checked, validation lines).

Usage: python record_red.py <melder_private context_compass root>
"""
import datetime
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from apply_support import ApplySession

NOW = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
TASK = "tickets/tasks/2026-09-30_resolve_injected_provider_on_first_direct_meld_task.md"
TEST = "tests/component/melder/aether/conduit/test_conduit_component_injected_provider_direct_meld.py"
RUNS = "context_compass/artifacts/injected_provider_first_direct_meld_20260930/runs"

session = ApplySession(sys.argv[1])
text = session._load(TASK)
updated = next(line for line in text.split("\n") if line.startswith("- Updated: "))
session.replace(TASK, updated + "\n", f"- Updated: {NOW}\n")
session.replace(TASK, "- [ ] Regression tests over the matrix", "- [x] Regression tests over the matrix")
session.replace(
    TASK,
    "## Validation\n- Not run.\n- Recommended commands:\n  - recorded in the MEASURE notes as they run\n",
    "## Validation\n"
    f"- Red ({NOW}, VM mirror at 0.2.8214, Python 3.14.7 free-threaded, GIL off): the\n"
    "  regression file, 11 failed and 2 passed (the controls); every failure is the direct service meld.\n"
    "  Fix, suites and probe: not run yet.\n"
    "- Recommended commands:\n"
    "  - cd ~/wt2_new && timeout 170 python -X gil=0 -m pytest -q -p no:cacheprovider --tb=short \\\n"
    f"    {TEST}\n",
)
note = (
    f"- DATETIME: {NOW}\n"
    "  TYPE: MEASURE\n"
    "  CLAIM: The regression tests are written and red on 0.2.8214 (VM mirror, Python 3.14.7 free-threaded, GIL off):\n"
    "    13 cases in 11 functions, 11 failed and 2 passed. Every failure is the reported error - \"Cannot build\n"
    "    CreationContext before spell_codegen_creation exists.\" from CreationContextBuilder.build - raised by the\n"
    "    first direct service meld after a consumer meld that succeeded, in: a named lesser, an unnamed lesser, the\n"
    "    root, sibling lessers, a unique provider, a many provider, a root holding a spell at conjure, system caching\n"
    "    cold and warm, and the SpellSpace door with the consumer melded through the conduit or the space. The two\n"
    "    controls pass: the service melded before its consumer, and the pair bound before conjure. The cached cases\n"
    "    remove the conjure cache folders they wrote (none left in the mirror). No src change; no notch.\n"
    "  EVIDENCE:\n"
    f"  - {TEST}:52-172\n"
    f"  - {TEST}:174-286\n"
    f"  - {RUNS}/regression_red.log:25-37\n"
    f"  - {RUNS}/regression_red_tb_short.log:3-12\n"
    "  IMPACT: The SpellSpace door and a warm conduit bundle fail the same way, so the fix must serve both meld\n"
    "    doors and does not depend on the conjure cache; the controls pin that option B leaves the orders that\n"
    "    already worked unchanged.\n"
    "  NEXT: Re-read the fix's code path in full, then write the patch docs (architecture, meld runtime, compiler\n"
    "    target pass, deferred-lane code description) and send NOTICE M0-146..148.\n"
    "  REREAD: REQUIRED\n"
    "  SCORE_0_TO_10: 9\n"
    "\n"
)
session.insert_before(TASK, "## Context / Handoff Summary\n", note)
session.replace(
    TASK,
    "Opened 2026-09-30T19:07:02Z on the owner's pick (option B, regression tests first). Next: component regression "
    "tests over the\nreproduce task's matrix, run red; then patch docs, NOTICE, unit tests, the fix, green, docs, "
    "notch 0.2.8215,\nrelease note, rebuild.\n",
    "Opened 2026-09-30T19:07:02Z on the owner's pick (option B, regression tests first). The component regression\n"
    f"tests are written and red ({NOW}: 11 failed at the direct service meld, 2 controls\n"
    "pass). Next: patch docs, NOTICE M0-146..148, unit tests red, the fix, green, docs, notch 0.2.8215, release\n"
    "note, rebuild.\n",
)
long_lines = session.long_added_lines()
if long_lines:
    raise SystemExit("long lines:\n" + "\n".join(long_lines))
print("written:", session.write(), NOW)
