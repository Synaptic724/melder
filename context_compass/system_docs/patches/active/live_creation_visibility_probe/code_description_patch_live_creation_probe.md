# Code Description Patch: Live Creation Probe

1. Caller asks `Conduit.has_live_creation(...)`.
2. `Conduit` delegates to `Meld`.
3. `Meld` resolves the target spell with the same lookup path used by `meld(...)`.
4. `Meld` inspects current live runtime storage only and builds one status payload.
5. `Meld.has_live_creation(...)` returns `status["is_live"]`.
6. `Conduit` facades both the bool and richer status methods.
7. No object creation or registration occurs anywhere in this flow.
