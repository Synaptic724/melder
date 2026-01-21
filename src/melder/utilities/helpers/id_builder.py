import ulid

class IDBuilder:
    """
    Utility to build hierarchical ULID-based lineage IDs.

    Rules:
        - IDs are always joined with dots ('.').
        - Each segment alternates between an object's ID and its class name.
        - Never ends with a dot.
    """

    @staticmethod
    def create_id() -> str:
        """Generates a new ULID string."""
        return str(ulid.ULID())

    # ---------------------------------------------------------------------
    # Object-aware composition helpers
    # ---------------------------------------------------------------------

    @staticmethod
    def compose(base_obj: object, new_obj: object | None = None) -> str:
        """
        Composes a lineage ID using the base object's ID and class name,
        optionally extended with a new object's ID and class name.

        Args:
            base_obj (object): The parent object (must have `_id` or `id`).
            new_obj (object | None): Optional child object.

        Returns:
            str: A dot-joined lineage string without trailing dots.

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
        Builds a Conduit ID based on its parent Spellbook.

        Example:
            '01ABC...Spellbook.01DEF...Conduit'
        """
        return IDBuilder.compose(spellbook, conduit)

    @staticmethod
    def ward_id(conduit: object, ward: object) -> str:
        """
        Builds a ConduitWard ID based on its parent Conduit.

        Example:
            '01ABC...Conduit.01XYZ...ConduitWard'
        """
        return IDBuilder.compose(conduit, ward)
