"""Remove exactly the obsolete mocked upgrade bodies replaced by component contracts.

This bounded migration preserves every other byte of the unit module. It verifies
the exact named function set and archives their original text for review before
writing. No source/runtime or generated asset is touched.
"""

import ast
from pathlib import Path


def main() -> None:
    """Archive and remove eight identified unit tests; refuse ambiguous input."""
    path = Path("tests/unit/melder/aether/conduit/test_conduit_dynamic.py")
    text = path.read_text(encoding="utf-8")
    names = {
        "test_upgrade_to_normal_transitions_and_registers",
        "test_upgrade_to_normal_refreshes_transaction_identity_without_changing_owner_id",
        "test_upgrade_to_normal_defaults_name_when_omitted",
        "test_upgrade_to_normal_registers_hooks",
        "test_upgrade_to_normal_logs_seed_failure_and_continues",
        "test_upgrade_to_normal_tolerates_root_conduit_lookup_failure",
        "test_upgrade_to_normal_clears_dirty_with_last_validated_at",
        "test_upgrade_to_normal_logs_and_reraises_outer_failure",
    }
    nodes = [node for node in ast.parse(text).body if isinstance(node, ast.FunctionDef) and node.name in names]
    if {node.name for node in nodes} != names or len(nodes) != 8:
        raise RuntimeError("Expected exactly the eight reviewed legacy upgrade test bodies.")
    lines = text.splitlines(keepends=True)
    archived = "\n".join("".join(lines[node.lineno - 1:node.end_lineno]) for node in nodes)
    Path("context_compass/artifacts/graduation_configuration_20260922/legacy_upgrade_tests.txt").write_text(
        archived, encoding="utf-8",
    )
    for node in reversed(nodes):
        del lines[node.lineno - 1:node.end_lineno]
    updated = "".join(lines).replace("MagicMock, PropertyMock, patch", "MagicMock, patch", 1)
    ast.parse(updated)
    path.write_text(updated, encoding="utf-8")


if __name__ == "__main__":
    main()
