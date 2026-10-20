- DATETIME: {ts}
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: S8's analysis and mechanism hold on 0.2.8260, after the new bind (0.2.8257-0.2.8258), as the owner asked
    (chat 2026-10-19: "make sure your change is true after our new bind changes because french and english should
    be seperate IDs now"). (1) English, French, SelfMade and TimedGreeter on one index at one address are four
    spell_ids (each the hash of its code) under one binding hash (one binding): a notch switches the index between
    separate spells. (2) The commit path, re-read whole, has the shape the 0.2.8255 FACT note gives: `notch_spell`
    ends the transaction outside its try and fans out to borrowers after; `_apply_notch` parks the outgoing
    version, promotes the incoming one, repoints the index and the frame claim by the incoming key and
    re-registers the index gated; the commit's structural validator resolves the staged binding key to the
    now-active member and runs phases 1-4 only for a never-compiled one, letting the error propagate. Nothing
    there takes identity from the bind call, so the undo inside the window still fits. (3) S1's defect still
    shapes the claims: staging at English's address drops its frame claim and Book lookup, and the failed notch
    leaves both on TimedGreeter. S1 and S2 land first (the owner's order) and change those steps, so the patch's
    claim and lookup restoration (the shared-address refinement) is re-derived on the tree they leave, before
    S8's code.
  EVIDENCE:
  - src/melder/aether/conduit/conduit.py:5650-5787
  - src/melder/aether/conduit/conduit.py:5828-5881
  - src/melder/aether/spellbook/spellbook.py:1572-1693
  - src/melder/aether/spellbook/spellbook.py:3947-4157
  - src/melder/aether/aetheric_frame/dev_ops/change_control_manager/change_control_manager.py:562-586
  - src/melder/aether/aetheric_frame/dev_ops/change_control_manager/change_control_manager.py:744-835
  - context_compass/artifacts/failed_notch_refusal_20261018/probes/probe_identity_after_new_bind.py:1-99
  - context_compass/artifacts/failed_notch_refusal_20261018/runs/probe_identity_after_new_bind_0_2_8260.txt:1-26
  IMPACT: S8's patch docs stand except their claim and lookup restoration step, which waits for the behaviour S1
    and S2 leave; nothing in them assumed spell_ids taken from the bind call.
  NEXT: Send M1-45 to melder_0 with the owner's order (S1, S3, S2, S8, S5, all with melder_1), then open S1.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
