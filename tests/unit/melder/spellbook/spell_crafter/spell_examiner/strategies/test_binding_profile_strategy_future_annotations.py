"""Future-annotation tests for BindingProfileStrategy."""
from __future__ import annotations

from typing import List, Optional, Union, get_args, get_origin

from melder.spellbook.spell_crafter.spell_examiner.profiles.binding_profile import (
    ClassBindingProfile,
)
from melder.spellbook.spell_crafter.spell_examiner.strategies.binding_profile_strategy import (
    BindingProfileStrategy,
)


class _FutureProfileRepo:
    """
    Purpose:
        Provide a repository class for future-annotation resolution tests.
    Contract:
        Serves as a concrete annotation target for binding profiles.
    """


class _FutureProfileOther:
    """
    Purpose:
        Provide a secondary class for union annotation coverage.
    Contract:
        Acts as a second type in Union annotations.
    """


class _FutureProfileService:
    """
    Purpose:
        Provide a class with future-style annotations for profile tests.
    Contract:
        Declares class-level annotations using optional, union, list, and dict shapes.
    """

    repo: _FutureProfileRepo
    repos: list[_FutureProfileRepo]
    repos_typing: List[_FutureProfileRepo]
    optional_repo: Optional[_FutureProfileRepo]
    union_repo: Union[_FutureProfileRepo, _FutureProfileOther]
    pep604_repo: _FutureProfileRepo | None
    mapping: dict[str, _FutureProfileRepo]
    count: int

    def ping(self) -> str:
        """
        Purpose:
            Provide a callable to ensure method collection still works.
        Contract:
            Returns a stable response string.
        Returns:
            str: A fixed response string.
        """
        return "pong"


class _FutureProfileMissing:
    """
    Purpose:
        Provide a class with an unresolved future-annotation.
    Contract:
        Allows tests to inject unresolved annotation strings.
    """

    def ping(self) -> str:
        """
        Purpose:
            Provide a callable to confirm profile generation still succeeds.
        Contract:
            Returns a stable response string.
        Returns:
            str: A fixed response string.
        """
        return "pong"


def _profile_for(candidate: type) -> ClassBindingProfile:
    """
    Purpose:
        Build a ClassBindingProfile for the given candidate.
    Contract:
        Returns the binding profile produced by BindingProfileStrategy.
    Args:
        candidate: Class object to inspect.
    Returns:
        ClassBindingProfile: The resulting binding profile.
    """
    strategy = BindingProfileStrategy()
    profile = strategy.build_profile(candidate)
    assert isinstance(profile, ClassBindingProfile)
    return profile


def test_binding_profile_future_annotations_resolve_direct() -> None:
    """
    Purpose:
        Validate future-style direct annotations resolve to concrete classes.
    Contract:
        The repo annotation resolves to _FutureProfileRepo.
    Returns:
        None.
    Raises:
        AssertionError: If the annotation is not resolved.
    """
    profile = _profile_for(_FutureProfileService)

    assert profile.annotations["repo"] is _FutureProfileRepo


def test_binding_profile_future_annotations_resolve_list() -> None:
    """
    Purpose:
        Validate list[T] annotations resolve collection element types.
    Contract:
        list[_FutureProfileRepo] resolves with list origin and Repo element.
    Returns:
        None.
    Raises:
        AssertionError: If list annotations are not resolved.
    """
    profile = _profile_for(_FutureProfileService)
    annotation = profile.annotations["repos"]

    assert get_origin(annotation) is list
    assert get_args(annotation) == (_FutureProfileRepo,)


def test_binding_profile_future_annotations_resolve_typing_list() -> None:
    """
    Purpose:
        Validate typing.List[T] annotations resolve collection element types.
    Contract:
        typing.List[_FutureProfileRepo] resolves with list origin and Repo element.
    Returns:
        None.
    Raises:
        AssertionError: If typing.List annotations are not resolved.
    """
    profile = _profile_for(_FutureProfileService)
    annotation = profile.annotations["repos_typing"]

    assert get_origin(annotation) is list
    assert get_args(annotation) == (_FutureProfileRepo,)


def test_binding_profile_future_annotations_resolve_optional() -> None:
    """
    Purpose:
        Validate Optional[T] annotations resolve to unions with None.
    Contract:
        Optional[_FutureProfileRepo] includes Repo and NoneType args.
    Returns:
        None.
    Raises:
        AssertionError: If Optional annotations are not resolved.
    """
    profile = _profile_for(_FutureProfileService)
    annotation = profile.annotations["optional_repo"]
    args = get_args(annotation)

    assert _FutureProfileRepo in args
    assert type(None) in args


def test_binding_profile_future_annotations_resolve_union() -> None:
    """
    Purpose:
        Validate Union[T, U] annotations resolve both branches.
    Contract:
        Union includes both Repo and Other types in its args.
    Returns:
        None.
    Raises:
        AssertionError: If Union annotations are not resolved.
    """
    profile = _profile_for(_FutureProfileService)
    annotation = profile.annotations["union_repo"]
    args = get_args(annotation)

    assert _FutureProfileRepo in args
    assert _FutureProfileOther in args


def test_binding_profile_future_annotations_resolve_pep604() -> None:
    """
    Purpose:
        Validate PEP 604 T | None annotations resolve correctly.
    Contract:
        Repo and NoneType appear in the union args.
    Returns:
        None.
    Raises:
        AssertionError: If PEP 604 annotations are not resolved.
    """
    profile = _profile_for(_FutureProfileService)
    annotation = profile.annotations["pep604_repo"]
    args = get_args(annotation)

    assert _FutureProfileRepo in args
    assert type(None) in args


def test_binding_profile_future_annotations_resolve_mapping() -> None:
    """
    Purpose:
        Validate dict annotations resolve key/value types.
    Contract:
        dict[str, _FutureProfileRepo] resolves with dict origin and args.
    Returns:
        None.
    Raises:
        AssertionError: If mapping annotations are not resolved.
    """
    profile = _profile_for(_FutureProfileService)
    annotation = profile.annotations["mapping"]

    assert get_origin(annotation) is dict
    assert get_args(annotation) == (str, _FutureProfileRepo)


def test_binding_profile_future_annotations_resolve_builtin() -> None:
    """
    Purpose:
        Validate builtin annotations resolve to builtin types.
    Contract:
        count annotation resolves to int.
    Returns:
        None.
    Raises:
        AssertionError: If builtin annotations are not resolved.
    """
    profile = _profile_for(_FutureProfileService)

    assert profile.annotations["count"] is int


def test_binding_profile_future_annotations_missing_names_clear_annotations() -> None:
    """
    Purpose:
        Validate unresolved names produce empty annotations instead of errors.
    Contract:
        Missing names cause annotations to fall back to an empty dict.
    Returns:
        None.
    Raises:
        AssertionError: If missing names do not clear annotations.
    """
    original = dict(getattr(_FutureProfileMissing, "__annotations__", {}))
    _FutureProfileMissing.__annotations__ = {"missing": "MissingType"}
    try:
        profile = _profile_for(_FutureProfileMissing)

        assert profile.annotations == {}
        assert "ping" in profile.method_names
    finally:
        _FutureProfileMissing.__annotations__ = original


def test_binding_profile_future_annotations_invalid_expression_clear_annotations() -> None:
    """
    Purpose:
        Validate invalid annotation expressions are handled safely.
    Contract:
        Syntax errors during annotation evaluation yield empty annotations.
    Returns:
        None.
    Raises:
        AssertionError: If invalid expressions are not handled.
    """
    class _BadAnnotation:
        """
        Purpose:
            Provide a class with a deliberately invalid annotation expression.
        Contract:
            __annotations__ is patched to trigger SyntaxError during evaluation.
        """

        def ping(self) -> str:
            """
            Purpose:
                Provide a callable to keep method collection active.
            Contract:
                Returns a stable response string.
            Returns:
                str: A fixed response string.
            """
            return "pong"

    _BadAnnotation.__annotations__ = {"value": "list["}

    profile = _profile_for(_BadAnnotation)

    assert profile.annotations == {}
    assert "ping" in profile.method_names
