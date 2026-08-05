"""
TIER: expert (33)
GOAL: WHAT A SYNTHETIC MODULE ACTUALLY IS, and why one crystal shape holds
      both it and a file on your disk. Lessons 26, 27, 29, 30 and 32 all
      MAKE synthetic modules. None of them says what one IS. This does.

      A SYNTHETIC MODULE IS A REAL MODULE WITH NO FILE. It is a live
      `ModuleType` subclass the crystallizer owns: it carries its own
      source text and hash, registers with a class-level import registry
      behind a meta-path finder, and answers plain `import name` like
      anything else. Its source IS the record - there is no file to go
      read, so there is nothing to go stale.

      FOUR STATES, NONE INFERRED FROM ANOTHER: registration, import-hook
      install, publication into `sys.modules`, and source execution.
      `materialize_codegen` is the convenience path that composes all
      four. And it PUBLISHES BEFORE IT EXECUTES, deliberately - that is
      how importlib treats real modules, so a circular import sees a
      partially-initialised module instead of a missing one.

      CUSTODY IS HOW THE CRYSTALLIZER DECIDES WHAT A MODULE *IS*.
      Bind walks your object's dependencies and classifies every module it
      meets through FOUR authority classes, taking the FIRST that matches:

        synthetic_module  claims by OBJECT IDENTITY (isinstance), never
                          path - because a path rule would misclassify it.
                          Reads no disk. Makes NO fingerprint claim; its
                          rebuild payload already carries source_sha256.
        user_source       claims by path under the configured user roots.
                          THE ONLY FINGERPRINT CUSTODIAN - a bind-time
                          SHA256 over your source. This is the trust
                          boundary, and it is the whole reason drift is
                          detectable at all.
        site_package      installed distributions. Descends and reads, but
                          claims NOTHING - you did not write it, so its
                          changing is not your bug.
        unknown           the fallback: pathless, unresolvable, binary.
                          THE ONLY CLASS THAT DOES NOT DESCEND. Recorded as
                          an honest leaf so the manifest never implies a
                          more complete picture than the source supports.

      SO THE ANSWER TO "CAN THIS DRIFT" IS DECIDED BY CUSTODY, NOT BY
      CHANCE. Only user source is fingerprinted, so only user source can
      be caught changing under you. A synthetic module cannot drift - not
      because drift is unchecked but because its text is the record.

      AND BIND FORMATS BOTH INTO ONE CRYSTAL. There is no synthetic
      crystal and no file crystal. One flat module inventory, plus four
      kind-partitions that are subsets of it, plus `root_module_kind`
      naming which lane the root took. The KIND is DATA IN the crystal,
      not a different crystal - which is exactly why a world can mix
      generated and hand-written code and still checkpoint as one thing.

      A NOTE ON WHAT THIS LESSON POINTS AT. `SyntheticModule`, the custody
      strategies and `SpellCrystal` are all AGENT_ACCESS: internal - "read
      it to understand the runtime, do not drive it directly". They are
      NAMED here because you cannot reason about your own world without
      knowing they exist. Every line below drives the PUBLIC surface only.
SURFACE EXERCISED: validate_codegen / materialize_codegen /
                   research_source / research_module /
                   research_source_drift
VERIFY: rides the owner's 3.14t harness; asserts are the contract.
"""
import importlib

import melder as md


FRAME = "custody-world"
SYNTHETIC_MODULE = "custody_generated_unit"

GENERATED_SOURCE = '''"""A module with no file. Its source IS the record."""


class Unit:
    def __init__(self) -> None:
        self.origin = "synthetic"

    def describe(self) -> str:
        return "unit:" + self.origin
'''


class DiskUnit:
    """Declared in THIS file, so its root module is file-backed."""

    def __init__(self) -> None:
        self.origin = "disk"


def _row(label: str, row: object) -> None:
    if isinstance(row, dict):
        print("  %-18s kind=%-11s origin=%-10s drifted=%-5s unavailable=%s"
              % (label, row.get("kind"), row.get("origin"),
                 row.get("drifted"), row.get("text_unavailable")))
    else:
        print("  %-18s -> %s" % (label, type(row).__name__))


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

    # AN EMPTY FRAME IS A REAL FRAME. `configure_aether_frame` declares the
    # frame's LAW; `conjure` REALIZES it by giving it a root conduit, and
    # that realization is what publishes it to the Nexus. Publication is
    # gated on `rift_enabled` ALONE - the spell loop it runs iterates
    # whatever the book holds, including nothing. So the frame below is
    # conjured EMPTY and is immediately linkable; spells are cargo, not a
    # precondition, and everything bound after this arrives incrementally.
    book.conjure(name="custody-root")

    nexus = md.Nexus()
    system_configuration = nexus.create_configuration()
    system_configuration.with_rift_creation_enabled(True)
    system_configuration.with_allowed_target_frame_names([FRAME])
    nexus.activate(system_configuration)
    rift_configuration = nexus.create_rift_configuration()
    rift_configuration.with_space_type("codegen")
    rift = nexus.create_rift(configuration=rift_configuration,
                             rift_name="custody")
    rift.mark_active()
    rift.create_frame_link(FRAME)
    commands = rift.space.command_system

    # ONE MODULE WITH NO FILE. materialize composes all four states:
    # register -> hook -> publish -> execute.
    commands.validate_codegen(GENERATED_SOURCE, frame_name=FRAME)
    kept = commands.materialize_codegen(
        GENERATED_SOURCE, module_name=SYNTHETIC_MODULE, frame_name=FRAME,
    )
    assert kept["materialized"] is True, kept
    print("materialized:", SYNTHETIC_MODULE)
    print("  it has no file, and `import` still resolves it - the import")
    print("  hook is installed and the module is registered")

    generated = importlib.import_module(SYNTHETIC_MODULE)
    assert generated.Unit().describe() == "unit:synthetic"
    print("  imported and executed: Unit().describe() ->",
          generated.Unit().describe())

    # TWO BINDS, TWO AUTHORITY CLASSES, ONE VERB - both landing in a frame
    # that was already live and empty before either existed.
    synthetic_spell = book.bind(spell=generated.Unit, existence="unique",
                                permissions="create",
                                binding_name="custody-synthetic")
    disk_spell = book.bind(spell=DiskUnit, existence="unique",
                           permissions="create", binding_name="custody-disk")
    print()
    print("bound BOTH with the same verb:")
    print("  synthetic root:", synthetic_spell[:12])
    print("  file-backed   :", disk_spell[:12])

    # THE SAME PUBLIC READ ANSWERS FOR BOTH - and labels the difference.
    print()
    print("research_source - same read, same shape, different KIND:")
    synthetic_view = commands.research_source(synthetic_spell)
    disk_view = commands.research_source(disk_spell)
    for label, view in (("synthetic", synthetic_view), ("file", disk_view)):
        assert isinstance(view, dict), view
        root = str(view["root_module"])
        row = view["modules"][root]
        assert set(row) >= {"source", "origin", "kind", "drifted",
                            "text_unavailable"}, sorted(row)
        _row(label + " root", row)

    synthetic_root = str(synthetic_view["root_module"])
    synthetic_row = synthetic_view["modules"][synthetic_root]
    disk_root = str(disk_view["root_module"])
    disk_row = disk_view["modules"][disk_root]

    # THE SYNTHETIC LANE IS THE RELIABLE ONE, not the exotic one:
    # synthetic sources are ALWAYS harvested; user text is opt-in.
    assert synthetic_row["kind"] == "synthetic", synthetic_row
    assert synthetic_row["origin"] == "recorded"
    assert synthetic_row["text_unavailable"] is False
    print("  the synthetic row is ALWAYS harvested - no opt-in, no file,")
    print("  no way for it to be missing")

    # A RECORDED ROW REPORTS drifted=None, AND THAT IS NOT IGNORANCE.
    # There is no second copy to disagree with: the text IS the record.
    assert synthetic_row["drifted"] is None
    print("  drifted=None on a recorded row means there is NOTHING TO")
    print("  DISAGREE WITH - the text is the record, not a copy of it")

    # THE FILE-BACKED ROW TOOK ONE OF TWO LANES, and both are honest.
    assert disk_row["kind"] in ("user", "live_disk"), disk_row
    if disk_row["kind"] == "user":
        print("  the file row was RETAINED (opt-in retention lane is on)")
    else:
        print("  the file row was read LIVE from disk through the recorded")
        print("  path - and only THIS lane can compute drift, because only")
        print("  user source carries a bind-time SHA256 to compare against")

    # THE DOSSIER READ. One call instead of hand-joining five.
    print()
    print("research_module - the one-call dossier for a single module:")
    dossier = commands.research_module(synthetic_spell, synthetic_root)
    assert isinstance(dossier, dict)
    print("  keys:", sorted(dossier)[:8])
    print("  source labeled synthetic/user/live_disk, plus fingerprint,")
    print("  path, dependencies both ways, importers, exports and drift")

    # THE WORLD-LEVEL DRIFT REPORT ONLY SEES WHAT WAS SEALED.
    print()
    drift = commands.research_source_drift()
    assert isinstance(drift, dict)
    print("research_source_drift ->", sorted(drift)[:5])
    print("  it reports per SEALED module - and sealing is a FINGERPRINT")
    print("  claim, which only user source makes. A synthetic module is")
    print("  absent from drift not because it was skipped but because the")
    print("  question does not apply to it")

    print()
    print("ONE CRYSTAL HOLDS BOTH. There is no synthetic crystal and no")
    print("file crystal - one flat module inventory, four kind-partitions")
    print("over it, and root_module_kind naming the lane the root took.")
    print("The kind is DATA IN the crystal, which is why a world can mix")
    print("generated and hand-written code and checkpoint as one thing.")


if __name__ == "__main__":
    main()
