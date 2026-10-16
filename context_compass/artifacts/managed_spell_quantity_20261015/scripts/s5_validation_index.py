"""Write runs/s5_validation_index.md: one summary line per S5 run log (pytest -q tails, resumable part sets, benchmarks).

Run from the tree root: python <this file>
"""
import pathlib
import re

RUNS = pathlib.Path("context_compass/artifacts/managed_spell_quantity_20261015/runs")
OUTCOME = re.compile(r"^(tests/\S.*?) (PASSED|FAILED|ERROR|SKIPPED|XFAIL|XPASS)\b")
SUMMARY = re.compile(r"\d+ (passed|failed)")


def tail_summary(path: pathlib.Path) -> str:
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    for number in range(len(lines), 0, -1):
        if SUMMARY.search(lines[number - 1]):
            return f"- runs/{path.name}:{number}-{number}  {lines[number - 1].strip().strip('=').strip()}"
    return f"- runs/{path.name}: no pytest summary line"


def resumable(prefix: str, ids_file: str) -> str:
    wanted = [line.strip() for line in (RUNS / ids_file).read_text(encoding="utf-8").splitlines() if line.strip()]
    done = {}
    parts = sorted(RUNS.glob(prefix + "_part*.txt"))
    for log in parts:
        for line in log.read_text(encoding="utf-8", errors="replace").splitlines():
            match = OUTCOME.match(line)
            if match:
                done[match.group(1)] = match.group(2)
    outcomes = {}
    for test_id in wanted:
        outcome = done.get(test_id, "NOT RUN")
        outcomes[outcome] = outcomes.get(outcome, 0) + 1
    names = ", ".join(log.name for log in parts)
    return f"- {prefix}: {len(wanted)} ids ({ids_file}); outcomes {outcomes}; parts {names}"


def main() -> None:
    lines = ["# S5 validation index (generated from the run logs by scripts/s5_validation_index.py)", ""]
    lines.append("Story tests (pytest -q):")
    for name in ("s5_green_unit_gil1.txt", "s5_green_unit_gil0.txt", "s5_green_component_gil1.txt",
                 "s5_green_component_gil0.txt", "s5_green_integration_gil1.txt", "s5_green_integration_gil0.txt"):
        lines.append(tail_summary(RUNS / name))
    lines += ["", "Whole tree (pytest -q):"]
    for name in ("s5_unit_aether_spellbook_gil0.txt", "s5_unit_aether_spellbook_gil1.txt"):
        lines.append(tail_summary(RUNS / name))
    lines += ["", "Whole tree, resumable shards (scripts/resumable_pytest_shard.py, pytest -v part logs):"]
    for prefix, ids_file in (("s5_unit_rest_gil0", "s5_unit_rest_ids.txt"), ("s5_unit_rest_gil1", "s5_unit_rest_ids.txt"),
                             ("s5_component_gil0", "s5_component_ids.txt"), ("s5_component_gil1", "s5_component_ids.txt"),
                             ("s5_integration_gil0", "s5_integration_ids.txt"),
                             ("s5_integration_gil1", "s5_integration_ids.txt"),
                             ("s5_experiments_gil0", "s5_experiments_ids.txt"),
                             ("s5_experiments_gil1", "s5_experiments_ids.txt")):
        lines.append(resumable(prefix, ids_file))
    lines += ["", "Emission gate:"]
    diff = (RUNS / "s5_emission_diff.txt").read_text(encoding="utf-8").splitlines()
    lines += [f"- runs/s5_emission_diff.txt:{n}-{n}  {text}" for n, text in enumerate(diff, 1)]
    lines += ["", "Warm lease-cycle benchmark (probes/probe_s5_warm_lease_cycle.py, 200,000 cycles x 7 rounds):"]
    for name in ("s5_bench_warm_lease_cycle_gil0.txt", "s5_bench_warm_lease_cycle_gil1.txt"):
        text = (RUNS / name).read_text(encoding="utf-8").splitlines()
        lines += [f"- runs/{name}:{n}-{n}  {row}" for n, row in enumerate(text, 1)]
    (RUNS / "s5_validation_index.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
