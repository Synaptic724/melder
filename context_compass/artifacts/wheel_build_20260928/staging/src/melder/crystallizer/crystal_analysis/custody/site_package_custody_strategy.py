"""
Custody strategy for site-package (installed distribution) modules.

Site-package classification is path-driven: configured site roots first,
then the historical `site-packages` / `dist-packages` path-text fallback.
Source is still read for fact analysis (the walk descends through installed
packages), but this class makes NO fingerprint custody claim (S1 law).
Distribution name/version provenance - formerly "the future env-layer
decision" (gap map section 1.3 / 3) - landed 2026-07-11 as the
harvest_provenance verb (finishing slice 1): identity capture via
importlib.metadata, never retention.

Lane: EPIC-2026-07-09-crystallizer-subsystem-decomposition, story S1.
"""

from pathlib import Path
from typing import Any, Dict, Optional, Tuple, ClassVar

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

    Registration:
        MELDER KERNEL - guarded. A per-analysis strategy in the analyzer's custody
        set; never user-constructed or bound.

    Subsystem Context:
        The site-package member of the `crystal_analysis` custody family (see
        `SourceCustodyStrategy`). Path-driven: it claims modules under the
        interpreter's site-package roots (or the historical site-/dist-packages
        path-text fallback), reads their source so the walk descends through
        installed packages, but makes NO fingerprint custody claim over
        third-party code. Its `harvest_provenance` verb captures distribution
        name/version identity via importlib.metadata.

    System Context:
        Third-party code sits at a different trust boundary than a user's own
        source, and this strategy encodes that: the crystallizer does not
        fingerprint-and-retain installed packages (it does not own them), but it
        DOES record their distribution identity so a restored world can diff its
        environment against the sealed one - the env-layer sibling of source
        drift. Descending through site packages for fact analysis while declining
        custody is the deliberate line between "understand what this world
        imports" and "claim responsibility for code Melder did not author."

    AGENT_ACCESS: internal

    AGENT_PURPOSE:
        access: internal. Authority-class custody for installed site-package modules. Melder
        kernel machinery: read it to understand the runtime, do not drive it directly.
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

    @property
    def claims_sha256_source_fingerprint(self) -> bool:
        """
        Mirror of `fingerprint()`: site packages make no claim (S1 law).

        Returns:
            bool: False.
        """
        return False

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

    def harvest_provenance(
            self,
            *,
            module_name: str,
            module_path: Optional[Path],
    ) -> Optional[Dict[str, object]]:
        """
        Resolve which installed distribution provides one module.

        Purpose:
            Distribution provenance (finishing slice 1, 2026-07-11):
            a restored world can say WHICH dependency versions the
            sealed world was built against. This retires the "future
            env-layer decision" note in the module docstring - the
            provenance lane is this verb.

        Contract:
            - Identity capture only, never retention: this is a
              SEPARATE verb from harvest_payload, whose seam stays
              retention-only by law.
            - Resolution walks importlib.metadata
              packages_distributions() from the module's TOP-LEVEL
              name; the version comes from the first mapped
              distribution. Multi-distribution top-levels (namespace
              packages) report every mapped name honestly.
            - Honest None when the top-level maps to no distribution
              (vendored trees, path-hacked imports) or metadata raises.

        Args:
            module_name:
                Canonical module name being walked.
            module_path:
                Physical module path (unused; resolution is
                metadata-driven, the path already classified custody).

        Returns:
            Optional[Dict[str, object]]:
                {"distribution_name": str, "distribution_version":
                Optional[str], "all_distributions": List[str],
                "top_level": str} or None when unresolvable.

        Raises:
            RuntimeError: If the strategy has been cleaned.
        """
        self.check_cleaned()
        top_level = module_name.split(".", 1)[0]
        try:
            import importlib.metadata as importlib_metadata
            mapped = importlib_metadata.packages_distributions().get(
                top_level
            )
            if not mapped:
                return None
            distribution_name = str(mapped[0])
            try:
                distribution_version: Optional[str] = (
                    importlib_metadata.version(distribution_name)
                )
            except importlib_metadata.PackageNotFoundError:
                distribution_version = None
            return {
                "distribution_name": distribution_name,
                "distribution_version": distribution_version,
                "all_distributions": [str(name) for name in mapped],
                "top_level": top_level,
            }
        except Exception:
            # Best-effort by contract: provenance must never break a
            # bind-time walk - unresolvable metadata is an honest None.
            return None
