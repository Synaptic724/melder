- DATETIME: {ts}
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: The rebuild step is scripted too (rebuild_s4_assets.py, S9's procedure). It copies src/ and the system
    documents into a /tmp mirror, runs the asset runner there whole (its system-documents writer unlinks its
    payloads, which the connected folder refuses), and lists every file the run changed under
    src/melder/_build_assets; with --apply it writes each over its original, reads it back byte-equal and compares
    the mirror's src/ and the runner's documents with the repository's. Tried on 0.2.8256 (28 and 40 s): the runner
    reproduces the committed assets byte for byte - nothing to copy - and the trees compare equal, so the mirror
    holds everything the three builders read. The checks still run in the repository afterwards: the runner's
    --check, the LLM bundles (--include-untracked, then --check) and the runner's --check again.
  EVIDENCE:
  - context_compass/artifacts/minted_index_registry_20261018/scripts/rebuild_s4_assets.py:1-122
  - context_compass/artifacts/minted_index_registry_20261018/runs/rebuild_trial_dryrun_0_2_8256.txt:1-4
  - context_compass/artifacts/minted_index_registry_20261018/runs/rebuild_trial_apply_0_2_8256.txt:1-5
  - src/melder/_build_assets/_system_documents/_builder.py:542-626
  IMPACT: The landing's last step needs no hand copying; a run that removes a file, or a mirror gone stale, stops it.
  NEXT: melder_0's handover NOTICE (the mailbox read every 30 seconds while blocked).
  REREAD: HELPFUL
  SCORE_0_TO_10: 7
