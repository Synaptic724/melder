"""Future-annotation tests for ClassInspector."""
from __future__ import annotations

from typing import Annotated, List, Optional, Union, get_args, get_origin

from melder.aether.spellbook.spell_crafter.spell_examiner.inspectors.class_inspector import (
    ClassInspector,
)


class _FutureInspectorRepo:
    """
    Purpose:
        Provide a repository class for future-annotation inspection tests.
    Contract:
        Serves as a resolved annotation target for ClassInspector.
    """


class _FutureInspectorOther:
    """
    Purpose:
        Provide a secondary type for Union annotation coverage.
    Contract:
        Acts as a union branch in class-level annotations.
    """


class _FutureInspectorOuter:
    """
    Purpose:
        Provide an outer type for dotted annotation coverage.
    Contract:
        Exposes Inner for dotted name resolution tests.
    """

    class Inner:
        """
        Purpose:
            Provide an inner type for dotted annotation coverage.
        Contract:
            Acts as a nested class for dotted name resolution.
        """


class _FutureInspectorContainer:
    """
    Purpose:
        Provide a class with future-style annotations for ClassInspector.
    Contract:
        Declares optional, union, list, dict, annotated, and dotted annotations.
    """

    repo: _FutureInspectorRepo
    repos: list[_FutureInspectorRepo]
    repos_typing: List[_FutureInspectorRepo]
    optional_repo: Optional[_FutureInspectorRepo]
    union_repo: Union[_FutureInspectorRepo, _FutureInspectorOther]
    pep604_repo: _FutureInspectorRepo | None
    mapping: dict[str, _FutureInspectorRepo]
    annotated_repo: Annotated[_FutureInspectorRepo, "meta"]
    inner: _FutureInspectorOuter.Inner

    def set_repo(self, repo: _FutureInspectorRepo) -> None:
        """
        Purpose:
            Provide a method with a future-annotation for parameter inspection.
        Contract:
            Accepts a repository parameter and performs no side effects.
        Args:
            repo: Repository instance to accept.
        Returns:
            None.
        """
        return None


def _inspect_container() -> dict[str, object]:
    """
    Purpose:
        Inspect the container class with ClassInspector.
    Contract:
        Returns the full inspection data for _FutureInspectorContainer.
    Returns:
        dict[str, object]: The inspection results dictionary.
    """
    inspector = ClassInspector(_FutureInspectorContainer, show_dunders=True)
    return inspector.inspect()


def test_class_inspector_future_annotations_resolve_direct() -> None:
    """
    Purpose:
        Validate direct future-style annotations resolve to concrete types.
    Contract:
        repo annotation resolves to _FutureInspectorRepo.
    Returns:
        None.
    Raises:
        AssertionError: If the annotation is not resolved.
    """
    data = _inspect_container()

    assert data["annotations"]["repo"] is _FutureInspectorRepo


def test_class_inspector_future_annotations_resolve_list() -> None:
    """
    Purpose:
        Validate list[T] annotations resolve collection element types.
    Contract:
        list[_FutureInspectorRepo] yields list origin with Repo element.
    Returns:
        None.
    Raises:
        AssertionError: If list annotations are not resolved.
    """
    data = _inspect_container()
    annotation = data["annotations"]["repos"]

    assert get_origin(annotation) is list
    assert get_args(annotation) == (_FutureInspectorRepo,)


def test_class_inspector_future_annotations_resolve_typing_list() -> None:
    """
    Purpose:
        Validate typing.List[T] annotations resolve collection element types.
    Contract:
        typing.List[_FutureInspectorRepo] yields list origin with Repo element.
    Returns:
        None.
    Raises:
        AssertionError: If typing.List annotations are not resolved.
    """
    data = _inspect_container()
    annotation = data["annotations"]["repos_typing"]

    assert get_origin(annotation) is list
    assert get_args(annotation) == (_FutureInspectorRepo,)


def test_class_inspector_future_annotations_resolve_optional() -> None:
    """
    Purpose:
        Validate Optional[T] annotations resolve to unions with None.
    Contract:
        Optional includes Repo and NoneType in its args.
    Returns:
        None.
    Raises:
        AssertionError: If Optional annotations are not resolved.
    """
    data = _inspect_container()
    annotation = data["annotations"]["optional_repo"]
    args = get_args(annotation)

    assert _FutureInspectorRepo in args
    assert type(None) in args


def test_class_inspector_future_annotations_resolve_union() -> None:
    """
    Purpose:
        Validate Union[T, U] annotations resolve both branches.
    Contract:
        Union includes Repo and Other in its args.
    Returns:
        None.
    Raises:
        AssertionError: If Union annotations are not resolved.
    """
    data = _inspect_container()
    annotation = data["annotations"]["union_repo"]
    args = get_args(annotation)

    assert _FutureInspectorRepo in args
    assert _FutureInspectorOther in args


def test_class_inspector_future_annotations_resolve_pep604() -> None:
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
    data = _inspect_container()
    annotation = data["annotations"]["pep604_repo"]
    args = get_args(annotation)

    assert _FutureInspectorRepo in args
    assert type(None) in args


def test_class_inspector_future_annotations_resolve_mapping() -> None:
    """
    Purpose:
        Validate dict annotations resolve key/value types.
    Contract:
        dict[str, _FutureInspectorRepo] resolves with dict origin and args.
    Returns:
        None.
    Raises:
        AssertionError: If mapping annotations are not resolved.
    """
    data = _inspect_container()
    annotation = data["annotations"]["mapping"]

    assert get_origin(annotation) is dict
    assert get_args(annotation) == (str, _FutureInspectorRepo)


def test_class_inspector_future_annotations_resolve_annotated() -> None:
    """
    Purpose:
        Validate Annotated[T, ...] annotations preserve the base type.
    Contract:
        Annotated args include the Repo type and the metadata string.
    Returns:
        None.
    Raises:
        AssertionError: If Annotated annotations are not resolved.
    """
    data = _inspect_container()
    annotation = data["annotations"]["annotated_repo"]
    args = get_args(annotation)

    assert args[0] is _FutureInspectorRepo
    assert "meta" in args


def test_class_inspector_future_annotations_resolve_dotted_inner() -> None:
    """
    Purpose:
        Validate dotted name annotations resolve nested classes.
    Contract:
        inner annotation resolves to _FutureInspectorOuter.Inner.
    Returns:
        None.
    Raises:
        AssertionError: If dotted annotations are not resolved.
    """
    data = _inspect_container()

    assert data["annotations"]["inner"] is _FutureInspectorOuter.Inner


def test_class_inspector_future_annotations_method_param_annotation_string() -> None:
    """
    Purpose:
        Validate method parameter annotations are captured as strings.
    Contract:
        Parameter annotation includes the Repo class name.
    Returns:
        None.
    Raises:
        AssertionError: If parameter annotation is missing or unexpected.
    """
    data = _inspect_container()
    params = data["members"]["set_repo"]["parameters"]

    assert len(params) >= 2
    annotation = params[1]["annotation"]
    assert annotation is not None
    assert "FutureInspectorRepo" in annotation
