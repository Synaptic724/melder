"""Apply the hand-written decisions of the spell_id wording lane, one occurrence at a time.

Run from the repository root:
    python apply_decisions.py <inventory_dir> --scope free|held [--check]
Each decision names one inventory record (path, line, text) and an exact (old, new) pair written by hand for it,
or KEEP with a reason. A decision applies only when the record's line still reads as inventoried and `old` occurs
exactly once in that line (or, for an `old` spanning k line breaks, in the k lines before it plus the line itself).
Lines are numbered as `str.splitlines` numbers them (the inventory's numbering) and each line keeps its own
terminator, so CRLF, LF and mixed files come back byte-identical outside the replaced text.
`--scope free` touches only files nobody else holds; `--scope held` only the files melder_1 holds for its rule-2
lane (applied after it releases them). `--check` reports and writes nothing. Line endings are kept.
"""
import json
import pathlib
import sys

HELD_FILES = {
    "src/melder/aether/spellbook/spellbook.py",
    "src/melder/aether/aetheric_frame/dev_ops/spell_system_states/spell_system_states.py",
    "src/melder/aether/conduit/conduit_ward/conduit_ward.py",
    "src/melder/aether/conduit/conduit.py",
    "src/melder/aether/conduit/meld/meld.py",
    "src/melder/aether/spellbook/spell_compiler/validation/strategies/contract_provider_presence_strategy.py",
    "src/melder/utilities/custom_exceptions/spellbook_validation_error.py",
    "src/melder/aether/conduit/conduit_ward/transfer/transfer_of_ownership.py",
    "src/melder/__version__.py",
    "tests/unit/melder/spellbook/test_spellbook.py",
    "tests/unit/melder/utilities/custom_exceptions/test_spellbook_validation_error.py",
    "tests/unit/melder/spellbook/spell_crafter/validation/strategies/test_contract_provider_presence_strategy.py",
    "tests/unit/melder/spellbook/spell_compiler/phases/test_compiler_phase_4.py",
    "tests/unit/melder/aether/conduit/meld/test_meld.py",
    "tests/integration/melder/multithreading/test_contract_mutation_during_meld_resolution_integration.py",
    "tests/component/melder/spellbook/test_spellbook_component_structural_snapshot_parity.py",
    "tests/component/melder/spellbook/test_spellbook_component_spellbook.py",
    "tests/component/melder/spellbook/test_spellbook_component_spell_crafter.py",
    "tests/integration/melder/conduit/test_conduit_integration_notch_revalidation.py",
    "tests/unit/melder/aether/dev_ops/spell_system_states/test_spell_system_states_dependent_walk.py",
    "context_compass/system_docs/src_architecture.md",
    "context_compass/system_docs/src_components.md",
    "context_compass/system_docs/tests_architecture.md",
    "context_compass/system_docs/tests_components.md",
    "release_docs/next_version_release.md",
}


def is_held(path: str) -> bool:
    """
    Tell whether a file waits for melder_1's release.

    Args:
        path: Repository-relative path.

    Returns:
        bool: True for melder_1's files, the system documents, the graph descriptors and the release note.
    """
    return path in HELD_FILES or path.startswith("context_compass/system_docs/graph/")


def split_keeping_terminators(raw: str) -> tuple:
    """
    Split text into line contents and their own terminators, numbered as `str.splitlines` numbers lines.

    Args:
        raw: The file's text.

    Returns:
        tuple: (contents, terminators), equal length; joining each pair restores `raw` exactly.
    """
    contents, terminators = [], []
    for part in raw.splitlines(keepends=True):
        if part.endswith("\r\n"):
            terminator = "\r\n"
        elif part and part[-1] in "\n\r\x0b\x0c\x1c\x1d\x1e\x85\u2028\u2029":
            terminator = part[-1]
        else:
            terminator = ""
        contents.append(part[:len(part) - len(terminator)])
        terminators.append(terminator)
    assert "".join(c + t for c, t in zip(contents, terminators)) == raw
    return contents, terminators


def load(inventory: pathlib.Path) -> tuple:
    """
    Load the inventory records and every decision file.

    Args:
        inventory: The inventory directory.

    Returns:
        tuple: (records by id, decisions by id).
    """
    records = {r["id"]: r for r in json.loads((inventory / "occurrences.json").read_text(encoding="utf-8"))}
    decisions = {}
    for path in sorted(inventory.glob("decisions_*.json")):
        for rid, old, new in json.loads(path.read_text(encoding="utf-8")):
            assert rid not in decisions, rid
            decisions[rid] = (old, new)
    missing = sorted(set(records) - set(decisions))
    assert not missing, ("records without a decision", missing)
    return records, decisions


def apply_one(lines: list, record: dict, old: str, new: str) -> None:
    """
    Apply one decision to a file's lines in place.

    Args:
        lines: The file's lines (without line terminators).
        record: The inventory record.
        old: The exact text to replace; may span line breaks ending on the record's line.
        new: Its replacement, with the same number of line breaks.
    """
    index = record["line"] - 1
    assert lines[index] == record["text"], ("line moved or changed", record["id"], record["path"], record["line"])
    breaks = old.count("\n")
    assert breaks == new.count("\n"), record["id"]
    window = "\n".join(lines[index - breaks:index + 1])
    assert window.count(old) == 1, ("old not found exactly once", record["id"], window.count(old))
    replaced = window.replace(old, new, 1).split("\n")
    lines[index - breaks:index + 1] = replaced


def main() -> None:
    """Apply (or check) the decisions for one scope."""
    inventory = pathlib.Path(sys.argv[1])
    scope = sys.argv[sys.argv.index("--scope") + 1]
    check = "--check" in sys.argv
    records, decisions = load(inventory)
    by_file = {}
    for rid, record in records.items():
        if is_held(record["path"]) != (scope == "held"):
            continue
        by_file.setdefault(record["path"], []).append(record)
    applied, kept, long_lines = 0, [], []
    for path, file_records in sorted(by_file.items()):
        raw = pathlib.Path(path).read_bytes().decode("utf-8")
        lines, terminators = split_keeping_terminators(raw)
        for record in sorted(file_records, key=lambda r: r["line"]):
            old, new = decisions[record["id"]]
            if old == "KEEP":
                kept.append((record["id"], path, record["line"], new))
                continue
            apply_one(lines, record, old, new)
            applied += 1
            for offset in range(new.count("\n") + 1):
                line = lines[record["line"] - 1 - offset]
                if len(line) > 120:
                    long_lines.append((record["id"], path, record["line"] - offset, len(line)))
        if not check:
            out = "".join(line + terminator for line, terminator in zip(lines, terminators))
            pathlib.Path(path).write_bytes(out.encode("utf-8"))
    print(("CHECK " if check else "APPLIED ") + scope + ": files", len(by_file), "decisions applied", applied,
          "kept", len(kept))
    for item in kept:
        print("KEEP", *item)
    for item in long_lines:
        print("LINE OVER 120", *item)


if __name__ == "__main__":
    main()
