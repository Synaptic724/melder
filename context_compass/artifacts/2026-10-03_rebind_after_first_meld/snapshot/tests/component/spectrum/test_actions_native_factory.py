"""Real native Actions registration, center topology and explicit disposal contracts."""

from types import SimpleNamespace
from typing import TYPE_CHECKING

import pytest
from melder import Conduit, HookExecutionError

from melder_ops.command_center.spectrum.actions.action.action import Action
from melder_ops.command_center.spectrum.actions.action.collect import Collect
from melder_ops.command_center.spectrum.actions.action.distribute import Distribute
from melder_ops.command_center.spectrum.actions.action.gather import Gather
from melder_ops.command_center.spectrum.actions.action.hand_out import HandOut
from melder_ops.command_center.spectrum.actions.action.self_check import SelfCheck
from melder_ops.command_center.spectrum.bootstraps.actions_bootstrap import ActionsBootstrap
from melder_ops.command_center.spectrum.configurations.melder_configuration import MelderConfiguration
from melder_ops.command_center.spectrum.configurations.spectrum_configuration import SpectrumConfig
import melder_ops.command_center.spectrum.spectrum as spectrum_module
from tests.mocks.actions_factory import (
    ExplodingAction, FailingDistribute, FailingGather, PayloadAction, ReplacementGather,
)

if TYPE_CHECKING:
    from melder_ops.command_center.spectrum.spectrum import Spectrum


@pytest.fixture
def host(spectrum: Spectrum) -> Spectrum:
    """Configure the native host; the shared isolation fixture owns final cleanup."""
    spectrum.configure(SpectrumConfig().with_iris_logger_options(
        include_stream_mirror=False, include_system_stream_mirror=False,
    ))
    return spectrum


def action_root(host: Spectrum) -> Conduit:
    """Borrow the registration root from the host's public frame cloud."""
    return host.get_conduit().get_conduit_cloud().get_conduit("spectrum_actions")


@pytest.mark.parametrize("name,reference", [
    ("gather", Gather), ("distribute", Distribute), ("collect", Collect),
    ("handout", HandOut), ("self_check", SelfCheck),
])
def test_stock_class_lookup_needs_no_center_or_product(host: Spectrum, name: str, reference: type) -> None:
    """Bootstrap owns stock definitions and get_action returns the exact class."""
    root = action_root(host)
    assert host.actions.get_action(name) is reference
    assert not root.has_live_creation(spellframe="actions", binding_name=name)
    assert not root.get_conduit_cloud().has_conduit_name("default_actions")
    assert host.get_conduit().meld(spellframe="spectrum", binding_name="Actions") is host.actions


@pytest.mark.parametrize("name", ["default", "alpha", "worker team"])
def test_center_owns_its_named_action_lesser(host: Spectrum, name: str) -> None:
    """Center creation allocates the named lesser and explicit cleanup releases it."""
    center = host.create_command_center(name)
    cloud = host.get_conduit().get_conduit_cloud()
    assert cloud.get_conduit(f"{name}_actions").spellbook is action_root(host).spellbook
    center.cleanup()
    assert not cloud.has_conduit_name(f"{name}_actions")
    assert not action_root(host).cleaned


@pytest.mark.parametrize("method,args", [
    ("meld", ("self_check",)), ("gather", ("k", [])), ("distribute", ("k", object(), [])),
    ("create_collect_action", ("k",)), ("create_handout_action", ("k", object())), ("self_check", ()),
])
def test_construction_requires_an_existing_center(host: Spectrum, method: str, args: tuple) -> None:
    """None of the construction conveniences silently creates the default center."""
    with pytest.raises(KeyError, match="default"):
        getattr(host.actions, method)(*args)
    assert host.get_command_center_by_name("default") is None
    assert not action_root(host).get_conduit_cloud().has_conduit_name("default_actions")


def test_custom_registration_shares_the_exact_native_definition(host: Spectrum) -> None:
    """Register and class lookup work without centers and publish no creations."""
    identifier = host.actions.register_action("payload", PayloadAction)
    row = next(row for row in action_root(host).describe_spells_in_conduit()
               if row["spell_id"] == identifier)
    assert (row["spellframe"], row["binding_name"], row["existence"]) == ("actions", "payload", "many")
    assert row["owner_conduit_id"] == action_root(host).id
    assert host.get_conduit().find_contracted_spell(identifier) is not None
    assert host.actions.get_action("payload") is PayloadAction
    assert not action_root(host).has_live_creation(spellframe="actions", binding_name="payload")


def test_meld_creates_fresh_actions_with_exact_payloads(host: Spectrum) -> None:
    """Independent many creations preserve external inputs and native cleanup ownership."""
    center = host.create_command_center()
    host.actions.register_action("payload", PayloadAction)
    value = {"data": []}
    first = host.actions.meld("payload", override={"payload": value})
    second = host.actions.meld("payload", override={"payload": value})
    assert first is not second and first.execute() is value and second.execute() is value
    assert not action_root(host).has_live_creation(spellframe="actions", binding_name="payload")
    center.cleanup()
    assert first.cleaned and second.cleaned


def test_center_disposal_is_isolated_and_explicit_cleanup_remains_idempotent(host: Spectrum) -> None:
    """Retiring one center cannot dispose another center's action or shared definition."""
    first_center = host.create_command_center()
    second_center = host.create_command_center("second")
    host.actions.register_action("payload", PayloadAction)
    first = host.actions.meld("payload", override={"payload": 1})
    second = host.actions.meld("payload", command_center_name="second", override={"payload": 2})
    first.cleanup()
    first_center.cleanup()
    assert first.cleanup_count == 1 and second.execute() == 2
    assert host.actions.get_action("payload") is PayloadAction
    second_center.cleanup()
    assert second.cleanup_count == 1


def test_native_direct_registration_and_nested_scope_are_usable(host: Spectrum) -> None:
    """Users may bypass the facade while retaining discovery and their own scope lifetime."""
    host.create_command_center()
    root = action_root(host)
    root.bind(spell=PayloadAction, existence="many", spellframe="actions", binding_name="direct",
              disposal_method_names=["cleanup"])
    assert host.actions.get_action("direct") is PayloadAction
    parent = root.get_conduit_cloud().get_conduit("default_actions")
    child = parent.create_lesser_conduit(name="action_batch")
    product = child.meld(spellframe="actions", binding_name="direct", override={"payload": 3})
    assert product.execute() == 3
    child.cleanup()
    assert product.cleaned and not parent.cleaned
    host.actions.unregister_action("direct")
    assert "direct" not in host.actions.list_actions()


@pytest.mark.parametrize("reference", [Action, object, object()])
@pytest.mark.parametrize("direct", [False, True])
def test_native_hook_rejects_invalid_references(host: Spectrum, reference: object, direct: bool) -> None:
    """Admission validates references equally through facade and native bind."""
    with pytest.raises(HookExecutionError):
        if direct:
            action_root(host).bind(spell=reference, existence="many", spellframe="actions",
                                   binding_name="invalid", disposal_method_names=["cleanup"])
        else:
            host.actions.register_action("invalid", reference)
    assert "invalid" not in host.actions.list_actions()


def test_duplicate_requires_explicit_removal_and_contract_is_withdrawn(host: Spectrum) -> None:
    """Unregister removes only the selected share and leaves existing products alive."""
    center = host.create_command_center()
    identifier = host.actions.register_action("payload", PayloadAction)
    product = host.actions.meld("payload", override={"payload": 5})
    with pytest.raises(RuntimeError):
        host.actions.register_action("payload", PayloadAction)
    host.actions.unregister_action("payload")
    assert host.get_conduit().find_contracted_spell(identifier) is None
    assert product.execute() == 5
    with pytest.raises(KeyError):
        host.actions.get_action("payload")
    host.actions.register_action("payload", PayloadAction)
    assert host.actions.meld("payload", override={"payload": 6}).execute() == 6
    center.cleanup()
    assert product.cleaned


def test_convenience_gather_uses_replaced_binding_and_releases_its_creation(host: Spectrum) -> None:
    """The named registration controls construction even through a convenience call."""
    host.create_command_center()
    host.actions.unregister_action("gather")
    host.actions.register_action("gather", ReplacementGather)
    assert host.actions.gather("k", []) == {"replacement": "k"}
    scope = action_root(host).get_conduit_cloud().get_conduit("default_actions")
    assert not scope.has_live_creation(spellframe="actions", binding_name="gather")
    assert host.actions.get_action("gather") is ReplacementGather


def test_stock_convenience_results_and_payload_identity_are_preserved(host: Spectrum) -> None:
    """Broadcast and gather keep ordinary behavior while releasing completed temporaries."""
    host.create_command_center("alpha")
    scope = action_root(host).get_conduit_cloud().get_conduit("alpha_actions")
    first = SimpleNamespace(_id="first", public_inventory={"item": 4})
    second = SimpleNamespace(_id="second", public_inventory={"item": 8})
    assert host.actions.gather("item", [first, second], consume=False,
                               command_center_name="alpha") == {"first": 4, "second": 8}
    payload = {"x": []}
    assert host.actions.distribute("broadcast", payload, [first, second], command_center_name="alpha")
    assert first.public_inventory["broadcast"] is payload
    assert second.public_inventory["broadcast"] is payload
    assert not scope.has_live_creation(spellframe="actions", binding_name="gather")
    assert not scope.has_live_creation(spellframe="actions", binding_name="distribute")


@pytest.mark.parametrize("name,reference,args", [
    ("gather", FailingGather, ("k", [])), ("distribute", FailingDistribute, ("k", object(), [])),
])
def test_execution_failure_releases_only_the_temporary_creation(
    host: Spectrum, name: str, reference: type, args: tuple,
) -> None:
    """Finally cleanup and single purge run on failure while a separate live action survives."""
    host.create_command_center()
    host.actions.unregister_action(name)
    host.actions.register_action(name, reference)
    scope = action_root(host).get_conduit_cloud().get_conduit("default_actions")
    inputs = {"key": "other", "target_agents": []}
    if name == "distribute":
        inputs["value"] = object()
    retained = host.actions.meld(name, override=inputs)
    with pytest.raises(ValueError, match="execution refused"):
        getattr(host.actions, name)(*args)
    assert not retained.cleaned
    assert scope.purge(retained, spellframe="actions", binding_name=name, purge_all=False) == 1
    assert not scope.has_live_creation(spellframe="actions", binding_name=name)


def test_returned_stock_actions_use_selected_center_and_keep_explicit_cleanup(host: Spectrum) -> None:
    """The three returned-product conveniences are scoped without executing on a foreign thread."""
    center = host.create_command_center("alpha")
    collect = host.actions.create_collect_action("k", consume=False, command_center_name="alpha")
    payload = object()
    handout = host.actions.create_handout_action("k", payload, command_center_name="alpha")
    check = host.actions.self_check(command_center_name="alpha")
    assert isinstance(collect, Collect) and collect.consume is False and collect.get_results() == {}
    assert isinstance(handout, HandOut) and handout.value_to_store is payload
    assert isinstance(check, SelfCheck)
    collect.cleanup()
    handout.cleanup()
    check.cleanup()
    center.cleanup()
    assert collect.cleaned and handout.cleaned and check.cleaned


def test_constructor_failure_publishes_no_action_creation(host: Spectrum) -> None:
    """Failed melding leaves the definition available and does not cache a partial product."""
    host.create_command_center()
    host.actions.register_action("explodes", ExplodingAction)
    with pytest.raises(Exception, match="action construction refused"):
        host.actions.meld("explodes")
    scope = action_root(host).get_conduit_cloud().get_conduit("default_actions")
    assert not scope.has_live_creation(spellframe="actions", binding_name="explodes")
    assert host.actions.get_action("explodes") is ExplodingAction


def test_native_action_scope_collision_compensates_only_new_center_allocations(host: Spectrum) -> None:
    """A user-held native name refuses center creation without deleting that user's scope."""
    cloud = host.get_conduit().get_conduit_cloud()
    held = host.get_conduit().create_lesser_conduit(name="alpha_actions")
    with pytest.raises(ValueError):
        host.create_command_center("alpha")
    assert cloud.get_conduit("alpha_actions") is held
    assert not cloud.has_conduit_name("alpha_toolbox")
    assert not cloud.has_conduit_name(f"{host.get_conduit().name}/center/alpha")
    held.cleanup()
    center = host.create_command_center("alpha")
    center.cleanup()
    assert not cloud.has_conduit_name("alpha_actions")


def test_custom_framework_root_name_is_used_for_action_contracts() -> None:
    """Sharing follows the configured peer name rather than a hardcoded framework name."""
    host = spectrum_module.Spectrum(melder_config=MelderConfiguration(spellbook_name="application"))
    host.configure()
    identifier = host.actions.register_action("payload", PayloadAction)
    assert host.get_conduit().name == "application"
    assert host.get_conduit().find_contracted_spell(identifier) is not None
    host.actions.unregister_action("payload")
    assert host.get_conduit().find_contracted_spell(identifier) is None


def test_actions_root_collision_does_not_adopt_an_unrelated_root(host: Spectrum) -> None:
    """Bootstrap name refusal preserves the already-owned Actions root and stock inventory."""
    existing = action_root(host)
    with pytest.raises(RuntimeError, match="Spell ID collision"):
        ActionsBootstrap.create_root(host.get_conduit())
    assert action_root(host) is existing and not existing.cleaned
    assert host.actions.get_action("gather") is Gather
