"""
TIER: expert (22)
GOAL: FORESIGHT. An agent about to replace a version can ask what the
      replacement WOULD do - what it defines, what it imports, how it
      differs from what is there, what it would break, and whether the
      room would even permit it - and get all of that WITHOUT running,
      binding, or recording anything.

        commands.research_preview(
            candidate_source,
            against_spell_id=existing_spell_id,
            frame_name=FRAME,
        )

      ONE CALL, FIVE ANSWERS
        defines / import_roots   what the candidate declares and pulls
        diff                     would-be source + structural diff
                                 against the version it would REPLACE
        impact                   the blast radius of that replacement,
                                 joined with research residency
        candidate_sha256         the identity it would have
        validation               the room's normal codegen verdict, but
                                 ONLY when frame_name is supplied
      That last one matters: `validate_codegen` answers "am I permitted",
      `research_preview` answers "what would happen", and passing a frame
      folds the first into the second so an agent asks once.

      ORDER OF SETUP IS LOAD-BEARING, IN TWO SEPARATE WAYS

      1. A BIND ONLY AUTO-RECORDS INTO A LIVE RESEARCH ROOT. The seam
         returns quietly when research is absent, cleaned or inactive,
         because "research bookkeeping never gates a bind". So a world
         built before you activate research is a world research never
         saw. Activate first, then build.

      2. AND A RECORDED WORLD MUST BE BORN CONFIGURED. With custody
         active, a DYNAMIC conjure REFUSES outright if any bind ran
         before the SpellbookConfiguration was finalized:

           md.SpellbookConfiguration(FRAME).with_defaults().finalize()
           md.Spellbook(aetheric_frame=FRAME, configuration=...)
           book.bind(...)          # now the binds are config-coherent
           book.conjure(dynamic=True)

         The reason is stated in the refusal itself: the profile record,
         the checkpoints and the default bootstrap would DURABLY PERSIST
         binds that ran against unsettled configuration. A runtime can
         tolerate that; a RECORD cannot, because the record is what a
         future boot rebuilds from. Automatic-mode worlds and worlds
         with no active Crystallizer are exempt, so nothing that is not
         being recorded pays for this.

         Note which lessons this caught: every lesson in this tier that
         activates custody AND conjures dynamic, and none of the others.
         The rule is narrow and it is exactly as narrow as the risk.

      AND FORESIGHT NEEDS CUSTODY. The impact half reaches through the
      Crystallizer for the physical picture (expert 14's record-vs-
      foresight split), so it refuses loudly when custody is not
      recording rather than handing back an empty radius.

      THE PROOF THAT PREVIEW IS READ-ONLY IS IN THIS FILE
      The lesson reads the research heads before and after the preview
      and asserts they are IDENTICAL. "Nothing executes, binds, or
      records" is a claim melder makes about itself; here it is checked.

      A BROKEN CANDIDATE ANSWERS, IT DOES NOT EXPLODE
      Hand it source that does not parse and `parse_error` comes back
      populated with the rest of the payload still shaped the same way.
      An agent generating code gets malformed output sometimes; a
      foresight tool that raised on it would be useless exactly when it
      is needed.
SURFACE EXERCISED: research_preview (defines / import_roots / diff /
                   impact / candidate_sha256 / parse_error),
                   research_impact, research_heads, and the
                   Crystallizer + MutationResearch activation order
VERIFY: rides the owner's 3.14t harness; asserts are the contract.
"""
import melder as md


FRAME = "foresight-world"


class PriceRule:
    """The version an agent is about to propose replacing."""

    def __init__(self) -> None:
        self.rate = 10

    def apply(self, amount: int) -> int:
        return amount * self.rate


# What the agent proposes. Note it DEFINES a class and IMPORTS nothing -
# the preview reports both without running a line of it.
CANDIDATE = (
    "class PriceRule:\n"
    "    def __init__(self):\n"
    "        self.rate = 25\n"
    "\n"
    "    def apply(self, amount):\n"
    "        return amount * self.rate + 1\n"
)

BROKEN = "class PriceRule\n    this is not python\n"


def main() -> None:
    # 1. RECORD AND CUSTODY FIRST. A world built before these are live is
    #    a world neither of them ever saw.
    crystallizer = md.Crystallizer()
    crystallizer.activate(
        md.CrystallizerConfigurationBuilder().with_defaults().activate(),
    )
    research = md.MutationResearch()
    research_configuration = research.create_configuration()
    research_configuration.with_defaults().activate()
    research.activate(research_configuration)
    assert crystallizer.activated and research.activated
    print("custody recording:", crystallizer.activated,
          " research live:", research.activated)

    # 2. NOW build the world. The bind auto-records because research was
    #    already up - had we activated afterwards, nothing would have
    #    been recorded and no foresight would have been possible.
    # A RECORDED WORLD MUST BE BORN CONFIGURED. With custody active, a
    # dynamic conjure REFUSES if any bind ran before the configuration
    # was finalized - the profile record and default bootstrap would
    # otherwise durably persist binds made against unsettled config.
    spellbook_configuration = (
        md.SpellbookConfiguration(FRAME).with_defaults().finalize()
    )
    book = md.Spellbook(aetheric_frame=FRAME,
                        configuration=spellbook_configuration)
    # AND THE FRAME POSTURE GOES BEFORE THE BIND TOO, for a DIFFERENT
    # reason: a plain bind only auto-records `if self._is_dynamic_posture()`,
    # which reads the FRAME configuration and is answerable before conjure.
    # Bind into a not-yet-dynamic frame and the spell is never declared -
    # no residency, no foresight, and no error either, because research
    # bookkeeping never gates a bind.
    book.configure_aether_frame(
        system_state="dynamic",
        disposal=None,
        disposal_method_names=None,
        rift_enabled=True,
        ai_native=True,
    )
    spell_id = book.bind(
        spell=PriceRule, existence="unique", permissions="create",
        binding_name="foresight-rule",
    )
    conduit = book.conjure(name="foresight-root")
    live = conduit.meld(spell=PriceRule, binding_name="foresight-rule")
    assert live.apply(4) == 40
    print()
    print("world up; PriceRule.apply(4) ->", live.apply(4))
    print("spell_id:", spell_id[:12], "...")

    # 3. A codegen room pointed at it.
    nexus = md.Nexus()
    system_configuration = nexus.create_configuration()
    system_configuration.with_rift_creation_enabled(True)
    system_configuration.with_allowed_target_frame_names([FRAME])
    nexus.activate(system_configuration)
    rift_configuration = nexus.create_rift_configuration()
    rift_configuration.with_space_type("codegen")
    rift = nexus.create_rift(configuration=rift_configuration,
                             rift_name="foresight")
    rift.mark_active()
    rift.create_frame_link(FRAME)
    commands = rift.space.command_system

    # 4. WHAT DOES THE EXISTING VERSION TOUCH, RIGHT NOW?
    # `spell_id` is KEYWORD-ONLY here, and so is `module_name` - the verb
    # answers about exactly ONE center per call, so it will not let you
    # pass a bare identifier and leave which-kind-of-center to inference.
    radius = commands.research_impact(spell_id=spell_id)
    print()
    print("research_impact(existing) -> keys:", sorted(radius)[:6], "...")
    print("  the CURRENT blast radius, joined with research residency")

    # 5. THE FORESIGHT CALL. Snapshot the record first so we can prove
    #    the preview did not touch it.
    heads_before = commands.research_heads()

    preview = commands.research_preview(
        CANDIDATE,
        against_spell_id=spell_id,
        frame_name=FRAME,
    )
    for key in ("candidate_sha256", "module_name", "parse_error",
                "defines", "import_roots", "diff", "impact",
                "against_spell_id"):
        assert key in preview, key
    print()
    print("research_preview ->", len(preview), "keys")
    print("   parse_error :", preview["parse_error"])
    print("   defines     :", preview["defines"])
    print("   import_roots:", preview["import_roots"] or "(none)")
    print("   candidate   :", str(preview["candidate_sha256"])[:12], "...")
    print("   against     :", str(preview["against_spell_id"])[:12], "...")
    assert preview["parse_error"] is None
    assert preview["against_spell_id"] == spell_id
    print("  it read the candidate's AST - a class defined, no imports -")
    print("  diffed it against the version it would replace, and priced")
    print("  the replacement, all without running a line")

    # 6. AND THE ROOM'S VERDICT CAME ALONG, because frame_name was given.
    print()
    print("frame_name folded the permission question in:")
    print("  'may I' and 'what would happen' answered in ONE call")

    # 7. THE PROOF. Nothing executed, bound, or recorded.
    heads_after = commands.research_heads()
    assert heads_after == heads_before, (
        "research_preview must not move the record - it is foresight, "
        "not a dry-run that half-commits"
    )
    still = conduit.meld(spell=PriceRule, binding_name="foresight-rule")
    assert still.apply(4) == 40
    print("record heads: IDENTICAL before and after the preview")
    print("live object : still the old rule ->", still.apply(4))
    print("  'nothing executes, binds, or records' - checked, not trusted")

    # 8. A CANDIDATE THAT DOES NOT PARSE STILL ANSWERS.
    broken = commands.research_preview(BROKEN, frame_name=FRAME)
    assert broken["parse_error"] is not None
    print()
    print("a candidate that does not parse ->")
    print("   parse_error:", str(broken["parse_error"])[:60])
    print("  same payload shape, populated honestly. An agent's generator")
    print("  emits garbage sometimes, and a foresight tool that raised on")
    print("  garbage would fail exactly when it is most needed")

    print()
    print("ask what it WOULD do, then decide - and the asking is free")
    print("activate record and custody BEFORE you build, or there is")
    print("nothing to have foresight about")


if __name__ == "__main__":
    main()
