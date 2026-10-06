# Validating a CI change

## Before you hand off

1. Run the workflow tests from the repository root in the development environment (`uv sync --locked --python
   3.14t`, see CONTRIBUTING.md):

   ```bash
   uv run --locked python -X gil=0 -m pytest tests/unit/github_workflows -q
   ```

   They parse every workflow and exercise every script without network access or GitHub.
2. Prove a new rule bites: break it on purpose (drop the step, change the flag), confirm the test you wrote fails,
   then restore the file exactly.
3. When you change how something installs, try it in a scratch copy outside the repository: build a test cell's
   environment from its manifest with the commands in [python_versions.md](python_versions.md) and run
   `pytest --collect-only` in it, or run `python_runtime_matrix.py speed-install --results <scratch folder>` with
   a free-threaded interpreter that has pip.
4. Rebuild the generated files last, after every other edit:
   `python src/melder/_build_assets/_build_asset_runner.py` and then the same command with `--check` (CI's
   `source-assets` job), and `python llm_support/_builder.py` and then `--check` (CI's `repo-assets` job). The LLM
   builder reads the tracked files, so while new files are untracked run both of its commands with
   `--include-untracked` and tell the owner to commit with `git add -A`; otherwise CI's check fails.
5. Report what ran and what did not. Hosted runs, the Windows and macOS runners, secrets and the GitHub API cannot
   be exercised locally: report them as "Not run" until the owner shares the result.

## Reading a failed run

Start with `CI / merge-ready`: its message lists every required job that did not succeed. Then open that job.

| Symptom | Usual cause and fix |
| --- | --- |
| `branch-policy`: "Promotion into ... requires ..." | The pull request skips a promotion step or comes from a fork. Retarget it. |
| `merge-ready`: "Incomplete CI dependency evidence" | `merge-ready`'s `needs` and `CIPolicy` disagree ([extending.md](extending.md)). |
| `repo-assets` or `source-assets`: stale | Rebuild with the command the job prints and commit the result, new files included. |
| `discover`: a manifest is refused | The message names the file and the rule; fix the manifest ([python_versions.md](python_versions.md)). |
| A test cell fails to install | A pin has no wheel for that release or runner; change the pin in that manifest. |
| A speed test fails in its install step | A benchmark library has no free-threaded wheel on that runner: pin another version or list it under `build_from_source`. Read `install.log` in the results artifact. |
| A speed test's inline step fails with "No module named 'benchmarks'" | The step imports `benchmarks` before putting the checkout on `sys.path`; add `sys.path.insert(0, str(Path.cwd()))` above the import ([extending.md](extending.md)). |
| `source-qualification` refused | No full CI run tested this exact tree. Run CI by hand on the branch (BRANCH_WORKFLOW.md, "Reusing full qualification"). |
| `RC / publish-to-TestPyPI`: HTTP 503 or another 5xx from TestPyPI after six tries | TestPyPI is down. When it answers again, use **Re-run failed jobs**; the run's build is reused. |
| An RC job: "Artifact not found for name: candidate-dists-<run>-<n>" | A failed-jobs re-run of a run that started before the build reported its artifact (2026-10-06); use **Re-run all jobs**. |
| `Publish to PyPI`: "Use Re-run all jobs: this attempt did not build the distributions" | A failed-jobs re-run of the upload; publication never reuses an earlier attempt's build. Use **Re-run all jobs**. |
| Prod pull request: "Candidate qualification has not passed" | The release-candidate run for that commit is pending or failed; finish or fix it, then rerun the check. |
| The Codecov upload fails | Reporting only: it never blocks a merge. |

Artifacts worth opening: `runtime-results-*` (JUnit) and `coverage-*` for each test cell,
`runtime-python-matrix-*` (the releases a run tested), the speed tests' results folders (logs, `install.log`,
`environment.json`), `source-qualification-*`, and the release candidate's `candidate-*` reports.

## Environment notes for agents

- In a Windows checkout the workflow files may have CRLF line endings, mixed in places. Keep each file's endings
  when you edit it; the system documents under `context_compass/system_docs/` must stay LF.
- Some agent sandboxes cannot delete files in the checkout. There, a git command that refreshes the index can
  leave `.git/index.lock` behind and block the owner's commits: run only read-only git, with
  `GIT_OPTIONAL_LOCKS=0`.
