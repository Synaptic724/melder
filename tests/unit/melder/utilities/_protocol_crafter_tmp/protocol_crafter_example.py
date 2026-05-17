class Example:
    """Example docstring."""
    name: str
    _secret: int

    def chain(self, value: int, label: str | None = None) -> "Example":
        """Return the fluent chain result."""
        return self

