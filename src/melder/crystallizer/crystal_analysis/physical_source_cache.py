"""
Process-wide stat-guarded physical-source fingerprint cache.

Purpose:
    Kill the analysis IO storm: bind-time module-world walks, the source_drift
    preflight, and the impact drift view all need "the sha256 of this file's
    current text" far more often than files actually change. This cache serves
    that answer from a (mtime_ns, size) stat guard so unchanged worlds cost a
    stat call instead of a read + hash per module per pass.

Contract:
    - Truth law: a served fingerprint always equals the sha256 of content that
      was observed together with the guarded (mtime_ns, size) stat pair. Any
      observable file change misses the guard and forces a fresh read + hash.
    - Accepted residual: an edit that preserves BOTH mtime_ns and byte size is
      undetectable by the guard - the same acceptance every build system makes
      for stat-based freshness; callers needing absolute proof re-hash.
    - No source text is retained; entries hold two ints and one 64-char hex
      digest per path, LRU-bounded.

Threading:
    Class-level RLock serializes entry reads/writes (mirrors the
    CrystalAnalyzer syntax-fact memo posture); stat and file reads run outside
    the lock. Safe under parallel restore workers.

Lane: crystallizer_analysis_io_cache_2026_07_19.
"""

import hashlib
import threading
from collections import OrderedDict
from pathlib import Path
from typing import Dict, Optional, Tuple, ClassVar
from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg


class PhysicalSourceCache:
    """
    Shared stat-guarded fingerprint cache over physical source files.

    Purpose:
        One process-wide answer for "what is this source file's sha256 right
        now" that only pays disk reads when the file's stat identity changed.

    Contract:
        - `fingerprint_if_unchanged` never reads file content.
        - `read_text_and_fingerprint` is the ONE read law for physical source
          (mirrors the custody read law byte-for-byte) and feeds the cache.
        - Entries are LRU-evicted beyond the class capacity; eviction releases
          only tuples/strings.

    Threading / Concurrency:
        All entry-map access is serialized by one class RLock; IO runs outside
        the lock so a slow disk never convoys unrelated lookups.

    Lifecycle / Cleanup:
        Class-hosted state (like the analyzer syntax memo); no instance
        lifecycle. `_clear_for_tests` resets entries and counters.
    """
    _ast_helper_access: str = "internal"
    __agent_purpose__: str = (
        "access: internal. Shared stat-guarded fingerprint cache over physical source files. "
        "Melder kernel machinery: read it to understand the runtime, do not drive it directly."
    )

    __melder_internal__: ClassVar[object] = _mrg.sentinel

    _SCHEMA_VERSION = 1
    _MAX_ENTRIES = 4096
    _lock = threading.RLock()
    _entries: OrderedDict[str, Tuple[int, int, str]] = OrderedDict()
    _hits = 0
    _misses = 0

    @classmethod
    def fingerprint_if_unchanged(cls, module_path: Path) -> Optional[str]:
        """
        Serve a cached sha256 when the file's stat identity is unchanged.

        Contract:
            - Stats the file OUTSIDE the lock; compares (mtime_ns, size) to
              the cached guard under the lock.
            - Hit: LRU-bumps the entry and returns its sha256 - no read.
            - Miss, changed guard, or stat failure: returns None (the caller
              falls to the cold read lane).

        Args:
            module_path:
                Physical path of the source file.

        Returns:
            Optional[str]: Cached hex sha256, or None when a fresh read is
            required.
        """
        try:
            stat_result = module_path.stat()
        except OSError:
            return None
        key = str(module_path)
        with cls._lock:
            entry = cls._entries.get(key)
            if (
                    entry is None
                    or entry[0] != stat_result.st_mtime_ns
                    or entry[1] != stat_result.st_size
            ):
                cls._misses += 1
                return None
            cls._entries.move_to_end(key)
            cls._hits += 1
            return entry[2]

    @classmethod
    def read_text_and_fingerprint(
            cls,
            module_name: str,
            module_path: Optional[Path],
    ) -> Tuple[Optional[str], Optional[str], Optional[str]]:
        """
        Read one physical source file, fingerprint it once, feed the cache.

        Contract:
            - Mirrors the custody read law byte-for-byte: a non-source suffix
              or missing file returns (None, None, None) - no source, not an
              error; a read failure returns (None, None, error_text) for the
              walk-error honesty channel.
            - The stat guard is taken BEFORE the read: a writer landing
              mid-read leaves a guard that self-corrects on the next stat
              (the next lookup misses and re-reads).
            - The sha256 covers the UTF-8 encoded text - identical to both the
              custody fingerprint law and the analyzer memo digest law, so one
              hash serves both consumers.

        Args:
            module_name:
                Canonical module name (used in error text only).
            module_path:
                Physical path of the source file, when available.

        Returns:
            Tuple[Optional[str], Optional[str], Optional[str]]:
                (source_text, sha256_hex, error_text).
        """
        if module_path is None:
            return None, None, None
        if module_path.suffix.lower() not in (".py", ".pyi"):
            return None, None, None
        if not module_path.exists():
            return None, None, None
        try:
            stat_result = module_path.stat()
            source_text = module_path.read_text(encoding="utf-8")
        except Exception as exc:
            return None, None, (
                "Failed to read source text for module '{0}': {1}: {2}".format(
                    module_name,
                    exc.__class__.__name__,
                    exc,
                )
            )
        fingerprint = hashlib.sha256(
            source_text.encode("utf-8")
        ).hexdigest()
        key = str(module_path)
        with cls._lock:
            cls._entries[key] = (
                stat_result.st_mtime_ns,
                stat_result.st_size,
                fingerprint,
            )
            cls._entries.move_to_end(key)
            while len(cls._entries) > cls._MAX_ENTRIES:
                cls._entries.popitem(last=False)
        return source_text, fingerprint, None

    @classmethod
    def _clear_for_tests(cls) -> None:
        """
        Reset entries and counters for deterministic test isolation.

        Contract:
            Test-only hook; never runs in production lanes. Releases only
            tuples/strings and never touches live modules or files.

        Returns:
            None.
        """
        with cls._lock:
            cls._entries.clear()
            cls._hits = 0
            cls._misses = 0

    @classmethod
    def _stats_for_tests(cls) -> Dict[str, int]:
        """
        Return detached counters for cache regression assertions.

        Returns:
            Dict[str, int]: size, capacity, hits, and misses.
        """
        with cls._lock:
            return {
                "size": len(cls._entries),
                "capacity": cls._MAX_ENTRIES,
                "hits": cls._hits,
                "misses": cls._misses,
            }
