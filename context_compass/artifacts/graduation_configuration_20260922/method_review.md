# Private Spellbook conjure method: source review

## Delivered slice
Spellbook._conjure_existing_conduit is implemented in spellbook.py. It is a separate private route;
normal public conjure and the public upgrade caller have not been changed.

Input is an existing live normal, detached, unregistered conduit, with caller-owned normal-root
preparation complete. The receiving Book already exists and therefore uses ordinary configuration
selection. The private route does not construct a Conduit, promote its status or copy old bindings.

It admits the receiving Book's CONJURE transaction, validates configuration/identity/policy, runs
normal phases using the supplied ID, installs Book/Meld references and selected hooks, registers the
root and runs the existing activation/publication tail. It preserves creation stores and rebases
retained local Space doors; old input and fast-door lookup caches are cleared.

The existing gate is temporarily parked only for attachment, and its prior admission state is
restored before activation hooks. Frame locking covers root publication, not recorder callbacks.
Shared frozen configuration still emits the new Book's own twin through origin-bearing freeze.

## Qualification
- 39 direct method cases pass across local and frame-wide configuration.
- Final combined selection: 389 passed in 16.25 seconds, zero failures/errors/skips.
- New test files pass Ruff with the repository's Optional/Union policy respected.
- Source fatal lint passes.
- Compared 592 src Python files: only spellbook.py changed; none were added. Build assets unchanged.

Evidence:
- method_final.xml and method_final.log
- method_tests_lint.log and method_fatal_lint.log
- method_source_changes.json

One fixture correction was necessary: the shared regression classes inherited cleanup, while the
binding profiler records methods declared on the concrete class. ParentService/GraduatedService now
declare cleanup explicitly, and disposal tests assert successful bind-time matching before teardown.
No runtime disposal logic changed.

## Explicit boundaries
- Public upgrade_to_normal integration is the next slice. The earlier red upgrade tests still
  target that unchanged public path; a final run confirms all 32 remain red, with corrected disposal
  admission in the shared fixture. This delivery does not claim they are green.
- Configuration-provided Bind defaults and default Conduit/Meld event APIs are not implemented yet.
- The private caller must quiesce foreign-thread managed Spaces and concurrent scope acquisition.
  Those thread-local stacks cannot be enumerated by this thread. Current-thread managed, manual
  registered and idle pooled Spaces are covered by direct tests.
- Preflight/configuration/phase failures precede ownership replacement. Post-attachment publication
  failures keep normal conjure's caller-owned cleanup semantics; callback effects are not transactional.
- No generators, wheel build, publication or normal meld hot-path changes.
