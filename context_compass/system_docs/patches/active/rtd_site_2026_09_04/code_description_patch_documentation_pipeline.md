# Code Description Patch: Validated documentation assembly

## Trigger
Source assembly creates a validation gate and deletes/replaces generated directories; error ordering,
path containment, and repeatability require an explicit control-flow contract.

## Control Flow
1. Resolve repository/docs roots from the tool location and parse the known navigation file.
2. Validate level names/order, page IDs, parent references, and every declared source path.
3. Compute the intended page tree and contents from the same model; reject duplicates/missing inputs.
4. Resolve the generated source directory and prove it is an expected child of docs/_build.
5. Prepare fresh generated source, include/copy only selected canonical inputs, and write navigation.
6. Build with Sphinx using the known configuration and return its exact success/failure state.
7. Check generated navigation/source links and record the output location for visual review.

## Edge/Error and Rollback Behavior
An invalid manifest never causes cleanup. An output path escaping the generated root is refused.
Missing source paths are not replaced with placeholder content. A Sphinx failure keeps diagnostic
output and is reported as failure; it does not alter canonical sources or hosted state.

## Invariants and Idempotency
Stable IDs and sorting produce the same page tree from the same inputs. Rebuild removes stale generated
pages safely. There is one canonical page parent and all learning pages are reachable from contents.
Absolute local filesystem paths must not leak into published explanatory text or downloadable sources.

## Non-goals
No runtime execution of the complete example suite during rendering, hidden account actions, runtime
rewrites, or generic repository-wide file copying.

## Validation Focus
Invalid manifest/path cases must refuse before cleanup. Repeated generation must preserve content and
navigation. Real rendering must show the selected source code, diagram, and API signatures.
