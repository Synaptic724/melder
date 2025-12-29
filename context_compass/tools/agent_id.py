"""Generate a session-scoped agent id."""

import argparse
import secrets
import sys
import time
from typing import Optional


def _encode_crockford(value: int, length: int) -> str:
    """
    Encode an integer into Crockford base32 with fixed length.

    Args:
        value (int): Non-negative integer to encode.
        length (int): Fixed output length.

    Returns:
        str: Base32 encoded string.
    """
    if value < 0:
        raise ValueError("value must be non-negative")
    alphabet = "0123456789ABCDEFGHJKMNPQRSTVWXYZ"
    chars = []
    for _ in range(length):
        chars.append(alphabet[value & 31])
        value >>= 5
    return "".join(reversed(chars))


def generate_ulid(now_ms: Optional[int] = None, randomness: Optional[int] = None) -> str:
    """
    Generate a lowercase ULID string (26 chars, Crockford base32).

    Args:
        now_ms (Optional[int]): Override timestamp in milliseconds.
        randomness (Optional[int]): Override 80-bit randomness integer.

    Returns:
        str: ULID string in lowercase.
    """
    if now_ms is None:
        now_ms = int(time.time() * 1000)
    if now_ms < 0 or now_ms >= (1 << 48):
        raise ValueError("now_ms must fit in 48 bits")
    if randomness is None:
        randomness = secrets.randbits(80)
    if randomness < 0 or randomness >= (1 << 80):
        raise ValueError("randomness must fit in 80 bits")

    time_part = _encode_crockford(now_ms, 10)
    rand_part = _encode_crockford(randomness, 16)
    return f"{time_part}{rand_part}".lower()


def generate_agent_id(prefix: Optional[str] = None, now_ms: Optional[int] = None, randomness: Optional[int] = None) -> str:
    """
    Generate an agent id using a ULID with an optional prefix.

    Args:
        prefix (Optional[str]): Optional prefix (e.g., "agent").
        now_ms (Optional[int]): Override timestamp in milliseconds.
        randomness (Optional[int]): Override 80-bit randomness integer.

    Returns:
        str: Agent id string.
    """
    ulid = generate_ulid(now_ms=now_ms, randomness=randomness)
    if prefix:
        return f"{prefix}_{ulid}"
    return ulid


def main() -> None:
    """
    CLI entrypoint for agent id generation.
    """
    parser = argparse.ArgumentParser(description="Generate a session agent id")
    parser.add_argument("--prefix", default=None, help="Optional prefix (e.g., agent)")
    args = parser.parse_args()
    sys.stdout.write(f"{generate_agent_id(prefix=args.prefix)}\n")


if __name__ == "__main__":
    main()
