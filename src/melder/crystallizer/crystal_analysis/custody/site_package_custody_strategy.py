"""
Custody strategy for site-package (installed distribution) modules.

Site-package classification is path-driven: configured site roots first,
then the historical `site-packages` / `dist-packages` path-text fallback.
Source is still read for fact analysis (the walk descends through installed
packages), but this class makes NO fingerprint custody claim in the first
cut - distribution name/version provenance is the future env-layer decision
(gap map section 1.3 / 3).

Lane: EPIC-2026-07-09-crystallizer-subsystem-decomposition, story S1.
"""

from pathlib import Path
from typing import Any, Optional, Tuple

from melder.crystallizer.crystal_analysis.custody.source_custody_strategy import (
    SourceCustodyStrategy,
)


class SitePackageCustodyStrategy(SourceCustodyStrategy):
    """
    Authority-class custody for installed site-package modules.

    Purpose:
        Claim modules whose backing files live under the interpreter's
        site-package roots (or match the historical path-text fallback)
        and expose their source for fact analysis without asserting any
        custody fingerprint over third-party code.

    Contract:
        - Path-driven; pathless modules never match.
        - The site-root tuple is fixed at construction.
        - `fingerprint` returns None (no custody claim in S1).

    Lifecycle / Cleanup:
        Owns the site-root tuple; cleanup deletes it (del posture).
    """

    __slots__ = ("_site_package_root_paths",)

    def __init__(self, site_package_root_paths: Tuple[Path, ...]) -> None:
        """
        Initialize the strategy with the resolved site-package roots.

        Args:
            site_package_root_paths:
                Resolved interpreter site-package roots. An empty tuple is
                legal; the path-text fallback still applies.

        Returns:
            None.
        """
        super().__init__()
        self._site_package_root_paths: Tuple[Path, ...] = tuple(
            site_package_root_paths
        )

    def cleanup(self) -> None:
        """
        Idempotently release the owned site roots.

        Returns:
            None.
        """
        if self._cleaned:
            return
        self._cleaned = True
        del self._site_package_root_paths

    @property
    def kind(self) -> str:
        """
        Return the site-package authority-class name.

        Returns:
            str: `site_package`.
        """
        return "site_package"

    @property
    def descends(self) -> bool:
        """
        Site-package modules participate fully in the dependency walk.

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
        Claim modules under site roots or the historical path-text fallback.

        Args:
            module_name:
                Canonical module name (unused; classification is path-driven).
            module_obj:
                Live module object (unused).
            module_path:
                Physical module path when available.

        Returns:
            bool:
                True when the resolved path is relative to any site root,
                or its text contains `site-packages` / `dist-packages`.
        """
        if module_path is None:
            return False
        resolved_path = self._normalize_path(module_path)
        if any(
                resolved_path.is_relative_to(root_path)
                for root_path in self._site_package_root_paths
        ):
            return True
        resolved_text = str(resolved_path)
        return "site-packages" in resolved_text or "dist-packages" in resolved_text

    def resolve_source(
            self,
            *,
            module_name: str,
            module_obj: Optional[Any],
            module_path: Optional[Path],
    ) -> Tuple[Optional[str], Optional[str]]:
        """
        Read `.py`/`.pyi` source text from the module's backing file.

        Args:
            module_name:
                Canonical module name whose source is requested.
            module_obj:
                Live module object (unused; disk is authoritative here).
            module_path:
                Physical module path when available.

        Returns:
            Tuple[Optional[str], Optional[str]]:
                `(source_text, error_text)` per the custody contract.
        """
        return self._read_source_like_file(module_name, module_path)

    def fingerprint(self, source_text: str) -> Optional[str]:
        """
        Make no custody fingerprint claim over third-party code (S1 law).

        Args:
            source_text:
                Ignored.

        Returns:
            Optional[str]: None always.
        """
        return None
