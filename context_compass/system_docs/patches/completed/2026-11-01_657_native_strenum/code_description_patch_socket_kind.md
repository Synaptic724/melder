# Socket numeric-code projection

<!-- BEGIN ENTRY: "Keep compiler rows numeric after StrEnum conversion" -->
## Ordering and fallback
The enum helper returns the original integer for each actual SocketKind by identity;
for any other object it reads that object's .value as the former consumer did.
Phase 5 keeps its existing None and AttributeError-to-repr handling. Other readers
continue to propagate their prior attribute failures. No type, ordering or cache
policy changes are introduced.

## Tests
Pin phase 5, override, topology and site-parameter rows as integers, including
foreign value objects and Phase 5 repr fallback; exercise real unresolved-input and
cache paths. Test old numeric constructor inputs and captured protocol-4 pickles.
<!-- END ENTRY: "Keep compiler rows numeric after StrEnum conversion" -->
