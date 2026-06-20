import sys
from pathlib import Path


def _ensure_repo_paths() -> None:
    """
    Ensure the repo root and src tree are importable for direct runner use.
    """
    current_dir = Path(__file__).resolve().parent
    repo_root = current_dir.parents[1]
    src_dir = repo_root / "src"
    for path in (repo_root, src_dir):
        path_as_str = str(path)
        if path_as_str not in sys.path:
            sys.path.insert(0, path_as_str)


_ensure_repo_paths()

import benchmarks.testing_other_di.test_real_world_gauntlet as gauntlet


def main() -> int:
    """
    Run the shared gauntlet once for each supported library.
    """
    cfg = gauntlet._GauntletConfig.from_env()
    results = []
    for lib in ("dependency-injector", "dishka", "melder"):
        result = gauntlet._run_gauntlet_benchmark(lib, cfg)
        gauntlet._print_benchmark_result(result)
        results.append(result)
    gauntlet._maybe_write_per_turn_csv(results)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
