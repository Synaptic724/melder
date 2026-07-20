"""
Runs every intermediate example as a pytest row (same harness law as the
beginner runner). Run on 3.14t:

    pytest UX_and_AIX_experiences/pytest_examples -v
"""
import importlib.util
from pathlib import Path

import pytest

EXAMPLES = sorted(
    (Path(__file__).parent.parent / "02_intermediate").glob("[0-9]*.py")
)


def _load(path: Path):
    spec = importlib.util.spec_from_file_location(
        "ux_int_example_" + path.stem, path
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.mark.parametrize("path", EXAMPLES, ids=[p.stem for p in EXAMPLES])
def test_intermediate_example_runs_green(path, capsys):
    module = _load(path)
    module.main()
    out = capsys.readouterr().out
    assert out.strip(), "examples narrate - silence means something broke"
