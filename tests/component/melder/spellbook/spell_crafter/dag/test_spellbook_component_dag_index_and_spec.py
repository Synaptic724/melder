import pytest


from melder.aether.spellbook.spell_compiler.dag.target_spec import TargetSpec, TargetSpecKind


def test_component_target_spec_parses_paths_and_wildcards() -> None:
    """
    Purpose:
        Validate TargetSpec parsing for path and wildcard forms.
    Contract:
        - PATH specs parse into segments.
        - UNIQUE and BROADCAST specs capture param_name.
    Returns:
        None.
    """
    path_spec = TargetSpec.parse(" root > child > leaf ")
    assert path_spec.kind is TargetSpecKind.PATH
    assert path_spec.path == ("root", "child", "leaf")
    assert path_spec.param_name is None

    unique_spec = TargetSpec.parse("*repo")
    assert unique_spec.kind is TargetSpecKind.UNIQUE
    assert unique_spec.param_name == "repo"

    broadcast_spec = TargetSpec.parse("**logger")
    assert broadcast_spec.kind is TargetSpecKind.BROADCAST
    assert broadcast_spec.param_name == "logger"


def test_component_target_spec_rejects_empty_or_missing_names() -> None:
    """
    Purpose:
        Validate TargetSpec rejects empty or malformed inputs.
    Contract:
        - Empty or missing parameter names raise ValueError.
    Returns:
        None.
    """
    with pytest.raises(ValueError):
        TargetSpec.parse("   ")
    with pytest.raises(ValueError):
        TargetSpec.parse("*")
    with pytest.raises(ValueError):
        TargetSpec.parse("**")


