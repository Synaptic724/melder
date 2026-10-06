"""Importable spell targets for the direct-meld probe: the epic's two plain classes plus one unrelated resident."""


class NativeService:
    """Concrete no-argument dependency, unrelated to any host framework (the epic's NativeService)."""

    def __init__(self) -> None:
        """Make ordinary instance state so this is not an empty-class signature probe."""
        self.value: int = 7


class NativeConsumer:
    """Require a service that the native graph supplies during construction (the epic's NativeConsumer)."""

    def __init__(self, service: NativeService) -> None:
        """Retain the injected dependency for identity verification."""
        self.service: NativeService = service


class ResidentService:
    """An unrelated spell the root already holds at conjure, standing in for a host's framework definitions."""

    def __init__(self) -> None:
        """Mark the instance ready."""
        self.ready: bool = True
