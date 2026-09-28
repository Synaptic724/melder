from typing import TYPE_CHECKING, Any, ClassVar, Dict, FrozenSet, List, Optional, Sequence, Tuple



if TYPE_CHECKING:
    from melder.aether.spellbook.spell import Spell
    from melder.aether.spellbook.spell_compiler.system.system_diagnostic import SystemDiagnostic

class SpellbookValidationError(RuntimeError):
    """
    Raised when the Spellbook pipeline finds spells it cannot build.

    Conjure raises it after the structural phases (1-4) when a spell failed
    validation, and after the resolution phases when the conduit verdict holds
    an error; meld raises it when a spell's validity is invalid, gated or
    disabled after a lazy re-validation. No Conduit is constructed first.

    Purpose:
        Tell a user which spells failed, why, and how to fix it, in plain words
        and by name, while keeping the spell objects for tooling.

    Raised When:
        - `conjure(...)` completes phases 1-4 and one or more spells are broken.
          This is the common case: the pipeline ran, validation rejected the
          graph, and no Conduit is produced.
        - `conjure(...)` resolves the conduit and the verdict carries an error
          (for example a scope-ordering violation or a dependency cycle).
        - `meld(...)` finds a spell whose validity is invalid, gated, or
          disabled, including after a lazy re-validation attempt under the
          per-spell lock.

    What To Do About It:
        Read the lines under each spell: every error names the parameter or the
        dependency at fault and says what to change. Errors marked `[internal]`
        come from Melder's own consistency checks and are Melder bugs; report
        them with the message. Warnings never block conjure and are only
        counted here; `conjure(validation_warnings=True)` logs them. Fix the
        binding, not the validator.

    Message shape (2026-09-26):
        - First line: "Spellbook validation failed. Broken spells: A, B." (the
          two substrings of earlier releases are kept for matchers).
        - One block per spell with errors, "Name (frame 'x'):", each error as
          "  - <message> [CODE]"; errors that belong to no spell under
          "Whole-graph errors:".
        - Exact duplicates are dropped; BINDING_RESOLUTION_CYCLE is hidden when
          CIRCULAR_DEPENDENCY is reported for the same spell, and CIRCULAR_DEPENDENCY
          when SELF_DEPENDENCY is (a spell that depends on itself); root_not_viable and
          broken_spell_in_dag are hidden when any other error is shown.
        - Footers count the hidden warnings and explain `[internal]`.

    Contract:
        - Always names the broken spells when spells are supplied.
        - Shows every recorded error reason: Phase 4 issues and Phase 6 errors
          on the spells, plus the conduit diagnostics handed in through
          `system_diagnostics`.
        - Never lists warnings, strategy sources or details payloads.
        - Remains resilient when spell artifacts are partially unavailable or
          cleaned while the error is being rendered. Rendering a diagnostic must
          never raise a second error on top of the first.
        - The message is built once, at construction; the diagnostics handed in
          are read then and not retained.

    Registration:
        Exported on the public root surface; import, raise, and catch freely.

    Subsystem Context:
        One of the 11 `utilities/custom_exceptions/` types and the primary error
        of the Spellbook binding surface. Where the scheduler family
        (`PhaseExecutionError`, `PhaseTimeoutError`) reports mechanical pipeline
        failure, this reports SEMANTIC failure: the phases ran fine and the
        graph they produced is not resolvable.

    System Context:
        The main build-time error of the DGR. It fires before any Conduit is
        constructed, so nothing has been registered into Aether and there is no
        partial world to clean up. Its runtime counterpart is
        `MeldExecutionError`; between them they split "your graph cannot be
        built" from "your resolution failed while running".

    AGENT_ACCESS: public

    AGENT_PURPOSE:
        access: public. The build-time 'your graph is broken' error from conjure/meld; the
        message lists each broken spell's errors by name with a fix, plus whole-graph errors.
        Fix the binding, not the validator.
    """

    # Codes whose checks guard Melder's own bookkeeping (index, blueprint, socket
    # references, bind metadata, Phase 1's own decision). A user cannot cause or
    # fix them through bindings, so they render as internal errors to report.
    INTERNAL_CODES: ClassVar[FrozenSet[str]] = frozenset({
        "CALLABLE_PROFILE_MISSING",
        "CLASS_PROFILE_MISSING",
        "DI_BUILTIN_ANNOTATION",
        "DI_COLLECTION_MISSING_ELEMENT",
        "DI_COLLECTION_NON_FRAME",
        "DI_MISSING_ANNOTATION",
        "EXISTING_CREATION_PROFILE_MISMATCH",
        "MISSING_BINDING_PROFILE",
        "MISSING_RESOLUTION_FRAME",
        "NON_CALLABLE_SPELL_TARGET",
        "NON_CLASS_SPELL_TARGET",
        "SPELLMAP_DEFAULT_MISSING",
        "SPELL_CONTRACT_INVALID",
        "contract_key_missing",
        "dag_orphan_node",
        "edge_mismatch_index",
        "edge_missing_from_blueprint",
        "identity_mixing_detected",
        "index_node_missing_from_blueprints",
        "lineage_conduit_conflict",
        "missing_index_dependency",
        "missing_index_node",
        "missing_phase4_validation",
        "missing_root_blueprint",
        "root_lineage_conflict",
        "root_lineage_mismatch",
        "root_missing_in_dag",
        "root_missing_in_index",
        "root_not_marked_in_index",
        "topology_dependency_mismatch",
    })

    # Codes that only restate another error; hidden whenever any other error is shown.
    RESTATING_CODES: ClassVar[FrozenSet[str]] = frozenset({"root_not_viable", "broken_spell_in_dag"})

    # Code -> code that reports the same fault more readably for the same spell.
    SUPERSEDED_BY: ClassVar[Dict[str, str]] = {
        "BINDING_RESOLUTION_CYCLE": "CIRCULAR_DEPENDENCY",
        "CIRCULAR_DEPENDENCY": "SELF_DEPENDENCY",
    }

    def __init__(
            self,
            broken_spells: list[Spell],
            *,
            system_diagnostics: Optional[Sequence[SystemDiagnostic]] = None,
    ) -> None:
        """
        Purpose:
            Build a validation error whose message explains every recorded failure.
        Contract:
            - Keeps `broken_spells` exactly as supplied (tooling reads the spells).
            - Renders the message once from the spells' Phase 4/6 results and the
              ERROR entries of `system_diagnostics`; WARNING diagnostics are ignored.
            - Remains resilient when spell or diagnostic attributes are missing or
              cleaned; a failed read degrades that field only.
        Args:
            broken_spells: Spells refused by validation (may be empty).
            system_diagnostics: Optional conduit resolution diagnostics that explain
                the refusal (the conjure and local-rerun gates pass them).
        Returns:
            None.
        """
        self.broken_spells = broken_spells
        if not broken_spells and not system_diagnostics:
            super().__init__("SpellbookValidationError raised with no broken spells.")
            return
        super().__init__(self._render(broken_spells, system_diagnostics or ()))

    @classmethod
    def _render(
            cls,
            broken_spells: Sequence[Spell],
            system_diagnostics: Sequence[SystemDiagnostic],
    ) -> str:
        """
        Purpose:
            Compose the full message from spell blocks, whole-graph errors and footers.
        Contract:
            - Lists a spell only when it has an error, except when no diagnostics were
              handed in (meld paths), where a spell without one is still named.
            - Applies the dedupe, superseded and restating rules of the class docstring.
        Args:
            broken_spells: Spells supplied to the error.
            system_diagnostics: Conduit diagnostics supplied to the error.
        Returns:
            str: The rendered message.
        """
        blocks: List[Tuple[str, str, List[Tuple[str, str]]]] = []
        block_by_id: Dict[str, List[Tuple[str, str]]] = {}
        warning_count = 0
        for spell in broken_spells:
            errors, warnings = cls._spell_errors(spell)
            warning_count += warnings
            name = cls._read_text(spell, "spell_name") or "<unknown spell>"
            blocks.append((name, cls._spell_label(spell, name), errors))
            spell_id = cls._read_text(spell, "spell_id")
            if spell_id is not None:
                block_by_id.setdefault(spell_id, errors)
        graph_errors: List[Tuple[str, str]] = []
        for diagnostic in system_diagnostics:
            entry = cls._diagnostic_error(diagnostic)
            if entry is None:
                continue
            owner = block_by_id.get(entry[2]) if entry[2] is not None else None
            (owner if owner is not None else graph_errors).append((entry[0], entry[1]))
        return cls._compose(blocks, graph_errors, warning_count, bool(system_diagnostics))

    @classmethod
    def _compose(
            cls,
            blocks: List[Tuple[str, str, List[Tuple[str, str]]]],
            graph_errors: List[Tuple[str, str]],
            warning_count: int,
            diagnostics_given: bool,
    ) -> str:
        """
        Purpose:
            Turn collected (code, message) errors into the final text.
        Contract:
            - Filters each block, then drops restating codes when anything else remains.
            - Emits header, spell blocks, whole-graph block and footers in that order.
        Args:
            blocks: (spell name, block label, errors) per supplied spell, in supply order.
            graph_errors: Errors attributed to no supplied spell.
            warning_count: Phase-4 warnings seen on the supplied spells.
            diagnostics_given: Whether conduit diagnostics were handed in.
        Returns:
            str: The rendered message.
        """
        filtered = [(name, label, cls._filter(errors)) for name, label, errors in blocks]
        graph = cls._filter(graph_errors)
        all_codes = [code for _, _, errors in filtered for code, _ in errors] + [code for code, _ in graph]
        if any(code not in cls.RESTATING_CODES for code in all_codes):
            filtered = [
                (name, label, [e for e in errors if e[0] not in cls.RESTATING_CODES])
                for name, label, errors in filtered
            ]
            graph = [e for e in graph if e[0] not in cls.RESTATING_CODES]
        shown = [(name, label, errors) for name, label, errors in filtered if errors or not diagnostics_given]
        names = ", ".join(name for name, _, _ in shown)
        lines = [f"Spellbook validation failed. Broken spells: {names}." if names
                 else "Spellbook validation failed. The dependency graph has errors."]
        has_internal = False
        for _, label, errors in shown:
            lines.append(f"{label}:")
            if not errors:
                lines.append("  - No validation error was recorded for this spell; its validity is "
                             "invalid, gated or disabled.")
            for code, message in errors:
                has_internal = has_internal or code in cls.INTERNAL_CODES
                lines.append(cls._error_line(code, message))
        if graph:
            lines.append("Whole-graph errors:")
            for code, message in graph:
                has_internal = has_internal or code in cls.INTERNAL_CODES
                lines.append(cls._error_line(code, message))
        if warning_count:
            plural = "warning" if warning_count == 1 else "warnings"
            lines.append(f"{warning_count} {plural} not shown (warnings never block conjure); "
                         "conjure(validation_warnings=True) logs them.")
        if has_internal:
            lines.append("Errors marked [internal] come from Melder's own consistency checks: they are "
                         "Melder bugs, not problems in your code. Please report them with this message.")
        return "\n".join(lines)

    @classmethod
    def _filter(cls, errors: List[Tuple[str, str]]) -> List[Tuple[str, str]]:
        """
        Purpose:
            Drop exact duplicates, superseded codes and repeated internal codes.
        Contract:
            - Keeps first-seen order; an internal code appears once per block.
        Args:
            errors: (code, message) pairs of one block.
        Returns:
            List[Tuple[str, str]]: The pairs to show.
        """
        codes = {code for code, _ in errors}
        seen: set[Tuple[str, str]] = set()
        seen_internal: set[str] = set()
        kept: List[Tuple[str, str]] = []
        for code, message in errors:
            if cls.SUPERSEDED_BY.get(code) in codes or (code, message) in seen:
                continue
            if code in cls.INTERNAL_CODES:
                if code in seen_internal:
                    continue
                seen_internal.add(code)
            seen.add((code, message))
            kept.append((code, message))
        return kept

    @classmethod
    def _error_line(cls, code: str, message: str) -> str:
        """
        Purpose:
            Format one error line, marking internal codes.
        Args:
            code: Issue or diagnostic code.
            message: Human-readable message.
        Returns:
            str: "  - <message> [CODE]" or "  - [internal] <message> [CODE]".
        """
        marker = "[internal] " if code in cls.INTERNAL_CODES else ""
        return f"  - {marker}{message} [{code}]"

    @classmethod
    def _spell_errors(cls, spell: Any) -> Tuple[List[Tuple[str, str]], int]:
        """
        Purpose:
            Collect a spell's error (code, message) pairs and count its Phase-4 warnings.
        Contract:
            - Phase 4: `validation_result_phase4.issues`, falling back to `.errors` plus
              `.warnings` when `issues` is unreadable or empty.
            - Phase 6: `validation_result_phase6.errors` (warnings ignored).
            - Any unreadable part is skipped; never raises.
        Args:
            spell: A Spell (or a stand-in exposing the same attributes).
        Returns:
            Tuple[List[Tuple[str, str]], int]: Errors in order, and the warning count.
        """
        errors: List[Tuple[str, str]] = []
        warnings = 0
        for issue in cls._phase4_issues(spell):
            severity = cls._read_text(issue, "severity")
            code = cls._read_text(issue, "code") or "UNKNOWN_ISSUE"
            if severity == "error":
                errors.append((code, cls._read_text(issue, "message") or repr(issue)))
            elif severity == "warning":
                warnings += 1
        for diagnostic in cls._read_list(cls._read_attr(spell, "validation_result_phase6"), "errors"):
            entry = cls._diagnostic_error(diagnostic)
            if entry is not None:
                errors.append((entry[0], entry[1]))
        return errors, warnings

    @classmethod
    def _phase4_issues(cls, spell: Any) -> List[Any]:
        """
        Purpose:
            Read a spell's Phase-4 issues with the documented fallback.
        Args:
            spell: A Spell (or stand-in).
        Returns:
            List[Any]: The issues, possibly empty.
        """
        result = cls._read_attr(spell, "validation_result_phase4")
        if result is None:
            return []
        issues = cls._read_list(result, "issues")
        if issues:
            return issues
        return cls._read_list(result, "errors") + cls._read_list(result, "warnings")

    @classmethod
    def _diagnostic_error(cls, diagnostic: Any) -> Optional[Tuple[str, str, Optional[str]]]:
        """
        Purpose:
            Read an ERROR system diagnostic as (code, message, spell_id).
        Contract:
            - Returns None for WARNING diagnostics and for unreadable severities.
        Args:
            diagnostic: A SystemDiagnostic (or stand-in).
        Returns:
            Optional[Tuple[str, str, Optional[str]]]: The entry, or None.
        """
        severity = cls._read_attr(diagnostic, "severity")
        try:
            severity_name = severity.name
        except AttributeError:
            severity_name = str(severity).upper() if severity is not None else ""
        if severity_name != "ERROR":
            return None
        code = cls._read_text(diagnostic, "code") or "UNKNOWN_DIAGNOSTIC"
        message = cls._read_text(diagnostic, "message") or repr(diagnostic)
        return code, message, cls._read_text(diagnostic, "spell_id")

    @classmethod
    def _spell_label(cls, spell: Any, name: str) -> str:
        """
        Purpose:
            Label a spell for its block header: "Name (frame 'x')", frame omitted when None.
        Args:
            spell: A Spell (or stand-in).
            name: The spell's display name, already read.
        Returns:
            str: The label.
        """
        frame = cls._read_attr(spell, "spellframe")
        if frame is None:
            return name
        if isinstance(frame, str):
            return f"{name} (frame {frame!r})"
        try:
            frame_text = frame.__qualname__
        except AttributeError:
            frame_text = repr(frame)
        return f"{name} (frame {frame_text})"

    @staticmethod
    def _read_attr(owner: Any, name: str) -> Any:
        """
        Purpose:
            Read one attribute of a spell, result or diagnostic without letting a
            cleaned or partial object raise into the error being built.
        Contract:
            - The object shapes are external to this renderer (live spells, results,
              diagnostics or test stand-ins, possibly cleaned), so the name is dynamic
              and any failure returns None.
        Args:
            owner: Object to read from (None allowed).
            name: Attribute name.
        Returns:
            Any: The value, or None.
        """
        if owner is None:
            return None
        try:
            return getattr(owner, name)
        except Exception:
            # Best-effort diagnostics: a failed read degrades one field only.
            return None

    @classmethod
    def _read_text(cls, owner: Any, name: str) -> Optional[str]:
        """
        Purpose:
            Read one attribute as text.
        Args:
            owner: Object to read from.
            name: Attribute name.
        Returns:
            Optional[str]: `str(value)`, or None when unreadable or None.
        """
        value = cls._read_attr(owner, name)
        return None if value is None else str(value)

    @classmethod
    def _read_list(cls, owner: Any, name: str) -> List[Any]:
        """
        Purpose:
            Read one iterable attribute as a list.
        Args:
            owner: Object to read from.
            name: Attribute name.
        Returns:
            List[Any]: The items, or an empty list when unreadable.
        """
        value = cls._read_attr(owner, name)
        if value is None:
            return []
        try:
            return list(value)
        except TypeError:
            return []
