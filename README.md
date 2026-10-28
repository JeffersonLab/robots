# Robots: your local AI, with workers on the JLab farm

Keep planning and discussing your research with your local AI. Hand off coding,
job monitoring and analysis to a remote AI worker using your project's JLab
LiteLLM API key.

## 1. Clone the repo on your laptop

```sh
git clone https://github.com/JeffersonLab/robots.git
cd robots
```

## 2. Ask your local AI to prepare the setup

Open this folder with a local AI that can use your terminal, and tell it:

> Read workflow.md and docs/SETUP.md. Set up this toolkit on my laptop and iFarm.
> Prepare `ssh ifarm` for my JLab username, preserving my existing SSH settings
> and workers. Guide me through authentication, then finish installing and
> configuring the remote tools. Tell me when I can enter my project API key.
> Use Codex workers by default.

The AI handles the installation and connection setup. You handle login and
private key entry. Prefer to do it yourself? Follow [detailed setup](docs/SETUP.md)
and [SSH setup](docs/SSH.md).

## 3. Authenticate to iFarm

In your laptop terminal, run:

```sh
ssh ifarm
```

Complete the JLab authentication prompts and leave the connection open while your
AI finishes setup. It can then reuse that connection. If authentication expires,
run `ssh ifarm` again.

## 4. Enter your project's LiteLLM API key

Once the AI confirms installation is complete, run this **at the iFarm prompt**:

```sh
~/.local/bin/jlab-workers store-key femtomind
```

Enter your own administrator-issued key at the hidden prompt. This is a
**LiteLLM API key**, separate from your SSH login. Do not paste it into the AI chat.
The toolkit stores it in a private file on iFarm. Use `quantom` instead if you
have a key issued for that project.

## 5. Start a local project chat and hand off the heavy work

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
