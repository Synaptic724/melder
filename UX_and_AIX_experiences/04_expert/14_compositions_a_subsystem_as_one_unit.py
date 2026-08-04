"""
TIER: expert (14)
GOAL: COMPOSITIONS - naming a SET of spells as one thing, and then
      asking questions about the thing instead of about its members.

      Expert 03 taught residency: a spell lives in exactly one lane.
      That answers "where is this one". It does not answer "what is our
      billing subsystem", because a subsystem is not a spell - it is a
      SET of them that someone decided to treat as a unit.

      THE EIGHT VERBS, AND TWO DIFFERENT SPLITS RUN THROUGH THEM

      SPLIT ONE - BY AUTHORITY (which room may call it)

        ORGANIZE (codegen rooms only - these WRITE)
          research_group_register(member_spell_ids, lane=..., reason=...)
          research_group_recompose(previous_group_id, add=..., remove=...)

        READ (capability rooms get these too)
          research_group_view(group_id)
          research_group_diff(left, right, strategy=...)
          research_group_impact(group_id)
          research_group_footprint(group_id)
          research_group_drift(group_id)
          research_group_history(group_id, campaign=...)

      Six reads, two writes. That is expert 08's law one grain up: a
      capability room can read the ENTIRE composition record and cannot
      change one thing in it. Only a codegen room may restate what a
      subsystem IS - because restating it changes what the next reader
      concludes about work nobody has redone.

      SPLIT TWO - BY DEPENDENCY (what the read has to reach)
      The six reads are NOT the same kind of question, and finding this
      out the hard way is the reason this lesson exists in its current
      form. Three answer from the RESEARCH RECORD alone:

          view        the roster and its lane joins
          history     the journal story
          diff        two rosters, plus lane-evidenced version moves

      Three are FORESIGHT reads that join research truth to CUSTODY
      material, and they reach through the Crystallizer to do it:

          footprint   the physical module shadow
          impact      the union blast radius and closure math
          drift       recorded-vs-disk, narrowed to the footprint

      A FORESIGHT READ WITH NO LIVE CRYSTALLIZER REFUSES. It does not
      return an empty report, and melder says why in the message:
      "foresight reads need the record - activate the crystallizer
      before asking for source, impact, or module graphs." Never-
      substitute, on a read path.

      AND THE TWO ABSENCES ARE DIFFERENT, WHICH IS THE SUBTLE PART
        instrument OFF   -> refusal      (no crystallizer: cannot answer)
        instrument ON,
        nothing to read  -> data         (members with no custody crystal
                                          come back under
                                          `unknown_custody_members`)
      "I cannot answer" and "the answer is none" are not the same fact,
      and melder refuses to spell them the same way.

      THE ID IS THE MEMBERSHIP, NOT A SERIAL NUMBER
      `group_id` is a sha256 over the SORTED, DEDUPED member list. Three
      consequences follow, and none of them are cosmetic:

        - A composition is a SET. Input order and duplicates cannot
          change its identity, because they are canonicalised away
          before the hash.
        - THE SAME ROSTER IS THE SAME COMPOSITION. Not a copy of it -
          it. So re-declaring an unchanged set REFUSES as a rediscovery
          and the error names the lane already holding it. You cannot
          accidentally end up with two names for one subsystem.
        - A recompose that resolves back to the previous roster refuses
          for exactly the same reason. Remove-then-re-add is a no-op, and
          melder will not record a no-op as history.

      RECOMPOSE SUCCEEDS THE OLD ONE, IT NEVER EDITS IT
      A new node is registered with `parent_group_ids=[previous]`, in the
      SAME lane, and the previous composition is untouched. Forward-only:
      the old answer stays exactly as true as it was, and the timeline is
      walkable instead of lossy.

      WHAT COMES BACK IS A PAYLOAD, NOT A NODE
      Both writes return `node.describe()` - a plain dict carrying
      `node_type`, `group_id`, `member_spell_ids`, `parent_group_ids`,
      `author`, `reason`, `campaign`, `created_at`, `metadata`. Detached
      and plain-value, so holding one cannot mutate the record.

      AND THE JOIN THAT MAKES IT USEFUL
        research_group_history(group_id, campaign=...)
      History is WHEN. Campaign is WHY. Passing both is the WHERE-by-WHEN
      join - "how did this subsystem change during that effort" - which
      is the question you actually have during a review, and the one you
      cannot ask if a set is only ever a list you kept in your head.

      IMPACT IS LIFTED TOO. `research_impact` on a single spell names the
      GroupedResearchNode subsystems it touches under
      `affected_compositions`. Blast radius stopped being a list of files
      and became a list of things with names.
SURFACE EXERCISED: the eight research_group_* commands across a codegen
                   room and a capability room, the read/write line
                   between them, and the record/foresight line inside the
                   reads
VERIFY: RUN GREEN 2026-08-03 on the owner's 3.14t harness.
"""
import melder as md


WRITES = ("research_group_register", "research_group_recompose")
# Answered from the research record alone.
RECORD_READS = (
    "research_group_view", "research_group_history", "research_group_diff",
)
# Joined against custody material - these need a live Crystallizer.
FORESIGHT_READS = (
    "research_group_footprint", "research_group_impact",
    "research_group_drift",
)
READS = RECORD_READS + FORESIGHT_READS


def _room(nexus, kind, name):
    """Open one rift of the given kind and hand back its command surface."""
    configuration = nexus.create_rift_configuration()
    configuration.with_space_type(kind)
    rift = nexus.create_rift(configuration=configuration, rift_name=name)
    rift.mark_active()
    return rift.space.command_system


def main() -> None:
    nexus = md.Nexus()
    system_configuration = nexus.create_configuration()
    system_configuration.with_rift_creation_enabled(True)
    nexus.activate(system_configuration)

    # The research family reaches the Aether-hosted root through a
    # NON-CONSTRUCTING peek, so it must be live before any of this answers.
    research = md.MutationResearch()
    research_configuration = research.create_configuration()
    research_configuration.with_defaults().activate()
    research.activate(research_configuration)
    print("research root live -", research.activated)

    codegen = _room(nexus, "codegen", "composer")
    capability = _room(nexus, "capability", "reviewer")

    # THE SPLIT, MEASURED. Six reads in both rooms; two writes in one.
    print()
    print("composition surface by room kind:")
    for verb in READS:
        assert hasattr(codegen, verb), verb
        assert hasattr(capability, verb), verb
    print(f"   reads   codegen {len(READS)}   capability {len(READS)}")
    for verb in WRITES:
        assert hasattr(codegen, verb), verb
        assert not hasattr(capability, verb), (
            f"capability gained {verb} - the read/write line moved"
        )
    print(f"   writes  codegen {len(WRITES)}   capability 0")
    print()
    print("a capability room reads the WHOLE record and changes nothing")

    # DECLARE A SUBSYSTEM. Members must already be resident - a composition
    # PINS declared versions, it does not introduce them.
    research_set = research.research_set()
    invoices = "a" * 64
    payments = "b" * 64
    research_set.register_spell(invoices)
    research_set.register_spell(payments)
    research_set.create_lane("billing", lane_type="production")

    payload = codegen.research_group_register(
        [invoices, payments], lane="billing", reason="billing subsystem",
    )
    # WHAT CAME BACK IS A describe() PAYLOAD - a detached plain dict, not
    # the node. Holding it cannot reach in and change the record.
    assert payload["node_type"] == "group"
    group_id = payload["group_id"]
    assert payload["member_spell_ids"] == sorted([invoices, payments])
    assert payload["parent_group_ids"] == []
    print()
    print("registered a composition ->", group_id[:12], "...")
    print("   members come back SORTED - a composition is a SET")

    # THE ID IS THE MEMBERSHIP. Declaring the same roster again is not a
    # second subsystem, it is the SAME one - so it refuses and says where
    # the original lives.
    try:
        codegen.research_group_register(
            [payments, invoices], lane="billing", reason="same set, again",
        )
        raise AssertionError("expected a rediscovery refusal")
    except RuntimeError as error:
        print()
        print("re-declaring the same roster refused -", error)
        print("   order reversed, identity identical: it hashes the SET")

    # RECOMPOSE SUCCEEDS THE OLD ONE. New id, previous recorded as parent,
    # same lane - and the old composition still resolves untouched.
    refunds = "c" * 64
    research_set.register_spell(refunds)
    second = codegen.research_group_recompose(
        group_id, add=[refunds], reason="refunds joined billing",
    )
    second_id = second["group_id"]
    assert second_id != group_id, (
        "a recompose must mint a NEW id - overwriting would destroy the "
        "old answer, and the old answer was never wrong"
    )
    assert second["parent_group_ids"] == [group_id], (
        "the new composition must record what it evolved FROM"
    )
    assert len(second["member_spell_ids"]) == 3
    print()
    print("recomposed -> new id, parent =", group_id[:12], "...")
    assert codegen.research_group_view(group_id) is not None
    print("   the previous composition still resolves, still true")

    # A RECOMPOSE THAT CHANGES NOTHING IS NOT HISTORY. Remove a member and
    # add it straight back and you are describing the roster you already
    # have - same content, same identity, nothing to record.
    try:
        codegen.research_group_recompose(
            second_id, add=[refunds], remove=[refunds], reason="no-op",
        )
        raise AssertionError("expected a refusal: unchanged roster")
    except RuntimeError as error:
        print()
        print("a no-op recompose refused -", type(error).__name__)
        print("   melder will not write 'nothing happened' into a timeline")

    # COMPOSITIONS DO NOT NEST. A group id is a real identity in the same
    # sha namespace, but it names no code - so it cannot be a member.
    try:
        codegen.research_group_register(
            [second_id, invoices], lane="billing", reason="nesting",
        )
        raise AssertionError("expected a refusal: composition as member")
    except ValueError as error:
        print("a composition cannot be a member of a composition -")
        print("  ", error)

    # THE RECORD READS, FROM THE ROOM THAT CANNOT WRITE. These need
    # nothing but the research record, so they answer right now.
    print()
    print("capability room, RECORD reads (research record only):")
    print("   view    ->",
          type(capability.research_group_view(second_id)).__name__)
    print("   history ->",
          type(capability.research_group_history(second_id)).__name__)
    print("   diff    ->",
          type(capability.research_group_diff(group_id, second_id)).__name__)

    # THE FORESIGHT READS REFUSE UNTIL CUSTODY IS RECORDING. The
    # crystallizer exists - Aether built it - but existing is not being
    # live, and melder will not answer a physical question from an
    # instrument that is switched off.
    print()
    print("capability room, FORESIGHT reads with custody not recording:")
    for verb in FORESIGHT_READS:
        try:
            getattr(capability, verb)(second_id)
            raise AssertionError(f"{verb} must refuse without custody")
        except RuntimeError as error:
            assert "crystallizer" in str(error).lower()
            print(f"   {verb.split('_')[-1]:<9} -> refused")
    print("   'cannot answer' is not 'the answer is none' - so it raises")
    print("   instead of handing back an empty report")

    # SWITCH THE INSTRUMENT ON. Same ladder as everywhere else: the
    # configuration activates first, then the subsystem.
    crystallizer = md.Crystallizer()
    crystallizer.activate(
        md.CrystallizerConfigurationBuilder().with_defaults().activate(),
    )
    assert crystallizer.activated is True
    print()
    print("crystallizer activated - custody is recording now")

    print()
    print("capability room, the SAME three foresight reads:")
    for verb in FORESIGHT_READS:
        answer = getattr(capability, verb)(second_id)
        print(f"   {verb.split('_')[-1]:<9} ->", type(answer).__name__)

    # AND NOW THE OTHER KIND OF ABSENCE. These members were declared by
    # id and never bound, so no custody crystal exists for any of them.
    # That is DATA, and the footprint names them rather than pretending.
    footprint = capability.research_group_footprint(second_id)
    assert set(footprint["unknown_custody_members"]) == set(
        second["member_spell_ids"]
    ), "every member was declared by id and never bound, so all are unknown"
    print()
    print("footprint reports", len(footprint["unknown_custody_members"]),
          "members with no custody crystal, BY NAME")
    print("   instrument off -> refusal.  nothing to read -> data.")
    print("   two different absences, spelled two different ways")

    print()
    print("a subsystem is a SET someone named, not a folder")
    print("the id IS the membership - so the same roster is the same thing")
    print("recompose succeeds the old answer instead of erasing it")
    print("only the room that may write code may restate what a thing IS")


if __name__ == "__main__":
    main()
