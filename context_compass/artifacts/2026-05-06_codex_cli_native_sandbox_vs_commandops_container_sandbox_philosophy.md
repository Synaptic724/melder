# Codex CLI Native Sandbox Vs CommandOps Container Sandbox Philosophy

## Metadata
- Artifact ID: ART-2026-05-06-codex-cli-native-sandbox-vs-commandops-container-sandbox-philosophy
- Parent Epic: EPIC-2026-05-03-general-open-questions
- Status: active
- Created: 2026-05-06T10:27:13Z
- Updated: 2026-05-06T10:27:13Z

## Purpose
Capture the practical design difference between:
- how Codex CLI implements local sandboxing today
- how the planned CommandOps sandbox direction should work

This artifact exists to stop a bad comparison from hardening:
- "their sandbox" vs "our sandbox"

That framing is too vague.

The real comparison is:
- native host-process sandboxing
vs
- container/pod worker sandboxing with an inner process-policy layer

This artifact keeps that distinction durable so later CommandOps work does not
copy the wrong abstraction just because Codex is successful.

## Why This Matters
The planned larger project needs protected execution surfaces around agents.
Rift should remain a mediated capability surface into Melder, not a place where
arbitrary agent code gets raw reach into the runtime.

That means the sandbox decision matters structurally:
- what is the first hard boundary?
- what sits outside the boundary?
- what authority is still mediated after code starts running?
- what deployment path works for general users versus business and enterprise?

If we do not name those differences clearly, we risk:
- copying host-native techniques when the product wants container-native ones
- overfitting to Codex local behavior even though our deployment story is different
- blurring "what Codex source actually does" with "what we should choose"

## Relationship To The AR / Codegen Capability Philosophy
This artifact is not a replacement for the older AR/codegen capability-surface
philosophy.

The relationship is:
- `2026-04-26_ar_codegen_capability_surface_philosophy.md`
  - explains why AR/Rift/codegen are mediated capability surfaces over Melder
- this artifact
  - explains where less-trusted agent execution should live relative to those
    capability surfaces

Another way to say it:
- the AR/codegen philosophy explains what the agent can do in the world
- this sandbox philosophy explains where the risky execution boundary should
  sit so those capabilities stay protected

This means the two artifacts should be read together when designing later
CommandOps execution backends:
- capability philosophy first
- sandbox/deployment philosophy second

## Observed Codex CLI Design (Source-Backed Facts)

### 1. The maintained CLI is Rust
The maintained CLI is the Rust implementation, not the old TypeScript CLI.

That matters because the local sandbox behavior is implemented in native Rust
crates rather than delegated to Docker or another external container runtime.

Source anchors:
- `<local-path>/Downloads/codex-main/codex-rs/README.md`
- `<local-path>/Downloads/codex-main/codex-rs/Cargo.toml`

### 2. Local sandboxing is backend-per-OS
Codex local does not have one universal Docker-style sandbox layer.
It has platform-specific sandbox backends.

Observed crates:
- Linux:
  - `codex-rs/linux-sandbox`
- Windows:
  - `codex-rs/windows-sandbox-rs`

Source anchors:
- `<local-path>/Downloads/codex-main/codex-rs/linux-sandbox/README.md`
- `<local-path>/Downloads/codex-main/codex-rs/windows-sandbox-rs/Cargo.toml`

### 3. Linux local sandbox is bubblewrap-first
On Linux, the source says Codex prefers bubblewrap and uses native Linux
sandboxing primitives around it.

Observed behavior:
- bubblewrap is the default filesystem sandbox
- seccomp network filter is applied
- user namespace isolation is used
- pid namespace isolation is used
- network namespace isolation is used when needed
- a legacy Landlock path exists as fallback

This is not container-first.
It is a restricted host-process model.

Source anchors:
- `<local-path>/Downloads/codex-main/codex-rs/linux-sandbox/README.md`

### 4. Windows local sandbox is a native restricted-process model
The Windows source tree is not a thin wrapper.
It is a substantial native sandbox implementation.

Observed ingredients from the source:
- restricted token creation
- sandbox users / credentials
- path ACL allow/deny logic
- workspace capability SIDs
- `CreateProcessAsUserW`
- firewall and WFP setup
- optional private desktop isolation
- job-object related Win32 dependencies in the crate

This is again not container-first.
It is a restricted host-process design using Windows-native security and
process primitives.

Source anchors:
- `<local-path>/Downloads/codex-main/codex-rs/windows-sandbox-rs/src/lib.rs`
- `<local-path>/Downloads/codex-main/codex-rs/windows-sandbox-rs/src/process.rs`
- `<local-path>/Downloads/codex-main/codex-rs/windows-sandbox-rs/src/identity.rs`
- `<local-path>/Downloads/codex-main/codex-rs/windows-sandbox-rs/src/token.rs`
- `<local-path>/Downloads/codex-main/codex-rs/windows-sandbox-rs/src/firewall.rs`
- `<local-path>/Downloads/codex-main/codex-rs/windows-sandbox-rs/Cargo.toml`

### 5. Codex also has per-exec mediation, not only a boundary
Codex local does not only "run inside a sandbox."
It also has a shell-escalation protocol for command execution on Unix.

Observed behavior from the docs:
- `Run`
  - keep the command inside the sandboxed shell
- `Escalate`
  - let the command run outside the sandbox faithfully
- `Deny`
  - block it

This is important.
Codex local is not only a hard boundary.
It is also a per-command policy system.

Source anchors:
- `<local-path>/Downloads/codex-main/codex-rs/shell-escalation/README.md`

## The Core Nature Of Codex Local
Codex local is best understood as:

- a native local agent runtime
- with OS-native sandbox backends
- plus per-command mediation/escalation logic

Its first hard boundary is:
- the sandboxed local process

That is the key design fact.

## What Codex Local Is Not
It is not:
- Docker-first local sandboxing
- Kubernetes-first sandboxing
- "just run code in a container"

It is process-first sandboxing.

That is a valid design for a local CLI/app because:
- it avoids requiring a container runtime
- it can mediate ordinary local shell commands directly
- it uses host-native security primitives

## Planned CommandOps Direction
The planned CommandOps direction is different on purpose.

The intended first hard boundary is not:
- a restricted host process

It is:
- a disposable worker container/pod

The design target is:
- general users
  - Docker Compose
- business / lightweight cluster
  - K3s
- enterprise / broader clustered environments
  - Kubernetes

That means the sandbox design is:
- container-first
- deployment-tier aware
- not dependent on OS-native host-process sandboxing as the primary primitive

## Why This Direction Is Reasonable
The larger project is not trying to clone Codex local.
It is building a different execution world.

For this project, the more natural primitive is:
- sandbox the worker environment

not:
- sandbox one local host process

That fits the intended deployment story better:
- Docker Compose for ordinary users
- K3s/Kubernetes for scaled or managed environments

It also fits the planned CommandOps position better:
- execution backends are part of orchestration architecture
- agent code can be treated as disposable worker execution
- Rift/Melder capability mediation can remain outside the raw code runner

## The First Hard Boundary Difference

### Codex local
First boundary:
- sandboxed local process

Meaning:
- command starts on the host
- Codex constrains the host process using OS-native primitives

### Planned CommandOps
First boundary:
- worker container or pod

Meaning:
- code runs inside a disposable contained worker
- filesystem/network/resources are constrained at the worker boundary first

This is the most important design difference.

## What The Planned Model Should Still Copy
We should not copy Codex's primitive, but we should copy several of its ideas.

### 1. Per-command mediation still matters
Even inside a container, we should still have an inner process-policy layer.

That means:
- allow / deny command policy
- explicit timeout handling
- stdout/stderr capture
- audit trail
- explicit escalation semantics when a command wants something outside policy

So the right model is:
- outer container/pod boundary
- inner process-policy runner

not:
- container only and nothing else

### 2. Policy should be explicit, not accidental
Codex source clearly separates:
- sandbox backend
- policy
- escalation path

We should do the same.

### 3. Silent no-op behavior is bad
One of the main lessons from the logger work also applies here:
- if a protection path depends on config/policy and it is not enabled,
  the system should fail fast rather than silently acting weaker than intended

## What The Planned Model Does Not Need To Copy

### 1. Host-native token and ACL surgery
If execution is already entirely inside a worker container, we do not need to
reproduce Windows restricted-token behavior or host-path ACL surgery to get the
main effect we care about.

Codex needs that because it is sandboxing host-local processes directly.

We are planning to sandbox workers.

### 2. Host-native firewall identity semantics
If the worker is already network-disabled or policy-routed at the container/pod
level, we do not need to reproduce the exact Windows firewall/WFP-per-identity
shape that Codex local uses.

### 3. Bubblewrap itself
Bubblewrap is solving the local Linux host-process problem.
That does not mean we should import bubblewrap into a container-first design.

## What The Planned Model Must Still Solve Explicitly
Container-first does not solve everything by itself.

The planned model still needs these explicit layers:

### Outer sandbox boundary
- container or pod isolation
- narrow mounts
- network off by default unless explicitly allowed
- read-only root where practical
- non-root execution
- resource limits
- disposable worker lifecycle

### Inner process-policy layer
- command allow/deny rules
- timeout / kill behavior
- env scrubbing
- cwd policy
- output capture
- audit trail

### Capability mediation layer
- agent does not get raw privileged runtime access by default
- privileged Melder/Rift mutation remains mediated
- ACL and capability checks live above raw command execution

### Content/pattern policy
- secret scanning
- regex or rule-based command rejection where useful
- import/module allow/deny policy where applicable

## Deployment Tiers

### General-user path
Use Docker Compose.

Why:
- simpler local install story
- one-machine self-hosting
- realistic for ordinary users
- enough isolation for the practical threat model

### Business path
Use K3s.

Why:
- lightweight cluster story
- closer to managed worker orchestration
- keeps the same conceptual sandbox backend with a stronger control plane

### Enterprise path
Use Kubernetes.

Why:
- richer policy/control-plane model
- better for multi-node and organizational deployment
- same broad container/pod execution model as K3s, just heavier and richer

## Practical Threat Model Difference
This is the cleanest way to think about it.

### Codex local optimizes for
- local CLI/app execution
- ordinary host shell mediation
- OS-native command sandboxing

### Planned CommandOps sandbox should optimize for
- worker isolation
- deployment portability
- general-user to enterprise upgrade path
- keeping agent code away from privileged runtime surfaces

Those are not the same optimization targets.

That is why the primitive should differ.

## The Real Equivalence
The right question is not:
- can we reproduce every native Codex trick exactly?

The right question is:
- can we produce an equivalent or better practical containment model for our
  worker architecture?

For the planned CommandOps direction, the answer is:
- yes

if we combine:
- outer container/pod isolation
- inner process-policy mediation
- capability ACLs outside the worker
- explicit deployment-tier backends

## Best Design Summary
Codex local:
- native local process sandbox
- OS-specific backends
- per-exec mediation

Planned CommandOps:
- disposable worker sandbox
- Compose for general users
- K3s/Kubernetes for business and enterprise
- inner process-policy runner inside the worker
- mediated Rift/Melder capability boundary outside the worker

That is not an inferior design.
It is a different design optimized for a different execution model.

## Source Anchors
- `<local-path>/Downloads/codex-main/codex-rs/README.md`
- `<local-path>/Downloads/codex-main/codex-rs/linux-sandbox/README.md`
- `<local-path>/Downloads/codex-main/codex-rs/shell-escalation/README.md`
- `<local-path>/Downloads/codex-main/codex-rs/windows-sandbox-rs/Cargo.toml`
- `<local-path>/Downloads/codex-main/codex-rs/windows-sandbox-rs/src/lib.rs`
- `<local-path>/Downloads/codex-main/codex-rs/windows-sandbox-rs/src/process.rs`
- `<local-path>/Downloads/codex-main/codex-rs/windows-sandbox-rs/src/identity.rs`
- `<local-path>/Downloads/codex-main/codex-rs/windows-sandbox-rs/src/token.rs`
- `<local-path>/Downloads/codex-main/codex-rs/windows-sandbox-rs/src/firewall.rs`
- `codex/context_compass/artifacts/2026-04-26_ar_codegen_capability_surface_philosophy.md`

## Current Best Summary
Codex local is native process sandboxing.

The planned CommandOps direction should be container/pod worker sandboxing.

The design goal is not to imitate Codex's host-native primitive exactly.
The design goal is to achieve strong worker containment and mediated runtime
protection in a form that scales from:
- Docker Compose
- to K3s
- to Kubernetes

That is the right comparison, and that is the right direction.
