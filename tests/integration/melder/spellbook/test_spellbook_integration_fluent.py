from __future__ import annotations

import pytest

from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.aether.spellbook.configuration.spellbook_configuration import SpellbookConfiguration
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spellbook import Spellbook
from melder.utilities.custom_exceptions.spell_space_scope_error import SpellSpaceScopeError
from tests.mocks.spellbook.core_classes import BasicConfig
from tests.mocks.spellbook.core_classes import BasicService
from tests.mocks.spellbook.protocols import IService


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


def test_spellbook_fluent_bind_inline_arguments_resolve() -> None:
    """
    Purpose:
        Validate fluent binding accepts inline bind arguments.
    Contract:
        - Inline existence, permissions, spellframe, and binding_name are applied.
        - Spellbook lookup resolves by spellframe and binding_name.
    Returns:
        None.
    Raises:
        AssertionError: If fluent inline binding does not resolve.
    """
    spellbook = Spellbook()
    config = spellbook.get_configuration()
    config.set_property("phase_scheduler_workers_per_spellbook", 1)

    binder = spellbook.create_binder()
    spell_id = binder.bind(
        BasicService,
        existence=Existence.unique,
        permissions="read",
        spellframe=IService,
        binding_name="primary",
    ).finalize()

    conduit = spellbook.conjure(name="root")
    try:
        instance = conduit.meld(spellframe=IService, binding_name="primary")
        assert isinstance(instance, BasicService)

        spell_index = spellbook.find_spell_index(IService, BasicService.__name__, "primary")
        assert spellbook.get_spell_permissions(spell_index) == "read"
        assert conduit.meld(spell=spell_id) is instance
    finally:
        conduit.cleanup()


def test_spellbook_fluent_with_permissions_sets_permissions() -> None:
    """
    Purpose:
        Validate fluent permissions update the bound spell metadata.
    Contract:
        - with_permissions updates the stored permissions string.
    Returns:
        None.
    Raises:
        AssertionError: If permissions are not persisted.
    """
    spellbook = Spellbook()
    config = spellbook.get_configuration()
    config.set_property("phase_scheduler_workers_per_spellbook", 1)

    binder = spellbook.create_binder()
    spell_id = binder.bind(BasicService).with_permissions("read").finalize()

    conduit = spellbook.conjure(name="root")
    try:
        assert isinstance(conduit.meld(spell=spell_id), BasicService)
        spell_index = spellbook.find_spell_index("BasicService", BasicService.__name__, "__default__")
        assert spellbook.get_spell_permissions(spell_index) == "read"
    finally:
        conduit.cleanup()


def test_spellbook_fluent_with_kwargs_overrides_hooks() -> None:
    """
    Purpose:
        Validate with_kwargs overrides existing hook lists.
    Contract:
        - Later with_kwargs calls replace earlier hook lists.
    Returns:
        None.
    Raises:
        AssertionError: If overridden hooks still execute.
    """
    calls: list[str] = []

    def first_hook() -> None:
        """
        Purpose:
            Record the first pre-hook call.
        Contract:
            Appends "first" to calls.
        Returns:
            None.
        """
        calls.append("first")

    def second_hook() -> None:
        """
        Purpose:
            Record the replacement pre-hook call.
        Contract:
            Appends "second" to calls.
        Returns:
            None.
        """
        calls.append("second")

    spellbook = Spellbook()
    config = spellbook.get_configuration()
    config.set_property("phase_scheduler_workers_per_spellbook", 1)

    binder = spellbook.create_binder()
    spell_id = (
        binder.bind(BasicService, pre_hooks=[first_hook])
        .with_kwargs(pre_hooks=[second_hook])
        .finalize()
    )

    conduit = spellbook.conjure(name="root")
    try:
        _instance = conduit.meld(spell=spell_id)
        assert calls == ["second"]
    finally:
        conduit.cleanup()


def test_spellbook_fluent_multiple_hook_lists_preserve_order() -> None:
    """
    Purpose:
        Validate fluent hook lists preserve call order.
    Contract:
        - pre hooks run in the order provided.
        - activation hooks run once for unique spells.
        - post hooks run in the order provided.
    Returns:
        None.
    Raises:
        AssertionError: If hook ordering is incorrect.
    """
    calls: list[str] = []

    def pre_one() -> None:
        """
        Purpose:
            Record the first pre-hook call.
        Contract:
            Appends "pre-1" to calls.
        Returns:
            None.
        """
        calls.append("pre-1")

    def pre_two() -> None:
        """
        Purpose:
            Record the second pre-hook call.
        Contract:
            Appends "pre-2" to calls.
        Returns:
            None.
        """
        calls.append("pre-2")

    def activation_hook(instance: object) -> None:
        """
        Purpose:
            Record activation hook execution.
        Contract:
            Appends "activation" to calls.
        Args:
            instance: Newly created instance.
        Returns:
            None.
        """
        calls.append("activation")

    def post_one() -> None:
        """
        Purpose:
            Record the first post-hook call.
        Contract:
            Appends "post-1" to calls.
        Returns:
            None.
        """
        calls.append("post-1")

    def post_two() -> None:
        """
        Purpose:
            Record the second post-hook call.
        Contract:
            Appends "post-2" to calls.
        Returns:
            None.
        """
        calls.append("post-2")

    spellbook = Spellbook()
    config = spellbook.get_configuration()
    config.set_property("phase_scheduler_workers_per_spellbook", 1)

    binder = spellbook.create_binder()
    spell_id = (
        binder.bind(BasicService)
        .as_unique()
        .with_pre_hooks(pre_one, pre_two)
        .with_activation_hooks(activation_hook)
        .with_post_hooks(post_one, post_two)
        .finalize()
    )

    conduit = spellbook.conjure(name="root")
    try:
        first = conduit.meld(spell=spell_id)
        second = conduit.meld(spell=spell_id)
        assert first is second
        assert calls == [
            "pre-1",
            "pre-2",
            "activation",
            "post-1",
            "post-2",
            "pre-1",
            "pre-2",
            "post-1",
            "post-2",
        ]
    finally:
        conduit.cleanup()


def test_spellbook_fluent_as_many_creates_new_instances() -> None:
    """
    Purpose:
        Validate fluent as_many creates new instances.
    Contract:
        - Each meld returns a distinct instance.
    Returns:
        None.
    Raises:
        AssertionError: If instances are reused.
    """
    spellbook = Spellbook()
    config = spellbook.get_configuration()
    config.set_property("phase_scheduler_workers_per_spellbook", 1)

    binder = spellbook.create_binder()
    spell_id = binder.bind(BasicService).as_many().finalize()

    conduit = spellbook.conjure(name="root")
    try:
        first = conduit.meld(spell=spell_id)
        second = conduit.meld(spell=spell_id)
        assert first is not second
    finally:
        conduit.cleanup()


def test_spellbook_fluent_as_unique_per_conduit_reuses_per_conduit() -> None:
    """
    Purpose:
        Validate fluent unique_per_conduit scopes per conduit.
    Contract:
        - Root and lesser conduits do not share instances.
        - Each conduit reuses its own instance.
    Returns:
        None.
    Raises:
        AssertionError: If per-conduit scoping fails.
    """
    spellbook = Spellbook()
    config = spellbook.get_configuration()
    config.set_property("phase_scheduler_workers_per_spellbook", 1)

    binder = spellbook.create_binder()
    spell_id = binder.bind(BasicService).as_unique_per_conduit().finalize()

    conduit = spellbook.conjure(name="root")
    lesser = conduit.create_lesser_conduit()
    try:
        root_first = conduit.meld(spell=spell_id)
        root_second = conduit.meld(spell=spell_id)
        lesser_first = lesser.meld(spell=spell_id)
        lesser_second = lesser.meld(spell=spell_id)

        assert root_first is root_second
        assert lesser_first is lesser_second
        assert root_first is not lesser_first
    finally:
        conduit.cleanup()


def test_spellbook_fluent_as_unique_per_conduit_lineage_shares_lineage() -> None:
    """
    Purpose:
        Validate fluent unique_per_conduit_lineage scopes by lineage.
    Contract:
        - Root and lesser conduits in the same lineage share instances.
    Returns:
        None.
    Raises:
        AssertionError: If lineage scoping fails.
    """
    spellbook = Spellbook()
    config = spellbook.get_configuration()
    config.set_property("phase_scheduler_workers_per_spellbook", 1)

    binder = spellbook.create_binder()
    spell_id = binder.bind(BasicService).as_unique_per_conduit_lineage().finalize()

    conduit = spellbook.conjure(name="root")
    lesser = conduit.create_lesser_conduit()
    try:
        root_instance = conduit.meld(spell=spell_id)
        lesser_instance = lesser.meld(spell=spell_id)
        assert root_instance is lesser_instance
    finally:
        conduit.cleanup()


def test_spellbook_fluent_as_unique_per_spell_space_scopes_instances() -> None:
    """
    Purpose:
        Validate fluent unique_per_spell_space scopes by spellspace.
    Contract:
        - Instances are reused within a spellspace.
        - Instances differ across spellspaces.
        - Missing spellspace raises SpellSpaceScopeError.
    Returns:
        None.
    Raises:
        AssertionError: If spellspace scoping fails.
    """
    spellbook = Spellbook()
    config = spellbook.get_configuration()
    config.set_property("phase_scheduler_workers_per_spellbook", 1)

    binder = spellbook.create_binder()
    spell_id = binder.bind(BasicService).as_unique_per_spell_space().finalize()

    conduit = spellbook.conjure(name="root")
    try:
        with conduit.enter_spellspace():
            first = conduit.meld(spell=spell_id)
            second = conduit.meld(spell=spell_id)
            assert first is second

        with conduit.enter_spellspace():
            third = conduit.meld(spell=spell_id)
            assert third is not first

        with pytest.raises(SpellSpaceScopeError, match="SpellSpace"):
            conduit.meld(spell=spell_id)
    finally:
        conduit.cleanup()


def test_spellbook_fluent_as_unique_per_conduit_cluster_shares_across_cluster() -> None:
    """
    Purpose:
        Validate fluent unique_per_conduit_cluster sharing across clusters.
    Contract:
        - Conduits in the same cluster resolve the same instance.
    Returns:
        None.
    Raises:
        AssertionError: If cluster sharing fails.
    """
    configuration = SpellbookConfiguration()
    apply_dynamic_defaults_for_spellbook_configuration(configuration)
    configuration.set_property("phase_scheduler_workers_per_spellbook", 1)

    owner_book = Spellbook(configuration=configuration)
    binder = owner_book.create_binder()
    spell_id = binder.bind(BasicService).as_unique_per_conduit_cluster().finalize()

    borrower_book = Spellbook(configuration=configuration)
    owner = owner_book.conjure(automatic=False, name="owner")
    borrower = borrower_book.conjure(automatic=False, name="borrower")
    try:
        owner.link(borrower)
        owner.create_cluster("cluster-a")
        owner.join_cluster("cluster-a")
        borrower.join_cluster("cluster-a")
        owner.refresh_cluster_shares()

        owner_instance = owner.meld(spell=spell_id)
        borrower_instance = borrower.meld(spell=spell_id)
        assert owner_instance is borrower_instance
    finally:
        borrower.cleanup()
        owner.cleanup()


def test_spellbook_fluent_with_existence_overrides_default() -> None:
    """
    Purpose:
        Validate with_existence overrides binder defaults.
    Contract:
        - with_existence applies the specified Existence for the binding.
    Returns:
        None.
    Raises:
        AssertionError: If the existence override is ignored.
    """
    spellbook = Spellbook()
    config = spellbook.get_configuration()
    config.set_property("phase_scheduler_workers_per_spellbook", 1)

    binder = spellbook.create_binder(default_existence=Existence.many, default_permissions="create")
    spell_id = binder.bind(BasicConfig).with_existence(Existence.unique).finalize()

    conduit = spellbook.conjure(name="root")
    try:
        first = conduit.meld(spell=spell_id)
        second = conduit.meld(spell=spell_id)
        assert first is second
    finally:
        conduit.cleanup()
