# Named discovery CI fixture repair

Both user-supplied CI logs report the same two failures on Linux and macOS:

- test_nexus.py::test_codegen_command_system_can_delegate_selected_runtime_helpers
- test_rift_runtime_contracts.py::test_capability_rift_spaces_expose_conduit_discovery_through_command_system

The shared named lookup resolves the authorized published ID and checks that the live Conduit
still carries the requested name. This protects against scope reuse between selection and lookup.
Both legacy test doubles omitted the Conduit.name contract, producing AttributeError at that check.

Reproduced both errors locally before editing. Updated only the doubles and their test contracts:
the codegen fixture now supplies name="root", and the capability fixture supplies name="alpha".
No runtime guard, API, lifecycle behavior or release version changed.

Validation:

- before.log / before.xml: 2 failed, reproducing both supplied errors.
- after.log / after.xml: 201 passed, with no failures or skips.
- Selection: both complete failing modules, named-lesser Nexus command integration tests, and
  named-lesser Nexus lifecycle component tests. Covers authorized root/lesser lookup, same-ID
  reuse, replacement-ID races, ACL denial, promotion, retirement and cleanup.
- Changed code read back; scoped whitespace check passes.
- Full repository suite and coverage: not run. The unrelated full-CI coroutine warning is not
  part of these two failures and did not occur in this selection.

All source and tracking changes are completed before the direct final package/LLM asset builders
and currentness checks. Per owner instruction, asset-only rebuilds create no task and no file
edits follow successful generation/checking. Final build outcomes are reported in command output.
