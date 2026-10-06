# CI/CD guide for agents

Read this folder before you change anything under `.github/`, change `project.requires-python` or Melder's
dependencies in `pyproject.toml`, add a Python release, a CI job or a benchmark, or diagnose a failed run. It says
what every CI file is for, how the pieces connect, how to extend them and how to check a change before handing it
off. Branch and release policy (which pull request may target which branch, cutting a release, the TestPyPI and
PyPI credentials) lives in [BRANCH_WORKFLOW.md](../BRANCH_WORKFLOW.md); this folder links to it instead of
repeating it.

| Read | When |
| --- | --- |
| [workflows.md](workflows.md) | You need to know what a workflow or job does, who calls it, or why it ran or was skipped. |
| [scripts.md](scripts.md) | You are reading or changing a script in `.github/scripts/`, a ruleset or another `.github` file. |
| [python_versions.md](python_versions.md) | You are adding or retiring a Python release, changing a pin, adding a dependency or moving the speed tests. |
| [extending.md](extending.md) | You are adding a job, a workflow, a benchmark or a script, or changing what a route requires. |
| [validating.md](validating.md) | You are about to hand off a CI change, or you are reading a failed run. |

## How CI fits together

Three workflows start runs. Every other workflow is reusable (`on: workflow_call`): it proves one thing, the entry
workflows call it, and it can also be started by hand from the Actions tab.

```text
pull request into dev, preprod, release_candidate or prod, or a manual run  -->  ci.yml
  branch-policy         refuses an invalid route, decides what this PR must run (ci_policy.py branch)
  hygiene               every time
  source-assets, repo-assets, tests, documentation      when the route needs the full checks
  real-world-gauntlet, persistent-runtime-gauntlet,
  shallow-all-thread-scaling                            only for a dev -> preprod PR
  packages              full checks outside dev
  source-qualification  only for a preprod -> release_candidate PR
  merge-ready           the one required status, "CI / merge-ready" (ci_policy.py merge-ready)

push to release_candidate, or a manual run there  -->  release-candidate.yml
  authorize -> source-qualification -> build -> publish (TestPyPI)
  -> install (every test-manifest release on Linux, Windows and macOS) -> package-ready

published release, or a manual run on prod  -->  python-publish.yml
  release-gate -> hygiene, source-assets, repo-assets, tests -> release-build -> pypi-publish
```

Workflows only orchestrate. The decisions (routes, required results, Python matrices, installs, package checks)
live in standard-library Python scripts in `.github/scripts/`, each tested in `tests/unit/github_workflows/`. The
Python releases CI may use are data: one manifest per release in `.github/python/`.

## Rules every agent follows

1. CI runs only the Python releases a manifest names ([python_versions.md](python_versions.md)). Never add
   `check-latest`, a `python-version-file`, a pre-release or a floating version such as `"3.14"`.
2. `CI / merge-ready` is the only required status. A job that must pass goes into `merge-ready`'s `needs` in
   `ci.yml` and into `CIPolicy` in `ci_policy.py` in the same change ([extending.md](extending.md)).
3. Logic goes in a script with a test, not in YAML. Scripts stay standard-library only: CI runs them before
   anything is installed.
4. Check every CI change locally ([validating.md](validating.md)). Hosted runs belong to the owner: report them as
   "Not run" until you have seen their result.
5. Keep this folder current in the change that changes CI. A contract test fails when a workflow, script or
   ruleset has no entry here, or when a link in this folder points at nothing.
6. Run the build-asset runner and the llm_support builder last, each with `--check`; new files must be tracked
   before CI's check passes, so tell the owner to commit with `git add -A`.
