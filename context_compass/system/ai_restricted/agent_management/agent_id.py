"""Generate a session-scoped agent id."""

import argparse
import secrets
import sys
import time
from typing import Optional

from context_compass.system.ai_restricted._shared.command_payload import PayloadError, optional_string
from context_compass.system.ai_restricted._shared.command_results import (
    exception_result,
    ok_result,
    payload_error_result,
)
from context_compass.system.ai_restricted._shared.command_contracts import (
    CommandResult,
    ExecutionContext,
)

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


def run(payload: dict, ctx: ExecutionContext) -> CommandResult:
    """
    Generate an agent id using the ToolCommandAPI contract.

    Args:
        payload (dict): JSON-serializable kwargs payload.
        ctx (ExecutionContext): Execution context for the command.

    Returns:
        CommandResult: Result containing the generated agent id.

    Raises:
        None: All errors are returned as CommandResult payloads.

    Contract:
        - Accepts an optional prefix string.
        - Returns agent_id in the output payload.
    """

    command_name = ctx.command_name
    try:
        prefix = optional_string(payload, "prefix", command_name=command_name)
    except PayloadError as exc:
        return payload_error_result(command_name, exc)

    try:
        agent_id = generate_agent_id(prefix=prefix)
    except Exception as exc:
        return exception_result(command_name, exc)

    return ok_result(output={"agent_id": agent_id})


def main() -> None:
    """
    CLI entrypoint for agent id generation.

    Returns:
        None: Exits with status 1 on command failure.

    Raises:
        SystemExit: When the command returns a non-ok result.
    """
    parser = argparse.ArgumentParser(description="Generate a session agent id")
    parser.add_argument("--prefix", default=None, help="Optional prefix (e.g., agent)")
    args = parser.parse_args()
    context = ExecutionContext(
        command_name="agent_id",
        agent_id=None,
        work_id=None,
        correlation_id=None,
    )
    result = run({"prefix": args.prefix}, context)
    if result.status != "ok":
        raise SystemExit(1)
    sys.stdout.write(f"{result.output.get('agent_id')}\n")


if __name__ == "__main__":
    main()
