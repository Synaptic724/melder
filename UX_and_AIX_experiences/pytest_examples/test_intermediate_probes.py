"""
Intermediate-tier contract probes. Run on 3.14t:

    pytest UX_and_AIX_experiences/pytest_examples/test_intermediate_probes.py -v

Probes print ground truth for lessons not yet authored - the crystallizer
acquisition path and the dynamic config-before-bind law (whose error text
we captured verbatim from a live traceback this session).
"""
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
    book = Spellbook()
    config = book.get_configuration()
    config.set_property("disposal", True)
    config.set_property("disposal_method_names", ["close"])
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
    config = md.SpellbookConfiguration()
    config.with_defaults()
    config.set_property("disposal", True)
    config.set_property("disposal_method_names", ["close"])
    config.set_property("phase_scheduler_workers_per_spellbook", 1)

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
      step 2 - PUBLICATION: some book must call configure_aether_frame(),
               the ONLY caller of _bind_configuration_to_aether
               (spellbook.py:5909-5910). conjure() does NOT publish.

    This half of the probe proves step 1 alone does nothing: flag on,
    nobody published, so the second book still mints its own config.

    FINDING: neither step has a public door for the switch itself - the
    only setters are the AethericFrameConfiguration constructor kwarg
    (:118) and with_shared_framewide_spellbook_configuration() (:607),
    and configure_aether_frame() never touches it. Pinned here through
    the retained posture the Spellbook holds BY REFERENCE
    (_initialize_aetheric_frame_configuration, spellbook.py:5359-5376)."""
    first = Spellbook(aetheric_frame="switch-only-frame")
    first._aetheric_frame_configuration.\
        with_shared_framewide_spellbook_configuration(True)

    second = Spellbook(aetheric_frame="switch-only-frame")
    assert second.get_configuration() is not first.get_configuration()
    assert second.is_configuration_locked() is False
    print("switch without publication: still per-book")


def test_probe_frame_owned_config_adoption_via_seam():
    """FRAME-OWNED SHARING, both steps (the shape lesson 35 describes).
    Switch on, then the first book PUBLISHES through
    configure_aether_frame() - which freezes its rich config
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
    first._aetheric_frame_configuration.\
        with_shared_framewide_spellbook_configuration(True)
    published = first.get_configuration()
    first.configure_aether_frame(
        system_state=None,
        disposal=None,
        disposal_method_names=None,
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
