# Acceptance procedure for a new installation

Use this procedure for each user's environment. Existing scientific work keeps
its current owner, launchers, SSH routes, credentials, automation and data.
This procedure does not authorize restarting or taking over an active worker.

## 1. Offline preflight

Read the project's handoff and site instructions. Inspect both configured pinned
iFarm hosts for existing owners; registry absence does not prove worker absence.
Verify host identity, Python, tmux and the requested AI CLI, then run:

```sh
python3 -m unittest discover -s tests -v
```

Choose a dedicated pilot workspace and unique worker name. Home directories may
be shared between hosts, so host separation does not isolate configuration.

## 2. Installation, SSH and enrollment

Follow README.md and SSH.md. Preserve existing executables, private configuration,
SSH helpers and shared connections. Merge the pinned SSH template carefully;
have the user run `ssh ifarm` and complete authentication in their own terminal.
Verify the actual host and that automated commands reuse the existing connection.
A config-parser check alone does not prove interactive login works.

Have the user enter their administrator-issued project key privately with
`store-key`. Verify file permissions, model entitlement and budget visibility.
If usage queries are denied, report that and use the dashboard or administrator
confirmation for budget information. Never substitute a different project's key.

## 3. One bounded worker

Start one explicitly authorized disposable worker in the pilot workspace. Codex
is the default. Use Claude only if requested, installed and allowed by the key.
Inspect provider, model, permissions and input readiness. Dispatch a small task:
report hostname and working directory, write and read a tiny workspace file,
then stop. Verify its acknowledgement and capture/attach after reconnecting.
This stage consumes model usage; do not launch it as part of offline tests.

## 4. Scheduler and logs

With explicit scheduler permission, run bounded read-only `squeue`/`sacct` checks
from the worker itself. Successful parent SSH commands are insufficient.
Before any authorized job submission, configure a dedicated user-owned task log
container and verify worker access. Follow [Slurm log guidance](JLAB_SLURM_LOGS.md):
use literal `/farm_out/` scheduler paths and the verified resolved collector path,
with unique child folders for subsequent attempts. Preserve existing logs.
A scientific job is not required for basic acceptance; any submission needs its
own authorized task and resource limits.

## 5. Optional NERSC and Claude checks

NERSC requires separate authentication from the pinned iFarm worker host and
exact socket/metadata permissions; `--slurm` alone does not provide these.
Verify hostname, user and queue read-only from inside the worker before enabling
jobs. NERSC-hosted workers and API routing require additional integration.

Test Claude separately only when requested. Verify a permitted model, JLab
Messages API support and the expected credential source in its status display.
Do not infer Claude readiness from Codex acceptance.

## 6. Durable handoff

Record results, failures, identity, permissions, job ownership and stop conditions
in the project's handoff. Migrate existing tasks only at an authorized checkpoint,
preserving conversation and accounting. Keep operational receipts and private
configuration outside this repository. Monitoring and cross-chat coordination
must have explicit owners and honor the user's stop instructions.
