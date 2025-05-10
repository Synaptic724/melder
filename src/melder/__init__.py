"""
melder
Lightweight dependency injection system designed for high-performance modular Python systems like ThreadFactory.
"""

import sys
import warnings

from melder.__version__ import __version__ as base_version
from melder.__author__ import CREATOR as __author__
from melder.__license__ import __license__
from melder.__description__ import __description__

DEBUG_MODE = True

# 🚫 Exit if Python version is less than 3.13 (hard fail)
if sys.version_info < (3, 13):
    sys.exit("melder requires Python 3.13 or higher.")

# ✅ Soft warning if not optimized Python version
if sys.version_info < (3, 13):
    warnings.warn(
        f"melder is optimized for Python 3.13+ (no-GIL). "
        f"You are running Python {sys.version_info.major}.{sys.version_info.minor}.",
        UserWarning
    )

# 🔧 Append "-dev" in DEBUG_MODE without mutating original
__version__ = base_version + "-dev" if DEBUG_MODE else base_version

__all__ = [
    "__version__",
    "__author__",
    "__license__",
    "__description__"
]

def _detect_nogil_mode() -> None:
    """
    Warn if we're not on a Python 3.13+ no-GIL build.
    This is a heuristic: there's no guaranteed official way to detect no-GIL.
    """
    if sys.version_info < (3, 13):
        warnings.warn(
            "melder is designed for Python 3.13+. "
            f"You are running Python {sys.version_info.major}.{sys.version_info.minor}.",
            UserWarning
        )
        return
    try:
        GIL_ENABLED = sys._is_gil_enabled()
    except AttributeError:
        GIL_ENABLED = True

    if GIL_ENABLED:
        warnings.warn(
            "You are using a Python version that allows no-GIL mode, "
            "but are not running in no-GIL mode. "
            "This package is designed for optimal performance with no-GIL.",
            UserWarning
        )

_detect_nogil_mode()
