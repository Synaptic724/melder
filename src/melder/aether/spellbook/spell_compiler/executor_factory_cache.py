"""
Process-wide compiled-executor *factory* cache.

This module is the second tier above ``executor_code_cache``. The code cache
deduplicates ``compile`` of identity-free emitted source; this cache
deduplicates the ``exec`` step by wrapping emitted executor source in a
*factory* function and exec-ing it exactly once per source shape.

Why a factory tier exists
-------------------------
Emitted executor source binds identity (live spells, instance keys, disposal
metadata) through function defaults whose names resolve from the enclosing
scope at ``def`` execution time. The legacy path runs ``exec(code, namespace)``
once per spell because identity arrives through that namespace. Wrapping the
same emitted source inside::

    def __melder_executor_factory__(bindings):
        <unpack identity names from bindings>
        <emitted executor def, defaults now resolve from factory locals>
        return <executor name>

moves identity injection from exec time to call time. The factory body is a
pure function of source shape, so two spells (or two conjures, or a live build
and a cache load) with the same emitted source share one exec'd factory and
hydrate per-spell executors with a plain function call.

Static helper names (exception types, enums, shared runtime helpers) are
provided through the factory's globals namespace on first build. They are
process-constant, so sharing one globals dict per cached factory is safe.

Concurrency
-----------
Same discipline as ``executor_code_cache``:

  - Reads (cache hits) are lock-free: a single ``dict.get``.
  - On a miss, ``compile`` + ``exec`` run OUTSIDE any lock.
  - Only store-and-evict bookkeeping runs under a short-lived lock, with a
    re-check so concurrent builders of the same source converge on one shared
    factory.
"""

import hashlib
import threading
from typing import Any, Callable, Dict, Iterable, Tuple

FACTORY_NAME = "__melder_executor_factory__"

# Maximum number of distinct exec'd factories retained at once. Eviction is
# FIFO and never affects correctness: an evicted shape is re-exec'd on next use.
_DEFAULT_MAX_ENTRIES: int = 4096

_store_lock: threading.Lock = threading.Lock()
_factory_by_source_hash: Dict[str, Callable[[Dict[str, Any]], Callable[..., Any]]] = {}
_max_entries: int = _DEFAULT_MAX_ENTRIES


def build_executor_factory_source(
        *,
        inner_source: str,
        binding_names: Tuple[str, ...],
        executor_name: str,
) -> str:
    """
    Wrap identity-free emitted executor source in a factory definition.

    Purpose:
        Produce factory source whose only inputs are one ``bindings`` mapping,
        so the exec'd factory is shareable across every spell that emits the
        same inner source.

    Contract:
        - ``binding_names`` are unpacked from ``bindings`` into factory locals
          in sorted order so factory source is deterministic per shape.
        - The inner emitted ``def`` is indented unmodified; its default
          expressions resolve identity names from factory locals and static
          helper names from factory globals.
        - Returns source defining exactly one module-level callable named
          ``__melder_executor_factory__``.

    Args:
        inner_source:
            Identity-free emitted executor source (one ``def`` statement).
        binding_names:
            Identity names the inner source resolves at def-execution time.
        executor_name:
            Name of the executor function defined by ``inner_source``.

    Returns:
        str:
            Factory source text.
    """
    lines = [f"def {FACTORY_NAME}(bindings):"]
    for name in sorted(binding_names):
        lines.append(f"    {name} = bindings[{name!r}]")
    for inner_line in inner_source.splitlines():
        if inner_line:
            lines.append("    " + inner_line)
        else:
            lines.append("")
    lines.append(f"    return {executor_name}")
    return "\n".join(lines)


def get_or_build_executor_factory(
        *,
        factory_source: str,
        source_name: str,
        static_namespace: Dict[str, Any],
) -> Callable[[Dict[str, Any]], Callable[..., Any]]:
    """
    Return the process-shared factory for one factory-source shape.

    Purpose:
        Guarantee one ``compile`` + one ``exec`` per distinct factory source
        per process, so per-spell hydration is one factory call.

    Contract:
        - Cache hits are lock-free.
        - ``static_namespace`` is consulted only on a build miss; callers must
          pass process-constant values so sharing is safe.
        - The returned factory accepts one ``bindings`` mapping and returns
          the hydrated executor callable.

    Args:
        factory_source:
            Source produced by ``build_executor_factory_source``.
        source_name:
            Synthetic filename for tracebacks through the factory.
        static_namespace:
            Process-constant helper names the inner source resolves globally.

    Returns:
        Callable[[Dict[str, Any]], Callable[..., Any]]:
            The shared exec'd factory.

    Raises:
        RuntimeError:
            If the factory source does not define the expected callable.
    """
    source_hash = hashlib.sha256(factory_source.encode("utf-8")).hexdigest()

    factory = _factory_by_source_hash.get(source_hash)
    if factory is not None:
        return factory

    code_object = compile(factory_source, source_name, "exec")
    factory_globals: Dict[str, Any] = dict(static_namespace)
    local_namespace: Dict[str, Any] = {}
    exec(code_object, factory_globals, local_namespace)
    built_factory = local_namespace.get(FACTORY_NAME)
    if not callable(built_factory):
        raise RuntimeError(
            "Executor factory source did not define a callable "
            f"{FACTORY_NAME}."
        )

    with _store_lock:
        existing_factory = _factory_by_source_hash.get(source_hash)
        if existing_factory is not None:
            return existing_factory
        while len(_factory_by_source_hash) >= _max_entries:
            oldest_key = next(iter(_factory_by_source_hash))
            del _factory_by_source_hash[oldest_key]
        _factory_by_source_hash[source_hash] = built_factory
    return built_factory


def split_namespace_for_factory(
        *,
        namespace: Dict[str, Any],
        static_keys: Iterable[str],
) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    """
    Split one legacy executor namespace into static helpers and bindings.

    Purpose:
        Let callers reuse the existing namespace builders unchanged, then
        partition their output into the process-constant globals half and the
        per-spell bindings half consumed by the factory.

    Contract:
        - Keys listed in ``static_keys`` land in the static half.
        - Every other key lands in the bindings half.
        - Neither half aliases the input dict.

    Args:
        namespace:
            Full namespace produced by a legacy namespace builder.
        static_keys:
            Names whose values are process-constant helpers.

    Returns:
        Tuple[Dict[str, Any], Dict[str, Any]]:
            ``(static_namespace, bindings)``.
    """
    static_key_set = set(static_keys)
    static_namespace: Dict[str, Any] = {}
    bindings: Dict[str, Any] = {}
    for key, value in namespace.items():
        if key in static_key_set:
            static_namespace[key] = value
        else:
            bindings[key] = value
    return static_namespace, bindings


def clear_executor_factory_cache() -> None:
    """
    Drop every cached factory. Intended for tests and diagnostics only.
    """
    with _store_lock:
        _factory_by_source_hash.clear()


def executor_factory_cache_size() -> int:
    """
    Return the current number of cached factories.
    """
    return len(_factory_by_source_hash)
