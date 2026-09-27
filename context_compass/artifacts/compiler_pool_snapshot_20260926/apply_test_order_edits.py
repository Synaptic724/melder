"""Test-order fix: view fixtures leave a live Aether; the guard test sets up its own. `--check` writes nothing."""
import argparse
import pathlib
import sys
from typing import Dict, List, Tuple

VIEW_CONTRACT_OLD = [
    "        - AetherUtilitySystem, Nexus, and Aether are reset before and after",
    "          each test.",
]
VIEW_CONTRACT_NEW = [
    "        - AetherUtilitySystem, Nexus, and Aether are reset before and after",
    "          each test; after the test a fresh Aether is booted and bound to",
    "          `Spellbook._aether`, so later tests find a live world (a reset alone",
    "          boots nothing, and `Spellbook()` needs the Nexus an Aether boot builds).",
]
VIEW_TEARDOWN_OLD = [
    "    yield",
    "    AetherUtilitySystem._reset_singleton_for_tests()",
    "    Nexus._reset_singleton_for_tests()",
    "    Aether._reset_singleton_for_tests()",
]
VIEW_TEARDOWN_NEW = VIEW_TEARDOWN_OLD + ["    Spellbook._aether = Aether()"]
VIEW_IMPORT_OLD = ["from melder.aether.aether_utility_system import AetherUtilitySystem"]
VIEW_IMPORT_NEW = VIEW_IMPORT_OLD + ["from melder.aether.spellbook.spellbook import Spellbook"]
VIEW_EDITS = [(VIEW_CONTRACT_OLD, VIEW_CONTRACT_NEW, 1), (VIEW_TEARDOWN_OLD, VIEW_TEARDOWN_NEW, 1),
              (VIEW_IMPORT_OLD, VIEW_IMPORT_NEW, 1)]

EDITS: Dict[str, List[Tuple[List[str], List[str], int]]] = {
    "tests/unit/melder/test_system_document_view.py": VIEW_EDITS,
    "tests/integration/melder/multithreading/test_multithreading_system_document_view.py": VIEW_EDITS,
    "tests/unit/melder/test_melder_registration_guard.py": [
        (["import pytest"], ["from typing import Iterator", "", "import pytest"], 1),
        (["from melder.aether.aether import Aether"],
         ["from melder.aether.aether import Aether",
          "from melder.aether.aether_utility_system import AetherUtilitySystem"], 1),
        (["from melder.utilities.custom_exceptions.internal_registration_error import InternalRegistrationError"],
         ["from melder.nexus.nexus import Nexus",
          "from melder.utilities.custom_exceptions.internal_registration_error import InternalRegistrationError",
          "",
          "",
          "def _boot_fresh_aether() -> None:",
          "    \"\"\"Reset the runtime singletons, boot a new Aether and bind it to `Spellbook._aether`.\"\"\"",
          "    AetherUtilitySystem._reset_singleton_for_tests()",
          "    Nexus._reset_singleton_for_tests()",
          "    Aether._reset_singleton_for_tests()",
          "    Spellbook._aether = Aether()",
          "",
          "",
          "@pytest.fixture(autouse=True)",
          "def live_aether() -> Iterator[None]:",
          "    \"\"\"",
          "    Run each test against a freshly booted Aether, and leave one behind.",
          "",
          "    Purpose:",
          "        `test_bind_rejects_internal_class` builds a Spellbook, which needs the Nexus an Aether boot",
          "        constructs. Without its own setup the test passed only when the test before it left a live",
          "        Aether, and failed after tests whose teardown reset the singletons without booting a new one.",
          "",
          "    Yields:",
          "        None.",
          "    \"\"\"",
          "    _boot_fresh_aether()",
          "    yield",
          "    _boot_fresh_aether()"], 1),
    ],
}


def _find(lines: List[bytes], old: List[bytes]) -> List[int]:
    """Return every start index where `old` matches consecutive lines (ending-insensitive)."""
    bare = [ln.rstrip(b"\r") for ln in lines]
    return [i for i in range(len(bare) - len(old) + 1) if bare[i:i + len(old)] == old]


def _apply(root: pathlib.Path, check: bool) -> int:
    """Verify every anchor, then (unless `check`) write; returns a process exit code."""
    staged: Dict[pathlib.Path, bytes] = {}
    for rel, edits in EDITS.items():
        path = root / rel
        lines = path.read_bytes().split(b"\n")
        for old_s, new_s, count in edits:
            old = [s.encode("utf-8") for s in old_s]
            hits = _find(lines, old)
            if len(hits) != count:
                print(f"ANCHOR MISMATCH {rel}: expected {count}, found {len(hits)}: {old_s[0][:70]!r}")
                return 1
            for start in reversed(hits):
                eol = b"\r" if lines[start].endswith(b"\r") else b""
                lines[start:start + len(old)] = [s.encode("utf-8") + eol for s in new_s]
        staged[path] = b"\n".join(lines)
        print(f"ok {rel} ({len(edits)} edits)")
    if check:
        return 0
    for path, data in staged.items():
        path.write_bytes(data)
    return 0


def main() -> int:
    """Parse arguments and run the edits."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", required=True)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    return _apply(pathlib.Path(args.root), args.check)


if __name__ == "__main__":
    sys.exit(main())
