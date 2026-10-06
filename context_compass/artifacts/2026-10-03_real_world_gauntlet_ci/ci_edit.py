"""Wire the owner's gauntlet into existing Melder CI and expose pytest configuration."""

from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path


def replace_once(text: str, old: str, new: str) -> str:
    """Replace one exact reviewed passage, refusing missing or ambiguous inputs."""
    if text.count(old) != 1:
        raise ValueError(f"Expected one passage: {old[:100]!r}")
    return text.replace(old, new, 1)


def main() -> None:
    """Prepare all edits before writing, preserve preimages and retain a bounded application record."""
    repo = Path("C:/Users/Mark/PycharmProjects/melder_private")
    artifact = repo / "context_compass/artifacts/2026-10-03_real_world_gauntlet_ci"
    source_path = "benchmarks/testing_other_di/test_real_world_gauntlet.py"
    source = (repo / source_path).read_text(encoding="utf-8")
    source = replace_once(source,
        '# Benchmark configuration: edit this list to change the default thread-count relay.\n'
        'REAL_WORLD_GAUNTLET_THREAD_COUNTS: list[int] = [3, 5, 7, 9]\n',
        '# EDIT THESE SETTINGS, then run test_real_world_gauntlet through pytest.\n'
        '# Every library/thread-count/round runs in a fresh GIL-off process automatically.\n'
        'REAL_WORLD_GAUNTLET_ITERATIONS: int = 5_000\n'
        'REAL_WORLD_GAUNTLET_THREAD_COUNTS: list[int] = [3, 5, 7, 9]\n'
        'REAL_WORLD_GAUNTLET_ROUNDS: int = 1\n')
    source = replace_once(source,
        '            iterations=_env_int("DI_GAUNTLET_ITERS", 5_000),\n',
        '            iterations=_env_int("DI_GAUNTLET_ITERS", REAL_WORLD_GAUNTLET_ITERATIONS),\n')
    source = replace_once(source,
        '    rounds = _env_int("REAL_WORLD_GAUNTLET_ROUNDS", 1)\n',
        '    rounds = _env_int("REAL_WORLD_GAUNTLET_ROUNDS", REAL_WORLD_GAUNTLET_ROUNDS)\n')
    source = replace_once(source,
        '        - `REAL_WORLD_GAUNTLET_ROUNDS` unset or blank means one round; any other\n',
        '        - `REAL_WORLD_GAUNTLET_ROUNDS` unset or blank uses the editable default; any other\n')
    source = replace_once(source,
        '        - Values only (str, int, float, bool and lists of them), so `json.dumps`\n',
        '        - JSON values only, including named lane cycle/variant dictionaries, so `json.dumps`\n')
    source = replace_once(source,
        'class _GauntletConfig:\n',
        'class _GauntletConfig:\n'
        '    """Scalar workload settings for one measured process.\n\n'
        '    The pytest wrapper selects each thread count from the editable relay.\n'
        '    Environment inputs support CI and existing single-count tools; ordinary\n'
        '    pytest use needs only the configuration block at the top of this file.\n'
        '    """\n')
    source = replace_once(source,
        '    def from_env() -> _GauntletConfig:\n',
        '    def from_env() -> _GauntletConfig:\n'
        '        """Read optional overrides over file defaults and reject empty workloads.\n\n'
        '        Counts must be positive; each request workload still creates at least\n'
        '        500 objects. Conversion errors and invalid counts propagate before\n'
        '        a library container or worker thread is created.\n'
        '        """\n')

    download = Path("C:/Users/Mark/Downloads/real-world-gauntlet.yml")
    workflow = download.read_text(encoding="utf-8")
    workflow = workflow[workflow.index("name:"):]
    workflow = replace_once(workflow,
        "on:\n  push:\n    branches: ['**']\n  workflow_dispatch:\n",
        "# ci.yml invokes this for full feature/promotion qualification.\n"
        "# Manual runs can override the benchmark file's editable thread-count list.\n"
        "on:\n  workflow_call:\n    inputs:\n      thread-counts:\n"
        "        description: Optional comma-separated counts; blank uses the benchmark configuration.\n"
        "        type: string\n        required: false\n        default: ''\n"
        "  workflow_dispatch:\n    inputs:\n      thread-counts:\n"
        "        description: Optional comma-separated counts; blank uses the benchmark configuration.\n"
        "        type: string\n        required: false\n        default: ''\n")
    workflow = replace_once(workflow,
        '    name: Gauntlet / ${{ github.ref_name }} / ${{ matrix.os }}\n',
        '    name: Gauntlet / ${{ github.head_ref || github.ref_name }} / ${{ matrix.os }}\n')
    for line in ("      PYTHON_GIL: '0'\n", "      DI_GAUNTLET_ITERS: '5000'\n",
                 "      DI_GAUNTLET_THREADS: '3'\n", "      REAL_WORLD_GAUNTLET_ROUNDS: '1'\n"):
        workflow = replace_once(workflow, line, "")
    workflow = replace_once(workflow,
        "      PYTEST_DISABLE_PLUGIN_AUTOLOAD: '1'\n",
        "      PYTEST_DISABLE_PLUGIN_AUTOLOAD: '1'\n"
        "      REAL_WORLD_GAUNTLET_THREAD_COUNTS: ${{ inputs.thread-counts }}\n")
    for step in ("Record source and runtime provenance", "Verify all libraries and no-GIL imports"):
        workflow = replace_once(workflow, f"      - name: {step}\n        shell: python\n",
            f"      - name: {step}\n        env:\n          PYTHON_GIL: '0'\n        shell: python\n")
    workflow = replace_once(workflow,
        "        timeout-minutes: 45\n        shell: python\n",
        "        timeout-minutes: 45\n        env:\n          PYTHON_GIL: '0'\n        shell: python\n")
    workflow = replace_once(workflow,
        "          data = {\n",
        "          sys.path.insert(0, str(Path.cwd()))\n"
        "          from benchmarks.testing_other_di import test_real_world_gauntlet as gauntlet\n"
        "          config = gauntlet._GauntletConfig.from_env()\n"
        "          thread_counts = gauntlet._gauntlet_thread_counts()\n"
        "          rounds = gauntlet._gauntlet_rounds()\n"
        "          data = {\n")
    workflow = replace_once(workflow,
        "              'iterations_per_library': 5000, 'threads': 3, 'rounds': 1,\n",
        "              'iterations_per_library': config.iterations, 'thread_counts': list(thread_counts), 'rounds': rounds,\n")
    workflow = replace_once(workflow,
        "          report = Path('gauntlet-results')\n          (report / 'requirements.txt')",
        "          report = Path('gauntlet-results')\n          report.mkdir(exist_ok=True)\n          (report / 'requirements.txt')")
    # The settings reader imports pytest through the benchmark module, so install first.
    provenance_start = workflow.index("      - name: Record source and runtime provenance\n")
    install_start = workflow.index("      - name: Install identical pinned benchmark dependencies\n")
    verify_start = workflow.index("      - name: Verify all libraries and no-GIL imports\n")
    workflow = (workflow[:provenance_start] + workflow[install_start:verify_start]
                + workflow[provenance_start:install_start] + workflow[verify_start:])
    workflow = replace_once(workflow,
        "          verified = {}\n",
        "          expected = json.loads((report / 'environment.json').read_text(encoding='utf-8'))\n"
        "          iterations = expected['iterations_per_library']\n"
        "          counts = expected['thread_counts']\n"
        "          rounds = expected['rounds']\n"
        "          verified = {}\n")
    workflow = replace_once(workflow,
        "                  len(configs) == 1\n"
        "                  and all(token in configs[0].split(', ') for token in ('gil=disabled', 'iterations=5000', 'threads=3'))\n"
        "                  and f'[{lib}] gauntlet total(5000)=' in output\n"
        "                  and f'[{lib}] gauntlet throughput |' in output\n",
        "                  len(configs) == len(counts) * rounds\n"
        "                  and sorted(int(re.search(r'threads=(\\d+)', config)[1]) for config in configs) == sorted(counts * rounds)\n"
        "                  and all(all(token in config.split(', ') for token in ('gil=disabled', f'iterations={iterations}')) for config in configs)\n"
        "                  and output.count(f'[{lib}] gauntlet total({iterations})=') == len(counts) * rounds\n"
        "                  and output.count(f'[{lib}] gauntlet throughput |') == len(counts) * rounds\n")
    workflow = replace_once(workflow,
        "          outcome = {'exit_code': status, 'verified_libraries': verified,\n",
        "          outcome = {'exit_code': status, 'verified_libraries': verified,\n"
        "                     'validation_passed': status == 0 and all(verified.values()),\n"
        "                     'thread_counts': counts, 'rounds': rounds,\n")
    workflow = replace_once(workflow,
        "              '] gauntlet config:', '] gauntlet total(', '] gauntlet throughput')))\n",
        "              '] gauntlet config:', '] gauntlet total(', '] gauntlet throughput', '] isolated median', '] lane=')))\n")
    workflow = workflow.replace("Branch-native real-world gauntlet", "Real-world gauntlet by thread count")
    workflow = workflow.replace("Compare branches within each OS.", "Compare matching thread counts within each OS.")
    workflow = replace_once(workflow,
        "          # SHA avoids slashes and other artifact-invalid characters in branch names.\n",
        "          # SHA identifies the actual tested PR merge commit (or manually selected commit).\n")

    ci_path = ".github/workflows/ci.yml"
    ci = (repo / ci_path).read_text(encoding="utf-8")
    ci = replace_once(ci, '  documentation:\n',
        "  real-world-gauntlet:\n    needs: branch-policy\n"
        "    if: needs.branch-policy.outputs.runtime-required == 'true'\n"
        "    uses: ./.github/workflows/real-world-gauntlet.yml\n\n  documentation:\n")
    ci = replace_once(ci,
        '    needs: [branch-policy, hygiene, source-assets, repo-assets, tests, documentation, packages, source-qualification]\n',
        '    needs: [branch-policy, hygiene, source-assets, repo-assets, tests, real-world-gauntlet, documentation, packages, source-qualification]\n')
    policy_path = ".github/scripts/ci_policy.py"
    policy = (repo / policy_path).read_text(encoding="utf-8")
    policy = replace_once(policy,
        '    FULL_JOBS: tuple[str, ...] = ("source-assets", "repo-assets", "tests", "documentation")\n',
        '    FULL_JOBS: tuple[str, ...] = ("source-assets", "repo-assets", "tests", "real-world-gauntlet", "documentation")\n')
    policy_tests_path = "tests/unit/github_workflows/test_ci_policy.py"
    policy_tests = (repo / policy_tests_path).read_text(encoding="utf-8")
    policy_tests = policy_tests.replace('"repo-assets", "tests", "documentation"',
                                       '"repo-assets", "tests", "real-world-gauntlet", "documentation"')
    policy_tests = replace_once(policy_tests,
        '                                "documentation", "source-qualification", "packages"])\n',
        '                                "real-world-gauntlet", "documentation", "source-qualification", "packages"])\n')
    policy_tests = replace_once(policy_tests,
        '    ("dev", "feature/work", (True, False, False)),\n',
        '    ("dev", "feature/work", (True, False, False)),\n'
        '    ("dev", "codex_features2", (True, False, False)),\n')
    qualification_path = "tests/unit/github_workflows/test_source_qualification.py"
    qualification = (repo / qualification_path).read_text(encoding="utf-8")
    qualification = qualification.replace('"repo-assets", "tests", "documentation", "packages"',
        '"repo-assets", "tests", "real-world-gauntlet", "documentation", "packages"')
    qualification = replace_once(qualification,
        '@pytest.mark.parametrize("mode", ["sha", "dirty", "parents", "failed-tests"])\n',
        '@pytest.mark.parametrize("mode", ["sha", "dirty", "parents", "failed-tests", "failed-gauntlet"])\n')
    qualification = replace_once(qualification,
        '        results["tests"]["result"] = "failure"\n',
        '        results["real-world-gauntlet" if mode == "failed-gauntlet" else "tests"]["result"] = "failure"\n')
    contracts_path = "tests/unit/github_workflows/test_workflow_contracts.py"
    contracts = (repo / contracts_path).read_text(encoding="utf-8")
    contracts = replace_once(contracts,
        '@pytest.mark.parametrize("name", ["build-src-assets.yml", "build-repo-assets.yml", "test-runtime.yml", "docs.yml"])\n',
        '@pytest.mark.parametrize("name", ["build-src-assets.yml", "build-repo-assets.yml", "test-runtime.yml", "real-world-gauntlet.yml", "docs.yml"])\n')
    contracts = replace_once(contracts,
        '    ("test-runtime.yml", "test"),\n',
        '    ("test-runtime.yml", "test"),\n    ("real-world-gauntlet.yml", "gauntlet"),\n')
    contracts += '''

def test_gauntlet_reports_all_counts_and_keeps_setup_outside_gil_override() -> None:
    """Full CI calls the three-OS relay; settings come from the benchmark and all evidence survives failure."""
    document = workflow("real-world-gauntlet.yml")
    assert set(document["on"]) == {"workflow_call", "workflow_dispatch"}
    for event in document["on"].values():
        assert event["inputs"]["thread-counts"]["default"] == ""
    job = document["jobs"]["gauntlet"]
    assert job["strategy"]["matrix"]["os"] == ["ubuntu-24.04", "windows-2025", "macos-15-intel"]
    assert job["strategy"]["fail-fast"] == "false"
    assert "PYTHON_GIL" not in job["env"]
    assert "DI_GAUNTLET_THREADS" not in job["env"]
    assert "DI_GAUNTLET_ITERS" not in job["env"]
    steps = job["steps"]
    setup = next(step for step in steps if step.get("uses", "").startswith("actions/setup-python@"))
    assert setup["with"]["python-version"] == "3.14.7"
    assert setup["with"]["architecture"] == "x64"
    assert setup["with"]["freethreaded"] == "true"
    install = next(index for index, step in enumerate(steps) if step.get("name") == "Install identical pinned benchmark dependencies")
    provenance = next(index for index, step in enumerate(steps) if step.get("name") == "Record source and runtime provenance")
    assert install < provenance
    assert "gauntlet._gauntlet_thread_counts()" in steps[provenance]["run"]
    measured = next(step for step in steps if step.get("name") == "Run smaller real-world gauntlet")
    assert measured["env"]["PYTHON_GIL"] == "0"
    assert int(measured["timeout-minutes"]) < int(job["timeout-minutes"])
    assert "GITHUB_STEP_SUMMARY" in measured["run"]
    assert "len(counts) * rounds" in measured["run"]
    assert "assert all(verified.values())" in measured["run"]
    retained = steps[-1]
    assert retained["if"] == "always()"
    assert retained["with"]["path"] == "gauntlet-results/"
    assert retained["with"]["retention-days"] == "30"
    caller = workflow("ci.yml")["jobs"]["real-world-gauntlet"]
    assert caller["uses"] == "./.github/workflows/real-world-gauntlet.yml"
    assert "secrets" not in caller


def test_gauntlet_inline_python_parses_after_yaml_indentation() -> None:
    """Every Python step is valid executable syntax after YAML removes its indentation."""
    import ast
    for step in workflow("real-world-gauntlet.yml")["jobs"]["gauntlet"]["steps"]:
        if step.get("shell") == "python":
            ast.parse(step["run"], filename=step["name"])
'''
    guide_path = ".github/BRANCH_WORKFLOW.md"
    guide = (repo / guide_path).read_text(encoding="utf-8")
    guide = replace_once(guide, "## Supported Python versions\n",
        "## Real-world gauntlet\n\n"
        "Full CI also runs real-world-gauntlet.yml, including codex_features2 and other feature PRs\n"
        "into dev, dev-to-preprod PRs, release-fix PRs and manual full CI. Its success is required by\n"
        "CI / merge-ready. Lightweight promotions retain their existing qualification path.\n\n"
        "Edit the configuration block at the top of benchmarks/testing_other_di/test_real_world_gauntlet.py:\n"
        "iterations default to 5,000, thread counts to [3, 5, 7, 9], and rounds to 1. Run that test\n"
        "normally through pytest; no separate launcher or environment variables are needed. Every\n"
        "library/thread-count/round runs in a fresh child with PYTHON_GIL=0 and -X gil=0, and the\n"
        "measured process refuses an enabled GIL. Request/A/B workloads repeat into distinct C, D, E\n"
        "and later lanes; threads synchronize their start and are joined each workload iteration.\n"
        "This is a synchronized burst, with independent scope work rather than a producer/consumer queue.\n\n"
        "The gauntlet uses pinned Python 3.14.7 and dependencies on Ubuntu x64, Windows x64 and macOS\n"
        "Intel x64 for comparison. This fixed benchmark baseline is separate from the compatibility\n"
        "test matrix below. Setup helpers do not inherit PYTHON_GIL=0. The optional manual thread-counts\n"
        "input overrides the file's list; blank uses it unchanged.\n\n"
        "Each OS job publishes timings by thread count in its summary and retains gauntlet-results\n"
        "for 30 days: JUnit, full log, summary, outcome JSON, dependency pins/install report and source\n"
        "hashes/runtime provenance. Results must include every requested count and library, even when\n"
        "pytest exits zero. There is no speed threshold; compare matching counts within the same OS\n"
        "and account for hosted hardware variation. A short correctness run is not a performance ranking.\n\n"
        "## Supported Python versions\n")
    edits = {source_path: source, ".github/workflows/real-world-gauntlet.yml": workflow,
             ci_path: ci, policy_path: policy, policy_tests_path: policy_tests,
             qualification_path: qualification, contracts_path: contracts, guide_path: guide}
    before = {}
    for path in edits:
        target = repo / path
        before[path] = target.read_bytes() if target.exists() else None
        if before[path] is not None:
            backup = artifact / "ci_baseline" / path
            backup.parent.mkdir(parents=True, exist_ok=True)
            if backup.exists():
                raise RuntimeError(f"Existing stage-two baseline: {backup}")
            backup.write_bytes(before[path])
    for path, text in edits.items():
        target = repo / path
        current = target.read_bytes() if target.exists() else None
        if current != before[path]:
            raise RuntimeError(f"Concurrent edit: {path}")
        target.write_text(text, encoding="utf-8", newline="\n")
    (artifact / "ci_edit.py").write_bytes(Path(__file__).read_bytes())
    pins = {path: hashlib.sha256(data).hexdigest() if data is not None else None
            for path, data in before.items()}
    (artifact / "ci_pre_pins.json").write_text(json.dumps(pins, indent=2), encoding="utf-8")
    task = repo / "context_compass/tickets/tasks/2026-10-03_real_world_gauntlet_ci_task.md"
    with task.open("a", encoding="utf-8") as handle:
        handle.write("\n## CI and easy pytest configuration\n"
                     "The top-of-file block now exposes iterations, the [3,5,7,9] list and rounds.\n"
                     "Workflow full-CI wiring is implemented with the existing route, merge gate and\n"
                     "source-qualification contract. Manual input can override the list; default CI\n"
                     "uses the file configuration. Logs validate every library/count/round, with no-GIL\n"
                     "provenance and artifacts. First benchmark selection passed 33 tests before these\n"
                     "three scalar default knobs were exposed; final focused validation is next.\n")
    print(f"Applied {len(edits)} bounded CI/configuration files.")


if __name__ == "__main__":
    main()
