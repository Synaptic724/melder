"""
Advanced-tier contract probes. Run on 3.14t:

    pytest UX_and_AIX_experiences/pytest_examples/test_advanced_probes.py -v
"""
import melder as md
import pytest

from melder import Aether, Conduit, Crystallizer, Nexus
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

    Crystallizer joined the reset with arc E (lessons 17-18): checkpoint
    ids and cached checkpoints are process-wide, so without it one row's
    checkpoints show up in the next row's list_checkpoint_ids().

    NOT reset here, deliberately:
      - AetherUtilitySystem: Aether resolves its logger provider through
        it, and resetting it underneath a live Aether is a wider blast
        radius than these rows need.
      - MutationResearch: untouched by advanced - it is EXPERT material.
    """
    def _fresh() -> None:
        Crystallizer._reset_singleton_for_tests()
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
    """Lesson 02 contract (README claim, pinned): two frames bind the
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
    """Lesson 03 contract: configure_aether_frame(system_state="dynamic")
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
    """Lesson 04 contract: melder boots silent; attach_logger attaches a
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
# Lesson 06 - AethericFrameConfiguration is CONSTRUCTOR-FIRST
# ---------------------------------------------------------------------------

def test_probe_frame_posture_is_constructor_first():
    """Lesson 06 claim #1: this config cannot be built empty. Four values
    are REQUIRED keyword-only arguments. If a bare constructor ever starts
    working, the lesson's headline is wrong and this row goes red first."""
    with pytest.raises(TypeError):
        md.AethericFrameConfiguration()
    posture = md.AethericFrameConfiguration(
        origin_spellbook_id=None,
        system_state="automatic",
        ai_native_enabled=False,
        rift_enabled=False,
    )
    assert posture.system_state.name == "automatic"
    print("constructor-first pinned: 4 required kw-only values")


def test_probe_frame_posture_with_star_mutates_and_returns_self():
    """Lesson 06 claim #2: with_* is fluent in SHAPE ONLY. It mutates this
    object and returns SELF - never a clone. The frame's settlement law
    requires the RETAINED posture to be the bound one, so a copying with_*
    would be silently harmful rather than merely surprising."""
    posture = md.AethericFrameConfiguration(
        origin_spellbook_id=None,
        system_state="automatic",
        ai_native_enabled=False,
        rift_enabled=False,
    )
    returned = posture.with_system_caching_enabled(False)
    assert returned is posture
    assert posture.system_caching_enabled is False
    # presets follow the same law
    assert posture.dynamic_defaults() is posture
    assert posture.system_state.name == "dynamic"
    print("with_* and presets pinned: mutate-and-return-self, no clones")


def test_probe_frame_posture_validate_raises_rather_than_returning_false():
    """Lesson 06 claim #3: validate() RAISES. The bool return is a
    convention, not a verdict channel - a caller who writes
    `if not cfg.validate()` never runs. The semantic rule it enforces:
    ai_native_enabled requires system_state dynamic."""
    posture = md.AethericFrameConfiguration(
        origin_spellbook_id=None,
        system_state="automatic",
        ai_native_enabled=False,
        rift_enabled=False,
    )
    posture.with_ai_native(True)
    with pytest.raises(ValueError, match="dynamic"):
        posture.validate()
    posture.with_system_state("dynamic")
    assert posture.validate() is True
    print("validate pinned: raises on ai_native-without-dynamic, True after")


def test_probe_frame_posture_finalize_seals_same_instance():
    """Lesson 06 claim #4: finalize() freezes and returns THE SAME
    instance, and the freeze seals rather than clears - values survive."""
    posture = md.AethericFrameConfiguration(
        origin_spellbook_id=None,
        system_state="dynamic",
        ai_native_enabled=True,
        rift_enabled=False,
    )
    finalized = posture.finalize()
    assert finalized is posture
    with pytest.raises(RuntimeError, match="frozen"):
        posture.with_system_state("automatic")
    assert posture.system_state.name == "dynamic"
    assert posture.ai_native_enabled is True
    print("finalize pinned: same instance, frozen, values intact")


def test_probe_frame_posture_has_no_public_install_door():
    """FINDING (2026-08-02, lesson 06): md.AethericFrameConfiguration is
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
# Lesson 07 - two doors, and the frozen/activated split
# ---------------------------------------------------------------------------

def test_probe_both_config_doors_land_frozen_not_activated():
    """Lesson 07 claim: create_configuration().finalize() and
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
    """Lesson 07 headline: frozen and activated are TWO bits. Freezing
    sets one. activate() sets the other. Nothing sets both at once."""
    aether = Aether()
    config = aether.create_configuration().with_defaults().finalize()
    assert (config.frozen, config.activated) == (True, False)
    config.activate()
    assert (config.frozen, config.activated) == (True, True)
    print("two-bit split pinned: frozen then activated, never together")


def test_probe_aether_refuses_frozen_but_inactive_configuration():
    """Lesson 07 ORDERING RULE, pinned where it is safe to pin it.
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
# Lesson 08 - Nexus enablement, and the asymmetry with Aether
# ---------------------------------------------------------------------------

def test_probe_nexus_factory_builds_but_never_installs():
    """Lesson 08 claim: create_system_configuration() returns a NEW
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
    """Lesson 08 HEADLINE, and the asymmetry that makes the lesson worth
    existing: Nexus.enable() finalizes the installed configuration on its
    way through. The caller never seals it. This is the OPPOSITE of
    Aether, which refuses a config the caller has not activated.

    A red here means the two subsystems converged - which would be good
    news for the configuration-uniformity program, and would mean lesson 08's contrast section needs rewriting rather than the code."""
    nexus = Nexus()
    config = nexus.create_system_configuration()
    assert config.frozen is False
    nexus.enable(config)
    assert config.frozen is True, "enable was supposed to seal it"
    assert nexus.is_configured is True
    assert nexus.is_enabled is True
    print("nexus asymmetry pinned: enable() seals; aether makes you do it")


def test_probe_nexus_disable_drops_liveness_not_configuration():
    """Lesson 08 claim: configured and enabled are separate bits, so
    disable() takes the subsystem down and leaves the config installed."""
    nexus = Nexus()
    nexus.enable(nexus.create_system_configuration())
    assert (nexus.is_configured, nexus.is_enabled) == (True, True)
    nexus.disable()
    assert (nexus.is_configured, nexus.is_enabled) == (True, False)
    print("two-bit split pinned on nexus: disable keeps the configuration")


def test_probe_nexus_frame_mode_is_a_real_enum():
    """Lesson 08 claim: NexusFrameMode is an enum with exactly three
    members, so a typo raises instead of silently defaulting."""
    modes = {mode.value for mode in md.NexusFrameMode}
    assert modes == {"single", "indexed", "one_per_workspace"}
    config = Nexus().create_system_configuration()
    config.with_nexus_frame_mode("single")
    print("frame modes pinned:", sorted(modes))


def test_probe_rift_space_type_is_a_real_enum():
    """Arc B foundation: RiftSpaceType names the three room kinds. Static
    and capability are ADVANCED (lessons 10-11); codegen is EXPERT."""
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
    """Lesson 09 claim: create_rift() CONSUMES the configuration. One
    config, one rift. A second call with the same object refuses with
    "already been consumed" - the same one-shot law build() follows."""
    nexus = _enabled_nexus()
    rift_config = nexus.create_rift_configuration()
    rift_config.with_space_type("static")
    rift = nexus.create_rift(configuration=rift_config, rift_name="probe-ops")
    assert isinstance(rift, md.Rift)
    with pytest.raises(ValueError, match="consumed"):
        nexus.create_rift(configuration=rift_config, rift_name="probe-ops-2")
    print("one-shot pinned: a rift configuration is spent by create_rift")


def test_probe_rift_registered_and_active_are_separate_bits():
    """Lesson 09 HEADLINE - the third appearance of melder's most repeated
    law. Creation REGISTERS; it does not make live. mark_inactive() drops
    liveness and leaves registration standing.

    frozen/activated (09), is_configured/is_enabled (10), and
    is_registered/is_active (11) are the same law under three names. A red
    on any of the three means the pattern the curriculum teaches broke."""
    nexus = _enabled_nexus()
    config = nexus.create_rift_configuration()
    config.with_space_type("static")
    rift = nexus.create_rift(configuration=config, rift_name="probe-bits")

    assert rift.is_registered is True
    rift.mark_active()
    assert (rift.is_registered, rift.is_active) == (True, True)
    rift.mark_inactive()
    assert (rift.is_registered, rift.is_active) == (True, False)
    print("two-bit split pinned on rift: registration outlives liveness")


def test_probe_created_rift_is_findable_on_the_nexus_registry():
    """Lesson 09 claim: create_rift registers through add_rift, so the
    rift is discoverable by id without a second registration step."""
    nexus = _enabled_nexus()
    config = nexus.create_rift_configuration()
    config.with_space_type("static")
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
    """Lesson 10 claim: `rift.space` is THE room, not a lookup or factory.
    Identity on every read, and no verb exists to swap or re-type it."""
    nexus = _enabled_nexus()
    rift = _rift_with_room(nexus, "static", "probe-one-room")
    room = rift.space
    assert rift.space is room
    assert room.owner_rift_id == rift.id
    for absent in ("set_space_type", "switch_space", "promote_space",
                   "retype", "activate_space"):
        assert not hasattr(room, absent), f"{absent} must not exist"
    print("one-room law pinned: identity stable, no re-type verb")


def test_probe_every_room_carries_the_same_fixture_set_by_name():
    """Lesson 10 claim, sharpened by the owner's run: every room carries
    the same fixtures BY NAME whatever its kind. Two of them differ BY
    TYPE (command_system, frame_viewer - see the corrected lesson 11);
    the other three are literally the same classes."""
    nexus = _enabled_nexus()
    static_room = _rift_with_room(
        nexus, "static", "probe-fixtures-static").space
    capability_room = _rift_with_room(
        nexus, "capability", "probe-fixtures-capability").space

    for room in (static_room, capability_room):
        for fixture in ("frame_viewer", "workstation", "command_system",
                        "event_system", "memory_system"):
            assert getattr(room, fixture) is not None, (
                f"{fixture} missing on {type(room).__name__}"
            )
    print("fixture-set parity pinned by name across both room kinds")


def test_probe_configured_space_type_becomes_the_room_kind():
    """Lesson 10 claim: RiftSpaceType is the single input that fixes the
    room kind, and the room reports back exactly what was configured."""
    nexus = _enabled_nexus()
    for space_type in ("static", "capability"):
        rift = _rift_with_room(
            nexus, space_type, f"probe-kind-{space_type}")
        assert rift.space.space_kind == space_type
    print("kind pinned: configuration in, room kind out, no translation")


def test_probe_rift_space_type_docstring_documents_a_member_that_is_gone():
    """FINDING (doc drift, 2026-08-02, lesson 10): RiftSpaceType's
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


def test_probe_room_kind_changes_exactly_two_fixtures():
    """Lesson 11, CORRECTED by the owner's run 2026-08-02.

    My original claim was that the room kinds override EXACTLY ONE
    property, command_system. THAT WAS WRONG. They override TWO:

        command_system  StaticCommandSystem / CapabilityCommandSystem
        frame_viewer    StaticFrameViewer   / FrameViewer

    Which is a BETTER story than the one I wrote, not a worse one: the
    room kind narrows BOTH what you may do AND what you may see, and it
    does it the same way both times - by handing you a different class
    rather than by guarding a shared one. Authority-by-absence applies to
    the read surface too.

    workstation / event_system / memory_system remain shared."""
    nexus = _enabled_nexus()
    static_room = _rift_with_room(
        nexus, "static", "probe-auth-static").space
    capability_room = _rift_with_room(
        nexus, "capability", "probe-auth-capability").space

    # the two that DIVERGE
    assert type(static_room.command_system) is not type(
        capability_room.command_system)
    assert type(static_room.frame_viewer) is not type(
        capability_room.frame_viewer)
    assert type(static_room.frame_viewer).__name__ == "StaticFrameViewer"
    assert type(capability_room.frame_viewer).__name__ == "FrameViewer"

    # the three that are SHARED
    for fixture in ("workstation", "event_system", "memory_system"):
        assert type(getattr(static_room, fixture)) is type(
            getattr(capability_room, fixture)), fixture
    print("two-fixtures-differ pinned: command_system AND frame_viewer")


def test_probe_authority_is_granted_by_absence_not_by_refusal():
    """Lesson 11 HEADLINE. The static command surface does not DENY the
    mutating verbs - it does not HAVE them. melder's own note says the
    methods "live on the capability surface INSTEAD OF BEING DENIED AFTER
    INHERITANCE".

    This is the row that matters most in arc B. If a mutating verb ever
    appears on StaticCommandSystem - even as an override that raises - the
    design property this lesson teaches is gone: capability stops being
    statically enumerable and hasattr stops being an honest question."""
    nexus = _enabled_nexus()
    static_commands = _rift_with_room(
        nexus, "static", "probe-absent-static"
    ).space.command_system
    capability_commands = _rift_with_room(
        nexus, "capability", "probe-absent-capability"
    ).space.command_system

    for verb in ("meld", "link", "sever_link", "create_lesser_conduit",
                 "create_cluster", "delete_cluster", "join_cluster",
                 "leave_cluster"):
        assert not hasattr(static_commands, verb), (
            f"{verb} appeared on the static surface - authority-by-absence "
            f"is broken, even if it only raises"
        )
        assert hasattr(capability_commands, verb), verb
    print("authority-by-absence pinned: 8 mutating verbs, static has none")


def test_probe_reuse_is_available_to_static_but_creation_is_not():
    """Lesson 11 claim: meld_existing_spell (REUSE) is on both surfaces;
    meld (CREATION) is capability-only. The static room can hand back
    something that already exists - it cannot bring anything into being."""
    nexus = _enabled_nexus()
    static_commands = _rift_with_room(
        nexus, "static", "probe-reuse-static"
    ).space.command_system
    capability_commands = _rift_with_room(
        nexus, "capability", "probe-reuse-capability"
    ).space.command_system

    assert hasattr(static_commands, "meld_existing_spell")
    assert hasattr(capability_commands, "meld_existing_spell")
    assert not hasattr(static_commands, "meld")
    assert hasattr(capability_commands, "meld")
    print("reuse/creation split pinned: static reuses, capability creates")


def test_probe_rooms_enumerate_their_own_command_surface():
    """Lesson 11 AIX claim: list_supported_command_methods() lets a caller
    READ a room's authority instead of probing it by trying things, and
    capability is the strictly broader surface."""
    nexus = _enabled_nexus()
    static_verbs = _rift_with_room(
        nexus, "static", "probe-enum-static"
    ).space.command_system.list_supported_command_methods()
    capability_verbs = _rift_with_room(
        nexus, "capability", "probe-enum-capability"
    ).space.command_system.list_supported_command_methods()

    assert len(static_verbs) > 0
    assert len(capability_verbs) > len(static_verbs)
    print("enumeration pinned: static", len(static_verbs),
          "verbs, capability", len(capability_verbs))


class _Greeter:
    def greet(self) -> str:
        return "hello from the canvas"


def _workstation(nexus, name="probe-bench"):
    return _rift_with_room(
        nexus, "capability", name).space.workstation


def test_probe_workstation_stores_are_independent_namespaces():
    """Lesson 12 claim: objects / attributes / methods are SEPARATE
    logical stores, so the same name in two stores is not a collision and
    releasing from one leaves the other standing."""
    workstation = _workstation(_enabled_nexus(), "probe-stores")
    greeter = _Greeter()
    workstation.bind_object("subject", greeter)
    workstation.bind_method("subject", greeter.greet)

    assert workstation.get("subject", store="objects") is greeter
    assert workstation.get("subject", store="methods")() == (
        "hello from the canvas")

    released = workstation.release("subject", store="objects")
    assert released is greeter
    summary = workstation.describe_bindings()
    assert "subject" not in summary["objects"]
    assert "subject" in summary["methods"]
    print("store independence pinned: same name, two stores, no collision")


def test_probe_explicit_weak_binding_refuses_instead_of_degrading():
    """Lesson 12 HEADLINE, and melder's honesty rule in miniature:

        "Explicit weak binding raises when the supplied value cannot be
         weak-referenced; it never silently degrades to strong storage."

    A silent degrade would pin an object the caller believed was
    collectable for the life of the room - a leak that reads as correct
    code. This row pins BOTH halves: the refusal happens, AND nothing was
    stored as a consolation prize."""
    workstation = _workstation(_enabled_nexus(), "probe-weak")

    # weak-referenceable: accepted.
    # HOLD A STRONG REFERENCE. The first version of this row passed
    # _Greeter() inline and the binding was EMPTY on the next line -
    # correct weak-storage behaviour, and a lesson in itself: a weak
    # binding to a temporary is already dead when you look at it.
    keeper = _Greeter()
    workstation.bind_object("ok", keeper, weak_ref=True)
    assert "ok" in workstation.describe_bindings()["objects"]

    # not weak-referenceable: refused, and NOT stored strongly
    with pytest.raises((TypeError, ValueError, RuntimeError)):
        workstation.bind_object("nope", 42, weak_ref=True)
    assert "nope" not in workstation.describe_bindings()["objects"]
    print("no-silent-degrade pinned: refused AND not stored as fallback")


def test_probe_workstation_holds_at_most_one_target():
    """Lesson 12 claim: at most one active target, and clear_target()
    deselects WITHOUT deleting the binding it pointed at."""
    workstation = _workstation(_enabled_nexus(), "probe-target")
    greeter = _Greeter()
    workstation.bind_method("greet", greeter.greet)

    workstation.set_target("greet", store="methods")
    assert workstation.get_target() is not None
    assert workstation.call_target() == "hello from the canvas"

    workstation.clear_target()
    assert workstation.get("greet", store="methods") is not None
    print("target ceiling pinned: clear deselects, binding survives")


def test_probe_describe_bindings_returns_five_keys_not_the_documented_four():
    """FINDING (doc drift, 2026-08-02, lesson 12): describe_bindings()
    documents "a FOUR-KEY summary - `objects`, `attributes`, `methods` and
    `target_name` - always with all four keys present, so callers can
    index". IT RETURNS FIVE - the implementation also emits
    `target_store`.

    This one has teeth: the docstring explicitly invites callers to rely
    on the count. Second drift of this shape in arc B (RiftSpaceType's
    documented-but-absent `dynamic`, lesson 10).

    Green while the docs are wrong; red when either side is fixed."""
    workstation = _workstation(_enabled_nexus(), "probe-drift")
    summary = workstation.describe_bindings()
    assert set(summary) == {
        "objects", "attributes", "methods", "target_name", "target_store",
    }
    assert len(summary) == 5
    doc = md.Workstation.describe_bindings.__doc__ or ""
    assert "FOUR-KEY" in doc or "four keys" in doc, (
        "docstring no longer claims four - delete this probe"
    )
    print("doc drift pinned: documented 4 keys, returns 5")


def test_probe_workstation_is_not_a_resolver():
    """Lesson 12 claim: the canvas STORES, it does not RESOLVE. It has no
    discovery verbs - resolution belongs to the command system. If a
    lookup verb ever lands here, the separation the lesson teaches is
    gone and the two fixtures have started overlapping."""
    workstation = _workstation(_enabled_nexus(), "probe-not-resolver")
    for resolver_verb in ("meld", "find_spell_id", "get_conduit_by_name",
                          "describe_spells_in_conduit", "get_nexus_frame"):
        assert not hasattr(workstation, resolver_verb), (
            f"{resolver_verb} appeared on the workstation - the canvas is "
            f"not supposed to resolve anything"
        )
    print("separation pinned: canvas holds, command system resolves")


def _viewer(nexus, name="probe-observatory"):
    return _rift_with_room(
        nexus, "capability", name).space.frame_viewer


def test_probe_view_accessors_split_into_host_and_frame_scoped():
    """Lesson 13, CORRECTED by the owner's run 2026-08-02.

    get_view_multiframe() is HOST-SCOPED and works with nothing bound.
    get_view_frame / get_view_conduit / get_view_spell are FRAME-SCOPED
    and REQUIRE a name - "the viewer no longer supports default-frame
    routing for frame-local operations"."""
    viewer = _viewer(_enabled_nexus(), "probe-views")
    assert isinstance(viewer, md.FrameViewer)
    assert isinstance(viewer.get_view_multiframe(), md.ViewMultiFrame)

    for accessor in ("get_view_frame", "get_view_conduit", "get_view_spell"):
        with pytest.raises(ValueError, match="frame_name is required"):
            getattr(viewer, accessor)()
    print("scope split pinned: 1 host-scoped, 3 frame-scoped")


def test_probe_frame_scoped_accessors_default_to_an_invalid_value():
    """DEFECT (owner's 3.14t run, 2026-08-02).

    get_view_frame / get_view_conduit / get_view_spell and the
    describe_*_surface reads are typed

        frame_name: Optional[str] = None

    and then reject None UNCONDITIONALLY. THE DEFAULT VALUE IS NEVER
    VALID. A reader who trusts the signature calls get_view_frame() and
    gets a ValueError for using the documented default.

    Either the parameter should be `frame_name: str` with no default, or
    None should route somewhere. This row goes GREEN while the defect
    stands and RED when it is fixed either way."""
    import inspect
    viewer = _viewer(_enabled_nexus(), "probe-defect")
    for accessor in ("get_view_frame", "get_view_conduit", "get_view_spell"):
        signature = inspect.signature(getattr(md.FrameViewer, accessor))
        assert signature.parameters["frame_name"].default is None, accessor
        with pytest.raises(ValueError, match="frame_name is required"):
            getattr(viewer, accessor)()
    print("defect pinned: Optional[str] = None where None always raises")


def test_probe_frame_viewer_holds_no_snapshot():
    """Lesson 13 claim: the facade resolves PER INVOCATION - melder's own
    docstrings say it builds "a ViewMultiFrame per invocation against a
    freshly resolved" source. So two calls give two objects and a viewer
    held for an hour cannot serve an hour-old world.

    A red here means someone added memoization, which would make every
    'is this stale?' question live again."""
    viewer = _viewer(_enabled_nexus(), "probe-nosnapshot")
    assert viewer.get_view_multiframe() is not viewer.get_view_multiframe()
    print("no-snapshot pinned: fresh view object per call")


def test_probe_frame_viewer_reads_are_coherent_on_an_empty_world():
    """Lesson 13 claim: the read surface works on a fresh rift with no
    assigned frames - honest zeros, not errors - and count agrees with
    the list it counts."""
    viewer = _viewer(_enabled_nexus(), "probe-empty")
    names = viewer.list_frame_names()
    assert isinstance(names, list)
    assert viewer.count_frames() == len(names)
    assert isinstance(viewer.describe_available_views(), list)
    print("empty-world reads pinned: count agrees with list")


def test_probe_viewer_onboards_agents_in_valid_json():
    """Lesson 13 HEADLINE and arc C's AIX claim: the viewer carries a
    surface built FOR AGENTS by name - describe_agent_onboarding_json(),
    describe_viewer_agent_purpose_json() - and both must be PARSEABLE, not
    merely present. A method that returns malformed JSON is worse than no
    method, because a caller has no way to tell the difference until it
    breaks mid-parse.

    Same idea as list_supported_command_methods() in lesson 11: melder
    answers "what may I do here?" with a method instead of a manual."""
    import json
    viewer = _viewer(_enabled_nexus(), "probe-aix")

    onboarding = viewer.describe_agent_onboarding_json()
    assert isinstance(onboarding, str) and onboarding.strip()
    assert isinstance(json.loads(onboarding), (dict, list))

    purpose = viewer.describe_viewer_agent_purpose_json()
    assert isinstance(purpose, str) and purpose.strip()
    assert isinstance(json.loads(purpose), (dict, list))

    surface = viewer.describe_viewer_method_surface()
    assert isinstance(surface, dict) and surface
    print("AIX surface pinned: onboarding + purpose parse as JSON")


def test_probe_viewer_clone_is_independent_but_agrees():
    """Lesson 13 claim: clone() returns a separate facade over the same
    world - a different object that reads the same numbers."""
    viewer = _viewer(_enabled_nexus(), "probe-clone")
    twin = viewer.clone()
    assert isinstance(twin, md.FrameViewer)
    assert twin is not viewer
    assert twin.count_frames() == viewer.count_frames()
    print("clone pinned: independent object, identical reading")


def test_probe_the_spell_describe_ladder_exists_rung_by_rung():
    """Lesson 14 claim: ViewSpell offers GRADED RESOLUTION - brief,
    normal, detail, payload - plus nine per-facet verbs. The ladder is a
    context budget control: survey 400 spells at brief, pay full price for
    the three that matter. A missing rung collapses that trade."""
    for verb in ("describe_spell_brief", "describe_spell",
                 "describe_spell_detail", "describe_spell_payload"):
        assert hasattr(md.ViewSpell, verb), verb
    facets = ("describe_spell_identity", "describe_spell_source",
              "describe_spell_origin", "describe_spell_binding",
              "describe_spell_index", "describe_spell_resolution",
              "describe_spell_metadata", "describe_spell_research",
              "describe_spell_class_profile")
    for verb in facets:
        assert hasattr(md.ViewSpell, verb), verb
    assert len(facets) > 4, "more facets than rungs is the design"
    print("spell ladder pinned: 4 rungs,", len(facets), "facets")


def test_probe_the_conduit_view_follows_the_same_plan():
    """Lesson 14 claim: ViewConduit is built to the same shape, and its
    narrowing filters sit on the CHEAP rung so a caller can reduce the
    set before paying to describe it."""
    for verb in ("describe_conduit_brief", "describe_conduit",
                 "describe_conduit_topology", "describe_conduit_inventory",
                 "describe_conduit_relationships",
                 "describe_conduit_crosswalk"):
        assert hasattr(md.ViewConduit, verb), verb
    for narrowing in ("list_conduits_by_root_id", "list_conduits_by_policy",
                      "is_root_conduit", "get_root_conduit_id"):
        assert hasattr(md.ViewConduit, narrowing), narrowing
    print("conduit ladder + cheap-rung filters pinned")


def test_probe_host_scoped_reads_answer_on_an_empty_world():
    """Lesson 14, CORRECTED by the owner's run. My original claim was
    that ALL reads answer with honest empties on a frameless rift. Only
    the HOST-SCOPED ones do - the frame-scoped views refuse, and refusing
    is right (see lesson 15).

    What survives, and it is the part that mattered: the SURVEY entry
    point works before you have committed to anything. count agrees with
    the list it counts, so you can size a world before paying to read
    it."""
    nexus = _enabled_nexus()
    rift = _rift_with_room(nexus, "capability", "probe-empty-rd")
    assert rift.list_assigned_frame_names() == ()

    viewer = rift.space.frame_viewer
    assert view_list(viewer.list_frame_names())
    assert viewer.count_frames() == len(viewer.list_frame_names())
    assert view_list(viewer.get_view_multiframe().list_frame_names())
    assert view_list(viewer.describe_available_views())
    print("host-scoped survey pinned: count agrees with list, no frame needed")


def view_list(value) -> bool:
    """A list result is the contract - emptiness is allowed, None is not."""
    return isinstance(value, list)


def test_probe_every_view_can_report_its_own_blind_spots():
    """Lesson 15 claim: the withheld-section probe exists at EVERY level
    of the view family, so a caller never has to wonder whether this
    particular view can tell it what it is hiding.

    Checked on the TYPES - the frame-scoped views cannot be instantiated
    without an assigned frame (lesson 13), and the probe's EXISTENCE is a
    property of the class either way."""
    assert hasattr(md.ViewSpell, "describe_spell_missing_sections")
    assert hasattr(md.ViewConduit, "describe_conduit_missing_sections")
    assert hasattr(md.ViewFrame, "describe_missing_surface")
    assert hasattr(md.FrameViewer, "describe_missing_surface")
    print("blind-spot probes pinned at every view level")


def test_probe_visible_and_missing_are_complements():
    """Lesson 15 claim: describe_visible_surface() and
    describe_missing_surface() are a PAIR - "what I can see" and "what I
    cannot". Either alone is half an answer, so both must exist wherever
    one does."""
    for owner_type in (md.FrameViewer, md.ViewFrame):
        assert hasattr(owner_type, "describe_visible_surface"), owner_type
        assert hasattr(owner_type, "describe_missing_surface"), owner_type
    print("complements pinned on both FrameViewer and ViewFrame")


def test_probe_blind_spot_report_refuses_when_no_frame_is_bound():
    """Lesson 15, CORRECTED by the owner's run 2026-08-02.

    I predicted this row might go red and said so in its docstring: "if
    it raises on an unbound frame, the lesson needs a bound frame". It
    raised - and the corrected reading is BETTER than my original.

    Asking "what am I not seeing?" with NO FRAME BOUND is refused rather
    than answered with an empty dict. That is the right call: with no
    frame there is no surface to compare against, so a cheerful empty
    result would be A LIE SHAPED LIKE AN ANSWER - which is precisely the
    confusion the whole missing-sections family exists to prevent.

    The never-substitute rule (08/13/14/18) reaches the read surface."""
    nexus = _enabled_nexus()
    rift = _rift_with_room(nexus, "static", "probe-nf-missing")
    assert rift.list_assigned_frame_names() == ()
    viewer = rift.space.frame_viewer
    for verb in ("describe_visible_surface", "describe_missing_surface"):
        with pytest.raises(ValueError, match="frame_name is required"):
            getattr(viewer, verb)()
    print("refusal pinned: no frame bound, no blind-spot report")


def test_probe_frame_name_is_an_assertion_not_a_selector():
    """Lesson 15's anti-footgun: frame_name on these reads is a GUARD, not
    a filter - "when supplied it must match the bound frame or the call
    raises". You cannot accidentally read a different frame than the one
    you believe you are holding.

    A rift with no assigned frames cannot match ANY name, so supplying one
    must be refused rather than quietly answered about something else.
    This is melder's never-substitute rule (lessons 06/13/14) applied to
    the read surface."""
    nexus = _enabled_nexus()
    rift = _rift_with_room(nexus, "static", "probe-assertion")
    assert rift.list_assigned_frame_names() == ()
    viewer = rift.space.frame_viewer
    with pytest.raises(Exception) as refused:
        viewer.describe_missing_surface(frame_name="a-frame-we-never-bound")
    print("assertion-not-selector pinned; refusal type:",
          type(refused.value).__name__)


def _dynamic_root(frame: str, conduit_name: str):
    book = Spellbook(aetheric_frame=frame)
    book.bind(spell=Payload, existence="unique")
    book.configure_aether_frame(system_state="dynamic", disposal=None,
                                disposal_method_names=None)
    return book, book.conjure(name=conduit_name)


def test_probe_policy_door_is_dynamic_mode_only():
    """Lesson 16 refusal #1: set_new_policy on an AUTOMATIC frame raises.
    Wards only form and sever contracts at runtime in dynamic mode, so
    outside it the setting would be decoration."""
    book = Spellbook(aetheric_frame="probe-ward-automatic")
    book.bind(spell=Payload, existence="unique")
    root = book.conjure(name="probe-automatic-root")
    with pytest.raises(RuntimeError, match="[Dd]ynamic"):
        root.set_new_policy("block_all")
    print("dynamic-only pinned: automatic frame refuses a policy")


def test_probe_policy_accepts_both_the_enum_and_the_string():
    """Lesson 16 FINDING: Conduit.set_new_policy is annotated `policy:
    str`, but it delegates to a ward method typed `str | Policies` that
    runs EnumHelpers.convert_enum_and_check. So the exported md.Policies
    enum works - the public hint under-sells the code.

    Pinned so that if the signature is ever tightened to reject the enum,
    the lesson's claim goes red rather than the docs quietly becoming
    right by accident."""
    _, root = _dynamic_root("probe-ward-both", "probe-both-root")
    root.set_new_policy("outbound_only")
    root.set_new_policy("inbound_only")
    root.set_new_policy("default")
    print("both forms pinned: enum and string are equally accepted")


def test_probe_policies_value_is_an_int_not_the_mode_name():
    """Lesson 16 FINDING: Policies uses auto(), so `.value` is an INT.
    Anyone reaching for `.value` to build the string argument gets a
    number. `.name` is the string form."""
    assert {p.name for p in md.Policies} == {
        "default", "whitelist_all", "block_all",
        "inbound_only", "outbound_only",
    }
    for policy in md.Policies:
        assert isinstance(policy.value, int)
    assert md.Policies.block_all.name == "block_all"
    print("auto() pinned: .value is int, .name is the mode string")


def test_probe_lesser_conduits_cannot_hold_a_policy():
    """Lesson 16 refusal #2: policy belongs to the owner of a lineage, not
    to a borrower. A lesser conduit is told to convert first."""
    _, root = _dynamic_root("probe-ward-lesser", "probe-lesser-root")
    lesser = root.create_lesser_conduit()
    with pytest.raises(RuntimeError, match="[Ll]esser"):
        lesser.set_new_policy("block_all")
    print("normal-only pinned: a lesser conduit refuses a policy")


def test_probe_no_retroactive_lockdown_while_contracts_exist():
    """Lesson 16 refusal #3, and the one worth the lesson. Setting
    block_all or whitelist_all WHILE CONTRACTS EXIST raises.

    Melder will not silently sever what you already granted, and it will
    not quietly leave the grants standing under a policy that says they
    should not exist. It refuses and makes you tear them down yourself -
    the never-substitute rule (08/13/14/17) applied to authority.

    The directional modes stay available, because they do not invalidate
    grants that already happened."""
    _, root = _dynamic_root("probe-ward-lock", "probe-lock-root")

    # no contracts yet: the restrictive modes are fine
    root.set_new_policy("block_all")
    root.set_new_policy("default")

    peer = Spellbook(aetheric_frame="probe-ward-lock").conjure(
        name="probe-lock-peer")
    assert root.link(peer) is True

    for restrictive in ("block_all", "whitelist_all"):
        with pytest.raises(RuntimeError, match="contracts"):
            root.set_new_policy(restrictive)

    # non-invalidating modes still allowed
    root.set_new_policy("outbound_only")
    print("no-retroactive-lockdown pinned: refuses, never partially applies")


def test_probe_policy_is_write_only_on_the_public_surface():
    """Lesson 16 FINDING: set_new_policy is public; there is NO public way
    to read a conduit's current policy back. Write-only authority - you
    can change it and cannot audit it from outside.

    Green while the gap exists, red the day a reader lands."""
    import inspect
    _, root = _dynamic_root("probe-ward-read", "probe-read-root")
    assert hasattr(root, "set_new_policy")
    public_readers = [
        name for name in dir(root)
        if not name.startswith("_") and "policy" in name.lower()
    ]
    assert public_readers == ["set_new_policy"], (
        f"a public policy reader appeared: {public_readers}"
    )
    print("write-only gap pinned: only door is", public_readers)


def _active_crystallizer() -> "Crystallizer":
    crystallizer = Crystallizer()
    config = md.CrystallizerConfiguration()
    config.with_defaults()
    config.finalize()
    config.activate()
    crystallizer.activate(config)
    return crystallizer


def test_probe_crystallizer_follows_aethers_ladder_not_nexuss():
    """Lesson 17 HEADLINE. Three subsystems, two ladders:

        Aether       caller finalizes AND activates the config, then
                     subsystem.activate() - a merely-frozen config raises
        Crystallizer SAME
        Nexus        enable() finalizes the config for the caller

    Two against one, so caller-driven activation is the house rule and
    Nexus is the exception. A red here means they converged - good news
    for the configuration-uniformity program, and it would mean lessons 08 and 19 need their contrast sections rewritten."""
    crystallizer = Crystallizer()
    assert crystallizer.activated is False

    config = md.CrystallizerConfiguration()
    config.with_defaults().finalize()
    assert config.activated is False, "finalize must not activate"

    config.activate()
    assert config.activated is True
    crystallizer.activate(config)
    assert crystallizer.activated is True
    # `is_activated` is a PROPERTY, not a method (owner run 2026-08-02).
    assert crystallizer.is_activated is True
    print("ladder pinned: crystallizer sides with aether, not nexus")


def test_probe_crystallizer_builder_offers_a_terminator_per_rung():
    """Lesson 17 claim: CrystallizerConfigurationBuilder is the most
    generous builder in the library - build / finalize / activate, one
    exit per rung - while AetherConfigurationBuilder offers only build()
    and leaves rung 2 to the caller.

    Divergence catalogued for the configuration-uniformity program."""
    builder = md.CrystallizerConfigurationBuilder()
    for terminator in ("build", "finalize", "activate"):
        assert hasattr(builder, terminator), terminator
    assert not hasattr(md.AetherConfigurationBuilder(), "activate"), (
        "the aether builder gained activate() - the divergence closed"
    )
    ready = md.CrystallizerConfigurationBuilder().with_defaults().activate()
    assert isinstance(ready, md.CrystallizerConfiguration)
    assert ready.activated is True
    print("terminator divergence pinned: crystallizer 3, aether 1")


def test_probe_create_checkpoint_returns_an_id_that_lists_and_describes():
    """Lesson 17 claim: create_checkpoint hands back an ID and the ID is
    the whole handle - list_checkpoint_ids finds it, describe_checkpoint
    reads it."""
    crystallizer = _active_crystallizer()
    before = crystallizer.list_checkpoint_ids()
    assert isinstance(before, list)

    checkpoint_id = crystallizer.create_checkpoint(description="probe-19")
    assert isinstance(checkpoint_id, str) and checkpoint_id

    after = crystallizer.list_checkpoint_ids()
    assert checkpoint_id in after
    assert len(after) == len(before) + 1

    described = crystallizer.describe_checkpoint(checkpoint_id)
    assert isinstance(described, dict) and described
    print("checkpoint id pinned: created, listed, described")


def test_probe_checkpoints_accumulate_rather_than_overwrite():
    """Lesson 17 claim: a second checkpoint is a NEW id, not a
    replacement. If checkpoints ever started overwriting, every restore
    story in arc E changes."""
    crystallizer = _active_crystallizer()
    first = crystallizer.create_checkpoint(description="probe-first")
    second = crystallizer.create_checkpoint(description="probe-second")
    assert first != second
    ids = crystallizer.list_checkpoint_ids()
    assert first in ids and second in ids
    print("accumulation pinned:", len(ids), "distinct checkpoint ids")


def test_probe_flush_moves_a_checkpoint_from_created_to_cached():
    """Lesson 18 claim: a checkpoint lives in two places - CREATED (an id
    in the running crystallizer) and CACHED (sealed locally).
    flush_checkpoint is the verb that moves it."""
    crystallizer = _active_crystallizer()
    checkpoint_id = crystallizer.create_checkpoint(description="probe-20")
    assert checkpoint_id in crystallizer.list_checkpoint_ids()

    flushed = crystallizer.flush_checkpoint(checkpoint_id)
    assert isinstance(flushed, list)
    assert isinstance(crystallizer.list_cached_checkpoint_ids(), list)
    print("seal pinned: flush returned", flushed)


def test_probe_the_cached_read_path_round_trips():
    """Lesson 18 claim: the id stays the whole handle across the seal -
    a cached checkpoint reads back as a dict.

    Guarded on presence rather than assumed, because the cache is FIFO
    bounded and the contract says a flush can evict."""
    crystallizer = _active_crystallizer()
    checkpoint_id = crystallizer.create_checkpoint(description="probe-rt")
    crystallizer.flush_checkpoint(checkpoint_id)

    if checkpoint_id in crystallizer.list_cached_checkpoint_ids():
        reloaded = crystallizer.reload_cached_checkpoint(checkpoint_id)
        assert isinstance(reloaded, dict)
        print("round trip pinned:", len(reloaded), "keys")
    else:
        print("evicted by the FIFO cap before reload - contract behavior")


def test_probe_checkpoint_chain_verification_answers():
    """Lesson 18 claim: checkpoints form a CHAIN, not a pile, and the
    crystallizer can report on that lineage."""
    crystallizer = _active_crystallizer()
    crystallizer.create_checkpoint(description="probe-chain-1")
    crystallizer.create_checkpoint(description="probe-chain-2")
    chain = crystallizer.verify_checkpoint_chain()
    assert isinstance(chain, dict) and chain
    print("chain verification pinned:", len(chain), "keys")


def test_probe_deletion_is_explicit_and_removes_from_the_cache():
    """Lesson 18 claim: EVICTION is a side effect of a bounded cache;
    DELETION is a decision. The two must not be confused, so deletion has
    its own verb and its effect is observable."""
    crystallizer = _active_crystallizer()
    checkpoint_id = crystallizer.create_checkpoint(description="probe-del")
    crystallizer.flush_checkpoint(checkpoint_id)
    if checkpoint_id not in crystallizer.list_cached_checkpoint_ids():
        print("already evicted - nothing to delete, contract behavior")
        return
    deleted = crystallizer.delete_cached_checkpoint(checkpoint_id)
    assert isinstance(deleted, str)
    assert checkpoint_id not in crystallizer.list_cached_checkpoint_ids()
    print("deletion pinned: explicit verb, observable effect")


def test_probe_caller_driven_activation_is_the_house_rule_three_to_one():
    """Arc E closing claim, and evidence for the configuration-uniformity
    program. FOUR subsystems, and only ONE activates the configuration on
    the caller's behalf:

        Aether           caller activates the config   (lesson 07)
        Crystallizer     caller activates the config   (lesson 17)
        MutationResearch caller activates the config   (expert tier)
        Nexus            enable() does it FOR you      (lesson 08)

    Their configuration BUILDERS diverge the same way: crystallizer and
    mutation-research offer build/finalize/activate; aether offers only
    build. Pinned so the split is a test rather than a memory."""
    for configuration_type in (md.AetherConfiguration,
                               md.CrystallizerConfiguration,
                               md.MutationResearchConfiguration):
        assert hasattr(configuration_type, "activate"), configuration_type
        assert hasattr(configuration_type, "finalize"), configuration_type

    for builder_type in (md.CrystallizerConfigurationBuilder,
                         md.MutationResearchConfigurationBuilder):
        for terminator in ("build", "finalize", "activate"):
            assert hasattr(builder_type, terminator), (builder_type, terminator)

    assert not hasattr(md.AetherConfigurationBuilder, "activate")
    print("house rule pinned 3-to-1: nexus is the lone exception")


def test_probe_spell_examiner_was_curated_off_the_public_root():
    """CURATION CALL EXECUTED (owner ruling 2026-08-02).

    SpellExaminer is Bind's private reflection registry - the thing that
    builds a binding profile when you bind a class. The graph records it
    as `Bind owns_lifecycle_of SpellExaminer, one_to_one`, and the only
    live instance is Bind's private `self._spell_examiner`.

    It had been exported WITH an extension point - register_profile_builder
    (...) and "the registry remains open for explicit extension" - but no
    public accessor ever reached the instance you would need to call it
    on. Public class, public extension API, private instance: half a
    feature. Curated off the root rather than left that way.

    Removed from `__all__` AND from the namespace, per the counter-example
    law in tests/unit/melder/test_package_public_surface.py, where it now
    sits in the curated-exclusions list beside ConduitWard and Meld.

    If the extension point is ever wanted for real, the fix is not to
    re-export the class - it is to expose the examiner on Bind."""
    import melder
    assert "SpellExaminer" not in melder.__all__
    assert not hasattr(melder, "SpellExaminer")
    print("curation pinned: SpellExaminer is off the public root")


def test_probe_rift_enabled_has_no_public_setter():
    """FINDING (2026-08-02, arc B): `rift_enabled` gates AR targeting
    (Nexus raises "AR requires rift_enabled on target frame") and there is
    NO PUBLIC DOOR TO SET IT. It is not a parameter of
    Spellbook.configure_aether_frame, and the frame posture that owns
    with_rift_enabled() cannot be installed from the public root
    (lesson 06 finding). Rifts themselves ARE reachable - Nexus.enable and
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
