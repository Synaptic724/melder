


class InternalRegistrationError(RuntimeError):
    """

    Purpose:
        Signal that code tried to register a Melder-owned object that is
        intentionally protected. One stable runtime error meaning "this object
        is reserved for the framework and cannot be registered through the
        public path."

    Raised When:
        `melder.aether.spellbook.bind.bind.assert_allowed(...)` finds the registration
        sentinel on a candidate. In practice this means `Spellbook.bind(...)`
        was handed a Melder kernel object - a gate, a scheduler, a control-plane
        registry - rather than a user service.

    What To Do About It:
        You almost certainly meant to bind your own class. If you genuinely need
        the framework object, reach it through its owning surface instead of
        registering it: substrate roots hang off `Aether`, AR objects off
        `Nexus`, and pooled runtime objects off their owning `Conduit`. Melder
        constructs its own internals; it will not inject them for you.

    Contract:
        - Raised by the registration guard, not by ordinary user-level
          validation paths.
        - Message names the offending type, its module, and the calling context
          so the refusal is actionable without a debugger.
        - Remains a `RuntimeError`, so callers may catch this specific guard
          failure or treat it as a broader runtime registration error.

    Registration:
        Exported on the public root surface; import, raise, and catch freely.

    Subsystem Context:
        One of the 11 `utilities/custom_exceptions/` types, and the only one
        produced by the registration guard itself. Its sibling user-facing
        errors are `SpellbookValidationError` (binding or phase validation
        failed) and `MeldExecutionError` (resolution failed at runtime).

    System Context:
        Fires at bind time, in the earliest user-facing phase of the DGR -
        before any compiler phase, conduit, or resolution work happens. It is
        the boundary that keeps Melder's own object world out of the user's
        spell registry, which is why the sentinel exists at all.
    """

    __ast_helper_access__: str = "public"
    __agent_purpose__: str = (
        "access: public. Raised by the registration guard when bind() is handed a Melder "
        "internal; catch it to detect a kernel-object-bound-as-spell mistake. The guard "
        "constructs it - you do not."
    )

