"""
Custody strategy for user-source (file-backed, policy-rooted) modules.

User-source classification is policy-driven: a module belongs here when its
resolved path sits under one of the configured user source roots. This is
also where physical custody gains its S1 upgrade - a bind-time module-text
SHA256 fingerprint, making on-disk drift detectable at load time instead of
silently restoring against changed code.

Lane: EPIC-2026-07-09-crystallizer-subsystem-decomposition, story S1.
"""

from pathlib import Path
from typing import Any, Dict, Optional, Tuple

from melder.crystallizer.crystal_analysis.custody.source_custody_strategy import (
    SourceCustodyStrategy,
)


class UserSourceCustodyStrategy(SourceCustodyStrategy):
    """
    Authority-class custody for policy-rooted user source modules.

    Purpose:
        Claim modules whose backing files live under the configured user
        source roots, expose their `.py`/`.pyi` text for fact analysis,
        and stamp the SHA256 fingerprint that turns silent on-disk drift
        into a detectable preflight finding.

    Contract:
        - Path-driven: a module with no path can never match.
        - The root set is fixed at construction (analysis policy input)
          and never mutated.
        - Fingerprints are hex SHA256 over the UTF-8 source (ABC default).

    Lifecycle / Cleanup:
        Owns the user-root tuple; cleanup deletes it (del posture).
    """

    __slots__ = ("_user_root_paths",)

    def __init__(self, user_root_paths: Tuple[Path, ...]) -> None:
        """
        Initialize the strategy with the classification policy roots.

        Args:
            user_root_paths:
                Resolved root paths that define `user_source` authority.
                An empty tuple is legal and simply never matches.

        Returns:
            None.
        """
        super().__init__()
        self._user_root_paths: Tuple[Path, ...] = tuple(user_root_paths)

    def cleanup(self) -> None:
        """
        Idempotently release the owned policy roots.

        Returns:
            None.
        """
        if self._cleaned:
            return
        self._cleaned = True
        del self._user_root_paths

    @property
    def kind(self) -> str:
        """
        Return the user-source authority-class name.

        Returns:
            str: `user_source`.
        """
        return "user_source"

    @property
    def descends(self) -> bool:
        """
        User-source modules participate fully in the dependency walk.

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
        Claim modules whose resolved path sits under a user source root.

        Args:
            module_name:
                Canonical module name (unused; classification is path-driven).
            module_obj:
                Live module object (unused).
            module_path:
                Physical module path when available.

        Returns:
            bool:
                True when the resolved path is relative to any configured
                user root; False for pathless modules.
        """
        if module_path is None:
            return False
        resolved_path = self._normalize_path(module_path)
        return any(
            resolved_path.is_relative_to(root_path)
            for root_path in self._user_root_paths
        )

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

    def harvest_payload(
            self,
            *,
            module_name: str,
            module_path: Optional[Path],
    ) -> Optional[Dict[str, object]]:
        """
        Capture one user module's rebuildable truth (S2 physical custody).

        Contract:
            - Returns None when the backing file exposes no readable
              source (pathless, binary, or read failure) - the walk-error
              honesty channel already carries the read failure from the
              facts pass; retention never invents text.
            - Plain detached values only; payload keys mirror the M3
              synthetic lane (source_text/source_sha256) plus the
              user-side identity (module_path, is_package).
            - The sha256 is computed from the SAME text that is retained,
              so preflight can compare it against the bind-time
              physical_module_fingerprints row for tamper detection.

        Args:
            module_name:
                Canonical user module name being walked.
            module_path:
                Physical module path when available.

        Returns:
            Optional[Dict[str, object]]:
                {source_text, source_sha256, module_path, is_package},
                or None when nothing readable backs the module.
        """
        source_text, _error_text = self._read_source_like_file(
            module_name, module_path
        )
        if source_text is None or module_path is None:
            return None
        return {
            "source_text": source_text,
            "source_sha256": self.fingerprint(source_text),
            "module_path": str(module_path),
            "is_package": module_path.name == "__init__.py",
        }
