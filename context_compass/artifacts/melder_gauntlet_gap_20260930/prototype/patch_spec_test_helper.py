"""
Temporary VM-mirror patch: let the singleton-specialization test helper see a door's globals (melder_0, 2026-09-30).

Purpose:
    `_door_binds_executor_named` finds a door's inner executor through defaults, kwdefaults and closure cells. The
    top-level door overlay keeps bindings in the door's globals dict instead, so this patch also scans
    `door.__globals__["_no_overrides_executor"]`. Used only to show that the two failures under the overlay come
    from the helper's introspection, not from behaviour; the file is restored from the device copy afterwards.

Usage:
    python patch_spec_test_helper.py <path to test_conduit_component_singleton_specialization.py>
"""
import pathlib
import sys


def main() -> int:
    """
    Patch the helper in place (keeps the file's line endings).

    Returns:
        int: 0.
    """
    path = pathlib.Path(sys.argv[1])
    raw = path.read_bytes().decode("utf-8")
    newline = "\r\n" if "\r\n" in raw else "\n"
    old = '    closure = getattr(door, "__closure__", None)'
    new = ('    namespace = getattr(door, "__globals__", None)' + newline
           + '    if isinstance(namespace, dict) and "_no_overrides_executor" in namespace:' + newline
           + '        candidates.append(namespace["_no_overrides_executor"])' + newline
           + '    closure = getattr(door, "__closure__", None)')
    if raw.count(old) != 1:
        raise SystemExit("anchor not found exactly once")
    path.write_bytes(raw.replace(old, new).encode("utf-8"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
