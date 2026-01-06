"""
Certification state helpers shared across agent profile workflows.

Purpose
- Provide a single source for default certification state payloads.
- Avoid circular imports between certification guards and profile stores.

Contract
- Returned payloads are JSON-serializable dictionaries.
- Callers may mutate the returned dict without affecting shared state.
"""

from __future__ import annotations


def default_certification_state() -> dict:
    """
    Return a default certification state payload.

    Returns:
        dict: Default certification state data.
    """

    return {
        "schema_version": 1,
        "state": "UNCERTIFIED",
        "certified": False,
        "certified_at": None,
        "approved_at": None,
        "approval_token": None,
        "approved_by": None,
        "self_certification_hash": None,
        "notes": None,
    }
