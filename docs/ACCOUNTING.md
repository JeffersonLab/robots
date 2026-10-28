# Accounting and worker status

| Question | Source | Limitation |
|---|---|---|
| This key's recorded spend and cap | `/key/info` via `usage PROJECT` | Needs route permission; deployed schema varies |
| This person's recorded spend | `/user/info` via `usage PROJECT --scope user` | Needs a user-bound key and self-read access; may span projects |
| Team cap and spend | Admin/UI or scoped team API | Key/member/team caps may all apply |
| Daily tokens and requests | LiteLLM `/user/daily/activity` with date bounds | Not implemented by this client; requires authorization |
| Registered live worker panes | `status` on each pinned host | This Unix user/tool only; not evidence of AI progress |
| Busy/ready/blocked worker | Terminal plus task handoff | No automatic semantic readiness detector |
| Scientific jobs and allocations | Slurm `squeue`, `sacct`, site accounting | Separate from AI/API budgets |

LiteLLM records requests and spending, not the number of idle agent processes.
Multiple workers can share one user's project key and its limits. A cost report
cannot reliably count workers. To associate costs with individual workers, agree
on gateway request tags or administrator-issued worker-specific keys; this version
records tags locally and does not claim to transmit billing metadata.

Ask the administrator to bind each user's key to the correct project team and
user identity. Request permission for **their own** key/user usage routes, with
server-side filtering. Some LiteLLM versions support `get_spend_routes` permissions;
route allowlists and role checks also apply. Confirm with the deployed version.
Never place a proxy master/admin key in a worker or share a key across people.
Project-wide reporting for colleagues requires a separately approved scoped reader
or a server-side report, not an ordinary worker key with guessed access.

The key used in the recorded live acceptance returned HTTP 403 for `/key/info`.
Each user's key permissions must be checked separately.
An error, missing field or null budget is unknown, not zero or unlimited. Numbers
are the gateway's recorded counters and can lag. Do not combine member, key and
team spend as though they were independent purchases, or treat all token categories
as additive (cached tokens may already be included in input tokens).

Funding caps are administered centrally, not hardcoded into this repository.
FemtoMind's communicated monthly team/member limits do not multiply with worker
count. QuantOm requires its actual funded key. Budget exhaustion must stop work;
never switch projects or providers automatically to continue spending.

Source: [LiteLLM spend tracking and access scopes](https://docs.litellm.ai/docs/proxy/cost_tracking).
