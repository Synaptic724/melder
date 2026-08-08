"""
Minimal internal ULID generator and reader.

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
    - Zero melder imports: safe to import from any module without cycles.

Shape of this module - why minting is a bare function:
    `new_ulid()` is deliberately module-level rather than a method. It is
    the hot path (every object identity in the runtime passes through it),
    and a module global is one LOAD_GLOBAL where a class attribute is a
    LOAD_GLOBAL plus a descriptor lookup. Everything else - decoding,
    validation - is cold by comparison and lives on `ULID_Factory` so the
    read side has one obvious home instead of six loose functions.

    `ULID_Factory.new_ulid` is bound to the SAME function object, not a
    wrapper, so calling it through the class costs the attribute lookup and
    nothing else. Hot callers should still import `new_ulid` directly.
"""

from datetime import datetime, timezone
import os
import time

_CROCKFORD32 = "0123456789ABCDEFGHJKMNPQRSTVWXYZ"

# Canonical Crockford decoding: case-insensitive, and I/L decode as 1 while
# O decodes as 0. Those aliases never appear in our own output (the encode
# alphabet excludes them) but the spec accepts them, so hand-typed or
# externally produced ids still round-trip.
_DECODE = {c: i for i, c in enumerate(_CROCKFORD32)}
_DECODE.update({c.lower(): i for i, c in enumerate(_CROCKFORD32)})
_DECODE.update({"I": 1, "i": 1, "L": 1, "l": 1, "O": 0, "o": 0})

_ULID_LEN = 26
_TIMESTAMP_BITS = 48
_RANDOM_BITS = 80
_RANDOM_MASK = (1 << _RANDOM_BITS) - 1
# 26 chars x 5 bits = 130 bits of encoding space for a 128-bit value, so the
# leading character carries only 3 usable bits and cannot exceed 7.
_MAX_ULID = (1 << (_TIMESTAMP_BITS + _RANDOM_BITS)) - 1


def new_ulid() -> str:
    """
    Return one freshly minted 26-character ULID string.

    Contract:
        - 48-bit millisecond timestamp in the high bits keeps outputs
          lexicographically sortable across calls in different ms.
        - 80 random bits from `os.urandom` make collisions negligible
          (2^80 space per millisecond).

    Returns:
        str: A fresh 26-character ULID.
    """
    value = (
        ((time.time_ns() // 1_000_000) & 0xFFFFFFFFFFFF) << 80
    ) | int.from_bytes(os.urandom(10), "big")
    encode = _CROCKFORD32
    return "".join(
        encode[(value >> shift) & 0x1F] for shift in range(125, -1, -5)
    )


class ULID_Factory:
    """

    Purpose:
        Mint and read ULIDs without the external `ulid` dependency. Minting
        alone would make this module write-only, which throws away the
        reason to prefer a ULID over a UUID: the creation time is IN the id.

    Responsibilities:
        - Expose minting via `new_ulid` (aliased, not reimplemented).
        - Decode the 48-bit timestamp back out as ms, seconds, or datetime.
        - Decode the 80 random bits for tie-breaking within one millisecond.
        - Validate untrusted strings without raising.

    Contract:
        - Every method is a static helper; this is a namespace, not an object
          with a lifetime. Never instantiate it.
        - `timestamp()` and `datetime()` mirror the `.timestamp` / `.datetime`
          accessors on the external `ulid` package, so callers migrating off
          it find what they expect.
        - All decoders raise on malformed input; `is_ulid()` is the ask-first
          counterpart that never raises.
        - Decoding accepts the full Crockford alphabet case-insensitively,
          which is a superset of what `new_ulid()` emits.

    Owned State:
        None. Stateless and therefore thread-safe; no shared counter to
        contend on under free threading.

    Lifecycle / Cleanup:
        No instances and no cleanup contract. Deliberately not `Cleanable` -
        there is nothing to release.

    Subsystem Context:
        One of the `utilities/helpers/` static namespaces alongside
        `IDBuilder` (identity FORMAT), `EnumHelpers` and `InitHelpers`.
        `IDBuilder.create_id()` mints through this module; this class owns the
        id VALUE, `IDBuilder` owns how values are joined into lineage strings.

    AGENT_ACCESS: public

    AGENT_PURPOSE:
        access: public. Static namespace for ULID values. new_ulid() mints;
        timestamp_ms()/timestamp()/datetime() read the creation time back out;
        randomness() breaks same-millisecond ties; is_ulid() validates. Stateless -
        call the methods directly, never instantiate.
    """

    # Bound to the SAME function object defined above, not a wrapper around it.
    # `ULID_Factory.new_ulid is new_ulid` -> True, so routing through the class
    # adds an attribute lookup and no call frame.
    new_ulid = staticmethod(new_ulid)

    @staticmethod
    def to_int(value: str) -> int:
        """
        Decode one ULID string back to its 128-bit integer value.

        Contract:
            - Accepts the canonical Crockford alphabet case-insensitively,
              including the I/L -> 1 and O -> 0 aliases.
            - Rejects anything that is not 26 valid characters, and rejects a
              leading character above 7 (which would overflow 128 bits).

        Args:
            value:
                The 26-character ULID string to decode.

        Returns:
            int: The 128-bit value encoded by the string.

        Raises:
            TypeError: If `value` is not a string.
            ValueError: If `value` is not a well-formed 26-character ULID.
        """
        if not isinstance(value, str):
            raise TypeError(f"ULID must be a str, got {type(value).__name__}.")
        if len(value) != _ULID_LEN:
            raise ValueError(f"ULID must be {_ULID_LEN} characters, got {len(value)}.")
        result = 0
        for position, char in enumerate(value):
            try:
                result = (result << 5) | _DECODE[char]
            except KeyError:
                raise ValueError(
                    f"Invalid Crockford base32 character {char!r} at position {position}."
                ) from None
        if result > _MAX_ULID:
            raise ValueError("ULID overflows 128 bits; the leading character must be 0-7.")
        return result

    @staticmethod
    def timestamp_ms(value: str) -> int:
        """
        Return the creation time encoded in a ULID, in Unix milliseconds.

        Contract:
            - Reads the high 48 bits, which `new_ulid()` fills from the
              millisecond wall clock at mint time.
            - Milliseconds is the id's true resolution; prefer this over
              `timestamp()` when you do not want float rounding.

        Args:
            value:
                The 26-character ULID string to read.

        Returns:
            int: Milliseconds since the Unix epoch.

        Raises:
            TypeError: If `value` is not a string.
            ValueError: If `value` is not a well-formed 26-character ULID.
        """
        return ULID_Factory.to_int(value) >> _RANDOM_BITS

    @staticmethod
    def timestamp(value: str) -> float:
        """
        Return the creation time encoded in a ULID, in Unix seconds.

        Contract:
            - Mirrors `ulid.ULID(...).timestamp` on the external package.
            - Millisecond resolution; the fractional part never carries more
              than three significant digits because that is all the id stores.

        Args:
            value:
                The 26-character ULID string to read.

        Returns:
            float: Seconds since the Unix epoch.

        Raises:
            TypeError: If `value` is not a string.
            ValueError: If `value` is not a well-formed 26-character ULID.
        """
        return ULID_Factory.timestamp_ms(value) / 1000

    @staticmethod
    def datetime(value: str) -> "datetime":
        """
        Return the creation time encoded in a ULID as an aware datetime.

        Contract:
            - Always UTC. Never returns a naive datetime, so callers cannot
              accidentally compare it against local time.
            - Millisecond resolution, matching what the id actually stores.
            - Mirrors `ulid.ULID(...).datetime` on the external package.

        Args:
            value:
                The 26-character ULID string to read.

        Returns:
            datetime: Creation time in UTC.

        Raises:
            TypeError: If `value` is not a string.
            ValueError: If `value` is not a well-formed 26-character ULID.
        """
        # `datetime` here resolves to the module-level import, not this method:
        # method bodies never see class scope. The return annotation is a string
        # for the same reason - it IS evaluated in class scope, where the name
        # would otherwise bind to this staticmethod.
        return datetime.fromtimestamp(
            ULID_Factory.timestamp_ms(value) / 1000, tz=timezone.utc
        )

    @staticmethod
    def randomness(value: str) -> int:
        """
        Return the 80 random bits of a ULID with the timestamp stripped off.

        Contract:
            - Distinguishes two ids minted in the same millisecond, where the
              timestamp alone cannot tell them apart.

        Args:
            value:
                The 26-character ULID string to read.

        Returns:
            int: The low 80 bits of the id.

        Raises:
            TypeError: If `value` is not a string.
            ValueError: If `value` is not a well-formed 26-character ULID.
        """
        return ULID_Factory.to_int(value) & _RANDOM_MASK

    @staticmethod
    def is_ulid(value: object) -> bool:
        """
        Return whether a value is a well-formed ULID string.

        Contract:
            - Never raises. This is the ask-first counterpart to the decoders,
              for call sites validating untrusted input.

        Args:
            value:
                Candidate to test. Any type is accepted.

        Returns:
            bool: True when `value` decodes as a 26-character ULID.
        """
        try:
            ULID_Factory.to_int(value)  # type: ignore[arg-type]
        except (TypeError, ValueError):
            return False
        return True
