# One-command iFarm authentication

After one-time setup, the user opens their laptop terminal and runs:

```sh
ssh ifarm
```

OpenSSH connects through the JLab gateway to the configured **pinned** interactive
host. It asks for gateway MFA and any required iFarm password in that same command.
One command does not mean one credential prompt: the site's two authentication
layers still apply. No separate gateway-login command is needed.

Once the iFarm prompt appears, the user can leave the terminal open or type `exit`
to return to the laptop. ControlMaster/ControlPersist retain authenticated
connections for reuse, subject to idle timeout and site/network limits. In another
local terminal, the AI coordinator checks:

```sh
jlab-workers remote ifarm -- status
```

The coordinator then controls registered workers through the same connection. If
it is unavailable, it asks the user to run **`ssh ifarm` again**, rather than trying
to supply passwords or MFA. The normal user workflow has no `connect` subcommands.
The older `jlab-workers connect` helper remains available for diagnostics.

## One-time setup by the local AI or user

1. Inspect existing SSH aliases and active workers before editing configuration.
   Back up the configuration. Merge the reviewed `examples/ssh_config` entries into
   `~/.ssh/config`; do not blindly append an overlapping `Host ifarm` block. SSH
   uses the first applicable value, so earlier broad rules can also take priority.
2. Replace the username and choose the pinned host that owns the intended workers.
   The example pins `ifarm` to `ifarm2401.jlab.org`; `jlab-ifarm2401` is another name
   for the same host and master. To choose ifarm2402, move `ifarm` into its `Host`
   line. Keep both explicit host aliases for administrative checks. Never silently
   repoint `ifarm` while a worker is active on its previous host.
3. Create `~/.ssh/jlab-workers` with mode 0700 and keep the SSH configuration private
   (0600). The template enables ProxyJump, ControlMaster and ControlPersist for
   both hops, without forwarding an SSH agent or storing credentials.
4. Inspect effective configuration with `ssh -G ifarm` and `ssh -G jlab-gateway`.
   Confirm the user, pinned hostname, gateway and control paths. Have the user run
   `ssh ifarm`; verify first-use host fingerprints against trusted site information
   before accepting. Changed host keys must be investigated, not bypassed.
5. Check actual hostname and destination master from the laptop. The automated
   wrapper uses strict host checking and the original resolved control socket,
   and refuses any new transport if that master expires. Confirm remote `status`
   once the toolkit is installed; don't launch paid work as a connection test.

This repository provides the template and workflow; it does not edit an existing
SSH configuration automatically. The local AI can perform the reviewed merge when
asked to install the setup. Password/PIN/OTP storage and authenticator extraction
are outside the repository. Approved Keychain helpers remain optional conveniences.

## Multiple hosts and connection lifetime

The routine workflow uses one pinned host. If an older worker is on a different
host, authenticate that explicit alias (for example `ssh jlab-ifarm2402`) before
controlling it. Authenticating to one host does not automatically authenticate to
every iFarm host. Shared home storage is not a shared tmux server or runtime.

`ControlPersist 8h` is an idle lifetime, not a guaranteed authentication duration.
Laptop sleep, network changes and server policy can close connections earlier.
`exit` closes the shell, not necessarily the shared master. Use `ssh -O check ifarm`
to inspect it. `ssh -O exit ifarm` deliberately closes that destination master and
can disrupt channels; use it only when intending to end that shared connection.
No desktop connection can persist through a laptop reboot. Remote tmux workers
can continue already assigned work even after the laptop connection disappears.

## NERSC from iFarm

NERSC authentication is separate. On the **same pinned iFarm host as the worker**,
configure a dedicated SSH alias for Perlmutter with its own private ControlPath,
ControlMaster and finite ControlPersist. Authenticate interactively using your
approved NERSC MFA/certificate process. A socket on ifarm2401 cannot be used from
ifarm2402, even if its filename is visible on a shared filesystem. Put that socket
in an owner-only host-local directory, or include `%l` in its path.

After authentication, a worker can check the existing connection, then run a
bounded read-only command with no new transport fallback:

```sh
ssh -o BatchMode=yes -O check nersc-worker
ssh -o BatchMode=yes -o ProxyCommand=false -o ProxyJump=none nersc-worker 'hostname'
```

The alias is an example to configure on iFarm, not one installed by this repo.
Check scheduler identity/account separately. For JAM use `jam` on iFarm and
`m4773`/`m4773_g` at NERSC, subject to the specific task's authorization. API project
tags never select scheduler accounts. Renew access when it expires; do not retry
MFA automatically. Shell command scripts sent to tcsh login accounts must explicitly
invoke `/bin/bash` when using Bash/POSIX assignment or control-flow syntax.

Source: [OpenSSH configuration reference](https://man.openbsd.org/ssh_config).
