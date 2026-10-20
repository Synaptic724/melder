"""Run the final race tests against the original admission method without editing source."""

import hashlib
import importlib.util
from pathlib import Path
import subprocess
import sys

import pytest


def main() -> int:
    """Patch only the original admission method into this test process and report the result."""
    root = Path("C:/Users/Mark/PycharmProjects/melder_private")
    artifacts = root / "context_compass/artifacts/cluster_duplicate_add_20261019"
    baseline = artifacts / "original_conduit_cloud.py"
    source = subprocess.check_output([
        "C:/Program Files/Git/cmd/git.exe", "--no-optional-locks", "show",
        "a2d2355dd0c64d7b277af27c6e53214e560ad7cf:src/melder/aether/aetheric_frame/conduit_cloud.py",
    ], cwd=root)
    baseline.write_bytes(source)
    sys.path.insert(0, str(root / "src"))
    sys.path.insert(0, str(root))
    from melder.aether.aetheric_frame.conduit_cloud import ConduitCloud

    spec = importlib.util.spec_from_file_location("original_cluster_admission", baseline)
    assert spec is not None and spec.loader is not None
    original = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(original)
    print("Original source SHA256:", hashlib.sha256(source).hexdigest())
    print("Only add_conduit_to_cluster is replaced; final tests and all collaborators remain current.")
    with pytest.MonkeyPatch.context() as patch:
        patch.setattr(ConduitCloud, "add_conduit_to_cluster", original.ConduitCloud.add_conduit_to_cluster)
        return pytest.main([
            "-q",
            "tests/integration/melder/aether/test_aether_integration_cluster_transactions_concurrency.py",
            "-k", "forced",
            "--tb=short",
            f"--junitxml={artifacts / 'final_harness_original_method.xml'}",
            f"--basetemp={artifacts / 'tmp_original_method'}",
            "-o", f"cache_dir={artifacts / 'cache'}",
        ])


if __name__ == "__main__":
    raise SystemExit(main())
