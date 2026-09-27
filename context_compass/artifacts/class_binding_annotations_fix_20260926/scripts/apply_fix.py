"""Apply the class binding-profile annotation fix and its tests to a tree root (argv[1]).

Anchored whole-line edits (patch_util.replace_block / append_block); refuses on any anchor mismatch.
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from patch_util import append_block, replace_block

ROOT = pathlib.Path(sys.argv[1])
SRC = ROOT / "src/melder/aether/spellbook/spell_compiler/spell_examiner/strategies/binding_profile_strategy.py"
TEST = ROOT / "tests/unit/melder/spellbook/spell_crafter/spell_examiner/strategies/test_binding_profile_strategy.py"

# --- source -------------------------------------------------------------------------------------------------
replace_block(SRC, "from annotationlib import Format\nfrom typing import TYPE_CHECKING, Any, List, ClassVar, Optional",
              "from annotationlib import Format\nfrom types import ModuleType\n"
              "from typing import TYPE_CHECKING, Any, Dict, List, ClassVar, Optional")

replace_block(SRC, '''        (`SignatureReflection.stabilize_signature`) and stays identical across
        processes; the cached signature object keeps the ForwardRefs.
        """
        module = inspect.getmodule(cls)

        try:
            annotations = inspect.get_annotations(
                cls,
                eval_str=True,
                globals=module.__dict__ if module is not None else None,
            )
        except Exception:
            annotations = {}''', '''        (`SignatureReflection.stabilize_signature`) and stays identical across
        processes; the cached signature object keeps the ForwardRefs.

        Class-level annotations come from `_read_class_annotations`: evaluated
        where every name resolves, otherwise read without evaluating the
        unavailable names, which stay as their source text (2026-09-26). The
        bind fingerprint hashes their keys, so every annotated field counts.
        """
        module = inspect.getmodule(cls)

        annotations = self._read_class_annotations(cls, module)''')

replace_block(SRC, "    def _build_callable_profile(self, fn: Any) -> CallableBindingProfile:", '''    @staticmethod
    def _read_class_annotations(cls: type, module: Optional[ModuleType]) -> Dict[str, Any]:
        """
        Return the class-level annotations recorded in a class binding profile.

        Contract:
            - Evaluates with `inspect.get_annotations(..., eval_str=True)` against
              the class's module, so string annotations resolve where possible.
              A class whose names all resolve gets exactly that mapping.
            - A name unbound at runtime (a TYPE_CHECKING-only import under Python
              3.14 lazy annotations) makes that evaluation raise NameError. The
              annotations are then read without evaluating it
              (`SignatureReflection.class_annotations`, the read ClassInspector
              uses): the same keys, each unavailable name as its source text
              (`'Decimal'`, `'list[Decimal]'`), quoted strings as written.
              Before 2026-09-26 this case dropped every annotation of the class.
            - Keys are always the class's own annotation names, so the bind
              fingerprint (which hashes the sorted keys) sees every annotated field.
            - Best-effort: any other failure, including one inside that fallback,
              yields an empty mapping, so binding never fails because a class's
              annotations cannot be read.

        Args:
            cls: Class candidate being profiled.
            module: Module returned by `inspect.getmodule(cls)`, or None.

        Returns:
            Dict[str, Any]: Attribute name to annotation value - the evaluated
                object, or source text for a name unavailable at runtime.
        """
        try:
            return inspect.get_annotations(
                cls,
                eval_str=True,
                globals=module.__dict__ if module is not None else None,
            )
        except NameError:
            try:
                return SignatureReflection.class_annotations(cls)
            except Exception:
                # Best-effort: annotations that cannot be read bind as none.
                return {}
        except Exception:
            # Best-effort: annotations that cannot be read bind as none.
            return {}

    def _build_callable_profile(self, fn: Any) -> CallableBindingProfile:''')

# --- tests --------------------------------------------------------------------------------------------------
replace_block(TEST, '''from melder.aether.spellbook.spell_compiler.spell_examiner.strategies.binding_profile_strategy import (
    BindingProfileStrategy,
)''', '''from melder.aether.spellbook.spell_compiler.spell_examiner.strategies.binding_profile_strategy import (
    BindingProfileStrategy,
)
from typing import TYPE_CHECKING, Optional

from melder.aether.spellbook.bind.bind import Bind
from melder.utilities.helpers.signature_reflection import SignatureReflection

if TYPE_CHECKING:
    # Annotations only: `Decimal` stays unbound at runtime in this module - the case under test.
    from decimal import Decimal


class _TypeCheckingField:
    """
    Purpose:
        Class whose field annotation names a TYPE_CHECKING-only type.
    """
    amount: Decimal
    label: str


class _QuotedUnavailable:
    """
    Purpose:
        Class whose quoted field annotation names a TYPE_CHECKING-only type.
    """
    amount: "Decimal"
    label: str


class _NestedUnavailable:
    """
    Purpose:
        Class whose unavailable name sits inside generic annotations.
    """
    amounts: list[Decimal]
    total: Optional[Decimal]
    count: int


@dataclass
class _DataclassUnavailable:
    """
    Purpose:
        Dataclass whose field annotation names a TYPE_CHECKING-only type.
    """
    amount: Decimal
    label: str = "x"


class _ResolvedFields:
    """
    Purpose:
        Class whose annotations all resolve at runtime, one of them quoted.
    """
    count: int
    name: "str"


def _priced_class(extra: bool) -> type:
    """
    Purpose:
        Build a class named `Priced` with one or two TYPE_CHECKING-typed fields.
    Contract:
        Both variants share name, qualname, module, bases and methods; only the annotation keys differ.
    Args:
        extra: Whether to declare the second field.
    Returns:
        type: The class.
    """
    class Priced:
        amount: Decimal
        if extra:
            surcharge: Decimal
    return Priced''')

append_block(TEST, '''

def test_binding_profile_class_annotations_keep_type_checking_names_as_source_text() -> None:
    """
    Purpose:
        Verify a field typed with a TYPE_CHECKING-only name keeps every class annotation.
    Contract:
        - Keys are the class's own annotation names.
        - The unavailable name is its source text; resolvable values stay evaluated.
    Returns:
        None.
    """
    profile = BindingProfileStrategy()._build_class_profile(_TypeCheckingField)

    assert profile.annotations == {"amount": "Decimal", "label": str}


def test_binding_profile_class_annotations_keep_quoted_and_nested_unavailable_names() -> None:
    """
    Purpose:
        Verify quoted and generic-nested unavailable names are kept as written.
    Contract:
        - A quoted annotation stays its string; a nested one is the generic's source text.
    Returns:
        None.
    """
    strategy = BindingProfileStrategy()

    quoted = strategy._build_class_profile(_QuotedUnavailable)
    nested = strategy._build_class_profile(_NestedUnavailable)

    assert quoted.annotations == {"amount": "Decimal", "label": str}
    assert nested.annotations == {"amounts": "list[Decimal]", "total": "Optional[Decimal]", "count": int}


def test_binding_profile_class_annotations_keep_dataclass_fields_with_unavailable_names() -> None:
    """
    Purpose:
        Verify a dataclass field typed with a TYPE_CHECKING-only name is kept.
    Returns:
        None.
    """
    profile = BindingProfileStrategy()._build_class_profile(_DataclassUnavailable)

    assert profile.annotations == {"amount": "Decimal", "label": str}
    assert profile.is_dataclass is True


def test_binding_profile_class_annotations_unchanged_when_every_name_resolves() -> None:
    """
    Purpose:
        Verify classes whose annotations resolve keep the evaluated read (quoted strings evaluated).
    Returns:
        None.
    """
    profile = BindingProfileStrategy()._build_class_profile(_ResolvedFields)

    assert profile.annotations == {"count": int, "name": str}


def test_binding_profile_class_annotations_fallback_failure_binds_with_none(monkeypatch) -> None:
    """
    Purpose:
        Verify a failure inside the unevaluated fallback still yields an empty mapping.
    Contract:
        - Binding never fails because class annotations cannot be read.
    Returns:
        None.
    """
    def _raise_name_error(*args, **kwargs):
        raise NameError("name 'Decimal' is not defined")

    def _raise_type_error(cls):
        raise TypeError("boom")

    monkeypatch.setattr(inspect, "get_annotations", _raise_name_error)
    monkeypatch.setattr(SignatureReflection, "class_annotations", staticmethod(_raise_type_error))

    profile = BindingProfileStrategy()._build_class_profile(_TypeCheckingField)

    assert profile.annotations == {}


def test_bind_fingerprint_counts_fields_typed_with_type_checking_names() -> None:
    """
    Purpose:
        Verify the bind fingerprint changes when a TYPE_CHECKING-typed field is added.
    Contract:
        - Before 2026-09-26 both classes profiled with no annotations and hashed equal.
        - Equal classes still hash equal.
    Returns:
        None.
    """
    strategy = BindingProfileStrategy()

    plain = Bind.sha256_profile(strategy._build_class_profile(_priced_class(False)))
    again = Bind.sha256_profile(strategy._build_class_profile(_priced_class(False)))
    extended = Bind.sha256_profile(strategy._build_class_profile(_priced_class(True)))

    assert plain == again
    assert plain != extended
''')
FUTURE = ROOT / ("tests/unit/melder/spellbook/spell_crafter/spell_examiner/strategies/"
                 "test_binding_profile_strategy_future_annotations.py")
replace_block(FUTURE, """def test_binding_profile_future_annotations_missing_names_clear_annotations() -> None:
    \"\"\"
    Purpose:
        Validate unresolved names produce empty annotations instead of errors.
    Contract:
        Missing names cause annotations to fall back to an empty dict.
    Returns:
        None.
    Raises:
        AssertionError: If missing names do not clear annotations.
    \"\"\"
    original = dict(getattr(_FutureProfileMissing, "__annotations__", {}))
    _FutureProfileMissing.__annotations__ = {"missing": "MissingType"}
    try:
        profile = _profile_for(_FutureProfileMissing)

        assert profile.annotations == {}""", """def test_binding_profile_future_annotations_missing_names_keep_source_text() -> None:
    \"\"\"
    Purpose:
        Validate unresolved names are kept as written instead of raising or clearing annotations.
    Contract:
        A missing name keeps its key with the annotation's source text; profile building still
        succeeds and collects methods. Before 2026-09-26 every annotation of the class was dropped.
    Returns:
        None.
    Raises:
        AssertionError: If the missing name is not kept as its source text.
    \"\"\"
    original = dict(getattr(_FutureProfileMissing, "__annotations__", {}))
    _FutureProfileMissing.__annotations__ = {"missing": "MissingType"}
    try:
        profile = _profile_for(_FutureProfileMissing)

        assert profile.annotations == {"missing": "MissingType"}""")
print("applied to", ROOT)
