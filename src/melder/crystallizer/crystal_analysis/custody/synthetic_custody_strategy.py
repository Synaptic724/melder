"""
Custody strategy for synthetic (crystallizer-born) modules.

Synthetic modules have no files - their source IS the record. This strategy
claims them by protocol identity, resolves source through the protocol
surface, and harvests the full rebuildable payload (loader chain M3) the
restore engine needs to reconstruct the module world in a fresh process.

Lane: EPIC-2026-07-09-crystallizer-subsystem-decomposition, story S1.
"""

from pathlib import Path
from typing import Any, Dict, Optional, Tuple

from melder.crystallizer.synthetic_module import SyntheticModule
from melder.crystallizer.crystal_analysis.custody.source_custody_strategy import (
    SourceCustodyStrategy,
)


class SyntheticCustodyStrategy(SourceCustodyStrategy):
    """
    Authority-class custody for `SyntheticModule` objects.

    Purpose:
        Claim explicitly synthetic modules first (their authority is
        explicit, so they win over every path-driven classification),
        expose their protocol source, and harvest the rebuildable custody
        payload that rides the analysis result.

    Contract:
        - `matches` is a strict protocol identity check.
        - `resolve_source` never touches disk; the protocol surface is the
          only source of truth.
        - `harvest_payload` captures everything SyntheticModule's
          constructor needs at restore: source_text, source_sha256,
          binding_signature, spell_crystal_id, parent_name, is_package.

    Lifecycle / Cleanup:
        Stateless beyond the Cleanable flag; cleanup is a flag flip.
    """

    __slots__ = ()

    @property
    def kind(self) -> str:
        """
        Return the synthetic authority-class name.

        Returns:
            str: `synthetic_module`.
        """
        return "synthetic_module"

    @property
    def descends(self) -> bool:
        """
        Synthetic modules participate fully in the dependency walk.

        Returns:
            bool: True.
        """
        return True

    def matches(
            self,
            *,
            module_name: str,
            module_obj: Optional[Any],
            module_path: Optional[Path],
    ) -> bool:
        """
        Claim modules that satisfy the synthetic-module protocol.

        Args:
            module_name:
                Canonical module name (unused; identity is object-driven).
            module_obj:
                Live module object when available.
            module_path:
                Physical module path (unused for synthetic identity).

        Returns:
            bool: True when `module_obj` is a `SyntheticModule`.
        """
        if module_obj is None:
            return False
        return isinstance(module_obj, SyntheticModule)

    def resolve_source(
            self,
            *,
            module_name: str,
            module_obj: Optional[Any],
            module_path: Optional[Path],
    ) -> Tuple[Optional[str], Optional[str]]:
        """
        Resolve source through the synthetic-module protocol surface.

        Args:
            module_name:
                Canonical module name whose source is requested.
            module_obj:
                Live `SyntheticModule` object.
            module_path:
                Ignored; synthetic source never comes from disk.

        Returns:
            Tuple[Optional[str], Optional[str]]:
                `(source_text, None)` when the protocol exposes text,
                otherwise `(None, None)`.
        """
        if not isinstance(module_obj, SyntheticModule):
            return None, None
        source_text = module_obj.source_text
        if isinstance(source_text, str):
            return source_text, None
        return None, None

    def fingerprint(self, source_text: str) -> Optional[str]:
        """
        Make no separate fingerprint claim for synthetic modules.

        Contract:
            Synthetic custody rides `harvest_payload` (which carries the
            module's own `source_sha256`); recording a second fingerprint
            channel would duplicate that truth.

        Args:
            source_text:
                Ignored.

        Returns:
            Optional[str]: None always.
        """
        return None

    @staticmethod
    def harvest_payload(module_obj: Any) -> Optional[Dict[str, object]]:
        """
        Capture one synthetic module's rebuildable truth (loader chain M3).

        Contract:
            - Returns None for non-synthetic objects (caller may probe).
            - Plain values only; the payload is detached from the module.

        Args:
            module_obj:
                Live module object being walked.

        Returns:
            Optional[Dict[str, object]]:
                The rebuild payload, or None when not synthetic.
        """
        if not isinstance(module_obj, SyntheticModule):
            return None
        return {
            "source_text": module_obj.source_text,
            "source_sha256": module_obj.source_sha256,
            "binding_signature": module_obj.binding_signature,
            "spell_crystal_id": module_obj.spell_crystal_id,
            "parent_name": module_obj.parent_name,
            "is_package": module_obj.is_package,
        }

    def cleanup(self) -> None:
        """
        Idempotently mark the strategy cleaned.

        Returns:
            None.
        """
        if self._cleaned:
            return
        self._cleaned = True
