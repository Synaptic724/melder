"""
Purpose:
- Show component tests for small slices of real wiring.

Notes:
- Use component tests when unit tests are too mocked and integration is too heavy.
- Keep IO boundaries out of component tests.
"""

from typing import Optional

import pytest


class MemoryStore:
    """
    In-memory store used as a component dependency.
    """

    def __init__(self) -> None:
        self._items: dict[str, str] = {}

    def put(self, key: str, value: str) -> None:
        self._items[key] = value

    def get(self, key: str) -> Optional[str]:
        return self._items.get(key)


class Service:
    """
    Small service that depends on MemoryStore.
    """

    def __init__(self, store: MemoryStore) -> None:
        self._store = store

    def register(self, key: str, value: str) -> None:
        self._store.put(key, value)

    def lookup(self, key: str) -> Optional[str]:
        return self._store.get(key)


def _build_component() -> tuple[MemoryStore, Service]:
    store = MemoryStore()
    service = Service(store)
    return store, service


@pytest.mark.component
def test_component_register_and_lookup() -> None:
    """
    Validate a small slice of real wiring without external IO.
    """
    _, service = _build_component()
    service.register("alpha", "ok")
    assert service.lookup("alpha") == "ok"
