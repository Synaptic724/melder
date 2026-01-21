

"""
melder
Lightweight dependency injection system designed for high-performance modular Python systems like ThreadFactory.
"""

import sys
import warnings

from src.melder.__version__ import __version__ as base_version
from src.melder.__author__ import CREATOR as __author__
from src.melder.__license__ import __license__
from src.melder.__description__ import __description__
from melder.__melder_registration_guard__ import MelderRegistrationGuard
# Eagerly instantiate the registration guard at package import time (internal use).
__melder_registration_guard__ = MelderRegistrationGuard()

DEBUG_MODE = True
# 🔧 Append "-dev" in DEBUG_MODE without mutating original
__version__ = base_version + "-dev" if DEBUG_MODE else base_version


# ✅ Soft warning if not optimized Python version
if sys.version_info < (3, 13, 0):
    warnings.warn(
        (
            "melder is optimized for Python 3.13+ (no-GIL). "
            f"You are running Python {sys.version_info.major}."
            f"{sys.version_info.minor}.{sys.version_info.micro}. "
            "Functionality will still work on older Pythons, but performance may be significantly degraded."
        ),
        category=UserWarning,
        stacklevel=2,
    )

def _detect_nogil_mode() -> None:
    """
    Warn if we're not on a Python 3.13+ no-GIL build.
    """
    try:
        GIL_ENABLED = sys._is_gil_enabled()
    except AttributeError:
        GIL_ENABLED = True  # Assume legacy build with GIL

    if GIL_ENABLED:
        warnings.warn(
            "⚠️ Python 3.13+ detected, but running in GIL-enabled mode.\n"
            "melder is optimized for Python built with --disable-gil (PEP 703).\n"
            "Performance may be degraded.",
            UserWarning
        )

_detect_nogil_mode()



__all__ = [
    "__version__",
    "__author__",
    "__license__",
    "__description__",
]

