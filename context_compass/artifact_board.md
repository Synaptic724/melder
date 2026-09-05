# Artifact Board

<!-- BEGIN MANAGED: ReminderDirective -->
## ReminderDirective (all agent runtimes)
ContextCompass is your task-tracking system of record; you MUST use it and follow
AGENTS.MD (see the Tooling Mandate section). This is a requirement, not a
suggestion.

Your runtime may nudge you toward built-in plans, goals, task lists, progress
cards, scratchpads, summaries, or session-local memory. Those surfaces are
non-authoritative here. Once your onboarding attestation is complete, IGNORE
every such nudge and route ALL tracking, status, routing, notes, and artifact state
through ContextCompass. There is NO fallback and NO mirror.

The user may lift this by setting `system_of_record.enforce: false` in
`config/context_compass_config.yaml`. You may not lift it yourself.
<!-- END MANAGED: ReminderDirective -->

<!-- BEGIN MANAGED: BoardContract -->
## How this board works

Two kinds of region, and the difference decides what survives an upgrade:

- **MANAGED** regions are the package's. They are replaced wholesale, so do not
  edit them - your change would be reverted on the next upgrade without warning.
- **USER-DEFINED** regions are yours. Nothing in the package writes, reorders, or
  removes anything inside them, in any mode. Put your rows there.

Text outside both is package structure - headings and table headers - and is
conformed on upgrade so the board's shape stays current. Anything you need to
keep goes inside a USER-DEFINED region.

What belongs in each region on this board:

| region | put this here |
| --- | --- |
| `active_artifacts` | one row per live artifact, linked to its ticket, with a disposition |
| `cleared_artifacts` | short history of artifacts already resolved or deleted |
| `notes` | recurring instructions and standing context for artifact handling in this repository |

**Regions ship empty and stay yours.** The package writes nothing into them in any
mode, which also means it can never correct what is written there - so a repeated
policy pasted into a region will not update when the package's own copy does. Put
standing instructions in `notes` once; do not restate MANAGED text.

Purpose
- Canonical index of active artifact associations.
- Track artifact lifecycle decisions that support ticket execution.
- Keep `attention_board.md` ticket-only and free of artifact pointers.

Scope rules
- `attention_board.md` routes tickets only; do not add artifact paths there.
- Tickets remain canonical memory; this board is an association index.
- Add rows only when a ticket has one or more active artifact files.
- Every artifact row must include a ticket path and retention decision.

Disposition values
- `delete_on_close`: remove artifact when ticket closes.
- `retain_as_reference`: keep artifact with explicit reason.
- `promote_to_documentation`: convert artifact into durable docs.
<!-- END MANAGED: BoardContract -->

## Active Artifact Links
| ticket | artifact_path | artifact_type | status | disposition | next | updated_at | reread |
| --- | --- | --- | --- | --- | --- | --- | --- |
<!-- BEGIN USER-DEFINED: active_artifacts -->
| tickets/tasks/2026-09-04_rtd_ci_and_offline_task.md | artifacts/rtd_validation_20260904/committed_corpus_audit_20260905.json | validation_report | active | retain_as_reference | Exact committed-input failure: one additional # byte in .gitignore. | 2026-09-05T15:54:51Z | HELPFUL |
| tickets/tasks/2026-09-04_rtd_ci_and_offline_task.md | artifacts/rtd_validation_20260904/rebuilt_commit_corpus_proof_20260905.json | validation_report | active | retain_as_reference | Rebuilt manifest matches both branch and actual CI merge inputs. | 2026-09-05T15:54:51Z | REQUIRED |
| tickets/tasks/2026-09-04_rtd_quality_audit_task.md | artifacts/rtd_validation_20260904/final_inventory_20260905.json | validation_report | active | retain_as_reference | Interpreted by the final quality audit; release qualification is current output proof. | 2026-09-05T14:03:49Z | HELPFUL |
| tickets/tasks/2026-09-04_rtd_quality_audit_task.md | artifacts/rtd_validation_20260904/final_docs_tests_20260905.log | validation_report | active | retain_as_reference | Interpreted by the final quality audit; release qualification is current output proof. | 2026-09-05T14:03:49Z | HELPFUL |
| tickets/tasks/2026-09-04_rtd_quality_audit_task.md | artifacts/rtd_validation_20260904/final_examples_20260905.log | validation_report | active | retain_as_reference | Interpreted by the final quality audit; release qualification is current output proof. | 2026-09-05T14:03:49Z | HELPFUL |
| tickets/tasks/2026-09-04_rtd_quality_audit_task.md | artifacts/rtd_validation_20260904/final_examples_20260905.xml | validation_report | active | retain_as_reference | Interpreted by the final quality audit; release qualification is current output proof. | 2026-09-05T14:03:49Z | HELPFUL |
| tickets/tasks/2026-09-04_rtd_quality_audit_task.md | artifacts/rtd_validation_20260904/final_protocol_retry_20260905.log | validation_report | active | retain_as_reference | Interpreted by the final quality audit; release qualification is current output proof. | 2026-09-05T14:03:49Z | HELPFUL |
| tickets/tasks/2026-09-04_rtd_quality_audit_task.md | artifacts/rtd_validation_20260904/final_protocol_retry_20260905.xml | validation_report | active | retain_as_reference | Interpreted by the final quality audit; release qualification is current output proof. | 2026-09-05T14:03:49Z | HELPFUL |
| tickets/tasks/2026-09-04_rtd_quality_audit_task.md | artifacts/rtd_validation_20260904/final_html_20260905.log | validation_report | active | retain_as_reference | Interpreted by the final quality audit; release qualification is current output proof. | 2026-09-05T14:03:49Z | HELPFUL |
| tickets/tasks/2026-09-04_rtd_quality_audit_task.md | artifacts/rtd_validation_20260904/final_links_20260905.log | validation_report | active | retain_as_reference | Interpreted by the final quality audit; release qualification is current output proof. | 2026-09-05T14:03:49Z | HELPFUL |
| tickets/tasks/2026-09-04_rtd_quality_audit_task.md | artifacts/rtd_validation_20260904/final_source_assets_20260905.log | validation_report | active | retain_as_reference | Interpreted by the final quality audit; release qualification is current output proof. | 2026-09-05T14:03:49Z | HELPFUL |
| tickets/tasks/2026-09-04_rtd_quality_audit_task.md | artifacts/rtd_validation_20260904/final_repo_assets_20260905.log | validation_report | active | retain_as_reference | Interpreted by the final quality audit; release qualification is current output proof. | 2026-09-05T14:03:49Z | HELPFUL |
| tickets/tasks/2026-09-04_rtd_quality_audit_task.md | artifacts/rtd_validation_20260904/final_epub_20260905.log | validation_report | active | retain_as_reference | Interpreted by the final quality audit; release qualification is current output proof. | 2026-09-05T14:03:49Z | HELPFUL |
| tickets/tasks/2026-09-04_rtd_quality_audit_task.md | artifacts/rtd_validation_20260904/final_pdf_20260905.log | validation_report | active | retain_as_reference | Interpreted by the final quality audit; release qualification is current output proof. | 2026-09-05T14:03:49Z | HELPFUL |
| tickets/tasks/2026-09-04_rtd_quality_audit_task.md | artifacts/rtd_validation_20260904/final_archive_20260905.log | validation_report | active | retain_as_reference | Interpreted by the final quality audit; release qualification is current output proof. | 2026-09-05T14:03:49Z | HELPFUL |
| tickets/tasks/2026-09-04_rtd_quality_audit_task.md | artifacts/rtd_validation_20260904/final_offline_20260905.json | validation_report | active | retain_as_reference | Interpreted by the final quality audit; release qualification is current output proof. | 2026-09-05T14:03:49Z | HELPFUL |
| tickets/tasks/2026-09-04_rtd_ci_and_offline_task.md | artifacts/rtd_validation_20260904/final_pdf_wrap_20260905.log | validation_report | active | retain_as_reference | Final wrapping, packaging, and version evidence. | 2026-09-05T14:03:49Z | HELPFUL |
| tickets/tasks/2026-09-04_rtd_ci_and_offline_task.md | artifacts/rtd_validation_20260904/hosted_environment_simulation_20260905.log | validation_report | active | retain_as_reference | Final wrapping, packaging, and version evidence. | 2026-09-05T14:03:49Z | HELPFUL |
| tickets/tasks/2026-09-04_rtd_ci_and_offline_task.md | artifacts/rtd_validation_20260904/post_config_repo_check_20260905.log | validation_report | active | retain_as_reference | Final wrapping, packaging, and version evidence. | 2026-09-05T14:03:49Z | HELPFUL |
| tickets/tasks/2026-09-04_rtd_ci_and_offline_task.md | artifacts/rtd_validation_20260904/release_archive_20260905.log | validation_report | active | retain_as_reference | Final wrapping, packaging, and version evidence. | 2026-09-05T14:03:49Z | HELPFUL |
| tickets/tasks/2026-09-04_rtd_ci_and_offline_task.md | artifacts/rtd_validation_20260904/release_epub_20260905.log | validation_report | active | retain_as_reference | Final wrapping, packaging, and version evidence. | 2026-09-05T14:03:49Z | HELPFUL |
| tickets/tasks/2026-09-04_rtd_ci_and_offline_task.md | artifacts/rtd_validation_20260904/release_html_20260905.log | validation_report | active | retain_as_reference | Final wrapping, packaging, and version evidence. | 2026-09-05T14:03:49Z | HELPFUL |
| tickets/tasks/2026-09-04_rtd_ci_and_offline_task.md | artifacts/rtd_validation_20260904/release_links_20260905.log | validation_report | active | retain_as_reference | Final wrapping, packaging, and version evidence. | 2026-09-05T14:03:49Z | HELPFUL |
| tickets/tasks/2026-09-04_rtd_ci_and_offline_task.md | artifacts/rtd_validation_20260904/release_other_build_20260905.log | validation_report | active | retain_as_reference | Final wrapping, packaging, and version evidence. | 2026-09-05T14:03:49Z | HELPFUL |
| tickets/tasks/2026-09-04_rtd_ci_and_offline_task.md | artifacts/rtd_validation_20260904/release_qualification_20260905.json | validation_report | active | retain_as_reference | Final wrapping, packaging, and version evidence. | 2026-09-05T14:03:49Z | HELPFUL |
| tickets/tasks/2026-09-04_rtd_ci_and_offline_task.md | artifacts/rtd_validation_20260904/release_repo_assets_20260905.log | validation_report | active | retain_as_reference | Final wrapping, packaging, and version evidence. | 2026-09-05T14:03:49Z | HELPFUL |
| tickets/tasks/2026-09-04_rtd_ci_and_offline_task.md | artifacts/rtd_validation_20260904/pdf_table_before_20260905.png | validation_report | active | retain_as_reference | Final wrapping, packaging, and version evidence. | 2026-09-05T14:03:49Z | HELPFUL |
| tickets/tasks/2026-09-04_rtd_ci_and_offline_task.md | artifacts/rtd_validation_20260904/pdf_table_after_20260905.png | validation_report | active | retain_as_reference | Final wrapping, packaging, and version evidence. | 2026-09-05T14:03:49Z | HELPFUL |
| tickets/tasks/2026-09-04_rtd_site_foundation_task.md | artifacts/rtd_validation_20260904/navigation_audit_build_20260905.log | validation_report | active | retain_as_reference | Initial focus fix build evidence. | 2026-09-05T13:02:41Z | HELPFUL |
| tickets/tasks/2026-09-04_rtd_site_foundation_task.md | artifacts/rtd_validation_20260904/navigation_audit_links_20260905.log | validation_report | active | retain_as_reference | Initial focus fix link evidence. | 2026-09-05T13:02:41Z | HELPFUL |
| tickets/tasks/2026-09-04_rtd_site_foundation_task.md | artifacts/rtd_validation_20260904/navigation_final_build_20260905.log | validation_report | active | retain_as_reference | Final drawer focus build evidence. | 2026-09-05T13:02:41Z | HELPFUL |
| tickets/tasks/2026-09-04_rtd_site_foundation_task.md | artifacts/rtd_validation_20260904/navigation_final_links_20260905.log | validation_report | active | retain_as_reference | Final drawer focus link evidence. | 2026-09-05T13:02:41Z | HELPFUL |
| tickets/tasks/2026-09-04_rtd_site_foundation_task.md | artifacts/rtd_validation_20260904/accessibility_build_20260905.log | validation_report | active | retain_as_reference | Contrast/copy visibility build evidence. | 2026-09-05T13:02:41Z | HELPFUL |
| tickets/tasks/2026-09-04_rtd_site_foundation_task.md | artifacts/rtd_validation_20260904/accessibility_links_20260905.log | validation_report | active | retain_as_reference | 294 pages, 35,497 links, source equality pass. | 2026-09-05T13:02:41Z | HELPFUL |
| tickets/tasks/2026-09-04_rtd_site_foundation_task.md | artifacts/rtd_validation_20260904/accessibility_final_build_20260905.log | validation_report | active | retain_as_reference | Final inline-code/sidebar contrast build evidence. | 2026-09-05T13:02:41Z | HELPFUL |
| tickets/tasks/2026-09-04_rtd_site_foundation_task.md | artifacts/rtd_validation_20260904/no_custom_js_build_20260905.log | validation_report | active | retain_as_reference | Strict build without navigation.js/catalog.js. | 2026-09-05T13:02:41Z | HELPFUL |
| tickets/tasks/2026-09-04_rtd_quality_audit_task.md | artifacts/2026-09-05_rtd_final_quality_audit.md | validation_report | active | retain_as_reference | Complete local and hosted requirements-to-evidence audit. | 2026-09-05T12:06:59Z | REQUIRED |
| tickets/tasks/2026-09-04_rtd_beginner_content_task.md | artifacts/rtd_validation_20260904/restore_typechecking_runtime_20260905.log | validation_report | active | retain_as_reference | Restored import and scoped push-readiness evidence. | 2026-09-05T11:47:56Z | HELPFUL |
| tickets/tasks/2026-09-04_rtd_beginner_content_task.md | artifacts/rtd_validation_20260904/restore_typechecking_html_20260905.log | validation_report | active | retain_as_reference | Restored import and scoped push-readiness evidence. | 2026-09-05T11:47:56Z | HELPFUL |
| tickets/tasks/2026-09-04_rtd_beginner_content_task.md | artifacts/rtd_validation_20260904/restore_typechecking_links_20260905.log | validation_report | active | retain_as_reference | Restored import and scoped push-readiness evidence. | 2026-09-05T11:47:56Z | HELPFUL |
| tickets/tasks/2026-09-04_rtd_beginner_content_task.md | artifacts/rtd_validation_20260904/restore_typechecking_epub_20260905.log | validation_report | active | retain_as_reference | Restored import and scoped push-readiness evidence. | 2026-09-05T11:47:56Z | HELPFUL |
| tickets/tasks/2026-09-04_rtd_beginner_content_task.md | artifacts/rtd_validation_20260904/restore_typechecking_pdf_20260905.log | validation_report | active | retain_as_reference | Restored import and scoped push-readiness evidence. | 2026-09-05T11:47:56Z | HELPFUL |
| tickets/tasks/2026-09-04_rtd_beginner_content_task.md | artifacts/rtd_validation_20260904/push_source_check_20260905.log | validation_report | active | retain_as_reference | Restored import and scoped push-readiness evidence. | 2026-09-05T11:47:56Z | HELPFUL |
| tickets/tasks/2026-09-04_rtd_beginner_content_task.md | artifacts/rtd_validation_20260904/push_repo_check_before_20260905.log | validation_report | active | retain_as_reference | Restored import and scoped push-readiness evidence. | 2026-09-05T11:47:56Z | HELPFUL |
| tickets/tasks/2026-09-04_rtd_beginner_content_task.md | artifacts/rtd_validation_20260904/push_source_build_20260905.log | validation_report | active | retain_as_reference | Restored import and scoped push-readiness evidence. | 2026-09-05T11:47:56Z | HELPFUL |
| tickets/tasks/2026-09-04_rtd_beginner_content_task.md | artifacts/rtd_validation_20260904/push_repo_build_20260905.log | validation_report | active | retain_as_reference | Restored import and scoped push-readiness evidence. | 2026-09-05T11:47:56Z | HELPFUL |
| tickets/tasks/2026-09-04_rtd_beginner_content_task.md | artifacts/rtd_validation_20260904/push_source_final_20260905.log | validation_report | active | retain_as_reference | Restored import and scoped push-readiness evidence. | 2026-09-05T11:47:56Z | HELPFUL |
| tickets/tasks/2026-09-04_rtd_beginner_content_task.md | artifacts/rtd_validation_20260904/push_repo_final_20260905.log | validation_report | active | retain_as_reference | Restored import and scoped push-readiness evidence. | 2026-09-05T11:47:56Z | HELPFUL |
| tickets/tasks/2026-09-05_release_candidate_testpypi_workflow_task.md | system_docs/patches/active/release_candidate_testpypi_2026_09_05/architecture_patch_index.md | patch_index | active | promote_to_documentation | Generated index for candidate boundaries. | 2026-09-05T11:34:57Z | HELPFUL |
| tickets/tasks/2026-09-05_release_candidate_testpypi_workflow_task.md | system_docs/patches/active/release_candidate_testpypi_2026_09_05/component_patch_candidate_index.md | patch_index | active | promote_to_documentation | Generated index for package qualification. | 2026-09-05T11:34:57Z | HELPFUL |
| tickets/tasks/2026-09-05_release_candidate_testpypi_workflow_task.md | system_docs/patches/active/release_candidate_testpypi_2026_09_05/component_patch_publication_index.md | patch_index | active | promote_to_documentation | Generated index for final source proof. | 2026-09-05T11:34:57Z | HELPFUL |
| tickets/tasks/2026-09-05_release_candidate_testpypi_workflow_task.md | system_docs/patches/active/release_candidate_testpypi_2026_09_05/code_description_patch_identity_index.md | patch_index | active | promote_to_documentation | Generated index for gate ordering. | 2026-09-05T11:34:57Z | HELPFUL |
| tickets/tasks/2026-09-04_rtd_beginner_content_task.md | artifacts/rtd_validation_20260904/capstone_annotations_20260905.log | validation_report | active | retain_as_reference | Capstone import/annotation review evidence. | 2026-09-05T11:20:37Z | HELPFUL |
| tickets/tasks/2026-09-04_rtd_beginner_content_task.md | artifacts/rtd_validation_20260904/capstone_import_html_20260905.log | validation_report | active | retain_as_reference | Capstone import/annotation review evidence. | 2026-09-05T11:20:37Z | HELPFUL |
| tickets/tasks/2026-09-04_rtd_beginner_content_task.md | artifacts/rtd_validation_20260904/capstone_import_links_20260905.log | validation_report | active | retain_as_reference | Capstone import/annotation review evidence. | 2026-09-05T11:20:37Z | HELPFUL |
| tickets/tasks/2026-09-04_rtd_beginner_content_task.md | artifacts/rtd_validation_20260904/capstone_import_other_20260905.log | validation_report | active | retain_as_reference | Capstone import/annotation review evidence. | 2026-09-05T11:20:37Z | HELPFUL |
| tickets/tasks/2026-09-04_rtd_beginner_content_task.md | artifacts/rtd_validation_20260904/capstone_import_epub_20260905.log | validation_report | active | retain_as_reference | Capstone import/annotation review evidence. | 2026-09-05T11:20:37Z | HELPFUL |
| tickets/tasks/2026-09-04_rtd_beginner_content_task.md | artifacts/rtd_validation_20260904/capstone_import_pdf_20260905.log | validation_report | active | retain_as_reference | Capstone import/annotation review evidence. | 2026-09-05T11:20:37Z | HELPFUL |
| tickets/tasks/2026-09-05_release_candidate_testpypi_workflow_task.md | artifacts/release_candidate_20260905/validation.md | validation_workspace | active | delete_on_close | Task-local tests, package outputs, and validation logs. | 2026-09-05T10:50:07Z | HELPFUL |
| tickets/tasks/2026-09-04_rtd_beginner_content_task.md | artifacts/2026-09-05_beginner_capstone_revision.md | validation_report | active | retain_as_reference | Four-module capstone evidence and separate runtime probe. | 2026-09-05T10:48:53Z | REQUIRED |
| tickets/tasks/2026-09-04_rtd_beginner_content_task.md | artifacts/rtd_validation_20260904/capstone_direct_20260905.log | validation_report | active | retain_as_reference | Interpreted by the capstone revision report. | 2026-09-05T10:48:53Z | HELPFUL |
| tickets/tasks/2026-09-04_rtd_beginner_content_task.md | artifacts/rtd_validation_20260904/capstone_fixed_20260905.log | validation_report | active | retain_as_reference | Interpreted by the capstone revision report. | 2026-09-05T10:48:53Z | HELPFUL |
| tickets/tasks/2026-09-04_rtd_beginner_content_task.md | artifacts/rtd_validation_20260904/capstone_class_20260905.log | validation_report | active | retain_as_reference | Interpreted by the capstone revision report. | 2026-09-05T10:48:53Z | HELPFUL |
| tickets/tasks/2026-09-04_rtd_beginner_content_task.md | artifacts/rtd_validation_20260904/capstone_beginner_20260905.log | validation_report | active | retain_as_reference | Interpreted by the capstone revision report. | 2026-09-05T10:48:53Z | HELPFUL |
| tickets/tasks/2026-09-04_rtd_beginner_content_task.md | artifacts/rtd_validation_20260904/capstone_beginner_20260905.xml | validation_report | active | retain_as_reference | Interpreted by the capstone revision report. | 2026-09-05T10:48:53Z | HELPFUL |
| tickets/tasks/2026-09-04_rtd_beginner_content_task.md | artifacts/rtd_validation_20260904/capstone_docs_tests_20260905.log | validation_report | active | retain_as_reference | Interpreted by the capstone revision report. | 2026-09-05T10:48:53Z | HELPFUL |
| tickets/tasks/2026-09-04_rtd_beginner_content_task.md | artifacts/rtd_validation_20260904/capstone_html_20260905.log | validation_report | active | retain_as_reference | Interpreted by the capstone revision report. | 2026-09-05T10:48:53Z | HELPFUL |
| tickets/tasks/2026-09-04_rtd_beginner_content_task.md | artifacts/rtd_validation_20260904/capstone_links_20260905.log | validation_report | active | retain_as_reference | Interpreted by the capstone revision report. | 2026-09-05T10:48:53Z | HELPFUL |
| tickets/tasks/2026-09-04_rtd_beginner_content_task.md | artifacts/rtd_validation_20260904/capstone_download_20260905.json | validation_report | active | retain_as_reference | Interpreted by the capstone revision report. | 2026-09-05T10:48:53Z | HELPFUL |
| tickets/tasks/2026-09-04_rtd_beginner_content_task.md | artifacts/rtd_validation_20260904/capstone_epub_20260905.log | validation_report | active | retain_as_reference | Interpreted by the capstone revision report. | 2026-09-05T10:48:53Z | HELPFUL |
| tickets/tasks/2026-09-04_rtd_beginner_content_task.md | artifacts/rtd_validation_20260904/capstone_pdf_20260905.log | validation_report | active | retain_as_reference | Interpreted by the capstone revision report. | 2026-09-05T10:48:53Z | HELPFUL |
| tickets/tasks/2026-09-04_rtd_beginner_content_task.md | artifacts/rtd_validation_20260904/capstone_other_20260905.log | validation_report | active | retain_as_reference | Interpreted by the capstone revision report. | 2026-09-05T10:48:53Z | HELPFUL |
| tickets/tasks/2026-09-04_rtd_beginner_content_task.md | artifacts/rtd_validation_20260904/capstone_other_final_20260905.log | validation_report | active | retain_as_reference | Interpreted by the capstone revision report. | 2026-09-05T10:48:53Z | HELPFUL |
| tickets/tasks/2026-09-05_release_candidate_testpypi_workflow_task.md | system_docs/patches/active/release_candidate_testpypi_2026_09_05/architecture_patch.md | patch_doc | active | promote_to_documentation | Candidate identity, branch boundaries, and rollout. | 2026-09-05T10:25:12Z | REQUIRED |
| tickets/tasks/2026-09-05_release_candidate_testpypi_workflow_task.md | system_docs/patches/active/release_candidate_testpypi_2026_09_05/component_patch_candidate.md | patch_doc | active | promote_to_documentation | TestPyPI upload and isolated installation contract. | 2026-09-05T10:25:12Z | REQUIRED |
| tickets/tasks/2026-09-05_release_candidate_testpypi_workflow_task.md | system_docs/patches/active/release_candidate_testpypi_2026_09_05/component_patch_publication.md | patch_doc | active | promote_to_documentation | Pinned candidate evidence and fresh final checks. | 2026-09-05T10:25:12Z | REQUIRED |
| tickets/tasks/2026-09-05_release_candidate_testpypi_workflow_task.md | system_docs/patches/active/release_candidate_testpypi_2026_09_05/code_description_patch_identity.md | patch_doc | active | promote_to_documentation | Exact failure and retry ordering. | 2026-09-05T10:25:12Z | REQUIRED |
| tickets/tasks/2026-09-04_rtd_ci_and_offline_task.md | artifacts/2026-09-05_rtd_local_build_validation.md | validation_report | active | retain_as_reference | Local build, download, browser, and asset evidence; hosted checks remain. | 2026-09-05T09:41:40Z | REQUIRED |
| tickets/tasks/2026-09-04_rtd_ci_and_offline_task.md | artifacts/rtd_validation_20260904/rebuild_regression_20260905.log | validation_report | active | retain_as_reference | Evidence interpreted by the local validation report. | 2026-09-05T09:41:40Z | HELPFUL |
| tickets/tasks/2026-09-04_rtd_ci_and_offline_task.md | artifacts/rtd_validation_20260904/rebuild_negative_20260905.log | validation_report | active | retain_as_reference | Evidence interpreted by the local validation report. | 2026-09-05T09:41:40Z | HELPFUL |
| tickets/tasks/2026-09-04_rtd_ci_and_offline_task.md | artifacts/rtd_validation_20260904/docs_tests_20260905.log | validation_report | active | retain_as_reference | Evidence interpreted by the local validation report. | 2026-09-05T09:41:40Z | HELPFUL |
| tickets/tasks/2026-09-04_rtd_ci_and_offline_task.md | artifacts/rtd_validation_20260904/html_20260905.log | validation_report | active | retain_as_reference | Evidence interpreted by the local validation report. | 2026-09-05T09:41:40Z | HELPFUL |
| tickets/tasks/2026-09-04_rtd_ci_and_offline_task.md | artifacts/rtd_validation_20260904/links_20260905.log | validation_report | active | retain_as_reference | Evidence interpreted by the local validation report. | 2026-09-05T09:41:40Z | HELPFUL |
| tickets/tasks/2026-09-04_rtd_ci_and_offline_task.md | artifacts/rtd_validation_20260904/epub_20260905.log | validation_report | active | retain_as_reference | Evidence interpreted by the local validation report. | 2026-09-05T09:41:40Z | HELPFUL |
| tickets/tasks/2026-09-04_rtd_ci_and_offline_task.md | artifacts/rtd_validation_20260904/pdf_20260905.log | validation_report | active | retain_as_reference | Evidence interpreted by the local validation report. | 2026-09-05T09:41:40Z | HELPFUL |
| tickets/tasks/2026-09-04_rtd_ci_and_offline_task.md | artifacts/rtd_validation_20260904/pdf_metadata_20260905.json | validation_report | active | retain_as_reference | Evidence interpreted by the local validation report. | 2026-09-05T09:41:40Z | HELPFUL |
| tickets/tasks/2026-09-04_rtd_ci_and_offline_task.md | artifacts/rtd_validation_20260904/epub_check_20260905.json | validation_report | active | retain_as_reference | Evidence interpreted by the local validation report. | 2026-09-05T09:41:40Z | HELPFUL |
| tickets/tasks/2026-09-04_rtd_ci_and_offline_task.md | artifacts/rtd_validation_20260904/staging_20260905.json | validation_report | active | retain_as_reference | Evidence interpreted by the local validation report. | 2026-09-05T09:41:40Z | HELPFUL |
| tickets/tasks/2026-09-04_rtd_ci_and_offline_task.md | artifacts/rtd_validation_20260904/source_check_20260905.log | validation_report | active | retain_as_reference | Evidence interpreted by the local validation report. | 2026-09-05T09:41:40Z | HELPFUL |
| tickets/tasks/2026-09-04_rtd_ci_and_offline_task.md | artifacts/rtd_validation_20260904/repo_check_before_20260905.log | validation_report | active | retain_as_reference | Evidence interpreted by the local validation report. | 2026-09-05T09:41:40Z | HELPFUL |
| tickets/tasks/2026-09-04_rtd_ci_and_offline_task.md | artifacts/rtd_validation_20260904/repo_build_20260905.log | validation_report | active | retain_as_reference | Evidence interpreted by the local validation report. | 2026-09-05T09:41:40Z | HELPFUL |
| tickets/tasks/2026-09-04_rtd_ci_and_offline_task.md | artifacts/rtd_validation_20260904/repo_check_20260905.log | validation_report | active | retain_as_reference | Evidence interpreted by the local validation report. | 2026-09-05T09:41:40Z | HELPFUL |
| tickets/tasks/2026-09-04_rtd_ci_and_offline_task.md | artifacts/rtd_validation_20260904/readme_bundle_20260905.log | validation_report | active | retain_as_reference | Evidence interpreted by the local validation report. | 2026-09-05T09:41:40Z | HELPFUL |
| tickets/tasks/2026-09-04_rtd_ci_and_offline_task.md | artifacts/rtd_validation_20260904/fresh_html_20260905.log | validation_report | active | retain_as_reference | Fresh Sphinx diagnostic succeeds. | 2026-09-05T09:07:00Z | HELPFUL |
| tickets/tasks/2026-09-04_rtd_ci_and_offline_task.md | artifacts/rtd_validation_20260904/fresh_links_20260905.log | validation_report | active | retain_as_reference | 294 pages and 35,119 links pass. | 2026-09-05T09:07:00Z | HELPFUL |
| tickets/tasks/2026-09-04_rtd_ci_and_offline_task.md | artifacts/rtd_validation_20260904/fresh_links_20260905.json | validation_report | active | retain_as_reference | Zero errors; prior 19 failures were cached reference prefixes. | 2026-09-05T09:07:00Z | REQUIRED |
| tickets/tasks/2026-09-04_rtd_ci_and_offline_task.md | artifacts/rtd_validation_20260904/final_html.log | validation_report | active | retain_as_reference | Prior rendering built 294 declared pages. | 2026-09-05T08:58:00Z | HELPFUL |
| tickets/tasks/2026-09-04_rtd_ci_and_offline_task.md | artifacts/rtd_validation_20260904/site_check.log | validation_report | active | retain_as_reference | Prior independent validation fails on 19 backlinks. | 2026-09-05T08:58:00Z | REQUIRED |
| tickets/tasks/2026-09-04_rtd_ci_and_offline_task.md | artifacts/rtd_validation_20260904/ci.xml | validation_report | active | retain_as_reference | 127 focused CI workflow tests passed. | 2026-09-05T08:58:00Z | HELPFUL |
| tickets/tasks/2026-09-04_rtd_ci_and_offline_task.md | artifacts/rtd_validation_20260904/source_assets.log | validation_report | active | retain_as_reference | Three source build assets regenerated. | 2026-09-05T08:58:00Z | HELPFUL |
| tickets/tasks/2026-09-04_rtd_ci_and_offline_task.md | artifacts/rtd_validation_20260904/handbook_pdf.log | validation_report | active | retain_as_reference | PDF compilation; final visual review remains. | 2026-09-05T08:58:00Z | HELPFUL |
| tickets/tasks/2026-09-04_rtd_ci_and_offline_task.md | artifacts/rtd_validation_20260904/handbook_epub.log | validation_report | active | retain_as_reference | Earlier ePub build; final rebuild remains. | 2026-09-05T08:58:00Z | HELPFUL |
| tickets/tasks/2026-09-04_rtd_reference_content_task.md | artifacts/rtd_validation_20260904/reference_build.log | validation_report | active | retain_as_reference | Complete strict reference build at 292 pages. | 2026-09-05T00:50:29Z | HELPFUL |
| tickets/tasks/2026-09-04_rtd_expert_content_task.md | artifacts/rtd_validation_20260904/expert.xml | validation_report | active | retain_as_reference | 35 scripts passed; ProtocolCrafter hit sandbox temp ACL. | 2026-09-05T00:06:02Z | HELPFUL |
| tickets/tasks/2026-09-04_rtd_expert_content_task.md | artifacts/rtd_validation_20260904/expert_protocol.xml | validation_report | active | retain_as_reference | ProtocolCrafter passed unchanged outside sandbox. | 2026-09-05T00:06:02Z | HELPFUL |
| tickets/tasks/2026-09-04_rtd_advanced_content_task.md | artifacts/rtd_validation_20260904/advanced.xml | validation_report | active | retain_as_reference | All 19 Advanced scripts and 267 metadata checks passed. | 2026-09-04T23:55:00Z | HELPFUL |
| tickets/tasks/2026-09-04_rtd_intermediate_content_task.md | artifacts/rtd_validation_20260904/intermediate.xml | validation_report | active | retain_as_reference | All 37 Intermediate scripts passed on Python 3.14t. | 2026-09-04T23:49:46Z | HELPFUL |
| tickets/tasks/2026-09-04_rtd_beginner_content_task.md | artifacts/rtd_validation_20260904/beginner.xml | validation_report | active | retain_as_reference | Beginner execution and corpus metadata evidence; two later-tier corrections remain. | 2026-09-04T23:45:10Z | REQUIRED |
| tickets/tasks/2026-09-04_rtd_site_foundation_task.md | system_docs/patches/active/rtd_site_2026_09_04/architecture_patch.md | patch_doc | active | promote_to_documentation | Public-source and build boundaries before implementation. | 2026-09-04T22:14:08Z | REQUIRED |
| tickets/tasks/2026-09-04_rtd_site_foundation_task.md | system_docs/patches/active/rtd_site_2026_09_04/component_patch_documentation_pipeline.md | patch_doc | active | promote_to_documentation | Documentation component interfaces and failure contract. | 2026-09-04T22:14:08Z | REQUIRED |
| tickets/tasks/2026-09-04_rtd_site_foundation_task.md | system_docs/patches/active/rtd_site_2026_09_04/code_description_patch_documentation_pipeline.md | patch_doc | active | promote_to_documentation | Validation order and generated-directory containment. | 2026-09-04T22:14:08Z | REQUIRED |
| tickets/epics/2026-09-04_readthedocs_documentation_epic.md | artifacts/2026-09-04_readthedocs_site_blueprint.md | site_design | active | promote_to_documentation | Detailed product contract for nine delivery stories; retain through parent closure. | 2026-09-04T21:47:53Z | REQUIRED |
| tickets/stories/2026-09-04_rtd_navigation_and_site_shell_story.md | artifacts/2026-09-04_readthedocs_site_blueprint.md | shared_site_design | planned | promote_to_documentation | S1 consumes sections 1-3, 10-11; lifecycle owned by parent epic. | 2026-09-04T21:47:53Z | REQUIRED |
| tickets/stories/2026-09-04_rtd_example_catalog_story.md | artifacts/2026-09-04_readthedocs_site_blueprint.md | shared_site_design | planned | promote_to_documentation | S2 consumes section 8; lifecycle owned by parent epic. | 2026-09-04T21:47:53Z | REQUIRED |
| tickets/stories/2026-09-04_rtd_beginner_curriculum_story.md | artifacts/2026-09-04_readthedocs_site_blueprint.md | shared_site_design | planned | promote_to_documentation | S3 consumes section 4; lifecycle owned by parent epic. | 2026-09-04T21:47:53Z | REQUIRED |
| tickets/stories/2026-09-04_rtd_intermediate_curriculum_story.md | artifacts/2026-09-04_readthedocs_site_blueprint.md | shared_site_design | planned | promote_to_documentation | S4 consumes section 5; lifecycle owned by parent epic. | 2026-09-04T21:47:53Z | REQUIRED |
| tickets/stories/2026-09-04_rtd_advanced_curriculum_story.md | artifacts/2026-09-04_readthedocs_site_blueprint.md | shared_site_design | planned | promote_to_documentation | S5 consumes section 6; lifecycle owned by parent epic. | 2026-09-04T21:47:53Z | REQUIRED |
| tickets/stories/2026-09-04_rtd_expert_curriculum_story.md | artifacts/2026-09-04_readthedocs_site_blueprint.md | shared_site_design | planned | promote_to_documentation | S6 consumes section 7; lifecycle owned by parent epic. | 2026-09-04T21:47:53Z | REQUIRED |
| tickets/stories/2026-09-04_rtd_reference_and_architecture_story.md | artifacts/2026-09-04_readthedocs_site_blueprint.md | shared_site_design | planned | promote_to_documentation | S7 consumes section 9; lifecycle owned by parent epic. | 2026-09-04T21:47:53Z | REQUIRED |
| tickets/stories/2026-09-04_rtd_build_and_hosting_story.md | artifacts/2026-09-04_readthedocs_site_blueprint.md | shared_site_design | planned | promote_to_documentation | S8 consumes sections 11-12; lifecycle owned by parent epic. | 2026-09-04T21:47:53Z | REQUIRED |
| tickets/stories/2026-09-04_rtd_quality_and_launch_story.md | artifacts/2026-09-04_readthedocs_site_blueprint.md | shared_site_design | planned | promote_to_documentation | S9 consumes sections 15-16; lifecycle owned by parent epic. | 2026-09-04T21:47:53Z | REQUIRED |
| tickets/tasks/2026-09-04_readthedocs_sphinx_reference_discovery_task.md | artifacts/rtd_probe_20260904/README.md | compatibility_probe | deferred | retain_as_reference | Retain observations for the later Melder strategy; no Sphinx build ran. | 2026-09-04T21:11:55Z | HELPFUL |
| tickets/tasks/2026-08-30_upgrade_python_publish_workflow_task.md | system_docs/patches/active/release_matrix_concurrency_repair_2026_08_30/architecture_patch.md | patch_doc | active | promote_to_documentation | Four-cell support, synchronization invariants, migration, rollback, and coverage. | 2026-08-30T23:50:41Z | REQUIRED |
| tickets/tasks/2026-08-30_upgrade_python_publish_workflow_task.md | system_docs/patches/active/release_matrix_concurrency_repair_2026_08_30/component_patch_shared_spell_context.md | patch_doc | active | promote_to_documentation | Shared-spell phase revalidation and cold context rebuild boundary. | 2026-08-30T23:50:41Z | REQUIRED |
| tickets/tasks/2026-08-30_upgrade_python_publish_workflow_task.md | system_docs/patches/active/release_matrix_concurrency_repair_2026_08_30/code_description_patch_shared_spell_context_rebuild.md | patch_doc | active | promote_to_documentation | Double-checked slow-path control flow and deterministic test corrections. | 2026-08-30T23:50:41Z | REQUIRED |
| tickets/tasks/2026-08-30_implement_llm_support_compilation_pipeline_task.md | artifacts/2026-08-30_llm_support_compilation_pipeline_discovery.md | discovery_report | active | promote_to_documentation | Accepted design promoted into README, builder, manifest, indexes, tests, and workflows. | 2026-08-30T22:32:04Z | REQUIRED |
| tickets/tasks/2026-08-30_meld_spell_reference_ergonomics_task.md | system_docs/patches/active/human_meld_identity_api_2026_08_30/architecture_patch.md | patch_doc | active | promote_to_documentation | Human/machine identity plus public override boundary, migration, rollback, and coverage. | 2026-08-30T21:31:49Z | REQUIRED |
| tickets/tasks/2026-08-30_meld_spell_reference_ergonomics_task.md | system_docs/patches/active/human_meld_identity_api_2026_08_30/component_patch_meld_resolution.md | patch_doc | active | promote_to_documentation | Three public surfaces, internal forwarding, state/error deltas, and validation. | 2026-08-30T21:31:49Z | REQUIRED |
| tickets/tasks/2026-08-30_meld_spell_reference_ergonomics_task.md | system_docs/patches/active/human_meld_identity_api_2026_08_30/code_description_patch_meld_identity_dispatch.md | patch_doc | active | promote_to_documentation | Exact identity dispatch and public override-to-internal forwarding flow. | 2026-08-30T21:31:49Z | REQUIRED |
| tickets/epics/2026-07-18_parallel_restore_ulid_identity_epic.md | system_docs/patches/active/parallel_restore_ulid_identity_2026_07_18/architecture_patch.md | patch_doc | active | promote_to_documentation | Entry-gate artifact: invariants (canon barriers, all-or-nothing, never-rehydrate-ULIDs, emit lock law), additive interface deltas, migration order S1->S4, rollback lanes, coverage matrix. | 2026-07-18T22:30:00Z | REQUIRED |
| tickets/stories/2026-07-18_link_identity_journal_rows_story.md | system_docs/patches/active/parallel_restore_ulid_identity_2026_07_18/component_patch_link_identity_persistence.md | patch_doc | active | promote_to_documentation | S1 before/after: link ULIDs at commit, additive crystal rows + tombstones, legacy link_targets compat fold, per-link replay units. | 2026-07-18T22:30:00Z | REQUIRED |
| tickets/stories/2026-07-18_phase_scheduler_config_seam_story.md | system_docs/patches/active/parallel_restore_ulid_identity_2026_07_18/component_patch_phase_scheduler_seam.md | patch_doc | active | promote_to_documentation | S2 before/after: keyword-only worker/timeout overrides, crystallizer config keys, zero execution-semantics drift. | 2026-07-18T22:30:00Z | REQUIRED |
| tickets/stories/2026-07-18_cohort_aware_load_gate_story.md | system_docs/patches/active/parallel_restore_ulid_identity_2026_07_18/component_patch_load_gate_cohort.md | patch_doc | active | promote_to_documentation | S3 before/after: span cohort membership, enroll/withdraw verbs, frozen foreign-park semantics; code_description patch REQUIRED at story start. | 2026-07-18T22:30:00Z | REQUIRED |
| tickets/stories/2026-07-18_loadplan_phase_compiler_story.md | system_docs/patches/active/parallel_restore_ulid_identity_2026_07_18/component_patch_restore_engine_parallel.md | patch_doc | active | promote_to_documentation | S4 before/after: phase compilation of canon stages, per-entity unit factories, lock-safe report/built-stack, parity+chaos validation law; code_description patch REQUIRED at story start. | 2026-07-18T22:30:00Z | REQUIRED |
| tickets/stories/2026-07-18_loadplan_phase_compiler_story.md | system_docs/patches/active/parallel_restore_ulid_identity_2026_07_18/code_description_patch_phase_scheduler_quiesce.md | patch_doc | active | promote_to_documentation | S4 REOPEN delta: fail-fast quiesce control flow (wait_all_reported barrier, bounded unwind, hung-straggler residual, timeout stays preemptive). | 2026-07-19T10:45:14Z | REQUIRED |
| tickets/stories/2026-07-18_loadplan_phase_compiler_story.md | system_docs/patches/active/parallel_restore_ulid_identity_2026_07_18/component_patch_conduit_cleanup_frame_truth.md | patch_doc | active | promote_to_documentation | S4 REOPEN delta: _cleanup_normal_conduit step-4 split, frame removal first and independent; ordering-safety evidence. | 2026-07-19T10:45:14Z | REQUIRED |
| tickets/stories/2026-07-19_crystallizer_analysis_io_cache_story.md | system_docs/patches/active/crystallizer_analysis_io_cache_2026_07_19/architecture_patch.md | patch_doc | active | promote_to_documentation | IO-economy objective, invariants (truth law, record shape), descent-default decision, rollback. | 2026-07-19T11:38:21Z | REQUIRED |
| tickets/stories/2026-07-19_crystallizer_analysis_io_cache_story.md | system_docs/patches/active/crystallizer_analysis_io_cache_2026_07_19/component_patch_crystal_analysis_io.md | patch_doc | active | promote_to_documentation | Before/after per surface; additive interface deltas; validation expectations. | 2026-07-19T11:38:21Z | REQUIRED |
| tickets/stories/2026-07-19_crystallizer_analysis_io_cache_story.md | system_docs/patches/active/crystallizer_analysis_io_cache_2026_07_19/code_description_patch_physical_source_cache.md | patch_doc | active | promote_to_documentation | Cache + fast-path control flow, staleness law, descent gate, edge semantics. | 2026-07-19T11:38:21Z | REQUIRED |
| tickets/stories/2026-07-19_melder_init_composition_story.md | system_docs/patches/active/melder_init_composition_2026_07_19/architecture_patch.md | patch_doc | active | promote_to_documentation | Package-root composition rulings, curated surface, invariants, wheel posture. | 2026-07-19T11:53:00Z | REQUIRED |
| tickets/stories/2026-07-19_melder_init_composition_story.md | system_docs/patches/active/melder_init_composition_2026_07_19/component_patch_package_root.md | patch_doc | active | promote_to_documentation | Init/pyproject before-after, additive export deltas, DEBUG_MODE removal. | 2026-07-19T11:53:00Z | REQUIRED |
<!-- END USER-DEFINED: active_artifacts -->

## Recently Cleared Artifacts
| ticket | artifact_path | disposition | reason | closed_at |
| --- | --- | --- | --- | --- |
<!-- BEGIN USER-DEFINED: cleared_artifacts -->
| tickets/epics/completed/2026-09-02_ordered_live_spell_disposal_epic.md | system_docs/patches/active/ordered_disposal_priority_2026_09_04/; artifacts/2026-09-05_disposal_graft_policy_probe.py; artifacts/ordered_disposal_validation_20260905/ | promote_to_documentation / delete_on_close | Durable contracts promoted; temporary patches, probe, and scratch removed at accepted closure. Validation results retained in completed tickets. | 2026-09-05T14:22:02Z |
| tickets/tasks/completed/2026-09-04_implement_branch_ci_release_validation_task.md | artifacts/branch_ci_release_20260904/ | delete_on_close | Disposable test/build/log/tool workspace removed; validation summaries preserved in the completed ticket. | 2026-09-05T10:12:21Z |
| tickets/tasks/completed/2026-09-04_implement_branch_ci_release_validation_task.md | system_docs/patches/completed/branch_ci_release_2026_09_04/architecture_patch.md | promote_to_documentation | Durable decisions in .github/BRANCH_WORKFLOW.md; original patch archived intact for audit. | 2026-09-05T10:12:21Z |
| tickets/tasks/completed/2026-09-04_implement_branch_ci_release_validation_task.md | system_docs/patches/completed/branch_ci_release_2026_09_04/component_patch_ci_validation.md | promote_to_documentation | Durable decisions in .github/BRANCH_WORKFLOW.md; original patch archived intact for audit. | 2026-09-05T10:12:21Z |
| tickets/tasks/completed/2026-09-04_implement_branch_ci_release_validation_task.md | system_docs/patches/completed/branch_ci_release_2026_09_04/component_patch_release_publication.md | promote_to_documentation | Durable decisions in .github/BRANCH_WORKFLOW.md; original patch archived intact for audit. | 2026-09-05T10:12:21Z |
| tickets/tasks/completed/2026-09-04_implement_branch_ci_release_validation_task.md | system_docs/patches/completed/branch_ci_release_2026_09_04/code_description_patch_gate_flow.md | promote_to_documentation | Durable decisions in .github/BRANCH_WORKFLOW.md; original patch archived intact for audit. | 2026-09-05T10:12:21Z |
| tickets/epics/completed/2026-08-28_architecture_and_design_documentation_epic.md | artifacts/2026-08-28_architecture_and_design_documentation_discovery.md | promote_to_documentation | Discovery plan was fully promoted into the public `architecture_and_design/` documentation system; supporting artifact removed at accepted epic closure. | 2026-08-29T16:31:01Z |
| (25 active rows, various tickets) | see git history + archived tickets' Artifact Links | retain_as_reference | owner clean-slate 2026-07-18: owning tickets archived; all artifact files retained on disk | 2026-07-18T21:25:00Z |
| tickets/tasks/completed/2026-07-11_mr_units_scales_group_philosophy_task.md | artifacts/2026-07-11_mr_units_and_scales_philosophy.md | retain_as_reference | Philosophy ticket closed RULED; retained as the CANONICAL units-and-scales frame for MR agent tooling: grain laws (change=parts, identity=objects, impact=modules, comparison=full module text, work=compositions, intent=campaigns), depth floor at parts, comparison laws (recorded-only diffs), crystal well, and the GroupedResearchNode model (own node type, content-addressed compositions, subsystem lanes, mirrored strategy system). Future MR lanes read it beside philosophy V3. | 2026-07-11T23:20:16Z |
| tickets/epics/completed/2026-07-09_crystallizer_subsystem_decomposition_epic.md | artifacts/2026-07-09_crystallizer_philosophy_v3.md | retain_as_reference | Epic closed owner-accepted 2026-07-10; retained as the CANONICAL crystallizer philosophy (V3 subsystem model; supersedes V2/April where conflicting): five identities, cross-subsystem laws (carrier/edge/lock/verdict/flush/bite-size/twin-kind), V3 build horizon (MR Phase B next). Future crystallizer/MR lanes read it. | 2026-07-11T10:21:39Z |
| tickets/tasks/completed/2026-07-01_crystallizer_mutation_research_philosophy_orientation_task.md | artifacts/2026-07-01_mutation_research_philosophy_v2.md | retain_as_reference | Task closed (owner-directed 2026-07-06); retained as the CANONICAL V2 mutation philosophy for the whole crystallizer/MR program (supersedes 2026-05-09 where conflicting); mutation_0's lane reads it. | 2026-07-06T20:45:00Z |
| tickets/tasks/completed/2026-07-01_crystallizer_mutation_research_philosophy_orientation_task.md | artifacts/Archived/2026-07-01_crystallizer_philosophy_v2.md | retain_as_reference | Archived 2026-07-10 (melder_0, owner-directed): superseded by artifacts/2026-07-09_crystallizer_philosophy_v3.md (subsystem model). Was the canonical V2; duties absorbed into V3. | 2026-07-10T00:00:00Z |
| tickets/tasks/2026-05-22_synthesize_mutationresearch_aethericrift_crystallizer_context_task.md | artifacts/Archived/2026-04-26_crystallizer_philosophy.md | retain_as_reference | Archived 2026-07-10 (melder_0, owner-directed): superseded by artifacts/2026-07-09_crystallizer_philosophy_v3.md. Historical origin of the package shape and bind-promotion/world-first rules; thesis absorbed into V3. | 2026-07-10T00:00:00Z |
| tickets/epics/completed/2026-07-03_wire_crystallizer_into_melder_epic.md | artifacts/2026-07-03_first_cut_design_detail.md | retain_as_reference | Wire epic closed owner-accepted (Phase A complete); retained as the first-cut design reference (seed/unseed, removal depths, callsign+alias, activation gate) - restore engine + M1/M2/M3 lanes still cite it. | 2026-07-06T20:45:00Z |
| tickets/tasks/completed/2026-06-12_investigate_current_source_system_doc_drift_task.md | system_docs/patches/active/source_doc_namespace_normalization_2026_06_12/architecture_patch.md | retain_as_reference | Task turned in (hope_0 departed cleanup); patch files retained on disk at their active path. | 2026-06-30T23:04:50Z |
| tickets/tasks/completed/2026-06-12_investigate_current_source_system_doc_drift_task.md | system_docs/patches/active/source_doc_namespace_normalization_2026_06_12/component_patch_system_docs.md | retain_as_reference | Task turned in (hope_0 departed cleanup); patch files retained on disk at their active path. | 2026-06-30T23:04:50Z |
| tickets/tasks/completed/2026-06-12_investigate_current_source_system_doc_drift_task.md | system_docs/patches/active/source_doc_namespace_normalization_2026_06_12/src_graph.expanded.json | retain_as_reference | Task turned in (hope_0 departed cleanup); patch files retained on disk at their active path. | 2026-06-30T23:04:50Z |
| tickets/tasks/completed/2026-06-13_understand_devops_and_mediator_system_task.md | artifacts/2026-06-13_devops_mediator_system_map.md | retain_as_reference | Task turned in (mediator_builder_0 cleanup); retained as the DevOps/mediator reference map. NOTE: its 'graph truncated/invalid JSON' caveat is now obsolete -- readable_src_graph.json has been regenerated and validates end to end. | 2026-06-20T22:30:01Z |
| tickets/tasks/completed/2026-06-12_implement_scope_lock_table_and_pending_acquisition_task.md | system_docs/patches/completed/devops_scope_acquisition_2026_06_12/architecture_patch.md | promote_to_documentation | Durable deltas merged into canonical src_architecture.md/src_components.md at task closure; patch lane retained under patches/completed as reference. | 2026-06-12T22:21:06Z |
| tickets/tasks/completed/2026-06-12_implement_scope_lock_table_and_pending_acquisition_task.md | system_docs/patches/completed/devops_scope_acquisition_2026_06_12/component_patch_dev_ops_transactions.md | promote_to_documentation | Durable deltas merged into canonical docs at task closure; retained as reference. | 2026-06-12T22:21:06Z |
| tickets/tasks/completed/2026-06-12_implement_scope_lock_table_and_pending_acquisition_task.md | system_docs/patches/completed/devops_scope_acquisition_2026_06_12/code_description_patch_dev_ops_transactions.md | promote_to_documentation | Durable deltas merged into canonical docs at task closure; retained as reference. | 2026-06-12T22:21:06Z |
| tickets/stories/completed/2026-06-05_define_devops_transaction_control_plane_philosophy_story.md | artifacts/2026-06-05_devops_transaction_control_plane_philosophy.md | retain_as_reference | Closed by user cleanup request; retain the DevOps philosophy artifact as reference even though the story is no longer active. | 2026-06-12T11:58:04Z |
| tickets/epics/completed/2026-05-30_right_size_execution_strategy_compiler_outputs_epic.md | artifacts/2026-05-30_execution_strateg | retain_as_reference | (row truncated by a prior write fault; full row in git history) | unknown |
| tickets/tasks/2026-05-22_investigate_spellindex_transfer_semantic_drift_task.md | artifacts/Archived/2026-05-22_spellindex_multi_spell_transfer_blast_radius.md | retain_as_reference | Archived 2026-07-02 (crystal_0, owner-directed): superseded by the SpellIndex-as-index reframe - only index-based transfers are supported; bind creates an index, so spell-level transfer is unnecessary. | 2026-07-02T23:21:15Z |
| (untracked orphan) | artifacts/Archived/2026-05-18_conduit_aether_refactor_plan.md | retain_as_reference | Archived 2026-07-02 (crystal_0, owner-directed): no longer applies to the current outlook (Conduit->Aether decoupling plan). | 2026-07-02T23:21:15Z |
<!-- END USER-DEFINED: cleared_artifacts -->

## Notes
<!-- BEGIN USER-DEFINED: notes -->
### Active Artifact Notes (carried from the pre-region board)
- DATETIME: 2026-08-01T18:02:00Z
  TYPE: FACT
  CLAIM: CLOSURE-SYNC DRIFT REPAIRED (bootstrap_0, owner-directed cleanup). The
    `2026-08-01_configuration_diff_catalogue.md` row sat in Active Artifact Links
    pointing at `tickets/tasks/2026-08-01_config_structural_survey_task.md`, but that
    ticket had already moved to `tickets/tasks/completed/`. It was closed without
    running artifact closure sync, so this board advertised an active artifact against
    a closed lane. Row cleared under its own declared disposition
    (`promote_to_documentation`). NO acceptance claim is made about examples_0's work -
    pointer repair only, matching the precedent melder_1 set in
    TASK-2026-07-25-attention-board-truth-repair.
  EVIDENCE:
  - tickets/tasks/completed/2026-08-01_config_structural_survey_task.md
  IMPACT: Every remaining Active Artifact Links row now resolves to a ticket that
    exists at the path given; all active row paths were checked against disk.
  NEXT: Run artifact closure sync at ticket close rather than as later board repair.
  REREAD: HELPFUL
- DATETIME: 2026-07-18T21:25:00Z
  TYPE: FACT
  CLAIM: Clean slate under owner directive: every previously active artifact link (25 rows)
    was cleared in one pass because their owning tickets were archived to `tickets/*/archive/`.
    ZERO artifact files were deleted - everything under `artifacts/` and
    `system_docs/patches/` is retained on disk at its existing path. The canonical reference
    artifacts (crystallizer philosophy V3, MR philosophy V3, units-and-scales, bootstrap /
    persistence design details, code map + proof ledger, import/module lifecycle findings)
    remain readable where they were. One prior row carried `delete_on_close`
    (artifacts/2026-07-05_collection_di_probe.py, collection-DI epic) - retained anyway,
    pending an explicit owner ruling. Full former row set: this file's git history plus the
    `Artifact Links` sections of the archived tickets.
  NEXT: Re-add rows only when a new active ticket links artifacts.
  REREAD: REQUIRED
<!-- END USER-DEFINED: notes -->
