"""Run one library through the FIXED shared harness (_run_gauntlet_benchmark) with trend windows."""
import sys
sys.path.insert(0, "/home/claude/work/melder"); sys.path.insert(0, "/home/claude/work/melder/src")
import benchmarks.testing_other_di.test_real_world_gauntlet as g
lib = sys.argv[1]
cfg = g._GauntletConfig.from_env()
result = g._run_gauntlet_benchmark(lib, cfg)
g._print_benchmark_result(result)
