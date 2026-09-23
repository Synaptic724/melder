# Bool-gated hook restoration

## Call flow
1. At normal-root construction/adoption, copy configuration dictionaries and inner callback lists.
   Keep each resulting dictionary identity for that root's lifetime, even when empty.
2. Meld initialization sets baseline=effective and modified=False. Space initialization inherits the
   owner's baseline and effective references and sets modified from their identity difference.
3. Rare registration normalizes and validates every callback outside publication locks. Under the
   existing mutation lock, local updates allocate independent lists/maps and set modified=True;
   shared root updates modify baseline contents and select that baseline with modified=False.
4. Existing internal set-by-reference does not broadcast; it marks a non-baseline reference modified.
   A separate trusted baseline-bind method resets both references for initialization/graduation.
5. At return, creations dispose using current state. If modified is true, restore the baseline and
   clear the bool under the existing Meld lock. Publish to idle storage afterward.
   Prewarming also restores temporary hooks before its direct idle publication; it does not run
   through ordinary scope cleanup, so that cold path must uphold the same idle-state invariant.
6. At Space acquisition, if the owner is modified, capture its current effective reference and
   baseline; compare identities to avoid treating an inherited temporary map as unchanged.
   If the owner is unmodified, the returned Space already points to the stable baseline.

## Threading and errors
Managed Space lifecycle retains its thread-confinement contract. Local hook mutation must complete
before handing that scope back; external mutation of an idle/returned scope is unsupported. Root-shared
updates may occur independently because inherited maps keep stable identity. No reader lock, extra
holder dereference, revision polling, map copy or hierarchy walk is added to ordinary meld execution.

Invalid batches change no family. Callback return/error policy remains unchanged. Sharing/installation
are different operations: reset and graduation must never publish into the former owner's dictionary.
Callable objects remain borrowed; terminal cleanup retires containers and subordinate Meld state.
Local copying snapshots the source dictionary on the rare mutation path because a different root
writer can change its entries concurrently. Inner event lists are copied for local ownership. Empty
event lists are omitted so clearing preserves the existing no-hooks fast-door guard.
