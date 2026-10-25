"""
Pytest plugin: run the Windows-only held-bundle tests on Linux by emulating Windows' rename refusal.

Not part of the repository's suite: it is kept with TASK-2026-10-24-windows_held_cache_bundle_test's artifacts
(melder_0, 2026-10-24) so the logic of
tests/integration/melder/conduit/test_conduit_integration_windows_held_cache_bundle.py can be run off Windows.
Load it with `-p windows_emulation_harness`, with this folder and the tree's `src` on PYTHONPATH, from the tree's
root (a /tmp copy: the meld test writes under the melder package's cache folder):

    PYTHONPATH=<tree>/src:<this folder> python -X gil=0 -m pytest -p windows_emulation_harness \
        -p no:cacheprovider tests/integration/melder/conduit/test_conduit_integration_windows_held_cache_bundle.py \
        -v -s

What it changes, only while it is loaded:
    1. The target test module is imported while `sys.platform` reads "win32", so its
       `skipif(sys.platform != "win32")` reads False. Melder and every module the test imports are imported by this
       plugin first, under the real platform, so no other import-time code sees the substitute; the real value is
       restored as soon as the module's collection ends, so at run time `sys.platform` is "linux" again.
    2. `CachingSystem.RETRY_REFUSED_RENAME` is True, as on Windows.
    3. `os.replace` refuses with PermissionError (errno EACCES) a rename whose destination this process holds open
       - an entry of /proc/self/fd links to it - which is what Windows does for a file opened without
       FILE_SHARE_DELETE; Python's open() never passes it. Every other rename passes through.
Everything is restored at unconfigure, and the terminal summary reports how many renames it refused.

What it cannot show: Windows' error code (the emulated error carries none), a handle held by another process, and
an on-access scanner's timing. Those are what the owner's Windows run is for.
"""

# Every module the target test module imports is imported here first, under the real platform (1. above), so the
# substitute is seen by the test module's own top-level code alone; most of these names are not used here.
import errno
import logging
import os
import shutil
import sys
import threading
import time
from collections.abc import Callable, Generator, Iterator
from pathlib import Path
from typing import IO, Any, List, Optional

import pytest

from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spellbook import Spellbook
from melder.nexus.nexus import Nexus
from melder.utilities.caching_system.caching_system import CachingSystem


class WindowsRenameEmulation:
    """
    Windows' rename refusal and retry switch, installed over the real ones for one pytest session.

    Contract:
        - `install()` replaces `os.replace` with `_replace` and sets `CachingSystem.RETRY_REFUSED_RENAME` to True;
          `uninstall()` puts back the values `__init__` read (on a tree older than 0.2.8266 it removes the
          switch it added). Neither is reentrant; the plugin calls each once.
        - `_replace` refuses a rename onto a file this process holds open and counts it in `refusals`; any other
          rename goes to the real `os.replace` unchanged.

    Threading:
        `refusals` is incremented without a lock; the tests rename on one thread.
    """

    def __init__(self) -> None:
        """Read the real `os.replace` and retry switch so `uninstall()` can restore them."""
        self.refusals: int = 0
        self._real_replace: Callable[..., None] = os.replace
        # None when the tree's CachingSystem predates the switch (0.2.8266): the red run on 0.2.8265 loads this
        # plugin too, and there the switch is set for the run and removed again.
        self._previous_retry: Optional[bool] = CachingSystem.__dict__.get("RETRY_REFUSED_RENAME")

    def install(self) -> None:
        """Put the emulated rename and the Windows retry switch in place."""
        setattr(os, "replace", self._replace)
        CachingSystem.RETRY_REFUSED_RENAME = True

    def uninstall(self) -> None:
        """Restore the real rename and the retry switch's earlier value."""
        setattr(os, "replace", self._real_replace)
        if self._previous_retry is None:
            delattr(CachingSystem, "RETRY_REFUSED_RENAME")
        else:
            CachingSystem.RETRY_REFUSED_RENAME = self._previous_retry

    def _replace(self, source: Any, target: Any, *args: Any, **kwargs: Any) -> None:
        """
        Refuse a rename onto a file this process holds open, as Windows does; pass any other through.

        Args:
            source: The file renamed.
            target: Its destination.
            *args: Passed through to `os.replace`.
            **kwargs: Passed through to `os.replace`.

        Raises:
            PermissionError: The destination is open in this process (errno EACCES).
        """
        destination = os.path.realpath(os.fspath(target))
        if self._held_by_this_process(destination):
            self.refusals += 1
            raise PermissionError(
                errno.EACCES,
                "Access is denied (emulated: the destination is open in this process)",
                os.fspath(source),
                None,
                os.fspath(target),
            )
        self._real_replace(source, target, *args, **kwargs)

    @staticmethod
    def _held_by_this_process(path: str) -> bool:
        """
        Return whether one of this process's open file descriptors refers to `path`.

        Args:
            path: A real (symlink-free) absolute path.

        Returns:
            bool: True when an entry of /proc/self/fd links to `path`.
        """
        for descriptor in os.listdir("/proc/self/fd"):
            try:
                link = os.readlink(f"/proc/self/fd/{descriptor}")
            except OSError:
                # The listing's own descriptor is closed by the time it is read.
                continue
            if link == path:
                return True
        return False


class WindowsEmulationPlugin:
    """
    The registered plugin object: substitutes the platform while the target module is collected.

    Contract:
        - `TARGET_MODULE_NAME` names the one test module whose import sees `sys.platform == "win32"`.
        - Owns the emulation it is given: `pytest_unconfigure` uninstalls it.
    """

    TARGET_MODULE_NAME: str = "test_conduit_integration_windows_held_cache_bundle.py"

    def __init__(self, emulation: WindowsRenameEmulation) -> None:
        """
        Keep the installed emulation.

        Args:
            emulation: The emulation `pytest_configure` installed.
        """
        self._emulation: WindowsRenameEmulation = emulation

    @pytest.hookimpl(wrapper=True)
    def pytest_make_collect_report(self, collector: pytest.Collector) -> Generator[None, Any, Any]:
        """
        Collect the target module while `sys.platform` reads "win32"; collect anything else unchanged.

        Args:
            collector: The node being collected.

        Returns:
            Any: The collect report of the wrapped hooks.
        """
        if not (isinstance(collector, pytest.Module) and collector.path.name == self.TARGET_MODULE_NAME):
            return (yield)
        real_platform = sys.platform
        sys.platform = "win32"
        try:
            return (yield)
        finally:
            sys.platform = real_platform

    def pytest_terminal_summary(self, terminalreporter: Any) -> None:
        """
        Report how many renames the emulation refused.

        Args:
            terminalreporter: pytest's terminal reporter.
        """
        terminalreporter.write_line(
            f"windows emulation: {self._emulation.refusals} renames refused; "
            f"RETRY_REFUSED_RENAME={CachingSystem.RETRY_REFUSED_RENAME}, platform at run time {sys.platform}"
        )

    def pytest_unconfigure(self, config: pytest.Config) -> None:
        """
        Restore the real rename and retry switch.

        Args:
            config: The pytest config.
        """
        self._emulation.uninstall()


def pytest_configure(config: pytest.Config) -> None:
    """
    Install the emulation and register the plugin object that owns it.

    Args:
        config: The pytest config.
    """
    emulation = WindowsRenameEmulation()
    emulation.install()
    config.pluginmanager.register(WindowsEmulationPlugin(emulation), "windows-emulation")
