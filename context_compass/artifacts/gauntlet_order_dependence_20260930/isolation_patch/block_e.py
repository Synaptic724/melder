@pytest.mark.timeout(3600)
def test_real_world_gauntlet() -> None:
    """
    Run the shared real-world gauntlet with every library in its own process.

    Contract:
        - Uses the same standalone runner pattern as the Melder-only benchmark and
          cProfile wrappers, once per library.
        - Each library runs in a fresh interpreter (`real_world_gauntlet_gil_runner.py
          --lib`), so no library's result depends on the libraries that ran before
          it. Running all three in one process, as this test did before 2026-09-30,
          made a library 5-12% slower when it ran second or third: on free-threaded
          CPython each library's run leaves starting and joining threads slower, and
          the gauntlet starts three threads per iteration. The runner with no
          arguments still runs that layout, to reproduce earlier baselines.
        - Forces `-X gil=0` when `REAL_WORLD_GAUNTLET_FORCE_NOGIL` is true.
        - `REAL_WORLD_GAUNTLET_ROUNDS` (default 1) repeats every library that many
          times, rotating the order each round (`_isolated_order`), and then prints
          one median line per library.
        - Streams each process's stdout/stderr into pytest output as soon as that
          process finishes, for direct visibility in IDE runs, and writes the
          per-turn CSV at the end when `GAUNTLET_PER_TURN_CSV` is set.
        - Fails, naming the library and round, if a process exits non-zero.
    """
    rounds = _gauntlet_rounds()
    payloads: list[dict[str, Any]] = []
    with tempfile.TemporaryDirectory(prefix="real_world_gauntlet_") as scratch:
        for round_ix in range(rounds):
            round_number = round_ix + 1
            for lib in _isolated_order(round_ix):
                result_path = Path(scratch) / f"round{round_number}_{lib}.json"
                print(f"[gauntlet] round {round_number}/{rounds}: {lib} in its own process")
                completed = _run_isolated_library(lib, round_number, result_path)
                if completed.stdout:
                    print(completed.stdout, end="" if completed.stdout.endswith("\n") else "\n")
                if completed.stderr:
                    print(completed.stderr, end="" if completed.stderr.endswith("\n") else "\n")
                if completed.returncode != 0:
                    raise AssertionError(
                        f"Shared real-world gauntlet runner failed for {lib} in round {round_number} "
                        f"with exit code {completed.returncode}."
                    )
                payloads.append(json.loads(result_path.read_text(encoding="utf-8")))
    if rounds > 1:
        for line in _isolated_median_lines(payloads):
            print(line)
    _write_isolated_per_turn_csv(payloads)
