"""Record the scope_exit_dispose_2026_09_27 tests in tests_components.md (0.2.8203).

Every edit is an exact-match anchor that must occur once; the script refuses to write otherwise.
Usage: python edit_tests_components.py <doc path> <verified_at UTC>
"""
import pathlib
import re
import sys

doc = pathlib.Path(sys.argv[1])
verified_at = sys.argv[2]
text = doc.read_bytes().decode("utf-8")
assert "\r\n" not in text


def swap(old: str, new: str) -> None:
    global text
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"anchor found {count} times:\n{old}")
    text = text.replace(old, new)


COMPONENT_EXIT = "tests/component/melder/aether/conduit/test_conduit_component_scope_exit_dispose.py"
COMPONENT_LEASE = "tests/component/melder/aether/conduit/test_spellspace_component_lease_release.py"
UNIT_CONTEXTS = "tests/unit/melder/utilities/general_base/test_cleanable_cleanup_contexts.py"

# Aether Component Cluster.
swap(
    "  managed-frame state; the extended viewer surface matrix\n"
    "Key Files (C1):\n"
    "- `tests/component/melder/aether/test_frame_descriptor_manager_component.py`\n"
    "- `tests/component/melder/aether/test_frame_acl_component.py`\n"
    "- `tests/component/melder/aether/test_nexus_viewer_extended_surface_component_matrix.py`\n",
    "  managed-frame state; the extended viewer surface matrix\n"
    "- scope exits (0.2.8203): `with conduit:` disposes (a lesser pooled with its objects disposed, a root torn\n"
    "  down, the block's error kept), `enter_lesser_conduit`, children-first pool return, finish-then-raise on\n"
    "  every exit, idempotent soft cleanup (two cleanups, one pool entry), and the SpellSpace lease flag (a kept\n"
    "  handle refuses meld and purge; a space released or destroyed inside its own block exits cleanly)\n"
    "Key Files (C1):\n"
    "- `tests/component/melder/aether/test_frame_descriptor_manager_component.py`\n"
    "- `tests/component/melder/aether/test_frame_acl_component.py`\n"
    "- `tests/component/melder/aether/test_nexus_viewer_extended_surface_component_matrix.py`\n"
    f"- `{COMPONENT_EXIT}`\n"
    f"- `{COMPONENT_LEASE}`\n",
)

# Utilities Unit Cluster.
swap(
    "  persistence round trips; exact line accounting in the agent text reader\n",
    "  persistence round trips; exact line accounting in the agent text reader\n"
    "- the Cleanable cleanup contexts (0.2.8203): `using_cleanup()` and `async_using_cleanup()` clean up at\n"
    "  most once and let the cleanup error propagate, chained to the block's error\n",
)
swap(
    "- `tests/unit/melder/utilities/data_structures/test_abstract_elastic_pool_multithreaded.py`\n\n",
    "- `tests/unit/melder/utilities/data_structures/test_abstract_elastic_pool_multithreaded.py`\n"
    f"- `{UNIT_CONTEXTS}`\n\n",
)

# Conduit Integration Cluster.
swap(
    "- teardown: idempotent cleanup that blocks meld, and dependents disposed before\n"
    "  their dependencies; a failing disposal method no longer skips the object's later methods\n"
    "  (0.2.80)\n",
    "- teardown: idempotent cleanup that blocks meld, and dependents disposed before\n"
    "  their dependencies; a failing disposal method no longer skips the object's later methods\n"
    "  (0.2.80); conduit cleanup and a SpellSpace exit finish and then raise the failures as one\n"
    "  ExceptionGroup (0.2.8203)\n",
)

# C1 map: new entries and one remeasure.
swap(
    "- path: `tests/component/melder/aether/test_nexus_viewer_extended_surface_component_matrix.py`\n"
    "  start_line: 1\n  end_line: 188\n  loc: 188\n  verified_at: 2026-09-26T22:11:36Z\n",
    "- path: `tests/component/melder/aether/test_nexus_viewer_extended_surface_component_matrix.py`\n"
    "  start_line: 1\n  end_line: 188\n  loc: 188\n  verified_at: 2026-09-26T22:11:36Z\n"
    f"- path: `{COMPONENT_EXIT}`\n  start_line: 1\n  end_line: 394\n  loc: 394\n  verified_at: {verified_at}\n"
    f"- path: `{COMPONENT_LEASE}`\n  start_line: 1\n  end_line: 317\n  loc: 317\n  verified_at: {verified_at}\n",
)
swap(
    "- path: `tests/unit/melder/utilities/data_structures/test_abstract_elastic_pool_multithreaded.py`\n"
    "  start_line: 1\n  end_line: 243\n  loc: 243\n  verified_at: 2026-09-26T22:11:36Z\n",
    "- path: `tests/unit/melder/utilities/data_structures/test_abstract_elastic_pool_multithreaded.py`\n"
    "  start_line: 1\n  end_line: 243\n  loc: 243\n  verified_at: 2026-09-26T22:11:36Z\n"
    f"- path: `{UNIT_CONTEXTS}`\n  start_line: 1\n  end_line: 114\n  loc: 114\n  verified_at: {verified_at}\n",
)
swap(
    "- path: `tests/integration/melder/conduit/test_conduit_integration_disposal_failures.py`\n"
    "  start_line: 1\n  end_line: 120\n  loc: 120\n  verified_at: 2026-09-27T13:27:50Z\n",
    "- path: `tests/integration/melder/conduit/test_conduit_integration_disposal_failures.py`\n"
    f"  start_line: 1\n  end_line: 142\n  loc: 142\n  verified_at: {verified_at}\n",
)

# Recount the core set (the union of every Key Files list).
key_files = set()
lines = text.split("\n")
in_block = False
for line in lines:
    if line.startswith("Key Files (C1):"):
        in_block = True
        key_files.update(re.findall(r"`([^`]*)`", line[len("Key Files (C1):"):]))
        continue
    if in_block:
        if line.startswith("- `"):
            key_files.update(re.findall(r"`([^`]*)`", line))
            continue
        in_block = False
core = {k for k in key_files if not any(ch in k for ch in "*?")}
c1 = set(re.findall(r"^- path: `([^`]*)`", text, flags=re.M))
print("key files", len(core), "c1 entries", len(c1), "missing from c1", sorted(core - c1)[:5], "extra", sorted(c1 - core)[:5])
swap("above - 183 paths - and nothing else.", f"above - {len(core)} paths - and nothing else.")

# Handoff.
swap(
    "## Context / Handoff Summary\n\n2026-09-27 disposal failures (0.2.80):",
    "## Context / Handoff Summary\n\n"
    "2026-09-27 scope exits (0.2.8203): `test_conduit_component_scope_exit_dispose.py` and\n"
    "`test_spellspace_component_lease_release.py` joined the Aether Component Cluster (`with conduit:` as a\n"
    "dispose scope, finish-then-raise exits, children-first pool return, idempotent soft cleanup, the SpellSpace\n"
    "lease flag), and `test_cleanable_cleanup_contexts.py` the Utilities Unit Cluster (cleanup contexts let errors\n"
    "propagate). `test_conduit_integration_disposal_failures.py` now expects conduit cleanup to raise its disposal\n"
    "failures after finishing (remeasured, 142 lines); the rewritten lock and root `with` tests sit in files this\n"
    "map keeps below cluster level (`test_conduit_lifecycle.py`, `test_conduit_integration_public_api.py`).\n"
    "\n"
    "2026-09-27 disposal failures (0.2.80):",
)

doc.write_bytes(text.encode("utf-8"))
print("edited", doc, len(text.splitlines()))
