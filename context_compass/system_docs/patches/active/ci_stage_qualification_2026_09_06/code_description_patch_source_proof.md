# Code-description patch: full-CI evidence selection and consumption

## Recording
Record only full PR/manual profiles after the exact dependency set succeeds. Require actual HEAD
to match GITHUB_SHA and no tracked checkout modifications. Store actual checkout/tree IDs plus
repository, run/attempt, event, target branch, PR number and head/base IDs. Upload under a name
containing the run ID and attempt; failed recording/upload prevents overall CI success.

## Selecting source evidence
Read current event and checkout identity. A preprod-to-RC PR requires its merge tree to equal the
preprod head tree. For RC push/manual qualification, resolve the current candidate's merged PR.
An unchanged preprod promotion follows the preprod head; a release-fix merge uses that PR's full CI.
An exact-commit manual CI run on the expected branch can provide fresh qualification.

Resolve merged-PR identity through GitHub's commit association and require the exact merge SHA,
base branch, same repository and permitted route. Select CI runs by immutable head SHA, event and
head branch; verify the PR number in the downloaded record because historical run.pull_requests may
be empty. Exact manual branch runs are also supported. Never fall back past a newer failure or
different-PR record; establish fresh manual qualification when history cannot prove this merge.
Require complete success, expected repository/workflow/event/head, and one current non-expired artifact.
Pagination must not silently omit newer or ambiguous evidence.

## Download and verify
Write a bounded selection record and action outputs. The official download action retrieves only
the named artifact from the selected run with read-only Actions access. Verify the JSON schema,
full qualification flags, event/PR/run/attempt fields and exact tree. Refresh selection to reject
a changed attempt/newer applicable run during download. Never execute artifact contents.

## Pending candidate
The prod source check may wait for queued/in-progress qualification with an explicit finite bound.
Check identity before waiting. Completed failures and forged/mismatched metadata do not wait.
Keep zero-wait defaults at final publication; no automatic upload or consumer-test retries.

## Failure behavior
Missing or expired proof requires new full CI on the intended branch. Changed merge contents require
qualification of those contents. No artifact presence alone or successful light run is sufficient.
