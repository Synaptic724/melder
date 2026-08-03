"""
Runs every expert example as a pytest row (same harness law as the
other tiers). Run on 3.14t:

    pytest UX_and_AIX_experiences/pytest_examples -v
"""
import importlib.util
import sys
from pathlib import Path

import pytest

EXAMPLES = sorted(
    (Path(__file__).parent.parent / "04_expert").glob("[0-9]*.py")
)


def _load(path: Path):
    spec = importlib.util.spec_from_file_location(
        "ux_expert_example_" + path.stem, path
    )
    module = importlib.util.module_from_spec(spec)
    # Import law (run 3): register BEFORE exec - lessons may look
    # themselves up via sys.modules[__name__].
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


@pytest.mark.parametrize("path", EXAMPLES, ids=[p.stem for p in EXAMPLES])
def test_expert_example_runs_green(path, capsys):
    module = _load(path)
    module.main()
    out = capsys.readouterr().out
    assert out.strip(), "examples narrate - silence means something broke"
