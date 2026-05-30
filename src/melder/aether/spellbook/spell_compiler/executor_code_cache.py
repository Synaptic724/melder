"""
Process-wide compiled-executor code-object cache.

Phase 13 emits Python source for spell executors and compiles it with the
built-in ``compile``. That emitted source is *identity-free*: it is a pure
function of plan **shape**, and every spell-identity value (spell objects,
spell ids, instance keys, root key, dependency targets) is supplied later, at
``exec`` time, through the executor namespace. Two spells -- or two conjures of
the same spell, or two different Spellbooks -- that emit the same source can
therefore safely share a single compiled code object.

This module owns one process-wide, bounded cache keyed on the SHA-256 of the
emitted source. It is consumed by both Phase 13 compile chokepoints:
``_compile_emitted_no_overrides_executor`` (no-overrides lane) and
``compile_phase13_overrides_executor_code_object`` (overrides lane).

Why source content is a safe key
--------------------------------
``compile`` is a deterministic pure function of its source text. The synthetic
filename only affects ``co_filename`` for tracebacks, and each lane uses a
single constant filename, so equal source yields an interchangeable code
object. If some future emitted source *did* embed identity, equal-identity
calls would simply land on distinct keys -- correct, only less sharing. The key
can never cause a wrong code object to be returned.

Concurrency
-----------
Conjure runs phases across ``PhaseScheduler`` worker threads, so this cache is
a cross-thread hot path. The design keeps the expensive work -- ``compile`` --
fully parallel and never serialized:

  - Reads (cache hits) are lock-free: a single ``dict.get``.
  - On a miss, ``compile`` runs OUTSIDE any lock, so threads never wait on each
    other's compilation.
  - Only the tiny store-and-evict bookkeeping runs under a short-lived lock,
    during which a re-check makes concurrent compilers of the same source
    converge on one shared code object (the duplicate is discarded).

Individual ``dict`` operations are atomic on CPython, including free-threaded
3.14t builds, so the lock-free read path is safe. No lock is required for
correctness; the store lock exists only to keep bounded eviction simple and to
deduplicate redundant stores.
"""

import hashlib
import threading
from types import CodeType
from typing import Dict


# Maximum number of distinct compiled executors retained at once. A long-lived
# process that authors many distinct spell shapes over time stays bounded.
# Eviction is FIFO (oldest inserted entry first) and never affects correctness:
# an evicted shape is simply recompiled the next time it is needed.
_DEFAULT_MAX_ENTRIES: int = 4096

_store_lock: threading.Lock = threading.Lock()
_code_by_source_hash: Dict[str, CodeType] = {}
_max_entries: int = _DEFAULT_MAX_ENTRIES

# Best-effort counters for observability only. Hits are incremented without the
# lock, so under heavy contention the totals are approximate.
_hit_count: int = 0
_miss_count: int = 0


def _hash_source(source: str) -> str:
    """Return the SHA-256 hex digest used as the cache key for ``source``."""
    return hashlib.sha256(source.encode("utf-8")).hexdigest()


def get_or_compile_executor_code(
        *,
        source: str,
        source_name: str,
) -> CodeType:
    """
    Return a compiled code object for ``source``, compiling on cache miss.

    The returned code object is identity-free and safe to ``exec`` against any
    per-spell namespace.

    Contract:
        - Cache hits take a single lock-free dict lookup.
        - On a miss, ``compile`` runs outside the lock; any exception it raises
          propagates unchanged so callers keep their own error wrapping.
        - Failed compilations are never cached.
        - Concurrent compilers of identical source converge on one shared code
          object.

    Args:
        source:
            Emitted, identity-free executor source text.
        source_name:
            Synthetic filename passed to ``compile`` (traceback display only).

    Returns:
        CodeType:
            Compiled code object defining ``_phase13_executor``.
    """
    global _hit_count, _miss_count

    source_hash = _hash_source(source)

    cached = _code_by_source_hash.get(source_hash)
    if cached is not None:
        _hit_count += 1
        return cached

    # Compile outside the lock so threads never wait on each other's compiles.
    compiled_code = compile(source, source_name, "exec")

    with _store_lock:
        # Re-check: another thread may have stored identical source meanwhile.
        existing = _code_by_source_hash.get(source_hash)
        if existing is not None:
            _hit_count += 1
            return existing
        _code_by_source_hash[source_hash] = compiled_code
        _miss_count += 1
        if len(_code_by_source_hash) > _max_entries:
            _evict_oldest_locked()
    return compiled_code


def _evict_oldest_locked() -> None:
    """
    Drop oldest-inserted entries until the cache is back within its bound.

    Must be called while holding ``_store_lock``. ``dict`` preserves insertion
    order, so iteration yields oldest-first (FIFO). Eviction is correctness-safe:
    an evicted shape is simply recompiled the next time it is needed.
    """
    target = (_max_entries * 9) // 10
    while len(_code_by_source_hash) > target:
        try:
            oldest_key = next(iter(_code_by_source_hash))
        except StopIteration:
            return
        _code_by_source_hash.pop(oldest_key, None)


def clear_executor_code_cache() -> None:
    """Clear all cached code objects and counters. Intended for tests/teardown."""
    global _hit_count, _miss_count
    with _store_lock:
        _code_by_source_hash.clear()
        _hit_count = 0
        _miss_count = 0


def set_executor_code_cache_max_entries(max_entries: int) -> None:
    """
    Set the cache bound, evicting immediately if the cache now exceeds it.

    Args:
        max_entries:
            New maximum entry count. Must be >= 1.
    """
    global _max_entries
    if max_entries < 1:
        raise ValueError("max_entries must be >= 1.")
    with _store_lock:
        _max_entries = max_entries
        if len(_code_by_source_hash) > _max_entries:
            _evict_oldest_locked()


def executor_code_cache_stats() -> Dict[str, int]:
    """Return approximate cache statistics for observability."""
    return {
        "entries": len(_code_by_source_hash),
        "max_entries": _max_entries,
        "hits": _hit_count,
        "misses": _miss_count,
    }

