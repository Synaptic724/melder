"""Demonstrate the original deadline test's false failure under delayed thread scheduling."""
import ast
import runpy
import time
from pathlib import Path
from typing import Callable


def main() -> None:
    """Run the preserved original test with a delayed worker; require its elapsed assertion to fail."""
    root = Path("C:/Users/Mark/PycharmProjects/melder_private")
    test_file = root / "tests/unit/melder/aether/conduit/creations/test_managed_spell_quantity.py"
    namespace = runpy.run_path(str(test_file))
    original_path = root / "context_compass/artifacts/queue_deadline_wakeups_20261019/original_deadline_test.py"
    tree = ast.parse(original_path.read_text(encoding="utf-8"), filename=str(original_path))
    # Keep the baseline's line numbers in the traceback while generating its callable over the real helpers.
    ast.increment_lineno(tree, 772)
    exec(compile(tree, str(original_path), "exec"), namespace)
    original_test = namespace["test_queue_deadline_is_taken_once_across_wakeups"]
    start_thread = original_test.__globals__["_run_in_thread"]

    def delayed_start(target: Callable[[], object]) -> object:
        """Defer the worker's first action by 0.6 seconds without changing the pool or its timeout."""
        def delayed_target() -> object:
            """Model a worker that is scheduled after the parent started its stopwatch."""
            time.sleep(0.6)
            return target()

        return start_thread(delayed_target)

    original_test.__globals__["_run_in_thread"] = delayed_start
    try:
        original_test()
    except AssertionError as error:
        if error.__traceback__.tb_next.tb_lineno != 793:
            raise
        print("EXPECTED FALSE FAILURE: preserved original elapsed-time assertion")
        print("Worker scheduling delayed 0.6 s; production deadline logic unchanged")
    else:
        raise AssertionError("The delayed-worker control did not expose the original timing assumption")


if __name__ == "__main__":
    main()
