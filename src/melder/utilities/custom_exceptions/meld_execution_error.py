from typing import Optional



class MeldExecutionError(RuntimeError):
    """
    Raised when DAG-based meld execution fails inside the Meld runtime.

    This is a **high-level wrapper** around any internal exception thrown
    while resolving a spell via the Meld engine.

    Why this exists
    ---------------

    * From the Conduit / Meld boundary we want a **single, stable**
      error type to represent "DI / resolution failed".
    * Internally, the engine may encounter:
        - Constructor/type errors
        - Missing dependency instances
        - Invalid override payloads
        - Unexpected DAG structure
    * `MeldExecutionError` captures:
        - The **root spell identity** (spell_id, spell_name).
        - Optional **node_id** if the error occurred at a specific
          DAG node.
        - Optional **param_name** if the failure is tied to a specific
          constructor parameter.
        - The underlying **inner exception**, if any.

    This gives callers and tooling enough context to log, trace, or
    present detailed diagnostics without having to interpret dozens of
    low-level exception types.
    """

    __slots__ = (
        "spell_id",
        "spell_name",
        "node_id",
        "param_name",
        "inner",
        "_message",
    )

    def __init__(
            self,
            *,
            spell_id: str,
            spell_name: str,
            message: str,
            node_id: Optional[str] = None,
            param_name: Optional[str] = None,
            inner: Optional[BaseException] = None,
    ) -> None:
        """
        Construct a new `MeldExecutionError`.

        Args:
            spell_id:
                The root spell's version identifier (typically SHA256).
            spell_name:
                Human-readable name of the root spell.
            message:
                High-level error message describing what went wrong.
            node_id:
                Optional DAG node identifier where the failure occurred.
            param_name:
                Optional parameter name associated with the failure.
            inner:
                Optional underlying exception that triggered this error.

        Contract:
            - Preserves all supplied diagnostic fields on the instance for
              downstream logging and tooling.
            - Uses `message` as the base `RuntimeError` payload while keeping
              the richer metadata separate.
        """
        super().__init__(message)
        self.spell_id: str = spell_id
        self.spell_name: str = spell_name
        self.node_id: Optional[str] = node_id
        self.param_name: Optional[str] = param_name
        self.inner: Optional[BaseException] = inner
        self._message: str = message

    def __str__(self) -> str:
        """
        Render a diagnostic string from the stored spell and node metadata.

        Returns:
            str: Stable human-readable summary including the root spell id/name
            plus any available node, parameter, message, and inner-exception
            details.
        """
        base = (
            f"[MELD] Execution failed for spell {self.spell_name!r} "
            f"({self.spell_id})"
        )

        if self.node_id is not None:
            base += f" at node {self.node_id}"

        if self.param_name is not None:
            base += f" (parameter {self.param_name!r})"

        if self._message:
            base += f": {self._message}"

        if self.inner is not None:
            base += f" (inner: {self.inner!r})"

        return base
