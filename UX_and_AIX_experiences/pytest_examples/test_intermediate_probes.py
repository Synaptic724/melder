"""
Intermediate-tier contract probes. Run on 3.14t:

    pytest UX_and_AIX_experiences/pytest_examples/test_intermediate_probes.py -v

Probes print ground truth for lessons not yet authored - the crystallizer
acquisition path and the dynamic config-before-bind law (whose error text
we captured verbatim from a live traceback this session).
"""
import sys

import melder as md
import pytest

from melder import Aether, Conduit
from melder.aether.spellbook.spellbook import Spellbook


@pytest.fixture(autouse=True)
def reset_aether_world() -> None:
    Aether._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether
    yield
    Aether._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether


class Payload:
    pass


def test_probe_dynamic_flag_settles_fresh_world():
    """
    SETTLE-THEN-INHERIT (landed 2026-07-20): on a fresh world the
    dynamic flag SETTLES the posture and conjure proceeds - the old
    always-refuse law is repealed by design.
    """
    conduit = _dyn_book().conjure(dynamic=True, name="settled")
    assert conduit is not None


def test_probe_helper_postured_dynamic_world_links():
    """The lesson-21 flow (settle at first dynamic conjure) works end to end."""
    import sys
    from pathlib import Path as _P
    sys.path.insert(0, str(_P(__file__).parent.parent / "02_intermediate"))
    from _dynamic_world import dynamic_spellbook

    owner_book = dynamic_spellbook()
    owner_book.bind(spell=Payload, existence="unique")
    owner = owner_book.conjure(dynamic=True, name="owner")
    borrower = dynamic_spellbook().conjure(dynamic=True, name="borrower")
    assert owner.link(borrower) is True


def _dyn_book() -> Spellbook:
    book = Spellbook()
    book.bind(spell=Payload, existence="unique")
    return book


def test_probe_crystallizer_acquisition_path():
    """
    OPEN QUESTION for the crystallizer lessons: how does a USER reach the
    live crystallizer (dynamic world, NO Nexus)? Prints which public doors
    exist on Aether so the next lesson copies truth.
    """
    aether = Aether()
    doors = [name for name in ("crystallizer", "get_crystallizer",
                               "hosted_crystallizer")
             if hasattr(aether, name)]
    print("crystallizer doors on Aether:", doors or "none of the guesses")
    print("md.Crystallizer exported:", md.Crystallizer is not None)


def test_probe_dynamic_config_before_bind_law():
    """
    CAPTURED CONTRACT (live traceback, run 2): dynamic-mode conjure with
    an ACTIVE crystallizer refuses books whose binds preceded config
    finalization. Without an active crystallizer, dynamic worlds are
    exempt - this probe pins the exemption; the active-crystallizer half
    waits on the acquisition probe above.
    """
    book = Spellbook()
    book.bind(spell=Payload, existence="unique")  # bind BEFORE any config
    conduit = book.conjure(dynamic=True, name="exempt-world")
    assert conduit is not None
    print("crystallizer-off dynamic world: bind-before-config exempt (as documented)")
def test_probe_world_settles_once_then_inherits():
    """Settle-then-inherit law: the first dynamic conjure settles the
    world; later books INHERIT with a plain conjure - no reposture."""
    import sys
    from pathlib import Path as _P
    sys.path.insert(0, str(_P(__file__).parent.parent / "02_intermediate"))
    from _dynamic_world import dynamic_spellbook

    settler_book = dynamic_spellbook()
    settler_book.bind(spell=Payload, existence="unique")
    settler = settler_book.conjure(dynamic=True, name="settler")
    inheritor = dynamic_spellbook().conjure(name="inheritor")  # no flag
    assert settler.link(inheritor) is True
    print("settled once; the second book inherited dynamic via plain conjure")


def test_probe_spell_contract_closes_across_linked_categories():
    """Lesson 26 base contract: a SpellContract socket closes when the
    provider arrives from a LINKED conduit - normal verbs only: link,
    pull, meld."""
    import sys
    from pathlib import Path as _P
    from typing import Protocol
    sys.path.insert(0, str(_P(__file__).parent.parent / "02_intermediate"))
    from _dynamic_world import dynamic_spellbook

    class IStore(Protocol):
        def get(self, key: str) -> str: ...

    class PlatformStore:
        def get(self, key: str) -> str:
            return f"{key}-ok"

    class NeedsStore:
        def __init__(self, store: IStore = md.SpellContract(
                spellframe=IStore, binding_name="platform")) -> None:
            self.store = store

    platform_book = dynamic_spellbook()
    store_id = platform_book.bind(spell=PlatformStore, existence="unique",
                                  spellframe=IStore, binding_name="platform")
    services_book = dynamic_spellbook()
    consumer_id = services_book.bind(spell=NeedsStore, existence="unique")

    platform = platform_book.conjure(dynamic=True, name="platform")
    services = services_book.conjure(dynamic=True, name="services")
    platform.link(services)
    assert services.add_spell_to_contract(
        spell_id=store_id, conduit=platform, permissions="create")

    consumer = services.meld(spell=consumer_id)
    assert isinstance(consumer, NeedsStore)
    assert consumer.store.get("region") == "region-ok"
    print("contract socket closed across the link")


def test_probe_two_hop_chain_canonical_order():
    """Lesson 26 contract, owner-ruled ORDER OF OPERATIONS (2026-07-20):
    per edge - conjure provider, conjure consumer, LINK after both are
    built, pull into the contract, then MELD after the fact. Edges are
    assembled in dependency order; the downstream category receives the
    edge's finished product (owner-creations reuse)."""
    import sys
    from pathlib import Path as _P
    from typing import Protocol
    sys.path.insert(0, str(_P(__file__).parent.parent / "02_intermediate"))
    from _dynamic_world import dynamic_spellbook

    class IConf(Protocol):
        def get(self, key: str) -> str: ...

    class IReport(Protocol):
        def report(self) -> str: ...

    class Conf:
        def get(self, key: str) -> str:
            return f"{key}-v"

    class Svc:
        def __init__(self, conf: IConf = md.SpellContract(
                spellframe=IConf, binding_name="platform")) -> None:
            self.conf = conf

        def report(self) -> str:
            return f"r({self.conf.get('region')})"

    class Flow:
        def __init__(self, svc: IReport = md.SpellContract(
                spellframe=IReport, binding_name="reporting")) -> None:
            self.svc = svc

        def run(self) -> str:
            return f"w->{self.svc.report()}"

    platform_book = dynamic_spellbook()
    conf_id = platform_book.bind(spell=Conf, existence="unique",
                                 spellframe=IConf, binding_name="platform")
    services_book = dynamic_spellbook()
    svc_id = services_book.bind(spell=Svc, existence="unique",
                                spellframe=IReport, binding_name="reporting")
    workflows_book = dynamic_spellbook()
    flow_id = workflows_book.bind(spell=Flow, existence="unique")

    # EDGE 1: provider conjured, consumer conjured, link AFTER both,
    # pull, meld after the fact.
    platform = platform_book.conjure(dynamic=True, name="platform")
    services = services_book.conjure(dynamic=True, name="services")
    assert platform.link(services) is True
    assert services.add_spell_to_contract(
        spell_id=conf_id, conduit=platform, permissions="create")
    service = services.meld(spell=svc_id)
    assert service.report() == "r(region-v)"

    # EDGE 2: same cycle one level up.
    workflows = workflows_book.conjure(dynamic=True, name="workflows")
    assert services.link(workflows) is True
    assert workflows.add_spell_to_contract(
        spell_id=svc_id, conduit=services, permissions="create")
    flow = workflows.meld(spell=flow_id)

    assert isinstance(flow, Flow)
    assert flow.svc is service  # the edge handed over the finished product
    assert flow.run() == "w->r(region-v)"
    print("two-hop category chain resolved in canonical order")


def test_probe_spell_override_targets_spells_inside_the_graph():
    """spell_override, both forms pinned. Flat dict = keyword overrides
    for the ROOT spell's own constructor (intermediate lesson 08 - kept
    simple on purpose). ">"-path key = walks dependency parameter names
    and REPLACES the actual object at that socket inside the graph
    (advanced lesson 02; mirrors the component deep-override suite)."""
    class Leaf:
        def __init__(self) -> None:
            self.marker = "default"

    class OtherLeaf:
        def __init__(self) -> None:
            self.marker = "other-default"

    class Branch:
        def __init__(self, left: Leaf, right: OtherLeaf) -> None:
            self.left, self.right = left, right

    class OtherBranch:
        def __init__(self, left: Leaf, right: OtherLeaf) -> None:
            self.left, self.right = left, right

    class Root:
        def __init__(self, left: Branch, right: OtherBranch) -> None:
            self.left, self.right = left, right

    class Mailer:
        def __init__(self, host: str = "localhost", port: int = 25) -> None:
            self.host, self.port = host, port

    book = Spellbook()
    for cls in (Leaf, OtherLeaf, Branch, OtherBranch, Root):
        book.bind(spell=cls, existence="unique")
    book.bind(spell=Mailer, existence="many")
    conduit = book.conjure(name="override-probe")

    # FORM 1: flat dict -> root ctor kwargs.
    mailer = conduit.meld(spell=Mailer,
                          spell_override={"host": "h", "port": 9})
    assert (mailer.host, mailer.port) == ("h", 9)

    # FORM 2: ">"-path -> replace the object at a socket in the graph.
    replacement = OtherLeaf()
    replacement.marker = "replaced"
    root = conduit.meld(spell=Root,
                        spell_override={"left>right": replacement})
    assert root.left.right is replacement
    assert root.left.right.marker == "replaced"
    assert root.right.right is not replacement  # untargeted socket kept
    assert root.right.right.marker == "other-default"
    print("spell_override proven: root kwargs + inside-the-graph path swap")


def test_probe_sever_link_kills_the_contract():
    """Lesson 27 contract: contracts ride links - severing removes the
    borrower's RIGHT TO RESOLVE the pulled spell (next meld refuses)
    while the owner's own resolution is untouched; a second sever
    refuses (no contract left to remove). Exception types printed for
    the decode pass; tighten once run-proven."""
    import sys
    from pathlib import Path as _P
    sys.path.insert(0, str(_P(__file__).parent.parent / "02_intermediate"))
    from _dynamic_world import dynamic_spellbook

    owner_book = dynamic_spellbook()
    spell_id = owner_book.bind(spell=Payload, existence="unique")
    owner = owner_book.conjure(dynamic=True, name="sever-owner")
    borrower = dynamic_spellbook().conjure(name="sever-borrower")

    assert owner.link(borrower) is True
    assert borrower.add_spell_to_contract(
        spell_id=spell_id, conduit=owner, permissions="create")
    shared = borrower.meld(spell=Payload)
    assert shared is not None

    owner.sever_link(borrower)

    with pytest.raises(Exception) as post_sever:
        borrower.meld(spell=Payload)
    print("post-sever meld refusal type:", type(post_sever.value).__name__)

    assert owner.has_live_creation(spell=Payload) is True  # creations retained
    assert owner.meld(spell=Payload) is shared  # owner world untouched

    with pytest.raises(Exception) as double_sever:
        owner.sever_link(borrower)
    print("double-sever refusal type:", type(double_sever.value).__name__)


def test_probe_upgrade_to_normal_keeps_creations_and_registers():
    """Lesson 28 contract (mirrors the validated component test
    test_component_conduit_upgrade_transfers_lesser_creations_and_
    reuses_unique): a promoted lesser keeps its per-conduit creations
    and becomes name-discoverable in the cloud."""
    import sys
    from pathlib import Path as _P
    sys.path.insert(0, str(_P(__file__).parent.parent / "02_intermediate"))
    from _dynamic_world import dynamic_spellbook

    book = dynamic_spellbook()
    book.bind(spell=Payload, existence="unique_per_conduit")
    root = book.conjure(dynamic=True, name="factory-floor")

    worker = root.create_lesser_conduit()
    before = worker.meld(spell=Payload)

    worker.upgrade_to_normal(name="worker")

    after = worker.meld(spell=Payload)
    assert after is before  # creations survive the promotion
    cloud = root.get_conduit_cloud()
    assert cloud.get_conduit_by_name("worker") is worker
    print("promotion kept creations and registered the name")


def test_probe_scoped_cleanup_child_disposes_root_survives():
    """Lesson 29 contract: a lesser conduit is a throwaway scope -
    child.cleanup() fires the book's disposal vocabulary on the CHILD's
    per-conduit creations only; the root's instance stays open, the
    root keeps resolving the same instance, and root.cleanup() closes
    its own on the way out."""
    class JobSession:
        def __init__(self) -> None:
            self.closed = False

        def close(self) -> None:
            self.closed = True

    book = Spellbook()
    book.bind(spell=JobSession, existence="unique_per_conduit",
              disposal_method_names=["close"])
    root = book.conjure(name="scope-root")

    root_session = root.meld(spell=JobSession)
    job = root.create_lesser_conduit()
    job_session = job.meld(spell=JobSession)
    assert job_session is not root_session

    job.cleanup()
    assert job_session.closed is True      # child scope disposed its own
    assert root_session.closed is False    # root untouched
    assert root.meld(spell=JobSession) is root_session  # root still resolves

    root.cleanup()
    assert root_session.closed is True     # world teardown closes the rest
    print("scoped cleanup: child disposed locally, root survived then closed")


def test_probe_lifecycle_law_runtime_holds_until_cleanup():
    """Beginner-41 contract, pinned in the mirror: the runtime HOLDS
    what it builds - after del + gc the melded unique instance is still
    alive (creations store references it); after conduit.cleanup() +
    gc it is collected. A red on the second half is a RETENTION LEAK
    finding, not a lesson bug."""
    import gc
    import weakref

    class HeavyThing:
        pass

    book = Spellbook()
    book.bind(spell=HeavyThing, existence="unique")
    conduit = book.conjure(name="memory-probe")

    thing = conduit.meld(spell=HeavyThing)
    watcher = weakref.ref(thing)
    del thing
    gc.collect()
    assert watcher() is not None   # the world still holds it

    conduit.cleanup()
    gc.collect()
    assert watcher() is None       # cleanup returned the memory
    print("lifecycle law pinned: held until cleanup, freed after")


def test_probe_config_idempotent_and_freeze_laws():
    """Lessons 19/30 contract: disposal + disposal_method_names are
    set-once (second set refuses); conjure freezes the WHOLE config
    (any set_property after refuses). Types printed for the decode."""
    # CONFIGURE-THEN-LOCK. A bare Spellbook() has already taken the standard
    # default set, and that set is COMPLETE - it fills disposal too. Since
    # disposal is set-once, a defaulted book has no room left for it. State
    # the policy first, then build the book on it.
    config = md.SpellbookConfiguration()
    config.set_property("disposal", True)
    config.set_property("disposal_method_names", ["close"])
    config.set_property("phase_scheduler_workers_per_spellbook", 5)
    config.set_property(
        "phase_scheduler_barrier_timeout_milliseconds", 60000)
    book = Spellbook(configuration=config)
    with pytest.raises(Exception) as idem:
        config.set_property("disposal", False)
    print("idempotent re-set refusal:", type(idem.value).__name__)
    book.bind(spell=Payload, existence="unique")
    book.conjure(name="config-law-probe")
    with pytest.raises(Exception) as frozen:
        config.set_property("phase_scheduler_workers_per_spellbook", 2)
    print("post-conjure set refusal:", type(frozen.value).__name__)


def test_probe_config_hook_families_fire():
    """Lessons 32-34 contract: meld pre/post fire per meld; the conduit
    lifecycle fires in order around conjure/cleanup; link + contract +
    unlink hooks fire across the dynamic arc (owner-book side)."""
    import sys
    from pathlib import Path as _P
    sys.path.insert(0, str(_P(__file__).parent.parent / "02_intermediate"))
    from _dynamic_world import dynamic_spellbook

    seen = []
    owner_book = dynamic_spellbook()
    config = owner_book.get_configuration()
    for name in ("on_meld_pre_resolve", "on_meld_post_resolve",
                 "on_conduit_pre_created", "on_conduit_post_created",
                 "on_conduit_activated", "on_conduit_post_link",
                 "on_contract_created", "on_contract_removed",
                 "on_conduit_post_unlink", "on_conduit_cleanup_start",
                 "on_conduit_cleanup_complete"):
        config.add_hook(owner_book.id, name,
                        (lambda n: lambda *a, **k: seen.append(n))(name))

    spell_id = owner_book.bind(spell=Payload, existence="unique")
    owner = owner_book.conjure(dynamic=True, name="hookprobe-owner")
    borrower = dynamic_spellbook().conjure(name="hookprobe-borrower")

    owner.meld(spell=Payload)
    owner.link(borrower)
    borrower.add_spell_to_contract(spell_id=spell_id, conduit=owner,
                                   permissions="create")
    owner.sever_link(borrower)
    owner.cleanup()

    print("hook stream:", seen)
    assert "on_meld_pre_resolve" in seen and "on_meld_post_resolve" in seen
    assert "on_conduit_pre_created" in seen
    assert "on_conduit_post_link" in seen
    assert seen.index("on_conduit_pre_created") < seen.index(
        "on_conduit_cleanup_start")
    print("all hook families observable; stream printed for the decode")


def test_probe_config_definition_laws():
    """Lesson 31 contract: the four laws pinned - closed registry
    (unknown key), idempotent pair (set-once), freeze (post-conjure),
    completion (a bare unfinished config refuses at conjure). Types
    printed for the decode pass."""
    # No with_defaults() here: this config states every value itself.
    # Defaults are complete and terminal, so asking for them first would
    # consume the set-once disposal pair before these lines could write it.
    config = md.SpellbookConfiguration()
    config.set_property("disposal", True)
    config.set_property("disposal_method_names", ["close"])
    config.set_property("phase_scheduler_workers_per_spellbook", 1)
    config.set_property(
        "phase_scheduler_barrier_timeout_milliseconds", 30000)

    with pytest.raises(Exception) as unknown:
        config.set_property("not_a_real_property", 1)
    print("unknown key:", type(unknown.value).__name__)

    with pytest.raises(Exception) as idem:
        config.set_property("disposal", False)
    print("idempotent re-set:", type(idem.value).__name__)

    book = Spellbook(configuration=config)
    book.bind(spell=Payload, existence="unique")
    book.conjure(name="definition-probe")
    with pytest.raises(Exception) as frozen:
        config.set_property("phase_scheduler_workers_per_spellbook", 2)
    print("post-freeze:", type(frozen.value).__name__)

    bare = Spellbook(configuration=md.SpellbookConfiguration())
    bare.bind(spell=Payload, existence="unique", binding_name="bare")
    with pytest.raises(Exception) as incomplete:
        bare.conjure(name="bare-probe")
    print("incomplete config at conjure:", type(incomplete.value).__name__)


def test_probe_manual_config_share_across_books():
    """Lesson 35 contract, shape 1 (fully public): ONE configuration
    object handed to two books - both read the same object, both
    conjure under it."""
    class Alpha:
        pass

    class Beta:
        pass

    shared = md.SpellbookConfiguration()
    shared.with_defaults()
    shared.set_property("phase_scheduler_workers_per_spellbook", 1)
    book_a = Spellbook(configuration=shared)
    book_b = Spellbook(configuration=shared)
    assert book_a.get_configuration() is book_b.get_configuration()
    book_a.bind(spell=Alpha, existence="unique")
    book_b.bind(spell=Beta, existence="unique")
    assert book_a.conjure(name="share-a").meld(spell=Alpha) is not None
    assert book_b.conjure(name="share-b").meld(spell=Beta) is not None
    print("manual share: one object, two books, both conjured")


def test_probe_config_is_per_book_by_default():
    """DEFAULT LAW: spellbook configuration is PER-BOOK, not per-frame.
    Two books on the SAME frame mint two DIFFERENT configuration
    objects, because the frame posture ships with
    shared_framewide_spellbook_configuration=False
    (AethericFrameConfiguration ctor default, aetheric_frame_configuration.py:118;
    frame-minted posture, aetheric_frame.py:224; with_defaults() resets it
    to False, :1177 - and dynamic_defaults()/automatic_defaults() are
    with_defaults() plus a state, so they are False too).
    This probe is the tripwire: if the runtime ever defaults sharing ON,
    this test goes red on purpose."""
    first = Spellbook(aetheric_frame="per-book-default")
    second = Spellbook(aetheric_frame="per-book-default")
    assert first.get_configuration() is not second.get_configuration()
    assert first.is_configuration_locked() is False
    assert second.is_configuration_locked() is False
    assert (
        first._aetheric_frame_configuration
        .shared_framewide_spellbook_configuration
        is False
    )
    print("default posture: per-book configs, sharing flag off")


def test_probe_frame_owned_config_needs_switch_and_publication():
    """FRAME-OWNED SHARING, exact mechanics (spellbook.py:5238/5306/5620,
    aether.py:1194). Turning one-config-per-frame ON takes TWO steps, and
    the flag alone is not enough:

      step 1 - THE SWITCH: the frame's retained posture must carry
               shared_framewide_spellbook_configuration=True. Every
               sharing gate early-outs while it is False:
               _get_configuration_from_aether (:5306),
               _bind_configuration_to_aether (:5620),
               _is_frame_owned_shared_configuration (:5347).
      step 2 - PUBLICATION: some book must bind its rich config to the
               frame. TWO doors do this, whichever runs first:
               configure_aether_frame() (spellbook.py:5910) and
               conjure() itself - SpellbookCreationSystem
               ._prepare_spellbook_for_conjure calls
               _validate_and_freeze_configuration +
               _bind_aetheric_frame_configuration_to_aether +
               _bind_configuration_to_aether whenever the book is not
               already locked (spellbook_creation_system.py:296-300,
               reached from Spellbook.conjure -> :6248 -> :210 -> :278).

    This half of the probe proves step 1 alone does nothing: flag on,
    nobody published through EITHER door (no configure_aether_frame,
    no conjure), so the second book still mints its own config.

    WHY THIS ROW STILL USES THE PRIVATE SEAM, deliberately, after the
    public door landed (2026-08-03): configure_aether_frame() now accepts
    shared_framewide_spellbook_configuration, but it also FREEZES and
    PUBLISHES in the same call. Setting the switch through it would
    perform step 2 as well, and this row exists to prove step 1 ALONE
    does nothing. The seam is the only instrument that can separate them,
    so it is the right instrument here and the wrong one everywhere else.
    Reached through the retained posture the Spellbook holds BY REFERENCE
    (_initialize_aetheric_frame_configuration, spellbook.py:5359-5376).
    See test_probe_frame_owned_config_adoption_via_public_door for the
    both-steps case, which now needs no seam at all."""
    first = Spellbook(aetheric_frame="switch-only-frame")
    first._aetheric_frame_configuration.\
        with_shared_framewide_spellbook_configuration(True)

    second = Spellbook(aetheric_frame="switch-only-frame")
    assert second.get_configuration() is not first.get_configuration()
    assert second.is_configuration_locked() is False
    print("switch without publication: still per-book")


def test_probe_frame_owned_config_adoption_via_public_door():
    """FRAME-OWNED SHARING, both steps, NOW IN ONE PUBLIC CALL
    (2026-08-03 - this row used to need the private posture seam for the
    switch and was named ..._via_seam). The switch travels IN the publish
    call because configure_aether_frame applies posture BEFORE it freezes
    and binds, so the bind that follows in the same call already sees
    shared=True. The rich config must therefore be shaped BEFORE the call.
    That is the shape lesson 35 describes.
    The call freezes its rich config
    (_validate_and_freeze_configuration, :5909) and binds it to the frame
    (:5910 -> aether._bind_configuration, aether.py:1194, first-wins).
    Every book constructed AFTER that adopts the frame-owned object at
    __init__ (_initialize_configuration, spellbook.py:311/5238) and is
    marked LOCKED. Handing a DIFFERENT config object to a later book on
    that frame is refused outright (:5257).

    Note disposal=None here: the auto-minted book config already carries
    disposal/disposal_method_names from load_default_dictionary(), and
    both are idempotent set-once keys (spellbook_configuration.py:148),
    so configure_aether_frame() can only set them on a book built from a
    user-supplied config that left them unset."""
    class Gamma:
        pass

    first = Spellbook(aetheric_frame="probe-shared-frame")
    published = first.get_configuration()
    first.configure_aether_frame(
        system_state=None,
        disposal=None,
        disposal_method_names=None,
        shared_framewide_spellbook_configuration=True,
    )
    assert first.is_configuration_locked() is True

    second = Spellbook(aetheric_frame="probe-shared-frame")
    assert second.get_configuration() is published
    assert second.is_configuration_locked() is True

    with pytest.raises(RuntimeError, match="does not match"):
        Spellbook(
            aetheric_frame="probe-shared-frame",
            configuration=md.SpellbookConfiguration("probe-shared-frame"),
        )

    first.bind(spell=Payload, existence="unique")
    second.bind(spell=Gamma, existence="unique")
    assert first.conjure(name="shared-first").meld(spell=Payload) is not None
    assert second.conjure(name="shared-second").meld(spell=Gamma) is not None
    print("frame-owned adoption pinned: switch + publish -> one config per frame")


def test_probe_frame_posture_is_shared_framewide_by_default():
    """OWNER LAW, source-verified: the AethericFrameConfiguration - the
    narrow frame POSTURE - is shared with EVERY spellbook on the frame BY
    DEFAULT. No flag, no opt-in, no publication step.

    The frame mints exactly ONE posture object at construction
    (aetheric_frame.py:218-224) and hands that same reference to every
    book. Spellbook._initialize_aetheric_frame_configuration
    (spellbook.py:5359-5376) only RETRIEVES it, through
    Aether._get_aetheric_frame_configuration (aether.py:1264-1297 ->
    frame.frame_configuration, aetheric_frame.py:563-573). A Spellbook
    NEVER mints its own posture.

    Consequence: posture set through ONE book IS the posture every book
    on that frame reads - configure_aether_frame() mutates that shared
    object directly (spellbook.py:5884-5889), and so does any reach
    through the retained reference.

    Do NOT confuse this with shared_framewide_spellbook_configuration:
    that flag governs a DIFFERENT object - the rich
    SpellbookConfiguration - and it is False on the minted posture
    (aetheric_frame.py:224). Two objects, two different default answers.
    """
    first = Spellbook(aetheric_frame="shared-posture-frame")
    second = Spellbook(aetheric_frame="shared-posture-frame")

    # ONE posture object for the whole frame - no opt-in required.
    assert (
        first._aetheric_frame_configuration
        is second._aetheric_frame_configuration
    )

    # Reach through one book; every book on the frame sees it. The
    # observable IS the switch this lesson is about - flipping it
    # through book one is how book two would ever adopt a shared rich
    # config. It is refused only after the posture freezes
    # (aetheric_frame_configuration.py:653-656), and the posture freezes
    # on the frame's FIRST conjure - both books here are unconjured.
    assert (
        second._aetheric_frame_configuration
        .shared_framewide_spellbook_configuration is False
    )
    first._aetheric_frame_configuration.\
        with_shared_framewide_spellbook_configuration(True)
    assert (
        second._aetheric_frame_configuration
        .shared_framewide_spellbook_configuration is True
    )

    # ...while the RICH configs stay per-book: still two objects.
    assert first.get_configuration() is not second.get_configuration()
    print("frame posture: one object shared framewide by default")


def test_probe_conjure_alone_publishes_frame_owned_config():
    """PUBLICATION DOOR 2 - conjure() itself. No configure_aether_frame()
    anywhere in this probe: switch on, first book conjures, later book
    adopts. Spellbook.conjure (:6248) -> SpellbookCreationSystem (:210)
    -> _prepare_spellbook_for_conjure (spellbook_creation_system.py:278):

        if not spellbook.is_configuration_locked():
            spellbook._validate_and_freeze_configuration()
            spellbook._bind_aetheric_frame_configuration_to_aether()
            spellbook._bind_configuration_to_aether()

    CORRECTION PROBE: an earlier governance note in this repo claimed
    conjure does NOT publish, from a grep of spellbook.py alone. It was
    wrong - the second caller lives in the creation system. This test is
    the guard so that claim cannot come back."""
    first = Spellbook(aetheric_frame="conjure-publishes")
    first._aetheric_frame_configuration.\
        with_shared_framewide_spellbook_configuration(True)
    policy = first.get_configuration()
    policy.set_property("phase_scheduler_workers_per_spellbook", 1)

    first.bind(spell=Payload, existence="unique")
    first.conjure(name="publisher")
    assert first.is_configuration_locked() is True

    second = Spellbook(aetheric_frame="conjure-publishes")
    assert second.get_configuration() is policy
    assert second.is_configuration_locked() is True
    assert second.get_configuration().get_property(
        "phase_scheduler_workers_per_spellbook"
    ) == 1
    print("conjure published: later book adopted the frame-owned config")


def test_probe_pre_existing_book_converges_at_its_own_conjure():
    """A book that existed BEFORE publication is NOT orphaned. At its own
    conjure, _bind_configuration_to_aether finds the frame-owned config
    already bound, swaps this book onto it, marks it locked, and
    cleanup()s the local config it was carrying
    (spellbook.py:5626-5650)."""
    class Gamma:
        pass

    first = Spellbook(aetheric_frame="converge-frame")
    first._aetheric_frame_configuration.\
        with_shared_framewide_spellbook_configuration(True)

    early = Spellbook(aetheric_frame="converge-frame")
    local = early.get_configuration()
    assert local is not first.get_configuration()

    policy = first.get_configuration()
    first.configure_aether_frame(
        system_state=None,
        disposal=None,
        disposal_method_names=None,
    )
    # Publication does not reach backwards into books already built.
    assert early.get_configuration() is local
    assert early.is_configuration_locked() is False

    early.bind(spell=Gamma, existence="unique")
    early.conjure(name="late-comer")
    assert early.get_configuration() is policy
    assert early.is_configuration_locked() is True
    print("pre-existing book converged onto the shared config at conjure")


def test_probe_switch_is_refused_after_posture_freeze():
    """THE SWITCH HAS A DEADLINE. The frame posture freezes on the
    frame's FIRST conjure: _prepare_spellbook_for_conjure calls
    _bind_aetheric_frame_configuration_to_aether, which routes to
    AethericFrame.bind_frame_configuration and freezes the retained
    posture (aetheric_frame.py:667-726). After that,
    with_shared_framewide_spellbook_configuration refuses
    (aetheric_frame_configuration.py:653-656). Flip the switch BEFORE
    anything on the frame conjures."""
    book = Spellbook(aetheric_frame="freeze-deadline")
    book.bind(spell=Payload, existence="unique")
    book.conjure(name="freezer")

    with pytest.raises(RuntimeError, match="after it is frozen"):
        book._aetheric_frame_configuration.\
            with_shared_framewide_spellbook_configuration(True)
    print("switch refused after posture freeze - flip it before first conjure")


# ---------------------------------------------------------------------------
# Lesson 37 - the frame-owned ConduitCloud
# ---------------------------------------------------------------------------

class _Ledger:
    pass


def test_probe_conduit_cloud_is_frame_owned_and_shared():
    """Lesson 37 HEADLINE: get_conduit_cloud() is a REACH, not a factory.
    melder's contract: "Reaches THROUGH the aetheric frame to the
    frame-owned cloud, so the returned object is SHARED by every conduit
    on the frame."

    Two conduits on one frame must hand back THE SAME OBJECT - identity,
    not equality. If this ever became per-conduit, "what conduits exist
    here?" would stop having one answer.

    NOTE THE IMPORT. `ConduitCloud` came OFF the package root on
    2026-08-04 (owner ruling), so this row reaches it by concrete path -
    which a probe may do and an example may not. The type check is still
    worth pinning; only the way we name the type changed."""
    from melder.aether.aetheric_frame.conduit_cloud import ConduitCloud

    book = Spellbook(aetheric_frame="probe-cloud")
    book.bind(spell=_Ledger, existence="unique")
    root = book.conjure(name="probe-cloud-root")
    peer = Spellbook(aetheric_frame="probe-cloud").conjure(
        name="probe-cloud-peer")

    cloud = root.get_conduit_cloud()
    assert isinstance(cloud, ConduitCloud)
    assert peer.get_conduit_cloud() is cloud
    assert root.get_conduit_cloud() is cloud
    assert cloud.frame_name == "probe-cloud"
    print("frame-owned cloud pinned: one object per frame, shared")


def test_probe_conduit_cloud_is_not_on_the_package_root():
    """Lesson 37's new claim, pinned in the tier that teaches it.

    Owner ruling 2026-08-04: `ConduitCloud` is not a root export. The
    reason is that it was UNUSABLE as one - its constructor requires an
    `AethericFrame` and a `DevopsInformationRegistry`, neither exported
    and neither defaulted, so `md.ConduitCloud(...)` could never be
    called. Its own docstring says "users do not construct one".

    THE REACH IS UNAFFECTED, which is the half that matters and the half
    this row guards: `get_conduit_cloud()` still returns the live object.
    A future re-export would be a decision, not an accident - and this
    row makes it visible either way.

    (The authoritative fence lives in
    tests/unit/melder/test_package_public_surface.py; this row keeps the
    claim honest in the tier whose lesson depends on it.)"""
    import melder

    assert "ConduitCloud" not in melder.__all__
    assert not hasattr(melder, "ConduitCloud")

    book = Spellbook(aetheric_frame="probe-cloud-unexported")
    book.bind(spell=_Ledger, existence="unique", binding_name="unexported")
    cloud = book.conjure(name="unexported-root").get_conduit_cloud()
    assert cloud is not None
    assert cloud.frame_name == "probe-cloud-unexported"
    print("root fence pinned: name is gone, the reach still works")


def test_probe_a_different_frame_gets_a_different_cloud():
    """Lesson 37 claim: frames are worlds (advanced 03) and the cloud is a
    world-level object, so the frame wall holds here too."""
    # binding_name differs because a spell_id does not carry the frame -
    # identical bindings on two frames collide process-wide. The CLOUD is
    # what this row is about, and it IS per-frame.
    first = Spellbook(aetheric_frame="probe-cloud-a")
    first.bind(spell=_Ledger, existence="unique", binding_name="cloud-a")
    second = Spellbook(aetheric_frame="probe-cloud-b")
    second.bind(spell=_Ledger, existence="unique", binding_name="cloud-b")

    cloud_a = first.conjure(name="a-root").get_conduit_cloud()
    cloud_b = second.conjure(name="b-root").get_conduit_cloud()
    assert cloud_a is not cloud_b
    assert cloud_a.frame_name == "probe-cloud-a"
    assert cloud_b.frame_name == "probe-cloud-b"
    print("frame wall pinned: separate worlds, separate clouds")


def test_probe_cloud_reads_agree_and_a_miss_is_none():
    """Lesson 37 claim: counts agree with the lists they count, and
    find_conduit_id_by_name returns Optional rather than raising - a
    lookup that can legitimately miss should not need a try block."""
    book = Spellbook(aetheric_frame="probe-cloud-reads")
    book.bind(spell=_Ledger, existence="unique")
    root = book.conjure(name="reads-root")
    cloud = root.get_conduit_cloud()

    assert cloud.count_conduits() == len(cloud.list_conduit_ids())
    assert cloud.has_conduit_name("reads-root")

    found = cloud.find_conduit_id_by_name("reads-root")
    assert found is not None
    assert cloud.has_conduit_id(found)
    assert cloud.get_conduit_by_id(found) is root
    assert cloud.get_conduit_by_name("reads-root") is root

    assert cloud.find_conduit_id_by_name("nope") is None
    assert cloud.has_conduit_name("nope") is False
    print("cloud reads pinned: count agrees, miss is None not an exception")


# ---------------------------------------------------------------------------
# scan - the module door, and only the module door
# ---------------------------------------------------------------------------

@md.scan_bind(existence=md.Existence.unique, permissions=md.Permissions.create)
class _ProbeTrail:
    pass


@md.scan_bind(existence=md.Existence.many, permissions=md.Permissions.create)
class _ProbeEntry:
    pass


def test_probe_book_scan_binds_a_module_and_keeps_the_lifecycles():
    """The scan API is `book.scan(module)`. It binds every scan_bind-marked
    object that ORIGINATES in that module, and the decorated existence
    survives the scan - unique stays one per frame, many stays fresh per
    meld. (Lesson 01 is the authored version; this row pins it.)

    NOTE: scan returns SPELL IDs (sha256 digests), not class names. The
    first draft of this row asserted names and went red on the owner's
    run. Lesson 01 only ever asserted the COUNT, which is why it stayed
    green - worth knowing before you write against this return value."""
    book = Spellbook(aetheric_frame="probe-scan-module")
    bound = book.scan(sys.modules[__name__])

    assert len(bound) == 2, "two scan_bind-marked classes live in this module"
    assert all(isinstance(spell_id, str) for spell_id in bound)
    assert all(len(spell_id) == 64 for spell_id in bound), "sha256 digests"

    conduit = book.conjure(name="probe-scan-root")
    assert conduit.meld(spell=_ProbeTrail) is conduit.meld(spell=_ProbeTrail)
    assert conduit.meld(spell=_ProbeEntry) is not conduit.meld(spell=_ProbeEntry)
    print("module scan pinned: 2 spell ids, lifecycles intact")
