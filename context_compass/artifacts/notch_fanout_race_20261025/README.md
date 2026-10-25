# notch_fanout_race_20261025

Evidence for EPIC-2026-10-25-notch_fanout_inflight_melds and its child task
TASK-2026-10-16-order_inflight_borrower_melds_against_notch_fanout (melder_0, 2026-10-25).

- `runs/` - the 0.2.8267 reruns: rule 2's rate and kinds probes (they live in `../meld_contract_scan_20261015/`)
  and the in-Book probe's 20- and 100-run captures, the GIL off and on.
- `probes/probe_inbook_notch_race.py` - the in-Book variant: a dependent melded on four threads while its own Book
  notches the dependency.
- `scripts/` - the pass that recorded these findings into the tickets.
