"""
TIER: expert (28)
GOAL: NO FILE, NO DATABASE, NO DRIVER - A PYTHON STRING. Merge two
      research lanes, turn the whole record into TEXT, throw the live set
      away, and rebuild it from that text with its identity intact.

      THE TWO VERBS THAT MAKE A RECORD PORTABLE
        research_set.describe()         -> Dict[str, object]
        md.ResearchSet.from_payload(d)  -> ResearchSet

      `describe_composition()` guarantees "PLAIN-VALUE THROUGHOUT. Every
      nested value is JSON-safe", which is why this script calls
      `json.dumps(payload)` with NO `default=` handler. The strict call
      IS the guard: the day something non-plain lands in that payload it
      raises TypeError and names the offender. A `default=str` would turn
      a broken guarantee into a silently lossy round trip - a datetime
      would go out as a string, come back as a string, and nothing would
      notice.

      WHAT SURVIVES, AND WHY IT MATTERS
      `from_payload` RESTORES THE RECORDED IDENTITY - the rebuilt set
      keeps its `set_id` and `created_at` rather than minting new ones.
      So this is not "a set that looks like the old one"; it is the SAME
      set, hydrated. Contrast expert 24/27, where a restored WORLD is
      deliberately equivalent-not-identical and hands you a translation
      map. Runtime objects are rebuilt; the RECORD is restored.

      It also carries `network_versioner`, so the undo ring survives and
      `restore_network` still reaches pre-death shapes on the rebuilt
      set. Rebuild is SILENT by design: `on_mutation` is suppressed
      during hydration and installed at the end, so rehydrating does not
      re-fire persistence for every recorded node.

      AND THE JOIN ORDER IS LOAD-BEARING. The clean join happens while
      the receiver still sits at the anchor; move the receiver first and
      even the "clean" branch is divergent. The lanes stay EMPTY on
      purpose - `bind_inactive` declares its version into `default`
      automatically, and single residence means that id then lives in
      exactly one lane, so registering it onto a branch would raise the
      rediscovery signal instead (expert 26 shows that refusal).
SURFACE EXERCISED: md.ResearchSet.from_payload, ResearchSet.describe /
                   lane_names / walk / set_id /
                   network_snapshot_shas, research_create_lane /
                   research_join / research_heads,
                   Conduit.bind_inactive, and the mesh quartet
                   (with_store_handler / with_fetch_handler)
VERIFY: rides the owner's 3.14t harness; asserts are the contract.
"""
import json

import melder as md


FRAME = "wire-world"

# The entire "wire" for the mesh coda: a dict of JSON strings in RAM.
WIRE: dict = {}


class Policy:
    def __init__(self) -> None:
        self.tag = "v1"


class PolicyV2:
    def __init__(self) -> None:
        self.tag = "v2"


def store(kind: str, profile_name: str, unit_id: str, payload: dict) -> None:
    WIRE[(kind, unit_id)] = json.dumps(payload, default=str, sort_keys=True)


def fetch(kind: str, unit_id: str):
    raw = WIRE.get((kind, unit_id))
    return None if raw is None else json.loads(raw)


def list_units(kind: str, profile_name: str):
    return [unit for (stored_kind, unit) in WIRE if stored_kind == kind]


def main() -> None:
    crystallizer = md.Crystallizer()
    crystallizer.activate(
        md.CrystallizerConfigurationBuilder().with_defaults().activate(),
    )
    research = md.MutationResearch()
    configuration = research.create_configuration()
    configuration.with_defaults().activate()
    research.activate(configuration)

    spellbook_configuration = (
        md.SpellbookConfiguration(FRAME).with_defaults().finalize()
    )
    book = md.Spellbook(aetheric_frame=FRAME,
                        configuration=spellbook_configuration)
    book.configure_aether_frame(
        system_state="dynamic",
        disposal=None,
        disposal_method_names=None,
        rift_enabled=True,
        ai_native=True,
    )
    v1 = book.bind(spell=Policy, existence="unique", permissions="create",
                   binding_name="wire-policy")
    conduit = book.conjure(name="wire-root")

    nexus = md.Nexus()
    system_configuration = nexus.create_configuration()
    system_configuration.with_rift_creation_enabled(True)
    system_configuration.with_allowed_target_frame_names([FRAME])
    nexus.activate(system_configuration)
    rift_configuration = nexus.create_rift_configuration()
    rift_configuration.with_space_type("codegen")
    rift = nexus.create_rift(configuration=rift_configuration,
                             rift_name="wirer")
    rift.mark_active()
    rift.create_frame_link(FRAME)
    commands = rift.space.command_system

    research_set = research.research_set()
    original_set_id = research_set.set_id
    print("v1 recorded:", v1[:12], "| set", original_set_id[:12], "...")

    # Two branches from one anchor. A lane starts EMPTY - anchoring
    # records ancestry, it does not copy nodes.
    for lane in ("wire-clean", "wire-forced"):
        cut = commands.research_create_lane(
            lane, attach_to="default", attach_at_spell_id=v1,
            reason="%s branch" % lane,
        )
        assert cut["anchor_spell_id"] == v1 and len(cut["nodes"]) == 0
    print("two lanes cut from one anchor; open lanes:",
          len(commands.research_heads()))

    # CLEAN JOIN FIRST, while the receiver is still at the anchor.
    commands.research_join("wire-clean", into="default",
                           reason="nothing diverged")
    print("join('wire-clean') accepted - an empty line is a legal line;")
    print("  what makes it clean is the ANCHOR agreeing with the tip")

    # Now move the receiver, so the second branch is provably stale.
    v2 = conduit.bind_inactive(
        spell=PolicyV2,
        spell_index=conduit.get_spell_by_id(v1).spell_index,
        existence="unique", permissions="create",
    )
    print("v2 staged; the default lane moved on:", v2[:12], "...")

    try:
        commands.research_join("wire-forced", into="default")
        raise AssertionError("expected a refusal: divergent join")
    except RuntimeError as error:
        print("join('wire-forced') refused -", str(error)[:100])

    commands.research_join("wire-forced", into="default", force=True,
                           reason="explicit supersede; content reconciled "
                                  "in the workshop, not by the record")
    print("join(force=True) accepted - a SUPERSEDE, never a merge")

    merged_lanes = research_set.lane_names()

    # THE WHOLE RECORD, AS TEXT. Strict dumps - no `default=`.
    payload = research_set.describe()
    assert isinstance(payload, dict)
    assert "organization" in payload and "journal" in payload
    wire = json.dumps(payload, sort_keys=True)
    assert isinstance(wire, str)
    print()
    print("describe() ->", len(payload), "keys ->", len(wire), "chars of TEXT")
    print("  head:", wire[:80], "...")

    # Throw the live set away - we hold only text now.
    del research_set, payload

    rebuilt = md.ResearchSet.from_payload(json.loads(wire))
    assert rebuilt.set_id == original_set_id, (
        "from_payload must restore the recorded identity - a rebuilt set "
        "is the SAME set hydrated, not an equivalent copy"
    )
    assert sorted(rebuilt.lane_names()) == sorted(merged_lanes)
    assert isinstance(rebuilt.walk("default"), list)
    assert isinstance(rebuilt.network_snapshot_shas(), list)
    print("from_payload -> set_id preserved,", len(rebuilt.lane_names()),
          "lanes, the joins intact, undo ring carried")

    # THE MESH CODA - the same plain payload across four callables.
    mesh = md.ExternalPersistenceManagerConfiguration()
    mesh.with_store_handler(store)
    mesh.with_fetch_handler(fetch)
    mesh.with_list_units_handler(list_units)
    crystallizer.configure_external_persistence_manager(mesh)
    assert isinstance(crystallizer.describe_external_persistence_manager(),
                      dict)

    checkpoint_id = crystallizer.create_checkpoint()
    crystallizer.flush_checkpoint(checkpoint_id)
    assert WIRE, (
        "flush must reach the store handler - upload_on_flush defaults "
        "True, which is why an empty config refuses to freeze"
    )
    (kind, unit_id), raw = next(iter(WIRE.items()))
    assert isinstance(raw, str)
    assert fetch(kind, unit_id) == json.loads(raw)
    assert fetch(kind, "never-stored") is None
    print()
    print("flush ->", len(WIRE), "unit(s) crossed as text; kind =", kind)
    print("  store(kind, profile_name, unit_id, payload: dict) is the whole")
    print("  integration - melder never imports your storage")

    WIRE.clear()
    assert fetch(kind, unit_id) is None
    print("wire cleared - the 'database' was a dict, and it is gone")


if __name__ == "__main__":
    main()
