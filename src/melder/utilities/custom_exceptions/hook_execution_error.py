class HookExecutionError(Exception):
    """
    Raised when a lifecycle hook fails during spell melding.

    Contract:
        - Preserves the hook phase and hook identity that failed.
        - Carries the original exception separately so callers can inspect or
          re-log the underlying failure without parsing the rendered message.
    """
    def __init__(self, phase: str, hook_name: str, original_exception: Exception):
        """
        Build a hook-execution failure with preserved source metadata.

        Args:
            phase (str): Hook phase such as `pre_cast`, `activation`, or
                `post_cast`.
            hook_name (str): Name or representation of the hook that failed.
            original_exception (Exception): Original exception raised by the
                hook body.
        """
        self.phase = phase
        self.hook_name = hook_name
        self.original_exception = original_exception
        super().__init__(f"[HOOK][{phase}] Hook '{hook_name}' failed: {type(original_exception).__name__}: {original_exception}")

