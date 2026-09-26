"""
Parity guard between the shared gauntlet's Melder lane and the Melder-only gauntlet.

Purpose:
    Two benchmarks run the same Melder workload:

    - `test_real_world_gauntlet._build_runtime_melder` - the Melder lane of the
      shared three-library comparison, built over the same class graph the
      dependency-injector and dishka lanes use;
    - `test_melder_gauntlet._build_runtime_melder` - the Melder-only gauntlet,
      built over `melder_gauntlet_support`'s copy of that graph.

    They are separate code on purpose, so tuning the Melder-only benchmark can
    never move the shared comparison. The owner's requirement is that they stay
    configured identically, so results from one are comparable with the other
    and neither is skewed. This module enforces that:

    - both builders make the same Melder setup calls (Spellbook construction,
      every configuration property, every bind, the conjure, any frame posture);
    - both conjure the same spells with the same existence;
    - both class graphs and lane sizes match;
    - both lanes meld the same types, in the same order, for every variant;
    - the shared gauntlet still builds when the Melder-only builder is broken,
      which proves it no longer borrows that builder.

Method:
    Setup calls are recorded by wrapping the public Melder entry points the
    builders use (`Spellbook.__init__`, `Spellbook.bind`, `Spellbook.conjure`,
    `Spellbook.configure_aether_frame`, `SpellbookConfiguration.set_property`)
    for the duration of one build, normalized to plain values (classes by name,
    enums by member name). Internal calls those entry points make are recorded
    too, which is intended: equal inputs through equal code must produce equal
    sequences.

Usage:
    python -X gil=0 -m pytest benchmarks/testing_other_di/test_gauntlet_melder_lane_parity.py -q

This is a benchmark diagnostic surface, not production runtime code.
"""

import difflib
import enum
import importlib
import sys
from pathlib import Path
from typing import Any, Callable, Dict, Iterator, List, Tuple

import pytest


def _ensure_local_paths() -> None:
    """
    Ensure the repository root, `src/` and this benchmark directory are importable.

    Contract:
        Adds each path once, so the module imports the same way from pytest or a
        direct `python` run, from the repository root or this directory.
    """
    current_dir = Path(__file__).resolve().parent
    repo_root = current_dir.parents[1]
    for path in (repo_root, repo_root / "src", current_dir):
        path_as_str = str(path)
        if path_as_str not in sys.path:
            sys.path.insert(0, path_as_str)


_ensure_local_paths()

import melder_gauntlet_support as _support
import test_melder_gauntlet as _melder_only
import test_real_world_gauntlet as _shared


class _LaneNames:
    """
    Frame and conduit names both lanes register, used to find the live conduit.

    Contract:
        Both builders conjure `"real-world-gauntlet"` on the frame of the same
        name; the setup-call test fails first if either changes.
    """

    FRAME: str = "real-world-gauntlet"
    CONDUIT: str = "real-world-gauntlet"


def _plain(value: Any) -> Any:
    """
    Normalize one recorded argument to a comparable plain value.

    Contract:
        - Classes compare by `__name__` (the two graphs are distinct class
          objects with the same names and shapes).
        - Enum members compare as `"<EnumType>.<member>"`.
        - Lists, tuples and dicts are normalized recursively (dicts sorted by key).
        - `str`, `int`, `float`, `bool` and `None` pass through.
        - Anything else compares by type name, so runtime objects with identity
          (loggers, conduits) never make two equal setups look different.

    Args:
        value: One positional or keyword argument value.

    Returns:
        Any: A hashable, comparable representation.
    """
    if isinstance(value, type):
        return f"class:{value.__name__}"
    if isinstance(value, enum.Enum):
        return f"{type(value).__name__}.{value.name}"
    if isinstance(value, (list, tuple)):
        return tuple(_plain(item) for item in value)
    if isinstance(value, dict):
        return tuple(sorted((str(key), _plain(item)) for key, item in value.items()))
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    return f"object:{type(value).__name__}"


class _SetupRecorder:
    """
    Record the Melder setup calls one lane builder makes.

    Purpose:
        Capture everything a builder asks Melder to configure, through the public
        entry points both builders use, so two builders can be compared call by
        call.

    Contract:
        - `record(builder)` wraps the entry points with `pytest.MonkeyPatch`,
          runs `builder()`, restores the originals, and returns the built ops
          plus the ordered, normalized call list.
        - Wrappers always delegate to the original; recording never changes
          behaviour.

    Lifecycle / Cleanup:
        Patches are scoped to one `record(...)` call. The caller owns the
        returned ops and must call `ops.cleanup()`.
    """

    def __init__(self) -> None:
        """Initialize an empty call log."""
        self._calls: List[Tuple[str, Any, Any]] = []

    def _wrap(self, label: str, original: Callable[..., Any]) -> Callable[..., Any]:
        """
        Return a wrapper that logs `(label, args, kwargs)` and calls `original`.

        Args:
            label: Name recorded for this entry point.
            original: The unbound method being wrapped.

        Returns:
            Callable[..., Any]: The logging wrapper (method-compatible).
        """

        def wrapper(receiver: Any, *args: Any, **kwargs: Any) -> Any:
            """Log this call's normalized arguments, then delegate unchanged."""
            self._calls.append((label, _plain(args), _plain(kwargs)))
            return original(receiver, *args, **kwargs)

        return wrapper

    def record(self, builder: Callable[[], Any]) -> Tuple[Any, List[Tuple[str, Any, Any]]]:
        """
        Build one lane while recording its Melder setup calls.

        Args:
            builder: A lane builder such as `_shared._build_runtime_melder`.

        Returns:
            Tuple[Any, List[Tuple[str, Any, Any]]]: The built ops and the call log.
        """
        from melder.aether.spellbook.configuration.spellbook_configuration import SpellbookConfiguration
        from melder.aether.spellbook.spellbook import Spellbook

        self._calls = []
        targets = (
            (Spellbook, "__init__", "Spellbook.__init__"),
            (Spellbook, "configure_aether_frame", "Spellbook.configure_aether_frame"),
            (Spellbook, "bind", "Spellbook.bind"),
            (Spellbook, "conjure", "Spellbook.conjure"),
            (SpellbookConfiguration, "set_property", "SpellbookConfiguration.set_property"),
        )
        with pytest.MonkeyPatch.context() as patcher:
            for owner, attribute, label in targets:
                patcher.setattr(owner, attribute, self._wrap(label, getattr(owner, attribute)))
            ops = builder()
        return ops, list(self._calls)


class _MeldRecorder:
    """
    Record what one scope cycle melds, for comparing the two lanes' workloads.

    Contract:
        - `record(call, variant)` wraps `Conduit.meld` and `SpellSpace.meld`,
          runs one scope cycle, and returns the ordered list of
          `(surface, resolved type name)` pairs.
        - Wrappers delegate to the originals; the cycle runs exactly as in the
          benchmark.
    """

    def record(self, call: Callable[[int], Any], variant: int) -> List[Tuple[str, str]]:
        """
        Run one scope cycle and return what it melded.

        Args:
            call: A lane callable such as `ops.request_scope_cycle`.
            variant: Variant index passed to the lane.

        Returns:
            List[Tuple[str, str]]: `(surface, type name)` per meld, in order.
        """
        from melder.aether.conduit.conduit import Conduit
        from melder.aether.conduit.spell_space.spell_space import SpellSpace

        melds: List[Tuple[str, str]] = []

        def wrap(surface: str, original: Callable[..., Any]) -> Callable[..., Any]:
            """Return a meld wrapper that records `(surface, resolved type name)`."""

            def wrapper(receiver: Any, *args: Any, **kwargs: Any) -> Any:
                """Delegate the meld, then record what it resolved."""
                result = original(receiver, *args, **kwargs)
                melds.append((surface, type(result).__name__))
                return result

            return wrapper

        with pytest.MonkeyPatch.context() as patcher:
            patcher.setattr(Conduit, "meld", wrap("conduit", Conduit.meld))
            patcher.setattr(SpellSpace, "meld", wrap("spellspace", SpellSpace.meld))
            call(variant)
        return melds


def _live_spells() -> List[Tuple[Any, ...]]:
    """
    Describe the spells visible through the conjured lane conduit.

    Returns:
        List[Tuple[Any, ...]]: Sorted `(spell_name, binding_name, spellframe,
        existence, resolvable)` rows. Spell ids are excluded: they hash the
        defining module, which differs between the two class graphs by design.
    """
    from melder.aether.aether import Aether

    conduit = Aether().get_conduit_by_name(_LaneNames.CONDUIT, _LaneNames.FRAME)
    return sorted(
        (
            row["spell_name"],
            row["binding_name"],
            row["spellframe"],
            str(row["existence"]),
            row["resolvable"],
        )
        for row in conduit.describe_spells_in_conduit()
    )


def _builders() -> Dict[str, Callable[[], Any]]:
    """
    Return the two lane builders under comparison, keyed by label.

    Returns:
        Dict[str, Callable[[], Any]]: `"shared"` and `"melder_only"` builders.
    """
    return {
        "shared": _shared._build_runtime_melder,
        "melder_only": _melder_only._build_runtime_melder,
    }


def _diff(left: List[Any], right: List[Any]) -> str:
    """
    Render a unified diff of two recorded sequences for assertion messages.

    Args:
        left: Shared-lane sequence.
        right: Melder-only-lane sequence.

    Returns:
        str: Unified diff text (empty when equal).
    """
    return "\n".join(
        difflib.unified_diff(
            [repr(item) for item in left],
            [repr(item) for item in right],
            fromfile="shared gauntlet lane",
            tofile="melder-only gauntlet lane",
            lineterm="",
        )
    )


@pytest.fixture
def built_lanes() -> Iterator[Dict[str, Dict[str, Any]]]:
    """
    Build each lane once (recording setup calls and live spells), then clean up.

    Yields:
        Dict[str, Dict[str, Any]]: Per label: `"calls"` (setup call log) and
        `"spells"` (live spell rows).

    Lifecycle / Cleanup:
        Each lane is cleaned before the next is built, because both reset and
        reuse the Aether singleton.
    """
    lanes: Dict[str, Dict[str, Any]] = {}
    for label, builder in _builders().items():
        ops, calls = _SetupRecorder().record(builder)
        try:
            lanes[label] = {"calls": calls, "spells": _live_spells()}
        finally:
            ops.cleanup()
    yield lanes


def test_lanes_make_identical_melder_setup_calls(built_lanes: Dict[str, Dict[str, Any]]) -> None:
    """
    Both builders configure Melder identically, call for call.

    Contract:
        Compares the full ordered setup-call logs: Spellbook construction
        arguments, every configuration property written, every bind (class name,
        existence, permissions), the conjure (name, dynamic) and any frame
        posture call. Any difference fails with a unified diff.
    """
    shared_calls = built_lanes["shared"]["calls"]
    melder_only_calls = built_lanes["melder_only"]["calls"]
    assert shared_calls, "Recorder captured no setup calls; the entry points it wraps may have moved."
    assert shared_calls == melder_only_calls, (
        "The shared gauntlet's Melder lane and the Melder-only gauntlet no longer configure "
        "Melder identically, so their results are not comparable:\n" + _diff(shared_calls, melder_only_calls)
    )


def test_lanes_conjure_identical_spells(built_lanes: Dict[str, Dict[str, Any]]) -> None:
    """
    Both lanes end up with the same spells, existence and resolvability.

    Contract:
        Reads the conjured conduit's public spell description after each build
        and compares every row except the spell id.
    """
    shared_spells = built_lanes["shared"]["spells"]
    melder_only_spells = built_lanes["melder_only"]["spells"]
    assert len(shared_spells) == len(_shared._ALL_CLASSES)
    assert shared_spells == melder_only_spells, _diff(shared_spells, melder_only_spells)


def test_lane_class_graphs_and_sizes_match() -> None:
    """
    The two workload definitions are the same graph with the same lane sizes.

    Contract:
        For every class name: identical constructor parameter names and
        annotation names, and identical membership in each existence group
        (the shared module lists request roots under its request-scoped group;
        the Melder-only builder adds them explicitly - both must resolve to the
        same set). Lane sizes, objects per root, variant count and seed match.
    """

    def shape(classes: Tuple[type, ...]) -> Dict[str, Tuple[Tuple[str, str], ...]]:
        """Map class name to its constructor `(parameter, annotation name)` pairs."""
        return {
            cls.__name__: tuple((name, annotation.__name__) for name, annotation in _shared._ctor_param_types(cls))
            for cls in classes
        }

    assert list(shape(_shared._ALL_CLASSES).items()) == list(shape(_support.ALL_CLASSES).items())
    request_roots = {"RequestRoot", "WorkerAJobRoot", "WorkerBJobRoot"}
    shared_request = {cls.__name__ for cls in _shared._REQUEST_SCOPED_TYPES}
    melder_only_request = {cls.__name__ for cls in _support.REQUEST_SCOPED_TYPES} | request_roots
    assert shared_request == melder_only_request
    for shared_group, support_group in (
            (_shared._SINGLETON_TYPES, _support.SINGLETON_TYPES),
            (_shared._BOOTSTRAP_TYPES, _support.BOOTSTRAP_TYPES),
            (_shared._OUTER_SCOPED_TYPES, _support.OUTER_SCOPED_TYPES),
    ):
        assert [cls.__name__ for cls in shared_group] == [cls.__name__ for cls in support_group]
    assert (
        _shared._REQUEST_OBJECTS_PER_ROOT,
        _shared._REQUEST_SCOPE_RUNS_DEFAULT,
        _shared._WORKER_A_OBJECTS_PER_ROOT,
        _shared._WORKER_B_OBJECTS_PER_ROOT,
        _shared._WORKER_A_JOBS_DEFAULT,
        _shared._WORKER_B_JOBS_DEFAULT,
        _shared._BOOTSTRAP_FANOUT_PER_SINGLETON,
        _shared._VARIANT_COUNT,
        _shared._LIB_SEEDS["melder"],
    ) == (
        _support.REQUEST_OBJECTS_PER_ROOT,
        _support.REQUEST_SCOPE_RUNS_DEFAULT,
        _support.WORKER_A_OBJECTS_PER_ROOT,
        _support.WORKER_B_OBJECTS_PER_ROOT,
        _support.WORKER_A_JOBS_DEFAULT,
        _support.WORKER_B_JOBS_DEFAULT,
        _support.BOOTSTRAP_FANOUT_PER_SINGLETON,
        _support.VARIANT_COUNT,
        _support.LIB_SEED,
    )


def test_lanes_meld_the_same_workload_per_variant() -> None:
    """
    Every lane and variant melds the same types in the same order in both builders.

    Contract:
        Runs one scope cycle per (lane, variant) on each builder with meld
        recording and compares the `(surface, type name)` sequences.
    """
    recorded: Dict[str, List[List[Tuple[str, str]]]] = {}
    for label, builder in _builders().items():
        ops = builder()
        try:
            ops.spawn_singletons()
            recorded[label] = [
                _MeldRecorder().record(call, variant)
                for call in (ops.request_scope_cycle, ops.worker_a_scope_cycle, ops.worker_b_scope_cycle)
                for variant in range(_shared._VARIANT_COUNT)
            ]
        finally:
            ops.cleanup()
    assert all(recorded["shared"]), "A cycle recorded no melds; the meld entry points may have moved."
    assert recorded["shared"] == recorded["melder_only"], _diff(recorded["shared"], recorded["melder_only"])


def test_shared_gauntlet_does_not_borrow_the_melder_only_builder(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    The shared gauntlet's Melder lane is isolated from the Melder-only gauntlet module.

    Contract:
        Replaces the Melder-only builder (under both import names it can have)
        with one that raises, then builds the shared lane through
        `_shared._build_ops("melder")`. Success proves the shared comparison no
        longer depends on the Melder-only benchmark's code.
    """

    def refuse() -> Any:
        """Stand-in builder that fails if the shared gauntlet ever calls it."""
        raise AssertionError("shared gauntlet called the Melder-only builder")

    for module_name in ("test_melder_gauntlet", "benchmarks.testing_other_di.test_melder_gauntlet"):
        module = importlib.import_module(module_name)
        monkeypatch.setattr(module, "_build_runtime_melder", refuse)
    ops = _shared._build_ops("melder")
    try:
        assert ops.name == "melder"
    finally:
        ops.cleanup()
