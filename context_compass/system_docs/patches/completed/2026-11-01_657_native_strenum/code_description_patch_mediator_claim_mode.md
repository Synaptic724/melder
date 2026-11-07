# Aetheric claim-mode projection

<!-- BEGIN ENTRY: "Keep claim evidence and request wire tokens" -->
## Flow
Enum lookup first accepts exact member-name values; its missing-value hook maps
only old x/s/ix strings to the original members. A member projection yields its
historical short code. Request build, blocking evidence and table snapshots call
that projection; request claim_map uses the legacy reader to reconstruct members.

## Contract
Unknown values keep raising ValueError. Typed request/compatibility boundaries do
not accept raw strings or foreign enum members. The admission matrix and locks are
unchanged. Test actual output strings, old pickle payloads and conflicting claims.
<!-- END ENTRY: "Keep claim evidence and request wire tokens" -->
