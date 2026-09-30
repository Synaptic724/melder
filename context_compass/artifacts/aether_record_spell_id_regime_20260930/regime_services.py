"""Importable spell targets for the regime probe; the restoring process imports them by module path."""


class TenantService:
    """The class every tenant frame binds (the multi-tenant shape: one class, several isolated frames)."""

    def __init__(self) -> None:
        """Mark the instance alive."""
        self.alive: bool = True


class OtherService:
    """A second class, for worlds whose frames bind different classes."""

    def __init__(self) -> None:
        """Mark the instance alive."""
        self.alive: bool = True
