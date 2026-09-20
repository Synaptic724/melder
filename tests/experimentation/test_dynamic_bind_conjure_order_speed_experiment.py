"""Opt-in timing of five binds, dynamic conjure, and five first melds.

Run this file alone with MELDER_BIND_ORDER_SPEEDTEST=1. Each sample owns a fresh
frame/book/root. Setup, correctness assertions, warmed reads and cleanup are
outside the requested workflow total. Production runtime code is not modified.
"""

import gc
import json
import os
import platform
import re
import statistics
import subprocess
import sys
import sysconfig
import time
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import TYPE_CHECKING, ClassVar, Optional, Sequence, Union, cast

import pytest

import melder
from melder.__version__ import __version__
from melder.aether.aether import Aether
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spellbook import Spellbook

if TYPE_CHECKING:
    from melder.aether.aetheric_frame.aetheric_frame import AethericFrame
    from melder.aether.conduit.conduit import Conduit


class PayloadOne:
    """Independent allocation with a deterministic public value and no resources."""

    __slots__ = ("value",)

    def __init__(self) -> None:
        """Initialize this fresh instance with the value one."""
        self.value: int = 1


class PayloadTwo:
    """Second independent class; no dependencies or external work."""

    __slots__ = ("value",)

    def __init__(self) -> None:
        """Initialize this fresh instance with the value two."""
        self.value: int = 2


class PayloadThree:
    """Third independent class; no dependencies or external work."""

    __slots__ = ("value",)

    def __init__(self) -> None:
        """Initialize this fresh instance with the value three."""
        self.value: int = 3


class PayloadFour:
    """Fourth independent class; no dependencies or external work."""

    __slots__ = ("value",)

    def __init__(self) -> None:
        """Initialize this fresh instance with the value four."""
        self.value: int = 4


class PayloadFive:
    """Fifth independent class; no dependencies or external work."""

    __slots__ = ("value",)

    def __init__(self) -> None:
        """Initialize this fresh instance with the value five."""
        self.value: int = 5


Payload = Union[PayloadOne, PayloadTwo, PayloadThree, PayloadFour, PayloadFive]


@dataclass(frozen=True)
class Sample:
    """Value-only timing record; durations are nanoseconds and retain no objects."""

    sequence: str
    pair: int
    position: int
    setup_ns: int
    bind_ns: int
    conjure_ns: int
    first_meld_ns: int
    total_ns: int
    per_bind_ns: list[int]
    per_first_meld_ns: list[int]
    warm_five_meld_ns: float
    cleanup_ns: int


class OrderBenchmark:
    """Measure real public APIs while owning each sample's runtime lifecycle.

    Aether is borrowed for the process. Each sample owns its book, frame and
    conduit and cleans them after timing. The same frame name is reused only
    after verifying its previous frame has been detached. No runtime methods
    are patched. Compilation uses the default five workers; caches and passive
    recording/publication are disabled to isolate operation ordering.
    """

    TARGETS: ClassVar[tuple[type, ...]] = (
        PayloadOne, PayloadTwo, PayloadThree, PayloadFour, PayloadFive,
    )
    SEQUENCES: ClassVar[tuple[str, str]] = ("bind_conjure_meld", "conjure_bind_meld")
    FRAME_NAME: ClassVar[str] = "dynamic_bind_conjure_order_speed"

    def __init__(self, warm_sweeps: int) -> None:
        """Borrow the fresh process host and retain the untimed reuse-sweep count."""
        self._aether: Aether = Aether()
        self._warm_sweeps: int = warm_sweeps
        if self._aether._aetheric_frames:
            raise RuntimeError("Run this experiment alone in a fresh pytest process.")

    def cleanup(self) -> None:
        """Release benchmark references; sample cleanup already released all frames."""
        if self._aether._aetheric_frames:
            raise AssertionError("Benchmark left a frame in the process host.")
        del self._aether
        del self._warm_sweeps

    @staticmethod
    def distribution(values: Sequence[float]) -> dict[str, float]:
        """Summarize at least two nanosecond observations as microseconds."""
        scaled = [value / 1000.0 for value in values]
        deciles = statistics.quantiles(scaled, n=10, method="inclusive")
        return {
            "median_us": statistics.median(scaled),
            "p10_us": deciles[0],
            "p90_us": deciles[8],
            "minimum_us": min(scaled),
            "mean_us": statistics.mean(scaled),
        }

    def _make_book(self) -> Spellbook:
        """Create fresh, identically configured runtime state outside the timer."""
        book = Spellbook(aetheric_frame=self.FRAME_NAME)
        assert book.get_configuration().get_property("phase_scheduler_workers_per_spellbook") == 5
        book.configure_aether_frame(
            system_state="dynamic",
            disposal=None,
            disposal_method_names=None,
            system_caching_enabled=False,
            ai_native=False,
            rift_enabled=False,
        )
        assert not book._crystallizer.activated
        assert book._aetheric_frame.frame_configuration.system_state.name == "dynamic"
        assert not book._aetheric_frame.frame_configuration.system_caching_enabled
        return book

    def _bind_five(self, book: Spellbook) -> tuple[list[str], list[int], int]:
        """Time five individual binds with identical existence and permissions."""
        spell_ids: list[str] = []
        times: list[int] = []
        batch_start = time.perf_counter_ns()
        for target in self.TARGETS:
            started = time.perf_counter_ns()
            spell_id = book.bind(spell=target, existence=Existence.unique, permissions="create")
            elapsed = time.perf_counter_ns() - started
            spell_ids.append(spell_id)
            times.append(elapsed)
        return spell_ids, times, time.perf_counter_ns() - batch_start

    @staticmethod
    def _meld_five(conduit: Conduit, spell_ids: list[str]) -> tuple[list[object], list[int], int]:
        """Time one meld of each returned id, preserving order and returned objects."""
        objects: list[object] = []
        times: list[int] = []
        batch_start = time.perf_counter_ns()
        for spell_id in spell_ids:
            started = time.perf_counter_ns()
            instance = conduit.meld(spell_id=spell_id)
            elapsed = time.perf_counter_ns() - started
            objects.append(instance)
            times.append(elapsed)
        return objects, times, time.perf_counter_ns() - batch_start

    def _verify_created(self, conduit: Conduit, objects: list[object]) -> None:
        """Check actual construction and dynamic mode after the primary timing."""
        assert conduit.__dynamic_environment__ is True
        assert len(objects) == 5
        for index, (instance, expected_type) in enumerate(zip(objects, self.TARGETS, strict=True)):
            assert type(instance) is expected_type
            assert cast(Payload, instance).value == index + 1

    @staticmethod
    def _release(conduit: Optional[Conduit], book: Spellbook, frame: AethericFrame) -> None:
        """Always attempt owned root, book and frame cleanup, outside timing."""
        try:
            if conduit is not None:
                conduit.permanent_cleanup()
        finally:
            try:
                if not book.cleaned:
                    book.cleanup()
            finally:
                if not frame.cleaned:
                    frame.cleanup()

    def run_case(self, sequence: str, pair: int, position: int) -> Sample:
        """Measure a fresh workflow; no correctness checks run inside its timer."""
        setup_start = time.perf_counter_ns()
        book = self._make_book()
        # This borrowed handle must survive book/root teardown for frame cleanup.
        frame = book._aetheric_frame
        setup_ns = time.perf_counter_ns() - setup_start
        conduit: Optional[Conduit] = None
        try:
            started = time.perf_counter_ns()
            if sequence == "bind_conjure_meld":
                spell_ids, per_bind_ns, bind_ns = self._bind_five(book)
                conjure_start = time.perf_counter_ns()
                conduit = book.conjure(dynamic=True, name="root")
                conjure_ns = time.perf_counter_ns() - conjure_start
            elif sequence == "conjure_bind_meld":
                conjure_start = time.perf_counter_ns()
                conduit = book.conjure(dynamic=True, name="root")
                conjure_ns = time.perf_counter_ns() - conjure_start
                spell_ids, per_bind_ns, bind_ns = self._bind_five(book)
            else:
                raise ValueError(f"Unknown benchmark sequence: {sequence}")
            objects, per_first_meld_ns, first_meld_ns = self._meld_five(conduit, spell_ids)
            total_ns = time.perf_counter_ns() - started
            self._verify_created(conduit, objects)
            warm_times: list[int] = []
            for _ in range(self._warm_sweeps):
                reused, _, elapsed = self._meld_five(conduit, spell_ids)
                assert all(a is b for a, b in zip(objects, reused, strict=True))
                warm_times.append(elapsed)
        finally:
            cleanup_start = time.perf_counter_ns()
            self._release(conduit, book, frame)
            cleanup_ns = time.perf_counter_ns() - cleanup_start
        assert self.FRAME_NAME not in self._aether._aetheric_frames
        return Sample(
            sequence, pair, position, setup_ns, bind_ns, conjure_ns, first_meld_ns,
            total_ns, per_bind_ns, per_first_meld_ns, statistics.mean(warm_times), cleanup_ns,
        )

    def measure(self, warmups: int, samples: int) -> list[Sample]:
        """Warm both cases, then collect balanced paired samples with GC enabled."""
        rows: list[Sample] = []
        for pair in range(warmups + samples):
            gc.collect()
            sequence_order = self.SEQUENCES if pair % 2 == 0 else tuple(reversed(self.SEQUENCES))
            for position, sequence in enumerate(sequence_order):
                row = self.run_case(sequence, pair - warmups, position)
                if pair >= warmups:
                    rows.append(row)
        return rows

    def summarize(self, rows: list[Sample]) -> dict[str, object]:
        """Build phase and per-object distributions without discarding slow samples."""
        summary: dict[str, object] = {}
        for sequence in self.SEQUENCES:
            chosen = [row for row in rows if row.sequence == sequence]
            phases = {
                "setup": [float(row.setup_ns) for row in chosen],
                "bind_five": [float(row.bind_ns) for row in chosen],
                "conjure": [float(row.conjure_ns) for row in chosen],
                "first_meld_five": [float(row.first_meld_ns) for row in chosen],
                "total": [float(row.total_ns) for row in chosen],
                "warm_meld_five": [row.warm_five_meld_ns for row in chosen],
                "cleanup": [float(row.cleanup_ns) for row in chosen],
            }
            summary[sequence] = {
                "samples": len(chosen),
                "phases": {name: self.distribution(values) for name, values in phases.items()},
                "per_first_meld": {
                    target.__name__: self.distribution([float(row.per_first_meld_ns[i]) for row in chosen])
                    for i, target in enumerate(self.TARGETS)
                },
            }
        return summary


@pytest.mark.skipif(
    os.environ.get("MELDER_BIND_ORDER_SPEEDTEST") != "1",
    reason="Opt-in timing experiment: set MELDER_BIND_ORDER_SPEEDTEST=1 and run this file alone.",
)
def test_dynamic_bind_conjure_order_speed() -> None:
    """Validate both real workflows and save repeated phase/per-object timings.

    No performance assertion is made. A timing comparison is meaningful only
    after both sequences construct all five expected instances successfully.
    """
    samples = int(os.environ.get("MELDER_BIND_ORDER_SAMPLES", "200"))
    warmups = int(os.environ.get("MELDER_BIND_ORDER_WARMUPS", "20"))
    warm_sweeps = int(os.environ.get("MELDER_BIND_ORDER_WARM_SWEEPS", "10"))
    run_id = os.environ.get("MELDER_BIND_ORDER_RUN_ID", "manual")
    assert samples >= 2 and warmups >= 0 and warm_sweeps >= 1
    assert re.fullmatch(r"[A-Za-z0-9_-]{1,32}", run_id)
    assert sysconfig.get_config_var("Py_GIL_DISABLED") == 1
    assert not sys._is_gil_enabled()
    assert sys.gettrace() is None and sys.getprofile() is None
    assert gc.isenabled()
    root = Path(__file__).resolve().parents[2]
    assert Path(melder.__file__).resolve().is_relative_to(root / "src")
    runner = OrderBenchmark(warm_sweeps)
    try:
        rows = runner.measure(warmups, samples)
        summary = runner.summarize(rows)
    finally:
        runner.cleanup()
    metadata = {
        "recorded_at_utc": datetime.now(timezone.utc).isoformat(),
        "run_id": run_id,
        "python": sys.version,
        "executable": sys.executable,
        "gil_enabled": sys._is_gil_enabled(),
        "platform": platform.platform(),
        "processor": platform.processor(),
        "melder_version": __version__,
        "melder_source": melder.__file__,
        "git_head": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root, text=True).strip(),
        "src_status": subprocess.check_output(["git", "status", "--porcelain", "--", "src/melder"], cwd=root, text=True),
        "warmup_pairs": warmups,
        "measured_pairs": samples,
        "warm_sweeps_per_sample": warm_sweeps,
        "workers": 5,
        "existence": "unique",
        "bind_api": "five individual Spellbook.bind calls; no outer transaction",
        "meld_api": "Conduit.meld(spell_id=returned_id)",
        "dynamic_posture_before_timing": True,
        "system_caching_enabled": False,
        "crystallizer_recording": False,
        "nexus_publication": False,
        "gc_enabled": gc.isenabled(),
        "total_excludes": ["import", "fresh book/frame setup", "assertions", "warm melds", "cleanup"],
    }
    output_dir = root / "context_compass" / "artifacts" / "bind_conjure_order_20260912"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / f"{run_id}.json"
    output_file.write_text(json.dumps({"metadata": metadata, "summary": summary, "samples": [asdict(row) for row in rows]}, indent=2) + "\n", encoding="utf-8")
    print(f"run={run_id}, samples={samples} per order; median milliseconds")
    for sequence in OrderBenchmark.SEQUENCES:
        selected = [row for row in rows if row.sequence == sequence]
        print(
            f"{sequence}: bind5={statistics.median(row.bind_ns for row in selected) / 1e6:.4f}, "
            f"conjure={statistics.median(row.conjure_ns for row in selected) / 1e6:.4f}, "
            f"first_meld5={statistics.median(row.first_meld_ns for row in selected) / 1e6:.4f}, "
            f"total={statistics.median(row.total_ns for row in selected) / 1e6:.4f}"
        )
    print(f"Raw results: {output_file}")
