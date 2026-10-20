"""Rule 2 test change: mark the meld-vs-notch race test xfail(strict=False), naming the owner's follow-up task (melder_1).

The owner split the race off rule 2 (2026-10-16): it predates rule 2 at the same rate and is
TASK-2026-10-16-order_inflight_borrower_melds_against_notch_fanout. Not strict: the race passes in most runs.
`raises=AssertionError` keeps any other failure of the test a failure.
usage: python <this script> <root> <relative path of test_conduit_integration_notch_revalidation.py> [--check]
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from apply_lib import apply

ROOT = pathlib.Path(sys.argv[1])
REL = sys.argv[2]
CHECK = "--check" in sys.argv[3:]

TEST_DEF = ("def test_melds_racing_notches_get_a_version_or_the_lost_provider_refusal_and_end_on_the_last_version() "
            "-> None:\n")

STEPS = [
    ("one",
     TEST_DEF,
     '''@pytest.mark.xfail(
    strict=False,
    raises=AssertionError,
    reason=(
        "OPEN, intermittent with the GIL off: a meld in flight while the lender's notch parks or reactivates the "
        "borrower's contracted copy can be built with the raw SpellContract default (AttributeError when it is "
        "used) or raise an internal RuntimeError ('many_only manifest references unknown spell_id', 'Cannot build "
        "CreationContext ...'), because the notch's fan-out runs after its transaction ends. It predates rule 2 at "
        "the same rate. TASK-2026-10-16-order_inflight_borrower_melds_against_notch_fanout. NOT STRICT: the race "
        "passes in most runs; whoever closes that task deletes this marker."
    ),
)
''' + TEST_DEF, ""),
]

apply(ROOT, REL, STEPS, CHECK)
