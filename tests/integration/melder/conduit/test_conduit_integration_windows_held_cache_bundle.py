"""
Windows-only integration tests: the creation-cache save against a rename Windows itself refuses.

Why these exist (TASK-2026-10-24-windows_held_cache_bundle_test; the owner's ask, chat 2026-10-24: "dude add it to my
machine and see what happens I can run whatever commands you want"):
    0.2.8266 (TASK-2026-10-24-cache_file_write_failure_fails_meld) made a creation-cache save that the operating
    system refuses a reported failure instead of a raised one: the owner's MelderOps run had failed a meld with
    PermissionError [WinError 5] when Windows refused the rename of the save's temp file onto a bundle another handle
    held open. On Windows the save also retries such a refusal (`CachingSystem.RETRY_REFUSED_RENAME`:
    `REPLACE_ATTEMPTS` attempts, sleeping `REPLACE_RETRY_DELAY_SECONDS` times the attempt number between them, about
    100 ms in all). The fix's own tests inject the refusal at `os.replace`, because Linux never refuses a rename for
    sharing. These tests inject nothing: they hold the bundle open with Python's `open()`, which on Windows shares
    read and write access but not delete access, so Windows itself refuses a rename onto it.

What they assert (each prints what it saw; run pytest with `-s` to see it):
    1. The premise: a rename onto a file held open raises PermissionError, and succeeds once the handle is closed.
    2. A hold that ends while the save retries: the save returns True and the bundle holds the new payload.
    3. A hold that outlasts the retries: the save returns False after exactly `REPLACE_ATTEMPTS` refused renames,
       the bundle is byte-for-byte as it was, no temp file is left and one WARNING is logged; once the hold ends,
       the next save writes everything the refused one kept.
    4. A meld whose save Windows refuses: a spell bound after conjure is first melded while its root's bundle is
       held. The meld returns its object although its save is refused `REPLACE_ATTEMPTS` times, a second meld
       returns the same object and saves nothing, and after the hold the first meld of another late spell saves
       the bundle with both plans.

How:
    `_HeldFile` holds a file open. `_RenameSpy` wraps `os.replace` (which `Path.replace` calls): it passes every
    rename through to the real call and records each one onto the bundle - refused, with the operating system's
    PermissionError re-raised unchanged, or done. It refuses nothing itself. Test 2 ends its hold from the spy after
    the second refusal, so where the hold ends does not depend on timing. An on-access scanner can only add
    refusals; the tests that let a save finish allow for that and print every count.

Off Windows the file is skipped. The ticket's artifacts keep a pytest plugin that runs it on Linux by emulating the
refusal (a rename onto a file the process holds open raises PermissionError) with the retry turned on.
"""

import logging
import os
import shutil
import sys
import time
from collections.abc import Callable, Iterator
from pathlib import Path
from typing import IO, Any, List, Optional

import pytest

from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spellbook import Spellbook
from melder.nexus.nexus import Nexus
from melder.utilities.caching_system.caching_system import CachingSystem

pytestmark = [
    pytest.mark.integration,
    pytest.mark.skipif(
        sys.platform != "win32",
        reason="Windows only: it needs Windows to refuse a rename onto a file held open.",
    ),
]


class HeldBundleSettings:
    """`unique`, bound before conjure, so the conjure-time save writes the bundle the meld test then holds."""


class HeldBundleReport:
    """`unique`, bound after conjure; its first meld compiles it, stages its plan and saves while the bundle is held."""


class AfterHoldReport:
    """`unique`, bound after the hold ends; its first meld saves the bundle with its plan and the one kept before."""


class _HeldFile:
    """
    Holds one file open for reading, as an on-access scanner or another reader holds a bundle on Windows.

    Contract:
        - `hold()` opens the file with Python's `open()` in binary read mode. On Windows that handle shares read and
          write access but not delete access, so Windows refuses a rename onto the file while it is open; elsewhere
          the handle refuses nothing.
        - `release()` closes the handle; it is idempotent, so a test may end the hold early (from a spy) and again
          in its `finally`.

    Threading:
        Not thread-safe; each test holds and releases on one thread.
    """

    def __init__(self, path: Path) -> None:
        """
        Remember the file; nothing is opened yet.

        Args:
            path: The file to hold.
        """
        self._path: Path = path
        self._handle: Optional[IO[bytes]] = None

    def hold(self) -> None:
        """
        Open the file for reading and keep the handle.

        Raises:
            RuntimeError: This object already holds the file.
            OSError: The file cannot be opened.
        """
        if self._handle is not None:
            raise RuntimeError(f"'{self._path}' is already held by this test.")
        self._handle = self._path.open("rb")

    def release(self) -> None:
        """
        Close the handle when the file is held; once released, calling it again does nothing.
        """
        if self._handle is None:
            return
        self._handle.close()
        self._handle = None


class _RenameSpy:
    """
    Records the renames onto one bundle and passes every rename through to the real `os.replace`.

    Contract:
        - Wraps `os.replace` (which `Path.replace` calls) through `monkeypatch`, which restores it after the test.
        - A rename whose destination is the bundle goes to the real call. When the real call raises PermissionError
          the spy appends the error to `refusals`, runs `on_refusal` with the number of refusals so far and re-raises
          the error unchanged; when it returns, the spy counts it in `successes`. Every other rename passes through
          unrecorded.
        - It refuses nothing itself: every refusal it records is the operating system's.
        - Destinations are compared after `os.path.abspath` and `os.path.normcase`, so case and separators do not
          matter on Windows.

    Threading:
        Not thread-safe; each test renames on one thread.
    """

    def __init__(
            self,
            monkeypatch: pytest.MonkeyPatch,
            bundle_path: Path,
            on_refusal: Optional[Callable[[int], None]] = None,
    ) -> None:
        """
        Install the wrapper.

        Args:
            monkeypatch: The test's monkeypatch fixture; it restores `os.replace` at teardown.
            bundle_path: The bundle whose renames are recorded.
            on_refusal: Called after each recorded refusal with the refusal count, before the error is re-raised.
        """
        self.refusals: List[PermissionError] = []
        self.successes: int = 0
        self._bundle_key: str = os.path.normcase(os.path.abspath(os.fspath(bundle_path)))
        self._on_refusal: Optional[Callable[[int], None]] = on_refusal
        real_replace: Callable[..., None] = os.replace

        def replace(source: Any, target: Any, *args: Any, **kwargs: Any) -> None:
            """Pass a rename through to the real call; record it when its destination is the bundle."""
            if os.path.normcase(os.path.abspath(os.fspath(target))) != self._bundle_key:
                real_replace(source, target, *args, **kwargs)
                return
            try:
                real_replace(source, target, *args, **kwargs)
            except PermissionError as error:
                self.refusals.append(error)
                if self._on_refusal is not None:
                    self._on_refusal(len(self.refusals))
                raise
            self.successes += 1

        monkeypatch.setattr(os, "replace", replace)


def _windows_error_code(error: OSError) -> Optional[int]:
    """
    Return the Windows error code an OSError carries, or None off Windows.

    Args:
        error: The error a rename raised.

    Returns:
        Optional[int]: `error.winerror` on Windows (5 is ERROR_ACCESS_DENIED, 32 ERROR_SHARING_VIOLATION), else None.
    """
    if sys.platform == "win32":
        return error.winerror
    return None


def _refusal_codes(refusals: List[PermissionError]) -> List[Optional[int]]:
    """
    Return the Windows error code of each recorded refusal, in order.

    Args:
        refusals: The errors a `_RenameSpy` recorded.

    Returns:
        List[Optional[int]]: One code per refusal (None off Windows).
    """
    return [_windows_error_code(error) for error in refusals]


def _test_logger() -> logging.Logger:
    """
    Return the stdlib logger these tests hand their cache utilities, so a test can pick out its records.

    Returns:
        logging.Logger: The logger named "windows-held-bundle-test".
    """
    return logging.getLogger("windows-held-bundle-test")


def _make_cache_utility(cache_root_path: Path) -> CachingSystem:
    """
    Build one cache utility over a test's own cache root, logging to the tests' logger.

    Args:
        cache_root_path: The test's cache root.

    Returns:
        CachingSystem: A utility for frame "frame-a" and conduit "root"; its bundle is
            `<cache_root_path>/frame-a/root.meldercache`.
    """
    return CachingSystem(
        frame_name="frame-a",
        conduit_name="root",
        cache_root_path=cache_root_path,
        logger=_test_logger(),
    )


def _folder_listing(folder: Path) -> List[str]:
    """
    Return the sorted names in a folder, or [] when it does not exist.

    Args:
        folder: The folder to list.

    Returns:
        List[str]: Sorted file names.
    """
    if not folder.exists():
        return []
    return sorted(path.name for path in folder.iterdir())


def _replace_until_allowed(source: Path, target: Path, attempts: int, delay_seconds: float) -> int:
    """
    Rename `source` onto `target`, retrying a PermissionError, and return the try that succeeded.

    Contract:
        Tries up to `attempts` times, sleeping `delay_seconds` between tries; the last try's PermissionError
        propagates. Used after a hold is released, because an on-access scanner may open a just-written file.

    Args:
        source: The file to rename.
        target: The destination it replaces.
        attempts: Tries in all, at least 1.
        delay_seconds: Sleep between two tries.

    Returns:
        int: The 1-based try that succeeded.

    Raises:
        PermissionError: Every try was refused.
    """
    attempt = 1
    while True:
        try:
            os.replace(source, target)
            return attempt
        except PermissionError:
            if attempt >= attempts:
                raise
        time.sleep(delay_seconds)
        attempt += 1


def _reset_world() -> None:
    """Install a fresh Aether (and Nexus) and hand it to Spellbook and Conduit."""
    Nexus._reset_singleton_for_tests()
    Aether._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether


@pytest.fixture
def fresh_world() -> Iterator[None]:
    """
    Give the test a fresh Aether and reset it again afterwards.

    Yields:
        None.
    """
    _reset_world()
    yield
    _reset_world()


@pytest.fixture
def cache_frame(fresh_world: None) -> Iterator[Callable[[str], Path]]:
    """
    Turn caching on for a frame of the test's own and empty its cache folder.

    Contract:
        The call takes a frame name unique to its test, ensures the frame, enables caching on its configuration
        (the default cache root, under the melder package), removes whatever an earlier run left in that frame's
        cache folder and returns the folder. At teardown each such folder is removed, best-effort: on Windows a
        scanner may still hold a just-written bundle, and the next run's preparation removes what is left.

    Args:
        fresh_world: Gives the test a fresh Aether first.

    Yields:
        Callable[[str], Path]: The preparation call, returning the frame's cache folder.
    """
    folders: List[Path] = []

    def prepare(frame_name: str) -> Path:
        """
        Prepare one frame's cache folder.

        Args:
            frame_name: Frame name unique to the calling test.

        Returns:
            Path: The frame's cache folder, resolved and empty.
        """
        configuration = Aether()._ensure_frame(frame_name).frame_configuration
        assert configuration is not None
        configuration.with_system_caching_enabled(True)
        folder = (configuration.resolve_conjure_cache_root_path() / frame_name).resolve()
        if folder.exists():
            shutil.rmtree(folder)
        folders.append(folder)
        return folder

    yield prepare
    for folder in folders:
        shutil.rmtree(folder, ignore_errors=True)


def test_windows_refuses_a_rename_onto_a_file_held_open(tmp_path: Path) -> None:
    """
    The premise: a rename onto a file held open is refused with PermissionError, and allowed once it is closed.

    Contract:
        `target.bin` is held open with `open(..., "rb")` and `source.bin` is renamed onto it: Windows raises
        PermissionError ([WinError 5] in the owner's MelderOps failure; [WinError 32] would be a PermissionError
        too, and the save retries both). Once the handle is closed the rename succeeds and the target holds the
        source's bytes; it is tried up to 50 times, 20 ms apart, because an on-access scanner may open the
        just-written files on its own, and the try that succeeded is printed. If the held rename were allowed,
        `open()` could not cause the refusal the 0.2.8266 retry guards against, and tests 2-4 would fail too.

    Args:
        tmp_path: The test's own folder.
    """
    target = tmp_path / "target.bin"
    source = tmp_path / "source.bin"
    target.write_bytes(b"held")
    source.write_bytes(b"replacement")
    held = _HeldFile(target)
    held.hold()
    try:
        with pytest.raises(PermissionError) as refused:
            os.replace(source, target)
    finally:
        held.release()
    allowed_on_try = _replace_until_allowed(source, target, attempts=50, delay_seconds=0.02)

    print(
        f"\n[held-bundle] premise: Python {sys.version.split()[0]} on {sys.platform}. A rename onto the held file "
        f"raised PermissionError (Windows code {_windows_error_code(refused.value)}): {refused.value}. After the "
        f"close it was allowed on try {allowed_on_try}. Save retry: {CachingSystem.RETRY_REFUSED_RENAME}, "
        f"{CachingSystem.REPLACE_ATTEMPTS} attempts, {CachingSystem.REPLACE_RETRY_DELAY_SECONDS} s step."
    )
    assert target.read_bytes() == b"replacement"
    assert not source.exists()


def test_save_waits_out_a_hold_that_ends_while_it_retries(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """
    A hold that ends after two refused renames: the save retries, writes the bundle and returns True.

    Contract:
        A first payload is saved, a second staged, and the bundle held open; the spy ends the hold once Windows has
        refused the rename twice. The save, still inside its `REPLACE_ATTEMPTS` attempts, renames on a later one
        and returns True; the bundle then holds both payloads and its folder holds it alone (no temp file). A
        scanner may add refusals: the test needs at least the two the hold causes and fewer than
        `REPLACE_ATTEMPTS`, and prints the count, the Windows codes and the time the save took.

    Args:
        tmp_path: The test's cache root.
        monkeypatch: Restores `os.replace` after the test.
    """
    caching_system = _make_cache_utility(tmp_path)
    bundle_path = caching_system.bundle_path
    held = _HeldFile(bundle_path)

    def end_the_hold_after_two(refusals: int) -> None:
        """
        End the hold once Windows has refused the rename twice.

        Args:
            refusals: Refusals the spy has recorded so far.
        """
        if refusals == 2:
            held.release()

    try:
        caching_system.upsert_spell_payload("a" * 64, {"plan": "saved before the hold"})
        saved_before = caching_system.emit()
        caching_system.upsert_spell_payload("b" * 64, {"plan": "saved through the hold"})
        held.hold()
        spy = _RenameSpy(monkeypatch, bundle_path, on_refusal=end_the_hold_after_two)
        started = time.perf_counter()
        saved = caching_system.emit()
        save_seconds = time.perf_counter() - started
        listing = _folder_listing(bundle_path.parent)
    finally:
        held.release()
        caching_system.cleanup()

    print(
        f"\n[held-bundle] short hold: the save returned {saved} after {len(spy.refusals)} refused renames "
        f"(Windows codes {_refusal_codes(spy.refusals)}) and {spy.successes} done, in {save_seconds:.3f} s; "
        f"folder: {listing}."
    )
    assert saved_before is True
    assert saved is True
    assert 2 <= len(spy.refusals) < CachingSystem.REPLACE_ATTEMPTS
    assert spy.successes == 1
    assert listing == [bundle_path.name]
    reloaded = _make_cache_utility(tmp_path)
    try:
        assert reloaded.get_spell_payload("a" * 64) == {"plan": "saved before the hold"}
        assert reloaded.get_spell_payload("b" * 64) == {"plan": "saved through the hold"}
    finally:
        reloaded.cleanup()


def test_save_outlasted_by_a_hold_returns_false_and_keeps_the_bundle(
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
        caplog: pytest.LogCaptureFixture,
) -> None:
    """
    A hold that outlasts the retries: the save returns False, the bundle stays as it was, the next save writes all.

    Contract:
        A first payload is saved, a second staged, and the bundle held open for the whole save. Windows refuses the
        rename on every one of the `REPLACE_ATTEMPTS` attempts (the spy records exactly that many) and the save
        returns False: the bundle reads byte for byte as before, its folder holds it alone (the temp file was
        removed) and one WARNING names it. Once the hold ends, the next save returns True and the bundle holds both
        payloads, the one the refused save kept included. On 0.2.8265 the refused save raised its PermissionError
        and left its temp file beside the bundle.

    Args:
        tmp_path: The test's cache root.
        monkeypatch: Restores `os.replace` after the test.
        caplog: Captures the cache utility's log records.
    """
    caching_system = _make_cache_utility(tmp_path)
    bundle_path = caching_system.bundle_path
    held = _HeldFile(bundle_path)
    try:
        caching_system.upsert_spell_payload("a" * 64, {"plan": "saved before the hold"})
        saved_before = caching_system.emit()
        bytes_before = bundle_path.read_bytes()
        caching_system.upsert_spell_payload("b" * 64, {"plan": "kept through the hold"})
        held.hold()
        spy = _RenameSpy(monkeypatch, bundle_path)
        started = time.perf_counter()
        refused = caching_system.emit()
        refused_seconds = time.perf_counter() - started
        refusals_during_hold = list(spy.refusals)
        bytes_during_hold = bundle_path.read_bytes()
        listing_during_hold = _folder_listing(bundle_path.parent)
        held.release()
        saved_after = caching_system.emit()
        listing_after = _folder_listing(bundle_path.parent)
    finally:
        held.release()
        caching_system.cleanup()

    warnings = [
        record.getMessage() for record in caplog.records
        if record.name == _test_logger().name and record.levelno == logging.WARNING
    ]
    print(
        f"\n[held-bundle] long hold: the save returned {refused} after {len(refusals_during_hold)} refused renames "
        f"(Windows codes {_refusal_codes(refusals_during_hold)}) in {refused_seconds:.3f} s; folder during the "
        f"hold: {listing_during_hold}; after it the save returned {saved_after} "
        f"({len(spy.refusals) - len(refusals_during_hold)} more refused, {spy.successes} done). "
        f"WARNING: {warnings}"
    )
    assert saved_before is True
    assert refused is False
    assert len(refusals_during_hold) == CachingSystem.REPLACE_ATTEMPTS
    assert bytes_during_hold == bytes_before
    assert listing_during_hold == [bundle_path.name]
    assert len(warnings) == 1
    assert str(bundle_path) in warnings[0]
    assert saved_after is True
    assert listing_after == [bundle_path.name]
    reloaded = _make_cache_utility(tmp_path)
    try:
        assert reloaded.get_spell_payload("a" * 64) == {"plan": "saved before the hold"}
        assert reloaded.get_spell_payload("b" * 64) == {"plan": "kept through the hold"}
    finally:
        reloaded.cleanup()


def test_meld_returns_its_object_while_windows_refuses_its_cache_save(
        cache_frame: Callable[[str], Path],
        monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    A meld whose cache save Windows refuses returns its object; the plan it staged is saved after the hold.

    Contract:
        A dynamic root is conjured over `HeldBundleSettings`, and its conjure-time save writes the bundle.
        `HeldBundleReport` is bound after conjure, so its first meld compiles it, stages its plan and saves the
        bundle. With the bundle held open, that meld returns its object although Windows refuses the save's rename
        on all `REPLACE_ATTEMPTS` attempts; the bundle is unchanged and no temp file is left; a second meld returns
        the same `unique` object and saves nothing (the spy records no further rename). After the hold
        `AfterHoldReport` is bound and melded: its first meld saves the bundle, which then holds both late spells'
        plans. On 0.2.8265 the first meld raised the save's PermissionError after building its object, and every
        later meld of the Book retried the save and raised while the hold lasted - the owner's MelderOps failure.

    Args:
        cache_frame: Enables caching for the test's frame and empties its cache folder.
        monkeypatch: Restores `os.replace` after the test.
    """
    frame_name = "windows_held_bundle_meld"
    folder = cache_frame(frame_name)
    book = Spellbook(aetheric_frame=frame_name)
    book.get_configuration().set_property("phase_scheduler_workers_per_spellbook", 1)
    book.bind(spell=HeldBundleSettings, existence=Existence.unique, permissions="create")
    root = book.conjure(dynamic=True, name="root")
    bundle_path = folder / f"root{CachingSystem.BUNDLE_SUFFIX}"
    assert bundle_path.exists(), f"Conjure did not save '{bundle_path}', so there is no bundle to hold."
    report_spell_id = root.bind(spell=HeldBundleReport, existence=Existence.unique, permissions="create")
    bytes_before = bundle_path.read_bytes()
    held = _HeldFile(bundle_path)
    held.hold()
    try:
        spy = _RenameSpy(monkeypatch, bundle_path)
        started = time.perf_counter()
        first = root.meld(spell=HeldBundleReport)
        first_meld_seconds = time.perf_counter() - started
        second = root.meld(spell=HeldBundleReport)
        refusals_during_hold = list(spy.refusals)
        successes_during_hold = spy.successes
        bytes_during_hold = bundle_path.read_bytes()
        listing_during_hold = _folder_listing(folder)
    finally:
        held.release()
    later_spell_id = root.bind(spell=AfterHoldReport, existence=Existence.unique, permissions="create")
    later = root.meld(spell=AfterHoldReport)
    listing_after = _folder_listing(folder)
    reloaded = CachingSystem(
        frame_name=frame_name,
        conduit_name="root",
        cache_root_path=folder.parent,
        logger=_test_logger(),
    )
    try:
        cached_spell_ids = set(reloaded.cached_spell_ids)
    finally:
        reloaded.cleanup()

    print(
        f"\n[held-bundle] meld: the first meld of a late spell returned {type(first).__name__} in "
        f"{first_meld_seconds:.3f} s while its save was refused {len(refusals_during_hold)} times (Windows codes "
        f"{_refusal_codes(refusals_during_hold)}); the second meld returned the same object: {second is first}. "
        f"After the hold the next late spell's meld saved the bundle ({spy.successes} done, "
        f"{len(spy.refusals) - len(refusals_during_hold)} more refused); the bundle holds {len(cached_spell_ids)} "
        f"plans; folder: {listing_after}."
    )
    assert isinstance(first, HeldBundleReport)
    assert second is first
    assert len(refusals_during_hold) == CachingSystem.REPLACE_ATTEMPTS
    assert successes_during_hold == 0
    assert bytes_during_hold == bytes_before
    assert listing_during_hold == [bundle_path.name]
    assert isinstance(later, AfterHoldReport)
    assert spy.successes == 1
    assert {report_spell_id, later_spell_id} <= cached_spell_ids
    assert listing_after == [bundle_path.name]
