# Install protocol for the local AI

Use this protocol when the user says “clone this repo and start the install
protocol,” or asks to install or set up Robots. Perform the setup with the user's
available terminal tools. Guide the user through the two human steps: JLab login
and private API-key entry. This document is an AI-led procedure, not a shell
installer. If terminal access is unavailable, explain that and offer the manual
[setup guide](docs/SETUP.md).

## 1. Ask for the minimum information

Read AGENTS.md and inspect the checkout and existing setup first. Reuse known
answers. Ask the following together, without requesting any secret values:

> What is your JLab username, which billing project should we use (FemtoMind or
> QuantOm), and do you already have your own LiteLLM API key for that project?
> Also let me know if you already have an iFarm worker or setup to preserve.

Use Codex by default. Configure Claude only when explicitly requested. The project
tag selects a credential; it cannot change the team assigned to that credential.
If the user has no key, continue software/SSH preparation and explain that a
project administrator must issue their personal project key before model access
can be verified. Do not ask them to paste passwords, PINs, OTPs or API keys in chat.

## 2. Prepare the laptop

- Reuse the requested checkout. If cloning, use a new directory; do not replace
  an existing checkout or discard local changes.
- Check Python 3.9+ and OpenSSH. Use [SETUP.md](docs/SETUP.md) for installation
  commands. Install `bin/jlab-workers` at `~/.local/bin/jlab-workers` and verify
  its `--help`. If a file already exists, compare it first: reuse an identical
  installation; preserve a differing installation and establish its ownership
  before an upgrade. Do not overwrite another tool or an active worker's launcher.
- Inspect effective SSH configuration and any existing project handoff without
  exposing credential contents. Read [SSH.md](docs/SSH.md), then merge the template
  in `examples/ssh_config` using the supplied username. Back up the original
  configuration, preserve unrelated settings, and keep socket/config permissions
  private. Never blindly append a conflicting `Host ifarm` block.
- Retain the pinned host of an existing setup/worker. For a new setup, propose
  the template's `ifarm2401` default, subject to site access. Ask about the host
  only if existing ownership or site restrictions make the choice unclear.
  Do not silently repoint a live connection to another host.
- Check `ssh -G ifarm` and the gateway configuration. Confirm the intended user,
  pinned host, gateway and shared-connection paths before requesting login.

## 3. Have the user authenticate

Tell the user:

> In your laptop terminal, run `ssh ifarm`, complete the JLab login prompts, and
> tell me when you reach the iFarm prompt. Leave that terminal open for key entry.

This single command can ask for both gateway MFA and the destination password.
Do not try to answer those prompts yourself. Verify first-use fingerprints using
trusted site information; do not bypass a changed-host-key warning.

After the user confirms login, verify the existing SSH master and run a bounded
hostname/user check through it, with fresh authentication disabled as described
in SSH.md. Confirm the host before modifying remote files. If access has expired,
ask for `ssh ifarm` again. Do not repeatedly retry failed authentication.

## 4. Finish remote installation

- Inspect existing installations and workers on accessible configured hosts.
  Do not interpret an inaccessible host or empty registry as proof of no worker.
  Preserve existing sessions, configuration, project data and credentials.
- Copy or clone the toolkit to a new remote checkout, or reuse a verified matching
  one. Install the executable in `~/.local/bin` following the same existing-file
  checks as on the laptop. Remote home may be shared between iFarm hosts.
- Check remote Python, tmux and the selected AI CLI. Locate the actual executable
  and version. If a dependency is missing, use the approved site installation
  method when available; otherwise name the missing dependency and next step.
  Do not claim that this repository installs Codex or Claude itself.
- For a fresh setup, run `~/.local/bin/jlab-workers init` on the remote host.
  If configuration already exists, inspect and reuse it; do not rerun init over it.
  Configure exact executable paths and the intended host/model according to
  SETUP.md. Keep this user-specific configuration outside Git. Model availability
  is checked after key enrollment; a configured default is not proof of access.
- Verify the installed remote command works over the shared connection. Before
  inviting key entry, specifically confirm that `~/.local/bin/jlab-workers`
  exists and is executable on the authenticated host.

Remote login shells may be tcsh: invoke an explicit compatible shell when sending
scripts that use POSIX assignments or control flow. Do not modify running workers
to test installation.

## 5. Guide private key enrollment

Give the exact command for the selected project, clearly labeled **run at the
iFarm prompt**, for example:

```sh
~/.local/bin/jlab-workers store-key femtomind
```

Explain that the user enters the administrator-issued LiteLLM API key twice at
the hidden prompts. This is an API credential, not an SSH key. The file is stored
on iFarm with owner-only permissions; this toolkit does not encrypt it at rest.
Do not watch or capture their terminal during secret entry. Wait for the user's
confirmation, then use `check` to verify file protection without reading the key.

For an existing key, use `check` and reuse it when appropriate; `store-key` refuses
to overwrite a key. Replacement requires a separate explicit rotation request.
Never copy a credential from another project, person or older launcher.

## 6. Verify and summarize

Use the installed toolkit over the shared connection to run `status`, `check
PROJECT`, `models PROJECT`, and `usage PROJECT`. These are status/metadata checks;
do not start a worker or scientific job for installation alone. Report HTTP 403
or unavailable budget data honestly and point to the dashboard/administrator.
Verify that the configured model is listed for this key; do not fall back to a
different project. Model listing does not establish paid inference readiness.

Record a small installation receipt outside Git, for example in a private local
`~/.local/state/robots/` directory. Record repository revision, username, pinned
host/alias, installation paths and versions, billing project, completed checks,
and pending steps. Include no secrets, key fragments or terminal transcripts.
Use that receipt on later setup requests so successful steps are not repeated.

Finish with a short summary of what is ready, any unresolved checks, and a prompt
the user can use in a local project chat:

> Use the Robots workflow in [local checkout path] to hand off the heavy work for
> this project to a [billing project]-funded remote Codex worker on iFarm. Reuse
> any existing task owner and establish the task and resource limits first.

Only say installation is complete when the required software, connection and key
checks have passed. Distinguish installation from live worker acceptance. The
first authorized task follows [workflow.md](workflow.md) and the relevant
[acceptance checks](docs/ACCEPTANCE.md), including worker-side Slurm/log access
when needed. Do not create monitors or cross-chat coordination during installation.
