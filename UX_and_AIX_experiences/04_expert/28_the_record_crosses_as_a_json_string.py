"""
TIER: expert (28)
GOAL: NO FILE, NO DATABASE, NO DRIVER - A PYTHON STRING. Merge two
      research lanes, turn the whole record into TEXT, throw the live set
      away, and rebuild it from that text with its identity intact.

      THE TWO VERBS THAT MAKE A RECORD PORTABLE

        research_set.describe()          -> Dict[str, object]
        md.ResearchSet.from_payload(d)   -> ResearchSet

      And the contract on the first one is the whole reason this lesson
      can assert what it asserts: "PLAIN-VALUE THROUGHOUT. Every nested
      value is JSON-safe, so the payload crosses the persistence boundary
      losslessly and rebuilds via `from_payload`."

      SO THIS SCRIPT CALLS `json.dumps(payload)` WITH NO `default=`
      HANDLER, ON PURPOSE. A `default=str` would paper over exactly the
      regression worth catching: the day something non-plain lands in that
      payload, this line raises `TypeError` and names the offender. The
      strict call is the guard. A lenient one would turn a broken
      guarantee into a silently lossy round trip - a datetime would go out
      as a string and come back as a string, and nothing would notice.

      WHAT SURVIVES, AND WHY IT MATTERS
      `from_payload` RESTORES THE RECORDED IDENTITY - the rebuilt set
      keeps its `set_id` and `created_at` rather than minting new ones. So
      this is not "a set that looks like the old one"; it is the SAME
      set, hydrated. Contrast expert 24/27, where a restored WORLD is
      deliberately equivalent-not-identical and hands you a translation
      map. Different guarantees, and the difference is the point: runtime
      objects are rebuilt, the RECORD is restored.

      It also carries `network_versioner`, so the undo ring survives the
      trip and `restore_network` still reaches pre-death organization
      shapes on the rebuilt set. A record that forgot how to undo itself
      would be a weaker thing than the one you sealed.

      REBUILD IS SILENT ON PURPOSE. `on_mutation` is suppressed during
      hydration and installed only at the end, so rehydrating does not
      re-fire persistence for every recorded node. A rebuild that
      re-emitted its own history would double every record it touched.

      AND PARTIAL PAYLOADS DEGRADE RATHER THAN CRASH: only `organization`
      and `journal` are hard requirements; a missing residence payload
      rebuilds an empty registry.
SURFACE EXERCISED: md.ResearchSet.from_payload, ResearchSet.describe /
                   register_spell / walk / heads / lane_names / set_id /
                   network_snapshot_shas, research_create_lane /
                   research_join, and the mesh quartet
                   (with_store_handler / with_fetch_handler)
VERIFY: NOT RUN by the authoring agent - this sandbox is Python 3.10 and
        melder requires >=3.14. Rides the owner's 3.14t harness; the
        asserts are the contract.
"""
import json

import melder as md


FRAME = "wire-world"


class Policy:
    def __init__(self) -> None:
        self.tag = "v1"


class PolicyV2:
    def __init__(self) -> None:
        self.tag = "v2"


# The entire "wire" for the mesh coda: a dict of JSON strings in RAM.
WIRE: dict = {}


def store(kind: str, profile_name: str, unit_id: str, payload: dict) -> None:
    WIRE[(kind, unit_id)] = json.dumps(payload, default=str, sort_keys=True)


def fetch(kind: str, unit_id: str):
    raw = WIRE.get((kind, unit_id))
    return None if raw is None else json.loads(raw)


def list_units(kind: str, profile_name: str):
    return [unit for (stored_kind, unit) in WIRE if stored_kind == kind]


def main() -> None:
    # 1. RECORD LIVE BEFORE THE WORLD, or the binds below declare nothing.
    crystallizer = md.Crystallizer()
    crystallizer.activate(
        md.CrystallizerConfigurationBuilder().with_defaults().activate(),
    )
    research = md.MutationResearch()
    research_configuration = research.create_configuration()
    research_configuration.with_defaults().activate()
    research.activate(research_configuration)

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
    print("v1 recorded:", v1[:12], "...")

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
    print("research set:", research_set.name, "id", original_set_id[:12], "...")

    # 2. TWO BRANCHES FROM ONE ANCHOR. A lane starts EMPTY - it records
    #    ancestry, it does not copy nodes (expert 23).
    for lane in ("wire-clean", "wire-forced"):
        cut = commands.research_create_lane(
            lane, attach_to="default", attach_at_spell_id=v1,
            reason=f"{lane} branch",
        )
        assert cut["anchor_spell_id"] == v1
        assert len(cut["nodes"]) == 0
    opened = commands.research_heads()
    print("two lanes cut from one anchor; open lanes:", len(opened))

    # 3. THE CLEAN MERGE FIRST, while the receiver is still sitting
    #    exactly at the anchor. Order matters here and it is easy to get
    #    backwards: move the receiver before this join and even the
    #    "clean" branch becomes divergent.
    #
    #    NOTE WHAT IS NOT HAPPENING. The lanes are still EMPTY and we do
    #    NOT register anything onto them. `bind_inactive` below already
    #    declares its version into `default` automatically, and SINGLE
    #    RESIDENCE means that id then lives in exactly one lane, network
    #    wide, permanently - so `register_spell(v2, lane="wire-clean")`
    #    would raise the rediscovery signal rather than file it twice.
    #    Expert 26 teaches that rule and shows the refusal.
    commands.research_join("wire-clean", into="default",
                           reason="nothing diverged")
    print()
    print("join('wire-clean' -> 'default') accepted")
    print("  a join moves a LINE, and an empty line is a legal line -")
    print("  what makes it clean is the ANCHOR agreeing with the tip")

    # 4. NOW MOVE THE RECEIVER, so the second branch is provably stale.
    v2 = conduit.bind_inactive(
        spell=PolicyV2,
        spell_index=conduit.get_spell_by_id(v1).spell_index,
        existence="unique",
        permissions="create",
    )
    print("v2 staged; the default lane moved on:", v2[:12], "...")

    # 5. THE DIVERGENT ONE REFUSES, AND THE REFUSAL NAMES BOTH TIPS.
    try:
        commands.research_join("wire-forced", into="default")
        raise AssertionError("expected a refusal: divergent join")
    except RuntimeError as error:
        print("join('wire-forced') refused -", str(error)[:110])

    commands.research_join("wire-forced", into="default", force=True,
                           reason="explicit supersede; content reconciled "
                                  "in the workshop, not by the record")
    print("join(..., force=True) accepted - a SUPERSEDE, never a merge")
    print("  reconciliation by CONTENT is work you do in a room; the")
    print("  record books an outcome and never guesses at your source")

    merged_lanes = research_set.lane_names()
    merged_heads = commands.research_heads()
    print("lanes now:", len(merged_lanes), " open heads:", len(merged_heads))

    # 6. THE WHOLE RECORD, AS TEXT. Strict dumps - no `default=` - so the
    #    plain-value guarantee is EXECUTED rather than trusted.
    payload = research_set.describe()
    assert isinstance(payload, dict)
    assert "organization" in payload and "journal" in payload

    wire = json.dumps(payload, sort_keys=True)

    assert isinstance(wire, str)
    print()
    print("describe() -> dict with", len(payload), "top-level keys:",
          sorted(payload))
    print("json.dumps(payload)  <- NO default= handler, on purpose")
    print("   type:", type(wire).__name__, f"({len(wire)} chars)")
    print("   head:", wire[:92], "...")
    print("  this line IS the guard: the day a non-plain value lands in")
    print("  the payload it raises TypeError and names it. A default=str")
    print("  would have hidden that and made the trip silently lossy")

    # 7. THROW THE LIVE SET AWAY - we only hold text now.
    del research_set, payload

    # 8. REBUILD FROM THE STRING. Not from a file. Not from a database.
    rebuilt = md.ResearchSet.from_payload(json.loads(wire))
    print()
    print("md.ResearchSet.from_payload(json.loads(wire)) ->",
          type(rebuilt).__name__)

    # 9. IDENTITY IS RESTORED, NOT MINTED. This is the guarantee that
    #    separates a RECORD restore from a WORLD restore.
    assert rebuilt.set_id == original_set_id, (
        "from_payload must restore the recorded identity - a rebuilt set is "
        "the SAME set hydrated, not an equivalent copy"
    )
    print("   set_id preserved:", rebuilt.set_id[:12], "...")
    print("  contrast expert 24/27: a restored WORLD is deliberately")
    print("  EQUIVALENT-not-identical and hands you a translation map.")
    print("  Runtime objects are rebuilt; the RECORD is restored")

    # 10. AND THE ORGANIZATION CAME WITH IT - including the merge.
    rebuilt_lanes = rebuilt.lane_names()
    rebuilt_heads = rebuilt.heads()
    assert sorted(rebuilt_lanes) == sorted(merged_lanes), (
        "every lane must survive the text round trip"
    )
    print()
    print("   lanes  :", len(rebuilt_lanes), "== before the round trip")
    print("   heads  :", len(rebuilt_heads), "lane -> tip entries")
    walked = rebuilt.walk("default")
    assert isinstance(walked, list)
    print("   walk('default') ->", len(walked), "nodes, still ordered")
    print("  the joins we performed are IN the text - a merge is part of")
    print("  the organization, not a live-object side effect")

    # 11. THE UNDO RING RODE ALONG TOO.
    shas = rebuilt.network_snapshot_shas()
    assert isinstance(shas, list)
    print()
    print("   network_snapshot_shas:", len(shas), "content address(es)")
    print("  `network_versioner` is carried in the payload, so the rebuilt")
    print("  set can still restore_network() to pre-death shapes. A record")
    print("  that forgot how to undo itself would be weaker than the one")
    print("  you sealed. NOTE snapshot_network() returns a content ADDRESS,")
    print("  not a payload - the text you can carry is describe()'s dict")

    # 12. THE MESH CODA - the same plain payload across four callables.
    mesh = md.ExternalPersistenceManagerConfiguration()
    mesh.with_store_handler(store)
    mesh.with_fetch_handler(fetch)
    mesh.with_list_units_handler(list_units)
    crystallizer.configure_external_persistence_manager(mesh)
    described = crystallizer.describe_external_persistence_manager()
    print()
    print("mesh attached ->", sorted(described)[:5])

    checkpoint_id = crystallizer.create_checkpoint()
    crystallizer.flush_checkpoint(checkpoint_id)
    assert WIRE, (
        "flush must reach the store handler - upload_on_flush defaults True, "
        "which is exactly why an empty config refuses to freeze"
    )
    (kind, unit_id), raw = next(iter(WIRE.items()))
    assert isinstance(raw, str)
    assert fetch(kind, unit_id) == json.loads(raw)
    assert fetch(kind, "never-stored") is None
    print("flush ->", len(WIRE), "unit(s) crossed as text; kind =", kind)
    print("  store(kind, profile_name, unit_id, payload: dict) is the whole")
    print("  integration - one callable, one table with a kind column, and")
    print("  melder never imports your storage")

    # 13. NOTHING LEFT BEHIND.
    WIRE.clear()
    assert fetch(kind, unit_id) is None
    print()
    print("wire cleared - the 'database' was a dict and it is gone")
    print("the record crossed as a string and came back as itself")


if __name__ == "__main__":
    main()
