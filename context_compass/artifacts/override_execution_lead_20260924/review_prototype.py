"""Independently qualify eligible prototype bodies against existing many-only contracts.

Run from the repository root with root and src on PYTHONPATH, after peer timing
finishes. No timings are collected. The isolated process substitutes executor
bodies as they are built and restores each body, defaults and globals afterward.
Existing tests own runtime setup/teardown; this runner owns only the reversible
prototype installation. Production files and test expectations remain unchanged.
"""

import hashlib
import json
from pathlib import Path
from types import FunctionType
from unittest.mock import patch

import pytest

from context_compass.artifacts.override_emission_prototype_20260924 import prototype


class CandidateReview(prototype.EmissionExperiment):
    """Install each candidate immediately so real regressions execute its body.

    Contract:
        Reuse the prototype's explicit eligibility assertions. A rejected shape
        fails this focused review rather than silently using the original body.
        The inherited cleanup restores all retained executors after pytest.
    """

    def bind(self, **kwargs: object) -> FunctionType:
        """Bind the real executor, lower its candidate, and select it before use."""
        executor = super().bind(**kwargs)
        self.pairs[-1].lower()
        self.pairs[-1].select(True)
        return executor


def main() -> int:
    """Run unchanged many-only regressions and record installation/restoration evidence.

    Returns:
        The pytest exit status, or an assertion failure if code/defaults or static
        namespace additions survive the review's cleanup boundary.
    """
    directory = Path(__file__).resolve().parent
    candidate_path = Path(prototype.__file__)
    candidate_sha256 = hashlib.sha256(candidate_path.read_bytes()).hexdigest()
    review = CandidateReview()
    try:
        with patch.object(
            prototype.finalize_module,
            "_compile_overrides_codegen_creation_executor_from_code_object_with_prefilter_cache",
            review.bind,
        ):
            result = int(pytest.main([
                "-q", "-p", "no:cacheprovider",
                "tests/component/melder/aether/conduit/test_conduit_component_non_resolvable_overrides.py",
                "-k", "many_only",
                f"--junitxml={directory / 'prototype_regressions.xml'}",
            ]))
        originals = [
            (pair.executor, pair.original_code, pair.original_defaults, tuple(pair.added_names))
            for pair in review.pairs
        ]
    finally:
        review.cleanup()
    assert originals, "No candidate body was installed; the review did not exercise the prototype."
    for executor, code, defaults, names in originals:
        assert executor.__code__ is code
        assert executor.__kwdefaults__ is defaults
        assert all(name not in executor.__globals__ for name in names)
    assert hashlib.sha256(candidate_path.read_bytes()).hexdigest() == candidate_sha256
    (directory / "prototype_review.json").write_text(
        json.dumps({
            "pytest_exit": result,
            "candidate_sha256": candidate_sha256,
            "executors_installed_and_restored": len(originals),
            "timing": "Not measured; independent contract qualification only.",
        }, indent=2) + "\n", encoding="utf-8",
    )
    return result


if __name__ == "__main__":
    raise SystemExit(main())
