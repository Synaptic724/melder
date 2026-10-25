"""
Regression tests: a creation-cache save that fails does not fail the meld that triggered it.

The defect (TASK-2026-10-24-cache_file_write_failure_fails_meld; the owner's Windows run, chat 2026-10-24):
    MelderOps' `Spectrum.configure` melded a spell whose first meld staged its plan into the conduit's
    creation-cache bundle. The save writes `<conduit>.meldercache.tmp` and renames it onto the bundle with
    `os.replace`; Windows refused the rename (PermissionError [WinError 5] - another handle held the bundle) and the
    meld raised it after it had built its object. Every meld door saves the bundle after its object is built, through
    `Spellbook._emit_cache_file_if_required`, which re-raises a failed save and leaves it pending, so on 0.2.8265 (the
    ticket's probe, cases A-D, the GIL off and on):
        - one failed save fails the meld that staged the plan, after the object was built and stored;
        - while saves keep failing (a read-only install, a scanner holding the file) every meld of the Book raises,
          warm melds of spells built earlier included, because each one retries the pending save;
        - a conjure whose save failed (conjure only logs it) leaves its first melds to raise;
        - a managed meld that raises has already taken its lease, so a limited pool loses the place for good;
        - the spellspace doors save, and raise, the same way.
    A bundle is an accelerator - a missing or unreadable one only makes the cache cold - so a meld must not fail
    because one could not be saved.

What these tests assert:
    - Each meld returns its object while saves fail, at the rename (the Windows refusal) or at the temp-file write
      (a read-only folder), once or every time; a second meld of a slotted spell returns the same object.
    - A lease taken through a failed save comes back, and once released the pool leases its object again.
    - Each test proves its fault fired, so none passes on a save that never ran.
    They do not assert where the failure is tolerated, how it is logged or whether the save is retried: that is the
    fix's choice (the ticket's DECISION_REQUEST) and belongs to its own tests.

The fault is injected at the operating-system boundary - `os.replace`, which `Path.replace` calls, and
`Path.write_bytes` - for `.meldercache` files in the test's own cache folder only, so it behaves alike on every
platform CI runs. The save's clean-up (no temp file left behind) is pinned in
`tests/unit/melder/utilities/test_caching_system_refused_save.py`.
"""

import errno
import os
import shutil
from collections.abc import Callable, Iterator
from pathlib import Path
from typing import Any, List, Optional

import pytest

from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.existence.managed_spell_mode import ManagedSpellMode
from melder.aether.spellbook.spellbook import Spellbook
from melder.nexus.nexus import Nexus


class Settings:
    """`unique`, bound before conjure: the spell a root already serves when a later one arrives."""


class ReportWriter:
    """`unique`, bound after conjure, so its first meld compiles it and stages its plan into the bundle."""


class LateReport:
    """`unique`, bound after conjure and first melded while every save fails."""


class AutomaticService:
    """`unique`, bound before an automatic conjure whose save fails."""


class PooledConnection:
    """`managed_spell_quantity`, limited_quantity with a limit of one, bound after conjure."""


class SpaceSession:
    """`unique_per_spell_space`, bound after conjure and first melded in a spellspace."""


class _FailingCacheSaves:
    """
    Fails the creation-cache saves in one frame's cache folder, as an operating system refuses a write.

    Contract:
        - Wraps `os.replace` (which `Path.replace` calls) and `Path.write_bytes` through `monkeypatch`, which
          restores both after the test. It starts disarmed.
        - `fail(step, times)` arms it. Step `REPLACE` refuses the rename of the temp file onto the bundle with
          PermissionError (errno EACCES; Windows reports [WinError 5] while another handle holds the bundle); step
          `WRITE` refuses the write of the temp file with PermissionError (errno EACCES; a read-only folder).
          `times` is how many calls fail; None fails every one for the rest of the test.
        - Only a call on a `.meldercache` file inside `folder` can fail; every other call passes through unchanged.
        - `failures` counts the failures raised, so a test can prove its fault fired.

    Threading:
        Not thread-safe; these tests meld on one thread.
    """

    REPLACE: str = "replace"
    WRITE: str = "write"

    def __init__(self, monkeypatch: pytest.MonkeyPatch, folder: Path) -> None:
        """
        Install the two wrappers, disarmed.

        Args:
            monkeypatch: The test's monkeypatch fixture; it restores both wrapped calls at teardown.
            folder: Resolved cache folder of the test's frame; only `.meldercache` files under it can fail.
        """
        self.failures: int = 0
        self._folder: Path = folder
        self._step: Optional[str] = None
        self._remaining: Optional[int] = 0
        real_replace: Callable[..., None] = os.replace
        real_write_bytes: Callable[[Path, Any], int] = Path.write_bytes

        def replace(source: Any, target: Any, *args: Any, **kwargs: Any) -> None:
            """Refuse a rename onto a bundle in the folder while armed for REPLACE; pass any other through."""
            if self._consume(self.REPLACE, target):
                raise PermissionError(
                    errno.EACCES,
                    "Access is denied (injected; Windows reports [WinError 5])",
                    os.fspath(source),
                    None,
                    os.fspath(target),
                )
            real_replace(source, target, *args, **kwargs)

        def write_bytes(path: Path, data: Any) -> int:
            """Refuse a temp-file write in the folder while armed for WRITE; pass any other through."""
            if self._consume(self.WRITE, path):
                raise PermissionError(
                    errno.EACCES,
                    "Permission denied (injected; a read-only cache folder)",
                    os.fspath(path),
                )
            return real_write_bytes(path, data)

        monkeypatch.setattr(os, "replace", replace)
        monkeypatch.setattr(Path, "write_bytes", write_bytes)

    def fail(self, step: str, times: Optional[int]) -> None:
        """
        Arm the wrappers.

        Args:
            step: `REPLACE` or `WRITE` - which call of the save fails.
            times: How many such calls fail; None fails every one for the rest of the test.
        """
        self._step = step
        self._remaining = times

    def _consume(self, step: str, target: Any) -> bool:
        """
        Decide whether one wrapped call fails, and count it when it does.

        Args:
            step: The wrapped call's step.
            target: The file the call writes: the rename's destination, or the written path.

        Returns:
            bool: True when the call must fail.
        """
        if step != self._step or self._remaining == 0:
            return False
        path = Path(os.fspath(target)).resolve()
        if ".meldercache" not in path.name or not path.is_relative_to(self._folder):
            return False
        if self._remaining is not None:
            self._remaining -= 1
        self.failures += 1
        return True


_SAVE_FAILURES = [
    pytest.param(_FailingCacheSaves.REPLACE, id="rename_refused"),
    pytest.param(_FailingCacheSaves.WRITE, id="temp_write_refused"),
]


def _reset_world() -> None:
    """Install a fresh Aether (and Nexus) and hand it to Spellbook and Conduit."""
    Nexus._reset_singleton_for_tests()
    Aether._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether


@pytest.fixture(autouse=True)
def fresh_world() -> Iterator[None]:
    """
    Give each test a fresh Aether and reset it again afterwards.

    Yields:
        None.
    """
    _reset_world()
    yield
    _reset_world()


@pytest.fixture
def cache_frame(monkeypatch: pytest.MonkeyPatch) -> Iterator[Callable[[str], _FailingCacheSaves]]:
    """
    Turn caching on for frames of the test's own, empty their cache folders and watch their saves.

    Contract:
        Each call takes a frame name unique to its test, ensures the frame, enables caching on its configuration
        (the default cache root, under the melder package), removes whatever an earlier run left in that frame's
        cache folder and returns a disarmed `_FailingCacheSaves` over it. At teardown each such folder is removed,
        best-effort: on Windows a scanner may still hold a just-written bundle, and the next run's preparation
        removes what is left.

    Args:
        monkeypatch: Restores the wrapped calls after the test.

    Yields:
        Callable[[str], _FailingCacheSaves]: The preparation call.
    """
    folders: List[Path] = []

    def prepare(frame_name: str) -> _FailingCacheSaves:
        """
        Prepare one frame's cache folder and its fault.

        Args:
            frame_name: Frame name unique to the calling test.

        Returns:
            _FailingCacheSaves: The disarmed fault over the frame's cache folder.
        """
        configuration = Aether()._ensure_frame(frame_name).frame_configuration
        assert configuration is not None
        configuration.with_system_caching_enabled(True)
        folder = (configuration.resolve_conjure_cache_root_path() / frame_name).resolve()
        if folder.exists():
            shutil.rmtree(folder)
        folders.append(folder)
        return _FailingCacheSaves(monkeypatch, folder)

    yield prepare
    for folder in folders:
        shutil.rmtree(folder, ignore_errors=True)


def _book(frame_name: str) -> Spellbook:
    """
    Build a Spellbook in the given frame with one phase-scheduler worker.

    Args:
        frame_name: The test's frame.

    Returns:
        Spellbook: An empty Book.
    """
    book = Spellbook(aetheric_frame=frame_name)
    book.get_configuration().set_property("phase_scheduler_workers_per_spellbook", 1)
    return book


def _dynamic_root(frame_name: str) -> Conduit:
    """
    Conjure a dynamic root over a Book holding `Settings`, so a spell bound later compiles at its first meld.

    Args:
        frame_name: The test's frame.

    Returns:
        Conduit: The root, its conjure-time save already done.
    """
    book = _book(frame_name)
    book.bind(spell=Settings, existence=Existence.unique, permissions="create")
    return book.conjure(dynamic=True, name="root")


@pytest.mark.parametrize("step", _SAVE_FAILURES)
def test_meld_returns_its_object_when_the_cache_save_fails(
        cache_frame: Callable[[str], _FailingCacheSaves],
        step: str,
) -> None:
    """
    The first meld of a spell bound after conjure returns its object although its cache save fails once.

    Contract:
        `ReportWriter`'s first meld compiles it, stages its plan and saves the bundle, and that save fails once.
        The meld returns the object it built, and a second meld returns the same `unique` object. On 0.2.8265 the
        first meld raised the save's PermissionError after building and storing the object (probe case A).

    Args:
        cache_frame: Prepares the frame's cache folder and its fault.
        step: Which call of the save fails.
    """
    frame_name = f"refused_save_once_{step}"
    saves = cache_frame(frame_name)
    root = _dynamic_root(frame_name)
    root.bind(spell=ReportWriter, existence=Existence.unique, permissions="create")
    saves.fail(step, times=1)

    first = root.meld(spell=ReportWriter)
    second = root.meld(spell=ReportWriter)

    assert isinstance(first, ReportWriter)
    assert second is first
    assert saves.failures == 1


@pytest.mark.parametrize("step", _SAVE_FAILURES)
def test_melds_keep_returning_while_every_cache_save_fails(
        cache_frame: Callable[[str], _FailingCacheSaves],
        step: str,
) -> None:
    """
    While every save fails, a late spell's first meld and warm melds of a spell built before still return.

    Contract:
        `Settings` is built before the saves start failing; then every save fails. The first meld of `LateReport`,
        bound after conjure, returns its object, and three melds of `Settings` return the object built before.
        On 0.2.8265 each of these melds raised: the failed save stays pending and every later meld retries it
        (probe case B, a read-only frame folder).

    Args:
        cache_frame: Prepares the frame's cache folder and its fault.
        step: Which call of the save fails.
    """
    frame_name = f"refused_save_always_{step}"
    saves = cache_frame(frame_name)
    root = _dynamic_root(frame_name)
    settings = root.meld(spell=Settings)
    root.bind(spell=LateReport, existence=Existence.unique, permissions="create")
    saves.fail(step, times=None)

    report = root.meld(spell=LateReport)
    warm = [root.meld(spell=Settings) for _ in range(3)]

    assert isinstance(report, LateReport)
    assert all(melded is settings for melded in warm)
    assert saves.failures >= 1


@pytest.mark.parametrize("step", _SAVE_FAILURES)
def test_first_melds_after_a_failed_conjure_save_return_their_object(
        cache_frame: Callable[[str], _FailingCacheSaves],
        step: str,
) -> None:
    """
    An automatic conjure whose save fails returns its root, and the first melds after it return their object.

    Contract:
        Every save fails from before conjure. Conjure logs its failed save and returns the root, as it already
        did; the first two melds of `AutomaticService` return one `unique` object. On 0.2.8265 conjure left the
        save pending and both melds raised it (probe case C, a read-only cache root).

    Args:
        cache_frame: Prepares the frame's cache folder and its fault.
        step: Which call of the save fails.
    """
    frame_name = f"refused_conjure_save_{step}"
    saves = cache_frame(frame_name)
    book = _book(frame_name)
    book.bind(spell=AutomaticService, existence=Existence.unique, permissions="create")
    saves.fail(step, times=None)
    root = book.conjure(name="root")

    first = root.meld(spell=AutomaticService)
    second = root.meld(spell=AutomaticService)

    assert isinstance(first, AutomaticService)
    assert second is first
    assert saves.failures >= 1


def test_managed_lease_survives_a_failed_cache_save(
        cache_frame: Callable[[str], _FailingCacheSaves],
) -> None:
    """
    A managed meld whose cache save fails returns its lease, and the released object is leased again.

    Contract:
        `PooledConnection` is limited_quantity with a limit of one and is bound after conjure, so its first
        leasing meld compiles it and saves the bundle; that save's rename is refused once. The lease comes back
        holding the pooled object, and once it is released the next managed meld leases that object again. On
        0.2.8265 the first managed meld raised after taking the pool's only place, and every later one raised
        ManagedSpellExhaustedError until the root was torn down (probe case D).

    Args:
        cache_frame: Prepares the frame's cache folder and its fault.
    """
    frame_name = "refused_save_managed"
    saves = cache_frame(frame_name)
    root = _dynamic_root(frame_name)
    root.bind(
        spell=PooledConnection,
        existence=Existence.managed_spell_quantity,
        permissions="create",
        managed_spell_mode=ManagedSpellMode.limited_quantity,
        managed_spell_limit=1,
    )
    saves.fail(_FailingCacheSaves.REPLACE, times=1)

    lease = root.managed_spell_meld(spell=PooledConnection)
    leased = lease.object
    lease.release()
    again = root.managed_spell_meld(spell=PooledConnection)
    leased_again = again.object
    again.release()

    assert isinstance(leased, PooledConnection)
    assert leased_again is leased
    assert saves.failures == 1


def test_spellspace_meld_returns_its_object_when_the_cache_save_fails(
        cache_frame: Callable[[str], _FailingCacheSaves],
) -> None:
    """
    A spellspace meld returns its object although the cache save it triggers fails once.

    Contract:
        `SpaceSession` is `unique_per_spell_space` and bound after conjure; its first meld, in a spellspace,
        compiles it and saves the bundle, and that save's rename is refused once. The meld returns the object and a
        second meld in the same spellspace returns that object. On 0.2.8265 the spellspace doors raised the save's
        error as the conduit doors do.

    Args:
        cache_frame: Prepares the frame's cache folder and its fault.
    """
    frame_name = "refused_save_spellspace"
    saves = cache_frame(frame_name)
    root = _dynamic_root(frame_name)
    root.bind(spell=SpaceSession, existence=Existence.unique_per_spell_space, permissions="create")
    saves.fail(_FailingCacheSaves.REPLACE, times=1)

    with root.enter_spellspace() as space:
        first = space.meld(spell=SpaceSession)
        second = space.meld(spell=SpaceSession)

    assert isinstance(first, SpaceSession)
    assert second is first
    assert saves.failures == 1
