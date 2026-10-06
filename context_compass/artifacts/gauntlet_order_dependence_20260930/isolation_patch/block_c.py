def _per_turn_csv_enabled() -> bool:
    """
    Report whether `GAUNTLET_PER_TURN_CSV` asks for the per-turn CSV.

    Returns:
        bool: True for "1", "true", "yes" or "on", in any case and with
            surrounding spaces ignored; False otherwise or when unset.
    """
    return os.getenv("GAUNTLET_PER_TURN_CSV", "").strip().lower() in {
        "1", "true", "yes", "on"
    }


def _per_turn_csv_path() -> Path:
    """
    Resolve the per-turn CSV file written next to this module.

    Returns:
        Path: `real_world_gauntlet_per_turn<suffix>.csv`, where the suffix is
            `GAUNTLET_PER_TURN_CSV_SUFFIX` (empty by default).
    """
    suffix = os.getenv("GAUNTLET_PER_TURN_CSV_SUFFIX", "").strip()
    return Path(__file__).resolve().with_name(
        f"real_world_gauntlet_per_turn{suffix}.csv"
    )


def _per_turn_csv_header() -> list[str]:
    """
    Return the per-turn CSV columns both writers share.

    Returns:
        list[str]: Library, turn, the three timings in ms, GC incidence and the
            gen0 live count.
    """
    return [
        "DI Container",
        "Turn",
        "Total (ms)",
        "Bootstrap (ms)",
        "Threaded (ms)",
        "GC During",
        "Gen0 Live",
    ]


def _per_turn_csv_row(lib: str, row: Sequence[Any]) -> list[Any]:
    """
    Format one captured turn as a per-turn CSV row.

    Args:
        lib: Library name for the "DI Container" column.
        row: `(turn, total_ns, bootstrap_ns, threaded_ns, gc_during, gen0_live)`
            as captured in `_BenchmarkResult.per_turn_rows` (a list after a JSON
            round trip).

    Returns:
        list[Any]: The row, with the three timings in milliseconds to four
            decimals and GC incidence as "yes"/"no".
    """
    turn, total_ns, bootstrap_ns, threaded_ns, gc_during, gen0_live = row
    return [
        lib,
        turn,
        f"{total_ns / 1_000_000:.4f}",
        f"{bootstrap_ns / 1_000_000:.4f}",
        f"{threaded_ns / 1_000_000:.4f}",
        "yes" if gc_during else "no",
        gen0_live,
    ]


def _maybe_write_per_turn_csv(results: list) -> None:
    """
    Write one CSV with every single turn for all libraries, if enabled.

    Off unless GAUNTLET_PER_TURN_CSV is truthy. Produces a single file next to
    this test module, one row per iteration per library, tagged with a
    "DI Container" column so all three libraries live in the same sheet.
    Used by the runner's all-in-one mode and by `--lib` when run by hand; the
    one-process-per-library wrapper writes the same file through
    `_write_isolated_per_turn_csv`, which adds a Round column.
    """
    if not _per_turn_csv_enabled():
        return
    path = _per_turn_csv_path()
    written = 0
    with open(path, "w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(_per_turn_csv_header())
        for result in results:
            for row in result.per_turn_rows:
                writer.writerow(_per_turn_csv_row(result.lib, row))
                written += 1
    print(
        f"[per-turn csv] wrote {written} rows for {len(results)} libraries -> {path}"
    )


def _write_isolated_per_turn_csv(payloads: Sequence[dict[str, Any]]) -> None:
    """
    Write the one-process-per-library wrapper's per-turn CSV, if enabled.

    Contract:
        - Off unless `GAUNTLET_PER_TURN_CSV` is truthy. Same file as
          `_maybe_write_per_turn_csv`, overwritten.
        - One row per turn per library per round, in the order the processes ran,
          with the same columns plus a trailing "Round" column (1-based), since
          more than one round repeats every library.
        - The rows come from the payloads the per-library processes handed back
          (`_result_payload`); those processes do not write the CSV themselves.

    Args:
        payloads: One `_result_payload` dict per library process, in run order.
    """
    if not _per_turn_csv_enabled():
        return
    path = _per_turn_csv_path()
    written = 0
    with open(path, "w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow([*_per_turn_csv_header(), "Round"])
        for payload in payloads:
            for row in payload["per_turn_rows"]:
                writer.writerow([*_per_turn_csv_row(payload["lib"], row), payload["round"]])
                written += 1
    print(
        f"[per-turn csv] wrote {written} rows for {len(payloads)} library runs -> {path}"
    )
