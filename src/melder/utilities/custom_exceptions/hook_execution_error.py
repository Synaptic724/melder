class HookExecutionError(Exception):
    """

    Purpose:
        Signal that a user-supplied lifecycle hook raised during spell melding,
        while preserving enough context to identify WHICH hook failed and WHY.

    Raised When:
        A hook registered through `SpellbookConfiguration` raises during
        resolution. Hooks run at defined points around meld - `pre_cast`,
        `activation`, `post_cast` - and a raising hook aborts that resolution.

    What To Do About It:
        The failure is in your hook body, not in Melder. Read
        `original_exception` for the real cause; `phase` and `hook_name` tell
        you which registration to look at. Melder does not swallow hook
        failures, because a hook that silently fails leaves the object half
        configured, which is worse than a refused resolution.

    Contract:
        - Preserves the hook phase and hook identity that failed.
        - Carries the original exception separately so callers can inspect or
          re-log the underlying failure without parsing the rendered message.
        - The rendered message embeds phase, hook name, and the original
          exception's type and text, so a bare log line is still diagnostic.

    Owned State:
        - `phase`: the hook phase that was executing.
        - `hook_name`: name or representation of the failing hook.
        - `original_exception`: the exception the hook body raised.

    Registration:
        USER-BINDABLE - deliberately unguarded. Exception types are values users
        catch and may legitimately register.

    Subsystem Context:
        One of the 11 `utilities/custom_exceptions/` types. It is the hook-path
        counterpart to `MeldExecutionError`: that one means Melder's own
        resolution failed, this one means YOUR code failed during Melder's
        resolution. Keeping them distinct is what lets a caller tell "the
        container is broken" apart from "my callback is broken".

    System Context:
        Fires inside the meld pipeline, after a spell has been resolved and
        while its lifecycle hooks execute. Hooks are one of the DGR's documented
        extension points, so this error is the boundary where user-supplied
        behavior re-enters Melder's control flow.
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

