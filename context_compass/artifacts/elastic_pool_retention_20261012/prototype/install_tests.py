"""
Install the elastic-retention test changes into a tree (TASK-2026-10-12-make_kernel_pools_elastic).

Usage: python install_tests.py <tree root> <newtests dir>
Keeps each file's line endings (CRLF files stay CRLF, LF files stay LF); every anchor must match exactly once.
"""
import pathlib
import sys


def read(path: pathlib.Path) -> tuple:
    """Return (text with LF, uses_crlf)."""
    raw = path.read_bytes().decode("utf-8")
    crlf = "\r\n" in raw
    if crlf:
        assert raw.count("\r\n") == raw.count("\n"), f"mixed endings in {path}"
    return raw.replace("\r\n", "\n"), crlf


def write(path: pathlib.Path, text: str, crlf: bool) -> None:
    """Write LF text back with the file's original ending."""
    path.write_bytes((text.replace("\n", "\r\n") if crlf else text).encode("utf-8"))


def replace_once(text: str, old: str, new: str) -> str:
    """Replace one exact occurrence."""
    assert text.count(old) == 1, old[:80]
    return text.replace(old, new)


def main() -> int:
    tree = pathlib.Path(sys.argv[1])
    new = pathlib.Path(sys.argv[2])
    unit_dir = tree / "tests/unit/melder/utilities/data_structures"

    path = unit_dir / "test_abstract_elastic_pool.py"
    text, crlf = read(path)
    text = replace_once(text, "from typing import Any, Dict, List\n", "from typing import Any, Dict, List\n\nimport pytest\n")
    start = text.index("def test_acquire_stretches_target_when_demand_exceeds_capacity() -> None:")
    end = text.index("def test_describe_reports_current_pool_state() -> None:")
    block = (new / "unit_block.py").read_text(encoding="utf-8").rstrip("\n") + "\n\n\n"
    text = text[:start] + block + text[end:]
    text = replace_once(text, '    assert snapshot["target_idle"] == 5\n', '    assert snapshot["target_idle"] == 4\n')
    write(path, text, crlf)

    path = unit_dir / "test_abstract_elastic_pool_multithreaded.py"
    text, crlf = read(path)
    start = text.index('@pytest.mark.parametrize("worker_count", [4, 8])\ndef test_multithreaded_overflow_decay_stays_within_bounds')
    end = text.index("def test_multithreaded_cleanup_after_hammer_destroys_retained_idle_once(")
    end = text.rindex("@pytest.mark.parametrize(", start, end)
    block = (new / "mt_block.py").read_text(encoding="utf-8").rstrip("\n") + "\n\n\n"
    text = text[:start] + block + text[end:]
    write(path, text, crlf)

    path = tree / "tests/component/melder/aether/conduit/test_named_lesser_directory_lifecycle.py"
    text, crlf = read(path)
    text = replace_once(
        text,
        "    root._conduit_pool._target_idle = 0\n",
        "    # A pool that keeps nothing (baseline = target = max = 0) destroys every return.\n"
        "    root._conduit_pool._baseline_idle = 0\n"
        "    root._conduit_pool._target_idle = 0\n"
        "    root._conduit_pool._max_idle = 0\n",
    )
    write(path, text, crlf)

    path = tree / "tests/experimentation/test_targeted_lesser_spellspace_meld_cycle_harness.py"
    text, crlf = read(path)
    text = replace_once(text, '''def _snapshot_pool_policy(pool: Any) -> Tuple[int, int]:
    """
    Snapshot the elastic-pool retention policy fields for later restore.

    Contract:
        Pools are elastic now (`AbstractElasticPool`); there is no boolean
        enabled flag. Retention is governed by `_target_idle` (release keeps
        while `len(_idle) <= _target_idle` after append-then-trim) and
        `_max_idle` (stretch ceiling), so those two fields ARE the policy
        this harness toggles.
    """
    return (pool._target_idle, pool._max_idle)
''', '''def _snapshot_pool_policy(pool: Any) -> Tuple[int, int, int]:
    """
    Snapshot the elastic-pool retention policy fields for later restore.

    Contract:
        Pools are elastic (`AbstractElasticPool`); there is no boolean
        enabled flag. Retention is governed by `_baseline_idle` (a return
        that leaves at most this many idle is kept on the fast path),
        `_target_idle` (the elastic target above it) and `_max_idle` (the
        ceiling), so those three fields ARE the policy this harness toggles
        (0.2.8234; through 0.2.8233 the harness toggled target and max only).
    """
    return (pool._baseline_idle, pool._target_idle, pool._max_idle)
''')
    text = replace_once(text, '''    pool._target_idle = max(pool._target_idle, 8)
    pool._max_idle = max(pool._max_idle, 8)
''', '''    pool._baseline_idle = max(pool._baseline_idle, 8)
    pool._target_idle = max(pool._target_idle, pool._baseline_idle)
    pool._max_idle = max(pool._max_idle, pool._baseline_idle)
''')
    text = replace_once(text, '''        With `_target_idle == 0` release's append-then-trim destroys every
        returned object, and with `_max_idle == 0` the post-miss stretch path
        returns immediately, so retention cannot re-enable mid-measurement.
    """
    with pool._lock:
        pool._idle.clear()
    pool._target_idle = 0
    pool._max_idle = 0
''', '''        With `_baseline_idle == _max_idle == 0` the pool is fixed-capacity at
        zero: every return destroys the returned object and nothing can
        stretch, so retention cannot re-enable mid-measurement.
    """
    with pool._lock:
        pool._idle.clear()
    pool._baseline_idle = 0
    pool._target_idle = 0
    pool._max_idle = 0
''')
    text = replace_once(text, '''def _restore_pool_policy(pool: Any, policy: Tuple[int, int]) -> None:
    """
    Restore a previously snapshotted elastic-pool retention policy.
    """
    pool._target_idle, pool._max_idle = policy
''', '''def _restore_pool_policy(pool: Any, policy: Tuple[int, int, int]) -> None:
    """
    Restore a previously snapshotted elastic-pool retention policy.
    """
    pool._baseline_idle, pool._target_idle, pool._max_idle = policy
''')
    write(path, text, crlf)

    target = tree / "tests/component/melder/aether/conduit/test_kernel_pool_elastic_retention.py"
    assert not target.exists()
    write(target, (new / "test_kernel_pool_elastic_retention.py").read_text(encoding="utf-8"), True)
    print("tests installed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
