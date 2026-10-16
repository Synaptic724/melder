"""Rule 2 / D1-B source change: Phase 4's contract check walks snapshots and names a lost contract (melder_1).

ContractProviderPresenceStrategy walks one-call snapshots of the Book's contracted maps and gives the missing-provider
warning its remedy; SpellbookValidationError lists a gating warning as a spell's reason.
contract_recheck_on_notch_2026_10_16, component_patch_contract_presence_report.
usage: python <this script> <tree root> [--check]
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from apply_lib import apply

ROOT = pathlib.Path(sys.argv[1])
CHECK = "--check" in sys.argv[2:]
STRATEGY = "src/melder/aether/spellbook/spell_compiler/validation/strategies/contract_provider_presence_strategy.py"
ERROR = "src/melder/utilities/custom_exceptions/spellbook_validation_error.py"

STRATEGY_STEPS = [
    ("one",
     '''        - Emits warnings for missing SpellContract providers in dynamic mode.
''',
     '''        - Emits warnings for missing SpellContract providers in dynamic mode. The
          warning names the contract and the remedy (D1-B, 2026-10-16): it is the
          one warning Phase 4 gates a lineage on, so SpellbookValidationError
          lists it as the reason a consumer is refused.
        - Walks one-call snapshots of the Book's contracted maps, built once per
          validation pass. Under rule 2 (2026-10-16) this check is the recheck a
          consumer's next meld runs after its provider changed, so it can meet
          the rest of that change still writing the maps under the Book lock.
''', ""),
    ("one",
     '''            - Uses the Spellbook's contracted spell maps when available to enumerate providers.
''',
     '''            - Uses the Spellbook's contracted spell maps when available to enumerate providers,
              walking one-call snapshots of them (no Book lock is held here; a provider
              change writes them under it).
''', ""),
    ("one",
     '''            if spellbook is not None:
                for contracted in spellbook._contracted_spells.values():
                    for index, provider_spell in contracted.items():
''',
     '''            if spellbook is not None:
                # One-call snapshots (exact under concurrent writers on 3.14t): the
                # mutators write these maps under the Book lock, which this pass does
                # not hold, and a recheck can run while a notch is still writing them.
                for contracted in list(spellbook._contracted_spells.values()):
                    for index, provider_spell in list(contracted.items()):
''', ""),
    ("one",
     '''                if not providers:
                    context.issues.append(
                        SpellValidationIssue(
                            severity="warning",
                            code="SPELL_CONTRACT_MISSING_PROVIDER",
                            message=(
                                f"Spell {spell.spell_name!r} parameter {param.name!r} "
                                f"has no provider for contract key {contract_key}."
                            ),
''',
     '''                if not providers:
                    frame_key, binding_key = contract_key
                    context.issues.append(
                        SpellValidationIssue(
                            severity="warning",
                            code="SPELL_CONTRACT_MISSING_PROVIDER",
                            message=(
                                f"Spell {spell.spell_name!r} parameter {param.name!r} has no provider "
                                f"for its SpellContract (frame_key={frame_key!r}, binding_key={binding_key!r}): "
                                "no active spell with that frame and binding name is contracted to this "
                                "Spellbook. Contract one from a linked conduit (add_index_to_contract, or "
                                "add_spell_to_contract for one version) and meld again."
                            ),
''', ""),
]

ERROR_STEPS = [
    ("one",
     '''        them with the message. Warnings never block conjure and are only
        counted here; `conjure(validation_warnings=True)` logs them. Fix the
        binding, not the validator.
''',
     '''        them with the message. Warnings never block conjure and are only
        counted here, except one that holds a spell's lineage gated (a lost
        SpellContract provider at meld): it is listed as that spell's reason,
        with its remedy. `conjure(validation_warnings=True)` logs the others.
        Fix the binding, not the validator.
''', ""),
    ("one",
     '''        - Footers count the hidden warnings and explain `[internal]`.
''',
     '''        - A spell with no error that a Phase-4 warning holds gated
          (`GATING_WARNING_CODES`, a lost SpellContract provider) lists that
          warning as its reason, "  - <message> [CODE]", instead of saying no
          error was recorded (D1-B, 2026-10-16).
        - Footers count the hidden warnings and explain `[internal]`.
''', ""),
    ("one",
     '''        - Never lists warnings, strategy sources or details payloads.
''',
     '''        - Never lists warnings, strategy sources or details payloads, except the
          gating warnings of a spell that shows no error: they are why its
          lineage is gated, so they are its reason (2026-10-16).
''', ""),
    ("one",
     '''    SUPERSEDED_BY: ClassVar[Dict[str, str]] = {
        "BINDING_RESOLUTION_CYCLE": "CIRCULAR_DEPENDENCY",
        "CIRCULAR_DEPENDENCY": "SELF_DEPENDENCY",
    }
''',
     '''    SUPERSEDED_BY: ClassVar[Dict[str, str]] = {
        "BINDING_RESOLUTION_CYCLE": "CIRCULAR_DEPENDENCY",
        "CIRCULAR_DEPENDENCY": "SELF_DEPENDENCY",
    }

    # Phase-4 warnings that hold a lineage `gated` (`CompilerPhase4.run`): a spell refused only because of one lists
    # it as its reason instead of "No validation error was recorded" (D1-B, 2026-10-16). A unit test pins this set
    # to the codes Phase 4 gates on.
    GATING_WARNING_CODES: ClassVar[FrozenSet[str]] = frozenset({"SPELL_CONTRACT_MISSING_PROVIDER"})
''', ""),
    ("one",
     '''        Contract:
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
''',
     '''        Contract:
            - Lists a spell when it has an error or a gating warning, and, when no
              diagnostics were handed in (meld paths), a spell with neither too.
            - Applies the dedupe, superseded and restating rules of the class docstring.
        Args:
            broken_spells: Spells supplied to the error.
            system_diagnostics: Conduit diagnostics supplied to the error.
        Returns:
            str: The rendered message.
        """
        blocks: List[Tuple[str, str, List[Tuple[str, str]], List[Tuple[str, str]]]] = []
        block_by_id: Dict[str, List[Tuple[str, str]]] = {}
        warning_count = 0
        for spell in broken_spells:
            errors, gating, warnings = cls._spell_errors(spell)
            warning_count += warnings
            name = cls._read_text(spell, "spell_name") or "<unknown spell>"
            blocks.append((name, cls._spell_label(spell, name), errors, gating))
''', ""),
    ("one",
     '''    def _compose(
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
''',
     '''    def _compose(
            cls,
            blocks: List[Tuple[str, str, List[Tuple[str, str]], List[Tuple[str, str]]]],
            graph_errors: List[Tuple[str, str]],
            warning_count: int,
            diagnostics_given: bool,
    ) -> str:
        """
        Purpose:
            Turn collected (code, message) errors and gating warnings into the final text.
        Contract:
            - Filters each block, then drops restating codes when anything else remains;
              a gating warning counts as something else (it is shown as a reason).
            - A block whose filtered errors are empty and whose gating warnings are not
              lists those warnings as its reasons ("  - <message> [CODE]", never marked
              internal); a block that shows errors counts its gating warnings with the
              hidden ones.
            - A block is shown when it has errors or gating warnings, or when no
              diagnostics were handed in, where it says no error was recorded.
            - Emits header, spell blocks, whole-graph block and footers in that order.
        Args:
            blocks: (spell name, block label, errors, gating warnings) per supplied
                spell, in supply order.
            graph_errors: Errors attributed to no supplied spell.
            warning_count: Phase-4 warnings seen on the supplied spells, gating
                warnings not included.
            diagnostics_given: Whether conduit diagnostics were handed in.
        Returns:
            str: The rendered message.
        """
        filtered = [
            (name, label, cls._filter(errors), cls._filter(gating)) for name, label, errors, gating in blocks
        ]
        graph = cls._filter(graph_errors)
        all_codes = [code for _, _, errors, gating in filtered for code, _ in errors + gating]
        all_codes += [code for code, _ in graph]
        if any(code not in cls.RESTATING_CODES for code in all_codes):
            filtered = [
                (name, label, [e for e in errors if e[0] not in cls.RESTATING_CODES], gating)
                for name, label, errors, gating in filtered
            ]
            graph = [e for e in graph if e[0] not in cls.RESTATING_CODES]
        shown: List[Tuple[str, List[Tuple[str, str]], List[Tuple[str, str]]]] = []
        names_shown: List[str] = []
        for name, label, errors, gating in filtered:
            if errors:
                # The errors are the reason; a gating warning beside them is only counted.
                warning_count += len(gating)
                shown.append((label, errors, []))
                names_shown.append(name)
            elif gating or not diagnostics_given:
                shown.append((label, [], gating))
                names_shown.append(name)
        names = ", ".join(names_shown)
        lines = [f"Spellbook validation failed. Broken spells: {names}." if names
                 else "Spellbook validation failed. The dependency graph has errors."]
        has_internal = False
        for label, errors, gating in shown:
            lines.append(f"{label}:")
            for code, message in gating:
                lines.append(f"  - {message} [{code}]")
            if not errors and not gating:
                lines.append("  - No validation error was recorded for this spell; its validity is "
                             "invalid, gated or disabled.")
''', ""),
    ("one",
     '''    def _spell_errors(cls, spell: Any) -> Tuple[List[Tuple[str, str]], int]:
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
''',
     '''    def _spell_errors(cls, spell: Any) -> Tuple[List[Tuple[str, str]], List[Tuple[str, str]], int]:
        """
        Purpose:
            Collect a spell's error (code, message) pairs and its gating warnings, and
            count its other Phase-4 warnings.
        Contract:
            - Phase 4: `validation_result_phase4.issues`, falling back to `.errors` plus
              `.warnings` when `issues` is unreadable or empty. An error is collected; a
              warning whose code is in `GATING_WARNING_CODES` is collected as a gating
              warning, in issue order; any other warning is only counted.
            - Phase 6: `validation_result_phase6.errors` (warnings ignored).
            - Any unreadable part is skipped; never raises.
        Args:
            spell: A Spell (or a stand-in exposing the same attributes).
        Returns:
            Tuple[List[Tuple[str, str]], List[Tuple[str, str]], int]: Errors in order,
                gating warnings in order, and the count of the other warnings.
        """
        errors: List[Tuple[str, str]] = []
        gating: List[Tuple[str, str]] = []
        warnings = 0
        for issue in cls._phase4_issues(spell):
            severity = cls._read_text(issue, "severity")
            code = cls._read_text(issue, "code") or "UNKNOWN_ISSUE"
            if severity == "error":
                errors.append((code, cls._read_text(issue, "message") or repr(issue)))
            elif severity == "warning":
                if code in cls.GATING_WARNING_CODES:
                    gating.append((code, cls._read_text(issue, "message") or repr(issue)))
                else:
                    warnings += 1
        for diagnostic in cls._read_list(cls._read_attr(spell, "validation_result_phase6"), "errors"):
            entry = cls._diagnostic_error(diagnostic)
            if entry is not None:
                errors.append((entry[0], entry[1]))
        return errors, gating, warnings
''', ""),
]

apply(ROOT, STRATEGY, STRATEGY_STEPS, CHECK)
apply(ROOT, ERROR, ERROR_STEPS, CHECK)
