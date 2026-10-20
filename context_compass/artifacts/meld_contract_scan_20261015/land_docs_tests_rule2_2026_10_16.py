"""Catalogue rule 2's tests (0.2.8250) in tests_components and recount tests_architecture (melder_1, 2026-10-16).

contract_recheck_on_notch_2026_10_16. Two new test modules (the registry's downstream walk; contract consumers and
dependents following a provider change), nine changed ones, recounted tier and subtree counts, the core set.
usage (from the repository root): python <this script> <UTC timestamp> [--check]
Exact-text edits through the rule-2 docs lib; each anchor must occur once; line endings kept.
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from land_docs_src_architecture_rule2_2026_10_16_lib import apply  # long-line-aware exact-text apply

TS = sys.argv[1]
CHECK = "--check" in sys.argv[2:]
ROOT = pathlib.Path(".")
TC = "context_compass/system_docs/tests_components.md"
TA = "context_compass/system_docs/tests_architecture.md"
WALK = "tests/unit/melder/aether/dev_ops/spell_system_states/test_spell_system_states_dependent_walk.py"
NOTCH = "tests/integration/melder/conduit/test_conduit_integration_notch_revalidation.py"
TASK = "TASK-2026-10-16-order_inflight_borrower_melds_against_notch_fanout"

UNIT_SUITE_OLD = (
    "- the public notch target (0.2.8249): `notch_spell` resolving a version id through the Book, passing an owned\n"
    "  `spell` through, and refusing every malformed or foreign target with nothing started, the in-window re-check\n"
    "  included (see `### Subcomponent: Spellbook Runtime And Binding Unit Cluster`)\n"
)
UNIT_SUITE_NEW = UNIT_SUITE_OLD + (
    "- contract consumers and dependents following a provider change (0.2.8250): the registry's downstream walk from\n"
    "  a notch and from every contract mark (see `### Subcomponent: DevOps Control Plane Unit Cluster`); the borrower\n"
    "  Book's contract marks and the meld gate without the per-meld contract scan, with its catch-up of stale\n"
    "  dependencies (see `### Subcomponent: Spellbook Runtime And Binding Unit Cluster`); and the lost-provider\n"
    "  report, Phase 4's warning (see `### Subcomponent: Spellbook Compiler Unit Cluster`) shown as the spell's\n"
    "  reason (see `### Subcomponent: Utilities Unit Cluster`)\n"
)
INT_SUITE_OLD = (
    "- the public notch target (0.2.8249): the stage -> notch -> meld loop and its revert by version id in real worlds,\n"
    "  and every foreign target refused with both indexes intact (see `### Subcomponent: Spellbook Integration Cluster`)\n"
)
INT_SUITE_NEW = INT_SUITE_OLD + (
    "- contract consumers and dependents following a provider change (0.2.8250): a borrower's contract consumer\n"
    "  follows its lender's notches with one rebuild each or fails as a first meld would, a lost provider is named\n"
    "  with its remedy, a version grant comes back on a notch back, and dependents one and two hops from a notched\n"
    "  spell, in its Book or across Books, build the new version (see\n"
    "  `### Subcomponent: Conduit Integration Cluster`)\n"
)
DEVOPS_PURPOSE_OLD = "  on a real `SpellSystemStates` registry rather than a stub\nProtects:\n"
DEVOPS_PURPOSE_NEW = (
    "  on a real `SpellSystemStates` registry rather than a stub\n"
    "- verify the registry's downstream walk from a notch and from every contract mark (0.2.8250), on the same real\n"
    "  registry\n"
    "Protects:\n"
)
DEVOPS_PROTECTS_OLD = (
    "  flag once; the registry stub of `test_risk_manager.py` answers an empty set, so its 21 tests keep their meaning\n"
    "Key Files (C1):\n"
)
DEVOPS_PROTECTS_NEW = (
    "  flag once; the registry stub of `test_risk_manager.py` answers an empty set, so its 21 tests keep their meaning\n"
    "- the downstream walk (0.2.8250; `test_spell_system_states_dependent_walk.py`, 17 tests): a walk from a lineage\n"
    "  marks the chain downstream of it by edge (`impacted_by_dependency`, transitively dirty) and never the seed; a\n"
    "  SpellContract consumer, in any Book, of a reached lineage's binding key gets the contract mark (`gated` +\n"
    "  `contract_unvalidated`) and its own dependents the edge mark; a lineage reached both ways carries both; one\n"
    "  with no recorded key is followed by edge only; a contract cycle across Books marks each lineage once; a\n"
    "  dependent with no registered state is passed over; empty seeds mark and publish nothing; a walk publishes\n"
    "  `gated` once per marked lineage, a second walk nothing, and adds every marked lineage to the dirty worklist;\n"
    "  `register_index` keeps the recorded key when given none and replaces it when given one, and\n"
    "  `unregister_index` and cleanup drop it; `mark_contract_dependents_dirty` walks on from the consumers it marks\n"
    "  and returns only them; and a walk on a cleaned registry raises the use-after-clean RuntimeError\n"
    "Key Files (C1):\n"
)
DEVOPS_KEYS_OLD = "- `tests/unit/melder/aether/dev_ops/risk_manager/test_risk_manager_non_resolvable.py` (2026-10-16)\n"
DEVOPS_KEYS_NEW = DEVOPS_KEYS_OLD + f"- `{WALK}` (2026-10-16)\n"
SB_UNIT_OLD = (
    "  automatic conduit raises the dynamic-mode RuntimeError before the Book is asked\n"
    "Key Files (C1):\n"
    "- `tests/unit/melder/spellbook/test_spellbook.py`\n"
)
SB_UNIT_NEW = (
    "  automatic conduit raises the dynamic-mode RuntimeError before the Book is asked\n"
    "- the borrower Book's contract marks (0.2.8250; six tests in `test_spellbook.py`): an add, a park, a\n"
    "  reactivation and a removal of an active contracted copy, and a clear of a peer's copies (by the key each\n"
    "  active copy is filed under), each mark the Book's consumers of the copy's key (`gated` +\n"
    "  `contract_unvalidated`); a parked copy's change and any change before conjure mark nothing; each mutator marks\n"
    "  once, after it releases the Book lock; a mark that raises is logged and propagates with the map change left\n"
    "  published\n"
    "- the meld gate and its catch-up (0.2.8250; the aether tree's `test_meld.py`, 97 tests): a `valid` contract\n"
    "  consumer melds with no contract lookup, verdict write or 5-11 pass; a marked consumer whose provider is\n"
    "  present reruns its structure and rebuilds once (`structure_changed`), and one whose provider is gone raises\n"
    "  SpellbookValidationError - three tests that replace the retired per-meld scan's five; before a spell\n"
    "  compiles, the catch-up refreshes each stale dependency its plan expands with the dependency's owner Book,\n"
    "  under its rebuild window and then its lock, and resets that dependency's plan (an existing creation's\n"
    "  excepted); it takes a recorded target to its lineage's current version, follows a contract socket through\n"
    "  the Book's active copy, walks a refreshed dependency's new topology, refreshes a shared dependency once,\n"
    "  rechecks staleness under the lock and holds no lock while it walks; it leaves a `valid` dependency alone,\n"
    "  raises SpellbookValidationError naming a broken dependency (pinned `invalid`) or one left gated, and does not\n"
    "  walk for a spell that will not compile; the deferred lane runs it before its pass and the gate leaves it to\n"
    "  that lane\n"
    "Key Files (C1):\n"
    "- `tests/unit/melder/spellbook/test_spellbook.py`\n"
)
COMPILER_OLD = "  holder may hold it (`test_scope_ordering_strategy.py`)\nKey Files (C1):\n"
COMPILER_NEW = (
    "  holder may hold it (`test_scope_ordering_strategy.py`)\n"
    "- the lost-provider warning (0.2.8250): Phase 4's presence check names the contract key and the remedy -\n"
    "  contract one from a linked conduit (`add_index_to_contract`, or `add_spell_to_contract` for one version) and\n"
    "  meld again (`test_contract_provider_presence_strategy.py`); Phase 4 gates a lineage on exactly the warnings\n"
    "  the validation report lists as a spell's reason, and a warning the report only counts leaves it valid\n"
    "  (`test_compiler_phase_4.py`)\n"
    "Key Files (C1):\n"
)
UTIL_OLD = "  trailing zeros, the two ways out - caught as a `MeldExecutionError`, with no inner cause\nKey Files (C1):\n"
UTIL_NEW = (
    "  trailing zeros, the two ways out - caught as a `MeldExecutionError`, with no inner cause\n"
    "- the lost-provider reason (0.2.8250; five tests in `test_spellbook_validation_error.py`): a spell whose lineage\n"
    "  a gating Phase-4 warning holds lists that warning as its reason instead of \"No validation error was\n"
    "  recorded\"; other warnings stay counted beside it; the warning joins the hidden count when the spell shows\n"
    "  errors; a spell with only that reason is still listed when conduit diagnostics are given; and\n"
    "  `GATING_WARNING_CODES` is exactly `SPELL_CONTRACT_MISSING_PROVIDER`\n"
    "Key Files (C1):\n"
)
SB_COMP_OLD = "  five transaction modes\nKey Files (C1):\n"
SB_COMP_NEW = (
    "  five transaction modes\n"
    "- the structural snapshot's notch event (0.2.8250; `test_spellbook_component_structural_snapshot_parity.py`):\n"
    "  cold and hydrated worlds still end alike through a notch, now both recording the first meld's\n"
    "  UnresolvedInputError after a notch to a class `engine: Engine` does not select, and building with Engine\n"
    "  after the notch back\n"
    "Key Files (C1):\n"
)
CONDUIT_OLD = "  notched in stores its object in the target\nKey Files (C1):\n"
CONDUIT_NEW = (
    "  notched in stores its object in the target\n"
    "- contract consumers and dependents following a provider change (0.2.8250;\n"
    "  `test_conduit_integration_notch_revalidation.py`, 16 tests): a borrower's contract consumer follows its\n"
    "  lender's notch, notch back and repeat notch with one 5-11 pass each and none on warm melds, an object built\n"
    "  before keeping its provider; a notch marks the consumer and builds nothing; a `unique` consumer keeps its\n"
    "  object and builds the new version after a purge; a notch to an unresolvable version raises the first meld's\n"
    "  UnresolvedInputError and the notch back recovers; an index destroy, an index uncontract and a version\n"
    "  uncontract fail the consumer with SpellbookValidationError naming the contract and its remedy; a notch back\n"
    "  makes a parked version grant active again (one pass; a linked peer that never borrowed it gains nothing), and\n"
    "  a grant of a parked version becomes active when the lender notches to it; dependents one and two hops from a\n"
    "  notched dependency build its new version whichever end melds first, or raise the first meld's error when the\n"
    "  annotation does not select it; a contract consumer's dependent compiled before the link resolves the linked\n"
    "  provider; a dependency notch in the lending Book reaches the borrower's dependents; and four threads melding\n"
    "  against 20 notches, held as a non-strict xfail until\n"
    f"  {TASK} (see `tests_architecture`)\n"
    "Key Files (C1):\n"
)
CONDUIT_KEYS_OLD = "- `tests/integration/melder/conduit/test_conduit_integration_managed_transfer.py` (2026-10-15)\n"
CONDUIT_KEYS_NEW = CONDUIT_KEYS_OLD + f"- `{NOTCH}` (2026-10-16)\n"
MT_OLD = "  once the contract returns\nKey Files (C1):\n"
MT_NEW = (
    "  once the contract returns\n"
    "- the explicit mark (0.2.8250): with the per-meld contract scan retired, a warm meld of a satisfied consumer no\n"
    "  longer compiles, so each mid-resolution test marks the consumer as a provider change does\n"
    "  (`mark_contract_dependents_dirty`) before its forced meld\n"
    "Key Files (C1):\n"
)


def record(path: str, end: int, ts: str, note: str = "") -> str:
    """One code-map record in the document's five-field shape, with an optional note."""
    text = f"- path: `{path}`\n  start_line: 1\n  end_line: {end}\n  loc: {end}\n  verified_at: {ts}\n"
    return text + (f"  note: {note}\n" if note else "")


SB_REC_OLD = record("tests/unit/melder/spellbook/test_spellbook.py", 5288, "2026-10-16T01:19:21Z")
SB_REC_NEW = record("tests/unit/melder/spellbook/test_spellbook.py", 5511, TS)
CSB_REC_OLD = record("tests/component/melder/spellbook/test_spellbook_component_spellbook.py", 1713,
                     "2026-10-16T01:19:21Z")
CSB_REC_NEW = record("tests/component/melder/spellbook/test_spellbook_component_spellbook.py", 1715, TS)
SVE = "tests/unit/melder/utilities/custom_exceptions/test_spellbook_validation_error.py"
SVE_REC_OLD = record(SVE, 326, "2026-09-26T22:11:36Z")
SVE_REC_NEW = record(SVE, 404, TS, "the conjure validation report; a gating warning shown as a spell's reason (0.2.8250).")
MR = "tests/integration/melder/multithreading/test_contract_mutation_during_meld_resolution_integration.py"
MR_REC_OLD = record(MR, 325, "2026-10-10T09:33:01Z", "a contract mutation forced inside a meld's resolution pass (0.2.8227).")
MR_REC_NEW = record(MR, 353, TS, "a contract mutation forced inside a meld's resolution pass (0.2.8227); the consumer is\n"
                    "    marked before the forced meld (0.2.8250).")
RISK_REC = record("tests/unit/melder/aether/dev_ops/risk_manager/test_risk_manager_non_resolvable.py", 296,
                  "2026-10-16T01:19:21Z", "RiskManager's Book flag ignores flagged lineages, on a real registry (0.2.8247).")
WALK_REC = record(WALK, 377, TS, "the registry's downstream walk, a binding key per lineage, the contract mark walking\n"
                  "    on (0.2.8250).")
TRANSFER_REC = record("tests/integration/melder/conduit/test_conduit_integration_managed_transfer.py", 346,
                      "2026-10-15T22:33:31Z", "pools and owner stamps through moves, no-moves and failed transfers (0.2.8246).")
NOTCH_REC = record(NOTCH, 672, TS, "contract consumers and dependents following notches, grants and uncontracts; the\n"
                   "    meld-vs-notch race as a non-strict xfail (0.2.8250).")
SOURCES_OLD = (
    "- `tests/integration/melder/aether/conduit/test_index_moves_by_spell_id_integration.py`\n"
    "- direct filesystem inventory of `tests/`\n"
)
SOURCES_NEW = (
    "- `tests/integration/melder/aether/conduit/test_index_moves_by_spell_id_integration.py`\n"
    f"- `{WALK}`\n"
    f"- `{NOTCH}`\n"
    "- `tests/unit/melder/aether/conduit/meld/test_meld.py`\n"
    "- `tests/unit/melder/spellbook/test_spellbook.py`\n"
    f"- `{SVE}`\n"
    "- `tests/unit/melder/spellbook/spell_crafter/validation/strategies/test_contract_provider_presence_strategy.py`\n"
    "- `tests/unit/melder/spellbook/spell_compiler/phases/test_compiler_phase_4.py`\n"
    "- `tests/component/melder/spellbook/test_spellbook_component_structural_snapshot_parity.py`\n"
    "- direct filesystem inventory of `tests/`\n"
)
TC_HANDOFF_OLD = (
    "## Context / Handoff Summary\n\n"
    "2026-10-16 public notch target (0.2.8249): the Spellbook Runtime And Binding Unit Cluster gains\n"
)
TC_HANDOFF_NEW = (
    "## Context / Handoff Summary\n\n"
    "2026-10-16 contract recheck on notch (0.2.8250): the DevOps Control Plane Unit Cluster gains\n"
    "`test_spell_system_states_dependent_walk.py` (the downstream walk, 17 tests) and the Conduit Integration Cluster\n"
    "`test_conduit_integration_notch_revalidation.py` (contract consumers and dependents following notches, grants\n"
    "and uncontracts, 16 tests, the meld-vs-notch race among them as a non-strict xfail), each a key file with a\n"
    "code-map record. The Spellbook Runtime And Binding Unit Cluster names the Book's contract marks and the meld\n"
    "gate's catch-up (`test_meld.py`, whose five tests of the retired per-meld scan are replaced by three), the\n"
    "Spellbook Compiler and Utilities Unit Clusters the lost-provider report, the Spellbook Runtime And Binding\n"
    "Component Cluster the snapshot parity notch event, and the Multithreading Integration Cluster the explicit\n"
    "mark; the Unit Test Suite and the Integration Runtime Suite name the protection. The records of\n"
    "`test_spellbook.py`, `test_spellbook_component_spellbook.py`, `test_spellbook_validation_error.py` and the\n"
    "mid-resolution file are remeasured. Counts are recounted from disk (unit 508 of 511 `.py`, aether tree 207,\n"
    "spellbook tree 158; integration 170 of 177, conduit 44, spellbook 51; 844 test modules in the three tiers); the\n"
    "two spellbook counts, the core section's module count (838) and the core set (252, while the catalog held 256)\n"
    "had not followed the 0.2.8248 and 0.2.8249 entries. The core set is now 258 paths, equal to the code map.\n"
    "\n"
    "2026-10-16 public notch target (0.2.8249): the Spellbook Runtime And Binding Unit Cluster gains\n"
)

TC_STEPS = [
    (UNIT_SUITE_OLD, UNIT_SUITE_NEW),
    ("- the densest tier: 507 `test_*.py` modules among 510 `.py` files (recounted 2026-10-16)\n",
     "- the densest tier: 508 `test_*.py` modules among 511 `.py` files (recounted 2026-10-16)\n"),
    ("- The aether tree carries 206 `test_*.py` modules beneath these; they are the\n",
     "- The aether tree carries 207 `test_*.py` modules beneath these; they are the\n"),
    ("- The spellbook tree carries 157 `test_*.py` modules beneath these; they are the\n",
     "- The spellbook tree carries 158 `test_*.py` modules beneath these; they are the\n"),
    (INT_SUITE_OLD, INT_SUITE_NEW),
    ("- 169 `test_*.py` modules among 176 `.py` files (recounted 2026-10-16); the others are benches and the\n",
     "- 170 `test_*.py` modules among 177 `.py` files (recounted 2026-10-16); the others are benches and the\n"),
    ("- No harness or support module of its own; the 43 test_*.py modules in\n  tests/integration/melder/conduit/",
     "- No harness or support module of its own; the 44 test_*.py modules in\n  tests/integration/melder/conduit/"),
    ("- No harness or support module of its own; the 50 test_*.py modules in\n  tests/integration/melder/spellbook/",
     "- No harness or support module of its own; the 51 test_*.py modules in\n  tests/integration/melder/spellbook/"),
    (DEVOPS_PURPOSE_OLD, DEVOPS_PURPOSE_NEW),
    (DEVOPS_PROTECTS_OLD, DEVOPS_PROTECTS_NEW),
    (DEVOPS_KEYS_OLD, DEVOPS_KEYS_NEW),
    (SB_UNIT_OLD, SB_UNIT_NEW),
    (COMPILER_OLD, COMPILER_NEW),
    (UTIL_OLD, UTIL_NEW),
    (SB_COMP_OLD, SB_COMP_NEW),
    (CONDUIT_OLD, CONDUIT_NEW),
    (CONDUIT_KEYS_OLD, CONDUIT_KEYS_NEW),
    (MT_OLD, MT_NEW),
    ("above - 252 paths (recounted 2026-10-16) - and nothing else.",
     "above - 258 paths (recounted 2026-10-16) - and nothing else."),
    ("builders - not every `test_*.py` module beneath it. The 838 test modules of the\n",
     "builders - not every `test_*.py` module beneath it. The 844 test modules of the\n"),
    (SB_REC_OLD, SB_REC_NEW),
    (CSB_REC_OLD, CSB_REC_NEW),
    (SVE_REC_OLD, SVE_REC_NEW),
    (MR_REC_OLD, MR_REC_NEW),
    (RISK_REC, RISK_REC + WALK_REC),
    (TRANSFER_REC, TRANSFER_REC + NOTCH_REC),
    (SOURCES_OLD, SOURCES_NEW),
    (TC_HANDOFF_OLD, TC_HANDOFF_NEW),
]

TA_FAILURE_OLD = (
    "  EVIDENCE: tests/unit/melder/aether/conduit/creations/test_managed_spell_quantity_multithreaded.py:94-124\n"
    "\n"
    "## C1 Code Map (Core Only)\n"
)
TA_FAILURE_NEW = (
    "  EVIDENCE: tests/unit/melder/aether/conduit/creations/test_managed_spell_quantity_multithreaded.py:94-124\n"
    "- KNOWN RACE HELD AS XFAIL (integration conduit, 0.2.8250): the meld-vs-notch race test in\n"
    "  `test_conduit_integration_notch_revalidation.py` carries `xfail(strict=False, raises=AssertionError)` naming\n"
    f"  {TASK}. On a free-threaded run a meld in flight can\n"
    "  meet the borrower's contracted copy parked by a notch, and the test xfails (2 of 5 GIL-off runs on\n"
    "  2026-10-16); otherwise, and with the GIL on (5 of 5), it xpasses. Neither result fails the cell, any other\n"
    "  exception still fails the test, and whoever closes that task deletes the marker.\n"
    f"  EVIDENCE: {NOTCH}:623-672\n"
    "\n"
    "## C1 Code Map (Core Only)\n"
)
TA_SOURCES_OLD = "- `tests/unit/melder/aether/conduit/creations/test_release_managed_spell_multithreaded.py`\n"
TA_SOURCES_NEW = TA_SOURCES_OLD + f"- `{NOTCH}`\n"
TA_HANDOFF_OLD = (
    "## Context / Handoff Summary\n\n"
    "2026-10-16 public notch target (0.2.8249): the inventory is recounted from disk"
)
TA_HANDOFF_NEW = (
    "## Context / Handoff Summary\n\n"
    "2026-10-16 contract recheck on notch (0.2.8250): the inventory is recounted from disk (unit 511 `.py`,\n"
    "component 168, integration 177, mocks 44, experimentation 204; 844 test modules in the three tiers) - the lane\n"
    "adds one unit module (the registry's downstream walk) and one integration module (contract consumers and\n"
    "dependents following a provider change), catalogued in `tests_components`. `## Failure Modes and Error Paths`\n"
    "gains the known meld-vs-notch race, held as a non-strict xfail in that integration module. No tier, conftest,\n"
    "declared marker or shared support module changes, and no extent in this map moves.\n"
    "\n"
    "2026-10-16 public notch target (0.2.8249): the inventory is recounted from disk"
)
TA_STEPS = [
    ("- `unit/`: 510 `.py` files, 507 of them `test_*.py` (465 on 2026-09-26, 334 on 2026-06-13)\n",
     "- `unit/`: 511 `.py` files, 508 of them `test_*.py` (465 on 2026-09-26, 334 on 2026-06-13)\n"),
    ("- `integration/`: 176 `.py` files, 169 of them `test_*.py` (149, 88)\n",
     "- `integration/`: 177 `.py` files, 170 of them `test_*.py` (149, 88)\n"),
    ("(pycache excluded); the three tiers' 842 `test_*.py`\n",
     "(pycache excluded); the three tiers' 844 `test_*.py`\n"),
    (TA_FAILURE_OLD, TA_FAILURE_NEW),
    (TA_SOURCES_OLD, TA_SOURCES_NEW),
    (TA_HANDOFF_OLD, TA_HANDOFF_NEW),
]

apply(ROOT, TC, TC_STEPS, CHECK)
apply(ROOT, TA, TA_STEPS, CHECK)
