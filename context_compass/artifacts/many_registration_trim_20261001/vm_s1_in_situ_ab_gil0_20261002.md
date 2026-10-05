# S1 in situ - interleaved A/B on the real emitted plans, VM 3.14.7t, GIL off, 2026-10-02T15:18:58Z

Method: `ab_medians.py N <before tree> <after tree>` runs the certification harness alternately on two working
copies N times (before = the pristine 0.2.8215 tree copy; after = the S1 working copy) and reports per-shape
medians of the plain plan (plan-direct ns per creation) and the whole meld by name. VM load average 0.9-1.4
during the runs (something outside the sandbox was busy), hence the interleaving and the medians; the ranges are
printed. Directional, 2-core VM.

## A1 (with-statement hot verb) vs the pristine tree, 5 reps each (logs/ab_medians_a1.md)

| shape | measure | before median (min-max) | after median (min-max) | delta |
| --- | --- | ---: | ---: | ---: |
| chain8_transient | meld | 882 (849-963) | 737 (711-780) | -16% |
| chain8_transient | plan | 804 (723-860) | 639 (630-714) | -21% |
| context_root | meld | 927 (880-1180) | 762 (738-840) | -18% |
| context_root | plan | 674 (647-693) | 559 (521-605) | -17% |
| wide8_existing | meld | 1168 (1117-1195) | 1082 (1000-1145) | -7% |
| wide8_existing | plan | 866 (829-1791) | 740 (698-784) | -15% |
| wide8_unique | meld | 962 (911-1003) | 765 (727-800) | -20% |
| wide8_unique | plan | 682 (653-762) | 527 (507-558) | -23% |
| worker | meld | 536 (512-630) | 414 (398-454) | -23% |
| worker | plan | 377 (362-433) | 249 (240-278) | -34% |

## A3 (explicit acquire/release) vs A1, 5 reps each (logs/ab_medians_a1_vs_a3.md)

| shape | measure | before median (min-max) | after median (min-max) | delta |
| --- | --- | ---: | ---: | ---: |
| chain8_transient | meld | 754 (737-777) | 698 (669-729) | -7% |
| chain8_transient | plan | 615 (591-651) | 602 (578-759) | -2% |
| context_root | meld | 736 (728-821) | 708 (697-748) | -4% |
| context_root | plan | 535 (534-560) | 513 (489-573) | -4% |
| wide8_existing | meld | 1045 (1001-1168) | 974 (959-990) | -7% |
| wide8_existing | plan | 730 (718-735) | 717 (683-1858) | -2% |
| wide8_unique | meld | 721 (719-778) | 724 (683-756) | +0% |
| wide8_unique | plan | 538 (501-553) | 491 (479-511) | -9% |
| worker | meld | 410 (392-438) | 386 (357-452) | -6% |
| worker | plan | 246 (231-279) | 216 (211-257) | -12% |

## Reading
- S1 (A1) on the real plans: plan -15..-34%, whole meld -7..-23% across the five shapes; the commandops shapes
  worker -23% and context_root -18% per meld.
- A3 over A1: plan -2..-12%, meld -4..-7% (one +0%), consistent in direction on nine of ten rows; the
  with-statement's enter/exit lookups are the difference.
- Single non-interleaved runs are not comparable on this VM today: paths S1 does not touch moved +8..+12%
  between two runs minutes apart (logs/shape_probe_before_0_2_8215.log vs logs/shape_probe_after_a1.log).

## Suites on the working copy with S1 (A1), 3.14t GIL off, sharded under the 120 s call cap
- unit: tests/unit/melder/aether 4166 passed; the rest of tests/unit 4150 passed, 3 skipped, 7 xfailed, with
  29 failed + 387 errors ALL in tests/unit/github_workflows, tests/unit/architecture_and_design,
  tests/unit/llm_support and tests/unit/melder/build_assets/test_system_documents_builder.py - repository-layout
  tests the src+tests working copy cannot satisfy (no .github/, no context_compass/system_docs, no llm_support/).
- component: 2257 passed, 43 skipped, 1 xfailed.
- integration: conduit+spellbook 875 passed; aether+multithreading+live_sim 800 passed; crystallizer 268
  passed; mutation_research 66 passed.
- A3 copy: creations unit directory + the two many-registration component files, 175 passed.
