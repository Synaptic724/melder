# Code Description Patch: Protocol Crafter Flow

## Generation Flow
1. Normalize target to class plus optional instance state.
2. Choose the protocol name by prefixing `I`.
3. Gather attributes from class annotations and, for object inputs, instance
   state.
4. Optionally gather inherited members from the MRO.
5. Gather methods and signatures, skipping dunder methods.
6. Mirror docstrings into generated class/method docstrings.
7. Emit a `@runtime_checkable` protocol block with `...` method bodies.

## Interface File Update Flow
1. Read the interface file text.
2. For add:
   - append the new protocol block cleanly
   - normalize trailing newlines
3. For remove:
   - locate the protocol block by name
   - remove the decorator + class block
   - normalize surrounding blank lines
