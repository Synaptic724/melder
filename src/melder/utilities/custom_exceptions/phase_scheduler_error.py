from mypy_extensions import mypyc_attr

@mypyc_attr(native_class=True)
class PhaseSchedulerError(RuntimeError):
    """
    Base exception for PhaseScheduler-related failures.

    Contract:
        - Provides one stable parent type for scheduler admission, execution,
          timeout, and barrier-related failures.
        - Carries the rendered message unchanged so child exceptions can define
          their own higher-level diagnostics.
    """

    def __init__(self, message: str) -> None:
        """
        Build a scheduler-scoped runtime error.

        Args:
            message (str): Human-readable diagnostic message describing the
                scheduler failure.
        """
        super().__init__(message)
