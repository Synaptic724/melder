"""Write runs/s6_validation_index.md: one summary line per S6 run log (pytest -q tails, resumable part sets, probes).

Run from the tree root: python <this file>
"""
import pathlib
import re

RUNS = pathlib.Path("context_compass/artifacts/managed_spell_quantity_20261015/runs")
OUTCOME = re.compile(r"^(tests/\S.*?) (PASSED|FAILED|ERROR|SKIPPED|XFAIL|XPASS)\b")
SUMMARY = re.compile(r"\d+ (passed|failed)")


def tail_summary(path: pathlib.Path) -> str:
    """The last pytest summary line of a -q log, with its line number."""
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    for number in range(len(lines), 0, -1):
        if SUMMARY.search(lines[number - 1]):
            return f"- runs/{path.name}:{number}-{number}  {lines[number - 1].strip().strip('=').strip()}"
    return f"- runs/{path.name}: no pytest summary line"


def resumable(prefix: str, ids_file: str) -> str:
    """The outcome counts of one resumable part set over its id list."""
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
    return f"- {prefix}: {len(wanted)} ids ({ids_file}); outcomes {outcomes}; {len(parts)} part logs"


def main() -> None:
    """Write the index."""
    lines = ["# S6 validation index (generated from the run logs by scripts/s6_validation_index.py)", ""]
    lines.append("Story tests, red before the change and green after (pytest -q; discard, owner-stamp unit, integration):")
    for name in ("s6_red_gil0.txt", "s6_red_gil1.txt", "s6_green_gil0.txt", "s6_green_gil1.txt"):
        lines.append(tail_summary(RUNS / name))
    lines += ["", "Transfer suites (pytest -q):"]
    for name in ("s6_transfer_unit_gil0.txt", "s6_transfer_unit_gil1.txt", "s6_transfer_component_gil0.txt",
                 "s6_transfer_component_gil1.txt", "s6_transfer_integration_gil0.txt",
                 "s6_transfer_integration_gil1.txt"):
        lines.append(tail_summary(RUNS / name))
    lines += ["", "Whole tree (pytest -q):"]
    for name in ("s6_unit_aether_spellbook_gil0.txt", "s6_unit_aether_spellbook_gil1.txt"):
        lines.append(tail_summary(RUNS / name))
    lines += ["", "Whole tree, resumable shards (scripts/resumable_pytest_shard.py, pytest -v part logs; unit-rest,"
              " component and experiments id lists are S5's, S6 adds no tests there):"]
    for prefix, ids_file in (("s6_unit_rest_gil0", "s6_unit_rest_ids.txt"), ("s6_unit_rest_gil1", "s6_unit_rest_ids.txt"),
                             ("s6_component_gil0", "s6_component_ids.txt"), ("s6_component_gil1", "s6_component_ids.txt"),
                             ("s6_integration_gil0", "s6_integration_ids.txt"),
                             ("s6_integration_gil1", "s6_integration_ids.txt"),
                             ("s6_experiments_gil0", "s6_experiments_ids.txt"),
                             ("s6_experiments_gil1", "s6_experiments_ids.txt")):
        lines.append(resumable(prefix, ids_file))
    lines += ["", "Probe (probes/probe_s6_managed_transfer.py, gil1), before and after the change:"]
    for name in ("s6_probe_managed_transfer_before_gil1.txt", "s6_probe_managed_transfer_after_gil1.txt"):
        text = (RUNS / name).read_text(encoding="utf-8").splitlines()
        keep = [(n, row) for n, row in enumerate(text, 1)
                if row.startswith(("A ", "B ", "C ", "D ", "E ", "F ", "G ")) or "raised" in row
                or "owner store" in row or "object stored in" in row or "meld after notch" in row
                or "owner meld" in row]
        lines += [f"- runs/{name}:{n}-{n}  {row.strip()[:150]}" for n, row in keep]
    lines += ["", "Not run, by scope: no emission capture (S6 changes no codegen file, so no emitted plan can move) and",
              "no benchmark (S6 changes no meld path; the transfer is a cold control-plane operation)."]
    (RUNS / "s6_validation_index.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
