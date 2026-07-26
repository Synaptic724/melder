from melder.utilities.helpers.ulid_factory import new_ulid



class IDBuilder:
    """

    Purpose:
        Build stable lineage-style identifiers for runtime-owned objects, so
        every id in the system is composed one way instead of each call site
        inventing its own string format.

    Responsibilities:
        - Mint fresh ULID segments for new object identities.
        - Compose dotted lineage ids from an object chain.
        - Provide the named conduit / ward id shapes the runtime relies on.

    Contract:
        - IDs are always joined with dots ('.').
        - Each segment alternates between an object's ID and its class name.
        - `compose()` reads `_id` first and falls back to `id`.
        - Convenience helpers are thin aliases over `compose()` and preserve its
          error behavior.

    Why ULIDs, and what that costs:
        `create_id()` returns a ULID, which is lexicographically sortable by
        creation time. That sortability is used elsewhere in the system as a
        cheap chronological ordering. It is NOT monotonic within a single
        millisecond, so two ids minted in the same tick can sort in either
        order - anywhere true ordering matters, use a recorded sequence rather
        than comparing ids.

    Owned State:
        None. Every method is a static helper; the class is a namespace, not an
        object with a lifetime.

    Threading:
        Stateless and therefore thread-safe. ULID minting carries no shared
        counter that could contend.

    Lifecycle / Cleanup:
        No instances and no cleanup contract. Deliberately not `Cleanable` -
        there is nothing to release.

    Registration:
        MELDER KERNEL - guarded. Identity composition is a runtime concern; a
        user calls these helpers directly rather than registering the namespace.

    Subsystem Context:
        One of the `utilities/helpers/` static namespaces alongside
        `SpellInputUtils` (key normalization), `EnumHelpers` (enum coercion),
        and `InitHelpers` (logger resolution). This one owns identity FORMAT;
        `SpellInputUtils` owns lookup-key format. They are deliberately separate
        because an id names one object while a key addresses a binding.

    System Context:
        Identity flows from here into essentially every runtime object -
        conduits, wards, and the lineage strings the control plane keys its
        registries on. Because those ids appear in change-control scope keys and
        transaction claims, the dotted format is effectively part of the
        system's wire contract even though it is only a string.

    AGENT_ACCESS: public

    AGENT_PURPOSE:
        access: public. Static namespace for building dotted lineage ids. create_id() mints a
        fresh ULID segment; compose() and the conduit/ward helpers join an object chain into the
        canonical dotted form. Stateless - call the methods directly, never instantiate.
    """


    @staticmethod
    def create_id() -> str:
        """
        Return a new ULID string suitable for one runtime lineage segment.

        Contract:
        - Produces a fresh globally sortable ULID string on each call.
        - Used for object identity, not for human-readable names.

        Returns:
            str: A fresh ULID segment. Lexicographic order matches creation order.
        """
        return new_ulid()

    # ---------------------------------------------------------------------
    # Object-aware composition helpers
    # ---------------------------------------------------------------------

    @staticmethod
    def compose(base_obj: object, new_obj: object | None = None) -> str:
        """
        Compose a lineage ID from one or two objects.

        Args:
            base_obj (object): Object that contributes the first identifier/class
                pair. The helper reads `_id` first and falls back to `id`.
            new_obj (object | None): Optional second object appended with the
                same identifier lookup rule.

        Returns:
            str: A dot-joined lineage string without trailing dots.

        Raises:
            AttributeError: If either object does not expose `_id` or `id`.

        Example:
            Spellbook._id = '01ABC...'
            Conduit._id = '01DEF...'
            => '01ABC...Spellbook.01DEF...Conduit'
        """
        base_id = getattr(base_obj, "_id", getattr(base_obj, "id", None))
        if base_id is None:
            raise AttributeError(f"{base_obj.__class__.__name__} missing required '_id' or 'id' attribute")

        segments = [base_id, base_obj.__class__.__name__]

        if new_obj is not None:
            new_id = getattr(new_obj, "_id", getattr(new_obj, "id", None))
            if new_id is None:
                raise AttributeError(f"{new_obj.__class__.__name__} missing required '_id' or 'id' attribute")
            segments.extend([new_id, new_obj.__class__.__name__])

        return ".".join(segments)

    # ---------------------------------------------------------------------
    # Convenience aliases for specific relationships
    # ---------------------------------------------------------------------

    @staticmethod
    def conduit_id(spellbook: object, conduit: object) -> str:
        """
        Build the lineage ID for a conduit owned by a spellbook.

        Contract:
        - Thin alias over `compose(...)`.
        - Preserves the same identifier lookup and `AttributeError` behavior as
          the underlying composition helper.

        Example:
            '01ABC...Spellbook.01DEF...Conduit'

        Returns:
            str: A dotted conduit lineage id built from the supplied parts.

        Args:
            parts:
                Lineage segments joined into a dotted conduit id.
        """
        return IDBuilder.compose(spellbook, conduit)

    @staticmethod
    def ward_id(conduit: object, ward: object) -> str:
        """
        Build the lineage ID for a ward owned by a conduit.

        Contract:
        - Thin alias over `compose(...)`.
        - Preserves the same identifier lookup and `AttributeError` behavior as
          the underlying composition helper.

        Example:
            '01ABC...Conduit.01XYZ...ConduitWard'

        Returns:
            str: A dotted ward lineage id built from the supplied parts.

        Args:
            parts:
                Lineage segments joined into a dotted ward id.
        """
        return IDBuilder.compose(conduit, ward)
