"""
Advanced-tier contract probes. Run on 3.14t:

    pytest UX_and_AIX_experiences/pytest_examples/test_advanced_probes.py -v
"""
import melder as md
import pytest

from melder import Aether, Conduit, Nexus
from melder.aether.spellbook.spellbook import Spellbook


@pytest.fixture(autouse=True)
def reset_aether_world() -> None:
    """Per-row world reset.

    FIVE classes in src/melder expose `_reset_singleton_for_tests`:
    Aether, AetherUtilitySystem, Crystallizer, MutationResearch, Nexus.
    This fixture resets the two THIS TIER touches - Aether (every row) and
    Nexus (arc B). The rows below activate Aether and enable Nexus, which
    are process-wide flips; without the reset they would leak forward and
    make later rows pass or fail depending on collection order.

    NOT reset here, deliberately:
      - AetherUtilitySystem: Aether resolves its logger provider through
        it, and resetting it underneath a live Aether is a wider blast
        radius than these rows need.
      - Crystallizer / MutationResearch: untouched by advanced today.
        ARC E (checkpoint/load) WILL need the Crystallizer reset - add it
        to this fixture in the same commit that adds those rows, not
        after, or arc E rows will bleed checkpoint state into each other.
    """
    def _fresh() -> None:
        Nexus._reset_singleton_for_tests()
        Aether._reset_singleton_for_tests()
        aether = Aether()
        Spellbook._aether = aether
        Conduit._aether = aether

    _fresh()
    yield
    _fresh()


class Payload:
    pass


def test_probe_frames_isolate_names_and_singletons():
    """Lesson 03 contract (README claim, pinned): two frames bind the
    SAME class with zero collision, and unique = one singleton PER
    FRAME. A red here is a finding against the README."""
    book_a = Spellbook(aetheric_frame="probe-tenant-a")
    book_b = Spellbook(aetheric_frame="probe-tenant-b")
    book_a.bind(spell=Payload, existence="unique")
    book_b.bind(spell=Payload, existence="unique")
    a = book_a.conjure().meld(spell=Payload)
    b = book_b.conjure().meld(spell=Payload)
    assert a is not b
    print("frame isolation pinned: same class, two worlds, two singletons")


def test_probe_posture_public_door_then_freeze():
    """Lesson 04 contract: configure_aether_frame(system_state="dynamic")
    before any conjure -> plain conjures inherit and link; after the
    first conjure froze the posture, reconfiguring refuses."""
    book = Spellbook(aetheric_frame="probe-ops")
    book.bind(spell=Payload, existence="unique")
    book.configure_aether_frame(system_state="dynamic", disposal=None,
                                disposal_method_names=None)
    root = book.conjure(name="probe-ops-root")
    peer = Spellbook(aetheric_frame="probe-ops").conjure(name="probe-ops-peer")
    assert root.link(peer) is True
    with pytest.raises(Exception) as refused:
        book.configure_aether_frame(system_state="automatic", disposal=None,
                                    disposal_method_names=None)
    print("post-freeze reconfigure refusal type:", type(refused.value).__name__)


def test_probe_devops_flags_gate_via_retained_posture_seam():
    """FINDING (2026-07-25): there is NO PUBLIC DOOR to stage the frame
    devops flags (disable_linking / disable_bind / ...) - the component
    suite stages them through the book's PRIVATE retained posture
    (book._aetheric_frame_configuration.with_disable_*). This probe pins
    the gate behavior through that same seam so the curriculum can teach
    it the day a public door exists. Public-surface gap recorded for the
    owner's init program."""
    book = Spellbook(aetheric_frame="probe-flags")
    book.bind(spell=Payload, existence="unique")
    book._aetheric_frame_configuration.with_system_state("dynamic")
    book._aetheric_frame_configuration.with_disable_linking(True)
    owner = book.conjure(dynamic=True, name="flag-owner")
    borrower = Spellbook(aetheric_frame="probe-flags").conjure(name="flag-borrower")
    with pytest.raises(RuntimeError, match="disabled"):
        owner.link(borrower)
    print("devops flag gate pinned: disable_linking refused the link")


def test_probe_attach_logger_lifecycle():
    """Lesson 05 contract: melder boots silent; attach_logger attaches a
    real logger post-boot; None detaches back to the null wrapper;
    enable_logging(explicit) is the same attachment."""
    import logging
    aether = Aether()
    logger = logging.getLogger("probe-advanced-logger")
    aether.attach_logger(logger)
    aether.attach_logger(None)
    aether.enable_logging(logger)
    aether.attach_logger(None)
    print("logger attach/detach lifecycle clean")


# ---------------------------------------------------------------------------
# Lesson 08 - AethericFrameConfiguration is CONSTRUCTOR-FIRST
# ---------------------------------------------------------------------------

def test_probe_frame_posture_is_constructor_first():
    """Lesson 08 claim #1: this config cannot be built empty. Four values
    are REQUIRED keyword-only arguments. If a bare constructor ever starts
    working, the lesson's headline is wrong and this row goes red first."""
    with pytest.raises(TypeError):
        md.AethericFrameConfiguration()
    posture = md.AethericFrameConfiguration(
        origin_spellbook_id=None,
        system_state=md.SystemState.automatic,
        ai_native_enabled=False,
        rift_enabled=False,
    )
    assert posture.system_state is md.SystemState.automatic
    print("constructor-first pinned: 4 required kw-only values")


def test_probe_frame_posture_with_star_mutates_and_returns_self():
    """Lesson 08 claim #2: with_* is fluent in SHAPE ONLY. It mutates this
    object and returns SELF - never a clone. The frame's settlement law
    requires the RETAINED posture to be the bound one, so a copying with_*
    would be silently harmful rather than merely surprising."""
    posture = md.AethericFrameConfiguration(
        origin_spellbook_id=None,
        system_state=md.SystemState.automatic,
        ai_native_enabled=False,
        rift_enabled=False,
    )
    returned = posture.with_system_caching_enabled(False)
    assert returned is posture
    assert posture.system_caching_enabled is False
    # presets follow the same law
    assert posture.dynamic_defaults() is posture
    assert posture.system_state is md.SystemState.dynamic
    print("with_* and presets pinned: mutate-and-return-self, no clones")


def test_probe_frame_posture_validate_raises_rather_than_returning_false():
    """Lesson 08 claim #3: validate() RAISES. The bool return is a
    convention, not a verdict channel - a caller who writes
    `if not cfg.validate()` never runs. The semantic rule it enforces:
    ai_native_enabled requires system_state dynamic."""
    posture = md.AethericFrameConfiguration(
        origin_spellbook_id=None,
        system_state=md.SystemState.automatic,
        ai_native_enabled=False,
        rift_enabled=False,
    )
    posture.with_ai_native(True)
    with pytest.raises(ValueError, match="dynamic"):
        posture.validate()
    posture.with_system_state(md.SystemState.dynamic)
    assert posture.validate() is True
    print("validate pinned: raises on ai_native-without-dynamic, True after")


def test_probe_frame_posture_finalize_seals_same_instance():
    """Lesson 08 claim #4: finalize() freezes and returns THE SAME
    instance, and the freeze seals rather than clears - values survive."""
    posture = md.AethericFrameConfiguration(
        origin_spellbook_id=None,
        system_state=md.SystemState.dynamic,
        ai_native_enabled=True,
        rift_enabled=False,
    )
    finalized = posture.finalize()
    assert finalized is posture
    with pytest.raises(RuntimeError, match="frozen"):
        posture.with_system_state(md.SystemState.automatic)
    assert posture.system_state is md.SystemState.dynamic
    assert posture.ai_native_enabled is True
    print("finalize pinned: same instance, frozen, values intact")


def test_probe_frame_posture_has_no_public_install_door():
    """FINDING (2026-08-02, lesson 08): md.AethericFrameConfiguration is
    EXPORTED FROM THE PUBLIC ROOT AND CANNOT BE INSTALLED FROM IT.
    Spellbook.__init__ takes (aetheric_frame, configuration, logger) where
    `configuration` is a SpellbookConfiguration. This row pins the gap by
    signature so it goes GREEN today and RED the day a door lands - at
    which point the lesson's closing paragraph needs rewriting."""
    import inspect
    parameters = inspect.signature(Spellbook.__init__).parameters
    assert "aetheric_frame_configuration" not in parameters
    annotation = parameters["configuration"].annotation
    assert "AethericFrameConfiguration" not in str(annotation)

    # The one public door reaches TWO of the fifteen posture knobs.
    door = inspect.signature(Spellbook.configure_aether_frame).parameters
    posture_knobs = {"system_state", "system_caching_enabled"}
    assert posture_knobs.issubset(set(door))
    assert "with_disable_linking" not in door
    assert "ai_native_enabled" not in door
    assert "rift_enabled" not in door
    print("init-surface gap pinned: exported type, no install door;",
          "configure_aether_frame reaches", len(posture_knobs), "of 15 knobs")


# ---------------------------------------------------------------------------
# Lesson 09 - two doors, and the frozen/activated split
# ---------------------------------------------------------------------------

def test_probe_both_config_doors_land_frozen_not_activated():
    """Lesson 09 claim: create_configuration().finalize() and
    create_configuration_builder().build() land on the SAME rung - frozen,
    NOT activated. If either door ever auto-activates, the ladder the
    lesson teaches is wrong."""
    aether = Aether()

    config = aether.create_configuration()
    assert config.frozen is False and config.activated is False
    assert config.with_defaults().finalize() is config
    assert config.frozen is True
    assert config.activated is False

    built = aether.create_configuration_builder().with_defaults().build()
    assert built.frozen is True
    assert built.activated is False
    assert built is not config
    print("both doors pinned: frozen is not activated")


def test_probe_config_activate_is_a_second_distinct_bit():
    """Lesson 09 headline: frozen and activated are TWO bits. Freezing
    sets one. activate() sets the other. Nothing sets both at once."""
    aether = Aether()
    config = aether.create_configuration().with_defaults().finalize()
    assert (config.frozen, config.activated) == (True, False)
    config.activate()
    assert (config.frozen, config.activated) == (True, True)
    print("two-bit split pinned: frozen then activated, never together")


def test_probe_aether_refuses_frozen_but_inactive_configuration():
    """Lesson 09 ORDERING RULE, pinned where it is safe to pin it.
    Aether's contract: "THE CONFIGURATION MUST BE ACTIVATED BEFORE AETHER
    CAN BE." This lives in the probe rather than the lesson because Aether
    is a process-wide singleton AND activate() installs the config BEFORE
    checking the activated bit - so even the refusing call mutates the
    world. The reset fixture owns a clean singleton; a lesson sharing an
    interpreter with 40 others does not."""
    aether = Aether()
    frozen_only = aether.create_configuration().with_defaults().finalize()
    assert frozen_only.activated is False
    with pytest.raises(RuntimeError, match="activated"):
        aether.activate(frozen_only)
    print("ordering rule pinned: aether refuses a merely-frozen config")


def test_probe_aether_comes_up_once_the_rungs_are_climbed_in_order():
    """The positive half of the ordering rule: rung 2 then rung 3 works."""
    aether = Aether()
    config = aether.create_configuration().with_defaults().finalize()
    config.activate()
    aether.activate(config)
    assert aether.activated is True
    print("ladder pinned: finalize -> config.activate -> aether.activate")


# ---------------------------------------------------------------------------
# Lesson 10 - Nexus enablement, and the asymmetry with Aether
# ---------------------------------------------------------------------------

def test_probe_nexus_factory_builds_but_never_installs():
    """Lesson 10 claim: create_system_configuration() returns a NEW
    pre-defaulted config each call and installs nothing. If it ever starts
    installing, the lesson's "factories never wire" sentence is wrong."""
    nexus = Nexus()
    assert nexus.is_configured is False
    assert nexus.is_enabled is False
    first = nexus.create_system_configuration()
    second = nexus.create_system_configuration()
    assert isinstance(first, md.NexusConfiguration)
    assert first is not second
    assert nexus.is_enabled is False
    print("nexus factory pinned: fresh config per call, installs nothing")


def test_probe_nexus_enable_finalizes_the_configuration_for_you():
    """Lesson 10 HEADLINE, and the asymmetry that makes the lesson worth
    existing: Nexus.enable() finalizes the installed configuration on its
    way through. The caller never seals it. This is the OPPOSITE of
    Aether, which refuses a config the caller has not activated.

    A red here means the two subsystems converged - which would be good
    news for the configuration-uniformity program, and would mean lesson
    10's contrast section needs rewriting rather than the code."""
    nexus = Nexus()
    config = nexus.create_system_configuration()
    assert config.frozen is False
    nexus.enable(config)
    assert config.frozen is True, "enable was supposed to seal it"
    assert nexus.is_configured is True
    assert nexus.is_enabled is True
    print("nexus asymmetry pinned: enable() seals; aether makes you do it")


def test_probe_nexus_disable_drops_liveness_not_configuration():
    """Lesson 10 claim: configured and enabled are separate bits, so
    disable() takes the subsystem down and leaves the config installed."""
    nexus = Nexus()
    nexus.enable(nexus.create_system_configuration())
    assert (nexus.is_configured, nexus.is_enabled) == (True, True)
    nexus.disable()
    assert (nexus.is_configured, nexus.is_enabled) == (True, False)
    print("two-bit split pinned on nexus: disable keeps the configuration")


def test_probe_nexus_frame_mode_is_a_real_enum():
    """Lesson 10 claim: NexusFrameMode is an enum with exactly three
    members, so a typo raises instead of silently defaulting."""
    modes = {mode.value for mode in md.NexusFrameMode}
    assert modes == {"single", "indexed", "one_per_workspace"}
    config = Nexus().create_system_configuration()
    config.with_nexus_frame_mode(md.NexusFrameMode.single)
    print("frame modes pinned:", sorted(modes))


def test_probe_rift_space_type_is_a_real_enum():
    """Arc B foundation: RiftSpaceType names the three room kinds. Static
    and capability are ADVANCED (lessons 12-13); codegen is EXPERT."""
    kinds = {kind.value for kind in md.RiftSpaceType}
    assert kinds == {"static", "capability", "codegen"}
    print("rift space types pinned:", sorted(kinds))


def _enabled_nexus() -> "Nexus":
    nexus = Nexus()
    system_config = nexus.create_system_configuration()
    system_config.with_rift_creation_enabled(True)
    nexus.enable(system_config)
    return nexus


def test_probe_rift_configuration_is_consumed_by_create_rift():
    """Lesson 11 claim: create_rift() CONSUMES the configuration. One
    config, one rift. A second call with the same object refuses with
    "already been consumed" - the same one-shot law build() follows."""
    nexus = _enabled_nexus()
    rift_config = nexus.create_rift_configuration()
    rift_config.with_space_type(md.RiftSpaceType.static)
    rift = nexus.create_rift(configuration=rift_config, rift_name="probe-ops")
    assert isinstance(rift, md.Rift)
    with pytest.raises(ValueError, match="consumed"):
        nexus.create_rift(configuration=rift_config, rift_name="probe-ops-2")
    print("one-shot pinned: a rift configuration is spent by create_rift")


def test_probe_rift_registered_and_active_are_separate_bits():
    """Lesson 11 HEADLINE - the third appearance of melder's most repeated
    law. Creation REGISTERS; it does not make live. mark_inactive() drops
    liveness and leaves registration standing.

    frozen/activated (09), is_configured/is_enabled (10), and
    is_registered/is_active (11) are the same law under three names. A red
    on any of the three means the pattern the curriculum teaches broke."""
    nexus = _enabled_nexus()
    config = nexus.create_rift_configuration()
    config.with_space_type(md.RiftSpaceType.static)
    rift = nexus.create_rift(configuration=config, rift_name="probe-bits")

    assert rift.is_registered is True
    rift.mark_active()
    assert (rift.is_registered, rift.is_active) == (True, True)
    rift.mark_inactive()
    assert (rift.is_registered, rift.is_active) == (True, False)
    print("two-bit split pinned on rift: registration outlives liveness")


def test_probe_created_rift_is_findable_on_the_nexus_registry():
    """Lesson 11 claim: create_rift registers through add_rift, so the
    rift is discoverable by id without a second registration step."""
    nexus = _enabled_nexus()
    config = nexus.create_rift_configuration()
    config.with_space_type(md.RiftSpaceType.static)
    rift = nexus.create_rift(configuration=config, rift_name="probe-registry")
    assert nexus.has_rift(rift.id) is True
    assert rift.id in nexus.list_rift_ids()
    assert rift.space is not None
    assert rift.rift_gate is not None
    print("registry pinned: found by id, owns a room and a gate")


def _rift_with_room(nexus, space_type, name="probe-room"):
    config = nexus.create_rift_configuration()
    config.with_space_type(space_type)
    rift = nexus.create_rift(configuration=config, rift_name=name)
    rift.mark_active()
    return rift


def test_probe_a_rift_owns_exactly_one_room_by_identity():
    """Lesson 12 claim: `rift.space` is THE room, not a lookup or factory.
    Identity on every read, and no verb exists to swap or re-type it."""
    nexus = _enabled_nexus()
    rift = _rift_with_room(nexus, md.RiftSpaceType.static, "probe-one-room")
    room = rift.space
    assert rift.space is room
    assert room.owner_rift_id == rift.id
    for absent in ("set_space_type", "switch_space", "promote_space",
                   "retype", "activate_space"):
        assert not hasattr(room, absent), f"{absent} must not exist"
    print("one-room law pinned: identity stable, no re-type verb")


def test_probe_every_room_carries_the_same_fixture_set():
    """Lesson 12 claim: room SHAPE is constant across kinds. Static and
    capability rooms expose the identical fixture set; only authority
    differs (lesson 13). A red means the kinds diverged structurally,
    which would change what lesson 12 can promise."""
    nexus = _enabled_nexus()
    static_room = _rift_with_room(
        nexus, md.RiftSpaceType.static, "probe-fixtures-static").space
    capability_room = _rift_with_room(
        nexus, md.RiftSpaceType.capability, "probe-fixtures-capability").space

    for room in (static_room, capability_room):
        for fixture in ("frame_viewer", "workstation", "command_system",
                        "event_system", "memory_system"):
            assert getattr(room, fixture) is not None, (
                f"{fixture} missing on {type(room).__name__}"
            )
    print("fixture parity pinned across static and capability rooms")


def test_probe_configured_space_type_becomes_the_room_kind():
    """Lesson 12 claim: RiftSpaceType is the single input that fixes the
    room kind, and the room reports back exactly what was configured."""
    nexus = _enabled_nexus()
    for space_type in (md.RiftSpaceType.static, md.RiftSpaceType.capability):
        rift = _rift_with_room(
            nexus, space_type, f"probe-kind-{space_type.value}")
        assert rift.space.space_kind == space_type.value
    print("kind pinned: configuration in, room kind out, no translation")


def test_probe_rift_space_type_docstring_documents_a_member_that_is_gone():
    """FINDING (doc drift, 2026-08-02, lesson 12): RiftSpaceType's
    docstring documents a FOURTH member -

        "dynamic: Legacy alias for `codegen`. Retained temporarily so
         older AR configuration inputs can still normalize during the
         room rename."

    The enum defines static, capability and codegen only, and there is no
    `_missing_` handler, so RiftSpaceType("dynamic") raises. Either the
    alias was removed and the prose was not, or it never landed.

    This row goes GREEN while the docstring is wrong and RED the day
    someone either adds the alias or deletes the paragraph - so the drift
    cannot sit there quietly. Same shape as the false with_defaults()
    docstring in spellbook_configuration.py."""
    members = {kind.value for kind in md.RiftSpaceType}
    assert members == {"static", "capability", "codegen"}
    assert "dynamic" not in members
    with pytest.raises(ValueError):
        md.RiftSpaceType("dynamic")
    assert "dynamic" in (md.RiftSpaceType.__doc__ or ""), (
        "docstring no longer mentions the alias - delete this probe"
    )
    print("doc drift pinned: 'dynamic' documented, not defined")


def test_probe_rift_enabled_has_no_public_setter():
    """FINDING (2026-08-02, arc B): `rift_enabled` gates AR targeting
    (Nexus raises "AR requires rift_enabled on target frame") and there is
    NO PUBLIC DOOR TO SET IT. It is not a parameter of
    Spellbook.configure_aether_frame, and the frame posture that owns
    with_rift_enabled() cannot be installed from the public root
    (lesson 08 finding). Rifts themselves ARE reachable - Nexus.enable and
    create_rift are public - but AR targeting is not.

    Pinned so the gap is a test rather than a memory. Goes red the day a
    setter lands, which is when arc B can teach AR."""
    import inspect
    door = inspect.signature(Spellbook.configure_aether_frame).parameters
    assert "rift_enabled" not in door
    assert "ai_native_enabled" not in door
    # the setter exists on the posture object - it is the INSTALL that is missing
    assert hasattr(md.AethericFrameConfiguration, "with_rift_enabled")
    print("AR gap pinned: with_rift_enabled exists, no public path installs it")
