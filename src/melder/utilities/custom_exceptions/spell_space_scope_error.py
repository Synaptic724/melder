



class SpellSpaceScopeError(RuntimeError):
    """

    Purpose:
        Signal that a SpellSpace scoping rule was violated - a lifetime or
        ownership failure, not a generic runtime error.

    Raised When:
        - A spell bound `Existence.unique_per_spell_space` is resolved with no
          active SpellSpace.
        - A SpellSpace is used across a different Conduit than the one that
          created it.
        - A SpellSpace is used after it has been closed.

    What To Do About It:
        Enter the scope before resolving: `conduit.enter_spellspace()` creates
        and activates one, and `SpellSpace.meld(...)` is the only door that can
        satisfy request-local storage. The conduit front door deliberately
        REFUSES `unique_per_spell_space` lineages rather than inventing a scope,
        so this error means you resolved through the wrong door, not that the
        binding is wrong.

    Contract:
        - Indicates a SpellSpace lifecycle or ownership violation rather than a
          generic runtime failure.
        - Message payload stays free-form so callers can name the exact rule
          that failed.
        - Subclasses `RuntimeError`, so broad runtime handlers still catch it.

    Registration:
        GUARDED, and exported. Present in `INTERNAL_MANIFEST`, so
        `Spellbook.bind(...)` refuses it. That restricts REGISTRATION only, never
        USE: import it, raise it, and catch it freely. Guarding and exporting are
        orthogonal - this type is on the public root surface AND unbindable.

    Subsystem Context:
        One of the 11 `utilities/custom_exceptions/` types, paired with the
        `Creations`/`SpellSpace` family in `aether/conduit/`. `SpellSpace`
        enforces active-scope semantics and supports reset/versioning; this is
        what it raises when that enforcement trips.

    System Context:
        Fires at meld time, in the resolution layer of the DGR. It is the one
        Existence mode whose scope the caller must open explicitly - the other
        five (`unique`, `unique_per_conduit`, `many`,
        `unique_per_conduit_cluster`, `unique_per_conduit_lineage`) resolve
        their container from state Melder already owns.
    """

    __ast_helper_access__: str = "public"
    __agent_purpose__: str = (
        "access: public. Raised when a unique_per_spell_space spell is resolved with no active "
        "SpellSpace, or a SpellSpace is used cross-conduit or after close; enter "
        "conduit.enter_spellspace() first."
    )

    def __init__(self, message: str) -> None:
        """
        Build a SpellSpace scope violation error.

        Args:
            message (str): Human-readable description of the violated scoping
                rule.

        Contract:
            - PASS-THROUGH constructor: it forwards the message unchanged and adds no
              fields. The type carries the meaning - a spellspace-scoped object was
              reached outside an active spellspace scope.

        Threading:
            Plain construction; no shared state.

        Lifecycle / Cleanup:
            None - it is an exception value.

        Returns:
            None.
        """
        super().__init__(message)
