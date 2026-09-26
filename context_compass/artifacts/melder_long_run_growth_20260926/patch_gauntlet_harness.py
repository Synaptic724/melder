"""Apply the owner-approved gauntlet harness fixes (2026-09-26) to benchmarks/testing_other_di.

Usage: python patch_gauntlet_harness.py <path-to-benchmarks/testing_other_di>

Every replacement asserts its anchor occurs exactly once, so a changed file aborts before any
write to that file. Line endings are preserved (the owner's files are CRLF).
"""
import pathlib
import sys

root = pathlib.Path(sys.argv[1])


def patch(path: pathlib.Path, pairs) -> None:
    text = path.read_bytes().decode("utf-8")
    newline = "\r\n" if "\r\n" in text else "\n"
    for old, new in pairs:
        old = old.replace("\n", newline)
        new = new.replace("\n", newline)
        count = text.count(old)
        if count != 1:
            raise SystemExit(f"{path.name}: anchor found {count} times:\n{old[:300]}")
        text = text.replace(old, new)
    path.write_bytes(text.encode("utf-8"))
    print(f"patched {path.name}")


SAMPLES_DOC = '''    """
    Per-lane scope-cycle timings in nanoseconds, one entry per cycle.

    Two storage kinds share this shape, and the split is deliberate:

    - One iteration's samples are plain lists (`{new_samples}`). The
      short-lived worker threads append to them; list appends stay safe when
      several workers share a lane, and the lists die with the iteration.
    - The run-long accumulation is packed `array("q")` storage
      (`{new_storage}`), extended on the main thread. It holds values, not int
      objects. Keeping the workers' int objects for the whole leg (the former
      list storage) retained objects allocated by threads that had exited, and
      on free-threaded CPython 3.14 that made every later scope cycle
      progressively more expensive: 2-2.5x slower over 40k iterations for
      Melder and dishka alike, with zero garbage collections. The attribution
      test in test_melder_long_run_retention.py reproduces it.

    Values, ordering and every summary computed from them are unchanged.
    """
'''

STORAGE_DOC = '''    """
    Return empty run-long sample storage: six signed 64-bit `array("q")`.

    Contract:
        - Used only for accumulation across iterations on the main thread.
        - `extend(...)` copies values out of an iteration's lists, so no int
          object created on a worker thread outlives that iteration. See
          `{samples_class}` for why this matters on free-threaded CPython.
    """
'''

# ---------------------------------------------------------------- shared gauntlet
real = root / "test_real_world_gauntlet.py"
patch(real, [
    (
        "import typing\nfrom collections.abc import Callable\n",
        "import typing\nfrom array import array\nfrom collections.abc import Callable, MutableSequence, Sequence\n",
    ),
    (
        "class _LaneMetricSamples:\n"
        "    outer_create_ns: list[int]\n"
        "    outer_cleanup_ns: list[int]\n"
        "    outer_total_ns: list[int]\n"
        "    request_create_ns: list[int]\n"
        "    request_cleanup_ns: list[int]\n"
        "    request_total_ns: list[int]\n",
        "class _LaneMetricSamples:\n"
        + SAMPLES_DOC.format(new_samples="_new_lane_metric_samples", new_storage="_new_lane_metric_storage")
        + "\n"
        "    outer_create_ns: MutableSequence[int]\n"
        "    outer_cleanup_ns: MutableSequence[int]\n"
        "    outer_total_ns: MutableSequence[int]\n"
        "    request_create_ns: MutableSequence[int]\n"
        "    request_cleanup_ns: MutableSequence[int]\n"
        "    request_total_ns: MutableSequence[int]\n",
    ),
    (
        "        request_total_ns=[],\n"
        "    )\n"
        "\n"
        "\n"
        "def _variant_counts_tuple(",
        "        request_total_ns=[],\n"
        "    )\n"
        "\n"
        "\n"
        "def _new_lane_metric_storage() -> _LaneMetricSamples:\n"
        + STORAGE_DOC.format(samples_class="_LaneMetricSamples")
        + "    return _LaneMetricSamples(\n"
        '        outer_create_ns=array("q"),\n'
        '        outer_cleanup_ns=array("q"),\n'
        '        outer_total_ns=array("q"),\n'
        '        request_create_ns=array("q"),\n'
        '        request_cleanup_ns=array("q"),\n'
        '        request_total_ns=array("q"),\n'
        "    )\n"
        "\n"
        "\n"
        "def _variant_counts_tuple(",
    ),
    (
        "        lane_metric_samples = {\n"
        '            "request": _new_lane_metric_samples(),\n'
        '            "worker_a": _new_lane_metric_samples(),\n'
        '            "worker_b": _new_lane_metric_samples(),\n'
        "        }\n",
        "        lane_metric_samples = {\n"
        '            "request": _new_lane_metric_storage(),\n'
        '            "worker_a": _new_lane_metric_storage(),\n'
        '            "worker_b": _new_lane_metric_storage(),\n'
        "        }\n",
    ),
    (
        "def _summarize(samples: list[int]) -> _Summary:\n",
        "def _summarize(samples: Sequence[int]) -> _Summary:\n",
    ),
    (
        "        combined_outer_create = []\n"
        "        combined_outer_cleanup = []\n"
        "        combined_outer_total = []\n"
        "        combined_request_create = []\n"
        "        combined_request_cleanup = []\n"
        "        combined_request_total = []\n",
        "        # Packed like the run-long lane storage, so combining multi-million-entry\n"
        "        # lanes does not materialize an int object per sample before summarizing.\n"
        '        combined_outer_create: array[int] = array("q")\n'
        '        combined_outer_cleanup: array[int] = array("q")\n'
        '        combined_outer_total: array[int] = array("q")\n'
        '        combined_request_create: array[int] = array("q")\n'
        '        combined_request_cleanup: array[int] = array("q")\n'
        '        combined_request_total: array[int] = array("q")\n',
    ),
    (
        "def _build_runtime_melder() -> _RuntimeOps:\n"
        "    from melder.aether.aether import Aether\n",
        "def _build_runtime_melder() -> _RuntimeOps:\n"
        '    """\n'
        "    Build the shared gauntlet's Melder lane over this module's class graph.\n"
        "\n"
        "    Contract:\n"
        "        - Uses the same classes as the dependency-injector and dishka lanes in\n"
        "          this module, so all three libraries resolve the identical graph.\n"
        "        - Setup MUST stay identical to the Melder-only gauntlet\n"
        "          (`test_melder_gauntlet._build_runtime_melder`): same frame and conduit\n"
        "          names, one phase-scheduler worker, no frame-posture overrides, the\n"
        '          same existence per class, `permissions="create"`, `dynamic=False`.\n'
        "          The two builders are separate code on purpose - tuning the\n"
        "          Melder-only benchmark cannot change this shared comparison - and\n"
        "          `test_gauntlet_melder_lane_parity.py` fails if their setup diverges.\n"
        "        - Resets the Aether singleton before building and again in cleanup.\n"
        "\n"
        "    Returns:\n"
        "        _RuntimeOps: The Melder lane callables for `_run_gauntlet_once`.\n"
        '    """\n'
        "    from melder.aether.aether import Aether\n",
    ),
    (
        '    spellbook = Spellbook(aetheric_frame="real-world-gauntlet")\n'
        "    cfg = spellbook.get_configuration()\n"
        "    spellbook.configure_aether_frame(\n"
        "        system_state=None,\n"
        "        disposal=None,\n"
        "        disposal_method_names=None,\n"
        "        system_caching_enabled=True,\n"
        "    )\n"
        '    cfg.set_property("phase_scheduler_workers_per_spellbook", 3)\n',
        '    spellbook = Spellbook(aetheric_frame="real-world-gauntlet")\n'
        "    cfg = spellbook.get_configuration()\n"
        "    # Matches the Melder-only gauntlet exactly: one phase-scheduler worker and no\n"
        "    # frame-posture overrides (system caching is already on by frame default).\n"
        "    # This builder previously called configure_aether_frame(...) first, which\n"
        "    # freezes the configuration, so the set_property below raised and the shared\n"
        "    # gauntlet had been borrowing the Melder-only builder instead.\n"
        '    cfg.set_property("phase_scheduler_workers_per_spellbook", 1)\n',
    ),
    (
        '    if lib == "melder":\n'
        "        from benchmarks.testing_other_di import test_melder_gauntlet as melder_gauntlet\n"
        "\n"
        "        return melder_gauntlet._build_runtime_melder()\n",
        '    if lib == "melder":\n'
        "        # This module's own Melder lane: isolated from the Melder-only gauntlet,\n"
        "        # kept equal to it by test_gauntlet_melder_lane_parity.py.\n"
        "        return _build_runtime_melder()\n",
    ),
])

# ---------------------------------------------------------------- Melder-only harness
support = root / "melder_gauntlet_support.py"
patch(support, [
    (
        "import time\nfrom dataclasses import dataclass\n"
        "from typing import Any, Callable, Dict, Iterable, List, Tuple, Union\n",
        "import time\nfrom array import array\nfrom dataclasses import dataclass\n"
        "from typing import Any, Callable, Dict, Iterable, List, MutableSequence, Sequence, Tuple, Union\n",
    ),
    (
        "class LaneMetricSamples:\n"
        "    outer_create_ns: List[int]\n"
        "    outer_cleanup_ns: List[int]\n"
        "    outer_total_ns: List[int]\n"
        "    request_create_ns: List[int]\n"
        "    request_cleanup_ns: List[int]\n"
        "    request_total_ns: List[int]\n",
        "class LaneMetricSamples:\n"
        + SAMPLES_DOC.format(new_samples="new_lane_metric_samples", new_storage="new_lane_metric_storage")
        + "\n"
        "    outer_create_ns: MutableSequence[int]\n"
        "    outer_cleanup_ns: MutableSequence[int]\n"
        "    outer_total_ns: MutableSequence[int]\n"
        "    request_create_ns: MutableSequence[int]\n"
        "    request_cleanup_ns: MutableSequence[int]\n"
        "    request_total_ns: MutableSequence[int]\n",
    ),
    (
        "        request_total_ns=[],\n"
        "    )\n"
        "\n"
        "\n"
        "def lane_objects_per_cycle(",
        "        request_total_ns=[],\n"
        "    )\n"
        "\n"
        "\n"
        "def new_lane_metric_storage() -> LaneMetricSamples:\n"
        + STORAGE_DOC.format(samples_class="LaneMetricSamples")
        + "    return LaneMetricSamples(\n"
        '        outer_create_ns=array("q"),\n'
        '        outer_cleanup_ns=array("q"),\n'
        '        outer_total_ns=array("q"),\n'
        '        request_create_ns=array("q"),\n'
        '        request_cleanup_ns=array("q"),\n'
        '        request_total_ns=array("q"),\n'
        "    )\n"
        "\n"
        "\n"
        "def lane_objects_per_cycle(",
    ),
    (
        "        lane_metric_samples = {\n"
        '            "request": new_lane_metric_samples(),\n'
        '            "worker_a": new_lane_metric_samples(),\n'
        '            "worker_b": new_lane_metric_samples(),\n'
        "        }\n",
        "        lane_metric_samples = {\n"
        '            "request": new_lane_metric_storage(),\n'
        '            "worker_a": new_lane_metric_storage(),\n'
        '            "worker_b": new_lane_metric_storage(),\n'
        "        }\n",
    ),
    (
        "def summarize(samples: List[int]) -> Summary:\n",
        "def summarize(samples: Sequence[int]) -> Summary:\n",
    ),
    (
        "        combined_outer_create: List[int] = []\n"
        "        combined_outer_cleanup: List[int] = []\n"
        "        combined_outer_total: List[int] = []\n"
        "        combined_request_create: List[int] = []\n"
        "        combined_request_cleanup: List[int] = []\n"
        "        combined_request_total: List[int] = []\n",
        "        # Packed like the run-long lane storage, so combining lanes does not\n"
        "        # materialize an int object per sample before summarizing.\n"
        '        combined_outer_create: array[int] = array("q")\n'
        '        combined_outer_cleanup: array[int] = array("q")\n'
        '        combined_outer_total: array[int] = array("q")\n'
        '        combined_request_create: array[int] = array("q")\n'
        '        combined_request_cleanup: array[int] = array("q")\n'
        '        combined_request_total: array[int] = array("q")\n',
    ),
])
