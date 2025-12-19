import pytest

from melder.spellbook.spell_crafter.dag.target_spec import TargetSpec, TargetSpecKind


def test_parse_path_trims_and_segments():
    spec = TargetSpec.parse(" root > child > leaf ")
    assert spec.kind is TargetSpecKind.PATH
    assert spec.path == ("root", "child", "leaf")
    assert spec.param_name is None


def test_parse_unique_and_broadcast_variants():
    unique = TargetSpec.parse("*logger")
    broadcast = TargetSpec.parse("**repo")
    assert unique.kind is TargetSpecKind.UNIQUE
    assert unique.param_name == "logger"
    assert broadcast.kind is TargetSpecKind.BROADCAST
    assert broadcast.param_name == "repo"


def test_parse_trims_param_names_and_paths():
    unique = TargetSpec.parse("* logger ")
    broadcast = TargetSpec.parse("** repo ")
    path = TargetSpec.parse(" a > b > c ")
    assert unique.param_name == "logger"
    assert broadcast.param_name == "repo"
    assert path.path == ("a", "b", "c")


@pytest.mark.parametrize(
    "raw",
    [None, "", "   ", "*", "**", ">", ">>>"],
)
def test_parse_invalid_inputs_raise(raw):
    with pytest.raises(ValueError):
        TargetSpec.parse(raw)  # type: ignore[arg-type]
