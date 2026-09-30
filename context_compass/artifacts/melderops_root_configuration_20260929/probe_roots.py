"""Probe how Melder's process roots and MelderOps' setup behave when a root is already configured.

Each scenario runs in its own interpreter (the roots are process singletons):
    python probe_roots.py <scenario>
Scenarios print one line per observation; a line starting with "OBSERVED" is the fact the scenario exists for.
"""

import sys


def aether_policy_after_first_frame() -> None:
    """A policy installed after the first frame is reported by Aether but does not change the spell-id regime."""
    from melder import Aether, AetherConfiguration, Spellbook

    aether = Aether()
    print("fresh: configured", aether.configured, "| activated", aether.activated)
    Spellbook()  # the host's first frame ("default")
    sealed = aether.configuration
    print("after the host's first Spellbook: policy installed", sealed is not None, "| frozen", sealed.frozen,
          "| activated", sealed.activated, "| process_wide_unique_spell_ids", sealed.process_wide_unique_spell_ids)
    replacement = AetherConfiguration().with_defaults().with_process_wide_unique_spell_ids(False)
    aether.configure(replacement)  # exactly what MelderRuntime._activate_root does for an inactive Aether
    replacement.activate()
    aether.activate()
    print("after configure+activate: Aether.configuration is the replacement", aether.configuration is replacement,
          "| reported process_wide_unique_spell_ids", aether.configuration.process_wide_unique_spell_ids)

    class Service:
        pass

    Spellbook(aetheric_frame="tenant_a").bind(spell=Service, existence="many")
    try:
        Spellbook(aetheric_frame="tenant_b").bind(spell=Service, existence="many")
        print("OBSERVED same class bound in a second frame: accepted (per-frame ids)")
    except Exception as error:
        print("OBSERVED same class bound in a second frame: refused ->", type(error).__name__, str(error)[:150])


def aether_policy_before_first_frame() -> None:
    """Control: the same policy installed before any frame does change the regime."""
    from melder import Aether, AetherConfiguration, Spellbook

    aether = Aether()
    policy = AetherConfiguration().with_defaults().with_process_wide_unique_spell_ids(False)
    aether.configure(policy)
    policy.activate()
    aether.activate()

    class Service:
        pass

    Spellbook(aetheric_frame="tenant_a").bind(spell=Service, existence="many")
    try:
        Spellbook(aetheric_frame="tenant_b").bind(spell=Service, existence="many")
        print("OBSERVED control, policy installed before the first frame: second-frame bind accepted")
    except Exception as error:
        print("OBSERVED control: refused ->", type(error).__name__, str(error)[:150])


def crystallizer_states() -> None:
    """Active refuses reconfigure; inactive replaces silently; deactivated keeps its policy for a re-activate."""
    from melder import Aether, CrystallizerConfiguration

    crystallizer = Aether().crystallizer
    host = CrystallizerConfiguration().with_defaults().with_max_persistence_crystals(7)
    crystallizer.configure(host)
    other = CrystallizerConfiguration().with_defaults().with_max_persistence_crystals(3)
    crystallizer.configure(other)
    print("OBSERVED inactive: configure(other) accepted; host policy displaced", crystallizer.configuration is other)
    other.activate()
    crystallizer.activate()
    try:
        crystallizer.configure(host)
        print("OBSERVED active: configure accepted")
    except RuntimeError as error:
        print("OBSERVED active: configure refused ->", error)
    crystallizer.deactivate()
    print("deactivated: activated", crystallizer.activated, "| policy kept", crystallizer.configuration is other,
          "| policy object still reports activated", other.activated)
    crystallizer.activate()  # what MelderRuntime does when it reuses a host policy that is already activated
    print("OBSERVED re-activate without a new policy: activated", crystallizer.activated)


def crystallizer_late_activation() -> None:
    """Books and binds that exist before activation are not in the record; later binds are."""
    from melder import Aether, CrystallizerConfiguration, Spellbook

    class Early:
        pass

    class Late:
        pass

    book = Spellbook(aetheric_frame="host")
    book.bind(spell=Early, existence="many")
    root = book.conjure(name="root", dynamic=True)
    crystallizer = Aether().crystallizer
    policy = CrystallizerConfiguration().with_defaults()
    crystallizer.configure(policy)
    policy.activate()
    crystallizer.activate()
    print("OBSERVED profile right after a late activation:", crystallizer.describe_profile())
    book.bind(spell=Late, existence="many")
    print("OBSERVED profile after one bind made after activation:", crystallizer.describe_profile())


def crystallizer_early_activation() -> None:
    """Control for the late case: activation first, then the same Book, bind and conjure."""
    from melder import Aether, CrystallizerConfiguration, Spellbook

    class Early:
        pass

    crystallizer = Aether().crystallizer
    policy = CrystallizerConfiguration().with_defaults()
    crystallizer.configure(policy)
    policy.activate()
    crystallizer.activate()
    book = Spellbook(aetheric_frame="host")
    book.bind(spell=Early, existence="many")
    book.conjure(name="root")
    print("OBSERVED control, activation before the Book:", crystallizer.describe_profile())


def mutation_research_states() -> None:
    """Same guard as the crystallizer: refuse while active, replace while inactive."""
    from melder import Aether, MutationResearchConfiguration

    research = Aether().mutation_research
    host = MutationResearchConfiguration().with_defaults().with_lane_type_enforcement(True)
    research.configure(host)
    other = MutationResearchConfiguration().with_defaults()
    research.configure(other)
    print("OBSERVED inactive: configure(other) accepted; host policy displaced", research.configuration is other)
    other.activate()
    research.activate()
    try:
        research.configure(host)
        print("OBSERVED active: configure accepted")
    except RuntimeError as error:
        print("OBSERVED active: configure refused ->", error)


def nexus_configure_while_active() -> None:
    """Nexus.configure has no active guard: a live Nexus takes an unfrozen replacement policy."""
    from melder import Aether, NexusConfiguration

    nexus = Aether().nexus
    policy = NexusConfiguration().with_defaults()
    nexus.configure(policy)
    nexus.activate()
    print("active with defaults: frozen", policy.frozen,
          "| allowed targets", policy.get_property("allowed_target_frame_names"))
    replacement = NexusConfiguration().with_defaults().with_allowed_target_frame_names(("melderops",))
    nexus.configure(replacement)
    print("OBSERVED configure on an active Nexus: accepted | still activated", nexus.activated,
          "| live policy is the replacement", nexus.configuration is replacement,
          "| replacement frozen", replacement.frozen,
          "| allowed targets now", nexus.configuration.get_property("allowed_target_frame_names"))


def melderops_conflict_with_active_crystallizer() -> None:
    """MelderOps refuses at prepare when an active root's policy differs from the one it was given."""
    from melder import Aether, CrystallizerConfiguration
    from melder_ops.command_center.spectrum.configurations.melder_configuration import MelderConfiguration

    host = CrystallizerConfiguration().with_defaults().with_max_persistence_crystals(7)
    Aether().crystallizer.configure(host)
    host.activate()
    Aether().crystallizer.activate()
    requested = CrystallizerConfiguration().with_defaults().with_max_persistence_crystals(3)
    setup = MelderConfiguration(ai_enabled=True, crystallizer_configuration=requested)
    try:
        setup.prepare()
        print("OBSERVED prepare accepted")
    except Exception as error:
        print("OBSERVED prepare refused ->", type(error).__name__, error)


def melderops_replaces_inactive_crystallizer() -> None:
    """MelderOps installs its own policy over a host policy that is configured but not active."""
    from melder import Aether, CrystallizerConfiguration
    from melder_ops.command_center.spectrum.configurations.melder_configuration import MelderConfiguration
    from melder_ops.command_center.spectrum.melder_setup.runtime import MelderRuntime

    host = CrystallizerConfiguration().with_defaults().with_max_persistence_crystals(7)
    Aether().crystallizer.configure(host)
    requested = CrystallizerConfiguration().with_defaults().with_max_persistence_crystals(3)
    setup = MelderConfiguration(ai_enabled=True, crystallizer_configuration=requested)
    runtime = MelderRuntime(setup)
    runtime.initialize()
    crystallizer = Aether().crystallizer
    print("OBSERVED after MelderRuntime.initialize: installed is MelderOps' policy", crystallizer.configuration is requested,
          "| host policy displaced", crystallizer.configuration is not host,
          "| max_persistence_crystals", crystallizer.configuration.max_persistence_crystals,
          "| activated", crystallizer.activated)


def melderops_reactivates_deactivated_crystallizer() -> None:
    """A crystallizer the host switched off comes back on when MelderOps requests it."""
    from melder import Aether, CrystallizerConfiguration
    from melder_ops.command_center.spectrum.configurations.melder_configuration import MelderConfiguration
    from melder_ops.command_center.spectrum.melder_setup.runtime import MelderRuntime

    host = CrystallizerConfiguration().with_defaults().with_max_persistence_crystals(7)
    crystallizer = Aether().crystallizer
    crystallizer.configure(host)
    host.activate()
    crystallizer.activate()
    crystallizer.deactivate()
    print("host switched recording off: activated", crystallizer.activated)
    MelderRuntime(MelderConfiguration(ai_enabled=True)).initialize()
    print("OBSERVED after MelderRuntime.initialize (AI preset, nothing supplied): activated", crystallizer.activated,
          "| same host policy", crystallizer.configuration is host)


def melderops_aether_after_host_frame() -> None:
    """MelderOps' Aether policy arrives after the host's first frame: reported, not in force for spell ids."""
    from melder import Aether, AetherConfiguration, Spellbook
    from melder_ops.command_center.spectrum.configurations.melder_configuration import MelderConfiguration
    from melder_ops.command_center.spectrum.melder_setup.runtime import MelderRuntime

    Spellbook()  # the host was already using Melder
    requested = AetherConfiguration().with_defaults().with_process_wide_unique_spell_ids(False)
    MelderRuntime(MelderConfiguration(aether_configuration=requested)).initialize()
    aether = Aether()
    print("after MelderRuntime.initialize: installed is MelderOps' policy", aether.configuration is requested,
          "| activated", aether.activated,
          "| reported process_wide_unique_spell_ids", aether.configuration.process_wide_unique_spell_ids)

    class Service:
        pass

    Spellbook(aetheric_frame="tenant_a").bind(spell=Service, existence="many")
    try:
        Spellbook(aetheric_frame="tenant_b").bind(spell=Service, existence="many")
        print("OBSERVED second-frame bind accepted")
    except Exception as error:
        print("OBSERVED second-frame bind refused ->", type(error).__name__, str(error)[:150])


def _bind_twice(label: str) -> None:
    """Bind one class into a conjured frame, then into a second frame; print whether the second bind is refused."""
    from melder import Spellbook

    class Service:
        pass

    first = Spellbook(aetheric_frame="tenant_a")
    first.bind(spell=Service, existence="many")
    first.conjure(name="root_a")
    try:
        Spellbook(aetheric_frame="tenant_b").bind(spell=Service, existence="many")
        print(f"OBSERVED {label}: same class in a second frame accepted (per-frame ids)")
    except Exception as error:
        print(f"OBSERVED {label}: same class in a second frame refused ->", type(error).__name__, str(error)[:160])


def regime_default() -> None:
    """Baseline: no policy installed; the first frame seals process-wide ids."""
    _bind_twice("default regime")


def regime_policy_before_first_frame() -> None:
    """Per-frame ids requested before any frame exists."""
    from melder import Aether, AetherConfiguration

    policy = AetherConfiguration().with_defaults().with_process_wide_unique_spell_ids(False)
    Aether().configure(policy)
    policy.activate()
    Aether().activate()
    _bind_twice("per-frame policy installed before the first frame")


def regime_policy_after_first_frame() -> None:
    """Per-frame ids requested after the host's first frame, the way MelderOps installs an inactive Aether."""
    from melder import Aether, AetherConfiguration, Spellbook

    Spellbook()
    policy = AetherConfiguration().with_defaults().with_process_wide_unique_spell_ids(False)
    Aether().configure(policy)
    policy.activate()
    Aether().activate()
    print("reported process_wide_unique_spell_ids", Aether().configuration.process_wide_unique_spell_ids)
    _bind_twice("per-frame policy installed after the first frame")


def crystallizer_early_activation_dynamic() -> None:
    """Proper control: activation first, then a dynamic Book (configuration finalized first), bind and conjure."""
    from melder import Aether, CrystallizerConfiguration, Spellbook, SpellbookConfiguration

    class Early:
        pass

    crystallizer = Aether().crystallizer
    policy = CrystallizerConfiguration().with_defaults()
    crystallizer.configure(policy)
    policy.activate()
    crystallizer.activate()
    book = Spellbook(aetheric_frame="host", configuration=SpellbookConfiguration("host").with_defaults().finalize())
    book.bind(spell=Early, existence="many")
    book.conjure(name="root", dynamic=True)
    print("OBSERVED control, activation before a dynamic Book:", crystallizer.describe_profile())


def host_conjure_after_crystallizer_turned_on() -> None:
    """A host that bound with a mutable configuration, then MelderOps turns recording on, then the host conjures."""
    from melder import Aether, CrystallizerConfiguration, Spellbook

    class HostService:
        pass

    book = Spellbook(aetheric_frame="host")
    book.bind(spell=HostService, existence="many")
    policy = CrystallizerConfiguration().with_defaults()   # what MelderOps' AI preset builds and activates
    Aether().crystallizer.configure(policy)
    policy.activate()
    Aether().crystallizer.activate()
    try:
        book.conjure(name="root", dynamic=True)
        print("OBSERVED host dynamic conjure accepted")
    except RuntimeError as error:
        print("OBSERVED host dynamic conjure refused ->", str(error).splitlines()[0][:150])
    try:
        book.conjure(name="root")
        print("OBSERVED host automatic conjure accepted")
    except Exception as error:
        print("OBSERVED host automatic conjure refused ->", type(error).__name__, str(error)[:150])


def _melderops():
    """Import MelderOps' configuration facade and runtime (the probe env's editable copy of the current tree)."""
    from melder_ops.command_center.spectrum.configurations.melder_configuration import MelderConfiguration
    from melder_ops.command_center.spectrum.melder_setup.runtime import MelderRuntime

    return MelderConfiguration, MelderRuntime


def _turn_crystallizer_on() -> None:
    """Activate the hosted crystallizer with default policy, the way MelderOps' AI preset does."""
    from melder import Aether, CrystallizerConfiguration

    policy = CrystallizerConfiguration().with_defaults()
    Aether().crystallizer.configure(policy)
    policy.activate()
    Aether().crystallizer.activate()


def melderops_equal_policy_with_active_crystallizer() -> None:
    """Equal values, different object: the assessment still calls the missing method."""
    from melder import Aether, CrystallizerConfiguration

    MelderConfiguration, _ = _melderops()
    host = CrystallizerConfiguration().with_defaults()
    Aether().crystallizer.configure(host)
    host.activate()
    Aether().crystallizer.activate()
    try:
        MelderConfiguration(ai_enabled=True, crystallizer_configuration=CrystallizerConfiguration().with_defaults()).prepare()
        print("OBSERVED equal-valued supplied crystallizer policy: prepare accepted")
    except Exception as error:
        print("OBSERVED equal-valued supplied crystallizer policy: prepare refused ->", type(error).__name__, error)


def melderops_supplied_nexus_with_active_nexus() -> None:
    """The same comparison for Nexus."""
    from melder import Aether, NexusConfiguration

    MelderConfiguration, _ = _melderops()
    Aether().nexus.configure(NexusConfiguration().with_defaults())
    Aether().nexus.activate()
    try:
        MelderConfiguration(ai_enabled=True, nexus_configuration=NexusConfiguration().with_defaults()).prepare()
        print("OBSERVED supplied Nexus policy over an active Nexus: prepare accepted")
    except Exception as error:
        print("OBSERVED supplied Nexus policy over an active Nexus: prepare refused ->", type(error).__name__, error)


def melderops_aether_regime_after_host_frame() -> None:
    """Discriminating end-to-end: MelderOps installs a per-frame Aether policy after the host's first frame."""
    from melder import Aether, AetherConfiguration, Spellbook

    MelderConfiguration, MelderRuntime = _melderops()
    Spellbook()
    requested = AetherConfiguration().with_defaults().with_process_wide_unique_spell_ids(False)
    MelderRuntime(MelderConfiguration(aether_configuration=requested)).initialize()
    print("installed is MelderOps' policy", Aether().configuration is requested,
          "| reported process_wide_unique_spell_ids", Aether().configuration.process_wide_unique_spell_ids)
    _bind_twice("MelderOps per-frame policy after the host's first frame")


def melderops_aether_regime_no_host_frame() -> None:
    """Control: the same MelderOps setup when no frame exists yet."""
    from melder import AetherConfiguration

    MelderConfiguration, MelderRuntime = _melderops()
    requested = AetherConfiguration().with_defaults().with_process_wide_unique_spell_ids(False)
    MelderRuntime(MelderConfiguration(aether_configuration=requested)).initialize()
    _bind_twice("MelderOps per-frame policy with no host frame first")


def host_automatic_conjure_after_crystallizer_on() -> None:
    """Automatic conjure alone after recording is turned on under a host that bound with a mutable configuration."""
    from melder import Spellbook

    class HostService:
        pass

    book = Spellbook(aetheric_frame="host")
    book.bind(spell=HostService, existence="many")
    _turn_crystallizer_on()
    try:
        book.conjure(name="root")
        print("OBSERVED host automatic conjure (no dynamic attempt first): accepted")
    except Exception as error:
        print("OBSERVED host automatic conjure (no dynamic attempt first): refused ->", type(error).__name__,
              str(error).splitlines()[0][:140])


def refused_dynamic_conjure_settles_frame() -> None:
    """Frame posture before and after a dynamic conjure the crystallizer guard refuses."""
    from melder import Aether, Spellbook

    class HostService:
        pass

    book = Spellbook(aetheric_frame="host")
    book.bind(spell=HostService, existence="many")
    _turn_crystallizer_on()
    posture = Aether().find_frame("host").frame_configuration
    print("before: frozen", posture.frozen, "| system_state", posture.system_state)
    try:
        book.conjure(name="root", dynamic=True)
        print("dynamic conjure accepted")
    except RuntimeError as error:
        print("dynamic conjure refused ->", str(error).splitlines()[0][:100])
    posture = Aether().find_frame("host").frame_configuration
    print("OBSERVED after the refused dynamic conjure: frozen", posture.frozen, "| system_state", posture.system_state)


def host_dynamic_conjure_after_melderops_ai() -> None:
    """End to end: a host Book bound under a mutable configuration, MelderOps' AI preset starts, the host conjures."""
    from melder import Aether, Spellbook

    MelderConfiguration, MelderRuntime = _melderops()

    class HostService:
        pass

    book = Spellbook(aetheric_frame="host")
    book.bind(spell=HostService, existence="many")
    MelderRuntime(MelderConfiguration(ai_enabled=True)).initialize()
    print("after MelderOps AI preset: crystallizer activated", Aether().crystallizer.activated)
    try:
        book.conjure(name="root", dynamic=True)
        print("OBSERVED host dynamic conjure after MelderOps AI preset: accepted")
    except RuntimeError as error:
        print("OBSERVED host dynamic conjure after MelderOps AI preset: refused ->", str(error).splitlines()[0][:120])


def melderops_injects_logging_into_host_aether_policy() -> None:
    """A host installed (not activated) its own Aether policy; MelderOps runs with nothing supplied."""
    from melder import Aether, AetherConfiguration

    MelderConfiguration, MelderRuntime = _melderops()
    host = AetherConfiguration().with_defaults()
    Aether().configure(host)
    print("host policy: resolver", host.channel_logger_resolver, "| activation enabled",
          host.channel_logger_activation_enabled)
    MelderRuntime(MelderConfiguration()).initialize()
    policy = Aether().configuration
    print("OBSERVED after MelderRuntime.initialize: same host policy object", policy is host,
          "| Aether activated", Aether().activated, "| policy frozen", policy.frozen,
          "| resolver", getattr(policy.channel_logger_resolver, "__qualname__", policy.channel_logger_resolver),
          "| resolver module", getattr(policy.channel_logger_resolver, "__module__", None),
          "| activation enabled", policy.channel_logger_activation_enabled)


def melderops_clears_utility_logger() -> None:
    """A host registered a default logger on the hosted utility system (an Internal-labelled method) and never
    activated Aether; MelderOps activates Aether."""
    import logging

    from melder import Aether
    from melder.aether.aether_utility_system import AetherUtilitySystem

    MelderConfiguration, MelderRuntime = _melderops()
    utility = AetherUtilitySystem()
    print("utility singleton is the hosted one", utility is Aether()._aether_utility_system)
    utility.register_default_logger(logging.getLogger("host_app"))
    print("before: has_default_logger", utility.has_default_logger(),
          "| has_channel_logger_resolver", utility.has_channel_logger_resolver())
    MelderRuntime(MelderConfiguration()).initialize()
    print("OBSERVED after MelderRuntime.initialize: has_default_logger", utility.has_default_logger(),
          "| has_channel_logger_resolver", utility.has_channel_logger_resolver())


def melderops_frame_default_settled_automatic() -> None:
    """The host already conjured automatic in frame default; MelderOps is pointed at frame default."""
    from melder import Spellbook

    MelderConfiguration, MelderRuntime = _melderops()

    class HostService:
        pass

    book = Spellbook()
    book.bind(spell=HostService, existence="many")
    book.conjure(name="host_root")
    try:
        MelderRuntime(MelderConfiguration(frame_name="default")).initialize()
        print("OBSERVED MelderOps into the host's settled automatic frame: accepted")
    except Exception as error:
        print("OBSERVED MelderOps into the host's settled automatic frame: refused ->", type(error).__name__, error)


def melderops_settles_host_unsettled_default_frame() -> None:
    """The host created a Book in frame default but has not conjured; MelderOps is pointed at frame default."""
    from melder import Aether, Spellbook

    MelderConfiguration, MelderRuntime = _melderops()

    class HostService:
        pass

    book = Spellbook()
    book.bind(spell=HostService, existence="many")
    posture = Aether().find_frame("default").frame_configuration
    print("before: frozen", posture.frozen, "| system_state", posture.system_state)
    try:
        MelderRuntime(MelderConfiguration(frame_name="default")).initialize()
    except Exception as error:
        print("OBSERVED MelderOps into the host's unsettled frame: refused ->", type(error).__name__, error)
        return
    posture = Aether().find_frame("default").frame_configuration
    print("OBSERVED after MelderOps: frozen", posture.frozen, "| system_state", posture.system_state)
    try:
        book.conjure(name="host_root")
        print("OBSERVED host's plain conjure afterwards: accepted; frame system_state",
              Aether().find_frame("default").frame_configuration.system_state)
    except Exception as error:
        print("OBSERVED host's plain conjure afterwards: refused ->", type(error).__name__, str(error)[:160])


def melderops_nexus_default_targets() -> None:
    """What Nexus policy MelderOps' AI preset leaves when nothing is supplied."""
    from melder import Aether

    MelderConfiguration, MelderRuntime = _melderops()
    MelderRuntime(MelderConfiguration(ai_enabled=True)).initialize()
    nexus = Aether().nexus
    print("OBSERVED after AI preset: nexus activated", nexus.activated,
          "| allowed_target_frame_names", nexus.configuration.get_property("allowed_target_frame_names"),
          "| frames", Aether().list_frame_names())


def crystallizer_late_activation_dynamic() -> None:
    """A dynamic host world built before recording starts, then MelderOps-style activation."""
    from melder import Aether, Spellbook, SpellbookConfiguration

    class Early:
        pass

    class Late:
        pass

    book = Spellbook(aetheric_frame="host", configuration=SpellbookConfiguration("host").with_defaults().finalize())
    book.bind(spell=Early, existence="many")
    root = book.conjure(name="root", dynamic=True)
    _turn_crystallizer_on()
    print("OBSERVED profile right after a late activation over a dynamic world:", Aether().crystallizer.describe_profile())
    root.bind(spell=Late, existence="many")
    print("OBSERVED profile after one bind made after activation:", Aether().crystallizer.describe_profile())


if __name__ == "__main__":
    scenario = sys.argv[1]
    print(f"== {scenario}")
    globals()[scenario]()
