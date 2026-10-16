"""Write runs/s8_validation_index.md: one summary line per S8 run log (pytest -q tails, resumable part sets, probes).

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


def probe_lines(name: str, keep: tuple) -> list:
    """The probe log's lines that start with one of `keep`, each cited with its line number."""
    text = (RUNS / name).read_text(encoding="utf-8").splitlines()
    return [f"- runs/{name}:{n}-{n}  {row.strip()[:150]}" for n, row in enumerate(text, 1) if row.lstrip().startswith(keep)]


def main() -> None:
    """Write the index."""
    lines = ["# S8 validation index (generated from the run logs by scripts/s8_validation_index.py)", ""]
    lines.append("Story tests, red on 0.2.8247 and green after the change (pytest -q; the new unit and integration files,")
    lines.append("the cache-schema test, the lowering's managed tests):")
    for name in ("s8_red_gil0.txt", "s8_green_new_gil0.txt", "s8_green_new_gil1.txt"):
        lines.append(tail_summary(RUNS / name))
    lines += ["", "Whole tree (pytest -q):"]
    for name in ("s8_unit_aether_spellbook_gil0.txt", "s8_unit_aether_spellbook_gil1.txt"):
        lines.append(tail_summary(RUNS / name))
    lines += ["", "Whole tree, resumable shards (scripts/resumable_pytest_shard.py, pytest -v part logs; id lists collected"
              " on the changed tree):"]
    for prefix, ids_file in (("s8_unit_rest_gil0", "s8_unit_rest_ids.txt"), ("s8_unit_rest_gil1", "s8_unit_rest_ids.txt"),
                             ("s8_component_gil0", "s8_component_ids.txt"), ("s8_component_gil1", "s8_component_ids.txt"),
                             ("s8_integration_gil0", "s8_integration_ids.txt"),
                             ("s8_integration_gil1", "s8_integration_ids.txt"),
                             ("s8_experiments_gil0", "s8_experiments_ids.txt"),
                             ("s8_experiments_gil1", "s8_experiments_ids.txt")):
        lines.append(resumable(prefix, ids_file))
    lines += ["", "ManagedSpellLease as built (pytest -q: its unit file, the release registry, the managed component and two"
              " integration files):"]
    for name in ("s8_lease_suites_gil0.txt", "s8_lease_suites_gil1.txt"):
        lines.append(tail_summary(RUNS / name))
    lines += ["", "Probes:"]
    lines += probe_lines("s8_owner_questions_after_gil0.txt", ("unique ", "unique_per_conduit ", "many ", "managed_spell_quantity "))
    for name in ("s8_managed_spell_lease_gil0.txt", "s8_managed_spell_lease_gil1.txt"):
        lines += probe_lines(name, ("PASS", "FAIL", "8 of"))
    lines += probe_lines("s8_existing_object_teardown_gil0.txt", ("notch=",))
    lines += ["", "Not run, by scope: no emission capture - the lowering's change is the text of a runtime helper the plans",
              "call (`_raise_missing_managed_pool`, bound into a plan's namespace), not code they contain, and no other",
              "emitting code changed; no benchmark - the change is on conjure's cold path. Hosted CI and coverage: the",
              "owner's."]
    (RUNS / "s8_validation_index.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
