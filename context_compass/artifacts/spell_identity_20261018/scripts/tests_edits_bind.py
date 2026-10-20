"""melder_0, 2026-10-18: S1's test_bind.py batch. The 44 test functions of the removed `Bind.sha256_profile` (47
cases) leave test_bind.py: 43 retire onto their successors (blast_radius/whole_tree_s1s2/retired_sha256_profile_tests.md),
the non-bool `resolvable` check moves to public `Bind.bind`, and the inspector test is rewritten for the code digest.
Section comments left without tests are kept and say where their tests went. The staged digest test, with its three
successor cases, is copied in."""
import ast
import re
from typing import Dict, List, Optional, Tuple

TEST_BIND = "tests/unit/melder/spellbook/bind/test_bind.py"
DIGEST_TEST = "tests/unit/melder/spellbook/bind/test_spell_code_digest.py"
FINGERPRINT_HEADER = "# Tests: Fingerprint/determinism ---------------------------------------"
SECTION = re.compile(r"^# .*-{4,}\s*$")

RETIRED = (
    "test_sha256_profile_deterministic_class",
    "test_sha256_profile_different_profiles_yield_different_hashes",
    "test_sha256_profile_includes_parameters",
    "test_sha256_parameters_kind_affects_hash",
    "test_sha256_class_init_signature_changes_hash",
    "test_sha256_class_source_preview_no_longer_affects_hash",
    "test_sha256_resolvable_preserves_the_fixed_legacy_fingerprint",
    "test_sha256_non_resolvable_keeps_existing_shape_version_rules",
    "test_sha256_class_annotations_order_irrelevant",
    "test_sha256_callable_repr_changes_hash",
    "test_sha256_callable_builtin_flag_changes_hash",
    "test_sha256_fallback_profile_has_hash_length",
    "test_sha256_annotation_content_changes_hash",
    "test_sha256_callable_signature_changes_hash",
    "test_sha256_callable_param_default_changes_hash",
    "test_sha256_callable_lambda_flag_changes_hash",
    "test_sha256_instance_repr_changes_hash",
    "test_sha256_handles_unicode_identifiers",
    "test_sha256_long_strings_stable_length",
    "test_sha_changes_with_mro_diff",
    "test_sha_changes_with_method_names_diff",
    "test_sha_changes_with_bases_diff",
    "test_sha_changes_with_parameter_annotation",
    "test_sha_changes_with_dataclass_flag",
    "test_sha_changes_with_decorated_flag",
    "test_sha_changes_with_origin_file",
    "test_callable_repr_and_lambda_flag_combo_changes_hash",
    "test_callable_param_default_repr_changes_hash",
    "test_callable_parameters_default_repr_affects_hash",
    "test_callable_lambda_flag_affects_hash_even_with_same_signature",
    "test_callable_builtin_flag_changes_hash",
    "test_callable_extension_flag_changes_hash",
    "test_class_method_names_order_stable_hash",
    "test_class_annotations_keys_change_hash",
    "test_instance_profile_module_changes_hash",
    "test_other_profile_module_changes_hash",
    "test_callable_qualname_vs_name_changes_hash",
    "test_sha_changes_with_extension_and_builtin_flags",
    "test_sha_changes_with_empty_vs_varargs_only",
    "test_sha256_class_reordering_stable",
    "test_sha256_callable_flags_change_hash",
    "test_sha256_instance_vs_other_profiles",
    "test_sha256_profile_changes_with_binding_signature_existence_and_disposal",
)

INSPECTOR_TEST = '''def test_spell_id_inspector_is_the_code_digest(monkeypatch: pytest.MonkeyPatch) -> None:
    """The inspector answers its target's code digest, the same on every call, and builds no binding profile."""

    def _refuse(*args: Any, **kwargs: Any) -> None:
        raise AssertionError("spell_id_inspector built a binding profile")

    monkeypatch.setattr(SpellGeneralProfile, "create_from_target", classmethod(_refuse), raising=True)
    digest = SpellCodeDigest()
    try:
        expected = digest.spell_id(RealClassImplementingProto)
    finally:
        digest.cleanup()
    first = Bind.spell_id_inspector(RealClassImplementingProto)
    assert first == Bind.spell_id_inspector(RealClassImplementingProto) == expected
    assert Bind.spell_id_inspector(ProtoWithFoo) != first'''

RESOLVABLE_TEST = '''@pytest.mark.parametrize("invalid", [None, 0, 1, "false"])
def test_bind_refuses_a_non_bool_resolvable_before_reflecting_the_target(
        monkeypatch: pytest.MonkeyPatch, invalid: object) -> None:
    """A capability that is not exactly True or False is refused at admission, before the target is examined."""
    examiner = StubExaminer(class_profile())
    monkeypatch.setattr("melder.aether.spellbook.bind.bind.SpellExaminer", lambda: examiner)
    binder = Bind(StubSpellbook())
    with pytest.raises(TypeError, match="resolvable must be a bool"):
        binder.bind(
            Permissions.read, Existence.unique, aetheric_frame="f", spell=RealClassImplementingProto,
            resolvable=invalid,
        )
    assert examiner.calls == 0'''

CONVERTED = {
    "test_spell_id_inspector_uses_examiner": INSPECTOR_TEST,
    "test_sha256_resolvable_rejects_non_bool_policy": RESOLVABLE_TEST,
}

FINGERPRINT_NOTE = (
    "# The tests of `Bind.sha256_profile` were retired with it (S1 of EPIC-2026-10-18-spell_identity_is_the_code):\n"
    "# the spell_id is the registered object's code, tested in test_spell_code_digest.py, and how a spell is bound is\n"
    "# its binding manifest, tested in test_binding_manifest.py. What stays here is bind's own contract around the id."
)
EMPTIED_NOTE = "# (Retired with `Bind.sha256_profile`; see the note under \"Tests: Fingerprint/determinism\".)"


def _spans(text: str, applier) -> Optional[List[Tuple[int, int, Optional[str]]]]:
    """Return (first line index, end index, replacement) per retired or converted test, or None on a miss."""
    nodes: Dict[str, ast.FunctionDef] = {node.name: node for node in ast.parse(text).body
                                         if isinstance(node, ast.FunctionDef)}
    wanted = RETIRED + tuple(CONVERTED)
    missing = [name for name in wanted if name not in nodes]
    if missing or len(set(wanted)) != len(wanted):
        applier.errors.append(f"RETIRE in {TEST_BIND}: missing {missing}")
        return None
    spans = []
    for name in wanted:
        node = nodes[name]
        start = min([decorator.lineno for decorator in node.decorator_list] + [node.lineno]) - 1
        spans.append((start, node.end_lineno, CONVERTED.get(name)))
    return spans


def _empty_headers(lines: List[str]) -> List[int]:
    """Indexes of the section comments followed, past blank lines, by another section comment or the end."""
    empty = []
    for index, line in enumerate(lines):
        if SECTION.match(line):
            after = index + 1
            while after < len(lines) and lines[after].strip() == "":
                after += 1
            if after == len(lines) or SECTION.match(lines[after]):
                empty.append(index)
    return empty


def _mark_emptied_sections(lines: List[str], before: List[str]) -> int:
    """Add the retirement pointer under every section comment the retirement left without a test.

    A section that was already empty before the retirement (its comment heads nothing in the original text) is left as
    it was.
    """
    already = {before[index] for index in _empty_headers(before)}
    marked = 0
    for index in reversed(_empty_headers(lines)):
        if lines[index] != FINGERPRINT_HEADER and lines[index] not in already:
            lines.insert(index + 1, EMPTIED_NOTE)
            marked += 1
    return marked


def retire(applier) -> None:
    """Drop the retired tests (with the blank lines after each), put the converted ones in place, mark sections."""
    text = applier._load(TEST_BIND)
    spans = _spans(text, applier)
    if spans is None:
        return
    lines = text.split("\n")
    for start, end, replacement in sorted(spans, reverse=True):
        if replacement is None:
            stop = end
            while stop < len(lines) and lines[stop].strip() == "":
                stop += 1
            del lines[start:stop]
        else:
            lines[start:end] = replacement.split("\n")
    if lines.count(FINGERPRINT_HEADER) != 1:
        applier.errors.append(f"HEADER in {TEST_BIND}: {lines.count(FINGERPRINT_HEADER)}")
        return
    header = lines.index(FINGERPRINT_HEADER)
    lines[header + 1:header + 1] = FINGERPRINT_NOTE.split("\n")
    marked = _mark_emptied_sections(lines, text.split("\n"))
    applier.texts[TEST_BIND] = "\n".join(lines)
    applier.counts[TEST_BIND] = applier.counts.get(TEST_BIND, 0) + len(spans) + 1 + marked
    print(f"retire: {len(RETIRED)} retired, {len(CONVERTED)} converted, {marked} section(s) marked in {TEST_BIND}")


def imports(applier) -> None:
    """`Any` and the digest for the rewritten inspector test; the header over the moved resolvable check."""
    applier.edit(TEST_BIND, [
        ("import inspect\nfrom typing import Protocol\nimport pytest\n",
         "import inspect\nfrom typing import Any, Protocol\nimport pytest\n"),
        ("from melder.aether.spellbook.bind.bind import Bind\n",
         "from melder.aether.spellbook.bind.bind import Bind\n"
         "from melder.aether.spellbook.bind.spell_code_digest import SpellCodeDigest\n"),
        # The section now holds the resolvable check moved from the retired SHA cases.
        ("# Additional SHA stability/diff cases ----------------------------------\n",
         "# Bind admission: a resolvable that is not a bool (the SHA cases here retired with\n"
         "# `Bind.sha256_profile`) -----------------------------------------------\n"),
    ], "bind imports")


def apply(applier) -> None:
    """The test_bind.py batch and the staged digest test."""
    # test_bind.py mixes CRLF (1,867 lines) and LF (72) in the working tree while git holds it LF; written all
    # CRLF, as its majority and binding_profile_strategy.py are.
    applier.normalize_mixed[TEST_BIND] = "\r\n"
    retire(applier)
    imports(applier)
    applier.copy(DIGEST_TEST)
