"""
TIER: expert (37)
GOAL: Gate agent-supplied existing objects with ordered pre-bind checks,
      verify agent metadata and annotate the new Spell during activation,
      then update and audit the published Spell in post-bind. Demonstrate
      rejection phases and why a post-bind failure does not undo registration.
SURFACE EXERCISED: md.Spellbook / find_spell_by_id / describe_spells_in_spellbook,
                  md.Conduit.add_bind_hooks / clear_bind_hooks / bind / meld,
                  md.Spell.metadata / tags, md.HookExecutionError
"""
import melder as md


class ReportTool:
    """Application-created tool that an agent proposes for registration.

    Contract:
        Carries its schema version as ordinary instance state. It owns no
        external resources; Melder must resolve the exact supplied reference.
    """

    def __init__(self, schema_version: int = 1) -> None:
        """Retain the supplied application schema version without registration work."""
        self.schema_version = schema_version

    def render(self, subject: str) -> str:
        """Render a deterministic result using the already-existing object."""
        return f"report:{subject}"


class BackupReport(ReportTool):
    """Distinct registration used to demonstrate failure after publication."""


class BindingReview:
    """Application policy and local audit for one Book's agent submissions.

    Contract:
        Borrows the Book and owns a list of published IDs. Pre checks run in
        declared order. Metadata updates annotate a Spell; they do not change
        its ID, replace its implementation or automatically refresh persistence.
        This small audit is used sequentially in the example.
    """

    def __init__(self, book: md.Spellbook) -> None:
        """Borrow the target Book and initialize this review's independent audit."""
        self.book = book
        self.published_ids: list[str] = []

    def require_report_tool(self, reference: object) -> None:
        """Reject references outside this application's supported existing-object type."""
        if not isinstance(reference, ReportTool):
            raise TypeError("Agent submissions must be existing ReportTool objects.")

    def require_supported_schema(self, reference: ReportTool) -> None:
        """Check instance state after the preceding callback has validated its type."""
        if reference.schema_version != 1:
            raise ValueError("ReportTool schema_version must be 1.")

    def configure_spell(self, spell: md.Spell) -> None:
        """Check bind metadata and decorate the actual unpublished Spell.

        Contract:
            Pre-bind receives only the reference. The submitted_by bind keyword
            is available here, on the newly constructed Spell's metadata.
        """
        if spell.metadata.get("submitted_by") != "report-agent":
            raise PermissionError("This Book accepts submissions from report-agent only.")
        assert self.book.find_spell_by_id(spell.spell_id) is None
        spell.metadata["review_policy"] = "report-schema-v1"
        spell.tags.append("agent-reviewed")

    def record_registration(self, spell: md.Spell) -> None:
        """Update and audit the same Spell after it becomes publicly discoverable.

        Contract:
            The post_checked annotation is live metadata. Post is not a
            transaction-commit or durable-record refresh callback.
        """
        assert self.book.find_spell_by_id(spell.spell_id) is spell
        assert spell.metadata["review_policy"] == "report-schema-v1"
        spell.metadata["post_checked"] = True
        self.published_ids.append(spell.spell_id)


def unavailable_audit_sink(spell: md.Spell) -> None:
    """Simulate an application notification failure after the earlier post callback."""
    raise RuntimeError(f"Audit sink unavailable for {spell.spell_name}.")


def main() -> None:
    """Bind accepted agent proposals and assert the precise refusal boundaries.

    Contract:
        Uses ordinary public binding against a live normal Conduit. The
        proposal references stand for objects supplied by an agent workflow;
        acquiring or generating those references is a separate concern.
    """
    book = md.Spellbook(configuration=md.SpellbookConfiguration().with_defaults())
    conduit = None
    try:
        conduit = book.conjure(dynamic=True, name="agent-bind-review")
        review = BindingReview(book)
        conduit.add_bind_hooks(
            pre=[review.require_report_tool, review.require_supported_schema],
            activation=[review.configure_spell],
            post=[review.record_registration],
        )

        # A reference check rejects by raising, not by returning False.
        for proposal, cause in ((object(), TypeError), (ReportTool(2), ValueError)):
            try:
                conduit.bind(spell=proposal, existence="unique", submitted_by="report-agent")
            except md.HookExecutionError as error:
                assert error.phase == "pre_bind"
                assert isinstance(error.original_exception, cause)
                print("reference refused:", error.phase, str(error.original_exception))
            else:
                raise AssertionError("The unsuitable proposal was registered.")
        assert book.describe_spells_in_spellbook() == []
        assert review.published_ids == []

        supplied = ReportTool()
        try:
            conduit.bind(spell=supplied, existence="unique", submitted_by="unknown-agent")
        except md.HookExecutionError as error:
            assert error.phase == "bind_activation"
            assert isinstance(error.original_exception, PermissionError)
            print("agent metadata refused:", error.phase)
        else:
            raise AssertionError("The unapproved agent was admitted.")
        assert book.describe_spells_in_spellbook() == []
        assert supplied.render("still-owned-by-caller") == "report:still-owned-by-caller"

        spell_id = conduit.bind(
            spell=supplied, existence="unique", submitted_by="report-agent",
        )
        registered = book.find_spell_by_id(spell_id)
        assert registered is not None
        assert registered.metadata == {
            "submitted_by": "report-agent",
            "review_policy": "report-schema-v1",
            "post_checked": True,
        }
        assert "agent-reviewed" in registered.tags
        assert conduit.meld("ReportTool") is supplied
        assert supplied.render("weekly") == "report:weekly"
        assert review.published_ids == [spell_id]
        print("accepted existing object:", registered.metadata)

        # add appends: record_registration runs before the later failing callback.
        conduit.add_bind_hooks(post=[unavailable_audit_sink])
        backup = BackupReport()
        try:
            conduit.bind(spell=backup, existence="unique", submitted_by="report-agent")
        except md.HookExecutionError as error:
            assert error.phase == "post_bind"
            assert isinstance(error.original_exception, RuntimeError)
            print("post notification failed; inspect the published binding before retrying")
        else:
            raise AssertionError("The audit failure was not propagated.")
        assert len(review.published_ids) == 2
        published_backup = book.find_spell_by_id(review.published_ids[-1])
        assert published_backup is not None
        assert published_backup.spell_name == "BackupReport"
        assert published_backup.metadata["post_checked"] is True
        assert conduit.meld("BackupReport") is backup
        print("binding survived post failure:", published_backup.spell_name)

        conduit.clear_bind_hooks()
        assert conduit.meld("ReportTool") is supplied
        assert registered.metadata["post_checked"] is True
    finally:
        if conduit is not None:
            conduit.cleanup()
        book.cleanup()


if __name__ == "__main__":
    main()
