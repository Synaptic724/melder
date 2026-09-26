from __future__ import annotations

import typing

import pytest

from melder.aether.spellbook.spell_compiler.validation.strategies.annotation_shape_guard_strategy import (
    AnnotationShapeGuardStrategy,
)
from melder.aether.spellbook.spell_compiler.spell_requirements_finder.parameter_di_shape import (
    ParameterDIShape,
)


class _Cancel:
    @property
    def is_set(self):
        return True

    def throw_if_set(self):
        raise RuntimeError("cancelled")


class _ToggleCancel:
    def __init__(self) -> None:
        self._checks = 0

    @property
    def is_set(self):
        self._checks += 1
        return self._checks > 1

    def throw_if_set(self):
        raise RuntimeError("cancelled")


class _Spell:
    def __init__(self, spell_name: str = "TestSpell") -> None:
        """Represent a resolvable constructor for the DI-shape checks."""
        self.spell_name = spell_name
        self.resolvable = True


class _Parameter:
    def __init__(
        self,
        name: str,
        annotation,
        di_shape: ParameterDIShape = ParameterDIShape.SINGLE_BY_ANNOTATION,
    ) -> None:
        self.name = name
        self.annotation = annotation
        self.di_shape = di_shape


class _Requirements:
    def __init__(self, parameters: list[_Parameter]) -> None:
        self.parameters = parameters


class _Context:
    def __init__(self, *, requirements, cancel_event=None) -> None:
        self.requirements = requirements
        self.cancel_event = cancel_event
        self.spell = _Spell()
        self.issues = []


def test_annotation_shape_guard_honors_cancellation_before_scan() -> None:
    strategy = AnnotationShapeGuardStrategy()
    context = _Context(requirements=_Requirements([]), cancel_event=_Cancel())

    with pytest.raises(RuntimeError, match="cancelled"):
        strategy.validate(context)


def test_annotation_shape_guard_honors_cancellation_between_parameters() -> None:
    strategy = AnnotationShapeGuardStrategy()
    context = _Context(
        requirements=_Requirements(
            [
                _Parameter("first", None),
                _Parameter("second", list[int]),
            ]
        ),
        cancel_event=_ToggleCancel(),
    )

    with pytest.raises(RuntimeError, match="cancelled"):
        strategy.validate(context)


def test_annotation_shape_guard_returns_when_requirements_missing() -> None:
    strategy = AnnotationShapeGuardStrategy()
    context = _Context(requirements=None)

    strategy.validate(context)

    assert context.issues == []


def test_annotation_shape_guard_skips_none_annotation() -> None:
    strategy = AnnotationShapeGuardStrategy()
    context = _Context(requirements=_Requirements([_Parameter("dep", None)]))

    strategy.validate(context)

    assert context.issues == []


def test_annotation_shape_guard_leaves_container_parameters_to_phase_1() -> None:
    """set/frozenset/dict/tuple parameters are PLAIN caller inputs in Phase 1; the guard emits nothing for them."""
    strategy = AnnotationShapeGuardStrategy()
    plain = ParameterDIShape.PLAIN
    context = _Context(
        requirements=_Requirements(
            [
                _Parameter("items", set["FrameKey"], plain),
                _Parameter("frozen", frozenset["FrameKey"], plain),
                _Parameter("by_name", dict[str, "FrameKey"], plain),
                _Parameter("parts", tuple["FrameKey", ...], plain),
                _Parameter("meta", dict[str, typing.Any], plain),
            ]
        )
    )

    strategy.validate(context)

    assert context.issues == []


def test_annotation_shape_guard_leaves_plain_data_lists_silent() -> None:
    """list[Any] and list[str] are plain caller inputs: no list-element warning (2026-09-26)."""
    strategy = AnnotationShapeGuardStrategy()
    context = _Context(
        requirements=_Requirements([
            _Parameter("values", list[typing.Any], ParameterDIShape.PLAIN),
            _Parameter("names", list[str], ParameterDIShape.PLAIN),
        ])
    )

    strategy.validate(context)

    assert context.issues == []


def test_annotation_shape_guard_warns_when_a_user_class_hides_in_the_element() -> None:
    """list[Optional[Plugin]] may have meant injection: warn, and say it is left to the caller."""
    class Plugin:
        """User class stand-in."""

    strategy = AnnotationShapeGuardStrategy()
    context = _Context(
        requirements=_Requirements([
            _Parameter("plugins", list[typing.Optional[Plugin]], ParameterDIShape.PLAIN),
        ])
    )

    strategy.validate(context)

    assert [issue.code for issue in context.issues] == ["LIST_ELEMENT_NOT_DI_TARGET"]
    assert "left for the caller to supply" in context.issues[0].message


def test_annotation_shape_guard_warns_for_list_forward_ref() -> None:
    strategy = AnnotationShapeGuardStrategy()
    context = _Context(
        requirements=_Requirements(
            [_Parameter("dep", list[typing.ForwardRef("FrameType")])]
        )
    )

    strategy.validate(context)

    assert [issue.code for issue in context.issues] == ["UNRESOLVED_FORWARD_REF"]


def test_annotation_shape_guard_warns_for_direct_forward_ref() -> None:
    strategy = AnnotationShapeGuardStrategy()
    context = _Context(
        requirements=_Requirements([_Parameter("dep", typing.ForwardRef("FrameType"))])
    )

    strategy.validate(context)

    assert [issue.code for issue in context.issues] == ["UNRESOLVED_FORWARD_REF"]


def test_looks_like_di_target_heuristics_cover_supported_shapes() -> None:
    class _CustomFrame:
        pass

    strategy = AnnotationShapeGuardStrategy()

    assert strategy._looks_like_di_target(typing.ForwardRef("FrameType")) is True  # noqa: SLF001
    assert strategy._looks_like_di_target("FrameKey") is True  # noqa: SLF001
    assert strategy._looks_like_di_target(_CustomFrame) is True  # noqa: SLF001
    assert strategy._looks_like_di_target(int) is False  # noqa: SLF001
    assert strategy._looks_like_di_target(123) is False  # noqa: SLF001
