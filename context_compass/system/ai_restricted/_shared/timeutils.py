"""Time utilities for context_compass tools."""

from datetime import datetime, timezone


def utc_now_iso() -> str:
    """
    Return the current UTC time as an ISO-8601 string with Z suffix.

    Returns:
        str: UTC timestamp (e.g., "2025-12-28T00:00:00Z").
    """
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def parse_iso8601(value: str) -> datetime:
    """
    Parse an ISO-8601 timestamp with optional Z suffix.

    Args:
        value (str): ISO-8601 timestamp string.

    Returns:
        datetime: Timezone-aware datetime in UTC.

    Raises:
        ValueError: If the timestamp cannot be parsed.
    """
    if value.endswith("Z"):
        value = value[:-1] + "+00:00"
    dt = datetime.fromisoformat(value)
    if dt.tzinfo is None:
        raise ValueError("Timestamp is not timezone-aware")
    return dt.astimezone(timezone.utc)
