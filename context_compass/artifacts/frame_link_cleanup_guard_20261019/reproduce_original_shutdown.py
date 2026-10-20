"""Reproduce the old fixture's stranded worker in a bounded, parent-owned local child process."""
import ast
from pathlib import Path
import subprocess
import sys
import threading
import time
import traceback


def run_child() -> None:
    """Delay the second cleanup worker and run the preserved original test, without changing production."""
    root = Path('C:/Users/Mark/PycharmProjects/melder_private')
    original = root / 'context_compass/artifacts/frame_link_cleanup_guard_20261019/before/test_frame_link_runtime_contracts.py'
    tree = ast.parse(original.read_text(encoding='utf-8'), filename=str(original))
    test = next(node for node in tree.body if isinstance(node, ast.FunctionDef)
                and node.name == 'test_frame_link_cleanup_rechecks_cleaned_inside_lock')
    delay = ast.parse('def _delayed_cleanup():\n    time.sleep(1.5)\n    link.cleanup()\n').body[0]
    first_index = next(index for index, node in enumerate(test.body)
                       if isinstance(node, ast.Assign) and isinstance(node.targets[0], ast.Name)
                       and node.targets[0].id == 'first')
    test.body.insert(first_index, delay)
    second = next(node for node in test.body if isinstance(node, ast.Assign)
                  and isinstance(node.targets[0], ast.Name) and node.targets[0].id == 'second')
    assert isinstance(second.value, ast.Call)
    second.value.keywords[0].value = ast.Name(id='_delayed_cleanup', ctx=ast.Load())
    ast.fix_missing_locations(tree)
    namespace = {'time': time, '__name__': '__original_fixture_control__'}
    exec(compile(tree, str(original), 'exec'), namespace)
    try:
        namespace[test.name]()
    except AssertionError:
        traceback.print_exc()
        assert any(worker is not threading.current_thread() and not worker.daemon
                   and worker.is_alive() for worker in threading.enumerate())
        print('ORIGINAL_FIXTURE_ASSERTION_AND_LIVE_NONDAEMON_WORKER', flush=True)
    else:
        raise AssertionError('Original fixture did not expose the delayed-worker failure')


def main() -> None:
    """Require the original failure and shutdown hang, then ensure the timed-out child is killed and joined."""
    if len(sys.argv) > 1:
        assert sys.argv[1] == '--child'
        run_child()
        return
    evidence = Path('C:/Users/Mark/PycharmProjects/melder_private/context_compass/artifacts/frame_link_cleanup_guard_20261019')
    try:
        outcome = subprocess.run(
            [sys.executable, '-B', '-X', 'gil=0', str(Path(__file__)), '--child'],
            capture_output=True, timeout=10.0, check=False,
        )
    except subprocess.TimeoutExpired as error:
        stdout = (error.stdout or b'').decode('utf-8', errors='replace')
        stderr = (error.stderr or b'').decode('utf-8', errors='replace')
        (evidence / 'original_shutdown_child.stdout.log').write_text(stdout, encoding='utf-8')
        (evidence / 'original_shutdown_child.stderr.log').write_text(stderr, encoding='utf-8')
        assert 'ORIGINAL_FIXTURE_ASSERTION_AND_LIVE_NONDAEMON_WORKER' in stdout
        assert 'AssertionError' in stderr
        print('EXPECTED REPRODUCTION: old fixture failed and stranded a non-daemon cleanup worker')
        print('Parent timeout killed and joined its own child; no test worker remains')
    else:
        raise AssertionError(f'Expected shutdown hang; child exited {outcome.returncode}')


if __name__ == '__main__':
    main()
