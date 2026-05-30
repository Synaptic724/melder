from importlib import import_module

import pytest

from melder.aether.conduit.creations.conduit_creations import ConduitCreations


def test_legacy_lesser_creations_module_is_removed() -> None:
    """
    Verify the removed legacy lesser-creations module stays unavailable.
    """
    with pytest.raises(ModuleNotFoundError):
        import_module("melder.aether.conduit.creations.lesser_creations")


@pytest.fixture()
def conduit_creations() -> ConduitCreations:
    """
    Build one conduit-owned creations registry.
    """
    return ConduitCreations(conduit_id="conduit-lesser")


def test_init_uses_conduit_id_for_owner_and_scope(
        conduit_creations: ConduitCreations,
) -> None:
    """
    Verify conduit creations uses the conduit id as both owner and scope id.
    """
    assert conduit_creations.owner_conduit_id == "conduit-lesser"
    assert conduit_creations.id == "conduit-lesser"


def test_conduit_creations_has_no_spellspace_specific_surface(
        conduit_creations: ConduitCreations,
) -> None:
    """
    Verify conduit creations does not re-expose old spellspace bucket APIs.
    """
    assert not hasattr(conduit_creations, "register_spellspace_creation")
    assert not hasattr(conduit_creations, "get_spellspace_creation")
    assert not hasattr(conduit_creations, "clear_spellspace_instances")


def test_extract_spell_creations_uses_base_behavior(
        conduit_creations: ConduitCreations,
) -> None:
    """
    Verify conduit creations inherits the base extract contract for unique/many.
    """
    first = object()
    second = object()
    conduit_creations.add_creation("spell-u", first)
    conduit_creations.add_many_creations("spell-m", second)

    extracted_unique = conduit_creations.extract_spell_creations("spell-u")
    extracted_many = conduit_creations.extract_spell_creations("spell-m")

    assert extracted_unique == [
        {
            "scope": "unique",
            "disposable": False,
            "stored": first,
        }
    ]
    assert extracted_many == [
        {
            "scope": "many",
            "disposable": False,
            "stored": second,
        }
    ]


def test_restore_spell_creations_uses_base_behavior(
        conduit_creations: ConduitCreations,
) -> None:
    """
    Verify conduit creations inherits the base restore contract for unique/many.
    """
    unique_value = object()
    many_value = object()

    conduit_creations.restore_spell_creations(
        "spell-u",
        [{"scope": "unique", "disposable": False, "stored": unique_value}],
    )
    conduit_creations.restore_spell_creations(
        "spell-m",
        [{"scope": "many", "disposable": False, "stored": many_value}],
    )

    extracted_unique = conduit_creations.extract_spell_creations("spell-u")
    extracted_many = conduit_creations.extract_spell_creations("spell-m")

    assert extracted_unique[0]["stored"] is unique_value
    assert extracted_unique[0]["scope"] == "unique"
    assert extracted_many[0]["stored"] is many_value
    assert extracted_many[0]["scope"] == "many"
