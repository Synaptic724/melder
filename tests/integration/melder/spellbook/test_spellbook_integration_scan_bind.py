from __future__ import annotations

import importlib

import pytest

from melder.aether.aether import Aether
from melder.nexus.nexus import Nexus
from melder.aether.conduit.conduit import Conduit
from melder.aether.spellbook.spellbook import Spellbook
from tests.mocks.spellbook import scan_bind_module_bad_metadata
from tests.mocks.spellbook import scan_bind_module_core
from tests.mocks.spellbook import scan_bind_module_duplicate
from tests.mocks.spellbook import scan_bind_module_empty
from tests.mocks.spellbook import scan_bind_module_lambda
from tests.mocks.spellbook import scan_bind_module_lambda_invalid
from tests.mocks.spellbook import scan_bind_module_reexport
from tests.mocks.spellbook import scan_bind_module_wrapped


from tests._frame_posture_test_support import (
    apply_dynamic_defaults_for_spellbook_configuration,
    set_frame_rift_enabled_for_spellbook_configuration,
)
@pytest.fixture(autouse=True)
def reset_aether_singleton_for_integration_scan_bind() -> None:
    """
    Purpose:
        Ensure scan_bind integration tests start with a clean Aether singleton.
    Contract:
        - Resets the Aether singleton before the test runs.
        - Rebinds Spellbook._aether and Conduit._aether to the new instance.
        - Resets the singleton again after the test for isolation.
    Returns:
        None.
    """
    Nexus._reset_singleton_for_tests()
    Aether._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether
    yield
    Nexus._reset_singleton_for_tests()
    Aether._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether


def _make_spellbook() -> Spellbook:
    """
    Purpose:
        Create a Spellbook configured for integration scan tests.
    Contract:
        Sets phase scheduler workers to a deterministic value.
    Returns:
        Spellbook: Configured Spellbook instance.
    """
    spellbook = Spellbook()
    config = spellbook.get_configuration()
    apply_dynamic_defaults_for_spellbook_configuration(config)
    config.set_property("phase_scheduler_workers_per_spellbook", 1)
    return spellbook


def test_scan_bind_integration_binds_only_marked_objects() -> None:
    """
    Purpose:
        Validate scan binds only scan_bind-decorated objects in a module.
    Contract:
        - Decorated objects are bound and returned as spell ids.
        - Undecorated objects remain unbound.
    Returns:
        None.
    """
    spellbook = _make_spellbook()

    spell_ids = spellbook.scan(scan_bind_module_core)

    assert len(spell_ids) == 3
    assert len(spellbook.spells) == 3

    conduit = spellbook.conjure(name="scan_root_marked")
    try:
        instance = conduit.meld(spellframe="scan_core", binding_name="alpha")
        assert instance.marker == "alpha"
        with pytest.raises(KeyError):
            conduit.meld(spell=scan_bind_module_core.ScanCoreIgnored)
    finally:
        conduit.permanent_cleanup()


def test_scan_bind_integration_rejects_reexported_objects() -> None:
    """
    Purpose:
        Ensure scan rejects re-exported decorated objects.
    Contract:
        Scanning a module that only re-exports a decorated object raises ValueError.
    Returns:
        None.
    """
    spellbook = _make_spellbook()

    with pytest.raises(ValueError):
        spellbook.scan(scan_bind_module_reexport)


def test_scan_bind_integration_duplicate_binding_raises() -> None:
    """
    Purpose:
        Ensure duplicate binding keys raise during scan binding.
    Contract:
        Scanning a module with duplicate binding metadata raises RuntimeError.
    Returns:
        None.
    """
    spellbook = _make_spellbook()

    with pytest.raises(RuntimeError):
        spellbook.scan(scan_bind_module_duplicate)


def test_scan_bind_integration_rescan_raises() -> None:
    """
    Purpose:
        Validate re-scanning the same module raises on duplicate registration.
    Contract:
        The first scan succeeds; a second scan raises RuntimeError.
    Returns:
        None.
    """
    spellbook = _make_spellbook()

    spellbook.scan(scan_bind_module_core)

    with pytest.raises(RuntimeError):
        spellbook.scan(scan_bind_module_core)


def test_scan_bind_integration_reimport_raises() -> None:
    """
    Purpose:
        Validate re-importing and re-scanning a module raises on duplicates.
    Contract:
        Scanning a reloaded module after a prior scan raises RuntimeError.
    Returns:
        None.
    """
    spellbook = _make_spellbook()
    module = importlib.reload(scan_bind_module_core)

    spellbook.scan(module)

    reloaded = importlib.reload(scan_bind_module_core)
    with pytest.raises(RuntimeError):
        spellbook.scan(reloaded)


def test_conduit_scan_integration_binds_after_conjure() -> None:
    """
    Purpose:
        Validate direct conduit-side scan binds decorated objects after conjure.
    Contract:
        Conduit.scan opens its own binding transaction when one is not already
        active, then returns spell ids.
    Returns:
        None.
    """
    spellbook = _make_spellbook()
    conduit = spellbook.conjure(name="scan_root")
    try:
        spell_ids = conduit.scan(scan_bind_module_core)
        assert len(spell_ids) == 3
        assert len(spellbook.spells) == 3
        spell = conduit.get_spell_by_id(spell_ids[0])
        assert spell is not None
        assert spell.validation_result_phase4 is not None
    finally:
        conduit.permanent_cleanup()


def test_scan_bind_integration_returns_ids_in_module_order() -> None:
    """
    Purpose:
        Validate scan returns spell ids in module definition order.
    Contract:
        Returned spell_ids match the order of decorated objects in the module.
    Returns:
        None.
    """
    spellbook = _make_spellbook()

    spell_ids = spellbook.scan(scan_bind_module_core)
    conduit = spellbook.conjure(name="scan_root_order")
    try:
        first = conduit.meld(spell=spell_ids[0])
        second = conduit.meld(spell=spell_ids[1])
        third = conduit.meld(spell=spell_ids[2])
        assert first.marker == "alpha"
        assert second.marker == "beta"
        assert third == "hello"
    finally:
        conduit.permanent_cleanup()


def test_scan_bind_integration_empty_module_returns_empty() -> None:
    """
    Purpose:
        Validate scanning a module with no scan_bind targets returns an empty list.
    Contract:
        No spells are bound and an empty list is returned.
    Returns:
        None.
    """
    spellbook = _make_spellbook()

    spell_ids = spellbook.scan(scan_bind_module_empty)

    assert spell_ids == []
    assert len(spellbook.spells) == 0


def test_scan_bind_integration_conjure_meld_class_by_binding() -> None:
    """
    Purpose:
        Validate end-to-end scan -> conjure -> meld for class spells by binding.
    Contract:
        Conduit.meld resolves the scanned class and returns the correct marker.
    Returns:
        None.
    """
    spellbook = _make_spellbook()
    spellbook.scan(scan_bind_module_core)
    conduit = spellbook.conjure(name="scan_root_class")
    try:
        instance = conduit.meld(spellframe="scan_core", binding_name="alpha")
        assert instance.marker == "alpha"
    finally:
        conduit.permanent_cleanup()


def test_scan_bind_integration_conjure_meld_class_by_spell_id() -> None:
    """
    Purpose:
        Validate end-to-end scan -> conjure -> meld for class spells by spell_id.
    Contract:
        Conduit.meld resolves by spell_id and returns the correct marker.
    Returns:
        None.
    """
    spellbook = _make_spellbook()
    spell_ids = spellbook.scan(scan_bind_module_core)
    spell_id = spell_ids[1]
    conduit = spellbook.conjure(name="scan_root_class_id")
    try:
        instance = conduit.meld(spell=spell_id)
        assert instance.marker == "beta"
    finally:
        conduit.permanent_cleanup()


def test_scan_bind_integration_conjure_meld_function_by_binding() -> None:
    """
    Purpose:
        Validate end-to-end scan -> conjure -> meld for function spells by binding.
    Contract:
        Conduit.meld executes the scanned function and returns its value.
    Returns:
        None.
    """
    spellbook = _make_spellbook()
    spellbook.scan(scan_bind_module_core)
    conduit = spellbook.conjure(name="scan_root_function")
    try:
        result = conduit.meld(spellframe="scan_factory", binding_name="message_factory")
        assert result == "hello"
    finally:
        conduit.permanent_cleanup()


def test_scan_bind_integration_lambda_unique_cached() -> None:
    """
    Purpose:
        Validate scan_bind supports lambda factories with unique existence.
    Contract:
        - Lambda is invoked once.
        - Conduit.meld returns the cached instance on subsequent calls.
    Returns:
        None.
    """
    spellbook = _make_spellbook()
    scan_bind_module_lambda.reset_lambda_calls()
    spell_ids = spellbook.scan(scan_bind_module_lambda)
    spell_id = spell_ids[0]
    conduit = spellbook.conjure(name="scan_root_lambda")
    try:
        first = conduit.meld(spell=spell_id)
        second = conduit.meld(spell=spell_id)
        assert first is second
        assert scan_bind_module_lambda.LAMBDA_CALLS == ["called"]
    finally:
        conduit.permanent_cleanup()


def test_scan_bind_integration_lambda_missing_binding_name_raises() -> None:
    """
    Purpose:
        Ensure scan rejects lambdas without a binding name.
    Contract:
        Scanning a module with an unnamed lambda raises ValueError.
    Returns:
        None.
    """
    spellbook = _make_spellbook()

    with pytest.raises(ValueError):
        spellbook.scan(scan_bind_module_lambda_invalid)


def test_scan_bind_integration_bad_metadata_raises() -> None:
    """
    Purpose:
        Ensure scan fails on corrupted scan_bind metadata.
    Contract:
        Scanning a module with invalid metadata raises TypeError.
    Returns:
        None.
    """
    spellbook = _make_spellbook()

    with pytest.raises(TypeError):
        spellbook.scan(scan_bind_module_bad_metadata)


def test_scan_bind_integration_bad_metadata_does_not_bind() -> None:
    """
    Purpose:
        Validate no spells are bound when scan fails on bad metadata.
    Contract:
        Spellbook registry remains empty after metadata failure.
    Returns:
        None.
    """
    spellbook = _make_spellbook()

    with pytest.raises(TypeError):
        spellbook.scan(scan_bind_module_bad_metadata)

    assert len(spellbook.spells) == 0


def test_scan_bind_integration_wrapped_module_binds_expected_targets() -> None:
    """
    Purpose:
        Validate scan_bind metadata survives wraps-based decorators.
    Contract:
        - Functions wrapped with functools.wraps remain bindable.
        - Bare wrappers drop metadata when scan_bind is inner.
    Returns:
        None.
    """
    spellbook = _make_spellbook()

    spell_ids = spellbook.scan(scan_bind_module_wrapped)
    assert len(spell_ids) == 2

    conduit = spellbook.conjure(name="scan_root_wrapped")
    try:
        outer = conduit.meld(spellframe="scan_wrapped", binding_name="outer_no_wrap")
        inner_wraps = conduit.meld(spellframe="scan_wrapped", binding_name="inner_wraps")
        assert outer == "outer_no_wrap"
        assert inner_wraps == "inner_wraps"
        with pytest.raises(KeyError):
            conduit.meld(spellframe="scan_wrapped", binding_name="inner_no_wrap")
    finally:
        conduit.permanent_cleanup()


def test_scan_bind_integration_non_module_type_error() -> None:
    """
    Purpose:
        Validate scan rejects non-module inputs.
    Contract:
        Spellbook.scan raises TypeError for non-module arguments.
    Returns:
        None.
    """
    spellbook = _make_spellbook()

    with pytest.raises(TypeError):
        spellbook.scan("not_a_module")


def test_scan_bind_integration_reexport_does_not_bind() -> None:
    """
    Purpose:
        Validate re-export failures do not bind any spells.
    Contract:
        Spellbook registry remains empty after re-export rejection.
    Returns:
        None.
    """
    spellbook = _make_spellbook()

    with pytest.raises(ValueError):
        spellbook.scan(scan_bind_module_reexport)

    assert len(spellbook.spells) == 0


def test_scan_bind_integration_scan_multiple_modules() -> None:
    """
    Purpose:
        Validate sequential scans across modules accumulate bindings.
    Contract:
        Total bound spells equals the sum of scanned module targets.
    Returns:
        None.
    """
    spellbook = _make_spellbook()

    spellbook.scan(scan_bind_module_core)
    spellbook.scan(scan_bind_module_wrapped)

    assert len(spellbook.spells) == 5

#@pytest.mark.skip(reason="Stalls; revisit after phase scheduler investigation. .PhaseTimeoutError: Phase 'root_blueprints' exceeded barrier timeout (60000 ms). Resolution pipeline aborted.")
def test_conduit_scan_integration_melds_after_scan() -> None:
    """
    Purpose:
        Validate Conduit.scan supports subsequent meld calls.
    Contract:
        Conduit.meld resolves scanned class spells after scan.
    Returns:
        None.
    """
    # This test fails due to phase 5 check without base check root check
    spellbook = _make_spellbook()
    conduit = spellbook.conjure(name="scan_root_meld")
    try:
        with conduit.transaction("bind"):
            spell_ids = conduit.scan(scan_bind_module_core)
        instance = conduit.meld(spell=spell_ids[1])
        assert instance.marker == "beta"
    finally:
        conduit.permanent_cleanup()

#@pytest.mark.skip(reason="Stalls; revisit after phase scheduler investigation. .PhaseTimeoutError: Phase 'root_blueprints' exceeded barrier timeout (60000 ms). Resolution pipeline aborted.")
def test_scan_bind_integration_spellbook_scan_after_conjure_registers_in_aether() -> None:
    """
    Purpose:
        Validate scan after conjure registers spells into the Aether registry.
    Contract:
        inspect_spell returns the scanned spell_id after conjure + scan.
    Returns:
        None.
    """
    spellbook = _make_spellbook()
    conduit = spellbook.conjure(name="scan_root_after_conjure")
    try:
        with spellbook.transaction("bind"):
            spell_ids = spellbook.scan(scan_bind_module_core)
        found_id = spellbook.inspect_spell(scan_bind_module_core.ScanCoreAlpha)
        assert found_id == spell_ids[0]
        instance = conduit.meld(spell=spell_ids[0])
        assert instance.marker == "alpha"
    finally:
        conduit.permanent_cleanup()


def test_conduit_scan_after_conjure_registers_in_aether() -> None:
    """
    Purpose:
        Validate conduit.scan after conjure registers spells into the Aether registry.
    Contract:
        inspect_spell returns the scanned spell_id after conduit scan.
    Returns:
        None.
    """
    spellbook = _make_spellbook()
    conduit = spellbook.conjure(name="scan_root_after_conduit_scan")
    try:
        with conduit.transaction("bind"):
            spell_ids = conduit.scan(scan_bind_module_core)
        found_id = spellbook.inspect_spell(scan_bind_module_core.ScanCoreBeta)
        assert found_id == spell_ids[1]
    finally:
        conduit.permanent_cleanup()


def test_scan_bind_integration_post_conjure_scan_updates_passive_nexus_records() -> None:
    """
    Purpose:
        Validate post-conjure scan publishes and later removes passive Nexus spell records.
    Contract:
        - A Rift-enabled Spellbook publishes one passive Nexus spell record per
          scanned spell after conjure.
        - conduit cleanup removes the scanned spell records from passive Nexus.
    Returns:
        None.
    """
    spellbook = _make_spellbook()
    spellbook_id = spellbook.id
    config = spellbook.get_configuration()
    set_frame_rift_enabled_for_spellbook_configuration(config, True)
    frame_name = spellbook._aetheric_frame_name

    conduit = spellbook.conjure(name="scan_root_nexus")
    spell_ids = []
    try:
        with spellbook.transaction("bind"):
            spell_ids = spellbook.scan(scan_bind_module_core)

        descriptor = Nexus()._get_required_frame_descriptor(frame_name)
        for spell_id in spell_ids:
            assert (spellbook_id, spell_id) in descriptor.spell_records_by_key
    finally:
        conduit.permanent_cleanup()

    descriptor = Nexus()._get_required_frame_descriptor(frame_name)
    for spell_id in spell_ids:
        assert (spellbook_id, spell_id) not in descriptor.spell_records_by_key
