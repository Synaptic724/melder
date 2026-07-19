"""
Unit tests for PhysicalSourceCache: the stat-guard truth law, the one read
law, LRU bounds, honesty channels, and thread discipline.

Runs only on 3.14t (melder package root import chain).
"""
import hashlib
import os
import threading

import pytest

from melder.crystallizer.crystal_analysis.physical_source_cache import (
    PhysicalSourceCache,
)


@pytest.fixture(autouse=True)
def clear_physical_source_cache():
    """
    Purpose:
        Isolate every test behind an empty shared cache.
    Contract:
        - Clears entries and counters before and after each test.
    Returns:
        None.
    """
    PhysicalSourceCache._clear_for_tests()
    yield
    PhysicalSourceCache._clear_for_tests()


def _write(tmp_path, name, text):
    """
    Write one source file and return its path.
    """
    path = tmp_path / name
    path.write_text(text, encoding="utf-8")
    return path


def test_cold_read_returns_text_sha_and_feeds_the_cache(tmp_path):
    """
    Purpose:
        The one read law: a cold read returns the text, its UTF-8 SHA256,
        and no error - and the next stat-guard lookup serves that sha.
    Contract:
        Served sha equals hashlib.sha256 of the exact text (truth law).
    """
    path = _write(tmp_path, "mod.py", "VALUE = 1\n")
    text, sha, error = PhysicalSourceCache.read_text_and_fingerprint(
        "mod", path
    )
    assert error is None
    assert text == "VALUE = 1\n"
    assert sha == hashlib.sha256(text.encode("utf-8")).hexdigest()
    assert PhysicalSourceCache.fingerprint_if_unchanged(path) == sha


def test_stat_hit_serves_without_reading_the_file(tmp_path, monkeypatch):
    """
    Purpose:
        The whole point: an unchanged stat serves the fingerprint with
        ZERO file reads.
    Contract:
        After priming, a poisoned read_text proves the guard never reads.
    """
    path = _write(tmp_path, "mod.py", "VALUE = 2\n")
    _, sha, _ = PhysicalSourceCache.read_text_and_fingerprint("mod", path)

    def _explode(*args, **kwargs):
        raise AssertionError("stat-hit lane must not read the file")

    monkeypatch.setattr(type(path), "read_text", _explode)
    assert PhysicalSourceCache.fingerprint_if_unchanged(path) == sha


def test_mtime_change_invalidates_the_guard(tmp_path):
    """
    Purpose:
        Truth law: any observable stat change forces a fresh read.
    Contract:
        A same-size content edit with a bumped mtime misses the guard and
        the re-read serves the NEW sha.
    """
    path = _write(tmp_path, "mod.py", "VALUE = 3\n")
    _, old_sha, _ = PhysicalSourceCache.read_text_and_fingerprint(
        "mod", path
    )
    path.write_text("VALUE = 9\n", encoding="utf-8")  # same byte length
    stat_result = path.stat()
    os.utime(
        path,
        ns=(stat_result.st_atime_ns, stat_result.st_mtime_ns + 1_000_000),
    )
    assert PhysicalSourceCache.fingerprint_if_unchanged(path) is None
    _, new_sha, _ = PhysicalSourceCache.read_text_and_fingerprint(
        "mod", path
    )
    assert new_sha != old_sha
    assert PhysicalSourceCache.fingerprint_if_unchanged(path) == new_sha


def test_size_change_invalidates_the_guard(tmp_path):
    """
    Purpose:
        The second guard axis: a size change misses even if mtime
        granularity were coarse.
    Contract:
        Appended content invalidates; the re-read serves the new sha.
    """
    path = _write(tmp_path, "mod.py", "VALUE = 4\n")
    _, old_sha, _ = PhysicalSourceCache.read_text_and_fingerprint(
        "mod", path
    )
    path.write_text("VALUE = 4\nEXTRA = True\n", encoding="utf-8")
    _, new_sha, _ = PhysicalSourceCache.read_text_and_fingerprint(
        "mod", path
    )
    assert new_sha != old_sha


def test_non_source_and_missing_paths_answer_no_source(tmp_path):
    """
    Purpose:
        Read-law parity with custody: non-source suffixes and missing
        files are "no source, not an error".
    Contract:
        (None, None, None) for both; None path likewise.
    """
    binary = tmp_path / "blob.so"
    binary.write_bytes(b"\x00\x01")
    assert PhysicalSourceCache.read_text_and_fingerprint(
        "blob", binary
    ) == (None, None, None)
    assert PhysicalSourceCache.read_text_and_fingerprint(
        "ghost", tmp_path / "ghost.py"
    ) == (None, None, None)
    assert PhysicalSourceCache.read_text_and_fingerprint(
        "pathless", None
    ) == (None, None, None)


def test_unreadable_file_reports_the_error_channel(tmp_path, monkeypatch):
    """
    Purpose:
        Honesty channel parity: a read failure returns error text in the
        walk-error shape, never raises, never caches.
    Contract:
        (None, None, error_text) naming the module and exception class.
    """
    path = _write(tmp_path, "mod.py", "VALUE = 5\n")

    def _explode(*args, **kwargs):
        raise PermissionError("locked")

    monkeypatch.setattr(type(path), "read_text", _explode)
    text, sha, error = PhysicalSourceCache.read_text_and_fingerprint(
        "mod", path
    )
    assert text is None and sha is None
    assert "mod" in error and "PermissionError" in error
    monkeypatch.undo()
    assert PhysicalSourceCache.fingerprint_if_unchanged(path) is None


def test_lru_cap_evicts_the_oldest_entry(tmp_path, monkeypatch):
    """
    Purpose:
        Bounded memory law: entries beyond capacity evict oldest-first.
    Contract:
        With capacity 2, the first-primed path misses after two newer
        primes; the newest two still serve.
    """
    monkeypatch.setattr(PhysicalSourceCache, "_MAX_ENTRIES", 2)
    paths = [
        _write(tmp_path, "m{0}.py".format(index), "V = {0}\n".format(index))
        for index in range(3)
    ]
    for index, path in enumerate(paths):
        PhysicalSourceCache.read_text_and_fingerprint(
            "m{0}".format(index), path
        )
    assert PhysicalSourceCache.fingerprint_if_unchanged(paths[0]) is None
    assert PhysicalSourceCache.fingerprint_if_unchanged(paths[1]) is not None
    assert PhysicalSourceCache.fingerprint_if_unchanged(paths[2]) is not None


def test_clear_for_tests_resets_entries_and_counters(tmp_path):
    """
    Purpose:
        Test-isolation hook contract.
    Contract:
        After clear: size 0, zeroed counters, primed path misses.
    """
    path = _write(tmp_path, "mod.py", "VALUE = 6\n")
    PhysicalSourceCache.read_text_and_fingerprint("mod", path)
    PhysicalSourceCache._clear_for_tests()
    stats = PhysicalSourceCache._stats_for_tests()
    assert stats["size"] == 0 and stats["hits"] == 0 and stats["misses"] == 0
    assert PhysicalSourceCache.fingerprint_if_unchanged(path) is None


def test_concurrent_readers_and_guards_stay_consistent(tmp_path):
    """
    Purpose:
        3.14t lock law: parallel cold reads and stat-guard lookups over
        shared paths never tear entries or serve a wrong sha.
    Contract:
        Every served fingerprint matches one file's true sha; no thread
        raises.
    """
    paths = [
        _write(tmp_path, "t{0}.py".format(index), "T = {0}\n".format(index))
        for index in range(4)
    ]
    truth = {
        str(path): hashlib.sha256(
            path.read_text(encoding="utf-8").encode("utf-8")
        ).hexdigest()
        for path in paths
    }
    errors = []
    barrier = threading.Barrier(8)

    def _hammer(worker_index):
        try:
            barrier.wait(5.0)
            for round_index in range(50):
                path = paths[(worker_index + round_index) % len(paths)]
                served = PhysicalSourceCache.fingerprint_if_unchanged(path)
                if served is None:
                    _, served, _ = (
                        PhysicalSourceCache.read_text_and_fingerprint(
                            path.stem, path
                        )
                    )
                if served != truth[str(path)]:
                    errors.append((str(path), served))
        except Exception as exc:
            errors.append(repr(exc))

    threads = [
        threading.Thread(target=_hammer, args=(index,), daemon=True)
        for index in range(8)
    ]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join(timeout=10.0)
    assert errors == []
