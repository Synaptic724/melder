class SpellbookValidationError(RuntimeError):
    """
    Raised when the Spellbook resolution pipeline (requirements → symbolic graph
    → local frame → validation) detects one or more **broken** spells.

    This is thrown from `_run_resolution_phases` after all phases have executed
    and per-spell validation has run, but **before** any Conduit is constructed.

    The error message includes a compact summary of all broken spells; callers
    may also inspect individual `Spell.validation_result` artifacts via the
    Spell's crafter for richer diagnostics.
    """

    def __init__(self, broken_spells: list["Spell"]) -> None:
        if not broken_spells:
            msg = "SpellbookValidationError raised with no broken spells."
        else:
            summary_parts = []
            for spell in broken_spells:
                try:
                    summary_parts.append(
                        f"{spell.spell_name} (id={spell.spell_id}, frame={spell.spellframe!r})"
                    )
                except Exception:
                    # Extremely defensive; we never want __str__ of the exception
                    # to blow up because a spell is half-constructed.
                    summary_parts.append(f"<spell id={getattr(spell, 'spell_id', '<?>')}>")

            summary = "; ".join(summary_parts)
            msg = (
                "Spellbook validation failed; one or more spells are broken. "
                f"Broken spells: {summary}"
            )

        super().__init__(msg)
        self.broken_spells = broken_spells
