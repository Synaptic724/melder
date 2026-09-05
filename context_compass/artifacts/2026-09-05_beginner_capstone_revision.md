# Beginner capstone revision evidence

- Owner: codex_2
- Recorded: 2026-09-05T10:47:49Z
- Task: TASK-2026-09-04-rtd-beginner-content

The chapter now shows four canonical files: models, bootstrap, consuming application, and entry point.
Bootstrap calls bind directly. Consumer-only type imports use TYPE_CHECKING; spell names select real
runtime objects. Constructor injection shares configuration/pool across fresh handlers. The entry point
attempts both cleanup calls and checks that the pool closed.

| Verification | Result | Evidence in rtd_validation_20260904/ |
| --- | --- | --- |
| Direct Python 3.14t execution | Three expected messages; pool closed; assertions pass | capstone_class_20260905.log |
| Beginner execution and metadata | 308 passed; one shared pytest-cache warning | capstone_beginner_20260905.xml |
| Documentation tests | 36 passed | capstone_docs_tests_20260905.log |
| Strict HTML | 294 pages | capstone_html_20260905.log |
| Site links/source bytes | 35,132 links; zero errors | capstone_links_20260905.log |
| Extracted four-file download | Exact bytes; independent run passes | capstone_download_20260905.json |
| ePub/PDF rebuild | Success; PDF is 106 pages | capstone_epub_20260905.log, capstone_pdf_20260905.log |
| Normal tracked other-corpus check | 347 files; proofs match | capstone_other_final_20260905.log |

Browser inspection confirmed module captions, binding explanation, typed consumer, expected output,
and downloads. The revised capstone is open at http://127.0.0.1:8765/beginner/capstone.html.
PDF guide pages 13-18 and lesson pages 90-92 were rendered and reviewed with no clipping or missing
glyphs observed. Existing small TeX overflow warnings elsewhere remain in the logs. HTML archive and
all four local RTD staging outputs were refreshed.

## Separate runtime observation

A prebuilt AppConfig requires spellframe=AppConfig for concrete constructor matching. That resolves
the first failure, but plan_group then reports that the AppConfig instance is not callable.
Reproduce by replacing the bootstrap registration with:
book.bind(spell=AppConfig("orders-service"), existence="unique", spellframe=AppConfig),
keeping the pool/handler registrations and calling book.conjure().
Traces: capstone_direct_20260905.log and capstone_fixed_20260905.log.
The published capstone uses the verified AppConfig class binding with constructor defaults.
No runtime workaround or compiler edit was made; root-cause investigation remains separate.

Commits remain owner-managed. These checks describe tested inputs; final hosted/release qualification
must use the final chosen revision after concurrent runtime work settles.

## Import and argument-flow clarification

On 2026-09-05T11:20:37Z, the consumer's Melder import moved out of TYPE_CHECKING. Normal calls had worked
on Python 3.14, but get_type_hints(run_application) raised NameError for md. It now resolves the real
Conduit type and list[str] return. Only local application-object annotations retain guarded imports.
The guide explains that imports make functions available, main calls bootstrap, and main passes the
returned conduit into run_application. The type annotation does not create or retrieve that object.
The focused capstone test, full site check, and normal other-corpus check pass. Browser and offline
outputs were refreshed; the 106-page PDF's revised capstone pages were rendered and reviewed.
Evidence: capstone_annotations_20260905.log and capstone_import_*_20260905.log in the same log folder.

## Final owner decision and push-readiness check

At 2026-09-05T11:47:56Z, the owner explicitly restored the earlier TYPE_CHECKING-only Melder import.
The prior ordinary call path was valid; evaluated annotation inspection was not its requirement.
The call-flow explanation remains. Restored execution, strict HTML, 35,132 links, and final source/
repository asset checks pass. Generated source manifests and all stale corpora were refreshed.
Web/offline/archive/staging copies now use the restored code; the preview and PDF were inspected.
See restore_typechecking_* and push_* logs. This qualifies the docs for a feature-branch push,
not the entire mixed branch for production. Hosted RTD and final S9 verification still remain.
