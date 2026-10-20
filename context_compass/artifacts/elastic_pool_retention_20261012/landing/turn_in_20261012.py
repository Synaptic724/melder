"""Turn in melder_1's finished tickets (owner directive 2026-10-12). Dry run by default; --apply writes."""
import os
import pathlib
import re
import sys

APPLY = "--apply" in sys.argv
NOW = sys.argv[1]
CC = pathlib.Path(".")
TASKS = CC / "tickets/tasks"
DONE = TASKS / "completed"
ACTIVE_P = CC / "system_docs/patches/active"
DONE_P = CC / "system_docs/patches/completed"
ARCHIVE = ["meldercache_suffix_2026_10_04", "spellmap_binding_name_case_2026_10_04",
           "live_unlink_visibility_race_2026_10_04"]
STALE_ACTIVE_LINKS = ARCHIVE + ["direct_spell_cleanup_lock_order_2026_10_11"]
EVIDENCE_OWED = "git add -A, commit, push, the Windows tiers and hosted CI"
T = [
    ("shallow_thread_scaling_ci", "2026-10-04_add_shallow_thread_scaling_to_preprod_benchmarks_task.md",
     ["The shallow thread-scaling benchmark runs on dev-to-preprod pull requests beside the two gauntlets",
      "(from speed-tests.yml since 2026-10-06, gating nothing); 475 workflow tests passed. No source change, no notch.",
      "Turned in by the owner 2026-10-12; staging, commit, push and the hosted three-OS run are the owner's."],
     "staging, commit, push and the hosted three-OS run",
     "Thread-scaling benchmark on dev-to-preprod PRs (no notch); turned in by owner directive. Next: none."),
    ("meldercache_suffix", "2026-10-04_rename_cache_suffix_to_meldercache_task.md",
     ["Landed, notched 0.2.8223: Melder's cache bundles are named .meldercache and old .melc files are inert;",
      "release note 'Cache files are named .meldercache' (release_docs/0.2.8227.md). Patch docs promoted at landing,",
      "archived at turn-in. Turned in by the owner 2026-10-12; the Windows tiers are the owner's."],
     "the Windows tiers",
     "Landed 0.2.8223 (.meldercache rename); patch archived; turned in by owner directive. Next: none."),
    ("preprod_ci_docs_and_bundles", "2026-10-04_fix_preprod_ci_docs_api_and_bundle_drift_task.md",
     ["Landed, notched 0.2.8225: SpellframeKind is off the package root (owner ruling), so the dev-to-preprod docs",
      "API check passes, and the llm_support bundle drift is fixed (packaging note in release_docs/0.2.8227.md).",
      "Turned in by the owner 2026-10-12; commit and push, with the four ignore-file changes, are the owner's."],
     "commit and push, with the four ignore-file changes",
     "Landed 0.2.8225 (docs API check, bundle drift); turned in by owner directive. Next: none."),
    ("ci_python_check_latest", "2026-10-04_use_newest_patch_in_single_version_ci_jobs_task.md",
     ["Every Python CI run comes from a per-release manifest (tests 3.14.0-3.14.8, speed 3.14.7) or the 3.14.7",
      "helper pin, and every route runs all 27 runtime cells; 503 workflow tests passed. No source change, no notch.",
      "Turned in by the owner 2026-10-12; commit, push and the hosted runs are the owner's."],
     "commit, push and the hosted runs",
     "Manifest-driven Python CI, 27 cells on every route (no notch); turned in by owner directive. Next: none."),
    ("descriptor_binding_name_case", "2026-10-04_match_descriptor_binding_names_like_bind_task.md",
     ["Landed, notched 0.2.8226: SpellMap and SpellContract keep binding names as written and resolve like bind and",
      "meld, locked by regression tests; release note 'Fixed: a SpellMap or SpellContract binding name matches the way",
      "bind and meld do' (release_docs/0.2.8227.md). Patch docs archived at turn-in. Turned in 2026-10-12."],
     "commit and push",
     "Landed 0.2.8226 (descriptor binding names); patch archived; turned in by owner directive. Next: none."),
    ("live_unlink_churn_phase_error", "2026-10-04_fix_live_unlink_churn_phase_error_task.md",
     ["Landed, notched 0.2.8227: a meld racing a link sever or an uncontract raises SpellbookValidationError, not",
      "PhaseExecutionError; release note 'Fixed: a meld that races a link change fails cleanly instead of with an",
      "internal phase error' (release_docs/0.2.8227.md). Patch docs archived at turn-in. Turned in 2026-10-12."],
     "push",
     "Landed 0.2.8227 (live unlink race); patch archived; turned in by owner directive. Next: none."),
    ("codecov_upload_tls", "2026-10-05_diagnose_codecov_upload_tls_failure_task.md",
     ["Diagnosed: the Codecov upload failed because Codecov's servers broke TLS; on the owner's directive it retries",
      "once with the PyPI-installed uploader when the signed download fails; 481 workflow tests passed. No notch.",
      "Turned in by the owner 2026-10-12; commit and push are the owner's."],
     "commit and push",
     "Codecov TLS diagnosis and PyPI-uploader retry (no notch); turned in by owner directive. Next: none."),
    ("agent_cicd_guide", "2026-10-05_write_agent_cicd_guide_task.md",
     [".github/ci_cd/ holds six guide pages for agents, special_instructions/ci_cd_guide.md points onboarding at it,",
      "and two contract tests keep it complete; 500 workflow tests passed. No notch. Turned in by the owner",
      "2026-10-12; git add -A of the six pages and push are the owner's."],
     "git add -A of the six guide pages and push",
     "Agent CI/CD guide folder (no notch); turned in by owner directive. Next: none."),
    ("rc_testpypi_recovery", "2026-10-06_recover_release_candidate_from_testpypi_outage_task.md",
     ["A TestPyPI blip is retried and a failed-jobs release-candidate re-run reuses the run's verified build;",
      "publication stays fresh-only; 512 workflow tests passed. No notch. Turned in by the owner 2026-10-12;",
      "commit, push and 'Re-run all jobs' on run 37443362134 are the owner's."],
     "commit, push and the release-candidate re-run",
     "Release-candidate recovery from a TestPyPI outage (no notch); turned in by owner directive. Next: none."),
    ("ubuntu_runner_pin", "2026-10-06_pin_ubuntu_runner_image_task.md",
     ["Every Linux CI job is pinned to ubuntu-24.04 before ubuntu-latest moves to Ubuntu 26.04, and a contract test",
      "refuses ubuntu-latest; 513 workflow tests passed. No notch. Turned in by the owner 2026-10-12; commit and push",
      "are the owner's."],
     "commit and push",
     "Linux runners pinned to ubuntu-24.04 (no notch); turned in by owner directive. Next: none."),
    ("speed_tests_nonblocking", "2026-10-06_make_speed_tests_nonblocking_task.md",
     ["The three speed tests start on every dev-to-preprod pull request from speed-tests.yml and never block",
      "merge-ready or the release-candidate qualification. No notch. Turned in by the owner 2026-10-12; git add -A,",
      "commit, push and a hosted dev-to-preprod run are the owner's."],
     "git add -A, commit, push and a hosted dev-to-preprod run",
     "Speed tests no longer block merge-ready (no notch); turned in by owner directive. Next: none."),
    ("spell_lookup_race", "2026-10-10_investigate_spell_lookup_by_id_race_task.md",
     ["Landed, notched 0.2.8229: Spellbook.find_spell_by_id answers from the Book's id maps instead of walking the",
      "live index map, locked by regression tests; release note 'Spell lookups and validation no longer fail while",
      "other spells change'. Turned in by the owner 2026-10-12; evidence kept."],
     EVIDENCE_OWED,
     "Landed 0.2.8229 (find_spell_by_id from id maps); evidence kept; turned in by owner directive. Next: none."),
    ("spell_map_followups", "2026-10-11_close_remaining_spell_map_races_task.md",
     ["Landed, notched 0.2.8230: bind publishes the spell maps under the Book lock, unlocked walks take snapshots,",
      "has_spell and contract details survive a racing cleanup, the Conduit spell lookups document their ValueError;",
      "release note 'Spell lookups and validation no longer fail while other spells change'. Turned in 2026-10-12."],
     EVIDENCE_OWED,
     "Landed 0.2.8230 (spell-map walks); evidence kept; turned in by owner directive. Next: none."),
    ("cross_object_lock_gaps", "2026-10-11_prove_and_fix_cross_object_lock_gaps_task.md",
     ["Landed, notched 0.2.8231: index-link notifications, contract reads and bind's cross-frame sweep hold under",
      "concurrent link/sever, member moves and frame birth/teardown, and the listing deadlock is gone; release note",
      "'Index links, contract reads and binds across frames hold up under concurrent changes'. Turned in 2026-10-12."],
     EVIDENCE_OWED,
     "Landed 0.2.8231 (cross-object locks); evidence kept; turned in by owner directive. Next: none."),
    ("lock_residuals_and_admission", "2026-10-11_close_lock_residuals_and_evaluate_mediator_admission_task.md",
     ["Landed, notched 0.2.8232 and 0.2.8233: find_contracted_spell and inspect_spell hold up under concurrent links",
      "and root registration, an overlapping cleanup_spell refuses, and a direct Spell.cleanup() no longer hangs",
      "against Book teardown or conjure (release note 'Index links, contract reads and binds across frames hold up",
      "under concurrent changes'). F2, F3 and the meld-time reruns stay recorded (Note 9). Turned in 2026-10-12."],
     EVIDENCE_OWED,
     "Landed 0.2.8232 and 0.2.8233 (lock residuals, direct cleanup); evidence kept; turned in. Next: none."),
    ("elastic_pool_retention", "2026-10-12_make_kernel_pools_elastic_task.md",
     ["Landed, notched 0.2.8234: SpellSpacePool and ConduitPool keep what a burst needed, up to 256, and decay to 20",
      "when quiet; the owner's native big test shows no regression at 20 threads and a 3-22x shorter return tail past",
      "20; release note 'Lesser conduits and spellspaces past 20 are kept and reused, then let go when quiet'.",
      "Accepted and turned in by the owner 2026-10-12; evidence kept."],
     "git add -A (the new component test, the archived patch folder, the evidence folder), commit, push, the Windows "
     "tiers and hosted CI",
     "Landed 0.2.8234 (elastic kernel pools); evidence kept; accepted and turned in by the owner. Next: none."),
]
CLEARED = [
    ("2026-10-12_make_kernel_pools_elastic_task.md", "artifacts/elastic_pool_retention_20261012/", "retain_as_reference",
     "Evidence of the 0.2.8234 landing: gauntlet runner, probes, big test, the VM and native runs, prototype and "
     "landing scripts."),
    ("2026-10-11_close_lock_residuals_and_evaluate_mediator_admission_task.md", "artifacts/lock_residuals_20261011/",
     "retain_as_reference", "Evidence of the 0.2.8232 and 0.2.8233 landings: residual stress logs and both scratch folders."),
    ("2026-10-11_prove_and_fix_cross_object_lock_gaps_task.md", "artifacts/cross_object_lock_gaps_20261011/",
     "retain_as_reference", "Evidence of the 0.2.8231 landing: probes, run logs and scratch_0.2.8231."),
    ("2026-10-11_close_remaining_spell_map_races_task.md", "artifacts/spell_lookup_race_20261010/followups/",
     "retain_as_reference", "Evidence of the 0.2.8230 landing: walker inventory, snapshot probe and scratch_0.2.8230."),
    ("2026-10-10_investigate_spell_lookup_by_id_race_task.md", "artifacts/spell_lookup_race_20261010/",
     "retain_as_reference", "Evidence of the 0.2.8229 landing: diagnostics, stress, benchmarks, r4/, r6/ and the proposals."),
    ("2026-10-04_fix_live_unlink_churn_phase_error_task.md",
     "system_docs/patches/completed/live_unlink_visibility_race_2026_10_04/", "promote_to_documentation",
     "Promoted to src_architecture and src_components at landing (0.2.8227); three patch docs archived at turn-in."),
    ("2026-10-04_match_descriptor_binding_names_like_bind_task.md",
     "system_docs/patches/completed/spellmap_binding_name_case_2026_10_04/", "promote_to_documentation",
     "Promoted to src_architecture and src_components at landing (0.2.8226); two patch docs archived at turn-in."),
    ("2026-10-04_rename_cache_suffix_to_meldercache_task.md",
     "system_docs/patches/completed/meldercache_suffix_2026_10_04/", "promote_to_documentation",
     "Promoted to src_architecture and src_components at landing (0.2.8223); two patch docs archived at turn-in."),
]


def section_span(text: str, heading: str):
    """Return (start, end) of a '## heading' section body, end at the next '## ' heading."""
    m = re.search(r"^## " + re.escape(heading) + r"[^\n]*\n", text, flags=re.M)
    assert m, heading
    nxt = re.search(r"^## ", text[m.end():], flags=re.M)
    return m.end(), (m.end() + nxt.start()) if nxt else len(text)


def close_ticket(item, name, summary, owed):
    p = TASKS / name
    text = p.read_bytes().decode("utf-8")
    assert "\r\n" not in text and "- Completed:" not in text, name
    assert re.search(r"^- Status: (review|in_progress)\s*$", text, flags=re.M), name
    text = re.sub(r"^- Status: (review|in_progress)\s*$", "- Status: done", text, count=1, flags=re.M)
    m = re.search(r"^- Updated: .*$", text, flags=re.M)
    assert m, name
    block = "- Updated: " + NOW + "\n\n- Completed: " + NOW + "\n- Summary: " + summary[0]
    for line in summary[1:]:
        block += "\n  " + line
    text = text[:m.start()] + block + text[m.end():]
    s, e = section_span(text, "State Transition Event")
    body = text[s:e].rstrip("\n")
    event = ("\n- from_state: review\n- to_state: done\n- transition_reason: (" + NOW + ") the owner turned in every "
             "finished melder_1 ticket (chat 2026-10-12: \"just close everything you finished\");\n  " + owed +
             " remain the owner's.")
    text = text[:s] + body + event + "\n\n" + text[e:]
    if "## Done Checklist" in text:
        s, e = section_span(text, "Done Checklist")
        part = text[s:e]
        part = re.sub(r"^- \[ \] (Acceptance criteria reviewed[^\n]*)$", r"- [x] \1 (owner turn-in, 2026-10-12)", part,
                      flags=re.M)
        part = re.sub(r"^- \[ \] (Board sync completed[^\n]*)$", r"- [x] \1", part, flags=re.M)
        text = text[:s] + part + text[e:]
    s, e = section_span(text, "Artifact Links")
    part = text[s:e]
    for pid in STALE_ACTIVE_LINKS:
        part = part.replace("system_docs/patches/active/" + pid + "/", "system_docs/patches/completed/" + pid + "/")
    text = text[:s] + part + text[e:]
    for line in text.split("\n"):
        pass
    long_new = [l for l in ([summary[0]] + summary[1:]) if len("  " + l) > 120 and len("- Summary: " + l) > 120]
    assert not [l for l in summary if len("- Summary: " + l) > 120 and l == summary[0]], name
    assert not [l for l in summary[1:] if len("  " + l) > 120], name
    if APPLY:
        p.write_bytes(text.encode("utf-8"))
        dest = DONE / name
        assert not dest.exists(), dest
        os.rename(p, dest)
    return text


def sync_attention(closed):
    b = CC / "attention_board.md"
    text = b.read_bytes().decode("utf-8")
    assert "\r\n" not in text
    lines = text.split("\n")
    out = []
    removed_rows = 0
    for l in lines:
        cells = l.split(" | ")
        if l.startswith("| ") and cells[0][2:] in closed and len(cells) == 12:
            removed_rows += 1
            continue
        out.append(l)
    text = "\n".join(out)
    # active attention details: bullet blocks under '### Active Attention Details' in the notes region
    m = re.search(r"^### Active Attention Details\n", text, flags=re.M)
    assert m
    nxt = re.search(r"^### ", text[m.end():], flags=re.M)
    s, e = m.end(), m.end() + nxt.start()
    block = text[s:e]
    entries = re.split(r"(?m)^(?=- )", block)
    kept, dropped = [], 0
    for ent in entries:
        mm = re.match(r"- ([a-z0-9_]+): SWITCH_TRIGGER", ent)
        if mm and mm.group(1) in closed:
            dropped += 1
            continue
        kept.append(ent)
    block = "".join(kept)
    if not block.startswith("\n"):
        block = "\n" + block
    text = text[:s] + block + text[e:]
    # closed anchors
    ab = "<!-- BEGIN USER-DEFINED: closed_anchors -->\n"
    ae = "<!-- END USER-DEFINED: closed_anchors -->"
    a0 = text.index(ab) + len(ab)
    a1 = text.index(ae)
    rows = [r for r in text[a0:a1].split("\n") if r.startswith("| ")]
    for item, name, _s, _o, note in T:
        rows.append("| " + item + " | done | melder_1 | tickets/tasks/completed/" + name + " | " + note + " | " + NOW + " |")
    rows = rows[-12:]
    text = text[:a0] + "\n".join(rows) + "\n" + text[a1:]
    if APPLY:
        b.write_bytes(text.encode("utf-8"))
    return removed_rows, dropped, rows


def sync_artifacts(closed_files):
    b = CC / "artifact_board.md"
    text = b.read_bytes().decode("utf-8")
    assert "\r\n" not in text
    act_b = "<!-- BEGIN USER-DEFINED: active_artifacts -->\n"
    act_e = "<!-- END USER-DEFINED: active_artifacts -->"
    clr_b = "<!-- BEGIN USER-DEFINED: cleared_artifacts -->\n"
    clr_e = "<!-- END USER-DEFINED: cleared_artifacts -->"
    a0, a1 = text.index(act_b) + len(act_b), text.index(act_e)
    active = [r for r in text[a0:a1].split("\n") if r.startswith("| ")]
    keep = [r for r in active if not any(r.startswith("| tickets/tasks/" + f + " |") for f in closed_files)]
    removed = len(active) - len(keep)
    c0, c1 = text.index(clr_b) + len(clr_b), text.index(clr_e)
    cleared = [r for r in text[c0:c1].split("\n") if r.startswith("| ")]
    fixed = 0
    for i, r in enumerate(cleared):
        for f in closed_files:
            if r.startswith("| tickets/tasks/" + f + " |"):
                cleared[i] = r.replace("| tickets/tasks/" + f + " |", "| tickets/tasks/completed/" + f + " |", 1)
                fixed += 1
    new = ["| tickets/tasks/completed/" + f + " | " + path + " | " + disp + " | " + reason + " | " + NOW + " |"
           for f, path, disp, reason in CLEARED]
    cleared = new + cleared
    text = (text[:a0] + "\n".join(keep) + "\n" + text[a1:c0] + "\n".join(cleared) + "\n" + text[c1:])
    if APPLY:
        b.write_bytes(text.encode("utf-8"))
    return removed, fixed, len(new)


def main():
    closed = {t[0] for t in T}
    closed_files = [t[1] for t in T]
    for pid in ARCHIVE:
        assert (ACTIVE_P / pid).is_dir() and not (DONE_P / pid).exists(), pid
    for item, name, summary, owed, _note in T:
        close_ticket(item, name, summary, owed)
        print("ticket ok", item)
    if APPLY:
        for pid in ARCHIVE:
            os.rename(ACTIVE_P / pid, DONE_P / pid)
    print("attention", sync_attention(closed)[:2])
    print("artifacts", sync_artifacts(closed_files))
    print("APPLIED" if APPLY else "DRY RUN")


main()
