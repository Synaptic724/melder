"""
Fallback custody strategy for unresolvable and non-source module targets.

Everything no prior authority class claimed lands here: pathless modules,
targets whose origin could not be resolved, and (indirectly) any module the
walk cannot read. Per the pre-decomposition walk law, unknown targets are
recorded as honest leaves - present in the manifest so it never implies a
more complete dependency picture than the source provides, but never walked.

Lane: EPIC-2026-07-09-crystallizer-subsystem-decomposition, story S1.
"""

from pathlib import Path
from typing import Any, Optional, Tuple

from melder.crystallizer.crystal_analysis.custody.source_custody_strategy import (
    SourceCustodyStrategy,
)


class BinaryUnknownCustodyStrategy(SourceCustodyStrategy):
    """
    Terminal fallback custody for the `unknown` authority class.

    Purpose:
        Guarantee every module classifies by claiming whatever synthetic,
        user-source, and site-package custody declined, recording those
        targets as honest manifest leaves.

    Contract:
        - `matches` returns True unconditionally; this strategy MUST be
          last in the analyzer's priority order.
        - No source, no fingerprint, no descent.

    Lifecycle / Cleanup:
        Stateless beyond the Cleanable flag; cleanup is a flag flip.
    """

    __slots__ = ()

    @property
    def kind(self) -> str:
        """
        Return the fallback authority-class name.

        Returns:
            str: `unknown`.
        """
        return "unknown"

    @property
    def descends(self) -> bool:
        """
        Unknown targets are honest leaves; the walk never follows them.

        Returns:
            bool: False.
        """
        return False

    def matches(
            self,
            *,
            module_name: str,
            module_obj: Optional[Any],
            module_path: Optional[Path],
    ) -> bool:
        """
        Claim every module no prior authority class matched.

        Args:
            module_name:
                Canonical module name (unused).
            module_obj:
                Live module object (unused).
            module_path:
                Physical module path (unused).

        Returns:
            bool: True always (terminal fallback).
        """
        return True

    def resolve_source(
            self,
            *,
            module_name: str,
            module_obj: Optional[Any],
            module_path: Optional[Path],
    ) -> Tuple[Optional[str], Optional[str]]:
        """
        Expose no source for unknown targets.

        Args:
            module_name:
                Canonical module name (unused).
            module_obj:
                Live module object (unused).
            module_path:
                Physical module path (unused).

        Returns:
            Tuple[Optional[str], Optional[str]]: `(None, None)` always.
        """
        return None, None

    def fingerprint(self, source_text: str) -> Optional[str]:
        """
        Make no fingerprint claim for unknown targets.

        Args:
            source_text:
                Ignored.

        Returns:
            Optional[str]: None always.
        """
        return None

    def cleanup(self) -> None:
        """
        Idempotently mark the strategy cleaned.

        Returns:
            None.
        """
        if self._cleaned:
            return
        self._cleaned = True
