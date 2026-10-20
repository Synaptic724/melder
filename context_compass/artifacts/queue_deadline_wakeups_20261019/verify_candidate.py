"""Capture and recheck the exact local qualification inputs and narrow documentation preservation."""
import argparse
import ast
from collections import Counter
from datetime import datetime, timezone
import hashlib
from importlib.metadata import version
import json
from pathlib import Path
import re
import subprocess
import sys
import sysconfig
import tomllib


def git(root: Path, *arguments: str) -> bytes:
    """Read repository metadata without refreshing its index or acquiring optional locks."""
    return subprocess.run(
        ["C:/Program Files/Git/cmd/git.exe", "--no-optional-locks", *arguments],
        cwd=root, check=True, capture_output=True,
    ).stdout


def input_identity(root: Path) -> dict:
    """Hash tracked test/runtime inputs in stable path order and report actual interpreter pins."""
    paths = git(
        root, "ls-files", "-z", "--", "src", "tests", ".github", "pyproject.toml", "uv.lock",
        "llm_support", "context_compass/system_docs/tests_components.md",
        "context_compass/system_docs/tests_components_index.md",
    ).decode().strip("\0").split("\0")
    digest = hashlib.sha256()
    for name in sorted(paths):
        digest.update(name.encode() + b"\0" + hashlib.sha256((root / name).read_bytes()).digest())
    manifest = tomllib.loads((root / ".github/python/tests/3.14.7.toml").read_text(encoding="utf-8"))
    dependencies = {}
    for requirement in manifest["dependencies"]:
        name, expected = requirement.split(";", 1)[0].strip().split("==")
        dependencies[name] = version(name)
        assert dependencies[name] == expected, (name, dependencies[name], expected)
    assert sysconfig.get_config_var("Py_GIL_DISABLED") == 1 and not sys._is_gil_enabled()
    assert git(root, "diff", "--name-only", "--", "src").strip() == b"", "Production files changed"
    return {
        "base_revision": git(root, "rev-parse", "HEAD").decode().strip(),
        "tracked_input_count": len(paths), "tracked_inputs_sha256": digest.hexdigest(),
        "test_sha256": hashlib.sha256((root / paths[paths.index(
            "tests/unit/melder/aether/conduit/creations/test_managed_spell_quantity.py"
        )]).read_bytes()).hexdigest(),
        "python": sys.version, "executable": sys.executable, "gil_enabled": sys._is_gil_enabled(),
        "dependencies": dependencies,
    }


def verify_document(root: Path, evidence: Path) -> dict:
    """Account for every removed normalized line and verify the changed C1 extent and portability."""
    before = (evidence / "before/tests_components.md").read_text(encoding="utf-8")
    path = root / "context_compass/system_docs/tests_components.md"
    raw = path.read_bytes()
    after = raw.decode("utf-8")
    before_lines = Counter(" ".join(line.split()) for line in before.splitlines() if line.strip())
    after_lines = Counter(" ".join(line.split()) for line in after.splitlines() if line.strip())
    missing = before_lines - after_lines
    expected = Counter({
        "- Updated: 2026-10-19T14:19:12Z": 1, "end_line: 1040": 1, "loc: 1040": 1,
        "verified_at: 2026-10-18T01:46:13Z": 1,
    })
    assert missing == expected, missing
    assert b"\r" not in raw
    assert not re.search(r"context_compass/|agent_onboarding/|tools/system_documents/|index_document\.py|system_docs/|patches/active/", after)
    test_path = "tests/unit/melder/aether/conduit/creations/test_managed_spell_quantity.py"
    entry = after.split(f"- path: `{test_path}`", 1)[1].split("- path:", 1)[0]
    actual_loc = len((root / test_path).read_text(encoding="utf-8").splitlines())
    assert f"end_line: {actual_loc}" in entry and f"loc: {actual_loc}" in entry
    original = ast.parse(git(root, "show", f"70ea25d23394f939bc75337e232a0e598d402ac4:{test_path}").decode())
    original_test = next(node for node in original.body if isinstance(node, ast.FunctionDef)
                         and node.name == "test_queue_deadline_is_taken_once_across_wakeups")
    preserved = ast.parse((evidence / "original_deadline_test.py").read_text(encoding="utf-8")).body[0]
    assert ast.dump(original_test, include_attributes=False) == ast.dump(preserved, include_attributes=False)
    return {"preserved_claims": True, "intentional_metadata_replacements": dict(missing),
            "test_loc": actual_loc, "document_sha256": hashlib.sha256(raw).hexdigest(),
            "original_control_matches_base_ast": True, "line_ending": "lf"}


def main() -> None:
    """Capture before runtime testing, or refuse acceptance if any qualified input subsequently changed."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=("capture", "check"))
    mode = parser.parse_args().mode
    root = Path("C:/Users/Mark/PycharmProjects/melder_private")
    evidence = root / "context_compass/artifacts/queue_deadline_wakeups_20261019"
    inputs = input_identity(root)
    documentation = verify_document(root, evidence)
    target = evidence / "qualification_inputs.json"
    if mode == "capture":
        target.write_text(json.dumps(inputs, indent=2) + "\n", encoding="utf-8")
    else:
        assert json.loads(target.read_text(encoding="utf-8")) == inputs, "Qualified inputs changed"
    receipt = {"checked_at": datetime.now(timezone.utc).isoformat(), "mode": mode,
               "qualified_inputs": "unchanged" if mode == "check" else "captured", **documentation}
    (evidence / "documentation_verification.json").write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print(f"OK {mode}: {inputs['tracked_input_count']} hashed inputs; test extent/preservation/control verified")


if __name__ == "__main__":
    main()
