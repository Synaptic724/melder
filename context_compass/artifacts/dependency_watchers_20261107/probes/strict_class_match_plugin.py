"""
Probe plugin: the full test suite under strict class matching.

Owner: TASK-2026-11-07-inventory_class_resolution_of_framed_spells (T1 of
EPIC-2026-11-07-spellframe_hides_the_concrete_class), melder_0.

Purpose:
    Measure which tests rely on a class annotation resolving a spell bound under a
    spellframe, without editing src. In strict mode this plugin applies, at runtime,
    the rule T2 will land - a class annotation, the type part of a single string
    annotation and `list[Class]` select only spells bound with no spellframe - and the
    suite runs once in each mode; the tests whose outcome differs are T2's test list.

Modes (environment variable MELDER_PROBE_STRICT):
    "1": the strict rule patches `CompilerPhase3._spell_keys_for` (the scan path) and
         `CompilerPhase3._build_candidate_index` (the index path).
    anything else: matching is left as shipped.

Both modes:
    The default conjure cache root (under `<melder package>/__melder_cache__`) is
    redirected to a fresh temporary directory per process, so a bundle written by the
    other run, or already in the source tree, never replays Phase 3-4 rows (the
    structural snapshot) into this run. A cache root a test chose itself is untouched.

Usage (from the repository root):
    PYTHONPATH=context_compass/artifacts/dependency_watchers_20261107/probes \
    MELDER_PROBE_STRICT=1 .venv_new/Scripts/python.exe -X gil=0 -m pytest tests \
        -p strict_class_match_plugin

Limits:
    A test that starts its own interpreter does not load the plugin, so its outcome is
    the same in both modes.
"""
import os
import shutil
import sys
import tempfile
from pathlib import Path
from typing import Any, Callable, Dict, List, Tuple

import pytest


class StrictClassMatchProbe:
    """
    Install and remove the probe's runtime patches for one pytest process.

    Contract:
        - `apply()` patches `CachingSystem.__init__` (the cache-root redirect, both modes)
          and, in strict mode, the two Phase 3 matchers. Each original is read from the
          owning class's `__dict__` before it is replaced, so `pytest_unconfigure`
          restores exactly what was there.
        - `pytest_unconfigure` restores the originals in reverse order and removes the
          temporary cache root. A second call does nothing.
        - The strict rule mirrors T2's planned change and nothing else: Protocol
          (contract and definition) matching and the label key of a string collection
          are left as shipped.

    Threading / Concurrency:
        The patches are installed in `pytest_configure`, before any test runs, and
        removed in `pytest_unconfigure`, after the last one, on pytest's main thread;
        the patched functions themselves are stateless.

    Lifecycle / Cleanup:
        Owns the temporary cache directory and the list of originals; both end in
        `pytest_unconfigure`.
    """

    def __init__(self, strict: bool) -> None:
        """
        Prepare a probe for one process.

        Args:
            strict: True to apply the strict class rule as well as the cache redirect.
        """
        self._strict: bool = strict
        self._cache_root: Path = Path(tempfile.mkdtemp(prefix="melder_probe_cache_"))
        self._originals: List[Tuple[Any, str, Any]] = []
        self._removed: bool = False

    def apply(self) -> None:
        """
        Install the cache redirect and, in strict mode, the strict class rule.

        Raises:
            KeyError: A patched name is no longer defined on its class (the probe is stale).
        """
        import melder
        from melder.aether.spellbook.spell_compiler.phases.compiler_phase_3 import CompilerPhase3
        from melder.utilities.caching_system.caching_system import CachingSystem

        default_root = Path(melder.__file__).resolve().parent / "__melder_cache__"
        self._redirect_cache_root(CachingSystem, default_root)
        if self._strict:
            self._patch_scan_path(CompilerPhase3)
            self._patch_index_path(CompilerPhase3)

    def pytest_report_header(self, config: pytest.Config) -> str:
        """
        Name the probe's mode and cache root in the run's header.

        Args:
            config: The pytest configuration (unused).

        Returns:
            str: One header line.
        """
        mode = "strict" if self._strict else "as shipped"
        return f"strict_class_match_plugin: class matching {mode}; conjure cache root {self._cache_root}"

    def pytest_unconfigure(self, config: pytest.Config) -> None:
        """
        Restore every patched attribute and remove the temporary cache root.

        Args:
            config: The pytest configuration (unused).
        """
        if self._removed:
            return
        self._removed = True
        for owner, name, original in reversed(self._originals):
            setattr(owner, name, original)
        self._originals.clear()
        shutil.rmtree(self._cache_root, ignore_errors=True)

    def _install(self, owner: Any, name: str, replacement: Callable[..., Any]) -> None:
        """
        Replace `owner.name`, recording the original from the class `__dict__`.

        Args:
            owner: The class that defines the attribute.
            name: The attribute name.
            replacement: The function to install.

        Raises:
            KeyError: `name` is not defined on `owner` itself.
        """
        self._originals.append((owner, name, owner.__dict__[name]))
        setattr(owner, name, replacement)

    def _redirect_cache_root(self, caching_system_class: Any, default_root: Path) -> None:
        """
        Make every cache utility built on the default root use the probe's temp root.

        Args:
            caching_system_class: `CachingSystem`.
            default_root: `<melder package>/__melder_cache__`, the default root's base.
        """
        original_init = caching_system_class.__dict__["__init__"]
        default_resolved = default_root.resolve()
        probe_root = self._cache_root

        def redirected_init(
                caching_self: Any,
                *,
                frame_name: str,
                conduit_name: str,
                cache_root_path: Path,
                logger: Any = None,
        ) -> None:
            """Build the cache utility under the probe root when the caller passed the default root."""
            target = Path(cache_root_path)
            try:
                relative = target.resolve().relative_to(default_resolved)
            except ValueError:
                relative = None
            if relative is not None:
                target = probe_root / relative
            original_init(
                caching_self,
                frame_name=frame_name,
                conduit_name=conduit_name,
                cache_root_path=target,
                logger=logger,
            )

        self._install(caching_system_class, "__init__", redirected_init)

    def _patch_scan_path(self, phase_class: Any) -> None:
        """
        Apply the strict rule to `_spell_keys_for`, which `_matches_annotation` (the scan) reads.

        A spell bound under a spellframe answers no class annotation (single or `list[...]`)
        and, for a single string annotation, only its contract keys; a bare spell, a Protocol
        annotation and a string collection keep the shipped keys.

        Args:
            phase_class: `CompilerPhase3`.
        """
        original_keys = phase_class.__dict__["_spell_keys_for"]

        def strict_spell_keys_for(
                phase_self: Any,
                annotation_kind: str,
                spell_obj: Any,
                *,
                collection: bool,
        ) -> Tuple[str, ...]:
            """T2's rule on the scan path: a framed spell is not reached by its type key."""
            if spell_obj.spellframe is None:
                return original_keys(phase_self, annotation_kind, spell_obj, collection=collection)
            if annotation_kind == phase_self._KIND_TYPE:
                return ()
            if annotation_kind == phase_self._KIND_NAME and not collection:
                return phase_self._spell_contract_keys(spell_obj)
            return original_keys(phase_self, annotation_kind, spell_obj, collection=collection)

        self._install(phase_class, "_spell_keys_for", strict_spell_keys_for)

    def _patch_index_path(self, phase_class: Any) -> None:
        """
        Apply the strict rule to `_build_candidate_index`: `by_type` keeps only bare spells.

        `_index_buckets_for` reads `by_type` for a class annotation and for a single string
        annotation, so this is the index-path twin of `_patch_scan_path`.

        Args:
            phase_class: `CompilerPhase3`.
        """
        original_build = phase_class.__dict__["_build_candidate_index"]

        def strict_build_candidate_index(phase_self: Any, spellbook: Any) -> Dict[str, Any]:
            """T2's rule on the index path: the type bucket holds only spells with no spellframe."""
            index = original_build(phase_self, spellbook)
            strict_by_type: Dict[str, List[Any]] = {}
            for key, entries in index["by_type"].items():
                kept = [entry for entry in entries if entry[2].spellframe is None]
                if kept:
                    strict_by_type[key] = kept
            index["by_type"] = strict_by_type
            return index

        self._install(phase_class, "_build_candidate_index", strict_build_candidate_index)


def pytest_configure(config: pytest.Config) -> None:
    """
    Install the probe in this process (the xdist controller and every worker).

    Puts the repository's `src` first on `sys.path`, as tests/conftest.py does, so the
    probe patches the melder the tests import.

    Args:
        config: The pytest configuration.
    """
    src_path = str(config.rootpath / "src")
    if src_path not in sys.path:
        sys.path.insert(0, src_path)
    probe = StrictClassMatchProbe(strict=os.environ.get("MELDER_PROBE_STRICT") == "1")
    probe.apply()
    config.pluginmanager.register(probe, "melder_strict_class_match_probe")
