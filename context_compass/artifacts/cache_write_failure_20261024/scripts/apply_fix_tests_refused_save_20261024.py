"""Extend the CachingSystem refused-save unit tests for the fix (melder_0, 2026-10-24; Note 21).

Anchored read-modify-write of tests/unit/melder/utilities/test_caching_system_refused_save.py: the module docstring
covers the fix's contract, the rename refusal can be limited to a number of refusals and records every rename
source, and new tests pin `emit()`'s bool, the kept payloads, the Windows-only retry, the one WARNING, the per-writer
temp name, a refused temp write or folder, and an unremovable temp file (patch cache_save_best_effort_2026_10_24,
M1). The first test, written before the fix, is unchanged.
"""
import pathlib
import sys

PATH = pathlib.Path.home() / "mnt/melder_private/tests/unit/melder/utilities/test_caching_system_refused_save.py"
COMPONENT = "tests/component/melder/aether/conduit/test_conduit_component_refused_cache_save_does_not_fail_meld.py"


def once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        sys.exit(f"ANCHOR {label}: found {count}")
    return text.replace(old, new)


NEW_TESTS = '''

def _refuse_temp_writes(monkeypatch: pytest.MonkeyPatch, folder: Path) -> None:
    """
    Refuse every write of a `.tmp` file under `folder`, as a read-only or full folder refuses it.

    Args:
        monkeypatch: Restores `Path.write_bytes` after the test.
        folder: Resolved cache root; only temp files under it are refused.
    """
    real_write_bytes: Callable[..., int] = Path.write_bytes

    def write_bytes(path: Path, data: Any) -> int:
        """Refuse a temp-file write under the folder; pass any other through."""
        if path.name.endswith(".tmp") and path.resolve().is_relative_to(folder):
            raise PermissionError(errno.EACCES, "Permission denied (injected)", os.fspath(path))
        return real_write_bytes(path, data)

    monkeypatch.setattr(Path, "write_bytes", write_bytes)


def _bundle_folder_listing(caching_system: CachingSystem) -> list[str]:
    """
    Return the sorted names in the bundle's frame folder, or [] when the folder does not exist.

    Args:
        caching_system: The utility whose frame folder to list.

    Returns:
        list[str]: Sorted file names.
    """
    folder = caching_system.bundle_path.parent
    if not folder.exists():
        return []
    return sorted(path.name for path in folder.iterdir())


def test_save_returns_true_and_leaves_only_the_bundle(tmp_path: Path) -> None:
    """
    A save that is not refused returns True and leaves the bundle alone in its folder.

    Args:
        tmp_path: The test's isolated cache root.
    """
    caching_system = _make_cache_utility(tmp_path)
    try:
        caching_system.upsert_spell_payload("a" * 64, {"resolve_route_key": "saved"})
        saved = caching_system.emit()
        bundle_name = caching_system.bundle_path.name
        listing = _bundle_folder_listing(caching_system)
    finally:
        caching_system.cleanup()

    assert saved is True
    assert listing == [bundle_name]


def test_refused_save_returns_false_and_the_next_save_writes_what_it_kept(
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    A refused save returns False and keeps its payloads; the next save writes them with any staged since.

    Contract (0.2.8266): `emit()` reports the refusal instead of raising, and the in-memory cache it could not
    write stays staged, so a later save loses nothing.

    Args:
        tmp_path: The test's isolated cache root.
        monkeypatch: Restores the patched rename and the retry switch.
    """
    monkeypatch.setattr(CachingSystem, "RETRY_REFUSED_RENAME", False)
    caching_system = _make_cache_utility(tmp_path)
    try:
        caching_system.upsert_spell_payload("a" * 64, {"resolve_route_key": "kept"})
        renames = _RefusedRenames(monkeypatch, tmp_path.resolve(), times=1)
        refused = caching_system.emit()
        caching_system.upsert_spell_payload("b" * 64, {"resolve_route_key": "later"})
        saved = caching_system.emit()
    finally:
        caching_system.cleanup()

    assert renames.refusals == 1
    assert refused is False
    assert saved is True
    reloaded = _make_cache_utility(tmp_path)
    try:
        assert reloaded.get_spell_payload("a" * 64) == {"resolve_route_key": "kept"}
        assert reloaded.get_spell_payload("b" * 64) == {"resolve_route_key": "later"}
    finally:
        reloaded.cleanup()


def test_refused_rename_is_retried_until_allowed_when_retry_is_on(
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    With the Windows retry on, a rename refused twice and then allowed saves the bundle.

    Args:
        tmp_path: The test's isolated cache root.
        monkeypatch: Restores the patched rename, the retry switch and the delay.
    """
    monkeypatch.setattr(CachingSystem, "RETRY_REFUSED_RENAME", True)
    monkeypatch.setattr(CachingSystem, "REPLACE_RETRY_DELAY_SECONDS", 0.0)
    caching_system = _make_cache_utility(tmp_path)
    try:
        caching_system.upsert_spell_payload("a" * 64, {"resolve_route_key": "retried"})
        renames = _RefusedRenames(monkeypatch, tmp_path.resolve(), times=2)
        saved = caching_system.emit()
        listing = _bundle_folder_listing(caching_system)
        bundle_name = caching_system.bundle_path.name
    finally:
        caching_system.cleanup()

    assert saved is True
    assert renames.refusals == 2
    assert len(renames.sources) == 3
    assert listing == [bundle_name]


def test_refused_rename_is_not_retried_when_retry_is_off(
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    With the retry off (every platform but Windows), the first refused rename makes the save refused.

    Args:
        tmp_path: The test's isolated cache root.
        monkeypatch: Restores the patched rename and the retry switch.
    """
    monkeypatch.setattr(CachingSystem, "RETRY_REFUSED_RENAME", False)
    caching_system = _make_cache_utility(tmp_path)
    try:
        caching_system.upsert_spell_payload("a" * 64, {"resolve_route_key": "refused"})
        renames = _RefusedRenames(monkeypatch, tmp_path.resolve())
        saved = caching_system.emit()
    finally:
        caching_system.cleanup()

    assert saved is False
    assert renames.refusals == 1


def test_lasting_refusal_with_retry_on_gives_up_after_the_attempt_budget(
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    With the retry on, a rename refused on every attempt is tried REPLACE_ATTEMPTS times, then the save is refused.

    Args:
        tmp_path: The test's isolated cache root.
        monkeypatch: Restores the patched rename, the retry switch and the delay.
    """
    monkeypatch.setattr(CachingSystem, "RETRY_REFUSED_RENAME", True)
    monkeypatch.setattr(CachingSystem, "REPLACE_RETRY_DELAY_SECONDS", 0.0)
    caching_system = _make_cache_utility(tmp_path)
    try:
        caching_system.upsert_spell_payload("a" * 64, {"resolve_route_key": "refused"})
        renames = _RefusedRenames(monkeypatch, tmp_path.resolve())
        saved = caching_system.emit()
        listing = _bundle_folder_listing(caching_system)
    finally:
        caching_system.cleanup()

    assert saved is False
    assert renames.refusals == CachingSystem.REPLACE_ATTEMPTS
    assert listing == []


def test_only_the_first_refused_save_of_a_bundle_logs_a_warning(
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
        caplog: pytest.LogCaptureFixture,
) -> None:
    """
    The first refused save of a bundle logs one WARNING naming the bundle and the remedy; later ones log below it.

    Args:
        tmp_path: The test's isolated cache root.
        monkeypatch: Restores the patched rename and the retry switch.
        caplog: Captures the cache utility's log records.
    """
    monkeypatch.setattr(CachingSystem, "RETRY_REFUSED_RENAME", False)
    caching_system = _make_cache_utility(tmp_path)
    try:
        caching_system.upsert_spell_payload("a" * 64, {"resolve_route_key": "refused"})
        _RefusedRenames(monkeypatch, tmp_path.resolve())
        first = caching_system.emit()
        second = caching_system.emit()
        bundle_path = caching_system.bundle_path
    finally:
        caching_system.cleanup()

    warnings = [
        record for record in caplog.records
        if record.name == "caching-system-refused-save-test" and record.levelno == logging.WARNING
    ]
    assert first is False
    assert second is False
    assert len(warnings) == 1
    assert str(bundle_path) in warnings[0].getMessage()
    assert "with_system_caching_enabled(False)" in warnings[0].getMessage()


def test_each_writer_saves_through_its_own_temp_file(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """
    The temp file carries the process id and the thread id, so two threads (or processes) never share one.

    Args:
        tmp_path: The test's isolated cache root.
        monkeypatch: Restores the patched rename.
    """
    caching_system = _make_cache_utility(tmp_path)
    try:
        caching_system.upsert_spell_payload("a" * 64, {"resolve_route_key": "saved"})
        renames = _RefusedRenames(monkeypatch, tmp_path.resolve(), times=0)
        caching_system.emit()
        other_thread = threading.Thread(target=caching_system.emit)
        other_thread.start()
        other_thread.join()
        bundle_name = caching_system.bundle_path.name
        listing = _bundle_folder_listing(caching_system)
    finally:
        caching_system.cleanup()

    this_thread_name = f"{bundle_name}.{os.getpid()}.{threading.get_ident()}.tmp"
    other_thread_name = Path(renames.sources[1]).name
    assert renames.refusals == 0
    assert Path(renames.sources[0]).name == this_thread_name
    assert other_thread_name != this_thread_name
    assert other_thread_name.startswith(f"{bundle_name}.{os.getpid()}.")
    assert other_thread_name.endswith(".tmp")
    assert listing == [bundle_name]


def test_refused_temp_write_returns_false_and_leaves_the_bundle_as_it_was(
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    A temp write the folder refuses makes the save refused; the bundle saved before stays as it was.

    Args:
        tmp_path: The test's isolated cache root.
        monkeypatch: Restores `Path.write_bytes`.
    """
    caching_system = _make_cache_utility(tmp_path)
    try:
        caching_system.upsert_spell_payload("a" * 64, {"resolve_route_key": "saved"})
        saved = caching_system.emit()
        caching_system.upsert_spell_payload("b" * 64, {"resolve_route_key": "refused"})
        _refuse_temp_writes(monkeypatch, tmp_path.resolve())
        refused = caching_system.emit()
        bundle_name = caching_system.bundle_path.name
        listing = _bundle_folder_listing(caching_system)
    finally:
        caching_system.cleanup()

    assert saved is True
    assert refused is False
    assert listing == [bundle_name]
    reloaded = _make_cache_utility(tmp_path)
    try:
        assert reloaded.get_spell_payload("a" * 64) == {"resolve_route_key": "saved"}
        assert reloaded.get_spell_payload("b" * 64) is None
    finally:
        reloaded.cleanup()


def test_refused_cache_folder_returns_false_and_creates_nothing(
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    A frame folder that cannot be created makes the save refused, and no file is written.

    Args:
        tmp_path: The test's isolated cache root.
        monkeypatch: Restores `Path.mkdir`.
    """
    folder = tmp_path.resolve()
    real_mkdir: Callable[..., None] = Path.mkdir

    def mkdir(path: Path, *args: Any, **kwargs: Any) -> None:
        """Refuse creating a folder under the cache root; pass any other through."""
        if path.resolve().is_relative_to(folder):
            raise PermissionError(errno.EACCES, "Permission denied (injected)", os.fspath(path))
        real_mkdir(path, *args, **kwargs)

    caching_system = _make_cache_utility(tmp_path)
    try:
        caching_system.upsert_spell_payload("a" * 64, {"resolve_route_key": "refused"})
        monkeypatch.setattr(Path, "mkdir", mkdir)
        refused = caching_system.emit()
        frame_folder = caching_system.bundle_path.parent
    finally:
        caching_system.cleanup()

    assert refused is False
    assert not frame_folder.exists()


def test_temp_file_that_cannot_be_removed_is_logged_not_raised(
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
        caplog: pytest.LogCaptureFixture,
) -> None:
    """
    A refused save whose temp file cannot be removed still returns False and logs the leftover file.

    Args:
        tmp_path: The test's isolated cache root.
        monkeypatch: Restores the patched rename, `Path.unlink` and the retry switch.
        caplog: Captures the cache utility's log records.
    """
    monkeypatch.setattr(CachingSystem, "RETRY_REFUSED_RENAME", False)
    folder = tmp_path.resolve()
    real_unlink: Callable[..., None] = Path.unlink

    def unlink(path: Path, missing_ok: bool = False) -> None:
        """Refuse removing a temp file under the cache root; pass any other through."""
        if path.name.endswith(".tmp") and path.resolve().is_relative_to(folder):
            raise PermissionError(errno.EACCES, "Permission denied (injected)", os.fspath(path))
        real_unlink(path, missing_ok=missing_ok)

    caching_system = _make_cache_utility(tmp_path)
    try:
        caching_system.upsert_spell_payload("a" * 64, {"resolve_route_key": "refused"})
        _RefusedRenames(monkeypatch, folder)
        monkeypatch.setattr(Path, "unlink", unlink)
        refused = caching_system.emit()
        temp_name = f"{caching_system.bundle_path.name}.{os.getpid()}.{threading.get_ident()}.tmp"
        listing = _bundle_folder_listing(caching_system)
    finally:
        caching_system.cleanup()

    leftover_messages = [
        record.getMessage() for record in caplog.records
        if record.levelno == logging.WARNING and "Could not remove the temp cache file" in record.getMessage()
    ]
    assert refused is False
    assert listing == [temp_name]
    assert len(leftover_messages) == 1
    assert temp_name in leftover_messages[0]
'''


def main() -> None:
    text = PATH.read_text(encoding="utf-8")
    text = once(text, '''"""
Regression test: a refused creation-cache save leaves no temp file behind.
''', '''"""
Regression tests: a refused creation-cache save is reported, not raised, and leaves nothing behind.
''', "title")
    text = once(text, '''What this test asserts:
    After a save whose rename is refused every time, the frame folder holds the bundle and nothing else, and the
    bundle saved before still loads with exactly what it held (emit's atomic replace: a refused save never touches
    the bundle). Whether `emit()` then raises or reports the failure is the fix's choice and is not asserted. The
    meld doors' side is
''', '''What these tests assert:
    The first test, written before the fix and red on 0.2.8265: after a save whose rename is refused every time,
    the frame folder holds the bundle and nothing else, and the bundle saved before still loads with exactly what it
    held (emit's atomic replace: a refused save never touches the bundle). It does not assert how `emit()` reports
    the refusal. The others pin the fix (0.2.8266, the owner's D1-D4): `emit()` returns True for a written save and
    False for a refused one, never raising OSError; a refused save keeps its payloads for the next save; the
    Windows-only rename retry (RETRY_REFUSED_RENAME, set explicitly here so every platform runs both ways) tries
    REPLACE_ATTEMPTS times; the first refused save of a bundle logs one WARNING; each writer saves through its own
    temp file; a refused temp write or folder leaves nothing; a temp file that cannot be removed is logged. The
    meld doors' side is
''', "docstring")
    text = once(text, "import logging\nimport os\nfrom collections.abc import Callable\nfrom pathlib import Path\n"
                      "from typing import Any\n",
                "import logging\nimport os\nimport threading\nfrom collections.abc import Callable\n"
                "from pathlib import Path\nfrom typing import Any, Optional\n", "imports")
    text = once(text, '''    Refuses every rename onto a `.meldercache` bundle under one folder, as Windows refuses a bundle in use.

    Contract:
        Wraps `os.replace` (which `Path.replace` calls) through `monkeypatch`, which restores it after the test. A
        rename whose destination is a `.meldercache` file under `folder` raises PermissionError (errno EACCES;
        Windows reports [WinError 5]); every other rename passes through unchanged. `refusals` counts the refusals.
    """

    def __init__(self, monkeypatch: pytest.MonkeyPatch, folder: Path) -> None:
        """
        Install the wrapper.

        Args:
            monkeypatch: The test's monkeypatch fixture; it restores `os.replace` at teardown.
            folder: Resolved cache root; only renames onto `.meldercache` files under it are refused.
        """
        self.refusals: int = 0
        real_replace: Callable[..., None] = os.replace

        def replace(source: Any, target: Any, *args: Any, **kwargs: Any) -> None:
            """Refuse a rename onto a bundle under the folder; pass any other through."""
            destination = Path(os.fspath(target)).resolve()
            if ".meldercache" in destination.name and destination.is_relative_to(folder):
                self.refusals += 1
''', '''    Refuses renames onto a `.meldercache` bundle under one folder, as Windows refuses a bundle in use.

    Contract:
        Wraps `os.replace` (which `Path.replace` calls) through `monkeypatch`, which restores it after the test. A
        rename whose destination is a `.meldercache` file under `folder` raises PermissionError (errno EACCES;
        Windows reports [WinError 5]) - every such rename, or only the first `times`; every other rename passes
        through unchanged. `refusals` counts the refusals and `sources` records the source of every rename onto a
        bundle under the folder, refused or not.
    """

    def __init__(self, monkeypatch: pytest.MonkeyPatch, folder: Path, times: Optional[int] = None) -> None:
        """
        Install the wrapper.

        Args:
            monkeypatch: The test's monkeypatch fixture; it restores `os.replace` at teardown.
            folder: Resolved cache root; only renames onto `.meldercache` files under it are refused.
            times: How many renames to refuse before allowing the rest; None refuses every one.
        """
        self.refusals: int = 0
        self.sources: list[str] = []
        real_replace: Callable[..., None] = os.replace

        def replace(source: Any, target: Any, *args: Any, **kwargs: Any) -> None:
            """Refuse a rename onto a bundle under the folder while refusals remain; pass any other through."""
            destination = Path(os.fspath(target)).resolve()
            if ".meldercache" in destination.name and destination.is_relative_to(folder):
                self.sources.append(os.fspath(source))
            if (".meldercache" in destination.name and destination.is_relative_to(folder)
                    and (times is None or self.refusals < times)):
                self.refusals += 1
''', "helper")
    if not text.endswith("        reloaded.cleanup()\n"):
        sys.exit("TAIL")
    text = text + NEW_TESTS
    if "\\r" in text or "\r" in text:
        sys.exit("CR")
    compile(text, str(PATH), "exec")
    PATH.write_text(text, encoding="utf-8", newline="\n")
    print("wrote", PATH.name, len(text.splitlines()), "lines")


if __name__ == "__main__":
    main()
