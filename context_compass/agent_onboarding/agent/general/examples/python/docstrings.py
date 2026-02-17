"""
Purpose:
- Show contract-first docstrings for public APIs.

Notes:
- Include purpose, invariants, inputs/outputs, and explicit error contracts.
- Use Spellbook.bind (src/melder/spellbook/spellbook.py) as the gold standard.
"""

from dataclasses import dataclass
from typing import Mapping


@dataclass(frozen=True)
class ConfigSnapshot:
    """
    Immutable config snapshot used for downstream validation.

    Contract:
      - Fields are validated before construction.
      - Instances are immutable and safe to share.
    """

    name: str
    timeout_seconds: int


class ConfigParser:
    """
    Parses raw config mappings into validated snapshots.

    Contract:
      - Does not mutate the input mapping.
      - Raises ValueError when required keys are missing.
      - Does not perform IO.
    """

    def parse(self, raw: Mapping[str, object]) -> ConfigSnapshot:
        """
        Parse a raw mapping into a validated ConfigSnapshot.

        Args:
            raw (Mapping[str, object]): Input config data.

        Returns:
            ConfigSnapshot: Immutable, validated config snapshot.

        Raises:
            ValueError: If required keys are missing or invalid.
        """
        name = raw.get("name")
        timeout = raw.get("timeout_seconds")
        if not isinstance(name, str):
            raise ValueError("name must be a string")
        if not isinstance(timeout, int):
            raise ValueError("timeout_seconds must be an int")
        return ConfigSnapshot(name=name, timeout_seconds=timeout)


def load_config(raw: Mapping[str, object]) -> ConfigSnapshot:
    """
    Load a config snapshot from a raw mapping.

    Contract:
      - Delegates validation to ConfigParser.
      - Does not perform IO.

    Args:
        raw (Mapping[str, object]): Input config data.

    Returns:
        ConfigSnapshot: Immutable, validated config snapshot.
    """
    return ConfigParser().parse(raw)
