# Robots: JLab remote AI workers

A local coordinator controls project-funded AI workers on a pinned iFarm host.
**Codex is the default. Claude Code is opt-in with `--engine claude`.**
Each user installs their own FemtoMind/QuantOm virtual keys; the repository has
no credentials. Codex has been exercised on iFarm; Claude and NERSC paths still
require their own acceptance checks. See [validation](docs/VALIDATION.md).

```text
Laptop coordinator -- reusable SSH --> pinned iFarm host
                                      tmux worker (Codex or Claude Code)
                                       | JLab LiteLLM, selected project key
                                       | Slurm / authenticated SSH to NERSC
```

The key's administrator-assigned team determines billing. A filename or worker
tag cannot move spending between projects. Worker type and funding are separate:
`femtomind + codex`, `femtomind + claude`, and the equivalent QuantOm combinations
use the same interface. There is no automatic fallback to another key or provider.

For NERSC, see [the two deployment paths](docs/NERSC.md). The recommended first
integration keeps the AI worker on iFarm and uses SSH for NERSC job control.
NERSC-hosted workers need a verified JLab API route and a separate site profile.

## Install

Requirements: Python 3.9+, OpenSSH locally; Python 3.9+, tmux with multi-argument
`new-session` support, and the selected AI CLI on the Linux remote host. Install
Codex/Claude through your approved site process; this repository doesn't download
executables. Its Codex configuration targets the permission-profile format used
by the existing iFarm Codex 0.162.1 setup. Check compatibility before upgrading.
Claude flags follow the current official docs; the installed iFarm version and
JLab Messages endpoint still need a real acceptance test.

Clone this repository on your laptop and chosen remote host:

```sh
git clone https://github.com/JeffersonLab/robots.git
cd robots
```

On each machine, from the checkout:

```sh
mkdir -p "$HOME/.local/bin"
# Check for an existing file first; don't overwrite another installation.
test ! -e "$HOME/.local/bin/jlab-workers" && install -m 700 bin/jlab-workers "$HOME/.local/bin/jlab-workers"
```

On the remote host only:

```sh
~/.local/bin/jlab-workers init
```

Review `~/.jlab-workers/config.json`: pinned hosts, absolute executable paths, and
exact model IDs available to your key. `models.codex` starts as `azure/gpt-6-sol`
for compatibility with the current workflow; verify availability. `models.claude`
is deliberately null until an allowed Claude model is selected. Initialization
refuses to overwrite an existing configuration.

In your own interactive remote terminal, install the **administrator-issued** key:

```sh
~/.local/bin/jlab-workers store-key femtomind
~/.local/bin/jlab-workers check femtomind
~/.local/bin/jlab-workers models femtomind
```

Paste only at the hidden prompt, never in chat, Git, command arguments or task
files. Keys are remote owner-only files (0600 under 0700 directories), not encrypted
at rest by this tool. Each person gets their own key per project; do not share keys.
The new store is independent of older `gpt2-project` credentials. It does not import
or modify those files. Install QuantOm only after its actual funded key is issued.

## Authenticate and reuse SSH

Follow [SSH setup](docs/SSH.md), then from a laptop terminal:

```sh
ssh ifarm
```

Complete gateway MFA and any required iFarm password within that one command.
After reaching the remote prompt, leave the terminal open or type `exit`; shared
connections remain available subject to their lifetime. The local AI then runs
`jlab-workers remote ifarm -- status` and controls the workers. Automated commands
require an existing master and disable new transport fallback. If it expires, the
user runs `ssh ifarm` again. One command still preserves both authentication layers.
The worker is in tmux on the actual pinned interactive host, not inside the laptop's
SSH process. Substantial computation belongs in Slurm.

## Start or call a worker

First inspect BOTH pinned hosts and existing project handoffs for a current owner.
Older untagged sessions are outside this tool's registry. Never start a duplicate
scientific worker or migrate an active conversation merely to adopt this tool.

After deployment and acceptance, examples from the laptop:

```sh
# Default = Codex. --slurm explicitly enables its scheduler/network permission layer.
jlab-workers remote ifarm -- start femtomind example --cwd /absolute/workspace --slurm

# Claude is used only when requested. Replace the model placeholder with an allowed ID.
jlab-workers remote ifarm -- start femtomind example-claude --cwd /absolute/other-workspace --engine claude --model EXACT_GATEWAY_CLAUDE_MODEL

jlab-workers remote ifarm -- status
jlab-workers remote ifarm -- capture femtomind example
jlab-workers remote ifarm -- attach femtomind example
```

Workers live in a separate `tmux -L jlab-workers` server. Detach with Ctrl-b, then d.
The session name is `jlab-PROJECT-WORKER`; the immutable record includes engine,
model, hostname, workspace and scheduler setting. Changing those requires a
reviewed migration. A retained exited session prevents a silent new start. Status
reports process liveness, **not** readiness, activity or scientific correctness.

Use [workflow.md](workflow.md) for task dispatch. Capture is an explicit request to
read terminal contents and may reveal task data. Attach permits normal interactive
control. This initial version deliberately has no blind `send-keys` command: the
coordinator must inspect CLI readiness before typing into its terminal. It cannot
automatically distinguish an AI prompt, approval prompt, busy turn or shell prompt.
There is no queue, automatic restart or automatic recovery of conversation IDs.

## Usage and budgets

```sh
jlab-workers remote ifarm -- usage femtomind
jlab-workers remote ifarm -- usage femtomind --scope user
```

These issue read-only `/key/info` or `/user/info` requests, redact nonessential
fields and report unavailable/HTTP 403 rather than inventing a zero balance.
A successful model listing does not prove funding, team ownership or inference
compatibility. Some deployments require additional query parameters/route grants;
this client reports incompatible shapes rather than displaying raw responses.
See [accounting](docs/ACCOUNTING.md) for administrator requests and scope limitations.

## Validation and remaining acceptance

```sh
python3 -m unittest discover -s tests -v
```

Local tests use dummy credentials, fake process observations and mocked requests.
The test suite makes no real model requests and starts no remote workers or Slurm
jobs. Separate authorized live Codex validation is recorded in
[VALIDATION.md](docs/VALIDATION.md); it does not certify every user environment.

Before production: verify SSH host identity and reuse; install a private project
key; confirm team/model entitlement; launch one explicitly authorized disposable
worker of the requested type; inspect provider and permissions; ask it for bounded
`hostname`, workspace file, `squeue` and `sacct` checks. No production job is needed
for acceptance. Claude also needs successful JLab `/v1/messages` support, permitted
model IDs and a confirmed credential source in `/status`. Stop on budget/auth errors.

Worker runtime and conversation history are host-local in
`/var/tmp/jlab-workers-UID/SESSION`. They survive SSH disconnection, but may be lost
to host cleanup/reboot. Store handoffs, source and scientific outputs durably in the
project; preserve needed conversation history before maintenance. tmux does not
make a worker survive reboot. Laptop-offline remote work can continue only within
previously dispatched instructions; the laptop coordinator itself stops.

## References

- [Codex provider authentication](https://learn.chatgpt.com/docs/auth)
- [Codex CLI options](https://learn.chatgpt.com/docs/cli/reference)
- [Claude gateway setup](https://code.claude.com/docs/en/llm-gateway-connect)
- [Claude CLI options](https://code.claude.com/docs/en/cli-reference)
- [LiteLLM spend tracking](https://docs.litellm.ai/docs/proxy/cost_tracking)
- [OpenSSH connection sharing](https://man.openbsd.org/ssh_config)
