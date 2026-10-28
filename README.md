# Robots: your local AI, with workers on the JLab farm

Keep planning and discussing your research with your local AI. Hand off coding,
job monitoring and analysis to a remote AI worker using your project's JLab
LiteLLM API key.

## How to use it

After the one-time installation below:

1. **Connect to iFarm.** In a terminal on your laptop, run:

   ```sh
   ssh ifarm
   ```

   Complete the JLab authentication prompts. Your local AI can then reuse this
   connection; run `ssh ifarm` again if it expires.

2. **Make a staged work plan with your local AI.** Agree on the work, resource
   limits, expected outputs and how each stage will be checked.

3. **Ask your local AI to send the plan to a remote worker.** The worker carries
   out coding, Slurm job submission and monitoring, post-analysis and reports.
   Keep discussing the project and reviewing results in your local chat.

For example:

> Let's make a staged plan for this project. Use the Robots workflow to send
> instructions to a FemtoMind-funded worker on iFarm for coding, job submissions,
> post-analysis and reports. Reuse the existing worker if this task has one.
> Bring the results back to this chat for review.

Remote worker inference is charged to your selected project's LiteLLM key;
planning in your local AI uses that AI's account. Each person needs their own
project key. Work already handed off can continue on iFarm while your laptop is
disconnected; local coordination resumes when you reconnect.

### Optional: control Slurm directly from your local AI

You can also ask your local AI to use the same authenticated SSH connection to
submit jobs, check their status and analyze results directly, without a remote AI
worker. For example:

> Use our staged plan and the existing iFarm SSH connection to submit and monitor
> these Slurm jobs directly from this chat. Do not start a remote AI worker.

In this mode, AI work uses your local AI account; no remote-worker LiteLLM key is
needed. The local AI must remain available for further coordination, while submitted
Slurm jobs can continue independently. Keep one execution owner for each task:
coordinate a handoff before taking over work already owned by a remote worker.
Both modes must follow the [JLab Slurm log requirements](docs/JLAB_SLURM_LOGS.md).

## Default worker and model

The default remote worker is **Codex**, configured to use **`azure/gpt-6-sol` through
JLab LiteLLM**. This is the repository's initial default; an existing installation
may have a different configured model. Setup checks that your project key can
access the selected model. Your local chat keeps its own model and account.

Ask your local AI to select another model available to your project if needed.
**Claude Code is optional and used only when requested**; it needs its own allowed
model and setup verification. Changing the worker model does not change the
billing project.

## One-time installation

Tell your local AI (with terminal access):

> Clone https://github.com/JeffersonLab/robots and start the install protocol.

The AI follows [INSTALL.md](INSTALL.md). It asks for your JLab username, your
billing project (FemtoMind or QuantOm), and whether you already have that project's
API key. It prepares the software and SSH connection, then guides you through:

1. Running `ssh ifarm` in your terminal and completing JLab authentication.
2. Entering your LiteLLM API key privately at the iFarm prompt, after installation:

   ```sh
   ~/.local/bin/jlab-workers store-key femtomind
   ```

The AI gives you the command for your selected project. The LiteLLM **API key**
is separate from your SSH login; enter it only at the hidden prompt, never in chat.
You do not need to choose SSH settings or run installation commands yourself.

Already cloned the repo? Open it with your local AI and say **“Start the install
protocol.”** Prefer manual setup? See [installation details](docs/SETUP.md).

## Further details

- [Workflow for the local AI](workflow.md)
- [Installation and commands](docs/SETUP.md)
- [Usage and budgets](docs/ACCOUNTING.md)
- [Slurm log requirements](docs/JLAB_SLURM_LOGS.md)
- [NERSC options and remaining setup](docs/NERSC.md)
- [Acceptance checks](docs/ACCEPTANCE.md) and [validation record](docs/VALIDATION.md)
