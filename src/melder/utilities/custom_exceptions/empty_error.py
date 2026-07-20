class Empty(Exception):
    """

    Purpose:
        Signal that an operation required at least one item and the container
        was empty. Intentionally broad and lightweight.

    Raised When:
        A caller demands an element from an empty container or an empty runtime
        state where emptiness is the contract failure rather than a normal
        result.

    What To Do About It:
        Check before you take, or treat empty as a legitimate branch. If you are
        reaching for this in new code, first ask whether a domain-specific error
        would tell the caller more - `Empty` deliberately carries no context
        beyond its type, so it is the right choice only when there is no useful
        context to carry.

    Contract:
        - Plain `Exception` subclass with no added state or metadata.
        - Deliberately does NOT mirror `queue.Empty`; catching one will not
          catch the other. Import this one explicitly.

    Registration:
        USER-BINDABLE - deliberately unguarded. Exception types are values users
        catch and may legitimately register.

    Subsystem Context:
        The most general of the 11 `utilities/custom_exceptions/` types. Where
        siblings such as `SpellSpaceScopeError` or `MeldExecutionError` name a
        specific subsystem failure, this one names only the shape of the
        failure, and is the fallback when no richer type applies.

    System Context:
        Not tied to any DGR phase or subsystem. It is a substrate-level
        signal usable anywhere in the stack, which is exactly why it should be
        reached for last rather than first.
    """
    pass
