from typing import Protocol

import pytest

from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.aether.conduit.meld.contracts.spell_map import SpellMap
from melder.aether.spellbook.configuration.spellbook_configuration import SpellbookConfiguration
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spellbook import Spellbook


from tests._frame_posture_test_support import (
    apply_dynamic_defaults_for_spellbook_configuration,
)
@pytest.fixture(autouse=True)
def reset_aether_singleton_for_integration() -> None:
    """
    Purpose:
        Ensure integration tests start with a clean Aether singleton.
    Contract:
        - Resets the Aether singleton before the test runs.
        - Rebinds Spellbook._aether and Conduit._aether to the new instance.
        - Resets the singleton again after the test for isolation.
    Returns:
        None.
    """
    Aether._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether
    yield
    Aether._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether


def test_meld_by_spell_name_string_resolves_default_binding() -> None:
    """
    Purpose:
        Validate Conduit.meld resolves by spell_name string.
    Contract:
        - The spell_name string resolves the default binding.
    Returns:
        None.
    Raises:
        AssertionError: If the resolved instance is incorrect.
    """
    class _Service:
        """
        Purpose:
            Provide a class spell for spell_name resolution.
        Contract:
            Stores a stable marker for assertions.
        """
        def __init__(self) -> None:
            """
            Purpose:
                Initialize the marker.
            Contract:
                Sets marker to "by-name".
            Returns:
                None.
            """
            self.marker = "by-name"

    spellbook = Spellbook()
    config = spellbook.get_configuration()
    config.set_property("phase_scheduler_workers_per_spellbook", 1)

    spellbook.bind(
        spell=_Service,
        existence=Existence.unique,
        permissions="create",
    )

    conduit = spellbook.conjure(name="root")
    try:
        instance = conduit.meld(spell=_Service.__name__)
        assert isinstance(instance, _Service)
        assert instance.marker == "by-name"
    finally:
        conduit.cleanup()


def test_meld_by_spellframe_string_normalizes_case() -> None:
    """
    Purpose:
        Validate string spellframe lookups are case-insensitive.
    Contract:
        - Spellframe normalization allows case-insensitive resolution.
    Returns:
        None.
    Raises:
        AssertionError: If the resolved instance is incorrect.
    """
    class _Config:
        """
        Purpose:
            Provide a config spell for string spellframe resolution.
        Contract:
            Stores a stable marker for assertions.
        """
        def __init__(self) -> None:
            """
            Purpose:
                Initialize the marker.
            Contract:
                Sets marker to "config".
            Returns:
                None.
            """
            self.marker = "config"

    spellbook = Spellbook()
    config = spellbook.get_configuration()
    config.set_property("phase_scheduler_workers_per_spellbook", 1)

    spellbook.bind(
        spell=_Config,
        existence=Existence.unique,
        permissions="create",
        spellframe="config",
    )

    conduit = spellbook.conjure(name="root")
    try:
        instance = conduit.meld(spellframe="CONFIG")
        assert isinstance(instance, _Config)
        assert instance.marker == "config"
    finally:
        conduit.cleanup()


def test_meld_by_protocol_binding_name_normalizes_case() -> None:
    """
    Purpose:
        Validate binding_name normalization for protocol spellframes.
    Contract:
        - Binding names are case-insensitive during resolution.
    Returns:
        None.
    Raises:
        AssertionError: If the resolved instance is incorrect.
    """
    class IService(Protocol):
        """
        Purpose:
            Provide a protocol spellframe for service resolution.
        Contract:
            Acts as a DI grouping key.
        """
        pass

    class _Service:
        """
        Purpose:
            Provide a service implementation for binding_name resolution.
        Contract:
            Stores a stable marker for assertions.
        """
        def __init__(self) -> None:
            """
            Purpose:
                Initialize the marker.
            Contract:
                Sets marker to "primary".
            Returns:
                None.
            """
            self.marker = "primary"

    spellbook = Spellbook()
    config = spellbook.get_configuration()
    config.set_property("phase_scheduler_workers_per_spellbook", 1)

    spellbook.bind(
        spell=_Service,
        existence=Existence.unique,
        permissions="create",
        spellframe=IService,
        binding_name="Primary",
    )

    conduit = spellbook.conjure(name="root")
    try:
        instance = conduit.meld(spell=IService, binding_name="primary")
        assert isinstance(instance, _Service)
        assert instance.marker == "primary"
    finally:
        conduit.cleanup()


def test_type_hint_di_by_protocol_reuses_unique_instance() -> None:
    """
    Purpose:
        Validate protocol-based DI reuses unique dependencies.
    Contract:
        - Unique dependencies are reused across multiple melds.
    Returns:
        None.
    Raises:
        AssertionError: If dependency reuse fails.
    """
    class IRepository(Protocol):
        """
        Purpose:
            Provide a protocol spellframe for repository DI.
        Contract:
            Acts as a DI grouping key.
        """
        pass

    class _Repo:
        """
        Purpose:
            Provide a repository implementation.
        Contract:
            Stores a stable marker for assertions.
        """
        def __init__(self) -> None:
            """
            Purpose:
                Initialize the marker.
            Contract:
                Sets marker to "repo".
            Returns:
                None.
            """
            self.marker = "repo"

    class _Service:
        """
        Purpose:
            Provide a service that depends on IRepository.
        Contract:
            Stores the repository dependency.
        """
        def __init__(self, repo: IRepository) -> None:
            """
            Purpose:
                Capture the repository dependency.
            Contract:
                Stores the repo on the instance.
            Args:
                repo: Injected repository dependency.
            Returns:
                None.
            """
            self.repo = repo

    spellbook = Spellbook()
    config = spellbook.get_configuration()
    config.set_property("phase_scheduler_workers_per_spellbook", 1)

    spellbook.bind(
        spell=_Repo,
        existence=Existence.unique,
        permissions="create",
        spellframe=IRepository,
    )
    spellbook.bind(
        spell=_Service,
        existence=Existence.many,
        permissions="create",
    )

    conduit = spellbook.conjure(name="root")
    try:
        first = conduit.meld(spell=_Service)
        second = conduit.meld(spell=_Service)
        assert first.repo is second.repo
    finally:
        conduit.cleanup()


def test_type_hint_di_by_concrete_class_reuses_unique_instance() -> None:
    """
    Purpose:
        Validate concrete-class DI reuses unique dependencies.
    Contract:
        - Unique dependencies are reused across multiple melds.
    Returns:
        None.
    Raises:
        AssertionError: If dependency reuse fails.
    """
    class _Repo:
        """
        Purpose:
            Provide a repository dependency.
        Contract:
            Stores a stable marker for assertions.
        """
        def __init__(self) -> None:
            """
            Purpose:
                Initialize the marker.
            Contract:
                Sets marker to "repo".
            Returns:
                None.
            """
            self.marker = "repo"

    class _Service:
        """
        Purpose:
            Provide a service that depends on _Repo.
        Contract:
            Stores the repository dependency.
        """
        def __init__(self, repo: _Repo) -> None:
            """
            Purpose:
                Capture the repository dependency.
            Contract:
                Stores the repo on the instance.
            Args:
                repo: Injected repository dependency.
            Returns:
                None.
            """
            self.repo = repo

    spellbook = Spellbook()
    config = spellbook.get_configuration()
    config.set_property("phase_scheduler_workers_per_spellbook", 1)

    spellbook.bind(
        spell=_Repo,
        existence=Existence.unique,
        permissions="create",
    )
    spellbook.bind(
        spell=_Service,
        existence=Existence.many,
        permissions="create",
    )

    conduit = spellbook.conjure(name="root")
    try:
        first = conduit.meld(spell=_Service)
        second = conduit.meld(spell=_Service)
        assert first.repo is second.repo
    finally:
        conduit.cleanup()


def test_spellmap_default_explicit_class_with_frame_matches() -> None:
    """
    Purpose:
        Validate SpellMap explicit class defaults respect spellframe filters.
    Contract:
        - Explicit SpellMap with a matching frame resolves correctly.
    Returns:
        None.
    Raises:
        AssertionError: If the resolved dependency is incorrect.
    """
    class _Config:
        """
        Purpose:
            Provide a config spell for explicit SpellMap resolution.
        Contract:
            Stores a stable marker for assertions.
        """
        def __init__(self) -> None:
            """
            Purpose:
                Initialize the marker.
            Contract:
                Sets marker to "cfg".
            Returns:
                None.
            """
            self.marker = "cfg"

    class _Service:
        """
        Purpose:
            Provide a service with an explicit SpellMap dependency.
        Contract:
            Stores the resolved config instance.
        """
        def __init__(self, cfg=SpellMap(_Config, spellframe="cfg")) -> None:
            """
            Purpose:
                Capture the config dependency.
            Contract:
                Stores the config on the instance.
            Args:
                cfg: Injected config instance.
            Returns:
                None.
            """
            self.cfg = cfg

    spellbook = Spellbook()
    config = spellbook.get_configuration()
    config.set_property("phase_scheduler_workers_per_spellbook", 1)

    spellbook.bind(
        spell=_Config,
        existence=Existence.unique,
        permissions="create",
        spellframe="cfg",
    )
    spellbook.bind(
        spell=_Service,
        existence=Existence.many,
        permissions="create",
    )

    conduit = spellbook.conjure(name="root")
    try:
        instance = conduit.meld(spell=_Service)
        assert isinstance(instance.cfg, _Config)
        assert instance.cfg.marker == "cfg"
    finally:
        conduit.cleanup()


def test_spellmap_default_frame_only_binding_name_is_case_insensitive() -> None:
    """
    Purpose:
        Validate SpellMap binding_name normalization for frame-only defaults.
    Contract:
        - SpellMap binding_name is case-insensitive during resolution.
    Returns:
        None.
    Raises:
        AssertionError: If the binding name is not honored.
    """
    class IConfig(Protocol):
        """
        Purpose:
            Provide a protocol spellframe for configuration DI.
        Contract:
            Acts as a DI grouping key.
        """
        pass

    class _Config:
        """
        Purpose:
            Provide a config implementation.
        Contract:
            Stores a stable marker for assertions.
        """
        def __init__(self) -> None:
            """
            Purpose:
                Initialize the marker.
            Contract:
                Sets marker to "primary".
            Returns:
                None.
            """
            self.marker = "primary"

    class _Service:
        """
        Purpose:
            Provide a service with a SpellMap dependency.
        Contract:
            Stores the resolved config instance.
        """
        def __init__(
                self,
                cfg=SpellMap(spell=None, spellframe=IConfig, binding_name="PRIMARY"),
        ) -> None:
            """
            Purpose:
                Capture the config dependency.
            Contract:
                Stores the config on the instance.
            Args:
                cfg: Injected config instance.
            Returns:
                None.
            """
            self.cfg = cfg

    spellbook = Spellbook()
    config = spellbook.get_configuration()
    config.set_property("phase_scheduler_workers_per_spellbook", 1)

    spellbook.bind(
        spell=_Config,
        existence=Existence.unique,
        permissions="create",
        spellframe=IConfig,
        binding_name="primary",
    )
    spellbook.bind(
        spell=_Service,
        existence=Existence.many,
        permissions="create",
    )

    conduit = spellbook.conjure(name="root")
    try:
        instance = conduit.meld(spell=_Service)
        assert isinstance(instance.cfg, _Config)
        assert instance.cfg.marker == "primary"
    finally:
        conduit.cleanup()


def test_collection_di_by_list_protocol_includes_multiple_bindings() -> None:
    """
    Purpose:
        Validate list[Protocol] DI includes multiple bindings.
    Contract:
        - All bound implementations appear in the injected list.
    Returns:
        None.
    Raises:
        AssertionError: If the handler list is incomplete.
    """
    class IHandler(Protocol):
        """
        Purpose:
            Provide a protocol spellframe for handler DI.
        Contract:
            Acts as a DI grouping key.
        """
        pass

    class _HandlerA:
        """
        Purpose:
            Provide a first handler implementation.
        Contract:
            Stores a stable marker for assertions.
        """
        def __init__(self) -> None:
            """
            Purpose:
                Initialize the handler marker.
            Contract:
                Sets marker to "A".
            Returns:
                None.
            """
            self.marker = "A"

    class _HandlerB:
        """
        Purpose:
            Provide a second handler implementation.
        Contract:
            Stores a stable marker for assertions.
        """
        def __init__(self) -> None:
            """
            Purpose:
                Initialize the handler marker.
            Contract:
                Sets marker to "B".
            Returns:
                None.
            """
            self.marker = "B"

    class _Service:
        """
        Purpose:
            Provide a service that depends on handler collection.
        Contract:
            Stores the handlers for assertions.
        """
        def __init__(self, handlers: list[IHandler]) -> None:
            """
            Purpose:
                Capture the handler list for assertions.
            Contract:
                Stores the handlers on the instance.
            Args:
                handlers: Injected handler list.
            Returns:
                None.
            """
            self.handlers = handlers

    spellbook = Spellbook()
    config = spellbook.get_configuration()
    config.set_property("phase_scheduler_workers_per_spellbook", 1)

    spellbook.bind(
        spell=_HandlerA,
        existence=Existence.unique,
        permissions="create",
        spellframe=IHandler,
        binding_name="a",
    )
    spellbook.bind(
        spell=_HandlerB,
        existence=Existence.unique,
        permissions="create",
        spellframe=IHandler,
        binding_name="b",
    )
    spellbook.bind(
        spell=_Service,
        existence=Existence.many,
        permissions="create",
    )

    conduit = spellbook.conjure(name="root")
    try:
        instance = conduit.meld(spell=_Service)
        markers = {handler.marker for handler in instance.handlers}
        assert markers == {"A", "B"}
    finally:
        conduit.cleanup()


def test_meld_by_spell_id_returns_existing_instance() -> None:
    """
    Purpose:
        Validate spell_id resolution for existing instances.
    Contract:
        - meld(spell_id) returns the bound existing object.
    Returns:
        None.
    Raises:
        AssertionError: If the existing object is not returned.
    """
    class _Config:
        """
        Purpose:
            Provide a configuration object for existing instance DI.
        Contract:
            Stores a stable marker for assertions.
        """
        def __init__(self, label: str) -> None:
            """
            Purpose:
                Initialize the config label.
            Contract:
                Stores the provided label.
            Args:
                label: Label assigned to the config instance.
            Returns:
                None.
            """
            self.label = label

    existing = _Config("existing")

    spellbook = Spellbook()
    config = spellbook.get_configuration()
    config.set_property("phase_scheduler_workers_per_spellbook", 1)

    spell_id = spellbook.bind(
        spell=existing,
        existence=Existence.unique,
        permissions="create",
        spellframe="config",
    )

    conduit = spellbook.conjure(name="root")
    try:
        resolved = conduit.meld(spell_id=spell_id)
        assert resolved is existing
    finally:
        conduit.cleanup()


def test_meld_by_missing_spell_id_raises_keyerror() -> None:
    """
    Purpose:
        Validate spell_id lookups raise for missing IDs.
    Contract:
        - meld(spell_id) raises KeyError when the id is unknown.
    Returns:
        None.
    Raises:
        AssertionError: If KeyError is not raised.
    """
    class _Service:
        """
        Purpose:
            Provide a bound spell to ensure the spellbook is initialized.
        Contract:
            Stores a stable marker for assertions.
        """
        def __init__(self) -> None:
            """
            Purpose:
                Initialize the marker.
            Contract:
                Sets marker to "svc".
            Returns:
                None.
            """
            self.marker = "svc"

    spellbook = Spellbook()
    config = spellbook.get_configuration()
    config.set_property("phase_scheduler_workers_per_spellbook", 1)

    spellbook.bind(
        spell=_Service,
        existence=Existence.unique,
        permissions="create",
    )

    conduit = spellbook.conjure(name="root")
    try:
        with pytest.raises(KeyError):
            conduit.meld(spell_id="missing-spell-id")
    finally:
        conduit.cleanup()


@pytest.mark.skip(reason="SpellIndex.update reserved for mutation pipeline; not used in current runtime.")
def test_spellindex_update_propagates_owned_id_map_for_meld() -> None:
    """
    Purpose:
        Validate SpellIndex.update updates owned spell_id resolution for meld.
    Contract:
        - Meld resolves by the new spell_id after update.
        - The old spell_id no longer resolves (KeyError).
    Returns:
        None.
    Raises:
        AssertionError: If resolution does not follow updated ids.
    """
    class _Service:
        """
        Purpose:
            Provide a class spell for owned update integration.
        Contract:
            Stores a stable marker for assertions.
        """
        def __init__(self) -> None:
            """
            Purpose:
                Initialize the marker.
            Contract:
                Sets marker to "owned".
            Returns:
                None.
            """
            self.marker = "owned"

    spellbook = Spellbook()
    config = spellbook.get_configuration()
    config.set_property("phase_scheduler_workers_per_spellbook", 1)

    spellbook.bind(
        spell=_Service,
        existence=Existence.unique,
        permissions="create",
    )

    conduit = spellbook.conjure(name="root")
    try:
        spell_index = next(iter(spellbook.spells.keys()))
        old_id = spell_index.selected_spell_id
        new_id = f"{old_id}-v2"

        spell_index.update(new_id)

        instance = conduit.meld(spell_id=new_id)
        assert isinstance(instance, _Service)
        assert instance.marker == "owned"

        with pytest.raises(KeyError):
            conduit.meld(spell_id=old_id)
    finally:
        conduit.cleanup()


@pytest.mark.skip(reason="SpellIndex.update reserved for mutation pipeline; not used in current runtime.")
def test_spellindex_update_propagates_contracted_id_map_for_meld() -> None:
    """
    Purpose:
        Validate SpellIndex.update updates contracted spell_id resolution for meld.
    Contract:
        - Borrower meld resolves by the new spell_id after update.
        - The old spell_id no longer resolves on the borrower (KeyError).
    Returns:
        None.
    Raises:
        AssertionError: If resolution does not follow updated ids.
    """
    class _Service:
        """
        Purpose:
            Provide a class spell for contracted update integration.
        Contract:
            Stores a stable marker for assertions.
        """
        def __init__(self) -> None:
            """
            Purpose:
                Initialize the marker.
            Contract:
                Sets marker to "contracted".
            Returns:
                None.
            """
            self.marker = "contracted"

    configuration = SpellbookConfiguration()
    apply_dynamic_defaults_for_spellbook_configuration(configuration)
    configuration.set_property("phase_scheduler_workers_per_spellbook", 1)

    owner_book = Spellbook(configuration=configuration)
    borrower_book = Spellbook(configuration=configuration)
    spell_id = owner_book.bind(
        spell=_Service,
        existence=Existence.unique,
        permissions="create",
    )

    owner = owner_book.conjure(dynamic=True, name="owner")
    borrower = borrower_book.conjure(dynamic=True, name="borrower")
    try:
        assert owner.link(borrower) is True
        with borrower.transaction("link", conduits=[borrower, owner]):
            borrower.add_spell_to_contract(
                spell_id=spell_id,
                conduit=owner,
                permissions="create",
            )

        spell_index = next(iter(owner_book.spells.keys()))
        old_id = spell_index.selected_spell_id
        new_id = f"{old_id}-v2"

        spell_index.update(new_id)

        instance = borrower.meld(spell_id=new_id)
        assert isinstance(instance, _Service)
        assert instance.marker == "contracted"

        with pytest.raises(KeyError):
            borrower.meld(spell_id=old_id)
    finally:
        borrower.cleanup()
        owner.cleanup()
