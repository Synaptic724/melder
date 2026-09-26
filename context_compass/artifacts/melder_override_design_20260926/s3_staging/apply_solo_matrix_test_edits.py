"""Experimentation override matrix: solo supplies its leaf like the other graphs - anchored edits.

Usage: python apply_solo_matrix_test_edits.py <tree_root> [--check]

Since 0.2.59 the benchmark's SoloRootA takes one `leaf`; the matrix still read it as a root with no inputs, so its
Python-only control called `SoloRootA()` and failed. `_root_inputs` now returns the leaf and the module docstring no
longer calls solo an existing-singleton case. Each anchor must match exactly once or nothing is written.
Engine: apply_s3b1_edits.py.
"""

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

from apply_s3b1_edits import _apply_one

MATRIX = "tests/experimentation/test_melder_creation_overrides_performance.py"

DOC_OLD = '''are transient: the legacy override suite's existing-singleton solo case is not
mixed into creation ratios. Supplying a dependency changes requested graph work;
'''
DOC_NEW = '''are transient; solo is one root over one leaf (its old existing-singleton form
left the benchmark in 0.2.59). Supplying a dependency changes requested graph work;
'''

INPUTS_OLD = '''    if isinstance(root, graph_models.SoloRootA):
        return {}
'''
INPUTS_NEW = '''    if isinstance(root, graph_models.SoloRootA):
        return {"leaf": root.leaf}
'''

EDITS = {MATRIX: [("replace", DOC_OLD, DOC_NEW), ("replace", INPUTS_OLD, INPUTS_NEW)]}


def main() -> None:
    """Check every anchor, then write every file (unless --check)."""
    root = pathlib.Path(sys.argv[1])
    check = "--check" in sys.argv[2:]
    pending = {}
    for rel, edits in EDITS.items():
        path = root / rel
        data = path.read_bytes().decode("utf-8")
        for edit in edits:
            data = _apply_one(data, edit, rel)
        compile(data, rel, "exec")
        pending[path] = data
    for path, data in pending.items():
        if not check:
            path.write_bytes(data.encode("utf-8"))
        print(("checked " if check else "edited ") + str(path))


if __name__ == "__main__":
    main()
