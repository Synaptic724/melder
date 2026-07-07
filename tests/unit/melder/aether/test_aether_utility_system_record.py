"""
Unit test for the AetherUtilitySystem emission seam: post-activation
mutations of the root logger policy re-emit the Aether twin so the record
never silently drifts from the live runtime surface.

Runs only on 3.14t (melder package root import chain).
"""
import logging

from melder.aether.aether import Aether
from melder.aether.aether_utility_system import AetherUtilitySystem
from melder.crystallizer.configuration.crystallizer_configuration import (
    CrystallizerConfiguration,
)
from melder.crystallizer.crystallizer import Crystallizer
from melder.nexus.nexus import Nexus


def test_post_activation_root_mutations_reemit_the_aether_twin():
    """
    Contract: a direct utility-system mutation AFTER crystallizer
    activation replaces the recorded root twin with the live truth
    (knob flip + default-logger presence), never drifting silently.
    """
    Aether._reset_singleton_for_tests()
    AetherUtilitySystem._reset_singleton_for_tests()
    Nexus._reset_singleton_for_tests()
    Crystallizer._reset_singleton_for_tests()
    Aether()
    try:
        configuration = CrystallizerConfiguration().with_defaults()
        configuration.activate()
        crystallizer = Crystallizer()
        crystallizer.activate(configuration)

        utility_system = AetherUtilitySystem()
        utility_system.set_channel_logger_activation_enabled(True)
        utility_system.register_default_logger(
            logging.getLogger("record-seam-test")
        )

        # Explicit record-contract read: the profile's root twin is the
        # documented single source of recorded root truth (no public
        # payload facade exists yet; tracked follow-up).
        twin = (
            crystallizer._persistence_system.active_profile._aether_crystal
        )
        assert twin is not None
        payload = twin.configuration_payload
        assert payload["channel_logger_activation_enabled"] is True
        assert payload["default_logger_present"] is True

        utility_system.clear_default_logger()
        twin = (
            crystallizer._persistence_system.active_profile._aether_crystal
        )
        payload = twin.configuration_payload
        assert payload["default_logger_present"] is False
    finally:
        Aether._reset_singleton_for_tests()
        AetherUtilitySystem._reset_singleton_for_tests()
        Nexus._reset_singleton_for_tests()
        Crystallizer._reset_singleton_for_tests()
