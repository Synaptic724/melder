"""Gather the facts S7's tests-docs pass writes from: the lane's test files and the tier counts.

Read-only. Run from the repository root:
    python context_compass/artifacts/managed_spell_quantity_20261015/scripts/s7_tests_facts.py [--names]

Prints, for each new and changed test file of the managed_spell_quantity lane, its line count (splitlines),
the first paragraph of its module docstring, its test count and test classes; whether tests_components and
tests_architecture cite it (and the end_line they record); then the test-module and .py counts of the three
CI tiers and of the subtrees tests_components counts.
"""

import ast
import pathlib
import re
import sys


def new_and_changed() -> tuple[list[str], list[str]]:
    """Return the lane's new and changed test files (repo-relative), as git listed them on 2026-10-15."""
    new = [
        "tests/unit/melder/aether/conduit/conduit_ward/transfer/test_transfer_of_ownership_owner_stamps.py",
        "tests/unit/melder/aether/conduit/creations/test_creations_discard_managed_quantity.py",
        "tests/unit/melder/aether/conduit/creations/test_creations_managed_quantities.py",
        "tests/unit/melder/aether/conduit/creations/test_managed_spell_lease.py",
        "tests/unit/melder/aether/conduit/creations/test_managed_spell_quantity.py",
        "tests/unit/melder/aether/conduit/creations/test_managed_spell_quantity_multithreaded.py",
        "tests/unit/melder/aether/conduit/creations/test_release_managed_spell.py",
        "tests/unit/melder/aether/conduit/creations/test_release_managed_spell_multithreaded.py",
        "tests/unit/melder/aether/conduit/meld/test_meld_doors_managed_spell_quantity.py",
        "tests/unit/melder/aether/test_static_rooms_managed_spell_quantity.py",
        "tests/unit/melder/crystallizer/test_spell_crystal_managed_options.py",
        "tests/unit/melder/spellbook/bind/test_bind_managed_spell_options.py",
        "tests/unit/melder/spellbook/bind/test_spell_index_selected_probe.py",
        "tests/unit/melder/spellbook/spell_compiler/shared_assets/test_site_plan_lowering_managed.py",
        "tests/unit/melder/spellbook/spell_compiler/test_managed_dispense_seams.py",
        "tests/unit/melder/spellbook/test_existence_managed_spell_quantity.py",
        "tests/unit/melder/spellbook/test_scan_bind_managed_options.py",
        "tests/unit/melder/spellbook/test_spell_managed_quantity_stamp.py",
        "tests/unit/melder/spellbook/test_spell_managed_spell_options.py",
        "tests/unit/melder/spellbook/test_spellbinder_managed_options.py",
        "tests/unit/melder/utilities/custom_exceptions/test_managed_spell_exhausted_error.py",
        "tests/component/melder/aether/conduit/test_conduit_component_managed_spell_quantity.py",
        "tests/integration/melder/conduit/test_conduit_integration_managed_quantity_pool.py",
        "tests/integration/melder/conduit/test_conduit_integration_managed_spell_quantity.py",
        "tests/integration/melder/conduit/test_conduit_integration_managed_transfer.py",
        "tests/integration/melder/conduit/test_conduit_integration_release_managed_spell.py",
        "tests/integration/melder/crystallizer/test_managed_spell_options_record_integration.py",
        "tests/integration/melder/spellbook/test_managed_bind_options_integration.py",
    ]
    changed = [
        "tests/component/melder/aether/conduit/test_conduit_component_purge.py",
        "tests/unit/melder/aether/conduit/test_conduit_facade.py",
        "tests/unit/melder/spellbook/spell_compiler/test_codegen_plan_discovery_core.py",
        "tests/unit/melder/spellbook/spell_compiler/test_generalized_specializer_wrapper.py",
        "tests/unit/melder/spellbook/spell_compiler/test_spell_artifact_processor_core.py",
        "tests/unit/melder/spellbook/spell_crafter/system/validation/test_scope_ordering_strategy.py",
        "tests/unit/melder/spellbook/test_resolution_style_matrix.py",
        "tests/unit/melder/spellbook/test_scan_bind_option_parity.py",
        "tests/unit/melder/test_package_public_surface.py",
    ]
    return new, changed


def describe(path: pathlib.Path, show_names: bool) -> str:
    """Summarize one test module: lines, docstring paragraph, tests per class."""
    text = path.read_text(encoding="utf-8")
    tree = ast.parse(text)
    lines = len(text.splitlines())
    doc = ast.get_docstring(tree) or ""
    first = " ".join(doc.strip().split("\n\n")[0].split())
    tests: list[str] = []
    classes: list[str] = []

    def label(fn: ast.AST, prefix: str) -> str:
        """Name a test and, with --names, the first line of its docstring."""
        first_doc = (ast.get_docstring(fn) or "").strip().split("\n")[0]
        return f"{prefix}{fn.name}" + (f" -- {first_doc[:160]}" if first_doc else "")

    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name.startswith("test"):
            tests.append(label(node, ""))
        elif isinstance(node, ast.ClassDef):
            own = [n for n in node.body
                   if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and n.name.startswith("test")]
            if own:
                classes.append(f"{node.name}({len(own)})")
                tests.extend(label(n, f"{node.name}.") for n in own)
    rel = path.relative_to(pathlib.Path.cwd()).as_posix()
    out = [f"{rel} lines={lines} tests={len(tests)} classes={' '.join(classes) or '-'}",
           f"  doc: {first[:600]}"]
    if show_names:
        out.extend(f"    {t}" for t in tests)
    return "\n".join(out)


def cited(doc_text: str, rel: str) -> str:
    """Report whether a document cites rel and the end_line its C1 record carries."""
    if f"`{rel}`" not in doc_text:
        return "not cited"
    m = re.search(r"^- path: `" + re.escape(rel) + r"`\n\s+start_line: \d+\n\s+end_line: (\d+)", doc_text, re.M)
    return f"cited; C1 end_line={m.group(1)}" if m else "cited; no C1 record"


def counts(root: pathlib.Path) -> None:
    """Print test-module and .py counts per tier and per counted subtree."""
    def n(p: pathlib.Path, pattern: str) -> int:
        return sum(1 for f in p.rglob(pattern) if "__pycache__" not in f.parts) if p.is_dir() else 0
    for tier in ("unit", "component", "integration"):
        t = root / "tests" / tier
        print(f"tier {tier}: test_*.py={n(t, 'test_*.py')} .py={n(t, '*.py')}")
    subtrees = [
        "unit/melder/aether", "unit/melder/aether/conduit", "unit/melder/crystallizer",
        "unit/melder/mutation_research", "unit/melder/spellbook", "unit/melder/utilities",
        "unit/melder/build_assets", "unit/github_workflows", "unit/llm_support", "unit/architecture_and_design",
        "component/melder/aether", "component/melder/crystallizer", "component/melder/mutation_research",
        "component/melder/spellbook", "component/melder/utilities",
        "integration/melder/aether", "integration/melder/aether/rift", "integration/melder/conduit",
        "integration/melder/crystallizer", "integration/melder/live_sim", "integration/melder/multithreading",
        "integration/melder/mutation_research", "integration/melder/spellbook",
    ]
    for s in subtrees:
        print(f"  {s}: test_*.py={n(root / 'tests' / s, 'test_*.py')}")
    top = root / "tests" / "unit" / "melder"
    print(f"  unit/melder top-level test_*.py={sum(1 for f in top.glob('test_*.py'))}")
    three = sum(n(root / "tests" / t, "test_*.py") for t in ("unit", "component", "integration"))
    print(f"three tiers test_*.py total={three}")


def main() -> None:
    """Print the facts."""
    root = pathlib.Path.cwd()
    show = "--names" in sys.argv
    tc = (root / "context_compass/system_docs/tests_components.md").read_text(encoding="utf-8")
    ta = (root / "context_compass/system_docs/tests_architecture.md").read_text(encoding="utf-8")
    new, changed = new_and_changed()
    print("== NEW ==")
    for rel in new:
        print(describe(root / rel, show))
    print("== CHANGED ==")
    for rel in changed:
        print(describe(root / rel, False))
        print(f"  tests_components: {cited(tc, rel)}; tests_architecture: {cited(ta, rel)}")
    print("== COUNTS ==")
    counts(root)


if __name__ == "__main__":
    main()
