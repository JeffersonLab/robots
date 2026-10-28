# NERSC execution: two deployment choices

Design notes, 2026-10-28. These are integration plans, not deployed features.
Recommendation: start with an iFarm AI worker controlling NERSC through SSH.

| Mode | Agent process and project API key | Scientific execution | Additional dependency |
|---|---|---|---|
| iFarm worker controls NERSC | iFarm, calling JLab LiteLLM directly | NERSC Slurm | Authenticated iFarm-to-NERSC connection and worker permission |
| Worker runs at NERSC | NERSC, calling JLab LiteLLM over a verified route | NERSC Slurm | API reachability, CLI/runtime setup and site-specific permission profile |

The model provider remains JLab LiteLLM in both modes. Moving the agent does not
move model inference onto NERSC GPUs or change its project billing. Scientific
allocation accounting remains separate.

## Mode 1: worker on iFarm (recommended first)

```text
Laptop coordinator -> iFarm worker -> JLab LiteLLM
                            |
                       SSH connection
                            |
                   NERSC shell / Slurm
```

The user runs `ssh ifarm`. From that pinned iFarm host, they authenticate to NERSC
using a separately configured persistent SSH alias or an interactive helper.
The NERSC master must be owned by the iFarm host that runs the worker; logging
into NERSC directly from the laptop does not create that remote capability.

After connection setup, the worker reuses the master for file operations, job
submission and bounded queue/log checks. Keep large inputs/results at NERSC and
return summaries to the coordinator. No JLab API key needs to be installed at NERSC.

Required integration work:

- Generalize the existing personal NERSC authentication helper for arbitrary users
  and their chosen pinned iFarm host. It is not yet part of this portable CLI.
- Give the worker's permission profile access to the exact dedicated socket and
  required non-secret SSH metadata. The existing `--slurm` flag alone does not
  grant this. Do not expose an entire private SSH directory to solve a socket issue.
- Verify `hostname`, user identity and a bounded queue query from inside the worker,
  with fresh-authentication fallback disabled, before enabling scientific jobs.
- On expiry, request interactive renewal. NERSC sshproxy can alternatively obtain
  temporary credentials on iFarm; this requires a separate setup and credential
  lifecycle, and is not implemented here.

NERSC documents sshproxy credentials with a default validity of 24 hours after
MFA. A certificate lifetime and a live SSH master lifetime are different concepts.
See [NERSC MFA](https://docs.nersc.gov/connect/mfa/).

## Mode 2: worker on NERSC

```text
Laptop coordinator -> NERSC worker -> NERSC Slurm
                            |
                       HTTPS API route
                            |
                       JLab LiteLLM
```

A NERSC API request needs both network reachability and a project key. A valid key
does not grant network access through a JLab firewall. First perform a bounded
DNS/TCP/TLS test from the intended NERSC host without a credential. If reachable,
perform an authenticated model-list check without printing the key or response
headers. Neither successful check alone proves model/tool-call compatibility.

Prefer an administrator-supported direct HTTPS endpoint or scoped API proxy. If
that is unavailable, an SSH tunnel between JLab and NERSC is technically possible
subject to site authorization. One possible direction is a reverse forward on an
iFarm-to-NERSC SSH connection, carrying NERSC API traffic back through JLab. Such a
route must preserve TLS hostname/certificate validation, restrict listener access,
and have explicit failure/reconnection handling. No tunnel has been configured.
A tunnel hosted on the laptop would reintroduce the laptop availability dependency.
A JLab-to-NERSC tunnel still depends on both remote hosts and that connection.

Before this toolkit supports NERSC-hosted workers it needs:

- Reviewed remote client installation and verified gateway compatibility.
- Pinned login-node identity and tmux reconnection rules; Perlmutter's front door
  balances connections, so reconnecting need not reach the same tmux server.
- A NERSC-specific runtime/storage/permission profile rather than iFarm socket
  paths, plus review of host-local runtime retention.
- Endpoint configuration if using a different approved API proxy (the present
  launcher fixes the JLab endpoint), private project-key enrollment and acceptance
  checks for the requested engine. Codex remains default; Claude is opt-in.

NERSC supports lightweight coding-agent work on login nodes; long or resource-heavy
calculations belong in scheduled allocations. See [NERSC coding-agent guidance](https://docs.nersc.gov/development/coding-agents/)
and [connection/load-balancing behavior](https://docs.nersc.gov/connect/).

## Laptop independence

Either mode can continue work already assigned to a remote worker when the laptop
disconnects, until the worker needs a decision or a required connection expires.
The local coordinator itself cannot continue while the laptop is offline. Already
submitted Slurm jobs normally continue independently of the agent/SSH session.
Do not equate persistent tmux with automatic supervision, renewal or reboot recovery.
