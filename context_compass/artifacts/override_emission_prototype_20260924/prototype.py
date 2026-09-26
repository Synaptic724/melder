"""Measure static named-override emission using actual cached executor objects.

This diagnostic supports only disposal-free, class-only many plans with scalar
named sockets and no contract/positional payloads. It changes executor code in
one isolated, single-thread experiment process, outside timing samples. All
code/defaults and namespace additions are restored before world cleanup.
Production source, public dispatch, targeting and cache identity are unchanged.
"""

import hashlib
import inspect
import json
import os
import statistics
import sys
import time
from collections.abc import Callable
from datetime import UTC, datetime
from functools import partial
from pathlib import Path
from types import CodeType, FrameType, FunctionType, SimpleNamespace
from typing import TYPE_CHECKING, Optional, cast
from unittest.mock import patch

from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spell_compiler.codegen_creation_system.strategies.many_only.steps import (
    many_only_finalize_creation_context_step as finalize_module,
)
from tests.experimentation.test_melder_creation_overrides_performance import (
    MelderExperiment,
    _average_ns,
    _path_value,
    _source_fingerprints,
)

if TYPE_CHECKING:
    from melder.aether.spellbook.spell_compiler.dag.dag_index import SocketRef


class ExecutorPair:
    """Own a reversible code swap and borrow one real per-shape executor.

    No supplied runtime values are retained in generated source or globals.
    Only targets, Spell error metadata and exact SocketRefs are prebound.
    Changes are local to this experiment process and require quiescent callers.
    """

    def __init__(self, executor: FunctionType) -> None:
        """Retain the original body/defaults; reject closure-based executors."""
        assert not executor.__code__.co_freevars
        self.executor = executor
        self.original_code = executor.__code__
        self.original_defaults = executor.__kwdefaults__
        self.prototype_code: Optional[CodeType] = None
        self.added_names: list[str] = []
        self.source = ""
        self.build_ns = 0

    def cleanup(self) -> None:
        """Restore the original callable before releasing namespace additions."""
        self.select(False)
        for name in self.added_names:
            del self.executor.__globals__[name]
        self.added_names.clear()
        del self.executor
        del self.original_code
        del self.original_defaults
        del self.prototype_code

    def select(self, prototype: bool) -> None:
        """Select a body outside samples; no dispatcher is added to timed calls."""
        if prototype:
            assert self.prototype_code is not None
            self.executor.__code__ = self.prototype_code
            self.executor.__kwdefaults__ = None
        else:
            self.executor.__code__ = self.original_code
            self.executor.__kwdefaults__ = self.original_defaults

    def _bind(self, name: str, value: object) -> str:
        """Publish a static compile-time binding and track it for restoration."""
        assert name not in self.executor.__globals__
        self.executor.__globals__[name] = value
        self.added_names.append(name)
        return name

    def lower(self, prefer_positional: bool = True) -> None:
        """Generate direct calls and locals from actual ordered steps.

        Every original constructor remains in order, including unused results.
        Complete positional-or-keyword layouts can use normal-style positional
        calls; incomplete layouts retain explicit keywords to preserve defaults.
        Unsupported layout is a diagnostic failure, never an optimized result.
        """
        started = time.perf_counter_ns()
        assert self.original_defaults is not None
        steps = cast(tuple[SimpleNamespace, ...], self.original_defaults["steps"])
        targets = self.original_defaults["step_override_targets"]
        slots = {step.instance_key: index for index, step in enumerate(steps)}
        root_index = slots[self.original_defaults["root_instance_key"]]
        lines = ["def _prototype_executor(meld, override_map, root_positional_override):"]
        for index, (step, sockets) in enumerate(zip(steps, targets, strict=True)):
            self._lower_step(lines, index, step, sockets, slots, prefer_positional)
        lines.append(f"    return v{root_index}")
        self.source = "\n".join(lines) + "\n"
        code = compile(self.source, "<experimental_static_many_override>", "exec")
        exec(code, self.executor.__globals__)
        candidate = self.executor.__globals__.pop("_prototype_executor")
        assert isinstance(candidate, FunctionType) and not candidate.__code__.co_freevars
        self.prototype_code = candidate.__code__
        self.build_ns = time.perf_counter_ns() - started

    def _lower_step(
        self, lines: list[str], index: int, step: SimpleNamespace,
        sockets: tuple[SocketRef, ...], slots: dict[tuple[str, Optional[int]], int],
        prefer_positional: bool,
    ) -> None:
        """Lower one qualified occurrence with exact per-call socket operands."""
        spell = step.spell
        assert spell.existence is Existence.many and spell.is_class_spell
        assert not spell.has_disposal_methods and not step.collection_param_names
        assert not step.has_contract_payload and not step.uses_positional_override
        assert step.contract_positional_override is None
        parameters = inspect.signature(spell.spell).parameters
        assert all(p.kind is inspect.Parameter.POSITIONAL_OR_KEYWORD for p in parameters.values())
        operands: dict[str, str] = {}
        for param, dependency_keys in step.dependency_resolution_order:
            assert len(dependency_keys) == 1 and slots[dependency_keys[0]] < index
            operands[param] = f"v{slots[dependency_keys[0]]}"
        seen = set()
        for socket_index, socket in enumerate(sockets):
            name = socket.param_name
            assert name in parameters and name not in seen
            seen.add(name)
            socket_name = self._bind(f"_prototype_socket_{index}_{socket_index}", socket)
            value_name = f"o{index}_{socket_index}"
            lines.append(f"    {value_name} = override_map[{socket_name}]")
            operands[name] = value_name
        assert all(name in parameters for name in operands)
        target = self._bind(f"_prototype_target_{index}", spell.spell)
        metadata = self._bind(f"_prototype_spell_{index}", spell)
        if prefer_positional and len(operands) == len(parameters):
            arguments = ", ".join(operands[name] for name in parameters)
        else:
            arguments = ", ".join(f"{name}={operands[name]}" for name in parameters if name in operands)
        lines.extend([
            "    try:",
            f"        v{index} = {target}({arguments})",
            "    except Exception as exc:",
            f"        error_spell = {metadata}",
            "        raise MeldExecutionError(",
            "            spell_id=error_spell.spell_index.selected_spell_id,",
            "            spell_name=error_spell.spell_name,",
            "            message=f\"Error invoking spell '{error_spell.spell_name}'.\",",
            "            inner=exc,",
            "        ) from exc",
        ])


class EmissionExperiment:
    """Own one graph's executor pairs and value-only results for a serial run."""

    def __init__(self) -> None:
        """Borrow the real binder and create empty per-world diagnostic state."""
        self.original_bind = finalize_module._compile_overrides_codegen_creation_executor_from_code_object_with_prefilter_cache
        self.pairs: list[ExecutorPair] = []
        self.rows: list[dict[str, object]] = []
        self.parity: list[dict[str, object]] = []
        self.preparation: list[dict[str, object]] = []
        self.excluded: list[dict[str, object]] = []
        self.prototype_hash = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
        self.repeats = int(os.environ.get("PROTOTYPE_REPEATS", "7"))
        self.sample_ms = float(os.environ.get("PROTOTYPE_SAMPLE_MS", "30"))
        self.call_style = os.environ.get("PROTOTYPE_CALL_STYLE", "positional")
        assert self.repeats > 0 and self.sample_ms > 0
        assert self.call_style in ("positional", "keyword")

    def cleanup(self) -> None:
        """Restore every remaining executor and release captured result values."""
        self._restore_world()
        self.rows.clear()
        self.parity.clear()
        self.preparation.clear()
        self.excluded.clear()
        del self.original_bind

    def _restore_world(self) -> None:
        """Restore body/defaults before the owning Melder world is torn down."""
        for pair in self.pairs:
            pair.cleanup()
        self.pairs.clear()

    def bind(self, **kwargs: object) -> FunctionType:
        """Capture a normal completed binding, without changing its behavior."""
        executor = self.original_bind(**kwargs)
        assert isinstance(executor, FunctionType)
        self.pairs.append(ExecutorPair(executor))
        return executor

    def select(self, prototype: bool) -> None:
        """Switch all known shapes outside timing and outside concurrent calls."""
        for pair in self.pairs:
            pair.select(prototype)

    def observe(self, call: Callable[[], object]) -> tuple[object, list[str], Optional[Callable[[], object]]]:
        """Collect constructor order and the real resolved executor arguments.

        Profiling is restricted to this untimed call and the previous profiler
        is restored. The returned inner closure is a borrowed executor control.
        """
        sequence: list[str] = []
        inner: list[Callable[[], object]] = []

        def trace(frame: FrameType, event: str, arg: object) -> None:
            """Capture fixture constructor identity and the active inner executor."""
            if event != "call":
                return
            code = frame.f_code
            if code.co_name == "__init__" and code.co_filename.endswith(("test_overrides_all.py", "deep_layers.py")):
                sequence.append(type(frame.f_locals["self"]).__qualname__)
            if code.co_name not in ("_overrides_codegen_creation_executor", "_prototype_executor"):
                return
            for pair in self.pairs:
                if frame.f_globals is pair.executor.__globals__:
                    meld = frame.f_locals["meld"]
                    override_map = frame.f_locals["override_map"]
                    assert frame.f_locals["root_positional_override"] is None
                    inner.append(partial(pair.executor, meld, override_map, None))
                    break

        previous = sys.getprofile()
        sys.setprofile(trace)
        try:
            result = call()
        finally:
            sys.setprofile(previous)
        assert len(inner) <= 1
        return result, sequence, inner[0] if inner else None

    def qualify_and_measure(self, graph: str, directory: Path) -> None:
        """Prepare, qualify and time both bodies on a single isolated world."""
        world = MelderExperiment()
        try:
            with patch.object(finalize_module, "_compile_overrides_codegen_creation_executor_from_code_object_with_prefilter_cache", self.bind):
                world.setup(graph, "automatic")
                calls = {label: case for label, case in world.cases.items() if label.startswith(("root_one", "root_all", "original", "nested"))}
                self.excluded.append({"graph": graph, "cases": sorted(set(world.cases) - set(calls) - {"normal"})})
                if graph == "shallow":
                    self._prepare_alternation(world)
                controls: dict[str, tuple[Callable[[], object], Callable[[], object]]] = {}
                sequences: dict[str, list[str]] = {}
                for label, (call, expected, _note) in calls.items():
                    bindings_before = len(self.pairs)
                    start = time.perf_counter_ns()
                    call()
                    self.preparation.append({"graph": graph, "case": label, "first_case_call_ns": time.perf_counter_ns() - start, "new_executor_bindings": len(self.pairs) - bindings_before})
                    result, sequence, inner = self.observe(call)
                    assert inner is not None
                    for path, supplied in expected.items():
                        assert _path_value(result, path) is supplied
                    controls[label] = (call, inner)
                    sequences[label] = sequence
                for index, pair in enumerate(self.pairs):
                    pair.lower(prefer_positional=self.call_style == "positional")
                    (directory / f"{graph}_{index:02d}_prototype.py").write_text(pair.source, encoding="utf-8")
                    self.preparation.append({"graph": graph, "executor": index, "additional_prototype_build_ns": pair.build_ns})
                self.select(True)
                normal_count = {"shallow": 3, "wide": 9, "diamond": 5, "deep": 511}[graph]
                for label, (call, expected, _note) in calls.items():
                    result, sequence, _inner = self.observe(call)
                    assert sequence == sequences[label] and len(sequence) == normal_count
                    for path, supplied in expected.items():
                        assert _path_value(result, path) is supplied
                    self.parity.append({"graph": graph, "case": label, "constructor_count": len(sequence), "constructor_order": sequence, "identity": "passed"})
                if graph == "shallow":
                    self._verify_alternation(world)
                normal_call = world.cases["normal"][0]
                normal, normal_sequence, _ = self.observe(normal_call)
                assert len(normal_sequence) == normal_count
                assert isinstance(normal, world.root_type)
                self.measure(graph, controls, normal_call)
        finally:
            self._restore_world()
            world.cleanup()

    def _prepare_alternation(self, world: MelderExperiment) -> None:
        """Materialize both equal-count socket shapes before compiling prototypes."""
        for key in ("a", "b"):
            world.conduit.meld(spell_id=world.root_id, override={key: object()})

    def _verify_alternation(self, world: MelderExperiment) -> None:
        """Prove shape and value changes never capture or leak a supplied value."""
        pair_count = len(self.pairs)
        for index in range(64):
            key = "a" if index % 2 == 0 else "b"
            other = "b" if key == "a" else "a"
            value = (None, False, 0, object())[(index // 2) % 4]
            root = world.conduit.meld(spell_id=world.root_id, override={key: value})
            assert _path_value(root, key) is value
            assert _path_value(root, other) is not value
            normal = world.conduit.meld(spell_id=world.root_id)
            assert _path_value(normal, key) is not value
        assert len(self.pairs) == pair_count
        self.parity.append({"graph": "shallow", "case": "alternating_a_b_values", "iterations": 64, "identity": "passed", "new_shape_compiles": 0})

    def measure(
        self, graph: str, controls: dict[str, tuple[Callable[[], object], Callable[[], object]]],
        normal: Callable[[], object],
    ) -> None:
        """Rotate paired samples, using equal iteration counts within each pair."""
        tasks = [(label, door, call) for label, pair in controls.items() for door, call in zip(("public", "executor"), pair, strict=True)]
        tasks.append(("normal", "public", normal))
        counts: dict[tuple[str, str], int] = {}
        samples: dict[tuple[str, str], dict[str, list[float]]] = {}
        for label, door, call in tasks:
            self.select(False)
            for _ in range(128):
                call()
            probe = _average_ns(call, 128, "disabled")
            counts[label, door] = max(128, min(100_000, int(self.sample_ms * 1e6 / probe)))
            samples[label, door] = {"current": [], "prototype": []}
        for repeat in range(self.repeats):
            shift = repeat % len(tasks)
            for offset, (label, door, call) in enumerate(tasks[shift:] + tasks[:shift]):
                order = (False, True) if (repeat + offset) % 2 == 0 else (True, False)
                for prototype in order:
                    self.select(prototype)
                    for _ in range(64):
                        call()
                    samples[label, door]["prototype" if prototype else "current"].append(
                        _average_ns(call, counts[label, door], "disabled")
                    )
        for label, door, _call in tasks:
            current = statistics.median(samples[label, door]["current"])
            candidate = statistics.median(samples[label, door]["prototype"])
            self.rows.append({
                "graph": graph, "case": label, "door": door, "iterations": counts[label, door],
                "samples_ns": samples[label, door], "current_median_ns": current, "prototype_median_ns": candidate,
                "speedup": current / candidate,
                "latency_reduction_percent": 100 * (1 - candidate / current),
            })

    def write(self, directory: Path, before: dict[str, str], after: dict[str, str]) -> None:
        """Persist paired observations and explicit runtime/source provenance."""
        changed = sorted(path for path in before.keys() | after.keys() if before.get(path) != after.get(path))
        prototype_after = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
        payload = {
            "timestamp": datetime.now(UTC).isoformat(), "python": sys.version, "executable": sys.executable,
            "gil_enabled": sys._is_gil_enabled(), "repeats": self.repeats, "sample_ms": self.sample_ms,
            "call_style": self.call_style,
            "gc": "disabled in samples; restored afterward", "source_changed": changed,
            "source_sha256": before, "results": self.rows, "parity": self.parity, "preparation": self.preparation,
            "prototype_sha256_before": self.prototype_hash, "prototype_sha256_after": prototype_after,
            "excluded_cases": self.excluded,
        }
        (directory / "results.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")
        lines = ["# Static override emission experiment", "", "Same constructors and public gates; no production source edits.", "", "| Graph | Case | Door | Current us | Prototype us | Speedup |", "| --- | --- | --- | ---: | ---: | ---: |"]
        for row in self.rows:
            lines.append(f"| {row['graph']} | {row['case']} | {row['door']} | {row['current_median_ns'] / 1000:.3f} | {row['prototype_median_ns'] / 1000:.3f} | {row['speedup']:.2f}x |")
        (directory / "results.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
        assert not changed, f"Runtime changed during measurement: {changed}"
        assert prototype_after == self.prototype_hash, "Prototype changed during measurement"

    @classmethod
    def run(cls) -> None:
        """Run the bounded graph matrix serially and restore all in-memory edits."""
        directory = Path(__file__).resolve().parent
        repo = directory.parents[2]
        before = _source_fingerprints(repo)
        experiment = cls()
        try:
            for graph in os.environ.get("PROTOTYPE_GRAPHS", "shallow,wide,diamond,deep").split(","):
                experiment.qualify_and_measure(graph, directory)
            experiment.write(directory, before, _source_fingerprints(repo))
        finally:
            experiment.cleanup()


if __name__ == "__main__":
    EmissionExperiment.run()
