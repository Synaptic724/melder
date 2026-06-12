"""
Minimal internal ULID generator.

Purpose:
    Replace the external `ulid` package for runtime ID generation. The
    package itself is small, but importing it drags `importlib.metadata`
    -> `email` -> `zipfile` into every process: ~27.7ms of the measured
    237.7ms cold-import wall, paid to mint 26-character ID strings.

Contract:
    - `new_ulid()` returns a spec-compliant ULID string: 26 uppercase
      Crockford base32 characters encoding 48 bits of millisecond Unix
      timestamp followed by 80 bits of `os.urandom` randomness.
    - Output is byte-for-byte format-compatible with `str(ulid.ULID())`
      (lexicographically sortable by creation time, first character 0-7).
    - Thread-safe and lock-free: timestamp read and urandom call share no
      mutable module state, so free-threaded callers never contend.
    - Monotonicity within a single millisecond is NOT guaranteed (same as
      the default `ulid.ULID()` constructor melder previously used).
      Melder only uses these as opaque unique lineage segments.
    - Zero melder imports: safe to import from any module without cycles.
"""

import os
import time

_CROCKFORD32 = "0123456789ABCDEFGHJKMNPQRSTVWXYZ"


def new_ulid() -> str:
    """
    Return one freshly minted 26-character ULID string.

    Contract:
        - 48-bit millisecond timestamp in the high bits keeps outputs
          lexicographically sortable across calls in different ms.
        - 80 random bits from `os.urandom` make collisions negligible
          (2^80 space per millisecond).
    """
    value = (
        ((time.time_ns() // 1_000_000) & 0xFFFFFFFFFFFF) << 80
    ) | int.from_bytes(os.urandom(10), "big")
    encode = _CROCKFORD32
    return "".join(
        encode[(value >> shift) & 0x1F] for shift in range(125, -1, -5)
    )
