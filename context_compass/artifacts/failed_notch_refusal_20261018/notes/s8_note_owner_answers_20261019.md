- DATETIME: {ts}
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: DECISION
  CLAIM: The owner's answers (chat 2026-10-19), asked for every open item after S7 landed: the order is S1, S3,
    S2, S8, S5, all with melder_1, each landed and rebuilt before the next; the pace is "go straight through" -
    re-verify, fix, test, land, report after, stopping only for a real decision; the parked backlog is melder_1's
    pick, with "regression tests for everything so you can see if its actually a bug". On S8 he did not yet say
    go: shown the half-switch with this story's broken version (a constructor that takes its own class), he said
    it "looks like recursion" and asked for a test that proves the half-switch can happen. So the proof comes
    first, with a version that fails its check for an ordinary reason (two registered providers of its `Clock`
    parameter, AMBIGUOUS_PROVIDER), as a probe in plain words and a regression test; his word on the fix follows.
  EVIDENCE: context_compass/tickets/stories/2026-10-17_failed_notch_keeps_switch_without_borrowers_story.md:83-89
  IMPACT: S8 resumes for its proof only (no src edit); the fix waits for the owner's word after he sees it.
  NEXT: Write the probe and the regression test; run them on 0.2.8260 with the GIL off and on.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
