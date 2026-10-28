# Repository development and use

- Default to Codex workers. Use Claude Code only when explicitly requested.
- Project and engine are independent; never fall back to another funding key.
- Keep credentials, generated configuration, logs and research data out of Git.
- Do not launch paid model calls or scientific jobs just to test this toolkit.
- Preserve existing workers and SSH configuration; deployment is a separate step.
- Test control/credential changes with `python3 -m unittest discover -s tests -v`.
- Read workflow.md and the task's site/project instructions before dispatch.
