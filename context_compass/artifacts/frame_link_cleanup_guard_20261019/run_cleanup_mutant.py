"""Verify the repaired guard regression rejects missing cleanup checks without changing production files."""
import argparse
import ast
import inspect
from pathlib import Path
import textwrap
import xml.etree.ElementTree as ET

import pytest

from melder.nexus.rift.frame_link import frame_link as frame_module


def main() -> None:
    """Generate a single removed-guard mutation and require one cleanly reported test failure."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('guard', choices=('inner', 'outer'))
    guard = parser.parse_args().guard
    tree = ast.parse(textwrap.dedent(inspect.getsource(frame_module.FrameLink.cleanup)))
    method = tree.body[0]
    assert isinstance(method, ast.FunctionDef)
    method.name = '_cleanup_mutant'
    if guard == 'inner':
        guarded = next(node for node in method.body if isinstance(node, ast.With))
        assert isinstance(guarded.body[0], ast.If)
        guarded.body.pop(0)
    else:
        check = next(node for node in method.body if isinstance(node, ast.If))
        method.body.remove(check)
    ast.fix_missing_locations(tree)
    exec(compile(tree, '<removed cleanup guard control>', 'exec'), frame_module.__dict__)
    frame_module.FrameLink.cleanup = frame_module._cleanup_mutant
    root = Path('C:/Users/Mark/PycharmProjects/melder_private')
    evidence = root / 'context_compass/artifacts/frame_link_cleanup_guard_20261019'
    report = evidence / f'mutant_{guard}.xml'
    result = pytest.main([
        str(root / 'tests/unit/melder/aether/test_frame_link_runtime_contracts.py')
        + '::test_frame_link_cleanup_rechecks_cleaned_inside_lock',
        '-q', '-o', f'cache_dir={evidence / ("cache_mutant_" + guard)}', f'--junitxml={report}',
    ])
    cases = ET.parse(report).findall('.//testcase')
    assert result == pytest.ExitCode.TESTS_FAILED and len(cases) == 1
    failure = cases[0].find('failure')
    assert failure is not None and 'AttributeError' in (failure.text or '')
    assert cases[0].find('error') is None and cases[0].find('skipped') is None
    print(f'EXPECTED REJECTION: removing the {guard} cleanup guard fails in the main test thread')


if __name__ == '__main__':
    main()
