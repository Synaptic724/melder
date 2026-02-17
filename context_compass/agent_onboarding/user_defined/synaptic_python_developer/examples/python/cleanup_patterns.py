"""
Purpose:
- Demonstrate idempotent cleanup with explicit nulling and lock-guarded teardown.

Notes:
- Shows logger-last ordering and SafeLogger-compatible cleanup.
- Focuses on clarity over optimization.
"""

import logging
import threading
from typing import Optional, Union

from melder.utilities.helpers.init_helpers import InitHelpers
from melder.utilities.interfaces.interfaces import IChannelLogger


class ManagedChild:
    """
    Minimal child resource with explicit cleanup.

    Contract:
      - cleanup is idempotent.
      - cleanup releases ownership and clears references.
    """

    def __init__(self, name: str) -> None:
        """
        Initialize the managed child.

        Args:
            name (str): Logical name of the child resource.
        """
        self._name: Optional[str] = name
        self._cleaned = False

    def cleanup(self) -> None:
        """
        Idempotently release child resources.

        Contract:
          - Safe to call multiple times.
          - After cleanup, internal fields are nulled.
        """
        if self._cleaned:
            return
        self._cleaned = True
        self._name = None


class ResourceOwner:
    """
    Owns resources and cleans them deterministically.

    Contract:
      - Cleanup is idempotent and ordered.
      - Logger teardown is last.
    """

    def __init__(self) -> None:
        """
        Initialize owned resources and logger.
        """
        self._child: Optional[ManagedChild] = ManagedChild("child")
        self._logger: Optional[logging.Logger] = logging.getLogger(__name__)
        self._cleaned = False

    def cleanup(self) -> None:
        """
        Tear down owned resources and null references.

        Order:
          1) child cleanup
          2) null child reference
          3) logger teardown last
        """
        if self._cleaned:
            return
        self._cleaned = True

        if self._child is not None:
            self._child.cleanup()
            self._child = None

        self._logger = None


class LockedOwner:
    """
    Owns resources and guards cleanup with a lock.

    Contract:
      - Cleanup is idempotent and lock-guarded.
      - Lock is released and nulled after teardown.
      - Logger cleanup is last.
    """

    def __init__(self, logger: Optional[Union[IChannelLogger, logging.Logger]] = None) -> None:
        """
        Initialize locked resources and a safe logger.

        Args:
            logger (Optional[Union[IChannelLogger, logging.Logger]]): Optional logger instance.
        """
        self._lock: threading.RLock = threading.RLock()
        self._logger = InitHelpers.resolve_safe_logger(logger)
        self._child: Optional[ManagedChild] = ManagedChild("locked-child")
        self._cleaned = False

    def cleanup(self) -> None:
        """
        Tear down owned resources under a lock.

        Order:
          1) lock-guarded child cleanup
          2) null child reference
          3) null lock
          4) logger cleanup last
        """
        if self._cleaned:
            return
        with self._lock:
            if self._cleaned:
                return
            self._cleaned = True
            if self._child is not None:
                self._child.cleanup()
                self._child = None

        # Null the lock after guarded teardown.
        self._lock = None

        if self._logger is not None:
            try:
                if hasattr(self._logger, "cleanup"):
                    self._logger.cleanup()
            except Exception:
                pass
            self._logger = None
