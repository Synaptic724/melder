"""
TIER: expert (38)
GOAL: Observe named lesser scopes through Nexus, then restore their recorded structure.
      New conduit IDs need the normal explicit Rift projection refresh. A known
      pooled ID keeps its compiled membership while named reuse replaces its payload.
      Crystallizer records dynamic scope structure and required unnamed ancestry;
      it does not save application instances or their mutable contents.
SURFACE EXERCISED: md.Crystallizer.activate / create_checkpoint / load_checkpoint,
                   md.Spellbook.configure_aether_frame / bind / conjure,
                   md.Nexus.activate / create_rift, md.Rift.create_frame_link /
                   refresh_runtime_projections, capability create_lesser_conduit /
                   get_conduit_by_name, md.Conduit.get_conduit_cloud / cleanup.
VERIFY: Requires a complete successful in-memory checkpoint replay. No exception is
        treated as success. A cold process restart additionally needs flush/reload.
"""

import melder as md


class JobNotebook:
    """Application state created inside each job, deliberately excluded from structural replay."""

    def __init__(self) -> None:
        """Initialize the state that a fresh meld must recreate after restore."""
        self.notes: list[str] = []


def open_observer(name: str) -> md.Rift:
    """Open a capability room on the already-published named-jobs world.

    Contract:
        Nexus configuration must already allow the target frame. The returned Rift
        is caller-owned and must be cleaned before tearing down its observed world.
    Args:
        name: Unique name for this observer.
    Returns:
        md.Rift: Attached observer with the current compiled projection.
    """
    nexus = md.Nexus()
    configuration = nexus.create_rift_configuration().with_space_type("capability")
    rift = nexus.create_rift(configuration=configuration, rift_name=name)
    rift.create_frame_link("named-jobs")
    return rift


def main() -> None:
    """Capture a live named hierarchy, retire it and rebuild fresh structural identities.

    Contract:
        Single-threaded: no scope acquisition/return races with load_checkpoint.
        The recorder remains alive, so this demonstrates in-memory replay; flush
        and reload are required when crossing process teardown instead.
    Returns:
        None.
    """
    recorder = md.Crystallizer()
    recorder.activate(md.CrystallizerConfigurationBuilder().with_defaults().activate())
    nexus = md.Nexus()
    nexus_configuration = nexus.create_configuration()
    nexus_configuration.with_rift_creation_enabled(True)
    nexus_configuration.with_allowed_target_frame_names(["named-jobs"])
    nexus.activate(nexus_configuration)

    configuration = md.SpellbookConfiguration("named-jobs").with_defaults().finalize()
    book = md.Spellbook(aetheric_frame="named-jobs", configuration=configuration)
    book.configure_aether_frame(
        system_state="dynamic", disposal=None, disposal_method_names=None,
        rift_enabled=True, ai_native=True,
    )
    book.bind(spell=JobNotebook, existence="unique_per_conduit", permissions="create")
    root = book.conjure(name="job-owner")
    observer = open_observer("before-restore")
    try:
        commands = observer.space.command_system
        job = commands.create_lesser_conduit(root.id, frame_name="named-jobs", name="job-42")
        observer.refresh_runtime_projections(frame_names=("named-jobs",))
        assert commands.get_conduit_by_name("job-42", frame_name="named-jobs") is job
        print("The capability command creates a named job; explicit refresh admits its new ID.")

        job.cleanup()
        assert "job-42" not in commands.list_conduit_names(frame_name="named-jobs")
        next_job = commands.create_lesser_conduit(root.id, frame_name="named-jobs", name="job-43")
        assert commands.get_conduit_by_name("job-43", frame_name="named-jobs") is next_job
        print("Named reuse updates the existing ID's descriptor without an in-command refresh.")

        support = root.create_lesser_conduit()
        nested = support.create_lesser_conduit(name="nested-job")
        original_id, support_id = nested.id, support.id
        original = nested.meld("JobNotebook")
        original.notes.append("not part of the structural record")
        observer.refresh_runtime_projections(frame_names=("named-jobs",))
        checkpoint = recorder.create_checkpoint()
        print("Checkpoint captured names and unnamed supporting ancestry, not notebook contents.")
    finally:
        observer.cleanup()
        root.permanent_cleanup()

    report = recorder.load_checkpoint(checkpoint)
    assert report["status"] == "complete"
    cloud = md.Aether().get_conduit_cloud("named-jobs")
    restored_root = cloud.get_conduit_by_name("job-owner")
    restored = cloud.get_conduit_by_name("nested-job")
    restored_observer = open_observer("after-restore")
    try:
        assert restored.id != original_id
        assert report["identity_map"][original_id] == restored.id
        assert support_id in report["identity_map"]
        assert not cloud.has_conduit_id(report["identity_map"][support_id])
        assert restored.meld("JobNotebook").notes == []
        assert restored_observer.space.command_system.get_conduit_by_name(
            "nested-job", frame_name="named-jobs",
        ) is restored
        print("Restore rebuilt named scopes with fresh IDs and retained the unnamed ancestor.")
        print("A new meld creates an empty notebook; earlier application data is not restored.")
    finally:
        restored_observer.cleanup()
        restored_root.permanent_cleanup()


if __name__ == "__main__":
    main()
