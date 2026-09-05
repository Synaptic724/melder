"""Execute the supported pytest tiers in a verified free-threaded Python process."""

import argparse
import pathlib
import sys
import sysconfig
from typing import Optional, Sequence


def require_free_threading(version: Sequence[int], supported: object, gil_enabled: bool) -> None:
    """Raise RuntimeError unless Python 3.14+ supports free threading and the GIL is off."""
    if tuple(version[:2]) < (3, 14) or supported != 1 or gil_enabled:
        raise RuntimeError(
            "Melder runtime CI requires Python 3.14+ free-threaded with the GIL disabled. "
            "Select Python 3.14t and set PYTHON_GIL=0 for the test process."
        )


def main(argv: Optional[Sequence[str]] = None) -> int:
    """Run the three supported tiers and write JUnit evidence even when pytest fails.

    Verify the actual process before and after pytest, rather than checking a
    separate interpreter invocation. The workflow explicitly fixes PYTHON_GIL=0.
    The return value is pytest's exit code; unsupported runtime state raises.
    """
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", type=pathlib.Path, required=True)
    args = parser.parse_args(argv)
    import pytest

    require_free_threading(sys.version_info, sysconfig.get_config_var("Py_GIL_DISABLED"),
                           sys._is_gil_enabled())
    args.report.parent.mkdir(parents=True, exist_ok=True)
    result = pytest.main([
        "-q", "tests/unit", "tests/component", "tests/integration",
        f"--junitxml={args.report}",
    ])
    require_free_threading(sys.version_info, sysconfig.get_config_var("Py_GIL_DISABLED"),
                           sys._is_gil_enabled())
    return int(result)


if __name__ == "__main__":
    raise SystemExit(main())
