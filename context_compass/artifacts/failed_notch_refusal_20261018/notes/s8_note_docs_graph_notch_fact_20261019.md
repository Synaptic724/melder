- DATETIME: {ts}
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: S8's documents, graph, notch and release note are in. land_s8_docs.py (41 edits) carries the refusal into
    src_architecture (the boundary list, the summary, a new step 6 of the SpellIndex Mutation Entry sequence, an
    operational invariant, a fixed failure mode, four code-map entries remeasured), src_components (Spellbook Core,
    Conduit Runtime, the error's contract, the SpellIndex Mutation Surface, the notch flow, the code map),
    tests_components (both test modules catalogued with key files and code-map records; the aether integration
    tree recounted to 50, the core union 278) and tests_architecture (a handoff entry); the three citations
    remap_s8_citations.py widened cite 4022-4024 again. The four indexes are regenerated and --check OK; the
    bounds recipe flags the same 2 of 1419 citations as at S3's landing (bare file names in an older handoff
    entry). Graph: extracted with --strict (593 descriptors, none skipped); Spellbook gains one responsibility and
    its MutationResearch edge's why, SpellbookValidationError one responsibility (graph_prose_s8.py); both accepted
    after their source was read (Spellbook: S3's accepted text plus S8's whole diff; the error file whole);
    assembled and --check OK (593 sections). Conduit and ChangeControlManager stay SEMANTICS_STALE, as before this
    landing. Notch: `__version__` read 0.2.8261, set 0.2.8262. Release note: the section "A notch whose new version
    fails its check is refused, and nothing moves" and one packaging bullet, the header 0.2.8262 and the rebuild
    line for 0.2.8262; its example, run as written, prints the refusal line and "release-note example: OK" with the
    GIL off and on.
  EVIDENCE:
  - context_compass/artifacts/failed_notch_refusal_20261018/runs/land_s8_docs_apply.txt:1-6
  - context_compass/artifacts/failed_notch_refusal_20261018/runs/index_check_src_architecture_s8.txt:1-1
  - context_compass/artifacts/failed_notch_refusal_20261018/runs/index_check_src_components_s8.txt:1-1
  - context_compass/artifacts/failed_notch_refusal_20261018/runs/index_check_tests_components_s8.txt:1-1
  - context_compass/artifacts/failed_notch_refusal_20261018/runs/index_check_tests_architecture_s8.txt:1-1
  - context_compass/artifacts/failed_notch_refusal_20261018/runs/citation_bounds_s8.txt:1-3
  - context_compass/artifacts/failed_notch_refusal_20261018/runs/graph_extract_0_2_8262.txt:1-46
  - context_compass/artifacts/failed_notch_refusal_20261018/runs/graph_prose_0_2_8262.txt:1-3
  - context_compass/artifacts/failed_notch_refusal_20261018/runs/graph_accept_0_2_8262.txt:1-6
  - context_compass/artifacts/failed_notch_refusal_20261018/runs/graph_assemble_check_0_2_8262.txt:1-4
  - context_compass/artifacts/failed_notch_refusal_20261018/runs/notch_0_2_8262.txt:1-1
  - context_compass/artifacts/failed_notch_refusal_20261018/runs/release_note_s8_apply.txt:1-2
  - context_compass/artifacts/failed_notch_refusal_20261018/runs/release_note_probe_s8_0_2_8262_gil0.txt:1-2
  - context_compass/artifacts/failed_notch_refusal_20261018/runs/release_note_probe_s8_0_2_8262_gil1.txt:1-6
  - context_compass/system_docs/src_architecture.md:1176-1215
  - context_compass/system_docs/src_architecture.md:2500-2513
  - release_docs/next_version_release.md:1145-1217
  - src/melder/__version__.py:12-12
  IMPACT: S8 is landed but for the rebuild, which comes last - after the closures and any small fixes this pass
    takes on the owner's word.
  NEXT: Turn S8 in (close_s8.py), then S3.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
