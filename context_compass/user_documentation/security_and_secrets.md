# Security and Secrets Policy

Purpose
- Protect user secrets and prevent accidental leakage into the repo.

Hard rule
- Secrets must never be written into context_compass/ or any repo file.
- This includes ctx/state/config/task artifacts and user documentation.
- This includes user/system memory stores under context_compass/memory/.

If a user requests storing secrets
- The agent must refuse the request.
- Provide safe alternatives and wait for confirmation.

What counts as a secret
- API keys, tokens, passwords, cookies, and private keys.
- Access URLs that embed credentials.
- Any value marked confidential by the user.

Approved alternatives
- Environment variables injected at runtime.
- OS keychain or secret manager (1Password, Keychain, Vault, etc.).
- CI/CD secret store or runtime injected config.
- Runtime-only prompts with no persistence and no logging.

Logging rules
- Do not print secrets to stdout/stderr.
- Do not echo secrets in summaries or examples.
- Mask secrets if they appear in user input.

Refusal text example
- "I can’t store secrets in this repo or in context_compass. Please provide the secret via a safe mechanism (env vars, secret manager, or runtime prompt)."
