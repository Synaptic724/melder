import pytest

from melder.mutation_research.diff.diff_engine import DiffEngine
from melder.mutation_research.diff.diff_strategy import DiffStrategy


def _resolver_for(materials):
    """
    Build one fake material resolver over a fixed mapping.

    Args:
        materials:
            spell_id -> material payload mapping.

    Returns:
        callable: Resolver raising KeyError on unknown identities.
    """
    def resolve(spell_id):
        return materials[spell_id]
    return resolve


def _materials():
    """
    Build two fixture materials with one changed module.

    Returns:
        dict: Two-identity material mapping.
    """
    return {
        "sha-left": {
            "spell_id": "sha-left",
            "sources": {"mod.a": "x = 1\n"},
            "fingerprints": {},
        },
        "sha-right": {
            "spell_id": "sha-right",
            "sources": {"mod.a": "x = 2\n"},
            "fingerprints": {},
        },
    }


def test_engine_registers_default_strategy_family() -> None:
    """
    Verify the built-in family is present without registration calls.
    """
    engine = DiffEngine(_resolver_for(_materials()))

    assert engine.list_strategy_names() == ["source", "structural"]
    engine.cleanup()


def test_engine_diff_dispatches_and_stamps_identities() -> None:
    """
    Verify the verdict carries identities, strategy, and the result body.
    """
    engine = DiffEngine(_resolver_for(_materials()))

    verdict = engine.diff("sha-left", "sha-right")

    assert verdict["left_spell_id"] == "sha-left"
    assert verdict["right_spell_id"] == "sha-right"
    assert verdict["strategy"] == "source"
    assert verdict["result"]["changed_modules"] == ["mod.a"]
    engine.cleanup()


def test_engine_unknown_strategy_names_known_ones() -> None:
    """
    Verify strategy resolution failures are teach-grade.
    """
    engine = DiffEngine(_resolver_for(_materials()))

    with pytest.raises(KeyError, match="Known strategies.*source"):
        engine.diff("sha-left", "sha-right", strategy="ast")
    engine.cleanup()


def test_engine_structural_strategy_dispatches() -> None:
    """
    Verify the structural default is reachable through normal dispatch.
    """
    engine = DiffEngine(_resolver_for(_materials()))

    verdict = engine.diff("sha-left", "sha-right", strategy="structural")

    assert verdict["strategy"] == "structural"
    assert "module_reports" in verdict["result"]
    engine.cleanup()


def test_engine_resolver_errors_propagate() -> None:
    """
    Verify unknown identities stay loud (resolver KeyError untouched).
    """
    engine = DiffEngine(_resolver_for(_materials()))

    with pytest.raises(KeyError):
        engine.diff("sha-left", "sha-ghost")
    engine.cleanup()


def test_engine_validates_inputs_and_construction() -> None:
    """
    Verify identity validation and resolver requirement.
    """
    with pytest.raises(ValueError, match="material_resolver"):
        DiffEngine(None)
    engine = DiffEngine(_resolver_for(_materials()))
    with pytest.raises(ValueError, match="left_spell_id"):
        engine.diff("", "sha-right")
    with pytest.raises(ValueError, match="right_spell_id"):
        engine.diff("sha-left", "")
    engine.cleanup()


def test_engine_open_closed_registration() -> None:
    """
    Verify new strategies extend the family without engine edits and
    duplicate names are refused.
    """
    class _CountStrategy(DiffStrategy):
        __slots__ = DiffStrategy.__slots__

        @property
        def name(self) -> str:
            self.check_cleaned()
            return "module-count"

        def diff(self, left_material, right_material):
            self.check_cleaned()
            return {
                "left_count": len(left_material["sources"]),
                "right_count": len(right_material["sources"]),
            }

    engine = DiffEngine(_resolver_for(_materials()))
    engine.register_strategy(_CountStrategy())

    verdict = engine.diff("sha-left", "sha-right", strategy="module-count")
    assert verdict["result"] == {"left_count": 1, "right_count": 1}
    with pytest.raises(ValueError, match="already owns"):
        engine.register_strategy(_CountStrategy())
    with pytest.raises(TypeError, match="DiffStrategy"):
        engine.register_strategy(object())
    engine.cleanup()


def test_engine_cleanup_cascades_into_strategies() -> None:
    """
    Verify cleanup cascades and guards further dispatch.
    """
    engine = DiffEngine(_resolver_for(_materials()))
    engine.cleanup()
    engine.cleanup()

    assert engine.cleaned is True
    with pytest.raises(RuntimeError):
        engine.diff("sha-left", "sha-right")
