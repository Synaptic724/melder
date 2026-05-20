from __future__ import annotations

import typing

import pytest

from melder.aether.spellbook.spell_compiler.validation.strategies.annotation_shape_guard_strategy import (
    AnnotationShapeGuardStrategy,
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
        self.spell_name = spell_name


class _Parameter:
    def __init__(self, name: str, annotation) -> None:
        self.name = name
        self.annotation = annotation


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


def test_annotation_shape_guard_flags_unsupported_collection_di_shape() -> None:
    strategy = AnnotationShapeGuardStrategy()
    context = _Context(
        requirements=_Requirements([_Parameter("dep", set["FrameKey"])])
    )

    strategy.validate(context)

    assert [issue.code for issue in context.issues] == ["UNSUPPORTED_COLLECTION_SHAPE"]


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


def test_collection_args_have_di_targets_ignores_ellipsis_and_detects_target() -> None:
    strategy = AnnotationShapeGuardStrategy()

    assert (
        strategy._collection_args_have_di_targets((Ellipsis, "FrameKey"))  # noqa: SLF001
        is True
    )
    assert (
        strategy._collection_args_have_di_targets((Ellipsis, int))  # noqa: SLF001
        is False
    )


def test_looks_like_di_target_heuristics_cover_supported_shapes() -> None:
    class _CustomFrame:
        pass

    strategy = AnnotationShapeGuardStrategy()

    assert strategy._looks_like_di_target(typing.ForwardRef("FrameType")) is True  # noqa: SLF001
    assert strategy._looks_like_di_target("FrameKey") is True  # noqa: SLF001
    assert strategy._looks_like_di_target(_CustomFrame) is True  # noqa: SLF001
    assert strategy._looks_like_di_target(int) is False  # noqa: SLF001
    assert strategy._looks_like_di_target(123) is False  # noqa: SLF001
