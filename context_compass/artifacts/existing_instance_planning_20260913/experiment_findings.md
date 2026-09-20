# Existing-instance injection: observations before production changes

Source: Melder 0.2.40, Python 3.14.7 free-threaded. Production source remains unchanged.

| Experiment | Observation |
| --- | --- |
| Existing value resolved directly, unqualified/type-frame/named | Returns the exact supplied object. |
| Concrete annotation with unqualified instance registration | No matching DI candidate in Phase 3. |
| Concrete annotation with matching type-frame registration | Resolves the candidate, then fails during signature inspection in planning. |
| Nested existing dependency | Same planning failure. |
| Collection containing an existing value | Same planning failure. |
| Explicit SpellMap selecting named existing value | Same planning failure. |
| Consumer bound after an existing-only root is conjured | Signature-inspection failure at first consumer meld. |
| Callable object bound through ordinary public bind | Classified as a factory; called once at meld; returns its product. |
| Callable factory selected through explicit SpellMap | Product is injected, with one factory call. |

All existing-value cases have zero constructor requirements at bind. The caller supplied the marker
argument before binding; Melder must inject that object without rediscovering its constructor inputs.
Skipping existing-object constructor inspection must preserve the consumer's dependency edge.

The 11 characterization cases passed while recording the present successes/failures. They are not
green repair evidence. The corrected-contract integration file has 10 cases: seven expected failures
(both iterators plus five injection paths), three direct-root preservation controls passing.

The initial draft's callable-as-existing assumptions were incorrect for today's public dispatch and
are archived in initial_native_cases.py. Whether to add callable-object-as-value binding is an open
API question, separate from correcting the two planning branches for supported existing creations.

Evidence:
- experiments_corrected.log
- experiments_corrected.xml
- ../provider_artifact_ownership_20260913/regressions_discussion_final.xml

Catch-up paths and source contracts are in the owning task's Catch-up Read Map.
