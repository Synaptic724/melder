"""Qualify the deadline regression oracle using transient, in-process production-method mutants."""
import argparse
import ast
import inspect
import textwrap
from pathlib import Path
import xml.etree.ElementTree as ET

import pytest

from melder.aether.conduit.creations import managed_spell_quantity as quantity_module


def install_mutant(variant: str) -> None:
    """Generate one deliberately broken queue method without writing to the production source."""
    tree = ast.parse(textwrap.dedent(inspect.getsource(quantity_module.ManagedSpellQuantity._reserve_queue)))
    method = tree.body[0]
    assert isinstance(method, ast.FunctionDef)
    method.name = "_deadline_mutant"
    loop = next(node for node in ast.walk(method) if isinstance(node, ast.While))
    if variant == "restart_deadline":
        deadline = next(
            node for node in method.body
            if isinstance(node, ast.Assign) and isinstance(node.targets[0], ast.Name)
            and node.targets[0].id == "deadline"
        )
        method.body.remove(deadline)
        loop.body.insert(0, deadline)
    elif variant == "full_timeout_wait":
        wait = next(
            node for node in ast.walk(loop)
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr == "wait"
        )
        wait.args = [ast.Attribute(value=ast.Name(id="self", ctx=ast.Load()), attr="_timeout_seconds", ctx=ast.Load())]
    else:
        assert variant == "early_expiry"
        loop.body.append(ast.Break())
    ast.fix_missing_locations(tree)
    exec(compile(tree, "<deadline mutation control>", "exec"), quantity_module.__dict__)
    quantity_module.ManagedSpellQuantity._reserve_queue = quantity_module._deadline_mutant


def main() -> None:
    """Require both regression cases to reject the selected mutant with assertion failures."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("variant", choices=("restart_deadline", "full_timeout_wait", "early_expiry"))
    variant = parser.parse_args().variant
    root = Path("C:/Users/Mark/PycharmProjects/melder_private")
    evidence = root / "context_compass/artifacts/queue_deadline_wakeups_20261019"
    report = evidence / f"mutant_{variant}.xml"
    install_mutant(variant)
    result = pytest.main([
        str(root / "tests/unit/melder/aether/conduit/creations/test_managed_spell_quantity.py")
        + "::test_queue_deadline_is_taken_once_across_wakeups",
        "-q", "-o", f"cache_dir={evidence / ('cache_' + variant)}", f"--junitxml={report}",
    ])
    cases = ET.parse(report).findall(".//testcase")
    assert result == pytest.ExitCode.TESTS_FAILED, f"Unexpected pytest exit: {result}"
    assert len(cases) == 2
    for case in cases:
        failure = case.find("failure")
        assert failure is not None and "AssertionError" in (failure.text or "")
        assert case.find("error") is None and case.find("skipped") is None
    print(f"EXPECTED REJECTION: both deadline cases reject {variant}")


if __name__ == "__main__":
    main()
