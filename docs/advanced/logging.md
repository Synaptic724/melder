# Attach logging explicitly

Prerequisite: [configuration ownership](posture.md). Melder's root starts without
an attached raw logger. Use `md.Aether().attach_logger(logger)` to install one
after boot; passing `None` detaches it again.

The saved logging lesson uses a standard-library logger with a collecting handler.
It checks the public `aether.logger` after attachment, detachment, and
`enable_logging(logger)`, then removes and closes the demonstration's handler.

## Two enablement paths

An explicit logger passed to `enable_logging` uses the attachment path. Calling
`enable_logging()` without one instead requires the automatic logger policy and
provider setup. Do not assume creating an `AetherConfiguration` enabled that path;
follow the root-configuration lesson's activation sequence.

Own the lifetime of application logging resources explicitly. Root logger
attachment and provider configuration are separate choices; installing one sink
does not by itself describe the policy of every object already in the process.
