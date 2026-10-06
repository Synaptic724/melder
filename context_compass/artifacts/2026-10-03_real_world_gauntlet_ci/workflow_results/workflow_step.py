import json, os, re, subprocess, sys, time
from pathlib import Path
report = Path('context_compass/artifacts/2026-10-03_real_world_gauntlet_ci/workflow_results')
command = [sys.executable, '-X', 'gil=0', '-m', 'pytest', '-s', '-v',
           '-o', 'addopts=', '-o', 'markers=timeout: timeout metadata (bounded by Actions)',
           '--junitxml=context_compass/artifacts/2026-10-03_real_world_gauntlet_ci/workflow_results/junit.xml',
           'benchmarks/testing_other_di/test_real_world_gauntlet.py::test_real_world_gauntlet']
start = time.monotonic()
(report / 'command.json').write_text(json.dumps(command, indent=2), encoding='utf-8')
with (report / 'benchmark.log').open('w', encoding='utf-8') as log:
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                               text=True, encoding='utf-8', errors='replace')
    for line in process.stdout:
        print(line, end='', flush=True)
        log.write(line)
        log.flush()
    status = process.wait()
output = (report / 'benchmark.log').read_text(encoding='utf-8')
expected = json.loads((report / 'environment.json').read_text(encoding='utf-8'))
iterations = expected['iterations_per_library']
counts = expected['thread_counts']
rounds = expected['rounds']
verified = {}
for lib in ('dependency-injector', 'dishka', 'melder'):
    configs = re.findall(r'\[' + re.escape(lib) + r'\] gauntlet config: ([^\n]+)', output)
    verified[lib] = (
        len(configs) == len(counts) * rounds
        and sorted(int(re.search(r'threads=(\d+)', config)[1]) for config in configs) == sorted(counts * rounds)
        and all(all(token in config.split(', ') for token in ('gil=disabled', f'iterations={iterations}')) for config in configs)
        and output.count(f'[{lib}] gauntlet total({iterations})=') == len(counts) * rounds
        and output.count(f'[{lib}] gauntlet throughput |') == len(counts) * rounds
    )
outcome = {'exit_code': status, 'verified_libraries': verified,
           'validation_passed': status == 0 and all(verified.values()),
           'thread_counts': counts, 'rounds': rounds,
           'elapsed_seconds': time.monotonic() - start, 'command': command}
(report / 'outcome.json').write_text(json.dumps(outcome, indent=2), encoding='utf-8')
summary = '\n'.join(line for line in output.splitlines() if any(token in line for token in (
    '] gauntlet config:', '] gauntlet total(', '] gauntlet throughput', '] isolated median', '] lane=')))
(report / 'summary.txt').write_text(summary + '\n', encoding='utf-8')
with open(os.environ['GITHUB_STEP_SUMMARY'], 'a', encoding='utf-8') as handle:
    handle.write('## Real-world gauntlet by thread count\n\n```text\n' + summary + '\n```\n')
    handle.write('\nValidation: ' + json.dumps(outcome) + '\n')
    handle.write('\nCompare matching thread counts within each OS. Hosted hardware and branch-native process isolation/workloads may differ; one round is not a controlled pure-OS comparison. See the artifact for raw logs and provenance.\n')
if status:
    raise SystemExit(status)
assert all(verified.values()), 'Missing results or wrong settings for one or more libraries: ' + repr(verified)
