from __future__ import annotations

import typing

import pytest

from melder.aether.spellbook.spell_compiler.spell_requirements_finder.parameter_di_shape import (
    ParameterDIShape,
)
from melder.aether.spellbook.spell_compiler.validation.strategies.parameter_policy_strategy import (
    ParameterPolicyStrategy,
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


class _Parameter:
    def __init__(
        self,
        *,
        name: str,
        di_shape: ParameterDIShape,
        annotation=None,
        collection_element_annotation=None,
        is_var_positional: bool = False,
        is_var_keyword: bool = False,
    ) -> None:
        self.name = name
        self.di_shape = di_shape
        self.annotation = annotation
        self.collection_element_annotation = collection_element_annotation
        self.is_var_positional = is_var_positional
        self.is_var_keyword = is_var_keyword


class _Requirements:
    def __init__(self, parameters) -> None:
        self.parameters = parameters


class _Spell:
    def __init__(self, spell_name: str = "spell") -> None:
        self.spell_name = spell_name


class _Context:
    def __init__(self, *, requirements, cancel_event=None) -> None:
        self.requirements = requirements
        self.cancel_event = cancel_event
        self.spell = _Spell()
        self.issues = []


def test_parameter_policy_honors_cancellation_before_scan() -> None:
    strategy = ParameterPolicyStrategy()
    context = _Context(requirements=_Requirements([]), cancel_event=_Cancel())

    with pytest.raises(RuntimeError, match="cancelled"):
        strategy.validate(context)


def test_parameter_policy_honors_cancellation_between_parameters() -> None:
    strategy = ParameterPolicyStrategy()
    context = _Context(
        requirements=_Requirements(
            [
                _Parameter(name="first", di_shape=ParameterDIShape.PLAIN),
                _Parameter(name="second", di_shape=ParameterDIShape.PLAIN),
            ]
        ),
        cancel_event=_ToggleCancel(),
    )

    with pytest.raises(RuntimeError, match="cancelled"):
        strategy.validate(context)


def test_parameter_policy_returns_when_requirements_missing() -> None:
    strategy = ParameterPolicyStrategy()
    context = _Context(requirements=None)

    strategy.validate(context)

    assert context.issues == []


def test_parameter_policy_flags_variadic_di_annotation() -> None:
    strategy = ParameterPolicyStrategy()
    context = _Context(
        requirements=_Requirements(
            [
                _Parameter(
                    name="items",
                    di_shape=ParameterDIShape.PLAIN,
                    annotation="FrameKey",
                    is_var_positional=True,
                )
            ]
        )
    )

    strategy.validate(context)

    assert [issue.code for issue in context.issues] == ["VARIADIC_DI_UNSUPPORTED"]


def test_parameter_policy_skips_variadic_non_di_annotation() -> None:
    strategy = ParameterPolicyStrategy()
    context = _Context(
        requirements=_Requirements(
            [
                _Parameter(
                    name="items",
                    di_shape=ParameterDIShape.PLAIN,
                    annotation=int,
                    is_var_keyword=True,
                )
            ]
        )
    )

    strategy.validate(context)

    assert context.issues == []


def test_parameter_policy_flags_missing_di_annotation() -> None:
    strategy = ParameterPolicyStrategy()
    context = _Context(
        requirements=_Requirements(
            [
                _Parameter(
                    name="service",
                    di_shape=ParameterDIShape.SINGLE_BY_ANNOTATION,
                    annotation=None,
                )
            ]
        )
    )

    strategy.validate(context)

    assert [issue.code for issue in context.issues] == ["DI_MISSING_ANNOTATION"]


def test_parameter_policy_flags_builtin_single_annotation() -> None:
    strategy = ParameterPolicyStrategy()
    context = _Context(
        requirements=_Requirements(
            [
                _Parameter(
                    name="service",
                    di_shape=ParameterDIShape.SINGLE_BY_ANNOTATION,
                    annotation=int,
                )
            ]
        )
    )

    strategy.validate(context)

    assert [issue.code for issue in context.issues] == ["DI_BUILTIN_ANNOTATION"]


def test_parameter_policy_flags_missing_collection_element() -> None:
    strategy = ParameterPolicyStrategy()
    context = _Context(
        requirements=_Requirements(
            [
                _Parameter(
                    name="services",
                    di_shape=ParameterDIShape.COLLECTION_BY_ANNOTATION,
                    annotation=list[int],
                    collection_element_annotation=None,
                )
            ]
        )
    )

    strategy.validate(context)

    assert [issue.code for issue in context.issues] == ["DI_COLLECTION_MISSING_ELEMENT"]


def test_parameter_policy_flags_non_di_collection_element() -> None:
    strategy = ParameterPolicyStrategy()
    context = _Context(
        requirements=_Requirements(
            [
                _Parameter(
                    name="services",
                    di_shape=ParameterDIShape.COLLECTION_BY_ANNOTATION,
                    annotation=list[int],
                    collection_element_annotation=int,
                )
            ]
        )
    )

    strategy.validate(context)

    assert [issue.code for issue in context.issues] == ["DI_COLLECTION_NON_FRAME"]


def test_parameter_policy_looks_like_di_target_heuristics() -> None:
    class _Frame:
        pass

    strategy = ParameterPolicyStrategy()

    assert strategy._looks_like_di_target(typing.ForwardRef("Frame")) is True  # noqa: SLF001
    assert strategy._looks_like_di_target("FrameKey") is True  # noqa: SLF001
    assert strategy._looks_like_di_target(_Frame) is True  # noqa: SLF001
    assert strategy._looks_like_di_target(int) is False  # noqa: SLF001
    assert strategy._looks_like_di_target(123) is False  # noqa: SLF001
