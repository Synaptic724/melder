"""
Apply the one-process-per-library change to the shared gauntlet (melder_0, 2026-09-30).

Usage:
    python apply_isolation.py <repo_root> <blocks_dir>

Reads the new text from <blocks_dir> (runner_new.py, block_b.py .. block_e.py,
md_section.md, test_isolation_new.py) and edits, keeping each file's line endings:
    - benchmarks/testing_other_di/real_world_gauntlet_gil_runner.py (replaced; CRLF)
    - benchmarks/testing_other_di/test_real_world_gauntlet.py (imports, three helper
      blocks, the per-turn CSV writer and the pytest wrapper; CRLF)
    - benchmarks/testing_other_di/benchmarks.md (section appended; CRLF)
    - benchmarks/testing_other_di/test_real_world_gauntlet_isolation.py (new; LF)
Every replacement must match exactly once, or nothing is written.
"""
import pathlib
import sys
from typing import Dict, List, Tuple


def _read_crlf(path: pathlib.Path) -> str:
    """Read a pure-CRLF file and return its text with LF line endings."""
    raw = path.read_bytes()
    assert raw.count(b"\r\n") == raw.count(b"\n"), f"{path} is not pure CRLF"
    return raw.decode("utf-8").replace("\r\n", "\n")


def _replace_once(text: str, old: str, new: str, label: str) -> str:
    """Replace `old` with `new`, requiring exactly one occurrence."""
    count = text.count(old)
    assert count == 1, f"{label}: expected 1 match, found {count}"
    return text.replace(old, new)


def main() -> int:
    """Stage every edit in memory, then write all files."""
    repo = pathlib.Path(sys.argv[1]).resolve()
    blocks = pathlib.Path(sys.argv[2]).resolve()
    bench = repo / "benchmarks" / "testing_other_di"
    block = {name: (blocks / name).read_text(encoding="utf-8") for name in (
        "runner_new.py", "block_b.py", "block_c.py", "block_d.py", "block_e.py", "md_section.md",
        "test_isolation_new.py")}
    writes: List[Tuple[pathlib.Path, bytes]] = []

    runner = bench / "real_world_gauntlet_gil_runner.py"
    _read_crlf(runner)
    writes.append((runner, block["runner_new.py"].replace("\n", "\r\n").encode("utf-8")))

    module = bench / "test_real_world_gauntlet.py"
    text = _read_crlf(module)
    text = _replace_once(text, "import gc\nimport os\n", "import gc\nimport json\nimport os\n", "import json")
    text = _replace_once(text, "import sys\nimport threading\n", "import sys\nimport tempfile\nimport threading\n",
                         "import tempfile")
    text = _replace_once(text, "def _build_ops(lib: str) -> _RuntimeOps:\n",
                         block["block_b.py"] + "def _build_ops(lib: str) -> _RuntimeOps:\n", "helpers before _build_ops")
    lines = text.split("\n")
    start = lines.index("def _maybe_write_per_turn_csv(results: list) -> None:")
    end = lines.index("def _print_benchmark_result(result: _BenchmarkResult) -> None:")
    old_csv = "\n".join(lines[start:end]).rstrip("\n") + "\n"
    assert old_csv.count("def ") == 1 and "real_world_gauntlet_per_turn" in old_csv
    text = _replace_once(text, old_csv, block["block_c.py"], "per-turn CSV writer")
    lines = text.split("\n")
    start = lines.index("@pytest.mark.timeout(3600)")
    assert lines[start + 1] == "def test_real_world_gauntlet() -> None:"
    old_test = "\n".join(lines[start:]).rstrip("\n") + "\n"
    assert old_test.count("def ") == 1
    text = _replace_once(text, old_test, block["block_d.py"] + block["block_e.py"], "pytest wrapper")
    writes.append((module, text.replace("\n", "\r\n").encode("utf-8")))

    notes = bench / "benchmarks.md"
    text = _read_crlf(notes)
    assert text.endswith("\n")
    text = text + block["md_section.md"]
    writes.append((notes, text.replace("\n", "\r\n").encode("utf-8")))

    new_test = bench / "test_real_world_gauntlet_isolation.py"
    assert not new_test.exists(), f"{new_test} already exists"
    writes.append((new_test, block["test_isolation_new.py"].encode("utf-8")))

    for path, data in writes:
        path.write_bytes(data)
        print(f"wrote {path.relative_to(repo)} ({len(data)} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
