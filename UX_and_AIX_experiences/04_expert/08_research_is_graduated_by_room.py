"""
TIER: expert (08)
GOAL: HOW AN AGENT REACHES MUTATION RESEARCH - and the discovery that
      access to it is GRADUATED BY ROOM KIND, exactly the way the conduit
      surface was in advanced 11.

      MEASURE THE THREE ROOMS AND THE PATTERN IS UNMISSABLE:

        static room       0 research verbs
        capability room  21 research verbs
        codegen room     34 research verbs

      And the split is not arbitrary. Compare the two that have any:

        capability-only verbs:  NONE
        codegen-only verbs:     13

      Codegen is a STRICT SUPERSET. So the question is only: which 13
      does it add? Every one of them is a WRITE.

        SHAPING LANES     research_create_lane, research_attach,
                          research_detach, research_join, research_archive
        CAMPAIGN STATE    research_set_campaign, research_clear_campaign
        ANCESTRY STAGING  research_stage_ancestry,
                          research_clear_staged_ancestry
        COMPOSITION       research_group_register, research_group_recompose
        CANDIDATES        research_preview, research_synthesize

      THE LAW, STATED PLAINLY:
        A CAPABILITY ROOM CAN READ THE ENTIRE RESEARCH RECORD AND CANNOT
        CHANGE ONE THING IN IT. ONLY A CODEGEN ROOM CAN SHAPE HISTORY.

      That is the same shape as advanced 11 one level up. There, static
      could reuse an existing spell but not create one; capability could
      create. Here, capability can read the whole record but not write
      it; codegen can. The library applies one authority idea to two
      different planes, and in both cases it does it BY ABSENCE - the
      verb is not on the class, it is not a guard that refuses.

      WHY THAT PARTICULAR LINE
      Reading history is safe: it cannot mislead anyone else. WRITING
      history is not - a lane you archived, an ancestry you staged, a
      group you recomposed all change what the NEXT reader concludes. So
      the room that may fabricate code is also the only room that may
      restate the past, and both powers arrive together rather than
      separately.

      AND THE PAIR THAT MAKES IT WORTH HAVING
        research_preview      what would this DO?
        validate_codegen      am I PERMITTED to do this?   (lesson 07)
      Two independent "would this work" questions, both answerable
      WITHOUT acting. Most systems make an agent choose between acting
      blindly and not acting at all.
SURFACE EXERCISED: the research_* gradient across static / capability /
                   codegen rooms; read-vs-write as the dividing line
VERIFY: RUN GREEN 2026-08-03 on the owner's 3.14t harness.
"""
import melder as md


# The 13 verbs a codegen room adds - every one writes to the record.
CODEGEN_ONLY = (
    "research_create_lane", "research_attach", "research_detach",
    "research_join", "research_archive",
    "research_set_campaign", "research_clear_campaign",
    "research_stage_ancestry", "research_clear_staged_ancestry",
    "research_group_register", "research_group_recompose",
    "research_preview", "research_synthesize",
)

# A sample of the reads capability already has - proof the line is
# read/write and not "codegen gets research".
SHARED_READS = (
    "research_walk", "research_history", "research_heads",
    "research_residency", "research_diff", "research_impact",
    "research_group_view", "research_group_diff", "research_source_drift",
)


def _room(nexus, kind, name):
    config = nexus.create_rift_configuration()
    config.with_space_type(kind)
    rift = nexus.create_rift(configuration=config, rift_name=name)
    rift.mark_active()
    return rift.space


def _research_verbs(commands) -> set:
    return {name for name in dir(commands) if name.startswith("research_")}


def main() -> None:
    nexus = md.Nexus()
    system_config = nexus.create_configuration()
    system_config.with_rift_creation_enabled(True)
    nexus.activate(system_config)

    static = _room(nexus, "static", "grad-static").command_system
    capability = _room(nexus, "capability", "grad-capability").command_system
    codegen = _room(nexus, "codegen", "grad-codegen").command_system

    static_verbs = _research_verbs(static)
    capability_verbs = _research_verbs(capability)
    codegen_verbs = _research_verbs(codegen)

    print("research verbs by room kind:")
    print("   static     ", len(static_verbs))
    print("   capability ", len(capability_verbs))
    print("   codegen    ", len(codegen_verbs))

    # THE GRADIENT. Not a binary - three tiers.
    assert len(static_verbs) == 0, "a static room cannot ask what changed"
    assert 0 < len(capability_verbs) < len(codegen_verbs)
    print()
    print("a STATIC room cannot ask what changed at all")

    # STRICT SUPERSET. Capability has nothing codegen lacks.
    assert capability_verbs < codegen_verbs, "codegen must be a superset"
    only_capability = capability_verbs - codegen_verbs
    assert not only_capability, f"capability-only verbs: {only_capability}"
    print("codegen is a STRICT SUPERSET - capability has nothing it lacks")

    # AND THE 13 IT ADDS ARE ALL WRITES.
    added = codegen_verbs - capability_verbs
    print()
    print("codegen adds", len(added), "verbs, and every one WRITES:")
    for verb in sorted(added):
        print("   ", verb)
    for verb in CODEGEN_ONLY:
        assert verb in added, f"{verb} was expected to be codegen-only"
        assert not hasattr(capability, verb), (
            f"capability gained {verb} - the read/write line moved"
        )

    # THE READS ARE SHARED. This is what proves the line is read-vs-write
    # rather than "codegen gets research".
    print()
    print("capability already has every read, including:")
    for verb in SHARED_READS:
        assert hasattr(capability, verb), verb
        assert hasattr(codegen, verb), verb
        print("   ", verb)

    # AUTHORITY BY ABSENCE, one plane up from advanced 11.
    assert not hasattr(static, "research_walk")
    assert not hasattr(capability, "research_create_lane")
    print()
    print("absence again - not a guard that refuses, a verb that is not there")

    # THE PAIR. Permission and consequence, both without acting.
    assert hasattr(codegen, "research_preview")
    assert hasattr(codegen, "validate_codegen")
    print()
    print("validate_codegen  -> am I PERMITTED?")
    print("research_preview  -> what would it DO?")
    print("both answerable without acting. that is the whole AIX story.")

    print()
    print("capability READS the record; only codegen may WRITE it")
    print("the room that may fabricate code is the room that may restate the past")


if __name__ == "__main__":
    main()
