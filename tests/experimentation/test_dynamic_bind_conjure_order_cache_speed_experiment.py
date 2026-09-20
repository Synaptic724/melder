"""Opt-in cold/warm disk-cache extension of the five-object order speed test.

Run alone with MELDER_BIND_ORDER_CACHE_SPEEDTEST=1. Timed samples use real,
unpatched runtime APIs. A separate call-through spy pass records cache
loads, writes and target compilation; its timings are discarded.
"""

import gc
import json
import os
import platform
import re
import shutil
import statistics
import subprocess
import sys
import sysconfig
from dataclasses import asdict
from contextlib import ExitStack
from datetime import datetime, timezone
from pathlib import Path
from typing import ClassVar, Optional
from uuid import uuid4
from unittest.mock import patch

import pytest

import melder
from melder.__version__ import __version__
from melder.aether.spellbook.spellbook import Spellbook
from melder.aether.spellbook.spellbook_creation_system import SpellbookCreationSystem
from melder.utilities.caching_system.caching_system import CachingSystem
from test_dynamic_bind_conjure_order_speed_experiment import OrderBenchmark, Sample


class CacheOrderBenchmark(OrderBenchmark):
    """Run the original workload against two isolated, task-owned cache files.

    Each order receives its own cache folder, with identical frame and conduit
    names. Cold means no bundle before each cycle; warm means a previous cycle
    for that same order produced all five payloads. Books and frames remain
    fresh in every case. The caller owns the temporary filesystem directory.
    """

    CACHE_MODES: ClassVar[tuple[str, ...]] = ("disabled", "cold", "warm")

    def __init__(self, warm_sweeps: int, cache_mode: str, cache_root: Path) -> None:
        """Borrow the process host and validate the requested cache treatment."""
        super().__init__(warm_sweeps)
        if cache_mode not in self.CACHE_MODES:
            raise ValueError(f"Unknown cache mode: {cache_mode}")
        self._cache_mode = cache_mode
        self._cache_root = cache_root.resolve()
        self._case_sequence = self.SEQUENCES[0]
        self._seeded = False

    def cleanup(self) -> None:
        """Release configuration after base cleanup verifies frame detachment."""
        super().cleanup()
        del self._cache_mode
        del self._cache_root
        del self._case_sequence
        del self._seeded

    def _bundle_path(self, sequence: str) -> Path:
        """Resolve the one cache file owned by an order; reject path escape."""
        if sequence not in self.SEQUENCES:
            raise ValueError(f"Unknown benchmark sequence: {sequence}")
        path = (
            self._cache_root / sequence / "__conjure_cache__" / self.FRAME_NAME / "root.melc"
        ).resolve()
        assert path.is_relative_to(self._cache_root)
        return path

    def _make_book(self) -> Spellbook:
        """Match the original configuration except for isolated cache posture.

        The configuration accepts a package-relative fragment. Compute that
        fragment from the task-owned absolute directory, and verify the public
        resolver returns the intended path before any cache I/O occurs.
        """
        book = Spellbook(aetheric_frame=self.FRAME_NAME)
        expected_root = self._cache_root / self._case_sequence
        fragment = Path(os.path.relpath(expected_root, Path(melder.__file__).resolve().parent))
        book.configure_aether_frame(
            system_state="dynamic",
            disposal=None,
            disposal_method_names=None,
            system_caching_enabled=self._cache_mode != "disabled",
            system_cache_root_path=fragment,
            ai_native=False,
            rift_enabled=False,
        )
        assert book.get_configuration().get_property("phase_scheduler_workers_per_spellbook") == 5
        posture = book._aetheric_frame.frame_configuration
        assert posture.system_state.name == "dynamic"
        assert posture.system_caching_enabled == (self._cache_mode != "disabled")
        assert posture.resolve_system_cache_root_path() == expected_root
        assert not book._crystallizer.activated
        return book

    def run_case(self, sequence: str, pair: int, position: int) -> Sample:
        """Prepare cache outside timing, then run the unchanged base workflow.

        Only this experiment's individual bundle may be unlinked. No user cache
        is read or removed. Warm file identity is checked after the cycle to
        detect accidental writes; cold cycles must create their bundle.
        """
        self._case_sequence = sequence
        bundle = self._bundle_path(sequence)
        if self._cache_mode == "cold":
            bundle.unlink(missing_ok=True)
        previous_stat: Optional[tuple[int, int]] = None
        if self._cache_mode == "warm" and self._seeded:
            previous_stat = (bundle.stat().st_size, bundle.stat().st_mtime_ns)
        result = super().run_case(sequence, pair, position)
        if self._cache_mode == "disabled":
            assert not bundle.exists()
        else:
            assert bundle.is_file() and bundle.stat().st_size > 0
        if previous_stat is not None:
            assert (bundle.stat().st_size, bundle.stat().st_mtime_ns) == previous_stat
        return result

    def seed(self) -> None:
        """Populate both warm bundles with this order's own full untimed cycle."""
        if self._cache_mode == "warm":
            for position, sequence in enumerate(self.SEQUENCES):
                assert not self._bundle_path(sequence).exists()
                self.run_case(sequence, -1, position)
        self._seeded = True

    def probe_calls(self) -> dict[str, dict[str, int]]:
        """Count cache/control-path calls in separate untimed cycles.

        Autospecced spies call through to the real implementations. Their call
        counts verify the route; their overhead is never part of timing data.
        """
        targets = {
            "payload_reads": (CachingSystem, "get_spell_payload"),
            "payload_upserts": (CachingSystem, "upsert_spell_payload"),
            "bundle_writes": (CachingSystem, "_write_current_cache_to_disk_locked"),
            "conjure_cache_loads": (
                SpellbookCreationSystem, "_load_cached_spell_payloads_for_conjure"
            ),
            "cached_context_publications": (
                SpellbookCreationSystem, "_publish_cached_creation_context_for_spell"
            ),
            "target_plan_compilations": (
                SpellbookCreationSystem, "_run_target_plan_resolution_phases"
            ),
            "deferred_plan_compilations": (
                SpellbookCreationSystem, "run_deferred_resolution_phases_for_target_spell"
            ),
        }
        reports: dict[str, dict[str, int]] = {}
        for position, sequence in enumerate(self.SEQUENCES):
            with ExitStack() as stack:
                # Attribute names are deliberately dynamic in this diagnostic map.
                spies = {
                    name: stack.enter_context(patch.object(
                        owner, method, autospec=True, side_effect=getattr(owner, method)
                    ))
                    for name, (owner, method) in targets.items()
                }
                self.run_case(sequence, -2, position)
                counts = {name: spy.call_count for name, spy in spies.items()}
            expected_loads = 5 if self._cache_mode == "warm" and position == 0 else 0
            assert counts["payload_reads"] == expected_loads
            assert counts["cached_context_publications"] == expected_loads
            assert counts["target_plan_compilations"] == (5 if position == 1 else 0)
            assert counts["deferred_plan_compilations"] == 0
            assert counts["bundle_writes"] == (
                (1 if position == 0 else 5) if self._cache_mode == "cold" else 0
            )
            reports[sequence] = counts
        return reports


@pytest.mark.skipif(
    os.environ.get("MELDER_BIND_ORDER_CACHE_SPEEDTEST") != "1",
    reason="Opt-in cache timing: set MELDER_BIND_ORDER_CACHE_SPEEDTEST=1 and run alone.",
)
def test_dynamic_bind_conjure_order_cache_speed() -> None:
    """Measure one cache treatment in a fresh process and preserve raw evidence.

    Correctness and reuse checks are inherited from the original workload.
    Call-through diagnostics run after measured samples and are reported separately.
    No performance thresholds are asserted.
    """
    cache_mode = os.environ.get("MELDER_BIND_ORDER_CACHE_MODE", "warm")
    samples = int(os.environ.get("MELDER_BIND_ORDER_SAMPLES", "200"))
    warmups = int(os.environ.get("MELDER_BIND_ORDER_WARMUPS", "20"))
    run_id = os.environ.get("MELDER_BIND_ORDER_RUN_ID", f"cache_{cache_mode}_manual")
    assert cache_mode in CacheOrderBenchmark.CACHE_MODES
    assert samples >= 2 and warmups >= 0
    assert re.fullmatch(r"[A-Za-z0-9_-]{1,40}", run_id)
    assert sysconfig.get_config_var("Py_GIL_DISABLED") == 1 and not sys._is_gil_enabled()
    assert sys.gettrace() is None and sys.getprofile() is None and gc.isenabled()
    root = Path(__file__).resolve().parents[2]
    assert Path(melder.__file__).resolve().is_relative_to(root / "src")
    output_dir = root / "context_compass" / "artifacts" / "bind_conjure_order_20260912"
    output_dir.mkdir(parents=True, exist_ok=True)
    # Normal mkdir inherits workspace permissions; Windows mode-0700 temp
    # directories can exclude the restricted process token from their own ACL.
    cache_root = (output_dir / f"{run_id}_{uuid4().hex[:8]}").resolve()
    assert cache_root.is_relative_to(output_dir.resolve())
    cache_root.mkdir()
    runner = CacheOrderBenchmark(10, cache_mode, cache_root)
    try:
        runner.seed()
        rows = runner.measure(warmups, samples)
        summary = runner.summarize(rows)
        probes = runner.probe_calls()
    finally:
        try:
            runner.cleanup()
        finally:
            # Recursive deletion is limited to this newly created task directory.
            assert cache_root.is_relative_to(output_dir.resolve())
            assert cache_root.name.startswith(f"{run_id}_")
            shutil.rmtree(cache_root)
    metadata = {
        "recorded_at_utc": datetime.now(timezone.utc).isoformat(),
        "run_id": run_id,
        "cache_mode": cache_mode,
        "python": sys.version,
        "executable": sys.executable,
        "gil_enabled": sys._is_gil_enabled(),
        "platform": platform.platform(),
        "processor": platform.processor(),
        "melder_version": __version__,
        "melder_source": melder.__file__,
        "git_head": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root, text=True).strip(),
        "src_status": subprocess.check_output(
            ["git", "status", "--porcelain", "--", "src/melder"], cwd=root, text=True
        ),
        "warmup_pairs": warmups,
        "measured_pairs": samples,
        "workers": 5,
        "existence": "unique",
        "dynamic": True,
        "cache_isolation": "separate temporary directory per order; removed after run",
        "warm_seed": "one same-order full cycle before warm-ups" if cache_mode == "warm" else None,
        "cold_definition": "no Melder bundle at cycle start; OS/filesystem caches are uncontrolled",
        "timing_instrumentation": "none; call-through spies only in subsequent discarded diagnostic cycles",
        "total_excludes": ["import", "cache setup/removal", "book/frame setup", "assertions", "reuse", "cleanup"],
    }
    output = output_dir / f"{run_id}.json"
    output.write_text(json.dumps({
        "metadata": metadata,
        "summary": summary,
        "call_probes": probes,
        "samples": [asdict(row) for row in rows],
    }, indent=2) + "\n", encoding="utf-8")
    print(f"cache={cache_mode}, run={run_id}, samples={samples} per order; median milliseconds")
    for sequence in OrderBenchmark.SEQUENCES:
        chosen = [row for row in rows if row.sequence == sequence]
        print(
            f"{sequence}: bind5={statistics.median(row.bind_ns for row in chosen) / 1e6:.4f}, "
            f"conjure={statistics.median(row.conjure_ns for row in chosen) / 1e6:.4f}, "
            f"first_meld5={statistics.median(row.first_meld_ns for row in chosen) / 1e6:.4f}, "
            f"total={statistics.median(row.total_ns for row in chosen) / 1e6:.4f}"
        )
        print(f"Untimed call probe: {probes[sequence]}")
    print(f"Raw results: {output}")


@pytest.mark.skipif(
    os.environ.get("MELDER_BIND_ORDER_PROFILE_REPRO") != "1",
    reason="Separate opt-in reproduction of the old interpreter profiling stall.",
)
def test_profile_stall_reproduction() -> None:
    """Run the original profiler trigger with a bounded hard-exit watchdog.

    Invoke this test alone in a disposable subprocess. If it stalls, the
    watchdog writes every thread stack and exits the process after ten seconds.
    This is diagnostic only and produces no performance measurements.
    """
    import cProfile
    import faulthandler

    root = Path(__file__).resolve().parents[2]
    output_dir = root / "context_compass" / "artifacts" / "bind_conjure_order_20260912"
    cache_root = (output_dir / f"profile_repro_{uuid4().hex[:8]}").resolve()
    assert cache_root.is_relative_to(output_dir.resolve())
    cache_root.mkdir()
    runner = CacheOrderBenchmark(10, "warm", cache_root)
    try:
        runner.seed()
        runner.measure(2, 4)
        print(f"PROFILE REPRO START: {sys.version}; gil={sys._is_gil_enabled()}", flush=True)
        faulthandler.dump_traceback_later(10, exit=True)
        try:
            for position, sequence in enumerate(runner.SEQUENCES):
                profiler = cProfile.Profile()
                profiler.enable()
                try:
                    runner.run_case(sequence, -2, position)
                finally:
                    profiler.disable()
            print("PROFILE REPRO COMPLETED", flush=True)
        finally:
            faulthandler.cancel_dump_traceback_later()
    finally:
        runner.cleanup()
        assert cache_root.is_relative_to(output_dir.resolve())
        assert cache_root.name.startswith("profile_repro_")
        shutil.rmtree(cache_root)
