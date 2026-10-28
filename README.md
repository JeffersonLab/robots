# Robots: your local AI, with workers on the JLab farm

Keep planning and discussing your research with your local AI. Hand off coding,
job monitoring and analysis to a remote AI worker using your project's JLab
LiteLLM API key.

## Get started

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

## Hand off work from a local project chat

In a new or existing local AI project chat, point the AI to this repo and say:

> Use the robots workflow to hand off the heavy work for this project to a
> FemtoMind-funded remote Codex worker on iFarm. Reuse an existing worker if this
> task already has one. Agree with me on the task, resource limits and completion
> criteria, then dispatch it. Keep this chat for planning and reviewing results.

Your local AI prepares the handoff and controls the remote worker through SSH.
The remote worker uses the selected project's LiteLLM key and runs substantial
computations through Slurm. Codex is the default; ask explicitly for Claude Code
if you want it instead (its setup needs separate verification).

For later tasks, reuse the setup and name the billing project. Each person needs
their own project key. Work already handed off can continue on iFarm while your
laptop is disconnected; new instructions and local monitoring resume when you
reconnect.

## Further details

- [Workflow for the local AI](workflow.md)
- [Installation and commands](docs/SETUP.md)
- [Usage and budgets](docs/ACCOUNTING.md)
- [Slurm log requirements](docs/JLAB_SLURM_LOGS.md)
- [NERSC options and remaining setup](docs/NERSC.md)
- [Acceptance checks](docs/ACCEPTANCE.md) and [validation record](docs/VALIDATION.md)
