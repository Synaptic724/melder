class HookExecutionError(Exception):
    """
    Raised when a lifecycle hook fails during spell melding.

    Attributes:
        phase (str): The hook phase (e.g., 'pre_cast', 'activation', 'post_cast').
        hook_name (str): The name or representation of the hook that failed.
        original_exception (Exception): The original exception that was raised.
    """
    def __init__(self, phase: str, hook_name: str, original_exception: Exception):
        self.phase = phase
        self.hook_name = hook_name
        self.original_exception = original_exception
        super().__init__(f"[HOOK][{phase}] Hook '{hook_name}' failed: {type(original_exception).__name__}: {original_exception}")

