"""Add the owner's editable iteration-count relay without changing the benchmark workloads."""

import json
from pathlib import Path


def once(text: str, old: str, new: str) -> str:
    """Refuse drift before replacing one reviewed passage."""
    if text.count(old) != 1:
        raise ValueError(f"Expected one passage: {old[:100]!r}")
    return text.replace(old, new, 1)


def main() -> None:
    """Update source, reporting, tests and the guide; preserve exact preimages in the owning task."""
    repo = Path("C:/Users/Mark/PycharmProjects/melder_private")
    artifact = repo / "context_compass/artifacts/2026-10-03_real_world_gauntlet_ci"
    source_path = "benchmarks/testing_other_di/test_real_world_gauntlet.py"
    source = (repo / source_path).read_text(encoding="utf-8")
    source = once(source, 'REAL_WORLD_GAUNTLET_ITERATIONS: int = 5_000\n',
        'REAL_WORLD_GAUNTLET_ITERATION_COUNTS: list[int] = [5_000, 10_000, 15_000, 25_000, 50_000]\n')
    source = once(source,
        '            iterations=_env_int("DI_GAUNTLET_ITERS", REAL_WORLD_GAUNTLET_ITERATIONS),\n',
        '            iterations=_env_int("DI_GAUNTLET_ITERS", _gauntlet_iteration_counts()[0]),\n')
    helper = '''def _gauntlet_iteration_counts() -> tuple[int, ...]:
    """Select the ordered iteration-count relay from the editable configuration.

    REAL_WORLD_GAUNTLET_ITERATION_COUNTS may also be supplied as comma-separated
    environment input. Without it, DI_GAUNTLET_ITERS selects one count for existing
    profiling tools; otherwise the file's list is used. Counts must be distinct
    positive integers, and a fresh child measures each count/thread/library/round.
    """
    series = os.getenv("REAL_WORLD_GAUNTLET_ITERATION_COUNTS", "").strip()
    single = os.getenv("DI_GAUNTLET_ITERS", "").strip()
    counts = ([int(value.strip()) for value in series.split(",")] if series
              else [int(single)] if single else list(REAL_WORLD_GAUNTLET_ITERATION_COUNTS))
    if not counts or any(type(value) is not int or value <= 0 for value in counts):
        raise ValueError("Gauntlet iteration counts must be a nonempty list of positive integers")
    if len(counts) != len(set(counts)):
        raise ValueError("Gauntlet iteration counts must be distinct; use rounds for repetition")
    return tuple(counts)


'''
    source = once(source, 'def _gauntlet_thread_counts() -> tuple[int, ...]:\n',
                  helper + 'def _gauntlet_thread_counts() -> tuple[int, ...]:\n')
    source = once(source,
        '        *, threads: Optional[int] = None,\n',
        '        *, threads: Optional[int] = None, iterations: Optional[int] = None,\n')
    source = once(source,
        '        child_env["DI_GAUNTLET_THREADS"] = str(threads)\n',
        '        child_env["DI_GAUNTLET_THREADS"] = str(threads)\n'
        '    if iterations is not None:\n'
        '        child_env["DI_GAUNTLET_ITERS"] = str(iterations)\n')
    source = once(source,
        "        threads: This child's count; None preserves the inherited single-run setting.\n",
        "        threads: This child's thread count; None preserves the inherited setting.\n"
        "        iterations: This child's workload iterations; None preserves the inherited setting.\n")
    source = once(source,
        '    thread_counts = dict.fromkeys(payload["threads"] for payload in payloads)\n'
        '    for threads in thread_counts:\n',
        '    settings = dict.fromkeys((payload["iterations"], payload["threads"]) for payload in payloads)\n'
        '    for iterations, threads in settings:\n')
    source = once(source,
        '                    if payload["lib"] == lib and payload["threads"] == threads]\n',
        '                    if (payload["lib"], payload["iterations"], payload["threads"]) == (lib, iterations, threads)]\n')
    source = once(source,
        '                f"[{lib}] isolated median over {len(runs)} {noun} | threads={threads} | "\n',
        '                f"[{lib}] isolated median over {len(runs)} {noun} | iterations={iterations} | threads={threads} | "\n')
    source = once(source,
        '        - One line per library/thread-count pair, in first-seen count order and\n',
        '        - One line per library/iteration-count/thread-count combination, in first-seen order and\n')
    source = once(source,
        '        writer.writerow([*_per_turn_csv_header(), "Round", "Threads"])\n',
        '        writer.writerow([*_per_turn_csv_header(), "Round", "Threads", "Iterations"])\n')
    source = once(source,
        '                writer.writerow([*_per_turn_csv_row(payload["lib"], row), payload["round"], payload["threads"]])\n',
        '                writer.writerow([*_per_turn_csv_row(payload["lib"], row), payload["round"], payload["threads"], payload["iterations"]])\n')
    source = source.replace('Round and Threads columns', 'Round, Threads and Iterations columns')
    source = once(source,
        '          more than one round repeats every library. A Threads column separates\n'
        '          rows from each configured thread count.\n',
        '          more than one round repeats every library. Threads and Iterations\n'
        '          columns distinguish every configured measurement combination.\n')
    source = once(source, '@pytest.mark.timeout(3600)\ndef test_real_world_gauntlet()',
                  '@pytest.mark.timeout(21_600)\ndef test_real_world_gauntlet()')
    source = once(source,
        '          Each count runs every library/round in a separate fresh process.\n',
        '          The editable iteration-count list defaults to 5k,10k,15k,25k,50k.\n'
        '          Every iteration-count/thread-count/library/round gets a fresh process.\n')
    start = source.index('    rounds = _gauntlet_rounds()\n', source.index('def test_real_world_gauntlet()'))
    source = source[:start] + '''    rounds = _gauntlet_rounds()
    iteration_counts = _gauntlet_iteration_counts()
    thread_counts = _gauntlet_thread_counts()
    payloads: list[dict[str, Any]] = []
    with tempfile.TemporaryDirectory(prefix="real_world_gauntlet_") as scratch:
        for iterations in iteration_counts:
            for threads in thread_counts:
                for round_ix in range(rounds):
                    round_number = round_ix + 1
                    for lib in _isolated_order(round_ix):
                        result_path = Path(scratch) / f"iters{iterations}_threads{threads}_round{round_number}_{lib}.json"
                        print(f"[gauntlet] iterations={iterations}, threads={threads}, round {round_number}/{rounds}: {lib} in its own process")
                        completed = _run_isolated_library(
                            lib, round_number, result_path, threads=threads, iterations=iterations)
                        if completed.stdout:
                            print(completed.stdout, end="" if completed.stdout.endswith("\\n") else "\\n")
                        if completed.stderr:
                            print(completed.stderr, end="" if completed.stderr.endswith("\\n") else "\\n")
                        if completed.returncode != 0:
                            raise AssertionError(
                                f"Shared real-world gauntlet runner failed for {lib}, iterations={iterations}, "
                                f"threads={threads}, round {round_number}, exit code {completed.returncode}."
                            )
                        payload = json.loads(result_path.read_text(encoding="utf-8"))
                        if (payload["lib"], payload["iterations"], payload["threads"], payload["round"], payload["gil_status"]) != (
                                lib, iterations, threads, round_number, "disabled"):
                            raise AssertionError("Gauntlet child returned mismatched iteration/thread/library/round/GIL identity")
                        payloads.append(payload)
    if rounds > 1 or len(thread_counts) > 1 or len(iteration_counts) > 1:
        for line in _isolated_median_lines(payloads):
            print(line)
    _write_isolated_per_turn_csv(payloads)
'''
    isolation_path = "benchmarks/testing_other_di/test_real_world_gauntlet_isolation.py"
    isolation = (repo / isolation_path).read_text(encoding="utf-8")
    isolation = once(isolation,
        '    assert rows[0] == [*_shared._per_turn_csv_header(), "Round", "Threads"]\n',
        '    assert rows[0] == [*_shared._per_turn_csv_header(), "Round", "Threads", "Iterations"]\n')
    isolation = once(isolation,
        '    assert rows[1] == ["dishka", "0", "1.0000", "0.0100", "0.9000", "no", "5", "1", "3"]\n',
        '    assert rows[1] == ["dishka", "0", "1.0000", "0.0100", "0.9000", "no", "5", "1", "3", "3"]\n')
    isolation = once(isolation,
        '    assert rows[2] == ["melder", "0", "2.0000", "0.0200", "1.8000", "yes", "7", "2", "3"]\n',
        '    assert rows[2] == ["melder", "0", "2.0000", "0.0200", "1.8000", "yes", "7", "2", "3", "3"]\n')
    isolation = once(isolation,
        '    assert rows[3][0] == "melder" and rows[3][-2:] == ["2", "3"]\n',
        '    assert rows[3][0] == "melder" and rows[3][-3:] == ["2", "3", "3"]\n')
    tests_path = "benchmarks/testing_other_di/test_real_world_gauntlet_threads.py"
    tests = (repo / tests_path).read_text(encoding="utf-8")
    tests = once(tests,
        '        payloads.append({"lib": "melder", "threads": threads, "total_ms": total,\n',
        '        payloads.append({"lib": "melder", "iterations": 1, "threads": threads, "total_ms": total,\n')
    tests = once(tests,
        '    monkeypatch.setattr(gauntlet, "REAL_WORLD_GAUNTLET_ITERATIONS", 4)\n',
        '    monkeypatch.delenv("REAL_WORLD_GAUNTLET_ITERATION_COUNTS", raising=False)\n'
        '    monkeypatch.setattr(gauntlet, "REAL_WORLD_GAUNTLET_ITERATION_COUNTS", [4, 8])\n')
    tests = once(tests,
        '    gauntlet._run_isolated_library("melder", 1, tmp_path / "result.json", threads=7)\n',
        '    gauntlet._run_isolated_library("melder", 1, tmp_path / "result.json", threads=7, iterations=11)\n')
    tests = once(tests, '    assert child_env["DI_GAUNTLET_THREADS"] == "7"\n',
                 '    assert child_env["DI_GAUNTLET_THREADS"] == "7"\n'
                 '    assert child_env["DI_GAUNTLET_ITERS"] == "11"\n')
    tests = once(tests,
        '    monkeypatch.setenv("DI_GAUNTLET_ITERS", "2")\n',
        '    monkeypatch.setenv("DI_GAUNTLET_ITERS", "2")\n'
        '    monkeypatch.setenv("REAL_WORLD_GAUNTLET_ITERATION_COUNTS", "1,2")\n')
    tests = once(tests,
        '        assert len(configs) == 4\n'
        '        assert [int(re.search(r"threads=(\\d+)", config)[1]) for config in configs] == [3, 5, 7, 9]\n'
        '        assert all("gil=disabled" in config and "iterations=2" in config for config in configs)\n',
        '        assert len(configs) == 8\n'
        '        observed = [(int(re.search(r"iterations=(\\d+)", config)[1]),\n'
        '                     int(re.search(r"threads=(\\d+)", config)[1])) for config in configs]\n'
        '        assert observed == [(iterations, threads) for iterations in (1, 2) for threads in (3, 5, 7, 9)]\n'
        '        assert all("gil=disabled" in config for config in configs)\n')
    tests = tests.replace('Two workload iterations make this a correctness check, not a performance',
                          'One- and two-iteration cells make this a correctness check, not a performance')
    tests = tests.replace('Normal pytest output retains all twelve results.',
                          'Normal pytest output retains all twenty-four results.')
    tests += '''

def test_iteration_relay_reads_the_editable_list_and_optional_overrides(monkeypatch: pytest.MonkeyPatch) -> None:
    """Iteration counts retain file order and support bounded legacy single-count runs."""
    monkeypatch.delenv("REAL_WORLD_GAUNTLET_ITERATION_COUNTS", raising=False)
    monkeypatch.delenv("DI_GAUNTLET_ITERS", raising=False)
    monkeypatch.setattr(gauntlet, "REAL_WORLD_GAUNTLET_ITERATION_COUNTS", [5, 2])
    assert gauntlet._gauntlet_iteration_counts() == (5, 2)
    monkeypatch.setenv("DI_GAUNTLET_ITERS", "3")
    assert gauntlet._gauntlet_iteration_counts() == (3,)
    monkeypatch.setenv("REAL_WORLD_GAUNTLET_ITERATION_COUNTS", " 2, 4 ")
    assert gauntlet._gauntlet_iteration_counts() == (2, 4)


@pytest.mark.parametrize("counts", [[], [0], [-1], [2, 2], [2.5], [True]])
def test_invalid_iteration_relays_are_refused(monkeypatch: pytest.MonkeyPatch, counts: list) -> None:
    """Refuse meaningless iteration relays before any measured process starts."""
    monkeypatch.delenv("REAL_WORLD_GAUNTLET_ITERATION_COUNTS", raising=False)
    monkeypatch.delenv("DI_GAUNTLET_ITERS", raising=False)
    monkeypatch.setattr(gauntlet, "REAL_WORLD_GAUNTLET_ITERATION_COUNTS", counts)
    with pytest.raises(ValueError):
        gauntlet._gauntlet_iteration_counts()


def test_round_summaries_do_not_mix_iteration_counts() -> None:
    """Identical thread counts still produce separate medians for different iteration budgets."""
    payloads = [{"lib": "melder", "iterations": iterations, "threads": 3, "total_ms": total,
                 "avg_ms": total, "p99_ms": total, "threaded_avg_ms": total,
                 "hot_scopes_per_s": 1, "setup_ms": 1}
                for iterations, total in ((5, 10), (10, 100), (5, 20), (10, 200))]
    lines = gauntlet._isolated_median_lines(payloads)
    assert len(lines) == 2
    assert "iterations=5" in lines[0] and "total=15.00ms" in lines[0]
    assert "iterations=10" in lines[1] and "total=150.00ms" in lines[1]
'''
    workflow_path = ".github/workflows/real-world-gauntlet.yml"
    workflow = (repo / workflow_path).read_text(encoding="utf-8")
    input_anchor = "        default: ''\n"
    if workflow.count(input_anchor) != 2:
        raise ValueError("Workflow dispatch/call input layout moved")
    workflow = workflow.replace(input_anchor, input_anchor +
        "      iteration-counts:\n"
        "        description: Optional comma-separated counts; blank uses the benchmark configuration.\n"
        "        type: string\n        required: false\n        default: ''\n")
    workflow = once(workflow,
        '      REAL_WORLD_GAUNTLET_THREAD_COUNTS: ${{ inputs.thread-counts }}\n',
        '      REAL_WORLD_GAUNTLET_THREAD_COUNTS: ${{ inputs.thread-counts }}\n'
        '      REAL_WORLD_GAUNTLET_ITERATION_COUNTS: ${{ inputs.iteration-counts }}\n')
    workflow = once(workflow, '    timeout-minutes: 60\n', '    timeout-minutes: 360\n')
    workflow = once(workflow, '        timeout-minutes: 45\n', '        timeout-minutes: 345\n')
    workflow = once(workflow,
        '          config = gauntlet._GauntletConfig.from_env()\n',
        '          iteration_counts = gauntlet._gauntlet_iteration_counts()\n')
    workflow = once(workflow,
        "              'iterations_per_library': config.iterations, 'thread_counts': list(thread_counts), 'rounds': rounds,\n",
        "              'iteration_counts': list(iteration_counts), 'thread_counts': list(thread_counts), 'rounds': rounds,\n")
    workflow = once(workflow,
        "          iterations = expected['iterations_per_library']\n",
        "          iteration_counts = expected['iteration_counts']\n")
    workflow = once(workflow,
        "          rounds = expected['rounds']\n          verified = {}\n",
        "          rounds = expected['rounds']\n"
        "          expected_pairs = sorted((iterations, threads) for iterations in iteration_counts for threads in counts for _ in range(rounds))\n"
        "          verified = {}\n")
    workflow = once(workflow,
        "                  len(configs) == len(counts) * rounds\n"
        "                  and sorted(int(re.search(r'threads=(\\d+)', config)[1]) for config in configs) == sorted(counts * rounds)\n"
        "                  and all(all(token in config.split(', ') for token in ('gil=disabled', f'iterations={iterations}')) for config in configs)\n"
        "                  and output.count(f'[{lib}] gauntlet total({iterations})=') == len(counts) * rounds\n"
        "                  and output.count(f'[{lib}] gauntlet throughput |') == len(counts) * rounds\n",
        "                  len(configs) == len(expected_pairs)\n"
        "                  and sorted((int(re.search(r'iterations=(\\d+)', config)[1]), int(re.search(r'threads=(\\d+)', config)[1])) for config in configs) == expected_pairs\n"
        "                  and all('gil=disabled' in config.split(', ') for config in configs)\n"
        "                  and all(output.count(f'[{lib}] gauntlet total({iterations})=') == len(counts) * rounds for iterations in iteration_counts)\n"
        "                  and output.count(f'[{lib}] gauntlet throughput |') == len(expected_pairs)\n")
    workflow = once(workflow,
        "                     'thread_counts': counts, 'rounds': rounds,\n",
        "                     'iteration_counts': iteration_counts, 'thread_counts': counts, 'rounds': rounds,\n")
    workflow = workflow.replace("Run smaller real-world gauntlet", "Run configured real-world gauntlet")
    contracts_path = "tests/unit/github_workflows/test_workflow_contracts.py"
    contracts = (repo / contracts_path).read_text(encoding="utf-8")
    contracts = contracts.replace("Run smaller real-world gauntlet", "Run configured real-world gauntlet")
    contracts = once(contracts,
        '        assert event["inputs"]["thread-counts"]["default"] == ""\n',
        '        assert event["inputs"]["thread-counts"]["default"] == ""\n'
        '        assert event["inputs"]["iteration-counts"]["default"] == ""\n')
    contracts = once(contracts, '    assert "len(counts) * rounds" in measured["run"]\n',
                     '    assert "expected_pairs" in measured["run"]\n')
    guide_path = ".github/BRANCH_WORKFLOW.md"
    guide = (repo / guide_path).read_text(encoding="utf-8")
    guide = once(guide,
        "iterations default to 5,000, thread counts to [3, 5, 7, 9], and rounds to 1. Run that test\n",
        "iteration counts default to [5,000, 10,000, 15,000, 25,000, 50,000], thread counts to\n"
        "[3, 5, 7, 9], and rounds to 1. Run that test\n")
    guide = guide.replace("Every\nlibrary/thread-count/round runs", "Every\nlibrary/iteration-count/thread-count/round runs")
    guide = once(guide,
        "input overrides the file's list; blank uses it unchanged.\n",
        "input overrides the file's list; iteration-counts similarly overrides iteration budgets. Blank\n"
        "uses the file unchanged. The default relay has 60 fresh child runs per round on each OS.\n"
        "The job permits six hours, with the measured step bounded at 345 minutes to leave upload time;\n"
        "the pytest wrapper has a six-hour timeout when pytest-timeout is active.\n")
    guide = guide.replace("timings by thread count", "timings by iteration and thread count")
    edits = {source_path: source, isolation_path: isolation, tests_path: tests,
             workflow_path: workflow, contracts_path: contracts, guide_path: guide}
    preimages = {path: (repo / path).read_bytes() for path in edits}
    for path, original in preimages.items():
        backup = artifact / "iteration_baseline" / path
        backup.parent.mkdir(parents=True, exist_ok=True)
        if backup.exists():
            raise RuntimeError(f"Existing iteration baseline: {path}")
        backup.write_bytes(original)
    for path, content in edits.items():
        if (repo / path).read_bytes() != preimages[path]:
            raise RuntimeError(f"Concurrent edit: {path}")
        (repo / path).write_text(content, encoding="utf-8", newline="\n")
    (artifact / "iteration_edit.py").write_bytes(Path(__file__).read_bytes())
    task_path = repo / "context_compass/tickets/tasks/2026-10-03_real_world_gauntlet_ci_task.md"
    task = task_path.read_text(encoding="utf-8-sig").replace("- Status: review", "- Status: in_progress")
    task += ("\n## Iteration relay extension\n"
             "Owner adds editable iteration counts [5000,10000,15000,25000,50000]. Every Cartesian\n"
             "iteration/thread/library/round combination gets a fresh child. Payload checks, medians,\n"
             "CSV and CI validation now include both dimensions. The larger default is 60 child runs\n"
             "per round/OS; existing execution ceilings extend to six hours, with upload headroom.\n"
             "Next: validate the expanded relay at small counts, then regenerate repository bundles.\n")
    task_path.write_text(task, encoding="utf-8")
    print(f"Applied iteration relay to {len(edits)} files.")


if __name__ == "__main__":
    main()
