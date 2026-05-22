import ulid



class IDBuilder:
    """
    Build stable lineage-style identifiers for runtime-owned objects.

    Contract:
        - IDs are always joined with dots ('.').
        - Each segment alternates between an object's ID and its class name.
        - `compose()` reads `_id` first and falls back to `id`.
        - Convenience helpers are thin aliases over `compose()` and preserve its
          error behavior.
    """

    @staticmethod
    def create_id() -> str:
        """
        Return a new ULID string suitable for one runtime lineage segment.

        Contract:
        - Produces a fresh globally sortable ULID string on each call.
        - Used for object identity, not for human-readable names.
        """
        return str(ulid.ULID())

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
        """
        return IDBuilder.compose(conduit, ward)
