# Public upgrade preparation and failure recovery

<!-- BEGIN ENTRY: "Upgrade to normal call path" -->
## Control flow
1. Under the target lock, validate live dynamic lesser status, attached lineage, no children, unique
   nonempty root name and callback payload. Reject non-configuration values and a borrowed local config.
2. Capture the original gate posture and temporarily drain it outside structural locks.
3. Lock the former parent ward, then the target; recheck admission. Construct a new same-frame Book
   through ordinary configuration selection and validate its selected policy.
4. Prepare independent normal pool/cluster resources and normal status; preserve the creation store.
   Ward conversion removes the old parent entry and makes the target its own root. Reindex its gate.
5. Release structural locks and invoke the separate Spellbook._conjure_existing_conduit method with
   the same target, name and original gate posture. No old resolution state is copied.
6. The Book route runs normal configuration/phases, attaches lookup owners and configured hooks,
   rebinds retained local Space runtimes and publishes the root. On successful attachment it restores
   original admission before invoking the ordinary activation/publication tail.
7. Apply explicit local runtime hooks after conjure returns. The public API returns None.

## Recovery boundary
The target's Book reference is the attachment marker. If it still points to the old Book, restore the
old parent/root/policy/name, clean the new pool/cluster facade and ward identity, and reindex the gate
under its original root. Drop failed new-root resolution state and clean the failed Book. Finally
restore original admission. A previously parked gate remains parked on both success and failure.

When the public caller supplied the original admission posture, the private route leaves the gate
parked on pre-attachment failure so rollback finishes before waiters resume. Standalone private-route
callers retain their previous admission restoration behavior.

After attachment, the new Book and normal root retain cleanup responsibility if publication fails;
the public path must not clean the former Book or pretend that arbitrary callback effects were undone.
Callbacks that attempt structural Bind while normal CONJURE claims are held follow the existing
transaction admission behavior. Bind after upgrade returns; no recursive registration bypass added.

## Scope boundaries
No parent definition inheritance, creation transfer, new object construction policy, pool hook-reset
redesign, callback persistence or ordinary Meld execution changes. Configuration setup additions
also apply to ordinary Books. Source, tests and patch documents only until owner asset approval.
<!-- END ENTRY: "Upgrade to normal call path" -->
