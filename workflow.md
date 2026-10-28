# Reusable local/remote task workflow

1. Read the project's AGENTS.md/CLAUDE.md and site resource/storage guidance. Identify
   the scientific owner and the authorized billing project. Use Codex unless the
   user explicitly requests Claude Code. Local coordinator reasoning uses the
   coordinator's account; remote inference uses the selected project key.
2. Inspect handoffs, Slurm jobs and both pinned hosts for an existing worker.
   Registry absence is not proof of absence: older workers use other tmux servers.
   Reuse the existing owner. Do not move/resume it as a new worker without review.
3. Ask the user to run `ssh ifarm` in their laptop terminal when authentication is
   needed. That one command handles gateway MFA and destination authentication.
   Once connected, use `jlab-workers remote ifarm -- status` and the other `remote`
   commands to reuse the connection. If it expires, ask for `ssh ifarm` again.
   Verify actual hostname against the pinned worker identity. NERSC needs its own
   authenticated connection from that host. Never store or request OTP seeds in
   task files.
4. For a new worker, verify the project key/team, model entitlement and CLI version.
   Start the requested engine with explicit project, worker name and workspace.
   Claude is opt-in, never an automatic fallback from Codex failure. Keep runtime
   state host-local. Use Slurm for heavy work; API funding and Slurm accounts differ.
5. Inspect `status`, then `capture`/`attach`. Confirm provider/model, active permission
   policy and that the model is at its input prompt. A pane can be alive while the
   client is blocked or failed. Never paste a task into an unverified terminal.
   New trust or permission prompts need normal review; do not turn off protections.
6. Put the brief below in a durable project TASK.md. Dispatch it through the verified
   CLI terminal. For a local AI using terminal automation, capture/check the prompt
   immediately before sending literal text; stop on ambiguous UI. This tool does
   not provide blind prompt injection or an unattended dispatch queue.
   Large pastes may still be buffering when `send-keys` returns. Inspect the
   composer after the paste, submit Enter separately, and verify the task appears
   in the conversation with a worker response. A pasted-content placeholder alone
   does not confirm dispatch; do not resend the whole task to fix a pending Enter.
7. First run bounded shell/scheduler preflight through the worker itself. Parent
   SSH access alone does not establish worker sandbox access. Report permission
   errors without bypassing them. Codex's explicit `--slurm` option permits the
   known iFarm sockets and outbound network; Claude retains its own default tool
   permission prompts and has no equivalent sandbox guarantee from this wrapper.
   On JLab, verify stdout/stderr use literal `/farm_out/` paths and that the actual
   worker can access its approved log directory. The site rejects alternate
   spellings such as `/u/scifarm/farm_out/`; read
   [JLab Slurm log requirements](docs/JLAB_SLURM_LOGS.md) before submission/retry.
8. Continue only within authorized resource/spend limits. Use concise milestone
   reports, avoid token-consuming polling loops, and stop on authentication/budget
   errors or scientific acceptance failures. Keep unique outputs and provenance.
9. Write a durable HANDOFF.md containing state, exact host/session/conversation ID,
   jobs, next step and stop conditions. Record terminal exits and blocked work.
   A reboot can remove tmux and host-local conversation state. This initial toolkit
   does not automatically resume sessions, supervise restarts or kill workers.

## Task brief

```text
Scientific project / owner:
Billing project: femtomind | quantom
Worker engine: codex (default) | claude (explicit request)
Worker name / actual host / tmux session:
Exact model / provider / permission policy:
Canonical workspace / source revision / uncommitted changes:
Existing conversation ID and handoff (if continuing):
Objective and measurable completion criteria:
Input locations and provenance:
Authorized actions and excluded actions:
Slurm site/account, maximum jobs, CPUs/GPUs, wall time, allocation:
Model spend limit, retries and stop conditions:
Preflight and numerical acceptance checks:
Monitoring owner/cadence; what continues if laptop disconnects:
Deliverables, evidence paths and handoff location:
```

## Team onboarding

Each user needs their own site accounts, approved SSH authentication, model-client
installation and project-specific virtual keys. Share this code and templates;
keep usernames, private configurations, credentials, terminal logs and scientific
data outside Git. Review local policy before running persistent processes on a
login/interactive host. Do not start another person's worker under your Unix login.

## User-facing onboarding script

After cloning, the user can tell their local AI:

> Read README.md and workflow.md. Install the toolkit locally and on my chosen
> iFarm host. Preserve my existing SSH setup and active workers. Configure
> `ssh ifarm` as the single login command through the JLab gateway to that pinned
> host. Guide me through its authentication prompts and hidden project-key entry.
> Verify connection reuse before launching a worker. Default to Codex; use Claude
> only when I explicitly request it.

The AI prepares the configuration and software; the user authenticates with
`ssh ifarm` and privately enters the project API key once with `store-key`. Later
tasks reuse both. Reauthentication uses the same `ssh ifarm` command. NERSC access
is a separate site authentication step, only when the task needs it.
