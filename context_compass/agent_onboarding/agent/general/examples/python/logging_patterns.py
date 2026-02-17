"""
Purpose:
- Demonstrate IrisLogger + SafeLogger usage (stdlib fallback only).

Notes:
- Shows structured error logging with method_name, exc_info, and metadata fields.
- Conduit-style errors include groups/system_groups/properties when helpful.
"""

import logging
from typing import Optional, Union

from melder.utilities.helpers.init_helpers import InitHelpers
from melder.utilities.interfaces.interfaces import IChannelLogger
from melder.utilities.logger.iris_logger_factory import IrisLoggerFactory
from melder.utilities.logger.safe_logger import SafeLogger


class Worker:
    """
    Performs a unit of work with explicit logging.

    Contract:
      - Prefer IrisLogger (Melder) when available.
      - Wrap all loggers with SafeLogger.
      - Stdlib logging is a fallback only.
    """

    def __init__(
        self,
        logger: Optional[Union[IChannelLogger, logging.Logger]] = None,
        logger_factory: Optional[IrisLoggerFactory] = None,
    ) -> None:
        """
        Initialize the worker.

        Args:
            logger (Optional[Union[IChannelLogger, logging.Logger]]): Optional logger override.
            logger_factory (Optional[IrisLoggerFactory]): Optional Iris logger factory.
        """
        if logger is None and logger_factory is not None:
            logger = logger_factory(self)
        self._logger: SafeLogger = InitHelpers.resolve_safe_logger(logger)

    def run(self, work_id: str) -> None:
        """
        Run a task and emit structured logs.

        Args:
            work_id (str): Identifier for the work item.
        """
        self._logger.info(f"starting work {work_id}", "run")
        try:
            self._do_work(work_id)
        except Exception as exc:
            self._logger.error(
                f"work {work_id} failed: {exc}",
                "run",
                exc_info=True,
                groups=("task", "execution"),
                system_groups=("melder", "worker"),
                properties={"work_id": work_id},
                owner=self,
                owner_id=f"worker:{work_id}",
                owner_display="Worker",
            )
            raise
        self._logger.info(f"completed work {work_id}", "run")

    def _do_work(self, work_id: str) -> None:
        """
        Internal work implementation.

        Args:
            work_id (str): Identifier for the work item.
        """
        _ = work_id

    def log_conduit_style_error(self, exc: BaseException) -> None:
        """
        Demonstrate Conduit-style error logging with extended metadata.

        Args:
            exc (BaseException): Exception to attach as exc_info.
        """
        self._logger.error(
            "Error cleaning meld",
            "_cleanup_normal_conduit",
            exc_info=exc,
            groups=("cleanup",),
            system_groups=("conduit", "melder"),
            properties={"conduit_state": "normal"},
            owner=self,
            owner_id="conduit:example",
            owner_display="Conduit",
        )
