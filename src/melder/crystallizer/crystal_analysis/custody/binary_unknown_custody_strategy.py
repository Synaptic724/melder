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
from typing import Any, ClassVar, Dict, Optional, Tuple

from melder.crystallizer.crystal_analysis.custody.source_custody_strategy import (
    SourceCustodyStrategy,
)
from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg


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
        - Binary identity (finishing slice 2, 2026-07-11): path-backed
          compiled leaves (.so/.pyd/.dylib) expose their file identity
          through harvest_binary_identity - a hash of the bytes, never
          a parse of them (the honesty law extended, not weakened).

    Lifecycle / Cleanup:
        Stateless beyond the Cleanable flag; cleanup is a flag flip.

    Registration:
        MELDER KERNEL - guarded. A per-analysis strategy in the analyzer's custody
        set; never user-constructed or bound.

    Subsystem Context:
        The terminal member of the `crystal_analysis` custody family (see
        `SourceCustodyStrategy`). Registered LAST in the analyzer's priority
        order, it claims every module the synthetic, user-source, and
        site-package strategies declined - pathless modules, unresolvable origins,
        and compiled leaves - recording them as honest manifest leaves.

    System Context:
        Its existence guarantees the custody decision is TOTAL: every walked
        module classifies, because the fallback claims unconditionally. Recording
        unknowns as leaves (present in the manifest, never walked) is the honesty
        law - the record never implies a more complete dependency picture than the
        source actually provides. Its binary-identity harvest extends that law
        without weakening it: a compiled .so/.pyd/.dylib leaf exposes a HASH of its
        bytes for drift detection, never a parse of them, so the record can verify
        a native dependency changed without pretending to understand its contents.
    """
    __ast_helper_access__: str = "internal"
    __agent_purpose__: str = (
        "access: internal. Terminal fallback custody for the `unknown` authority class. Melder "
        "kernel machinery: read it to understand the runtime, do not drive it directly."
    )

    __melder_internal__: ClassVar[object] = _mrg.sentinel

    # Compiled-extension suffixes whose file identity is worth capturing.
    BINARY_EXTENSIONS: ClassVar[Tuple[str, ...]] = (".so", ".pyd", ".dylib")

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

    @property
    def reads_physical_source(self) -> bool:
        """
        Unknown/binary leaves expose no readable source lane.

        Returns:
            bool: False.
        """
        return False

    @property
    def claims_sha256_source_fingerprint(self) -> bool:
        """
        Mirror of `fingerprint()`: no claim is ever made here.

        Returns:
            bool: False.
        """
        return False

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

    def harvest_binary_identity(
            self,
            *,
            module_name: str,
            module_path: Optional[Path],
    ) -> Optional[Dict[str, object]]:
        """
        Capture the file identity of one compiled-extension leaf.

        Purpose:
            Binary identity (finishing slice 2): a sealed world can
            detect that a compiled dependency's FILE changed between
            seal and restore, even though its contents stay unreadable
            (identity capture only - the honest-leaf law is extended,
            never weakened by parsing).

        Contract:
            - Only path-backed modules whose suffix is one of
              BINARY_EXTENSIONS yield a payload; everything else is
              None (pathless unknowns stay pure honest leaves).
            - The sha256 covers the raw file bytes. An unreadable file
              still yields its path identity with binary_sha256 None -
              the path is identity too, and a half-answer beats
              silence.

        Args:
            module_name:
                Canonical module name being walked (payload context).
            module_path:
                Physical module path when available.

        Returns:
            Optional[Dict[str, object]]:
                {"binary_path": str, "binary_sha256": Optional[str],
                "top_level": str} or None for non-binary/pathless
                targets.

        Raises:
            RuntimeError: If the strategy has been cleaned.
        """
        self.check_cleaned()
        if module_path is None:
            return None
        resolved_path = self._normalize_path(module_path)
        if resolved_path.suffix.lower() not in self.BINARY_EXTENSIONS:
            return None
        binary_sha256: Optional[str] = None
        try:
            import hashlib
            binary_sha256 = hashlib.sha256(
                resolved_path.read_bytes()
            ).hexdigest()
        except OSError:
            # Documented best-effort: the path IS identity; a vanished
            # or unreadable file reports itself with a None hash rather
            # than breaking the bind-time walk.
            binary_sha256 = None
        return {
            "binary_path": str(resolved_path),
            "binary_sha256": binary_sha256,
            "top_level": module_name.split(".", 1)[0],
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
