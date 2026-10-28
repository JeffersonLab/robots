# JLab Slurm stdout/stderr policy

Recorded 2026-10-28 from Chris's site notice supplied by the user in the
workflow chat. The notice states this policy has applied since October 20, 2026.
This records that notice; it is not an independent live scheduler test.

## Required paths

JLab farm Slurm rejects explicitly specified stdout/stderr paths unless they
literally begin with `/farm_out/` or equal `/dev/null`. An equivalent resolved
path beginning `/u/scifarm/farm_out/` is rejected. Preserve the `/farm_out/`
spelling in arguments passed to `sbatch`; do not canonicalize it away.

For direct Slurm submission, use an approved per-user, per-project log directory,
for example `/farm_out/USER/PROJECT_TASK_LOGS/`, with unique job filenames such as
`diagnosis-%j.out` and `diagnosis-%j.err`. Substitute the actual username and
project before submission. Do not assume shell variables expand in `#SBATCH`
directives. Preserve scientific logs rather than redirecting them to `/dev/null`
merely to avoid a configuration problem.

## Worker readiness

The directory must exist and be writable under the site's permissions. The AI
worker also needs narrowly scoped sandbox access to create/check/read its logs.
Successful SSH access or `squeue` alone does not verify this. Verify both the
literal submission paths and access from the actual worker's tool environment.
Where the directory is a symlink, inspect the actual target when configuring
filesystem permissions, while keeping the literal `/farm_out/` submission path.
Do not grant access to all users' logs or disable the sandbox.

Live finding on Codex 0.162.1: exact path grants expose the resolved log leaf but
do not recreate the `/farm_out` symlink inside the sandbox. Use two explicit paths:
literal `/farm_out/USER/LEAF` in Slurm directives, and the attested resolved leaf
for worker-side directory checks, preparation and log collection. Do not replace
the Slurm directive with the resolved path, or broaden access merely to recreate
the alias. Verify worker write/read/delete on a unique probe in the granted leaf.

The launcher supports explicit per-worker grants in its private `config.json`:

```json
{
  "worker_log_directories": {
    "jlab-femtomind-example": ["/farm_out/USER/PROJECT_TASK_LOGS"]
  }
}
```

Substitute the exact registered worker, Unix username and approved leaf. The leaf
must be precreated, owned by that user, not a symlink, and not group/world-writable;
0700 is preferred. Only Codex workers with explicit Slurm access receive these
grants. The launcher grants the literal and resolved leaf, never the parent tree.
This configuration is not a hot-update mechanism: verify the running worker's
effective policy. In the observed 0.162.1 session, reopening `/permissions` did
not reload new profiles. A coordinator safely exited the idle process, verified
its exit, and resumed the exact saved conversation in the same retained tmux pane
with the new profile. Preserve provider/key routing, ownership, conversation ID
and checkpoint; never launch a duplicate to apply a permission change.

## Multi-job tasks without repeated permission changes

For an authorized multi-job task, agree on one dedicated project/task log
container before dispatch, rather than granting a new sibling leaf for each job.
The exact container and its descendants are the permission scope. Each attempt
uses a fresh mode0700 child with a safe unique basename, and logs named
`slurm-%j.out` and `slurm-%j.err`. Reject reused attempt directories, path traversal
and symlink components. Record both literal scheduler and resolved collector paths
in each frozen job plan and associate them with its eventual Slurm job ID.
Keep old logs intact; collectors must read only the selected attempt child.

An existing granted leaf may become this container after explicit coordination
and worker validation, preserving its historical name and root-level logs. SIDIS
used this approach after b002 completed: later attempts use unique children of
the same already-granted b002 directory. This adds no parent/sibling permission
and needs no restart. Record the decision in a durable container policy and
worker acceptance. It does not expand scientific authorization, resource caps,
concurrency or accounting rules; unrelated projects need their own containers.

Before retrying, inspect the prior submission receipt, scheduler state and ledger
to establish whether a job exists and reconcile any reservation. Preserve failed
attempt evidence and the one-worker/one-job controls. A rejected submission is not
a completed scientific job; model usage and Slurm CPU accounting are separate.

## SWIF-specific recovery from the notice

For SWIF workflows, `swif2 status <workflow> -problems SITE_LAUNCH_FAIL` identifies
launch failures. Inspect `job_attempt_problem_details` for the `sbatch` error
requiring `/farm_out/` or `/dev/null`; this problem label may have other causes.

The notice says `swif2 modify-jobs` now accepts `-stdout` and `-stderr`, and
automatically requeues affected jobs without `retry-jobs`. Its example is:

```sh
swif2 modify-jobs my-workflow \
  -stdout /farm_out/$USER/my-workflow/@job_name@-@attempt_id@.out \
  -stderr /farm_out/$USER/my-workflow/@job_name@-@attempt_id@.err \
  -problems SITE_LAUNCH_FAIL
```

SWIF expands `@job_name@` and `@attempt_id@`; these are not direct `sbatch`
placeholders. Jobs not yet attempted also need their incorrect paths corrected.
For new SWIF jobs, specify compliant paths or use SWIF's default under
`/farm_out/$USER/swif/<workflow>/`. These commands mutate/requeue workflows and
are examples, not instructions to run them against unrelated jobs.

SIDIS currently uses direct `sbatch`, so its controller and worker filesystem
permissions need review; SWIF recovery commands do not apply to that controller.

Site support named in the notice: [JLab Scientific Computing ServiceNow](https://jlab.servicenowservices.com/scicomp).
