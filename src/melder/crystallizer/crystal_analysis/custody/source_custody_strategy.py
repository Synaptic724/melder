"""
Authority-class custody contract for crystal analysis.

One custody strategy exists per source authority class (synthetic module,
user source, site package, binary/unknown fallback). The analyzer resolves
the FIRST matching strategy in priority order - synthetic, user_source,
site_package, fallback - which reproduces the pre-decomposition
`SpellCrystal._classify_module_target` decision table exactly.

Lane: EPIC-2026-07-09-crystallizer-subsystem-decomposition, story S1.
"""

import hashlib
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

from melder.utilities.general_base.cleanable import Cleanable


class SourceCustodyStrategy(Cleanable, ABC):
    """
    Contract for one authority class's custody behavior during analysis.

    Purpose:
        Answer, for one module, the four custody questions the analyzer
        needs: does this module belong to my authority class, what is its
        readable source (if any), what fingerprint claim do I make over
        that source, and does the walk descend through my modules.

    Contract:
        - Strategy instances are per-analysis: constructed with the policy
          they need, used by exactly one analyzer pass, then cleaned.
        - Immutable after construction; no internal locking is required
          because instances are thread-confined to their analysis pass.
        - `matches(...)` must be deterministic for a given input triple.
        - `resolve_source(...)` never raises for content problems; failures
          are returned through the error channel for the result's
          walk-error honesty ledger.

    Threading:
        Thread-confined by contract (one analyzer pass); no locks.

    Lifecycle / Cleanup:
        `cleanup()` on subclasses deletes owned policy references and is
        idempotent.
    """
    _ast_helper_access: str = "internal"
    __agent_purpose__: str = (
        "access: internal. Contract for one authority class's custody behavior during analysis. "
        "Melder kernel machinery: read it to understand the runtime, do not drive it directly."
    )

    @property
    @abstractmethod
    def kind(self) -> str:
        """
        Return the authority-class name this strategy claims.

        Returns:
            str:
                One of `synthetic_module`, `user_source`, `site_package`,
                or `unknown`.
        """

    @property
    @abstractmethod
    def descends(self) -> bool:
        """
        Return whether the dependency walk follows this class's modules.

        Contract:
            Mirrors the pre-decomposition walk law: every classified kind
            descends except the unknown fallback, whose modules are
            recorded as honest leaves.

        Returns:
            bool: True when imports of matched modules are walked.
        """

    @abstractmethod
    def matches(
            self,
            *,
            module_name: str,
            module_obj: Optional[Any],
            module_path: Optional[Path],
    ) -> bool:
        """
        Return whether this strategy's authority class claims the module.

        Args:
            module_name:
                Canonical module name being classified.
            module_obj:
                Live module object when available.
            module_path:
                Physical module path when available.

        Returns:
            bool: True when this authority class owns the module.
        """

    @abstractmethod
    def resolve_source(
            self,
            *,
            module_name: str,
            module_obj: Optional[Any],
            module_path: Optional[Path],
    ) -> Tuple[Optional[str], Optional[str]]:
        """
        Resolve readable source text for one matched module.

        Contract:
            - Returns `(source_text, None)` on success.
            - Returns `(None, None)` when the module format simply exposes
              no source (binaries, pathless modules) - not an error.
            - Returns `(None, error_text)` when a read was expected to work
              and failed; the analyzer records the text as a walk error.

        Args:
            module_name:
                Canonical module name whose source is requested.
            module_obj:
                Live module object when available.
            module_path:
                Physical module path when available.

        Returns:
            Tuple[Optional[str], Optional[str]]:
                `(source_text, error_text)` per the contract above.
        """

    def harvest_payload(
            self,
            *,
            module_name: str,
            module_path: Optional[Path],
    ) -> Optional[Dict[str, object]]:
        """
        Return this authority class's RETENTION payload for one module.

        Contract:
            Default implementation returns None: most custody classes
            retain nothing (site packages are provenance; binaries have
            no source claim). Subclasses that own a retention lane
            override this - UserSourceCustodyStrategy returns the S2
            physical-custody payload ({source_text, source_sha256,
            module_path, is_package}) when the backing file reads.
            The SYNTHETIC lane keeps its own object-driven static
            (harvest works off the live SyntheticModule, not a path) -
            this seam is for path-backed retention only.

        Args:
            module_name:
                Canonical module name being walked.
            module_path:
                Physical module path when available.

        Returns:
            Optional[Dict[str, object]]:
                Detached retention payload, or None when this custody
                class retains nothing.
        """
        return None

    @property
    def reads_physical_source(self) -> bool:
        """
        Whether this authority class resolves source from a disk file.

        Contract:
            True for the base read law (user_source and site_package read
            `.py`/`.pyi` backing files); overridden False by strategies whose
            source lives elsewhere (synthetic module objects) or nowhere
            (binary/unknown leaves). The analyzer routes physical readers
            through the shared `PhysicalSourceCache` stat-guard lane.

        Returns:
            bool: True when `resolve_source` reads the module's backing file.
        """
        return True

    @property
    def claims_sha256_source_fingerprint(self) -> bool:
        """
        Whether this class's fingerprint claim IS the base UTF-8 SHA256 law.

        Contract:
            The 1:1 mirror of the `fingerprint()` overrides: True only when
            `fingerprint(text)` returns `sha256(text.encode("utf-8"))`. The
            analyzer's stat fast path records cached SHA256 values as
            fingerprints WITHOUT re-reading text, so a subclass that
            overrides `fingerprint()` with any other law MUST override this
            to False or the fast path would misclaim custody.

        Returns:
            bool: True when the base SHA256 fingerprint law applies.
        """
        return True

    def fingerprint(self, source_text: str) -> Optional[str]:
        """
        Return this authority class's fingerprint claim over source text.

        Contract:
            Default implementation returns the hex SHA256 of the UTF-8
            encoded source. Subclasses that make NO custody claim (for
            example site packages in the first cut) override and return
            None; the analyzer records fingerprints only when one is
            returned.

        Args:
            source_text:
                Source text to fingerprint.

        Returns:
            Optional[str]: Hex SHA256, or None when no claim is made.
        """
        return hashlib.sha256(source_text.encode("utf-8")).hexdigest()

    @staticmethod
    def _normalize_path(module_path: Path) -> Path:
        """
        Best-effort resolve a path for root-containment checks.

        Args:
            module_path:
                Physical module path to normalize.

        Returns:
            Path: Resolved path, or the input path when resolution fails.
        """
        try:
            return module_path.resolve()
        except Exception:
            return module_path

    @staticmethod
    def _read_source_like_file(
            module_name: str,
            module_path: Optional[Path],
    ) -> Tuple[Optional[str], Optional[str]]:
        """
        Read source text from a `.py`/`.pyi` backing file.

        Contract:
            - Non-source-like extensions and missing files return
              `(None, None)` (no source, not an error) - preserving the
              pre-decomposition read law.
            - Read failures return `(None, error_text)` for the honesty
              ledger instead of raising.

        Args:
            module_name:
                Canonical module name (used in error text).
            module_path:
                Physical module path when available.

        Returns:
            Tuple[Optional[str], Optional[str]]:
                `(source_text, error_text)`.
        """
        if module_path is None:
            return None, None
        if module_path.suffix.lower() not in (".py", ".pyi"):
            return None, None
        if not module_path.exists():
            return None, None
        try:
            return module_path.read_text(encoding="utf-8"), None
        except Exception as exc:
            return None, (
                "Failed to read source text for module '{0}': {1}: {2}".format(
                    module_name,
                    exc.__class__.__name__,
                    exc,
                )
            )
