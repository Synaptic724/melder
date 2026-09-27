"""Promote the creations_disposal_failures_2026_09_27 patch lane into the system docs (melder_0). Run from system_docs/."""
import datetime
import pathlib
import sys

assert sys.version_info >= (3, 14), "run with the 3.14 venv"
NOW = sys.argv[1]


def edit(path: str, pairs) -> None:
    text = pathlib.Path(path).read_bytes().decode("utf-8")
    assert "\r\n" not in text, path
    for old, new in pairs:
        found = text.count(old)
        assert found == 1, f"{path}: expected 1 of {old[:70]!r}, found {found}"
        text = text.replace(old, new)
    for i, line in enumerate(text.splitlines(), 1):
        if line not in ORIG[path] and len(line) > 120 and not line.startswith("|"):
            raise SystemExit(f"{path}:{i} is {len(line)} chars")
    OUT[path] = text


ORIG = {p: set(pathlib.Path(p).read_text(encoding="utf-8").splitlines())
        for p in ("src_components.md", "src_architecture.md", "tests_components.md")}
OUT = {}

edit("src_components.md", [
    ("  EVIDENCE: src/melder/aether/conduit/creations/creations.py:305-354.\n",
     "  EVIDENCE: src/melder/aether/conduit/creations/creations.py:365-413.\n"),
    ("- Method names execute in list order. A failing method stops that object's remaining\n"
     "  methods; later objects are still attempted and errors aggregate.\n",
     "- Method names execute in list order, and every one runs even after an earlier one fails\n"
     "  (2026-09-27, 0.2.80; before, the first failure stopped that object's remaining methods).\n"
     "  Each failing method is one `RuntimeError` in the aggregated group, chained from the\n"
     "  exception it raised; the error text never depends on the object's own `__str__`, so a\n"
     "  failing object cannot strand the rest. Later objects are still attempted.\n"),
    ("- ExceptionGroup raised if any disposal errors occur.\n",
     "- ExceptionGroup raised if any disposal errors occur: one `RuntimeError` per failing method,\n"
     "  each with `__cause__` set to the exception that method raised (0.2.80).\n"),
    ("  at a time. A single failing disposal must not strand the rest of the scope.\n"
     "  EVIDENCE:\n"
     "  - src/melder/aether/conduit/creations/creations.py:69-80\n"
     "  - src/melder/aether/conduit/creations/creations.py:223-239\n",
     "  at a time. A single failing disposal must not strand the rest of the scope.\n"
     "  Since 0.2.80 this holds per method as well, and every error keeps the original\n"
     "  exception as its cause, so the logged or raised group shows what actually failed.\n"
     "  EVIDENCE:\n"
     "  - src/melder/aether/conduit/creations/creations.py:69-84\n"
     "  - src/melder/aether/conduit/creations/creations.py:227-243\n"
     "  - src/melder/aether/conduit/creations/creations.py:245-324\n"),
    ("Contract/Interface:\n- `Creations.cleanup()`.\nData Structures:\n- Existence maps for unique/many/scope.\n",
     "Contract/Interface:\n- `Creations.cleanup()`.\n"
     "- Every declared method of every object runs; each failing method is one chained `RuntimeError`,\n"
     "  aggregated into one `ExceptionGroup` (0.2.80).\n"
     "Data Structures:\n- Existence maps for unique/many/scope.\n"),
    ("6. After lock release, _attempt_cleanup or _dispose_many_creations runs the recorded disposal methods.\n",
     "6. After lock release, _attempt_cleanup or _dispose_many_creations runs every recorded disposal method,\n"
     "   collecting one chained error per failing method (0.2.80).\n"),
    ("- path: `src/melder/aether/conduit/creations/creations.py`\n  start_line: 1\n  end_line: 1125\n  loc: 1125\n"
     "  verified_at: 2026-09-25T23:40:00Z\n",
     "- path: `src/melder/aether/conduit/creations/creations.py`\n  start_line: 1\n  end_line: 1189\n  loc: 1189\n"
     f"  verified_at: {NOW}\n"),
    ("## Context / Handoff Summary\n\n",
     "## Context / Handoff Summary\n\n"
     "2026-09-27 disposal failures (0.2.80): Creations runs every declared disposal method of an object even after\n"
     "one raises, and reports one `RuntimeError` per failing method, chained from the exception it raised, in the\n"
     "group cleanup, clear_all and purge already raise; error text no longer trusts the object's `__str__`. Promoted\n"
     "into Creations and SpellSpace (invariants, failure modes, observability), the Creations Disposal Pipeline and\n"
     "the purge flow; three `creations.py` citations remapped (69-84, 227-243, 365-413).\n\n"),
])

edit("src_architecture.md", [
    ("   rather than stopping at the first, so a single bad object cannot strand the\n"
     "   rest of the scope.\n",
     "   rather than stopping at the first, so a single bad object cannot strand the\n"
     "   rest of the scope. Since 0.2.80 that holds per method too: every declared method\n"
     "   runs even after one fails, and each failure is chained from what the method raised.\n"),
    ("## Operational Invariants\n",
     "## Operational Invariants\n"
     "- Disposal failures (2026-09-27, 0.2.80): Creations runs every declared disposal method of every object, in\n"
     "  declared order, even after one raises. Each failing method is one `RuntimeError` in the `ExceptionGroup` that\n"
     "  cleanup, clear_all and purge raise, chained from the exception the method raised; a refused late publication\n"
     "  chains its errors the same way. The error text never trusts the object's `__str__`, so one failing object\n"
     "  cannot strand the rest of a scope. Disposal order and which objects are disposed are unchanged.\n"
     "  EVIDENCE: `src/melder/aether/conduit/creations/creations.py:Creations._attempt_cleanup` and\n"
     "  `Creations._describe_for_disposal_error`.\n"),
    ("- Cleanup errors are logged; Creations may raise ExceptionGroup.\n",
     "- Cleanup errors are logged; Creations may raise ExceptionGroup. Since 0.2.80 it holds one error per failing\n"
     "  disposal method, each chained from what that method raised; before, an object's first failure ended its\n"
     "  disposal and the original exception was dropped.\n"),
    ("- path: `src/melder/aether/conduit/creations/creations.py`\n  start_line: 1\n  end_line: 1125\n  loc: 1125\n"
     "  verified_at: 2026-09-25T23:40:00Z\n",
     "- path: `src/melder/aether/conduit/creations/creations.py`\n  start_line: 1\n  end_line: 1189\n  loc: 1189\n"
     f"  verified_at: {NOW}\n"),
    ("## Context / Handoff Summary\n\n",
     "## Context / Handoff Summary\n\n"
     "2026-09-27 disposal failures (0.2.80): one failing disposal method no longer stops an object's teardown;\n"
     "every declared method runs and every failure reaches the caller chained from its original exception. The\n"
     "cleanup sequence, the operational invariants, the failure modes and the code map carry it; the component map\n"
     "carries the per-method contract.\n\n"),
])

edit("tests_components.md", [
    ("- teardown: idempotent cleanup that blocks meld, and dependents disposed before\n  their dependencies\n",
     "- teardown: idempotent cleanup that blocks meld, and dependents disposed before\n  their dependencies; a failing "
     "disposal method no longer skips the object's later methods\n  (0.2.80)\n"),
    ("- `tests/integration/melder/conduit/test_conduit_integration_disposal_ordering.py`\n"
     "- `tests/integration/melder/conduit/test_conduit_integration_transfer_ownership.py`\n",
     "- `tests/integration/melder/conduit/test_conduit_integration_disposal_ordering.py`\n"
     "- `tests/integration/melder/conduit/test_conduit_integration_disposal_failures.py`\n"
     "- `tests/integration/melder/conduit/test_conduit_integration_transfer_ownership.py`\n"),
    ("- path: `tests/integration/melder/conduit/test_conduit_integration_disposal_ordering.py`\n"
     "  start_line: 1\n  end_line: 342\n  loc: 342\n  verified_at: 2026-09-26T22:11:36Z\n",
     "- path: `tests/integration/melder/conduit/test_conduit_integration_disposal_ordering.py`\n"
     "  start_line: 1\n  end_line: 342\n  loc: 342\n  verified_at: 2026-09-26T22:11:36Z\n"
     "- path: `tests/integration/melder/conduit/test_conduit_integration_disposal_failures.py`\n"
     f"  start_line: 1\n  end_line: 120\n  loc: 120\n  verified_at: {NOW}\n"),
    ("## Context / Handoff Summary\n\n",
     "## Context / Handoff Summary\n\n"
     "2026-09-27 disposal failures (0.2.80): `test_conduit_integration_disposal_failures.py` joined the Conduit\n"
     "Integration Cluster (real conduit cleanup and managed SpellSpace exit run every disposal method after one\n"
     "fails). The unit regression `test_creations_disposal_failure_aggregation_regression.py` and the updated\n"
     "creations and component purge tests sit in files this map keeps below cluster level.\n\n"),
])

for path, text in OUT.items():
    pathlib.Path(path).write_bytes(text.encode("utf-8"))
    print("wrote", path)
