# Validation record — 2026-10-28

## Automated checks

The suite contains 23 Python unittest cases using temporary homes, dummy keys,
mocked gateway responses and mocked tmux observations. It covers engine selection,
project isolation, private credential permissions and symlinks, enrollment,
provider routing, immutable worker identity, tmux targeting, usage redaction,
SSH connection reuse without a fresh transport, resolved executable access, and
scoped Slurm log-directory grants. The SSH template is checked with `ssh -G`.
Run from the repository root:

```sh
python3 -m unittest discover -s tests -v
```

The earlier 21-case suite also passed on iFarm with Python 3.9.25. Later fixes
were tested locally and exercised in the authorized live Codex session below.
The unit suite does not authenticate, spend model tokens, or submit Slurm jobs.

## Live Codex acceptance

A separate authorized deployment on iFarm used tmux 3.2a, Codex CLI 0.162.1 and
JLab LiteLLM model `azure/gpt-6-sol`. Private key enrollment, model listing, actual
inference, the worker's shell tools, canonical workspace access, SSSD lookup,
read-only scheduler access, and durable ownership acknowledgement were verified.
The key-info route returned HTTP 403; remaining budget was therefore unavailable
through that route. Model listing alone does not establish inference readiness.

Live checks exposed and resolved these issues:

- Standalone Codex installs need read access to their resolved executable directory.
- Tmux window options need a session/window target with a trailing colon.
- Codex 0.162.1 uses `codex sandbox -P worker ...`, without a `linux` subcommand.
- Restricted workers cannot inspect the host's tmux/process namespace; the
  coordinator must independently check existing ownership over SSH.
- Large pasted tasks need verified submission, not merely successful `send-keys`.
- Slurm requires literal `/farm_out/` output paths, while this worker sandbox
  exposes the resolved log directory for filesystem operations.

After narrowly scoped log access and a safe same-conversation resume, the actual
worker passed log create/read/delete checks and submitted jobs with compliant
stdout/stderr paths. Completed diagnostic and targeted replay jobs demonstrated
submission and collection. A dedicated task log container with unique child
folders then allowed subsequent jobs without another permission change or restart.
See [Slurm log guidance](JLAB_SLURM_LOGS.md).

These checks establish infrastructure behavior for that deployment, not completion
or correctness of the scientific task. Private job receipts, runtime identities,
research data and credentials remain outside this shared repository.

## Remaining acceptance per installation

Each user must verify pinned SSH authentication and connection reuse, their own
project entitlement, executable paths, worker permissions and task ownership.
Mocked tests and a prior user's live run cannot certify a different installation.
Claude Code and its JLab Messages endpoint have not received live acceptance here.
NERSC integration remains a documented plan, not a deployed feature. Follow
[the acceptance procedure](ACCEPTANCE.md) before relying on either path.
