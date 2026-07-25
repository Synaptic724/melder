


class DeadReferenceError(ReferenceError):
    """

    Purpose:
        Signal that a weak-reference target was requested after the referent was
        already collected. Turns a silent `None` into an explicit failure at the
        point of use.

    Raised When:
        A weak-reference helper is asked for a live target and the referenced
        object has already been garbage collected. Sources in-tree are the weak
        containers (`WeakConcurrentDict`, `WeakConcurrentList`,
        `WeakConcurrentSet`, `WeakRefNode`) and `SyncWeakRef`.

    What To Do About It:
        The referent outlived nothing - you outlived it. Either hold a strong
        reference for as long as you need the object, or treat absence as normal
        and probe before asking for a live target. In a room/workstation
        context, weak binding is the default posture precisely so stale bindings
        collapse instead of pinning objects alive; hitting this usually means
        you wanted a strong binding.

    Contract:
        - Subclasses `ReferenceError`, so existing weak-reference handling
          catches it without knowing about Melder.
        - Raised only on explicit live-target requests. Membership and iteration
          over weak containers skip dead entries rather than raising.

    Registration:
        GUARDED, and exported. Present in `INTERNAL_MANIFEST`, so
        `Spellbook.bind(...)` refuses it. That restricts REGISTRATION only, never
        USE: import it, raise it, and catch it freely. Guarding and exporting are
        orthogonal - this type is on the public root surface AND unbindable.

    Subsystem Context:
        One of the 11 `utilities/custom_exceptions/` types, and the one tied to
        `utilities/data_structures/weak_data_structures/`. It is the failure
        mode of the weak-container family, which exists so caches and registries
        can hold objects without extending their lifetime.

    System Context:
        Outside the DGR phases entirely - this is a substrate-level lifetime
        error, not a resolution error. It can surface anywhere weak references
        are used, including room-local workstation bindings, which publish a
        collection event rather than raising when a weakly-bound object goes
        away.
    """

    __ast_helper_access__: str = "public"
    __agent_purpose__: str = (
        "access: public. Raised when a weak-reference target is requested after collection; "
        "catch it (it subclasses ReferenceError) or hold a strong reference. It means you "
        "outlived the referent."
    )