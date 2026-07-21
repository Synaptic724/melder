"""
Runs every beginner example as a pytest row - main() must complete with
all its asserts green. Run on 3.14t from the repo root:

    pytest UX_and_AIX_experiences/pytest_examples -v
"""
import importlib.util
import sys
from pathlib import Path

import pytest

EXAMPLES = sorted(
    (Path(__file__).parent.parent / "01_beginner").glob("[0-9]*.py")
)


def _load(path: Path):
    spec = importlib.util.spec_from_file_location(
        "ux_example_" + path.stem, path
    )
    module = importlib.util.module_from_spec(spec)
    # Import law (run 3): a module must be registered in sys.modules
    # BEFORE exec - lessons that look themselves up (scan lessons use
    # sys.modules[__name__]) are broken by an unregistered exec.
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


@pytest.mark.parametrize("path", EXAMPLES, ids=[p.stem for p in EXAMPLES])
def test_beginner_example_runs_green(path, capsys):
    module = _load(path)
    module.main()
    out = capsys.readouterr().out
    assert out.strip(), "examples narrate - silence means something broke"
