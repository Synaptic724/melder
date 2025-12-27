class SpellbookValidationError(RuntimeError):
    """
    Raised when the Spellbook resolution pipeline (requirements → symbolic graph
    → local frame → validation) detects one or more **broken** spells.

    This is thrown from `_run_resolution_phases` after all phases have executed
    and per-spell validation has run, but **before** any Conduit is constructed.

    The error message includes a compact summary of all broken spells; callers
    may also inspect individual `Spell.validation_result` artifacts via the
    Spell's crafter for richer diagnostics.

    This exception now expands its message with Phase 4 and Phase 6 diagnostics
    (including strategy attribution) when those artifacts are available on the
    broken spells.

    Purpose:
        Surface spellbook-level validation failures in a readable error while
        preserving per-spell context for remediation.
    Contract:
        - Always includes a broken-spell summary when spells are supplied.
        - Includes Phase 4 issues and Phase 6 diagnostics when available.
        - Preserves the primary failure line for backward compatibility.
    """

    def __init__(self, broken_spells: list["Spell"]) -> None:
        """
        Purpose:
            Build a validation error with a readable diagnostic summary.
        Contract:
            - Always includes a broken-spell summary when spells are supplied.
            - Includes Phase 4 issues and Phase 6 diagnostics when available.
            - Remains resilient when spell attributes are missing or cleaned.
        Args:
            broken_spells: Spells marked as broken after validation.
        Returns:
            None.
        """
        self.broken_spells = broken_spells
        if not broken_spells:
            msg = "SpellbookValidationError raised with no broken spells."
            super().__init__(msg)
            return

        spell_contexts = []
        summary_parts = []
        for spell in broken_spells:
            try:
                spell_name = spell.spell_name
            except Exception:
                spell_name = "<unknown>"
            if not spell_name:
                spell_name = "<unknown>"
            try:
                spell_id = spell.spell_id
            except Exception:
                spell_id = "<?>"
            try:
                spell_frame = spell.spellframe
            except Exception:
                spell_frame = None

            summary_parts.append(
                f"{spell_name} (id={spell_id}, frame={spell_frame!r})"
            )
            spell_contexts.append(
                {
                    "spell": spell,
                    "spell_name": spell_name,
                    "spell_id": spell_id,
                    "spell_frame": spell_frame,
                }
            )

        summary = "; ".join(summary_parts)
        lines = [
            "Spellbook validation failed; one or more spells are broken. "
            f"Broken spells: {summary}",
            "Diagnostics:",
            "Phase 4 issues:",
        ]

        for context in spell_contexts:
            spell = context["spell"]
            header = (
                f"- Spell {context['spell_name']!r} "
                f"(id={context['spell_id']}, frame={context['spell_frame']!r}):"
            )
            lines.append(header)

            phase4_result = None
            try:
                phase4_result = spell.validation_result_phase4
            except Exception:
                phase4_result = None

            phase4_issues = []
            if phase4_result is not None:
                try:
                    phase4_issues = list(phase4_result.issues)
                except Exception:
                    phase4_issues = []
                if not phase4_issues:
                    errors = []
                    warnings = []
                    try:
                        errors = list(phase4_result.errors)
                    except Exception:
                        errors = []
                    try:
                        warnings = list(phase4_result.warnings)
                    except Exception:
                        warnings = []
                    phase4_issues = errors + warnings

            if not phase4_issues:
                lines.append("    (none recorded)")
            else:
                for issue in phase4_issues:
                    try:
                        severity = issue.severity
                    except Exception:
                        severity = "unknown"
                    try:
                        code = issue.code
                    except Exception:
                        code = "UNKNOWN_ISSUE"
                    try:
                        message = issue.message
                    except Exception:
                        message = repr(issue)
                    try:
                        source = issue.source
                    except Exception:
                        source = None
                    try:
                        details = issue.details
                    except Exception:
                        details = None

                    source_part = f" (source={source})" if source else ""
                    lines.append(
                        f"    - [{severity}] {code}{source_part}: {message}"
                    )
                    if details:
                        lines.append(f"      details: {details!r}")

        lines.append("Phase 6 diagnostics:")
        phase6_diagnostics = []
        seen_diag_ids = set()
        for context in spell_contexts:
            spell = context["spell"]
            phase6_state = None
            try:
                phase6_state = spell.validation_result_phase6
            except Exception:
                phase6_state = None

            if phase6_state is None:
                continue

            try:
                phase6_errors = list(phase6_state.errors)
            except Exception:
                phase6_errors = []
            try:
                phase6_warnings = list(phase6_state.warnings)
            except Exception:
                phase6_warnings = []

            for diag in phase6_errors + phase6_warnings:
                diag_id = id(diag)
                if diag_id in seen_diag_ids:
                    continue
                seen_diag_ids.add(diag_id)
                phase6_diagnostics.append(diag)

        if not phase6_diagnostics:
            lines.append("  (none recorded)")
        else:
            for diag in phase6_diagnostics:
                try:
                    severity_value = diag.severity
                except Exception:
                    severity_value = None

                if severity_value is None:
                    severity = "unknown"
                else:
                    try:
                        severity = severity_value.name.lower()
                    except Exception:
                        severity = str(severity_value).lower()

                try:
                    code = diag.code
                except Exception:
                    code = "UNKNOWN_DIAGNOSTIC"
                try:
                    message = diag.message
                except Exception:
                    message = repr(diag)
                try:
                    source = diag.source
                except Exception:
                    source = None
                try:
                    spell_id = diag.spell_id
                except Exception:
                    spell_id = None
                try:
                    root_id = diag.root_id
                except Exception:
                    root_id = None
                try:
                    details = diag.details
                except Exception:
                    details = None

                meta_parts = []
                if source:
                    meta_parts.append(f"source={source}")
                if spell_id:
                    meta_parts.append(f"spell_id={spell_id}")
                if root_id:
                    meta_parts.append(f"root_id={root_id}")
                meta = f" ({', '.join(meta_parts)})" if meta_parts else ""

                lines.append(f"  - [{severity}] {code}{meta}: {message}")
                if details:
                    lines.append(f"    details: {details!r}")

        msg = "\n".join(lines)
        super().__init__(msg)
