"""Capture actual emitted executors and constructor counts, without timing.

Run from the repo root with Python 3.14 and src on PYTHONPATH. Both compile
seams delegate unchanged. All worlds are isolated and closed deterministically;
only diagnostic artifacts are written, and no production source is changed.
"""

import cProfile
import hashlib
import json
import sys
from datetime import UTC, datetime
from pathlib import Path
from types import CodeType
from unittest.mock import patch

from melder.aether.spellbook.spell_compiler.codegen_creation_system.strategies.many_only.compilers import (
    many_only_no_overrides_codegen_creation_compiler as normal_compiler,
)
from melder.aether.spellbook.spell_compiler.codegen_creation_system.strategies.many_only.compilers import (
    many_only_overrides_codegen_creation_compiler as override_compiler,
)
from melder.aether.spellbook.spell_compiler.executor_code_cache import (
    get_or_compile_executor_code,
)
from tests.experimentation.test_melder_creation_overrides_performance import (
    MelderExperiment,
    _path_value,
    _source_fingerprints,
)


class CodegenCapture:
    """Own source snapshots for a diagnostic using one compiler worker.

    The normal cache function is borrowed and called unchanged. Retained data
    contains values only. cleanup releases captured values after writing.
    """

    def __init__(self) -> None:
        """Start with an explicit setup label and empty captured value stores."""
        self.stage = "setup"
        self.sources: list[dict[str, str]] = []
        self.cases: list[dict[str, object]] = []

    def cleanup(self) -> None:
        """Release captured values after diagnostic files have been written."""
        self.sources.clear()
        self.cases.clear()

    def compile(self, *, source: str, source_name: str) -> CodeType:
        """Record a compile request and call the original cache unchanged."""
        self.sources.append({
            "stage": self.stage,
            "source_name": source_name,
            "sha256": hashlib.sha256(source.encode()).hexdigest(),
            "source": source,
        })
        return get_or_compile_executor_code(source=source, source_name=source_name)

    def capture(self, graph: str) -> None:
        """Build a real graph and count fixture constructors for warmed cases."""
        world = MelderExperiment()
        self.stage = f"{graph}_setup"
        try:
            world.setup(graph, "automatic")
            labels = ("normal", "root_one_reused", "root_all_reused", "original_override")
            for label in labels:
                self.stage = f"{graph}_{label}"
                call = world.cases[label][0]
                call()
                profile = cProfile.Profile()
                profile.enable()
                result = call()
                profile.disable()
                assert isinstance(result, world.root_type)
                for path, supplied in world.cases[label][1].items():
                    assert _path_value(result, path) is supplied
                profile.create_stats()
                rows = [
                    {"file": Path(file).name, "line": line, "calls": stats[1]}
                    for (file, line, name), stats in profile.stats.items()
                    if name == "__init__" and file.endswith(("test_overrides_all.py", "deep_layers.py"))
                ]
                constructor_calls = sum(row["calls"] for row in rows)
                assert constructor_calls == {"shallow": 3, "diamond": 5}[graph]
                self.cases.append({
                    "stage": self.stage,
                    "fixture_constructor_calls": constructor_calls,
                    "constructor_rows": rows,
                })
        finally:
            world.cleanup()

    def write(self, directory: Path, before: dict[str, str], after: dict[str, str]) -> None:
        """Persist exact source and provenance; reject concurrent source drift."""
        source_rows = []
        for index, row in enumerate(self.sources):
            filename = f"{index:03d}_{row['stage']}.py"
            (directory / filename).write_text(row["source"] + "\n", encoding="utf-8")
            source_rows.append({key: value for key, value in row.items() if key != "source"})
            source_rows[-1]["path"] = filename
        changed = sorted(path for path in before.keys() | after.keys() if before.get(path) != after.get(path))
        report = {
            "timestamp_utc": datetime.now(UTC).isoformat(),
            "python": sys.version,
            "gil_enabled": sys._is_gil_enabled(),
            "source_changed": changed,
            "source_sha256": before,
            "captures": source_rows,
            "cases": self.cases,
            "timing": "Not measured: source capture and constructor counts only.",
        }
        (directory / "capture.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
        assert not changed, f"Source changed while capturing: {changed}"

    @classmethod
    def run(cls) -> None:
        """Capture shallow/diamond calls and restore both compile seams."""
        directory = Path(__file__).resolve().parent
        repo = directory.parents[2]
        before = _source_fingerprints(repo)
        capture = cls()
        try:
            with (
                patch.object(normal_compiler, "get_or_compile_executor_code", capture.compile),
                patch.object(override_compiler, "get_or_compile_executor_code", capture.compile),
            ):
                capture.capture("shallow")
                capture.capture("diamond")
            capture.write(directory, before, _source_fingerprints(repo))
        finally:
            capture.cleanup()


if __name__ == "__main__":
    CodegenCapture.run()
