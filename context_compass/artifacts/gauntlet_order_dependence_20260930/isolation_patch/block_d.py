def _result_payload(result: _BenchmarkResult, round_number: int) -> dict[str, Any]:
    """
    Reduce one library's result to the JSON payload a per-library process hands back.

    Contract:
        - Values only (str, int, float, bool and lists of them), so `json.dumps`
          accepts it and the parent needs nothing else from the child process.
        - Carries what the wrapper summarizes across rounds - setup, the loop total
          and per-iteration statistics, the threaded and bootstrap averages,
          throughput - and the per-turn rows, which stay empty unless
          `GAUNTLET_PER_TURN_CSV` is set.

    Args:
        result: The library's `_BenchmarkResult`.
        round_number: 1-based round this run belongs to.

    Returns:
        dict[str, Any]: The payload; times in milliseconds.
    """
    return {
        "lib": result.lib,
        "round": round_number,
        "iterations": result.cfg.iterations,
        "threads": result.cfg.threads,
        "gil_status": result.gil_status,
        "setup_ms": _ms(result.setup_ns),
        "cleanup_ms": _ms(result.cleanup_ns),
        "total_ms": _ms(result.iteration_summary.total_ns),
        "avg_ms": _ms(result.iteration_summary.avg_ns),
        "median_ms": _ms(result.iteration_summary.median_ns),
        "p95_ms": _ms(result.iteration_summary.p95_ns),
        "p99_ms": _ms(result.iteration_summary.p99_ns),
        "max_ms": _ms(result.iteration_summary.max_ns),
        "threaded_avg_ms": _ms(result.threaded_summary.avg_ns),
        "bootstrap_avg_ms": _ms(result.bootstrap_summary.avg_ns),
        "hot_scopes_per_s": result.hot_scope_cycles_per_s,
        "per_turn_rows": [list(row) for row in result.per_turn_rows],
    }


def _isolated_median_lines(payloads: Sequence[dict[str, Any]]) -> list[str]:
    """
    Summarize each library across the wrapper's rounds as one median line.

    Contract:
        - One line per library that has payloads, in `_gauntlet_libraries()` order;
          a library with none is skipped.
        - Every value is the median over that library's runs; the loop total also
          shows its min and max, so run-to-run spread stays visible.

    Args:
        payloads: `_result_payload` dicts from the library processes.

    Returns:
        list[str]: The lines to print.
    """
    lines: list[str] = []
    for lib in _gauntlet_libraries():
        runs = [payload for payload in payloads if payload["lib"] == lib]
        if not runs:
            continue
        totals = [run["total_ms"] for run in runs]
        noun = "round" if len(runs) == 1 else "rounds"
        lines.append(
            f"[{lib}] isolated median over {len(runs)} {noun} | "
            f"total={statistics.median(totals):.2f}ms (min={min(totals):.2f}, max={max(totals):.2f}) | "
            f"avg={statistics.median([run['avg_ms'] for run in runs]):.3f}ms | "
            f"p99={statistics.median([run['p99_ms'] for run in runs]):.3f}ms | "
            f"threaded avg={statistics.median([run['threaded_avg_ms'] for run in runs]):.3f}ms | "
            f"hot_scopes/s={statistics.median([run['hot_scopes_per_s'] for run in runs]):,.0f} | "
            f"setup={statistics.median([run['setup_ms'] for run in runs]):.3f}ms"
        )
    return lines


def _run_isolated_library(
        lib: str,
        round_number: int,
        result_path: Path,
) -> subprocess.CompletedProcess[str]:
    """
    Run one library of the shared gauntlet in a fresh interpreter process.

    Contract:
        - Starts `real_world_gauntlet_gil_runner.py --lib <lib>` with this
          interpreter, adding `-X gil=0` when `REAL_WORLD_GAUNTLET_FORCE_NOGIL` is
          true, from the repository root and with a copy of this environment.
        - The child loads and runs only that library, prints its result and writes
          its `_result_payload` JSON to `result_path`.
        - Never raises for a failing child: the caller checks `returncode`.

    Args:
        lib: A name from `_gauntlet_libraries()`.
        round_number: 1-based round, recorded in the payload.
        result_path: Where the child writes its JSON payload.

    Returns:
        subprocess.CompletedProcess[str]: The finished child, with stdout and stderr
            captured as text.
    """
    command = [sys.executable]
    if REAL_WORLD_GAUNTLET_FORCE_NOGIL:
        command.extend(["-X", "gil=0"])
    command.extend([
        str(_runner_path()),
        "--lib",
        lib,
        "--round",
        str(round_number),
        "--result-json",
        str(result_path),
    ])
    return subprocess.run(
        command,
        cwd=str(_repo_root()),
        env=os.environ.copy(),
        capture_output=True,
        text=True,
        check=False,
    )


