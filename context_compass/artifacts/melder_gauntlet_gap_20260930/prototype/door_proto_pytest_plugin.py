"""
pytest plugin: install the top-level door overlay before any test builds a Spellbook (melder_0, 2026-09-30).

Usage:
    PYTHONPATH=<dir holding door_proto.py> python -X gil=0 -m pytest -p door_proto_pytest_plugin <tests>

Contract:
    - Installs the overlay once in pytest_configure and prints one line saying so; nothing else changes.
"""
from typing import Any

import door_proto


def pytest_configure(config: Any) -> None:
    """
    Install the overlay before collection.

    Args:
        config: The pytest config (unused).
    """
    originals = door_proto.install(door_proto.door_module())
    print(f"[door_proto] overlay installed over {sum(len(v) for v in originals.values())} template entries")
